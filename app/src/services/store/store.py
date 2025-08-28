from typing import List, Dict, Any
from app.src.config import get_settings
from app.src.utils.logs import logger
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
import uuid
from app.src.services.embedder.embedder import Embedder

class VectorStore:
    def __init__(self):
        self.settings = get_settings()
        self.client = QdrantClient(host=self.settings.qdrant_host, port=self.settings.qdrant_port)
        self.collection_name = self.settings.collection_name
        if self.collection_name not in [c.name for c in self.client.get_collections().collections]:
            logger.info("Qdrant collection missing, creating...")
            emb_dim = self._detect_embedding_dim()
            self._create_collection(emb_dim)
        logger.info(f"Vector store initialized: {self.collection_name} (Qdrant)")

    def _detect_embedding_dim(self) -> int:
        try:
            emb = Embedder().embed(["dimension probe"])[0]
            return len(emb)
        except Exception as e:
            logger.error(f"Failed to detect embedding dimension: {e}")
            raise

    def _create_collection(self, dim: int):
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(size=dim, distance=qmodels.Distance.COSINE)
        )
        logger.info(f"Created Qdrant collection name={self.collection_name} dim={dim}")

    def add(self, ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]]):
        try:
            if not ids:
                return
            points = []
            for i, emb in enumerate(embeddings):
                point_id = ids[i] if i < len(ids) and ids[i] else str(uuid.uuid4())
                try:
                    uuid.UUID(point_id)
                except ValueError:
                    point_id = str(uuid.uuid4())

                meta = metadatas[i] if i < len(metadatas) else {}
                payload = {
                    **meta,
                    "content": documents[i] if i < len(documents) else ""
                }
                points.append(qmodels.PointStruct(id=point_id, vector=emb, payload=payload))
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info(f"Added {len(points)} documents to vector store (Qdrant)")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def query(self, embedding: list[float], k: int):
        try:
            result = self.client.query_points(
                collection_name=self.collection_name,
                query=embedding,
                limit=k,
                with_payload=True,
                with_vectors=False
            )
            ids = [str(point.id) for point in result.points]
            documents = [point.payload.get("content", "") for point in result.points]
            metadatas = []
            distances = []
            for point in result.points:
                payload = dict(point.payload)
                payload.pop("content", None)
                metadatas.append(payload)
                distances.append(point.score)
            distances = [1 - s for s in distances]
            return {
                'ids': [ids],
                'documents': [documents],
                'metadatas': [metadatas],
                'distances': [distances]
            }
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            raise

    def get_all_chunks_by_url(self, url: str) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Fetching all chunks for URL: {url}")
            scroll_res, _next = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=qmodels.Filter(should=[qmodels.FieldCondition(key="url", match=qmodels.MatchValue(value=url))]),
                with_payload=True,
                with_vectors=False,
                limit=10000
            )
            chunks = []
            for p in scroll_res:
                payload = p.payload or {}
                chunks.append({
                    'id': str(p.id),
                    'content': payload.get('content', ''),
                    'url': payload.get('url', ''),
                    'title': payload.get('title', ''),
                    'index': payload.get('index', 0),
                    'total': payload.get('total', 1)
                })

            chunks.sort(key=lambda x: x['index'])
            logger.info(f"Retrieved {len(chunks)} chunks for URL: {url}")
            return chunks
        except Exception as e:
            logger.error(f"Error fetching chunks by URL {url}: {e}")
            return []

    def clear(self):
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name in collections:
                self.client.delete_collection(self.collection_name)
            emb_dim = self._detect_embedding_dim()
            self._create_collection(emb_dim)
            logger.info(f"Vector store cleared: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
