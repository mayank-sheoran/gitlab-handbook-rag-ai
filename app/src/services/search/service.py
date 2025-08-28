from typing import List, Dict, Any, Optional
from app.src.config import get_settings
from app.src.services.embedder.embedder import Embedder
from app.src.services.store.store import VectorStore
from app.src.utils.logs import logger

class SearchService:
    def __init__(self):
        self.settings = get_settings()
        self.embedder = Embedder()
        self.store = VectorStore()

    def _vector_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        embedding = self.embedder.embed([query])[0]
        try:
            result = self.store.query(embedding, k)
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

        ids = result.get('ids', [[]])[0]
        documents = result.get('documents', [[]])[0]
        metadatas = result.get('metadatas', [[]])[0]
        distances = result.get('distances', [[]])[0]

        results = []
        for i, doc_id in enumerate(ids):
            meta = metadatas[i] if i < len(metadatas) else {}
            distance = distances[i] if i < len(distances) else 1.0
            similarity = max(0.0, 1.0 - distance)

            results.append({
                'id': doc_id,
                'content': documents[i],
                'url': meta.get('url', ''),
                'title': meta.get('title', ''),
                'index': meta.get('index', 0),
                'total': meta.get('total', 1),
                'similarity': similarity
            })
        return results

    def search(self, query: str, k: Optional[int] = None) -> List[Dict[str, Any]]:
        candidates = self._vector_search(query, k)

        for result in candidates:
            result['rerank_score'] = result['similarity']

        final_results = candidates[:k]
        for i, result in enumerate(final_results):
            result['rank'] = i + 1

        logger.info(f"Search completed: query_len={len(query)}, k={k}, results={len(final_results)}")
        return final_results
