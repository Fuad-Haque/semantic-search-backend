from qdrant_client.models import (
    VectorParams, Distance, PointStruct, Filter,
    FieldCondition, MatchValue, ScoredPoint
)
from app.database import qdrant_client
from app.config import settings
import uuid

async def ensure_collection_exists():
    """Create the Qdrant collection if it doesn't exist yet."""
    collections = await qdrant_client.get_collections()
    names = [c.name for c in collections.collections]
    if settings.QDRANT_COLLECTION not in names:
        await qdrant_client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_DIM,
                distance=Distance.COSINE
            )
        )

async def upsert_chunks(
    document_id: str,
    document_name: str,
    chunks: list[str],
    embeddings: list[list[float]]
):
    """Store chunks + their embeddings in Qdrant."""
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "document_id": document_id,
                "document_name": document_name,
                "chunk_index": i,
                "chunk_text": chunk,
            }
        )
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    await qdrant_client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points
    )

async def semantic_search(query_vector: list[float], top_k: int = 10) -> list[ScoredPoint]:
    results = await qdrant_client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True
    )
    return results.points

async def delete_document_vectors(document_id: str):
    """Delete all vectors belonging to a document."""
    await qdrant_client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        )
    )