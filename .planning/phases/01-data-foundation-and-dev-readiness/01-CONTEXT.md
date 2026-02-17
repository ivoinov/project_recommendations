# Phase 1: Data Foundation and Dev Readiness - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Ingest and validate multi-shop data locally and produce an architecture decision document covering hosting options and vector/LLM tradeoffs.

</domain>

<decisions>
## Implementation Decisions

### Architecture decision scope
- Initial hosting target: Cloud app runner (AWS App Runner / GCP Cloud Run)
- Compare App Runner/Cloud Run vs VM-based hosting in the decision doc
- Run API and Celery worker on the same platform
- Use managed Postgres (RDS/Cloud SQL) for v1 hosting guidance
- Use managed Redis (Elasticache/Memorystore) for Celery broker/cache
- Multi-shop tenancy: separate DB/schema per shop (not shared `shop_id` tenancy)
- Baseline sizing guidance: small, cost-optimized
- CI/CD target: GitHub Actions
- LLM stance: include LLM-based summarization ideas in the decision doc
- Vector DB stance: recommend pgvector in Postgres as default
- Include rough monthly cost estimates in the decision doc
- Hosted CSV ingestion: upload to API endpoint and store in DB
- Environments: dev + prod only
- Include migration path and scale triggers in the decision doc

### CSV ingestion shape & shop separation
- Unified CSV schema across all shops
- Separate files per shop
- Products and Orders are both required for v1 ingestion
- File naming: `{shop_id}_products.csv` and `{shop_id}_orders.csv`
- Encoding: UTF-8, semicolon-delimited, header row required
- Price fields are numeric decimals with dot separator
- Shop IDs are slugs (e.g., `acme_products.csv`)
- Allow multiple CSVs per shop per day; append/merge behavior

### Validation/normalization rules
- Products require: SKU, name, category, price, in_stock, short_description, meta info
- Orders require: order_id, shop_id, customer_id, order_date, items (sku, qty, price)
- Missing required fields: reject row with error (skip row, not full import fail)
- Category normalization: use as-is (no mapping)

### Local validation flow
- Provide a CLI command to run validation locally
- Output: summary report only (counts and errors summary)
- Validation is dry-run only (no DB writes)
- Health criteria: allow errors up to a threshold (threshold value set during planning)

### OpenCode's Discretion
- Exact CLI command name and location
- Exact error threshold value for validation health
- Additional optional CSV fields and normalization details

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-data-foundation-and-dev-readiness*
*Context gathered: 2026-02-17*
