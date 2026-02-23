# Roadmap: FastAPI Recommendation System

## Overview

This roadmap sequences data foundation, baseline recommendations, and serving reliability before performance hardening and hybrid ranking improvements. Each phase delivers a user-observable capability for shoppers or operators while honoring the existing FastAPI, Celery, Postgres, and Redis stack constraints.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Data Foundation and Dev Readiness** - Ingest validated data locally and document architecture tradeoffs.
- [x] **Phase 2: Baseline Recommendations and API Surfaces** - Serve PDP/cart recommendations with rules and engagement logging.
- [ ] **Phase 3: Reliable Batch Publishing and Candidate Store** - Daily refreshes with versioned, cached precompute.
- [ ] **Phase 4: Deployment Pipeline** - CI/CD deploys API and worker to initial hosting.
- [ ] **Phase 5: Latency Hardening** - Meet the <200ms p95 target for recommendation endpoints.
- [ ] **Phase 6: Hybrid Ranking Blend** - Blend co-purchase and content signals in ranking.

## Phase Details

### Phase 1: Data Foundation and Dev Readiness
**Goal**: Operators can ingest and validate multi-shop data locally with a documented architecture direction.
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, OPS-03, OPS-05
**Success Criteria** (what must be TRUE):
  1. Operator can ingest catalog and order data with validation/normalization into the internal DB from sample data.
  2. Operator can import CSVs for multiple shops and see records separated by shop in the internal DB.
  3. Developer can run a repeatable local validation/test flow that confirms ingestion health.
  4. Developer can read an architecture decision document covering hosting options and vector/LLM tradeoffs.
**Plans**: 2/2 complete

Plans:
- [x] 01-02 - CSV spec, validation CLI, architecture decision
- [x] 01-03 - Multi-shop ingestion and shop-scoped routing

### Phase 2: Baseline Recommendations and API Surfaces
**Goal**: Shoppers receive baseline PDP/cart recommendations with business rules applied and engagement logged.
**Depends on**: Phase 1
**Requirements**: REC-01, REC-02, SRV-01, RULE-01, ANL-01
**Success Criteria** (what must be TRUE):
  1. Shopper can request PDP and cart recommendations and receive a list from the API.
  2. Recommendations include co-purchase and content-based candidates derived from catalog/order data.
  3. Results apply business rules (in-stock, exclusions) and remove duplicates within a list.
  4. Engagement events (CTR/add-to-cart) are logged by placement and retrievable for analysis.
**Plans**: 3/3 complete

Plans:
- [x] 02-01 - Shop-scoped DB dependency + product metadata (in_stock/tags)
- [x] 02-02 - Baseline PDP/cart recommendations (co-purchase + content) with rules
- [x] 02-03 - Engagement logging + summary retrieval endpoints

### Phase 3: Reliable Batch Publishing and Candidate Store
**Goal**: Recommendations refresh daily and serve from versioned, cached precomputed candidates.
**Depends on**: Phase 2
**Requirements**: DATA-03, SRV-02, OPS-01, OPS-02
**Success Criteria** (what must be TRUE):
  1. Daily batch refresh completes on schedule and reports a successful run status.
  2. API serves recommendations from a precomputed candidate store with caching enabled.
  3. Recommendation publishes are versioned with atomic promote and rollback available.
**Plans**: 3/3

Plans:
- [x] 03-01-PLAN.md — Candidate store models, repositories, and cache utilities
- [x] 03-02-PLAN.md — Versioned publish service with daily batch scheduling
- [x] 03-03-PLAN.md — Precomputed serving plus publish status/rollback APIs

### Phase 4: Deployment Pipeline
**Goal**: API and worker deploy through CI/CD to the initial hosting environment.
**Depends on**: Phase 3
**Requirements**: OPS-04
**Success Criteria** (what must be TRUE):
  1. CI/CD deploys the API and worker to the initial hosting environment without manual steps.
  2. Operator can verify the deployed API and worker are running via health/status checks.
**Plans**: TBD

Plans:
- [ ] TBD

### Phase 5: Latency Hardening
**Goal**: Recommendation endpoints meet the <200ms p95 target.
**Depends on**: Phase 3
**Requirements**: SRV-03
**Success Criteria** (what must be TRUE):
  1. PDP recommendation endpoint measured p95 latency is <200ms under expected load.
  2. Cart recommendation endpoint measured p95 latency is <200ms under expected load.
**Plans**: TBD

Plans:
- [ ] TBD

### Phase 6: Hybrid Ranking Blend
**Goal**: Recommendations are ranked using blended co-purchase and content-based signals.
**Depends on**: Phase 5
**Requirements**: REC-03
**Success Criteria** (what must be TRUE):
  1. PDP/cart ranking combines co-purchase and content-based signals into a single ordered list.
  2. Items with both signals rank higher than items with only one signal when scores are comparable.
**Plans**: TBD

Plans:
- [ ] TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 2 -> 2.1 -> 2.2 -> 3 -> 3.1 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Foundation and Dev Readiness | 2/2 | Complete | 2026-02-17 |
| 2. Baseline Recommendations and API Surfaces | 3/3 | Complete | 2026-02-21 |
| 3. Reliable Batch Publishing and Candidate Store | 3/3 | Complete | 2026-02-23 |
| 4. Deployment Pipeline | 0/TBD | Not started | - |
| 5. Latency Hardening | 0/TBD | Not started | - |
| 6. Hybrid Ranking Blend | 0/TBD | Not started | - |
