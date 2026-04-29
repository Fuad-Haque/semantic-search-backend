from sentence_transformers import SentenceTransformer
from app.config import settings
import numpy as np

# Load model once at startup — this takes ~2 seconds the first time
_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns list of float vectors."""
    model = get_model()
    # encode returns numpy array — convert to plain Python lists for JSON + Qdrant
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=False)
    return embeddings.tolist()

def embed_query(query: str) -> list[float]:
    """Embed a single search query."""
    return embed_texts([query])[0]