import os
from functools import lru_cache
from dotenv import load_dotenv
from app.src.utils.logs import logger

class Settings:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    if load_dotenv(os.path.join(BASE_DIR, "../.env"), override=True):
        logger.info("Loaded .env file successfully")
    else:
        logger.warning(".env file not found or failed to load")

    base_urls: list[str] = [
        "https://handbook.gitlab.com/",
        "https://about.gitlab.com/direction/"
    ]
    user_agent: str = "Mozilla/5.0 (compatible; GitLabDocBot/1.0)"
    request_timeout: int = 10
    max_concurrency: int = 8
    crawl_max_pages: int = 300
    crawl_max_depth: int = 3

    collection_name: str = "gitlab_docs"

    chunk_size: int = 800
    chunk_overlap: int = 200

    embedding_model_name: str = "BAAI/bge-m3"
    embedding_batch_size: int = 32

    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    gemini_model: str = "gemini-1.5-flash"

    answer_max_tokens: int = 4000

    qdrant_host: str = os.getenv("QDRANT_HOST")
    qdrant_port: int = int(os.getenv("QDRANT_PORT"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
