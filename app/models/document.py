from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class ChunkStrategy(str, enum.Enum):
    FIXED = "fixed"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100))
    total_chunks = Column(Integer, default=0)
    token_count = Column(Integer, default=0)
    embedding_model = Column(String(100))
    chunk_strategy = Column(String(50))
    status = Column(String(50), default="pending")   # pending | processing | ready | failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False)
    chunk_index = Column(Integer)
    text = Column(Text, nullable=False)
    fts_vector = Column(TSVECTOR)   # PostgreSQL full-text search vector
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text = Column(Text)
    search_type = Column(String(50))   # semantic | keyword | hybrid
    results_count = Column(Integer)
    latency_ms = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())