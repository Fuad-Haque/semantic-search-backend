from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class DocumentOut(BaseModel):
    id: UUID
    filename: str
    total_chunks: int
    token_count: int
    embedding_model: str
    chunk_strategy: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class SearchResult(BaseModel):
    document_id: UUID
    document_name: str
    chunk_index: int
    chunk_text: str
    similarity_score: float
    search_type: str    # "semantic" | "keyword" | "hybrid"

class SearchResponse(BaseModel):
    query: str
    semantic_results: list[SearchResult]
    keyword_results: list[SearchResult]
    hybrid_results: list[SearchResult]
    latency_ms: float