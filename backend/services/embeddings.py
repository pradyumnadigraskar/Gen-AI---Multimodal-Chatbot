from sentence_transformers import SentenceTransformer
from ..config import settings

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.SENTENCE_EMBEDDINGS_MODEL)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    embs = model.encode(texts, normalize_embeddings=True).tolist()
    # ensure list[list[float]]
    if isinstance(embs[0], float):
        return [embs]
    return embs
