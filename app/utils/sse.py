import json
from typing import AsyncGenerator

async def sse_event(event: str, data: dict) -> str:
    """Format a single SSE message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"

async def progress_stream(
    chunks: list[str],
    document_id: str,
    embed_fn,
    store_fn
) -> AsyncGenerator[str, None]:
    """Generator that embeds chunks in batches and yields progress events."""
    total = len(chunks)
    batch_size = 32
    all_embeddings = []

    yield await sse_event("start", {"total_chunks": total, "document_id": document_id})

    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        embeddings = embed_fn(batch)    # sync — sentence-transformers is sync
        all_embeddings.extend(embeddings)
        processed = min(i + batch_size, total)
        yield await sse_event("progress", {
            "processed": processed,
            "total": total,
            "percent": round(processed / total * 100, 1)
        })

    await store_fn(all_embeddings)
    yield await sse_event("complete", {"document_id": document_id, "total_chunks": total})