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
