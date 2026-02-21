---
phase: 02-baseline-recommendations-and-api-surfaces
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - app/services/shop_db.py
  - app/models/product.py
  - app/repositories/product_repository.py
  - app/services/csv_ingestion_service.py
  - tests/models/test_product.py
autonomous: true
must_haves:
  truths:
    - "API code can open a shop-scoped DB session (search_path=shop_{shop_id}) while still using the normal FastAPI db dependency override in tests."
    - "Product records store `in_stock` and `tags` from CSV ingestion so Phase 2 rules/content-based candidates can use them."
  artifacts:
    - path: "app/services/shop_db.py"
      provides: "Shop-aware DB dependency that sets search_path and ensures schema/tables exist"
    - path: "app/models/product.py"
      provides: "Product model includes `in_stock` and `tags` fields"
    - path: "app/services/csv_ingestion_service.py"
      provides: "Ingestion maps normalized CSV fields into product persistence payloads"
  key_links:
    - from: "app/services/shop_db.py"
      to: "app/config.py"
      via: "Depends(db_settings.get_db)"
      pattern: "Depends\(db_settings\.get_db\)"
    - from: "app/services/shop_db.py"
      to: "app/models/base.py"
      via: "Base.metadata.create_all"
      pattern: "Base\.metadata\.create_all"
    - from: "app/services/csv_ingestion_service.py"
      to: "app/models/product.py"
      via: "payload includes in_stock/tags"
      pattern: "in_stock|tags"
---

<objective>
Add shop-scoped DB session support and persist product metadata needed for Phase 2 baseline recommendations.

Purpose: Phase 2 PDP/cart recs must be shop-specific and apply rules like in-stock filtering; this plan makes shop-scoped sessions and product fields available.
Output: Shop-aware DB dependency, Product model extensions, and ingestion/repository wiring for `in_stock` + `tags`.
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
@.planning/phases/01-data-foundation-and-dev-readiness/03-SUMMARY.md
@docs/data/csv-spec.md
@app/services/db_routing.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement shop-aware DB dependency using search_path</name>
  <files>app/services/shop_db.py</files>
  <action>
    Create `app/services/shop_db.py` that provides shop-scoped DB utilities designed for FastAPI dependencies:
    - Implement `normalize_shop_id(shop_id: str) -> str` using the same constraints as `app/services/db_routing.py` (lowercase, alnum + underscore).
    - Implement `shop_schema_name(shop_id: str) -> str` returning `shop_{shop_id}`.
    - Implement `ensure_shop_schema(db: Session, shop_id: str) -> str` that:
      - Creates schema if missing (CREATE SCHEMA IF NOT EXISTS).
      - Sets `search_path` to that schema for this session.
      - Runs `Base.metadata.create_all(bind=db.get_bind())` while the search_path is set so tables appear in the shop schema.
      - Performs lightweight schema evolution for existing shops by ensuring `products.in_stock` (boolean) and `products.tags` (text) exist via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...`.
    - Implement a FastAPI dependency `get_shop_db(shop_id: str, db: Session = Depends(db_settings.get_db)) -> Session` that calls `ensure_shop_schema` and returns the SAME `db` session.

    Constraints:
    - Do NOT create a new engine/session inside this dependency; it must respect `db_settings.get_db` overrides used by `tests/conftest.py`.
    - Keep SQL schema operations idempotent and safe for repeated calls.
  </action>
  <verify>
    python3 - <<'PY'
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.base import Base
    from app.services.shop_db import ensure_shop_schema

    engine = create_engine("postgresql://test:test@localhost:5433/test_recommendations")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        ensure_shop_schema(db, "acme")
        # Should not raise, and should be able to create tables in shop schema
        Base.metadata.create_all(bind=db.get_bind())
        print("ok")
    finally:
        db.close()
    PY
  </verify>
  <done>
    `ensure_shop_schema` is idempotent, sets the session search_path to `shop_{shop_id}`, creates missing tables, and can be used as a FastAPI dependency without breaking test DB overrides.
  </done>
</task>

<task type="auto">
  <name>Task 2: Persist `in_stock` and `tags` on products during ingestion</name>
  <files>app/models/product.py, app/repositories/product_repository.py, app/services/csv_ingestion_service.py, tests/models/test_product.py</files>
  <action>
    Extend the product persistence layer to store inventory/tags fields described in `docs/data/csv-spec.md`:
    - Update `app/models/product.py`:
      - Add `in_stock = Column(Boolean, nullable=True)` and `tags = Column(Text, nullable=True)`.
      - Include `in_stock` and `tags` in `as_dict` output.
    - Update `app/repositories/product_repository.py`:
      - Wire `in_stock` and `tags` through create/update and bulk update mappings.
    - Update `app/services/csv_ingestion_service.py` `_build_product_payload` to map:
      - `in_stock` from normalized product row.
      - `tags` from normalized row `tags` (optional); keep as raw string (no parsing) for v1.
    - Update `tests/models/test_product.py` expectations to assert the new columns exist and `as_dict` includes them.

    Notes:
    - Do not change CSV validation requirements; it already normalizes `in_stock` and trims strings.
    - Keep changes backward-compatible: if `tags` or `in_stock` are missing from older DB rows, code should behave safely (treat `in_stock is None` as "unknown" for now).
  </action>
  <verify>
    docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
  </verify>
  <done>
    Product ORM and repository accept and persist `in_stock` + `tags`, model tests pass, and the shop-schema dependency can add missing columns for existing shop tables.
  </done>
</task>

</tasks>

<verification>
- Model tests pass and include the new product columns.
- `ensure_shop_schema` can run against an existing database and leaves it in a usable state for subsequent shop-scoped queries.
</verification>

<success_criteria>
- Phase 2 can safely use `shop_{shop_id}` schemas from HTTP handlers without bypassing the test DB override.
- Product data includes the metadata needed for in-stock filtering and basic tag/category similarity.
</success_criteria>

<output>
After completion, create `.planning/phases/02-baseline-recommendations-and-api-surfaces/01-SUMMARY.md`.
</output>
