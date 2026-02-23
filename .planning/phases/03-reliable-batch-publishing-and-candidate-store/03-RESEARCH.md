# Phase 03: Reliable Batch Publishing and Candidate Store - Research

**Researched:** 2026-02-23
**Domain:** Batch scheduling, versioned publishing, candidate store, caching
**Confidence:** MEDIUM

## Summary

This phase is about running a reliable daily batch job that computes recommendation candidates, publishing them in a versioned store, and serving from cache-backed precomputed results. The core constraints from context (single 02:00 UTC schedule, per-shop runs only for new data, no same-day retries, atomic per-shop promote/rollback, and cache invalidation/warming) require a job runner that can be scheduled, a store that supports atomic pointer updates, and a cache strategy that is safe during publish transitions.

The standard implementation uses managed Postgres for the candidate store and publish metadata plus Redis for caching, with scheduled batch execution handled by Cloud Scheduler + Cloud Run Jobs (GCP) or EventBridge Scheduler + an App Runner HTTP-triggered worker (AWS). Postgres transactions provide the atomic promote/rollback semantics. Postgres advisory locks are a simple and reliable mechanism to prevent concurrent runs per shop.

**Primary recommendation:** Use versioned candidate rows plus a per-shop publish pointer updated in a single transaction, and schedule daily jobs via Cloud Scheduler/Cloud Run Jobs (GCP) or EventBridge Scheduler/App Runner (AWS), with Redis cache invalidation and warm-up on publish.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PostgreSQL | 18 (current docs) | Versioned candidate store, publish metadata, atomic promote/rollback | Transactions and advisory locks support atomic publish and per-shop concurrency control. |
| Redis | 8.6 (current commands reference) | Cache for precomputed candidates | Fast cache with standard GET/SET/DEL/MGET primitives. |
| Cloud Run Jobs (GCP) | Current | Batch execution platform | Jobs run tasks to completion and exit; tasks can retry and be parallelized. |
| Cloud Scheduler (GCP) | Current | Daily cron scheduling | Schedules recurring jobs via cron expressions. |
| EventBridge Scheduler (AWS) | Current | Daily cron scheduling | Serverless scheduler with cron/rate, retries, and at-least-once delivery. |
| AWS App Runner | Current | HTTP worker for batch execution on AWS | Managed web app hosting; can be triggered by scheduled HTTP requests. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pgvector | Current | Vector storage if needed | Only if Phase 2 vector features are used in candidate computation. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Cloud Run Jobs + Cloud Scheduler | App Runner + EventBridge Scheduler | Cloud Run Jobs is purpose-built for batch jobs; App Runner is a web app host and relies on HTTP triggers for batch. |
| Redis cache | Database-only reads | Simpler, but higher latency and load on Postgres; violates SRV-02 caching requirement. |

**Installation:**
```bash
npm install pg redis
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── jobs/                # batch entrypoints (daily publish)
├── publish/             # versioning, promote/rollback logic
├── store/               # candidate store repository
├── cache/               # redis cache utilities + invalidation
└── api/                 # read path: serve candidates
```

### Pattern 1: Versioned Candidate Store + Publish Pointer
**What:** Write candidates into immutable, versioned rows; atomically update a per-shop pointer to the current version and previous version.
**When to use:** Any time you need atomic promote/rollback and partial shop failures.
**Example:**
```sql
-- Source: https://www.postgresql.org/docs/current/tutorial-transactions.html
BEGIN;
  -- insert candidates with version = :new_version
  -- update publish pointer for shop_id in one transaction
COMMIT;
```

### Pattern 2: Per-Shop Concurrency Guard
**What:** Use advisory locks per shop to prevent concurrent runs from overlapping.
**When to use:** Daily batch jobs with overlapping execution windows or manual triggers.
**Example:**
```sql
-- Source: https://www.postgresql.org/docs/current/explicit-locking.html
-- Advisory locks are application-defined and released at transaction end.
```

### Pattern 3: Cache-Aside with Publish Invalidate + Warm
**What:** Read from Redis cache; on miss, fetch from Postgres, apply serve-time rules, then cache. On publish, invalidate shop-specific keys and warm cache.
**When to use:** SRV-02 requirement with cache live until next publish.
**Example:**
```javascript
// Source: https://redis.io/docs/latest/commands/get/ and /set/
await redis.get(cacheKey);
await redis.set(cacheKey, payload, { EX: ttlSeconds });
```

### Anti-Patterns to Avoid
- **In-place candidate updates:** breaks atomic promote/rollback; use versioned rows and pointer updates instead.
- **Implicit retries:** Cloud Run Jobs and EventBridge Scheduler support retries by default; disable to honor no same-day retries.
- **Global cache flush:** too destructive; invalidate by shop/version instead.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Job scheduling | Custom cron runner | Cloud Scheduler or EventBridge Scheduler | Managed reliability, cron support, retries control. |
| Concurrency control | DIY lock tables | Postgres advisory locks | Built-in cleanup on transaction/session end. |
| Atomic publish | Multi-step updates without transactions | Postgres transactions | Atomicity for promote/rollback. |
| Cache primitives | In-memory singleton | Redis GET/SET/DEL/MGET | Durable, shared cache with standard commands. |

**Key insight:** The combination of Postgres transactions + advisory locks + Redis cache is simpler and more reliable than bespoke coordination logic.

## Common Pitfalls

### Pitfall 1: Implicit retries violate no-retry policy
**What goes wrong:** Cloud Run Jobs and EventBridge Scheduler retry tasks by default, causing same-day re-runs.
**Why it happens:** Default max-retries is non-zero (Cloud Run Jobs defaults to 3).
**How to avoid:** Set job task retries to 0 and scheduler retry limits to 0.
**Warning signs:** Multiple executions for the same shop/version on the same day.

### Pitfall 2: Non-atomic promote causes mixed versions
**What goes wrong:** API reads candidates from a partially updated version.
**Why it happens:** Publish logic updates candidates and the version pointer separately without a transaction.
**How to avoid:** Use a single transaction to insert candidates and update publish pointer; serve by pointer only.
**Warning signs:** Two versions reported as current, or missing candidates right after publish.

### Pitfall 3: Cache invalidation races
**What goes wrong:** Cache serves stale or empty data after publish.
**Why it happens:** Invalidating keys before the pointer update or without warm-up.
**How to avoid:** Update pointer first, then invalidate, then warm cache; serve stale if cache miss.
**Warning signs:** Post-publish cache miss spikes or empty responses.

### Pitfall 4: Long-running transactions
**What goes wrong:** Locks are held too long, blocking other shops.
**Why it happens:** Computing candidates inside the same transaction as the publish update.
**How to avoid:** Compute candidates outside the transaction; use a short transaction for insert + pointer update.
**Warning signs:** Elevated lock waits or deadlocks.

## Code Examples

Verified patterns from official sources:

### Atomic transaction block
```sql
-- Source: https://www.postgresql.org/docs/current/tutorial-transactions.html
BEGIN;
  -- multiple related updates
COMMIT;
```

### Redis cache access
```javascript
// Source: https://redis.io/docs/latest/commands/get/
// Source: https://redis.io/docs/latest/commands/set/
// Source: https://redis.io/docs/latest/commands/del/
await redis.set(key, value);
const cached = await redis.get(key);
await redis.del(key);
```

### Multi-key fetch
```javascript
// Source: https://redis.io/docs/latest/commands/mget/
const values = await redis.mGet([key1, key2, key3]);
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Compute on request | Daily precompute + versioned publish + cache | Ongoing best practice | Predictable latency and rollback safety. |

**Deprecated/outdated:**
- In-place overwrites without versioning: breaks rollback and violates atomic publish requirements.

## Open Questions

1. **Which hosting path (App Runner vs Cloud Run) is chosen?**
   - What we know: Both are allowed for v1 hosting.
   - What's unclear: Scheduler/runner integration differs (Cloud Run Jobs vs App Runner HTTP trigger).
   - Recommendation: Decide before planning tasks so infra steps are concrete.

## Sources

### Primary (HIGH confidence)
- https://cloud.google.com/run/docs/create-jobs - Cloud Run Jobs create/update and task behavior
- https://cloud.google.com/run/docs/execute/jobs - Job execution semantics
- https://docs.cloud.google.com/scheduler/docs - Cloud Scheduler overview and cron scheduling
- https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html - EventBridge Scheduler features and retries
- https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html - App Runner web app hosting model
- https://www.postgresql.org/docs/current/tutorial-transactions.html - Transaction atomicity
- https://www.postgresql.org/docs/current/explicit-locking.html - Advisory lock concepts
- https://redis.io/docs/latest/commands/get/ - Redis GET
- https://redis.io/docs/latest/commands/set/ - Redis SET
- https://redis.io/docs/latest/commands/del/ - Redis DEL
- https://redis.io/docs/latest/commands/mget/ - Redis MGET

### Secondary (MEDIUM confidence)
- https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS - Advisory lock functions list (use for exact function names)

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - cloud provider choice not finalized; Postgres/Redis versions vary by managed service.
- Architecture: MEDIUM - based on standard transactional + cache patterns.
- Pitfalls: MEDIUM - derived from scheduler/job defaults and publish race conditions.

**Research date:** 2026-02-23
**Valid until:** 2026-03-25
