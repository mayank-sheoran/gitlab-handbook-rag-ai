import asyncio
from typing import Optional, Set
from urllib.parse import urljoin, urldefrag, urlparse
import httpx
from bs4 import BeautifulSoup
from app.src.config import get_settings
from app.src.domain.raw_page import RawPage
from app.src.utils.logs import logger


class Crawler:
    def __init__(self):
        self.settings = get_settings()
        self.seen = set()
        self._pages_count = 0

    def allowed(self, url: str) -> bool:
        return any(base in url for base in self.settings.base_urls)

    def extract_text(self, html: str) -> tuple[str, Optional[str]]:
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.body or soup
        text = body.get_text(strip=True, separator='\n')
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else None
        try:
            from trafilatura import extract
            tranfilatura_text = extract(html, include_comments=False, include_images=False, favor_recall=True, output_format='markdown')
            text = tranfilatura_text or text
        except Exception:
            pass
        return text or '', title

    async def enqueue_a_tags(self, html: str, depth, url_queue):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            next_url = link['href']
            if next_url not in self.seen and self.allowed(next_url):
                await url_queue.put((next_url, depth + 1))

    async def crawl(self, queue: asyncio.Queue, previsited: Optional[Set[str]] = None):
        self.seen = previsited or set()
        self._pages_count = 0
        url_queue = asyncio.Queue()

        for url in self.settings.base_urls:
            if url not in self.seen:
                await url_queue.put((url, 0))

        logger.info(f"Starting crawl with max_pages={self.settings.crawl_max_pages}")

        async with httpx.AsyncClient(headers={'User-Agent': self.settings.user_agent}) as client:
            async def worker():
                while True:
                    if self._pages_count >= self.settings.crawl_max_pages:
                        while not url_queue.empty():
                            url_queue.get_nowait()
                            url_queue.task_done()
                        return
                    try:
                        url, depth = await asyncio.wait_for(url_queue.get(), timeout=1.0)
                    except asyncio.TimeoutError:
                        return

                    if depth > self.settings.crawl_max_depth or url in self.seen:
                        url_queue.task_done()
                        continue

                    try:
                        response = await client.get(url, timeout=self.settings.request_timeout)

                        if response.status_code != 200 or 'text/html' not in response.headers.get('content-type', '').lower():
                            logger.warning(f"Skipping {url}: status={response.status_code}")
                            url_queue.task_done()
                            continue

                        text, title = self.extract_text(response.text)
                        if len(text.strip()) < 100:
                            logger.warning(f"Skipping {url}: insufficient content")
                            url_queue.task_done()
                            continue

                        await queue.put(RawPage(url=url, depth=depth, html=response.text, text=text, title=title))
                        self.seen.add(url)
                        self._pages_count += 1
                        if depth < self.settings.crawl_max_depth:
                            await self.enqueue_a_tags(response.text, depth, url_queue)

                    except Exception as e:
                        logger.error(f"Error crawling {url}: {e}")
                    finally:
                        url_queue.task_done()

            workers = [asyncio.create_task(worker()) for _ in range(self.settings.max_concurrency)]
            await url_queue.join()

            for worker in workers:
                worker.cancel()
            await asyncio.gather(*workers, return_exceptions=True)

        await queue.put(None)
        logger.info(f"Crawling complete: {self._pages_count} pages")
        return self._pages_count
