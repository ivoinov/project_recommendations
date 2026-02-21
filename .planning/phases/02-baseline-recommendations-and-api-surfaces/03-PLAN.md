---
phase: 02-baseline-recommendations-and-api-surfaces
plan: 03
type: execute
wave: 3
depends_on:
  - 01
files_modified:
  - app/models/recommendation_event.py
  - app/models/__init__.py
  - app/repositories/recommendation_event_repository.py
  - app/routers/engagement.py
  - app/routers/engagement_schemas.py
  - app/repositories/__init__.py
  - main.py
  - tests/test_engagement_events.py
autonomous: true
must_haves:
  truths:
    - "Engagement events (click/add-to-cart) can be logged by placement for a shop via an API endpoint."
    - "Engagement events are retrievable for analysis (at least aggregated counts by placement and event type)."
  artifacts:
    - path: "app/models/recommendation_event.py"
      provides: "Engagement event persistence table for recommendation interactions"
    - path: "app/routers/engagement.py"
      provides: "API endpoints to log and query engagement events"
    - path: "tests/test_engagement_events.py"
      provides: "Integration tests proving events can be logged and queried"
  key_links:
    - from: "app/routers/engagement.py"
      to: "app/services/shop_db.py"
      via: "Depends(get_shop_db)"
      pattern: "get_shop_db"
    - from: "app/routers/engagement.py"
      to: "app/repositories/recommendation_event_repository.py"
      via: "create + aggregate query"
      pattern: "RecommendationEventRepository"
    - from: "main.py"
      to: "app/routers/engagement.py"
      via: "app.include_router"
      pattern: "include_router\(engagement\.router\)"
---

<objective>
Add engagement logging and retrieval for PDP/cart recommendation placements.

Purpose: Phase 2 requires that CTR/add-to-cart engagement is logged by placement and retrievable for analysis (ANL-01).
Output: New engagement event model + repository + router with tests.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/codebase/ARCHITECTURE.md
@.planning/codebase/CONVENTIONS.md
@.planning/codebase/TESTING.md
@.planning/phases/02-baseline-recommendations-and-api-surfaces/01-SUMMARY.md
@app/services/shop_db.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add recommendation engagement event model and repository</name>
  <files>app/models/recommendation_event.py, app/models/__init__.py, app/repositories/recommendation_event_repository.py, app/repositories/__init__.py</files>
  <action>
    Create a new DB model for engagement tracking:
    - Add `app/models/recommendation_event.py` with a SQLAlchemy model (table name `recommendation_events`) that includes:
      - `id` primary key
      - `created_at` timestamp (timezone-aware) defaulting to now
      - `placement` string (e.g., "pdp" or "cart")
      - `event_type` string enum-like ("click", "add_to_cart", optionally "impression")
      - `context_skus` text (store comma-separated list for v1)
      - `recommended_sku` string
      - optional `session_id` string
      - optional `customer_id` integer
      - optional `request_id` string
    - Export the model via `app/models/__init__.py`.
    - Add `app/repositories/recommendation_event_repository.py`:
      - `create(event: RecommendationEvent) -> RecommendationEvent`
      - `count_by_placement_and_type(from_ts, to_ts, placement=None) -> list[dict]` (or similar) returning aggregated counts.
      - Follow repository error handling conventions (rollback + logger.exception + re-raise).
    - Export repository via `app/repositories/__init__.py`.

    Notes:
    - Rely on the shop schema search_path; tables should be created by `ensure_shop_schema` when the engagement endpoints are called.
  </action>
  <verify>
    python3 - <<'PY'
    from app.models import RecommendationEvent
    print(RecommendationEvent.__tablename__)
    PY
  </verify>
  <done>
    Engagement events can be persisted and aggregated through a repository API, and the model is discoverable via `app.models`.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add engagement API endpoints (log + summary) and tests</name>
  <files>app/routers/engagement.py, app/routers/engagement_schemas.py, main.py, tests/test_engagement_events.py</files>
  <action>
    Add an authenticated API surface for engagement logging and retrieval:
    - Create `app/routers/engagement_schemas.py` with Pydantic models:
      - POST body: `placement`, `event_type`, `recommended_sku`, `context_skus: list[str] = []`, and optional ids (`session_id`, `customer_id`, `request_id`).
      - Response: `id`, `created_at`, and echoed fields.
      - Summary response: aggregated counts per `placement` + `event_type` for a date/time window.
    - Create `app/routers/engagement.py`:
      - Reuse the same OAuth2 token verification pattern as other protected routers.
      - Use `get_shop_db` so writes/read happen in the shop schema.
      - Implement:
        - `POST /v1/shops/{shop_id}/engagement/recommendations` (log an event)
        - `GET /v1/shops/{shop_id}/engagement/recommendations/summary?from=...&to=...&placement=...` (aggregate)
    - Update `main.py` to include the new router.
    - Add `tests/test_engagement_events.py` that:
      - Seeds shop schema via search_path as needed.
      - Posts a click and add_to_cart event.
      - Fetches summary and asserts counts are correct.

    Constraints:
    - Keep endpoints small and composable; DB logic goes in the repository.
  </action>
  <verify>
    docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
  </verify>
  <done>
    Engagement endpoints log events for a shop and can return an aggregated summary by placement and event_type; tests prove the round trip.
  </done>
</task>

</tasks>

<verification>
- Engagement events are persisted per shop schema and are queryable.
- API supports at least click + add_to_cart and summarizes counts by placement.
</verification>

<success_criteria>
- ANL-01 satisfied: CTR/add-to-cart engagement events are logged by placement and retrievable for analysis.
</success_criteria>

<output>
After completion, create `.planning/phases/02-baseline-recommendations-and-api-surfaces/03-SUMMARY.md`.
</output>
