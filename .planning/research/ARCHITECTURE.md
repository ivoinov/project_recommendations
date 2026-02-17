# Architecture Research

**Domain:** ecommerce recommendation service (upsell + content-based recs)
**Researched:** 2026-02-17
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Client / Commerce Platform                          │
├──────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐         ┌───────────────────────┐                  │
│  │ Magento Store │  HTTP   │  Recommendation API   │                  │
│  │ PDP / Cart    │ ───────▶│  (FastAPI)            │                  │
│  └───────────────┘         └───────────┬───────────┘                  │
│                                      │                                 │
├──────────────────────────────────────┴────────────────────────────────┤
│                       Online Serving Layer                             │
├──────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌─────────────────┐  ┌──────────────────────────┐ │
│  │ Rules/Filters │  │ Ranker/Fallback │  │ Cache (Redis)            │ │
│  └───────┬───────┘  └────────┬────────┘  └───────────┬──────────────┘ │
│          │                   │                      │                │
├──────────┴───────────────────┴──────────────────────┴────────────────┤
│                       Offline Pipeline Layer                           │
├──────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────┐ │
│  │ Celery Scheduler  │  │ Celery Workers     │  │ Feature Builder  │ │
│  └─────────┬─────────┘  └─────────┬──────────┘  └─────────┬────────┘ │
│            │                      │                     │           │
├────────────┴──────────────────────┴─────────────────────┴───────────┤
│                          Data / Storage Layer                          │
├──────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌────────────────────┐  ┌───────────────────────┐ │
│  │ PostgreSQL    │  │ Redis (broker)    │  │ Metrics / Logs         │ │
│  │ Catalog/Orders│  │ + cache           │  │ (Prometheus/ELK/etc.)  │ │
│  └───────────────┘  └────────────────────┘  └───────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Magento integration | Source of catalog, orders, product attributes, inventory state | API/DB sync jobs, nightly exports |
| Ingestion/ETL | Normalize Magento data into analytics schema | Celery ETL tasks into PostgreSQL |
| Feature builder | Construct item features and co-occurrence matrices | Celery tasks, SQL aggregates |
| Recommender jobs | Build people-also-bought and content-based candidate sets | Celery tasks, Python/SQL |
| Recommendation store | Persist precomputed candidates and scores | PostgreSQL tables, partitioned by model/date |
| Online API | Serve recs under latency budget, apply rules | FastAPI endpoints, pydantic models |
| Rules/filters | Remove OOS, dedupe, enforce business constraints | In-process service layer |
| Ranker/fallback | Combine candidates, fallback to popularity or content | Service layer, cached lookups |
| Cache | Hot path caching of rec sets and product lookups | Redis |
| Observability | Track latency, hit rates, CTR, failures | Metrics + structured logs |

## Recommended Project Structure

```
src/
├── api/                 # FastAPI routers and request models
│   ├── routes/          # PDP/cart recommendation endpoints
│   └── deps.py          # dependency wiring
├── services/            # orchestration and business rules
│   ├── ranking.py       # ranking + fallback ladder
│   └── filters.py       # availability/dedupe/constraints
├── recommenders/        # algorithm-specific logic
│   ├── cooccurrence.py  # people-also-bought
│   └── content_based.py # similarity-based recs
├── jobs/                # Celery tasks and schedules
│   ├── tasks.py         # batch recompute tasks
│   └── schedules.py     # daily refresh cadence
├── etl/                 # Magento data ingestion
│   ├── loaders.py       # pull/export/transform
│   └── schemas.py       # staging/analytics schemas
├── stores/              # data access layer
│   ├── postgres.py      # queries and transaction helpers
│   └── redis.py         # cache/broker helpers
├── observability/       # metrics, tracing, logging
└── config/              # settings, env, feature flags
```

### Structure Rationale

- **api/:** Keeps request/response shape isolated from algorithm changes.
- **recommenders/:** Algorithm code stays independent of serving rules.
- **jobs/:** Batch workflows are versioned alongside code, not ad-hoc scripts.

## Architectural Patterns

### Pattern 1: Two-stage recommendation (candidate generation + ranking)

**What:** Generate candidates (co-occurrence or content similarity), then apply ranking and business rules.
**When to use:** When you need multiple algorithms and low latency.
**Trade-offs:** More moving parts, but easier to tune and test.

**Example:**
```python
def recommend_for_pdp(product_id: int, limit: int = 10) -> list[int]:
    candidates = cooccurrence_candidates(product_id)
    if not candidates:
        candidates = content_based_candidates(product_id)
    filtered = apply_inventory_and_category_filters(candidates)
    return rank_with_business_rules(filtered, limit=limit)
```

### Pattern 2: Offline precompute + online serving

**What:** Daily batch jobs compute recommendation sets; API reads precomputed results.
**When to use:** When latency is strict and data refresh is daily.
**Trade-offs:** Recommendations are slightly stale; fixes require batch rerun.

**Example:**
```python
@celery.task
def rebuild_pab_candidates(run_date: str) -> None:
    pairs = compute_order_cooccurrence(run_date)
    write_candidate_sets(pairs, table="rec_pab_daily")
```

### Pattern 3: Fallback ladder for cold start

**What:** Try strongest signal first, then degrade to weaker signals.
**When to use:** Cold start or sparse interaction data.
**Trade-offs:** More logic, but fewer empty carousels.

## Data Flow

### Request Flow

```
Shopper views PDP/cart
    ↓
Magento frontend → FastAPI /recommendations
    ↓
Cache lookup → Recommendation store (PostgreSQL)
    ↓
Rules/filters → Ranker/fallback
    ↓
Response (<= 200ms p95)
```

### Recommendation State Updates

```
Magento catalog/orders → ETL → PostgreSQL
    ↓
Celery batch jobs → candidate sets → recommendation store
    ↓
Cache warmup / invalidate
```

### Key Data Flows

1. **People-also-bought:** Orders → co-occurrence counts → candidate sets → PDP upsell.
2. **Content-based:** Catalog attributes → similarity vectors → candidate sets → PDP/cart fallback.
3. **Feedback loop:** Exposure/click events → interaction tables → next daily refresh.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Single FastAPI service + daily Celery batch is sufficient |
| 1k-100k users | Add Redis cache for hot SKUs, optimize SQL indexes, partition rec tables |
| 100k+ users | Split ETL/batch from serving, introduce vector index or search service |

### Scaling Priorities

1. **First bottleneck:** DB queries for rec lookups → add cache and tuned indexes.
2. **Second bottleneck:** Batch job duration → parallelize Celery tasks, incremental updates.

## Anti-Patterns

### Anti-Pattern 1: Compute recommendations in request path

**What people do:** Run heavy similarity or co-occurrence on every request.
**Why it's wrong:** Breaks p95 latency and increases DB load.
**Do this instead:** Precompute daily and serve from cached tables.

### Anti-Pattern 2: No fallback for cold start

**What people do:** Return empty arrays for new products/users.
**Why it's wrong:** Reduces engagement and makes experiments noisy.
**Do this instead:** Use fallback ladder (content-based, category popular, global popular).

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Magento | API/DB export → ETL | Source of catalog, orders, stock state |
| CDN/Frontend | HTTP calls to FastAPI | Keep response payload stable |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| FastAPI ↔ recommender store | SQL queries | Keep queries indexed and bounded |
| Celery ↔ PostgreSQL | Batch writes | Use idempotent upserts per run_date |
| FastAPI ↔ Redis | Cache get/set | Cache by product_id + rec_type |

## Sources

- https://developers.google.com/machine-learning/recommendation/overview (HIGH)
- https://developers.google.com/machine-learning/recommendation/overview/candidate-generation (HIGH)
- https://docs.aws.amazon.com/personalize/latest/dg/how-it-works.html (MEDIUM)

---
*Architecture research for: ecommerce recommendation service*
*Researched: 2026-02-17*
