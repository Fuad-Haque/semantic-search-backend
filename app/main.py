from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, search
from app.database import engine
from app.models.document import Base

app = FastAPI(
    title="Semantic Search Platform",
    description="Upload documents, search by meaning.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(search.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "semantic-search-api"}