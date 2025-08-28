import asyncio
from typing import List
from app.src.config import get_settings
from app.src.services.ingest.chunker import Chunker
from app.src.services.ingest.crawler import Crawler
from app.src.services.embedder.embedder import Embedder
from app.src.services.store.store import VectorStore
from app.src.services.store.visited_store import VisitedStore
from app.src.utils.logs import logger
from app.src.domain.chunks import Chunk


class IngestionPipeline:
    def __init__(self):
        self.settings = get_settings()
        self.crawler = Crawler()
        self.chunker = Chunker()
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.visited_store = VisitedStore()

    async def run(self):
        queue = asyncio.Queue()

        visited_urls = self.visited_store.get_visited_urls()
        crawler_task = asyncio.create_task(self.crawler.crawl(queue, visited_urls))

        total_pages = 0
        total_chunks = 0
        chunk_buffer: List[Chunk] = []

        logger.info("Starting ingestion pipeline")

        while True:
            page = await queue.get()
            if page is None:
                break
            if self.visited_store.is_visited(str(page.url)):
                continue

            self.visited_store.mark_visited(str(page.url))
            total_pages += 1

            chunks = self.chunker.chunk_page(page)
            chunk_buffer.extend(chunks)

            if len(chunk_buffer) >= 10:
                await self._process_chunks(chunk_buffer)
                total_chunks += len(chunk_buffer)
                chunk_buffer.clear()

        if chunk_buffer:
            await self._process_chunks(chunk_buffer)
            total_chunks += len(chunk_buffer)

        pages_crawled = await crawler_task
        self.visited_store.save_visited()

        logger.info(f"Ingestion complete: {pages_crawled} pages, {total_chunks} chunks")
        return {"pages": pages_crawled, "chunks": total_chunks}

    async def _process_chunks(self, chunks: List[Chunk]):
        if not chunks:
            return

        ids = [chunk.id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [
            {
                "url": str(chunk.url),
                "title": chunk.title or "",
                "index": chunk.index,
                "total": chunk.total
            }
            for chunk in chunks
        ]

        embeddings = self.embedder.embed(documents)
        self.vector_store.add(ids, documents, metadatas, embeddings)

    def run_sync(self):
        return asyncio.run(self.run())
