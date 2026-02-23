---
phase: 03-reliable-batch-publishing-and-candidate-store
verified: 2026-02-23T18:59:22Z
status: human_needed
score: 3/3 must-haves verified
human_verification:
  - test: "Daily publish run executes on schedule"
    expected: "At 02:00 UTC, a publish run executes and creates a RecommendationPublishRun record per shop with status success/failed/skipped."
    why_human: "Requires Celery beat running against a real DB/Redis setup to confirm scheduling and persistence."
  - test: "Precomputed recommendation cache hits"
    expected: "Repeated PDP/cart requests for the same shop/seed/version hit Redis (cache key present) and return the cached payload."
    why_human: "Redis availability and cache hit behavior depend on runtime environment configuration."
  - test: "Rollback endpoint switches versions"
    expected: "POST /v1/shops/{shop_id}/publishes/rollback flips current/previous version and invalidates relevant cache keys."
    why_human: "Needs live data with multiple versions to confirm rollback and cache invalidation effects."
---

# Phase 3: Reliable Batch Publishing and Candidate Store Verification Report

**Phase Goal:** Recommendations refresh daily and serve from versioned, cached precomputed candidates.
**Verified:** 2026-02-23T18:59:22Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Daily batch refresh completes on schedule and reports a successful run status. | ✓ VERIFIED | Celery beat schedule set to 02:00 UTC in `celery_app/celery_worker.py`, task wired in `celery_app/tasks.py`, and runs recorded via `RecommendationPublishRepository.create_run` in `app/services/recommendation_publish_service.py`. |
| 2 | API serves recommendations from a precomputed candidate store with caching enabled. | ✓ VERIFIED | PDP/cart endpoints call precomputed service in `app/routers/baseline_recommendations.py`, which uses cache-aside reads in `app/services/precomputed_recommendation_service.py` with Redis helpers in `app/cache/recommendation_cache.py`. |
| 3 | Recommendation publishes are versioned with atomic promote and rollback available. | ✓ VERIFIED | Publish state model holds current/previous versions in `app/models/recommendation_publish_state.py`, publish workflow updates state in `app/services/recommendation_publish_service.py`, and rollback endpoint updates state in `app/routers/publish_status.py`. |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `app/models/recommendation_candidate.py` | Versioned candidate rows per seed/placement. | ✓ VERIFIED | Model includes seed/placement/type/version fields and is used by repositories and publish service. |
| `app/models/recommendation_publish_state.py` | Current/previous version pointers per placement. | ✓ VERIFIED | `current_version` and `previous_version` fields present and updated in publish/rollback paths. |
| `app/models/recommendation_publish_run.py` | Per-shop publish run status and data counts. | ✓ VERIFIED | Stores run_date/status/counts; written by publish service within shop schema. |
| `app/cache/recommendation_cache.py` | Redis cache access for candidate lists. | ✓ VERIFIED | Cache key builder plus get/set/delete helpers with REDIS_CACHE_URL fallback. |
| `app/repositories/recommendation_candidate_repository.py` | Candidate store persistence helpers. | ✓ VERIFIED | Supports create, read, and version cleanup used by publish and serve paths. |
| `app/repositories/recommendation_publish_repository.py` | Publish state/run metadata helpers. | ✓ VERIFIED | State and run helpers used by publish_status router and publish service. |
| `app/services/recommendation_publish_service.py` | Atomic publish + rollback workflow. | ✓ VERIFIED | Advisories, versioned inserts, state updates, run records, cache invalidation. |
| `celery_app/background_tasks/recommendation_publish.py` | Daily batch entrypoint for publishing candidates. | ✓ VERIFIED | Iterates shops, calls publish service, returns status summary. |
| `celery_app/celery_worker.py` | 02:00 UTC beat schedule for daily publish. | ✓ VERIFIED | `beat_schedule` targets publish task with UTC schedule. |
| `app/services/precomputed_recommendation_service.py` | Read path from candidate store with cache-aside behavior. | ✓ VERIFIED | Reads current version, cache-aside seed candidates, applies business rules. |
| `app/routers/baseline_recommendations.py` | PDP/cart endpoints wired to precomputed candidates. | ✓ VERIFIED | Uses `get_pdp_recommendations` and `get_cart_recommendations`. |
| `app/routers/publish_status.py` | Publish status + rollback endpoints. | ✓ VERIFIED | Exposes status and rollback with cache invalidation. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `app/repositories/recommendation_publish_repository.py` | `app/models/recommendation_publish_state.py` | `update_publish_state` | ✓ WIRED | Repository reads/writes publish state model. |
| `app/repositories/recommendation_candidate_repository.py` | `app/models/recommendation_candidate.py` | `create_candidates` | ✓ WIRED | Candidate repository creates rows for candidate model. |
| `app/cache/recommendation_cache.py` | Redis client | `get/set/delete` | ✓ WIRED | Redis client created from REDIS_CACHE_URL/CELERY_BROKER_URL. |
| `app/services/recommendation_publish_service.py` | Publish state updates | DB transaction | ✓ WIRED | Updates `RecommendationPublishState` directly inside `db.begin()`. |
| `celery_app/background_tasks/recommendation_publish.py` | `app/services/recommendation_publish_service.py` | `publish_shop_candidates` | ✓ WIRED | Daily task calls publish service per shop. |
| `celery_app/celery_worker.py` | `celery_app/tasks.py` | Beat schedule | ✓ WIRED | Beat schedule targets `celery_app.tasks.publish_recommendations`. |
| `app/routers/baseline_recommendations.py` | `app/services/precomputed_recommendation_service.py` | Serve-time fetch | ✓ WIRED | Router uses precomputed service for PDP/cart. |
| `app/services/precomputed_recommendation_service.py` | `app/cache/recommendation_cache.py` | Cache-aside read | ✓ WIRED | Uses `get_cached_candidates` and `set_cached_candidates`. |
| `app/routers/publish_status.py` | `app/repositories/recommendation_publish_repository.py` | Status + rollback | ✓ WIRED | Uses `get_state` and `update_publish_state`. |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
| ----------- | ------ | -------------- |
| DATA-03 | ? NEEDS HUMAN | Requires live batch run confirmation. |
| SRV-02 | ? NEEDS HUMAN | Cache behavior depends on Redis availability in runtime. |
| OPS-01 | ? NEEDS HUMAN | Reliability needs runtime observation. |
| OPS-02 | ? NEEDS HUMAN | Rollback behavior needs live versioned data. |

### Anti-Patterns Found

None detected in phase-related files.

### Human Verification Required

1. Daily publish run executes on schedule

**Test:** Run Celery beat/worker and wait for 02:00 UTC execution.
**Expected:** `RecommendationPublishRun` row created per shop with success/failed/skipped.
**Why human:** Requires runtime scheduling and DB persistence confirmation.

2. Precomputed recommendation cache hits

**Test:** Call PDP/cart endpoints twice for same shop/seed/version with Redis configured.
**Expected:** Second call uses cached payload (Redis key exists).
**Why human:** Cache hit depends on runtime Redis configuration.

3. Rollback endpoint switches versions

**Test:** Call rollback with a placement after multiple publishes.
**Expected:** `current_version` and `previous_version` swap and cache keys are invalidated.
**Why human:** Needs live publish history and cache state.

### Gaps Summary

No code-level gaps identified. Runtime verification is needed to confirm scheduling, cache hits, and rollback behavior with real data.

---

_Verified: 2026-02-23T18:59:22Z_
_Verifier: OpenCode (gsd-verifier)_
