---
phase: 02-baseline-recommendations-and-api-surfaces
plan: 02
subsystem: api
tags: [fastapi, sqlalchemy, postgres, pytest]

# Dependency graph
requires:
  - phase: 02-baseline-recommendations-and-api-surfaces
    provides: "Shop-scoped DB dependency and product metadata persistence"
provides:
  - Baseline co-purchase + content-based recommendation service
  - PDP/cart recommendation endpoints with auth and shop-scoped DB
  - Integration tests for rule-filtered recommendations
affects: [02-baseline-recommendations-and-api-surfaces, recommendation-engine]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "baseline recommendations from SQL co-purchase plus content signals"
    - "rule-filtered merge of recommendation candidates"

key-files:
  created:
    - app/services/baseline_recommendation_service.py
    - app/routers/baseline_recommendations.py
    - app/routers/baseline_schemas.py
    - tests/test_baseline_recommendations.py
  modified:
    - app/repositories/order_repository.py
    - app/repositories/product_repository.py
    - app/services/token_service.py
    - main.py
    - tests/conftest.py

key-decisions:
  - "None - followed plan as specified"

patterns-established:
  - "baseline service builds co-purchase + content candidates then applies rule filtering"
  - "shop-scoped endpoints use get_shop_db with shared auth verification"

# Metrics
duration: 8min
completed: 2026-02-21
---

# Phase 2 Plan 2: Baseline Recommendations and API Surfaces Summary

**Baseline PDP/cart recommendation endpoints returning co-purchase and content candidates with rule-based filtering.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-02-21T12:06:31+01:00
- **Completed:** 2026-02-21T12:14:26+01:00
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- Implemented baseline recommendation service with co-purchase SQL and content-based ranking.
- Added authenticated PDP/cart endpoints backed by shop-scoped database sessions.
- Added integration tests for co-purchase derivation and rule filtering.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement baseline co-purchase + content-based recommendation service** - `c3512b0` (feat)
2. **Task 2: Add PDP/cart recommendation endpoints (shop-scoped + authed) with integration tests** - `46e1a35` (feat)

**Plan metadata:** (docs commit)

_Note: TDD tasks may have multiple commits (test → feat → refactor)_

## Files Created/Modified
- `app/services/baseline_recommendation_service.py` - Builds co-purchase and content-based candidates with rule filtering.
- `app/repositories/order_repository.py` - Adds co-purchase aggregation query.
- `app/repositories/product_repository.py` - Adds helper queries for SKU/category lookups.
- `app/routers/baseline_recommendations.py` - PDP/cart endpoints with auth and shop-scoped DB.
- `app/routers/baseline_schemas.py` - Request/response models for baseline recommendations.
- `main.py` - Registers baseline recommendation router.
- `tests/test_baseline_recommendations.py` - Integration tests for baseline endpoints and rules.
- `app/services/token_service.py` - Normalizes token expiry checks for auth verification.
- `tests/conftest.py` - Stabilizes authenticated client for repeated signup.

## Decisions Made
None - followed plan as specified.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Normalized timezone-aware token expiry checks**
- **Found during:** Task 2 (dockerized verification)
- **Issue:** Token verification compared naive and aware datetimes, raising TypeError.
- **Fix:** Normalized expires_at to timezone-aware before comparison.
- **Files modified:** app/services/token_service.py
- **Verification:** `docker compose -f docker-compose.test.yml up --build --abort-on-container-exit`
- **Committed in:** 46e1a35 (part of Task 2)

**2. [Rule 3 - Blocking] Stabilized authenticated_client for shop-scoped tests**
- **Found during:** Task 2 (dockerized verification)
- **Issue:** search_path bleed and repeated email caused signup to fail during tests.
- **Fix:** Reset search_path to public and use unique signup credentials per fixture.
- **Files modified:** tests/conftest.py
- **Verification:** `docker compose -f docker-compose.test.yml up --build --abort-on-container-exit`
- **Committed in:** 46e1a35 (part of Task 2)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Fixes required to complete verification. No scope creep.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Baseline recommendation endpoints and tests are in place.
- Ready for 02-03 engagement logging endpoints.

---
*Phase: 02-baseline-recommendations-and-api-surfaces*
*Completed: 2026-02-21*
