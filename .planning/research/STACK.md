# Stack Research

**Domain:** Ecommerce recommendation service (FastAPI backend, batch + online recs)
**Researched:** 2026-02-17
**Confidence:** MEDIUM

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.14.3 | Runtime for API + batch ML jobs | Latest stable Python with broad library support and performance improvements; aligns with FastAPI ecosystem. Confidence: HIGH. |
| FastAPI | 0.129.0 | Online recommendation API | High-performance ASGI framework already in use; strong typing and validation for request/response contracts. Confidence: HIGH. |
| PostgreSQL | 18.2 | Primary data store + feature storage | Mature relational core for catalog/behavior data, supports pgvector extension and analytical queries in one system. Confidence: HIGH. |
| Redis (server) | 8.2.4 | Broker + low-latency cache | Stable Redis 8.x for Celery broker and hot cache, compatible with current redis-py support matrix. Confidence: MEDIUM. |
| Celery | 5.6.2 | Batch jobs for daily refresh | Production-stable task queue that fits the existing batch architecture and retry semantics. Confidence: HIGH. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| SQLAlchemy | 2.0.46 | ORM/query layer | Keep DB interactions consistent and efficient for both features and logging pipelines. Confidence: HIGH. |
| psycopg | 3.3.2 | PostgreSQL driver | Use for all new DB access; Psycopg 3 is the current adapter. Confidence: HIGH. |
| redis (redis-py) | 7.2.0 | Redis client | Required for broker/caching access; align with Redis 8.2.x server. Confidence: HIGH. |
| Pydantic | 2.12.5 | Schema validation | Ensure strict model IO, feature payload validation, and fast serialization. Confidence: HIGH. |
| Uvicorn | 0.41.0 | ASGI server | Low-latency server for FastAPI with standard extras in production. Confidence: HIGH. |
| pgvector (python) | 0.4.2 | Vector type support | Use when storing embeddings in PostgreSQL and querying with HNSW/IVFFLAT indexes. Confidence: HIGH. |
| sentence-transformers | 5.2.3 | Embeddings for cold-start + content recs | Generate product/text embeddings for content-based and cold-start coverage. Confidence: HIGH. |
| scikit-learn | 1.8.0 | Classical ML + TF-IDF | Baseline models, TF-IDF, and offline evaluation; lightweight for batch jobs. Confidence: HIGH. |
| implicit | 0.7.2 | Collaborative filtering (ALS/BPR) | Use for people-also-bought and implicit feedback matrix factorization in batch. Confidence: MEDIUM (latest release is older but still standard). |
| faiss-cpu | 1.13.2 | ANN indexing (optional) | Use if embedding search must stay in-memory or scale beyond Postgres vector indexes. Confidence: MEDIUM. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Docker + Compose | Local and prod parity | Keep services Dockerized to match current deployment constraint. |
| PgBouncer | Connection pooling | Stabilizes DB load for mixed batch/online traffic; deploy as sidecar. |

## Installation

```bash
# Core
pip install fastapi==0.129.0 celery==5.6.2

# Supporting
pip install "uvicorn==0.41.0" "pydantic==2.12.5" "SQLAlchemy==2.0.46" "psycopg==3.3.2" "redis==7.2.0" "pgvector==0.4.2"

# Recs/ML
pip install "sentence-transformers==5.2.3" "scikit-learn==1.8.0" "implicit==0.7.2" "faiss-cpu==1.13.2"
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| PostgreSQL + pgvector | Faiss-only ANN service | Choose Faiss-only if you need ultra-low-latency vector search at very large scale or separate GPU indexing. |
| Celery | RQ/Arq | Choose lighter queues for small job volumes or if you want Redis-only workers with simpler ops. |
| sentence-transformers | TF-IDF only | Use TF-IDF-only when you need low compute cost and can accept weaker cold-start quality. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| psycopg2 (for new code) | Legacy adapter; Psycopg 3 is the current recommended driver for new development. | psycopg 3.3.2 |
| Redis server 8.6.x without client validation | redis-py 7.2.0 officially lists support through Redis 8.2.x; upgrade only after compatibility checks. | Redis 8.2.4 + redis-py 7.2.0 |

## Stack Patterns by Variant

**If you need <200ms p95 with daily batch refresh:**
- Use PostgreSQL + pgvector for retrieval and Redis for caching hot recs
- Because it minimizes infra changes and keeps online latency low

**If catalog size grows beyond Postgres vector performance:**
- Add Faiss for ANN + keep Postgres as source of truth
- Because Faiss handles large-scale vector search with lower latency

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| FastAPI 0.129.0 | Python 3.10+ (use 3.14.3) | FastAPI PyPI metadata lists Python >=3.10. |
| scikit-learn 1.8.0 | Python 3.11+ | PyPI metadata lists Python >=3.11. |
| redis-py 7.2.0 | Redis 8.2.x | Client docs list support through Redis 8.2. |
| psycopg 3.3.2 | PostgreSQL 18.2 | Psycopg 3 is the current adapter; use with latest server. |

## Sources

- https://www.python.org/downloads/ — Python 3.14.3 latest release
- https://pypi.org/project/fastapi/ — FastAPI 0.129.0
- https://pypi.org/project/celery/ — Celery 5.6.2
- https://www.postgresql.org/ — PostgreSQL 18.2
- https://github.com/redis/redis/releases — Redis 8.2.4/8.6.0 release stream
- https://pypi.org/project/redis/ — redis-py 7.2.0 and supported Redis versions
- https://pypi.org/project/SQLAlchemy/ — SQLAlchemy 2.0.46
- https://pypi.org/project/pydantic/ — Pydantic 2.12.5
- https://pypi.org/project/uvicorn/ — Uvicorn 0.41.0
- https://pypi.org/project/psycopg/ — psycopg 3.3.2
- https://pypi.org/project/pgvector/ — pgvector 0.4.2
- https://pypi.org/project/scikit-learn/ — scikit-learn 1.8.0
- https://pypi.org/project/sentence-transformers/ — sentence-transformers 5.2.3
- https://pypi.org/project/implicit/ — implicit 0.7.2
- https://pypi.org/project/faiss-cpu/ — faiss-cpu 1.13.2

---
*Stack research for: Ecommerce recommendation service (FastAPI backend)*
*Researched: 2026-02-17*
