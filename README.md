# Semantic Search Platform

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Sora&weight=700&size=22&duration=2800&pause=1000&color=6C63FF&center=true&vCenter=true&width=700&lines=Upload+Documents.+Search+by+Meaning.;Semantic+%C2%B7+Keyword+%C2%B7+Hybrid+RRF+Search;sentence-transformers+%C2%B7+Qdrant+%C2%B7+PostgreSQL;Built+for+developers+who+ship+fast.)](https://git.io/typing-svg)

</div>

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js_16-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-DC244C?style=for-the-badge&logo=qdrant&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)

</div>

---

## Overview

**Semantic Search Platform** is a production-grade document search engine that goes beyond keyword matching. Upload any `.txt`, `.pdf`, or `.md` file and instantly search by meaning — not just words. The platform runs three search strategies in parallel and returns all three results side-by-side so you can see exactly how semantic, keyword, and hybrid search compare on every query.

**Live Dashboard** → [semantic-search-frontend-j6yp.vercel.app/search](https://semantic-search-frontend-j6yp.vercel.app/search)  
**Backend API / Swagger Docs** → *(coming soon — Railway deployment in progress)*

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Stack](#stack)
- [API Reference](#api-reference)
- [Search Strategies](#search-strategies)
- [Environment Variables](#environment-variables)
- [Quick Start](#quick-start)
- [Docker](#docker)
- [Project Structure](#project-structure)
- [Error Handling](#error-handling)
- [Author](#author)

---

## Features

| Feature | Detail |
|---------|--------|
| Semantic Search | Embeds documents and queries using `sentence-transformers/all-MiniLM-L6-v2`, retrieves by cosine similarity via Qdrant |
| Keyword Search | Full-text search using PostgreSQL `tsvector` and `plainto_tsquery` |
| Hybrid RRF Search | Reciprocal Rank Fusion merges semantic and keyword ranked lists into a single superior result set |
| Three-Column Comparison | All three result sets rendered side-by-side — the demo weapon for client calls |
| SSE Upload Progress | Chunk embedding progress streamed to the frontend in real time via Server-Sent Events |
| Multi-Strategy Chunking | Fixed-size, sentence-based, and paragraph-based chunking strategies — user selectable |
| Multi-Format Support | Accepts `.txt`, `.pdf`, and `.md` files up to 10MB |
| Query Logging | Every search logged with query text, type, result count, and latency |
| Health Endpoint | `/health` for uptime monitoring and deployment readiness |
| Swagger / OpenAPI Docs | Full interactive API documentation auto-generated at `/docs` |

---

## Architecture
Browser (Next.js · Vercel)
│
├── HTTP (REST) ──────────── FastAPI (Railway)
│                                │
│                           PostgreSQL (Neon) ── Full-Text Search
│                                │
│                           Qdrant Cloud ──────── Vector Search
│
└── SSE Stream ───────────── FastAPI /documents/upload
│
Streams chunk embedding progress

### Upload & Indexing Flow
File Upload (POST /documents/upload)
│
├── Extract text from file (.txt / .pdf / .md)
├── Split into chunks (fixed / sentence / paragraph)
├── Embed each chunk via sentence-transformers
├── Store vectors + metadata in Qdrant
├── Store chunk text in PostgreSQL for FTS
└── Stream progress events via SSE

### Search Flow
Query (GET /search/?q=...)
│
├── Embed query → Qdrant vector search → semantic results
├── plainto_tsquery → PostgreSQL FTS → keyword results
├── RRF fusion → merge both ranked lists → hybrid results
└── Return all three result sets + latency

---

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy (async), asyncpg |
| Vector Database | Qdrant Cloud |
| Relational Database | PostgreSQL — Neon (serverless) |
| Embedding Model | sentence-transformers `all-MiniLM-L6-v2` (384 dimensions) |
| Search Fusion | Reciprocal Rank Fusion (RRF, k=60) |
| Deployment | Vercel (frontend) + Railway (backend) |
| API Documentation | Swagger UI — auto-generated via FastAPI |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/upload` | Upload a document and stream chunking/embedding progress via SSE |
| `GET` | `/documents/` | List all indexed documents |
| `DELETE` | `/documents/{id}` | Delete a document and its vectors from Qdrant and PostgreSQL |
| `GET` | `/search/` | Run semantic, keyword, and hybrid search — returns all three result sets |
| `GET` | `/health` | Health check — returns service status |

### Request / Response Examples

**Upload a document**
```http
POST /documents/upload?strategy=fixed
Content-Type: multipart/form-data

file: research_paper.pdf
```
event: start
data: {"document_id": "99af...", "total_chunks": 42}
event: progress
data: {"processed": 32, "total": 42, "percent": 76.2}
event: complete
data: {"document_id": "99af...", "total_chunks": 42}

**Search**
```http
GET /search/?q=cardiovascular+risk+reduction&top_k=10
```

```json
{
  "query": "cardiovascular risk reduction",
  "semantic_results": [...],
  "keyword_results": [...],
  "hybrid_results": [...],
  "latency_ms": 312.5
}
```

---

## Search Strategies

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Semantic** | Embeds query → finds nearest vectors in Qdrant by cosine similarity | Conceptual queries, synonyms, paraphrased questions |
| **Keyword** | PostgreSQL `tsvector` full-text index with `ts_rank_cd` scoring | Exact terms, proper nouns, technical identifiers |
| **Hybrid (RRF)** | Scores each result as `Σ 1/(rank + 60)` across both lists | Best general-purpose — combines signal from both |

---

## Environment Variables

### Backend (`.env`)

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=semantic_search
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIM=384
```

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

A fully documented `.env.example` file is included in both repositories.

---

## Quick Start

### Backend

```bash
git clone https://github.com/Fuad-Haque/semantic-search-backend
cd semantic-search-backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
git clone https://github.com/Fuad-Haque/semantic-search-frontend
cd semantic-search-frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Backend runs at `http://localhost:8000` — Swagger docs at `http://localhost:8000/docs`.  
Frontend runs at `http://localhost:3000`.

---

## Docker

```bash
git clone https://github.com/Fuad-Haque/semantic-search-backend
cd semantic-search-backend
cp .env.example .env
docker compose up -d
```

Services started:
- `postgres` — PostgreSQL on port `5432`
- `qdrant` — Qdrant on port `6333`

Run the backend separately with `uvicorn app.main:app --reload` after Docker services are up.

---

## Project Structure

### Backend
semantic-search-backend/
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Settings via pydantic-settings
│   ├── database.py              # Async SQLAlchemy + Qdrant client
│   ├── models/
│   │   ├── document.py          # SQLAlchemy ORM models
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── routers/
│   │   ├── documents.py         # Upload, list, delete
│   │   └── search.py            # Semantic, keyword, hybrid search
│   ├── services/
│   │   ├── chunker.py           # Fixed, sentence, paragraph chunking
│   │   ├── embedder.py          # sentence-transformers wrapper
│   │   ├── vector_store.py      # Qdrant operations
│   │   └── search_service.py    # RRF fusion logic
│   └── utils/
│       └── sse.py               # SSE progress stream helper
├── .env.example
├── docker-compose.yml
├── Procfile
└── requirements.txt

### Frontend
semantic-search-frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx             # Root → redirects to /search
│   │   └── search/
│   │       └── page.tsx         # Main search + upload page
│   ├── components/
│   │   ├── upload/
│   │   │   └── DropZone.tsx     # Drag-and-drop uploader with SSE progress
│   │   └── search/
│   │       ├── SearchBar.tsx    # Debounced search input
│   │       ├── ResultCard.tsx   # Single result with score bar
│   │       └── ComparisonView.tsx # Three-column comparison layout
│   ├── hooks/
│   │   └── useSSE.ts            # SSE upload progress hook
│   └── lib/
│       ├── api.ts               # Typed API client
│       └── types.ts             # TypeScript interfaces
├── .env.local.example
└── package.json

---

## Error Handling

| Status Code | Scenario |
|-------------|----------|
| `200 OK` | Request processed successfully |
| `400 Bad Request` | File too large or unsupported format |
| `404 Not Found` | Document ID does not exist |
| `422 Unprocessable Entity` | Request validation error (Pydantic) |
| `500 Internal Server Error` | Embedding failure or database error |

---

## Author

Built by [Fuad Haque](https://fuadhaque.com)

[fuadhaque.dev@gmail.com](mailto:fuadhaque.dev@gmail.com) · [Book a Call](https://cal.com/fuad-haque) · [GitHub](https://github.com/Fuad-Haque)
