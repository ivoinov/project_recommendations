# FastAPI Recommendation System

## What This Is

This is a FastAPI-based recommendation service for ecommerce shoppers that delivers upsell ("people also bought with") and content-based product recommendations on PDP and cart pages. It integrates with PostgreSQL and Magento-sourced data, with Celery background jobs handling data syncs and model training.

## Core Value

Shoppers see relevant recommendations fast enough to drive higher engagement on PDP/cart.

## Requirements

### Validated

- ✓ Authenticate users and protect recommendation endpoints — existing
- ✓ Serve recommendation responses from the API — existing
- ✓ Run background jobs for data ingestion and model training — existing

### Active

- [ ] Improve upsell recommendations for PDP and cart placements
- [ ] Improve content-based recommendations using category, price, and tags
- [ ] Reduce cold-start gaps so more products have recommendations
- [ ] Stabilize background jobs to eliminate failures and slow runs
- [ ] Maintain <200ms p95 response time for recommendation endpoints
- [ ] Recompute recommendations on a daily batch cadence

### Out of Scope

- New infrastructure services (e.g., Kafka) — constraint to keep current stack

## Context

- Existing FastAPI + SQLAlchemy + Celery + Postgres + Redis stack with repository/service layers
- Recommendations delivered via API endpoints with OAuth2 token auth
- Background tasks ingest Magento data and train ML models
- Known pain points: cold-start gaps and slow/unstable Celery jobs
- Success is defined as higher recommendation engagement (click-through/add-to-cart)

## Constraints

- **Tech stack**: Keep current stack (FastAPI, SQLAlchemy, Celery, Postgres, Redis) — reduce migration risk
- **Deployment**: Must remain Dockerized — keep existing build/deploy flow

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Recommendations appear on PDP and cart | Highest shopper impact locations | — Pending |
| Daily batch refresh cadence | Balances freshness with compute cost | — Pending |
| <200ms p95 response time target | Preserve shopper UX on PDP/cart | — Pending |
| Fallback behavior returns empty list | Simpler behavior; caller handles no-recs | — Pending |
| Content-based attributes: category, price, tags | Uses available product metadata | — Pending |
| Success metric: engagement uplift (CTR/add-to-cart) | Directly tied to shopper behavior | — Pending |

---
*Last updated: 2026-02-17 after initialization*
