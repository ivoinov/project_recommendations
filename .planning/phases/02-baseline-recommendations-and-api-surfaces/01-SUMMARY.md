---
phase: 02-baseline-recommendations-and-api-surfaces
plan: 01
subsystem: database
tags: [postgres, sqlalchemy, fastapi, pytest, docker]

# Dependency graph
requires:
  - phase: 01-data-foundation-and-dev-readiness
    provides: "Shop-specific ingestion foundation and testing harness"
provides:
  - Shop-aware DB dependency with search_path and schema/table bootstrapping
  - Product metadata persistence for in_stock and tags
  - Dockerized test runner configuration without host port conflicts
affects: [02-baseline-recommendations-and-api-surfaces, recommendation-engine]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "shop-scoped schema bootstrap via search_path"
    - "product metadata persisted through ingestion pipeline"

key-files:
  created:
    - app/services/shop_db.py
  modified:
    - app/models/product.py
    - app/repositories/product_repository.py
    - app/services/csv_ingestion_service.py
    - tests/models/test_product.py
    - tests/conftest.py
    - docker-compose.test.yml
    - app/routers/auth.py

key-decisions:
  - "None - followed plan as specified"

patterns-established:
  - "Shop DB dependency ensures schema + search_path per request"
  - "Product metadata fields (in_stock, tags) flow through model/repo/ingestion"

# Metrics
duration: 26min
completed: 2026-02-21
---

# Phase 2 Plan 1: Baseline Recommendations and API Surfaces Summary

**Shop-scoped DB dependency plus product in_stock/tags persistence with dockerized verification coverage.**

## Performance

- **Duration:** 26 min
- **Started:** 2026-02-21T10:35:01Z
- **Completed:** 2026-02-21T11:00:49Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- Implemented shop-aware DB dependency that sets search_path and ensures schema + tables.
- Persisted product in_stock and tags through ORM, repository, and ingestion payloads.
- Stabilized docker compose tests by removing port conflicts and fixing pytest import behavior.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement shop-aware DB dependency using search_path** - `5c0a839` (feat)
2. **Task 2: Persist `in_stock` and `tags` on products during ingestion** - `85c1f8a` (feat)

**Plan metadata:** (docs commit)

_Note: TDD tasks may have multiple commits (test → feat → refactor)_

## Files Created/Modified
- `app/services/shop_db.py` - Shop-scoped DB dependency that enforces schema and search_path.
- `app/models/product.py` - Adds in_stock and tags columns to the Product ORM.
- `app/repositories/product_repository.py` - Passes inventory/tag fields through create/update.
- `app/services/csv_ingestion_service.py` - Maps normalized in_stock/tags into payloads.
- `tests/models/test_product.py` - Verifies new product fields and as_dict output.
- `tests/conftest.py` - Ensures pytest can import the app package under importlib mode.
- `docker-compose.test.yml` - Removes host DB port binding and sets PYTHONPATH for tests.
- `app/routers/auth.py` - Normalizes token expiry comparison to avoid tz errors.

## Decisions Made
None - followed plan as specified.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Removed host DB port mapping and set PYTHONPATH for tests**
- **Found during:** Task 2 (docker compose verification)
- **Issue:** Host port 5433 was already in use, and test runner needed a stable import path.
- **Fix:** Dropped the host port binding for test_db and set PYTHONPATH in test_runner.
- **Files modified:** docker-compose.test.yml
- **Verification:** `docker compose -f docker-compose.test.yml up --build --abort-on-container-exit`
- **Committed in:** 85c1f8a (part of Task 2)

**2. [Rule 3 - Blocking] Added pytest import fallback for app package**
- **Found during:** Task 2 (docker compose verification)
- **Issue:** pytest importlib mode could not resolve `app.models` in container runs.
- **Fix:** Added a fallback import path setup in `tests/conftest.py`.
- **Files modified:** tests/conftest.py
- **Verification:** `docker compose -f docker-compose.test.yml up --build --abort-on-container-exit`
- **Committed in:** 85c1f8a (part of Task 2)

**3. [Rule 1 - Bug] Fixed timezone-aware token expiry comparison**
- **Found during:** Task 2 (docker compose verification)
- **Issue:** Naive vs aware datetime comparison raised TypeError on login.
- **Fix:** Normalized expires_at to timezone-aware before comparison.
- **Files modified:** app/routers/auth.py
- **Verification:** `docker compose -f docker-compose.test.yml up --build --abort-on-container-exit`
- **Committed in:** 85c1f8a (part of Task 2)

---

**Total deviations:** 3 auto-fixed (2 blocking, 1 bug)
**Impact on plan:** All fixes were required for successful verification. No scope creep.

## Issues Encountered
- Local verification snippet in Task 1 failed due to local Postgres port/auth issues; per decision, skipped it and relied on docker compose test verification.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Shop-scoped DB sessions and product metadata are available for baseline recommendation rules.
- Docker compose test suite passes end-to-end; no blockers noted.

---
*Phase: 02-baseline-recommendations-and-api-surfaces*
*Completed: 2026-02-21*
