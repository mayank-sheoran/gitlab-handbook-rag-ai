from typing import List, Dict, Any
from app.src.services.store.store import VectorStore
from app.src.config import get_settings
from app.src.utils.logs import logger

class DocumentRetriever:
    def __init__(self):
        self.settings = get_settings()
        self.store = VectorStore()

    def get_full_document(self, citation: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = citation.get('url', '')
            title = citation.get('title', '')
            logger.info(f"Attempting to retrieve full document - URL: {url}, Title: {title}")
            if url:
                logger.info(f"Retrieving full document for URL: {url}")
                all_chunks = self.store.get_all_chunks_by_url(url)
                if not all_chunks:
                    logger.warning(f"No chunks found for URL: {url}")
                    return []
                logger.info(f"Retrieved {len(all_chunks)} chunks for URL: {url} in original order")
                return all_chunks

            logger.warning(f"Could not retrieve full document for citation: {citation.get('id', 'unknown')}")
            return [citation]

        except Exception as e:
            logger.error(f"Failed to retrieve full document: {str(e)}")
            return [citation]
