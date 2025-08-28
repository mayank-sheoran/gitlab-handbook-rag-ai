from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.src.config import get_settings
import uuid
from app.src.domain.chunks import Chunk
from app.src.domain.raw_page import RawPage
from app.src.utils.logs import logger


class Chunker:
    def __init__(self):
        settings = get_settings()
        self.char_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " "],
        )

    def chunk_page(self, page: RawPage) -> list[Chunk]:
        if not page.text or len(page.text.strip()) < 50:
            logger.warning(f"Skipping page with insufficient content: {page.url}")
            return []

        parts = self.char_splitter.split_text(page.text)
        chunks = []

        for i, part in enumerate(parts):
            if len(part.strip()) < 20:
                continue
            namespace = uuid.UUID('12345678-1234-5678-1234-123456789abc')
            chunk_id = str(uuid.uuid5(namespace, f"{page.url}-{i}"))
            chunks.append(
                Chunk(
                    id=chunk_id,
                    url=page.url,
                    title=page.title,
                    content=part.strip(),
                    index=i,
                    total=len(parts),
                )
            )

        logger.info(f"Chunked page into {len(chunks)} chunks with preserved order")
        return chunks
