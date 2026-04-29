from fastapi import APIRouter, UploadFile, File, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import get_db
from app.models.document import Document, Chunk
from app.models.schemas import DocumentOut
from app.services.chunker import chunk_text, extract_text_from_file
from app.services.embedder import embed_texts
from app.services.vector_store import ensure_collection_exists, upsert_chunks, delete_document_vectors
from app.utils.sse import sse_event, progress_stream
from app.config import settings
import uuid

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {"text/plain", "application/pdf", "text/markdown"}
CHUNK_STRATEGIES = {"fixed", "sentence", "paragraph"}

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    strategy: str = Query(default="fixed"),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document and stream chunking/embedding progress via SSE."""
    if strategy not in CHUNK_STRATEGIES:
        strategy = "fixed"

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        from fastapi import HTTPException
        raise HTTPException(400, f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB")

    document_id = str(uuid.uuid4())
    text_content = extract_text_from_file(content, file.filename or "file.txt")
    chunks = chunk_text(text_content, strategy)

    # Save document record immediately
    doc = Document(
        id=document_id,
        filename=file.filename,
        content_type=file.content_type,
        total_chunks=len(chunks),
        token_count=len(text_content.split()),
        embedding_model=settings.EMBEDDING_MODEL,
        chunk_strategy=strategy,
        status="processing"
    )
    db.add(doc)
    await db.commit()

    await ensure_collection_exists()

    async def generate():
        total = len(chunks)
        batch_size = 32
        all_embeddings = []

        yield await sse_event("start", {"document_id": document_id, "total_chunks": total})

        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            embeddings = embed_texts(batch)
            all_embeddings.extend(embeddings)
            processed = min(i + batch_size, total)
            yield await sse_event("progress", {
                "processed": processed,
                "total": total,
                "percent": round(processed / total * 100, 1)
            })

        # Store in Qdrant
        await upsert_chunks(document_id, file.filename, chunks, all_embeddings)

        # Store chunks in PG for FTS
        for idx, (chunk, _) in enumerate(zip(chunks, all_embeddings)):
            c = Chunk(
                id=str(uuid.uuid4()),
                document_id=document_id,
                chunk_index=idx,
                text=chunk
            )
            db.add(c)
        await db.commit()

        # Update fts_vector column using PG function
        await db.execute(text(
            "UPDATE chunks SET fts_vector = to_tsvector('english', text) WHERE document_id = :doc_id"
        ), {"doc_id": document_id})
        await db.execute(text(
            "UPDATE documents SET status = 'ready' WHERE id = :doc_id"
        ), {"doc_id": document_id})
        await db.commit()

        yield await sse_event("complete", {"document_id": document_id, "total_chunks": total})

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/", response_model=list[DocumentOut])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()

@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    await delete_document_vectors(document_id)
    await db.execute(text("DELETE FROM chunks WHERE document_id = :id"), {"id": document_id})
    await db.execute(text("DELETE FROM documents WHERE id = :id"), {"id": document_id})
    await db.commit()
    return {"deleted": document_id}