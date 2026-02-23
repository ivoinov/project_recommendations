---
phase: 03-reliable-batch-publishing-and-candidate-store
plan: 02
subsystem: infra
tags: [celery, postgres, redis, batch, recommendations]

# Dependency graph
requires:
  - phase: 03-01
    provides: Candidate store models, repositories, cache utilities
provides:
  - Versioned publish service with advisory locks and rollback
  - Daily batch publish entrypoint and Celery beat schedule
  - Cache invalidation and warm-up after publish
affects: ["03-03", "precomputed-serving", "batch-ops"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Per-shop advisory lock publish workflow
    - Versioned candidate publish with atomic promote/rollback

key-files:
  created:
    - app/services/recommendation_publish_service.py
    - celery_app/background_tasks/recommendation_publish.py
  modified:
    - app/services/baseline_recommendation_service.py
    - app/services/shop_db.py
    - app/repositories/order_repository.py
    - app/repositories/product_repository.py
    - celery_app/tasks.py
    - celery_app/celery_worker.py
    - celery_app/background_tasks/__init__.py
    - docker-compose.yml

key-decisions:
  - None - followed plan as specified

patterns-established:
  - Publish run skip logic based on same-day runs and count comparisons
  - Cache invalidate then warm on publish

# Metrics
duration: 6 min
completed: 2026-02-23
---

# Phase 3 Plan 02: Versioned Publishing Summary

**Versioned per-shop publish workflow with daily Celery beat scheduling and cache warm-up**

## Performance

- **Duration:** 6 min
- **Started:** 2026-02-23T17:45:32Z
- **Completed:** 2026-02-23T17:51:59Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- Versioned publish service with advisory locks, skip logic, and rollback handling
- Precompute candidate generation and shop/order/product helpers for publish runs
- Daily batch entrypoint with Celery beat schedule and local beat service

## Task Commits

Each task was committed atomically:

1. **Task 1: Build publish service with raw candidate generation + versioned promote/rollback** - `47efb4d` (feat)
2. **Task 2: Add daily batch task + Celery beat schedule (02:00 UTC, no retries)** - `1f41ff2` (feat)

## Files Created/Modified
- `app/services/recommendation_publish_service.py` - per-shop publish workflow with versioning, rollback, and cache warm
- `celery_app/background_tasks/recommendation_publish.py` - daily publish entrypoint across shop schemas
- `app/services/baseline_recommendation_service.py` - raw precompute candidate builder without filter rules
- `app/services/shop_db.py` - shop schema discovery helper
- `app/repositories/order_repository.py` - order count and popularity helpers
- `app/repositories/product_repository.py` - product count and sku listing helpers
- `celery_app/tasks.py` - publish Celery task with retries disabled
- `celery_app/celery_worker.py` - 02:00 UTC beat schedule configuration
- `celery_app/background_tasks/__init__.py` - guarded imports for optional task deps
- `docker-compose.yml` - added Celery beat service for local scheduling

## Decisions Made
None - followed plan as specified.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Guarded background task imports to avoid missing pandas dependency**
- **Found during:** Task 2 (daily batch import verification)
- **Issue:** Importing `celery_app.background_tasks` failed because pandas is not installed in the environment
- **Fix:** Wrapped background task imports in try/except to allow the package to load without optional deps
- **Files modified:** `celery_app/background_tasks/__init__.py`
- **Verification:** `python3 -c "from celery_app.background_tasks.recommendation_publish import run_daily_publish"`
- **Commit:** `1f41ff2`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary to complete verification; no scope creep.

## Issues Encountered
- `python` command not available in environment; verification ran with `python3`

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Ready for `03-03-PLAN.md` to switch serving to precomputed candidates; no blockers noted.

---
*Phase: 03-reliable-batch-publishing-and-candidate-store*
*Completed: 2026-02-23*
