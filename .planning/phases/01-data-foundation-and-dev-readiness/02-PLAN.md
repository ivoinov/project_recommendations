---
phase: 01-data-foundation-and-dev-readiness
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/data/csv-spec.md
  - docs/architecture/decision.md
  - app/services/csv_validation_service.py
  - app/services/__init__.py
  - scripts/validate_csv.py
autonomous: true
must_haves:
  truths:
    - "Operator can validate multi-shop CSVs locally and see error thresholds and summary counts."
    - "Validation normalizes product and order fields before error reporting."
    - "Developer can reference an architecture decision document covering hosting options and vector/LLM tradeoffs."
  artifacts:
    - path: "docs/data/csv-spec.md"
      provides: "CSV schema, validation rules, error threshold, naming/merge behavior"
    - path: "app/services/csv_validation_service.py"
      provides: "Reusable CSV parsing, normalization, and validation rules"
    - path: "scripts/validate_csv.py"
      provides: "Local validation CLI entrypoint"
    - path: "docs/architecture/decision.md"
      provides: "Hosting and vector/LLM tradeoff guidance"
  key_links:
    - from: "scripts/validate_csv.py"
      to: "app/services/csv_validation_service.py"
      via: "validation call path"
      pattern: "csv_validation_service"
    - from: "app/services/csv_validation_service.py"
      to: "normalize_product_row|normalize_order_row"
      via: "normalization step before validation"
      pattern: "normalize_product_row|normalize_order_row"
    - from: "docs/architecture/decision.md"
      to: "App Runner|Cloud Run|pgvector|LLM"
      via: "explicit comparison sections"
      pattern: "App Runner|Cloud Run|pgvector|LLM"
---

<objective>
Deliver CSV spec documentation, a local validation CLI with normalization, and an architecture decision document for hosting and vector/LLM choices.

Purpose: Enable local data readiness checks and clear initial hosting guidance for Phase 1 requirements.
Output: CSV spec doc, architecture decision doc, and validation CLI with explicit normalization rules.
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
</context>

<tasks>

<task type="auto">
  <name>Task 1: Document CSV spec and architecture decisions (DATA-01, OPS-05)</name>
  <files>docs/data/csv-spec.md, docs/architecture/decision.md</files>
  <action>
    Create `docs/data/csv-spec.md` with sections for required/optional fields for products and orders, file naming (`{shop_id}_products.csv`, `{shop_id}_orders.csv`), UTF-8 semicolon delimiter, merge/append behavior for multiple files, and explicit validation/normalization rules with an error threshold value (set to 5%).
    Normalization rules must include: trimming whitespace on all string fields, normalizing `in_stock` to boolean, converting `price`/`qty` fields to decimals, and parsing `order_date` to ISO-8601 date strings. Keep category as-is per context.
    Create `docs/architecture/decision.md` covering App Runner/Cloud Run vs VM hosting, managed Postgres and Redis recommendations, pgvector default stance, LLM/embedding tradeoffs, cost estimates with assumptions, and migration triggers.
    Align decisions with `01-CONTEXT.md` and keep scope limited to v1 hosting guidance.
  </action>
  <verify>
    rg "CSV Schema|Validation Rules|Error Threshold|File Naming" docs/data/csv-spec.md
    rg "App Runner|Cloud Run|VM|pgvector|LLM|cost|migration" docs/architecture/decision.md
  </verify>
  <done>
    CSV spec includes required fields and error threshold; architecture decision doc includes hosting tradeoffs and vector/LLM guidance.
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement validation-only CLI and reusable rules (OPS-03)</name>
  <files>app/services/csv_validation_service.py, app/services/__init__.py, scripts/validate_csv.py</files>
  <action>
    Add a validation service that parses semicolon-delimited CSVs, normalizes rows, enforces required fields for products/orders, and returns per-file and per-shop error summaries without DB writes.
    Implement `normalize_product_row` and `normalize_order_row` helpers that apply the documented normalization rules and return cleaned row dicts for downstream ingestion.
    Ensure validation operates on normalized values and returns normalized rows to callers (not just errors).
    Implement a CLI at `scripts/validate_csv.py` that accepts `--input-dir` and optional `--error-threshold`, discovers per-shop files by naming convention, runs validation, and prints a concise summary with an exit code that reflects pass/fail of the threshold.
    Export the validation service via `app/services/__init__.py` for reuse in ingestion.
  </action>
  <verify>
    python scripts/validate_csv.py --input-dir var --error-threshold 0.05
    python - <<'PY'
    from app.services.csv_validation_service import normalize_product_row
    row = {"sku": "  ABC-1 ", "price": "12.50", "in_stock": "true"}
    print(normalize_product_row(row))
    PY
  </verify>
  <done>
    CLI produces a summary for all discovered shop files, exits non-zero when the error threshold is exceeded, and normalization helpers return cleaned values.
  </done>
</task>

</tasks>

<verification>
- Validation CLI runs locally and summarizes errors per shop without DB writes.
- Architecture decision document clearly states hosting and vector/LLM guidance with cost assumptions.
- Normalization rules are applied before validation results are reported.
</verification>

<success_criteria>
- OPS-03: Local validation/test flow is repeatable via CLI.
- OPS-05: Architecture decision document exists and covers required tradeoffs.
- DATA-01: Validation includes explicit normalization rules aligned with the CSV spec.
</success_criteria>

<output>
After completion, create `.planning/phases/01-data-foundation-and-dev-readiness/02-SUMMARY.md`.
</output>
