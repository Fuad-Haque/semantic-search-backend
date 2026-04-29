from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.vector_store import semantic_search as qdrant_search
from app.services.embedder import embed_query
from app.models.schemas import SearchResult
from uuid import UUID

async def run_keyword_search(query: str, db: AsyncSession, top_k: int = 10) -> list[dict]:
    """PostgreSQL full-text search on chunk text."""
    sql = text("""
        SELECT
            c.id,
            c.document_id,
            d.filename,
            c.chunk_index,
            c.text,
            ts_rank_cd(c.fts_vector, plainto_tsquery('english', :query)) AS score
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE c.fts_vector @@ plainto_tsquery('english', :query)
        ORDER BY score DESC
        LIMIT :limit
    """)
    result = await db.execute(sql, {"query": query, "limit": top_k})
    rows = result.mappings().all()
    return [dict(r) for r in rows]

def reciprocal_rank_fusion(
    semantic_results: list,
    keyword_results: list,
    k: int = 60
) -> list[dict]:
    """Merge two ranked lists using RRF. Higher score = better."""
    scores: dict[str, float] = {}
    metadata: dict[str, dict] = {}

    for rank, hit in enumerate(semantic_results):
        chunk_id = f"{hit.payload['document_id']}-{hit.payload['chunk_index']}"
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (rank + 1 + k)
        metadata[chunk_id] = {
            "document_id": hit.payload["document_id"],
            "document_name": hit.payload["document_name"],
            "chunk_index": hit.payload["chunk_index"],
            "chunk_text": hit.payload["chunk_text"],
        }

    for rank, row in enumerate(keyword_results):
        chunk_id = f"{row['document_id']}-{row['chunk_index']}"
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (rank + 1 + k)
        if chunk_id not in metadata:
            metadata[chunk_id] = {
                "document_id": str(row["document_id"]),
                "document_name": row["filename"],
                "chunk_index": row["chunk_index"],
                "chunk_text": row["text"],
            }

    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    return [
        {**metadata[cid], "rrf_score": scores[cid]}
        for cid in sorted_ids
    ]

async def run_all_searches(query: str, db: AsyncSession, top_k: int = 10):
    """Run semantic + keyword, then fuse. Returns all three result sets."""
    import time
    start = time.time()

    # Embed query
    query_vector = embed_query(query)

    # Semantic search
    sem_hits = await qdrant_search(query_vector, top_k)
    semantic_results = [
        SearchResult(
            document_id=h.payload["document_id"],
            document_name=h.payload["document_name"],
            chunk_index=h.payload["chunk_index"],
            chunk_text=h.payload["chunk_text"],
            similarity_score=round(h.score, 4),
            search_type="semantic"
        )
        for h in sem_hits
    ]

    # Keyword search
    kw_rows = await run_keyword_search(query, db, top_k)
    keyword_results = [
        SearchResult(
            document_id=r["document_id"],
            document_name=r["filename"],
            chunk_index=r["chunk_index"],
            chunk_text=r["text"],
            similarity_score=round(float(r["score"]), 4),
            search_type="keyword"
        )
        for r in kw_rows
    ]

    # Hybrid: RRF
    fused = reciprocal_rank_fusion(sem_hits, kw_rows)[:top_k]
    hybrid_results = [
        SearchResult(
            document_id=r["document_id"],
            document_name=r["document_name"],
            chunk_index=r["chunk_index"],
            chunk_text=r["chunk_text"],
            similarity_score=round(r["rrf_score"], 4),
            search_type="hybrid"
        )
        for r in fused
    ]

    latency = (time.time() - start) * 1000
    return semantic_results, keyword_results, hybrid_results, round(latency, 2)