from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.schemas import SearchResponse
from app.services.search_service import run_all_searches

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    semantic, keyword, hybrid, latency = await run_all_searches(q, db, top_k)
    return SearchResponse(
        query=q,
        semantic_results=semantic,
        keyword_results=keyword,
        hybrid_results=hybrid,
        latency_ms=latency
    )