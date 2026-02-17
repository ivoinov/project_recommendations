# Project Research Summary

**Project:** FastAPI Recommendation System
**Domain:** ecommerce recommendation service (PDP/cart upsell, batch + online serving)
**Researched:** 2026-02-17
**Confidence:** MEDIUM

## Executive Summary

This project is an ecommerce recommendation service that serves PDP/cart upsell widgets using an offline-precompute + online-serving architecture. The research points to a classic two-stage pattern: daily batch jobs build candidate sets from catalog and order data, and a low-latency API applies rules, ranking, and fallback logic under a strict <200ms p95 budget. Success depends on reliable data ingestion, cold-start coverage, and operational stability more than on complex real-time ML.

The recommended approach keeps the existing FastAPI + Celery + Postgres + Redis stack, adds explicit data-quality gates during ingestion, and uses content-based similarity alongside co-purchase to cover cold-start gaps. Business rules, inventory filters, and caching are treated as first-class serving concerns, while analytics and experimentation provide the feedback loop for tuning and trust.

Key risks include noisy catalog data degrading relevance, batch jobs overwriting good outputs with partial results, and latency regressions from heavy request-path work. Mitigations are well-known: validation pipelines, versioned/atomic publishes with rollback, and precompute + cache with strict timeouts. The roadmap should sequence phases around these dependencies and pitfalls.

## Key Findings

### Recommended Stack

See `.planning/research/STACK.md` for detailed versions and rationale. The stack is optimized for low-latency serving with daily batch refresh and minimizes infra change by leaning on Postgres + Redis. Python/FastAPI/Celery are already in place and recommended to keep, with pgvector or optional Faiss for embeddings if scale demands it.

**Core technologies:**
- Python 3.14.3: API + batch runtime — strong library compatibility and performance.
- FastAPI 0.129.0: serving layer — high-performance ASGI with typed contracts.
- PostgreSQL 18.2: primary data/feature store — mature relational core with pgvector.
- Redis 8.2.4: broker + cache — low-latency hot-path caching.
- Celery 5.6.2: batch jobs — stable task queue for daily refreshes.

### Expected Features

See `.planning/research/FEATURES.md` for full landscape. MVP focuses on ingestion, PDP/cart APIs, co-purchase + content-based fallbacks, rules, and analytics; differentiators like hybrid ranking and contextual reranking follow once baseline metrics stabilize.

**Must have (table stakes):**
- Catalog + order ingestion — enables all downstream rec computation.
- PDP/cart placement APIs — deliver recs to core surfaces.
- People-also-bought + content-based similarity — relevance plus cold-start coverage.
- Business rules/filters — in-stock, exclusions, dedupe, guardrails.
- Basic analytics logging — CTR/add-to-cart measurement.

**Should have (competitive):**
- Hybrid ranking — blends co-purchase and content for robustness.
- Contextual reranking — cart/device/locale signals.
- Diversity controls — avoid repetitive lists.

**Defer (v2+):**
- Session-aware personalization — data volume + privacy review needed.
- Merchandising control plane — higher complexity, stakeholder alignment.
- Automated quality monitoring — justify after scale.

### Architecture Approach

See `.planning/research/ARCHITECTURE.md` for full diagrams. Recommended architecture is offline precompute with online serving: ETL normalizes Magento data into Postgres; Celery builds candidate sets; FastAPI serves recs with rules, ranking, and cache.

**Major components:**
1. Ingestion/ETL + feature builder — normalize catalog/orders and compute features.
2. Recommender jobs + recommendation store — precompute candidates and persist versions.
3. Online API + rules/ranker/cache — low-latency serving with fallbacks and filters.
4. Observability — latency, CTR, freshness, job health.

### Critical Pitfalls

Top risks from `.planning/research/PITFALLS.md` and how to avoid them:

1. **Noisy catalog data** — add validation and normalization gates before feature generation.
2. **Cold-start treated as an afterthought** — implement explicit content-based and category-popularity fallbacks.
3. **Partial/stale batch publishes** — use versioned tables/keys with atomic promote + rollback.
4. **Latency regressions in serving layer** — precompute and cache; avoid heavy request-path joins.
5. **Offline-only evaluation** — plan for online experimentation and business metrics.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Data Foundation + Quality Gates
**Rationale:** All recommendation quality depends on clean catalog/order data.
**Delivers:** Magento ingest, normalization, validation, schemas, baseline metrics logging.
**Addresses:** Catalog/order ingestion, analytics logging.
**Avoids:** Noisy catalog data pitfall.

### Phase 2: Baseline Recommendations (PDP/Cart)
**Rationale:** Ship table-stakes relevance and cold-start coverage quickly.
**Delivers:** People-also-bought + content-based candidates, placement APIs, rules/filters, fallback ladder.
**Addresses:** PDP/cart APIs, co-purchase, content-based, business rules, fallback strategy.
**Avoids:** Cold-start gaps; promo-bias via basic decay/filters.

### Phase 3: Serving Reliability + Latency Hardening
**Rationale:** Protect UX and prevent regression as load grows.
**Delivers:** Redis caching, denormalized read paths, timeouts, versioned batch publish/rollback.
**Addresses:** Performance targets (<200ms p95), batch stability, cache strategy.
**Avoids:** Latency regressions; partial/stale batch publishes.

### Phase 4: Measurement + Ranking Improvements
**Rationale:** Optimize with data after baseline is stable.
**Delivers:** Online experimentation, hybrid ranking, contextual reranking, diversity controls.
**Addresses:** Hybrid ranking, contextual signals, diversity, evaluation.
**Avoids:** Offline-only evaluation; relevance drops from untuned rankers.

### Phase Ordering Rationale

- Ingestion and validation are prerequisites for any rec computation and must land first.
- Candidate generation + API delivery are the core MVP; rules and fallbacks are required for safety and cold-start.
- Reliability and latency hardening stabilize production before adding complexity.
- Ranking improvements and experimentation depend on reliable logging and serving.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** Magento integration details and data quality rules vary per client.
- **Phase 4:** Experimentation framework and metrics governance require stakeholder alignment.

Phases with standard patterns (skip research-phase):
- **Phase 2:** Co-purchase + content-based baseline recs are well-established patterns.
- **Phase 3:** Cache + versioned batch publish patterns are standard for offline/online serving.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions sourced from official docs and aligns with existing stack constraints. |
| Features | MEDIUM | Based mostly on domain knowledge; no external sources. |
| Architecture | HIGH | Standard rec system patterns with reputable references. |
| Pitfalls | MEDIUM | Largely experience-based; validate in discovery. |

**Overall confidence:** MEDIUM

### Gaps to Address

- Magento data specifics (fields, availability rules, returns/refunds) — confirm with actual data exports.
- Experimentation and analytics definitions (CTR, AOV, attach rate) — align with stakeholders.
- Scaling thresholds for pgvector vs Faiss — validate with catalog size and latency targets.

## Sources

### Primary (HIGH confidence)
- https://www.python.org/downloads/ — Python 3.14.3 release
- https://pypi.org/project/fastapi/ — FastAPI 0.129.0
- https://www.postgresql.org/ — PostgreSQL 18.2
- https://pypi.org/project/SQLAlchemy/ — SQLAlchemy 2.0.46
- https://pypi.org/project/pydantic/ — Pydantic 2.12.5
- https://pypi.org/project/psycopg/ — psycopg 3.3.2
- https://pypi.org/project/redis/ — redis-py 7.2.0
- https://pypi.org/project/pgvector/ — pgvector 0.4.2
- https://developers.google.com/machine-learning/recommendation/overview — rec system overview
- https://developers.google.com/machine-learning/recommendation/overview/candidate-generation — candidate generation pattern

### Secondary (MEDIUM confidence)
- https://pypi.org/project/celery/ — Celery 5.6.2
- https://pypi.org/project/uvicorn/ — Uvicorn 0.41.0
- https://pypi.org/project/scikit-learn/ — scikit-learn 1.8.0
- https://pypi.org/project/sentence-transformers/ — sentence-transformers 5.2.3
- https://pypi.org/project/implicit/ — implicit 0.7.2
- https://pypi.org/project/faiss-cpu/ — faiss-cpu 1.13.2
- https://docs.aws.amazon.com/personalize/latest/dg/how-it-works.html — personalization patterns

### Tertiary (LOW confidence)
- Personal experience / known ecommerce recommendation pitfalls — validate during discovery

---
*Research completed: 2026-02-17*
*Ready for roadmap: yes*
