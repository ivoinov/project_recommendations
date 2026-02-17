---
phase: 01-data-foundation-and-dev-readiness
plan: 03
type: execute
wave: 2
depends_on: [02]
files_modified:
  - app/services/csv_ingestion_service.py
  - app/services/db_routing.py
  - scripts/ingest_csv.py
  - app/repositories/product_repository.py
  - app/repositories/order_repository.py
autonomous: true
must_haves:
  truths:
    - "Operator can ingest products and orders for multiple shops with data separated per shop in the DB."
    - "Ingestion uses normalized/validated rows and reports accepted/rejected counts per shop."
  artifacts:
    - path: "app/services/csv_ingestion_service.py"
      provides: "Validated ingestion with per-shop DB routing"
    - path: "app/services/db_routing.py"
      provides: "Shop-scoped DB session or schema routing"
    - path: "scripts/ingest_csv.py"
      provides: "Local ingestion CLI entrypoint"
    - path: "app/repositories/product_repository.py"
      provides: "Product persistence for shop-scoped schemas"
    - path: "app/repositories/order_repository.py"
      provides: "Order persistence for shop-scoped schemas"
  key_links:
    - from: "app/services/csv_ingestion_service.py"
      to: "app/services/db_routing.py"
      via: "shop-scoped DB session"
      pattern: "get_shop_session|shop_db"
    - from: "app/services/csv_ingestion_service.py"
      to: "app/services/csv_validation_service.py"
      via: "validation + normalization pipeline"
      pattern: "normalize_product_row|normalize_order_row|validate"
    - from: "scripts/ingest_csv.py"
      to: "app/services/csv_ingestion_service.py"
      via: "ingestion call path"
      pattern: "csv_ingestion_service"
---

<objective>
Deliver a multi-shop CSV ingestion path that routes writes to shop-scoped schemas and uses normalized, validated rows.

Purpose: Enable local multi-tenant data loading while keeping shop data isolated.
Output: Ingestion service, DB routing helper, and CLI for batch ingestion.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-data-foundation-and-dev-readiness/01-CONTEXT.md
@.planning/codebase/STRUCTURE.md
@.planning/codebase/CONVENTIONS.md
@.planning/phases/01-data-foundation-and-dev-readiness/02-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement shop-scoped DB routing helper (DATA-02)</name>
  <files>app/services/db_routing.py</files>
  <action>
    Implement a shop-scoped DB routing helper that uses a `shop_{shop_id}` schema naming convention for local runs.
    Ensure schemas are created if missing and provide a session/connection bound to the shop schema for repository usage.
  </action>
  <verify>
    python - <<'PY'
    from app.services.db_routing import get_shop_session
    print(get_shop_session("acme"))
    PY
  </verify>
  <done>
    Shop-scoped sessions can be created for any shop id and target a `shop_{shop_id}` schema.
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement ingestion service using normalized validation output (DATA-01, DATA-02)</name>
  <files>app/services/csv_ingestion_service.py, app/repositories/product_repository.py, app/repositories/order_repository.py</files>
  <action>
    Implement a CSV ingestion service that calls the validation service, uses normalized rows, skips invalid rows, and tracks rejected counts.
    Write valid products and orders into the shop-scoped schema using the repositories, ensuring no cross-shop mixing.
    Return per-shop summaries (accepted/rejected counts for products and orders) for CLI reporting.
  </action>
  <verify>
    python - <<'PY'
    from app.services.csv_ingestion_service import ingest_directory
    print(ingest_directory("var"))
    PY
  </verify>
  <done>
    Ingestion uses normalized rows, rejects invalid rows, and writes valid records into the correct shop schema.
  </done>
</task>

<task type="auto">
  <name>Task 3: Add ingestion CLI for multi-shop directories (OPS-03)</name>
  <files>scripts/ingest_csv.py</files>
  <action>
    Provide a CLI at `scripts/ingest_csv.py` that ingests all shop files in an input directory and prints a per-shop summary including accepted and rejected counts.
  </action>
  <verify>
    python scripts/ingest_csv.py --input-dir var
    psql "$DATABASE_URL" -c "\dn" | rg "shop_"
  </verify>
  <done>
    CLI outputs per-shop summaries and data is written into shop-specific schemas.
  </done>
</task>

</tasks>

<verification>
- Ingestion writes data into shop-specific DB schemas without cross-shop mixing.
- Ingestion summaries include accepted/rejected counts per shop.
</verification>

<success_criteria>
- DATA-01: Valid product/order rows ingest into the internal DB after validation and normalization.
- DATA-02: Multiple shops ingest into separate schemas or databases without mixing.
</success_criteria>

<output>
After completion, create `.planning/phases/01-data-foundation-and-dev-readiness/03-SUMMARY.md`.
</output>
