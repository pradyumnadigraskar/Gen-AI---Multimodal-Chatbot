# backend/services/vectorstore.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from ..config import settings
import os

_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)
AUTO_RECREATE = os.getenv("QDRANT_AUTO_RECREATE", "true").lower() in ("1","true","yes","on")

def ensure_collection(dim: int):
    try:
        # exists?
        info = _client.get_collection(settings.QDRANT_COLLECTION)
        # Qdrant >=1.7 returns vectors schema under config
        current = info.config.params.vectors.size
        if current != dim:
            if AUTO_RECREATE:
                _client.recreate_collection(
                    collection_name=settings.QDRANT_COLLECTION,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
            else:
                raise RuntimeError(f"Qdrant collection dim={current} != embed dim={dim}")
    except Exception:
        # create if missing (or if older servers threw above get_collection error)
        _client.recreate_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

def upsert(points: list[tuple[str, list[float], dict]]):
    from qdrant_client.http.models import PointStruct
    _client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=[PointStruct(id=pid, vector=vec, payload=payload) for pid, vec, payload in points],
    )

def search(query: list[float], top_k: int = 5):
    return _client.search(collection_name=settings.QDRANT_COLLECTION, query_vector=query, limit=top_k)
