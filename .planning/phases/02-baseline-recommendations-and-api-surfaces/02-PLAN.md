---
phase: 02-baseline-recommendations-and-api-surfaces
plan: 02
type: execute
wave: 2
depends_on:
  - 01
files_modified:
  - app/services/baseline_recommendation_service.py
  - app/routers/baseline_recommendations.py
  - app/routers/baseline_schemas.py
  - app/repositories/order_repository.py
  - app/repositories/product_repository.py
  - main.py
  - tests/test_baseline_recommendations.py
autonomous: true
must_haves:
  truths:
    - "Shopper can request PDP and cart recommendations and receive a list from the API."
    - "Responses include both co-purchase and content-based candidates derived from the shop's catalog/order data."
    - "Business rules apply: exclude seed/excluded SKUs, filter out-of-stock items, and de-duplicate within a placement list."
  artifacts:
    - path: "app/routers/baseline_recommendations.py"
      provides: "PDP + cart recommendation endpoints with auth + shop-scoped DB"
    - path: "app/services/baseline_recommendation_service.py"
      provides: "Baseline co-purchase + content-based candidate generation and merging"
    - path: "tests/test_baseline_recommendations.py"
      provides: "Integration tests proving endpoints return derived candidates with rules applied"
  key_links:
    - from: "main.py"
      to: "app/routers/baseline_recommendations.py"
      via: "app.include_router"
      pattern: "include_router\(baseline_recommendations\.router\)"
    - from: "app/routers/baseline_recommendations.py"
      to: "app/services/shop_db.py"
      via: "Depends(get_shop_db)"
      pattern: "get_shop_db"
    - from: "app/services/baseline_recommendation_service.py"
      to: "app/repositories/order_repository.py"
      via: "co-purchase query"
      pattern: "co_purchase|copurchase|increment_id"
---

<objective>
Deliver baseline PDP/cart recommendation endpoints that return co-purchase and content-based candidates with business rules applied.

Purpose: Satisfy Phase 2 serving requirements (REC-01, REC-02, SRV-01, RULE-01) using only existing Postgres data (products + orders) per shop.
Output: New baseline recommendation router + service and integration tests.
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
@app/routers/recommendations.py
@app/services/shop_db.py
@app/repositories/order_repository.py
@app/repositories/product_repository.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement baseline co-purchase + content-based recommendation service</name>
  <files>app/services/baseline_recommendation_service.py, app/repositories/order_repository.py, app/repositories/product_repository.py</files>
  <action>
    Create `app/services/baseline_recommendation_service.py` that generates candidates from the DB (no pickled ML artifacts):
    - Co-purchase (REC-01): given seed SKUs, find orders containing any seed SKU and rank other SKUs by co-occurrence count.
      - Implement this as a repository method in `app/repositories/order_repository.py` (prefer a single SQL query using increment_id grouping).
    - Content-based (REC-02): given a seed product (and optionally the rest of cart), rank other products using:
      - Same `parent_category` as a strong prior.
      - Tag overlap using `tags` and/or `categories_names` tokenization (simple split on comma/pipe/space; keep deterministic).
      - Price proximity using absolute difference on `current_price`.
      - Return a ranked list of SKUs.
      - Use `ProductRepository` helpers; add small repository methods if needed (e.g., get by sku, get candidates in same category).
    - Business rules (RULE-01): implement a single merge/filter step that:
      - Removes any seed SKUs and any `exclude_skus`.
      - De-duplicates while preserving a stable ordering.
      - Filters out products where `in_stock is False` (treat `None` as in-stock for now).
      - Enforces `limit`.

    Keep the service pure and testable (functions or a small class) and avoid calling FastAPI objects from the service.
  </action>
  <verify>
    python3 - <<'PY'
    # Smoke import test
    from app.services.baseline_recommendation_service import build_recommendations
    print(callable(build_recommendations))
    PY
  </verify>
  <done>
    A baseline recommendation builder exists that can produce co-purchase and content-based candidate SKUs and returns a final filtered list with rules applied.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add PDP/cart recommendation endpoints (shop-scoped + authed) with integration tests</name>
  <files>app/routers/baseline_recommendations.py, app/routers/baseline_schemas.py, main.py, tests/test_baseline_recommendations.py</files>
  <action>
    Add a new router providing explicit PDP and cart placements (SRV-01):
    - Create `app/routers/baseline_schemas.py` with Pydantic models for:
      - Cart request: `cart_skus: list[str]`, optional `exclude_skus: list[str] = []`, optional `limit: int = 20`.
      - Response: include `placement` ("pdp"|"cart"), `seed_skus`, `co_purchase`, `content_based`, and `recommendations` (final merged list).
    - Create `app/routers/baseline_recommendations.py` with an `APIRouter` that:
      - Reuses the OAuth2 bearer verification pattern from `app/routers/recommendations.py` (keep behavior consistent; 401 on invalid token).
      - Uses `app.services.shop_db.get_shop_db` so queries run against `shop_{shop_id}`.
      - Exposes:
        - `GET /v1/shops/{shop_id}/recommendations/pdp/{product_sku}`
        - `POST /v1/shops/{shop_id}/recommendations/cart`
      - Calls the baseline recommendation service and returns the response schema.
    - Update `main.py` to include the new router (`app.include_router(...)`).
    - Create `tests/test_baseline_recommendations.py`:
      - Use `authenticated_client`.
      - Seed shop schema data by setting search_path to `shop_test` (or `shop_acme`) on the test session and inserting Products + Orders.
      - Assert PDP endpoint returns co-purchase candidates derived from orders.
      - Assert cart endpoint returns a merged list with de-duplication and exclusions enforced.

    Constraints:
    - Do NOT change existing `/similar-recommendations/*` endpoints; existing tests must keep passing.
  </action>
  <verify>
    docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
  </verify>
  <done>
    PDP/cart endpoints are reachable, return co-purchase + content-based lists derived from DB data, apply rule filters, and are covered by new integration tests.
  </done>
</task>

</tasks>

<verification>
- Phase 2 endpoints exist for PDP and cart placements and require auth.
- Responses include both co-purchase and content-based candidates and a final merged list.
- Business rules (exclude seed/excluded, in-stock filter, dedupe) are enforced by tests.
</verification>

<success_criteria>
- REC-01 satisfied: co-purchase candidates derived from order history.
- REC-02 satisfied: content-based candidates derived from catalog attributes (category/price/tags).
- SRV-01 satisfied: API serves PDP/cart recommendations.
- RULE-01 satisfied: rule filtering/dedup is applied.
</success_criteria>

<output>
After completion, create `.planning/phases/02-baseline-recommendations-and-api-surfaces/02-SUMMARY.md`.
</output>
