import json
import os
from typing import Set
from app.src.config import get_settings
from app.src.utils.logs import logger


class VisitedStore:
    def __init__(self):
        self.settings = get_settings()
        self.visited_urls_path = "./resources/visited_urls.json"
        self.visited_urls: Set[str] = self._load_visited()

    def is_visited(self, url: str) -> bool:
        return url in self.visited_urls

    def mark_visited(self, url: str):
        self.visited_urls.add(url)

    def get_visited_urls(self) -> Set[str]:
        return self.visited_urls.copy()

    def save_visited(self):
        try:
            os.makedirs(os.path.dirname(self.visited_urls_path), exist_ok=True)
            with open(self.visited_urls_path, 'w') as f:
                json.dump(sorted(self.visited_urls), f)
            logger.info(f"Saved {len(self.visited_urls)} visited URLs")
        except Exception as e:
            logger.error(f"Error saving visited URLs: {e}")

    def _load_visited(self) -> Set[str]:
        if not os.path.exists(self.visited_urls_path):
            return set()
        try:
            with open(self.visited_urls_path, 'r') as f:
                data = json.load(f)
            if isinstance(data, list):
                logger.info(f"Loaded {len(data)} visited URLs")
                return set(data)
        except Exception as e:
            logger.error(f"Error loading visited URLs: {e}")
        return set()
