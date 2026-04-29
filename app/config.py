from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "semantic_search"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384       # matches all-MiniLM-L6-v2 output
    MAX_FILE_SIZE_MB: int = 10
    DEFAULT_CHUNK_SIZE: int = 512  # tokens / chars
    DEFAULT_CHUNK_OVERLAP: int = 64
    TOP_K: int = 10

    class Config:
        env_file = ".env"

settings = Settings()