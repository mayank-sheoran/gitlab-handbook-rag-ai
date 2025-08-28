import re
from typing import Optional
from app.src.utils.logs import logger

class QueryProcessor:
    def __init__(self):
        pass

    def clean_query(self, query: str) -> str:
        query = query.strip()
        query = re.sub(r'\s+', ' ', query)
        return query

    def is_valid_query(self, query: str) -> bool:
        if not query or len(query.strip()) < 2:
            return False
        if len(query) > 500:
            return False
        return True

    def process_query(self, query: str) -> Optional[str]:
        try:
            cleaned = self.clean_query(query)
            if not self.is_valid_query(cleaned):
                return None
            return cleaned
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return None
