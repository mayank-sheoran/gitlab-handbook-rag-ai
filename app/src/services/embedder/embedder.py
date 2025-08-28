from sentence_transformers import SentenceTransformer
from app.src.config import get_settings
from app.src.utils.logs import logger
class Embedder:
    _model = None
    def __init__(self):
        self.s = get_settings()
        self.batch_size = self.s.embedding_batch_size
    def _ensure_model(self):
        if self.__class__._model is None:
            logger.info(f"embedding_model_load name={self.s.embedding_model_name}")
            self.__class__._model = SentenceTransformer(self.s.embedding_model_name, trust_remote_code=True)
    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self._ensure_model()
        logger.info(f"embed texts={len(texts)} batch={self.batch_size}")
        out: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i+self.batch_size]
            arr = self.__class__._model.encode(batch, batch_size=min(self.batch_size, len(batch)), normalize_embeddings=True, convert_to_numpy=True)
            for emb in arr:
                out.append(emb.tolist())
        return out
