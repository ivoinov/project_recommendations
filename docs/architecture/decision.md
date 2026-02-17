# Architecture Decision: Phase 1 Hosting and Vector/LLM Choices

## Decision Summary
For v1 hosting, use a managed container platform (AWS App Runner or GCP Cloud Run) for both API and Celery worker. Use managed Postgres and Redis. Default to pgvector for vector search needs, and keep LLM usage optional for enrichment and summaries.

## Hosting Options

### App Runner / Cloud Run (Recommended for v1)
**Pros**
- Managed container runtime with autoscaling and low ops overhead
- Simple CI/CD via GitHub Actions and container registry
- Pay-per-use with small baseline costs

**Cons**
- Cold start risk for low-traffic services
- Less control over low-level networking

### VM Hosting (EC2 / Compute Engine)
**Pros**
- Full control over runtime and networking
- Easier to run long-lived workers with stable latency

**Cons**
- Higher operational overhead (patching, scaling, monitoring)
- Cost floors even at low usage

**Decision:** Start with App Runner or Cloud Run for v1. Revisit VM hosting when scale or latency needs make cold starts unacceptable.

## Managed Postgres and Redis

**Postgres:** Use managed Postgres (RDS or Cloud SQL) for v1. This aligns with existing SQLAlchemy usage and keeps backup/patching overhead low.

**Redis:** Use managed Redis (Elasticache or Memorystore) for Celery broker/cache to avoid running Redis on the same container runtime.

## Vector and LLM Stance

### pgvector (Default)
Use pgvector in Postgres as the default vector store. It minimizes new infrastructure and keeps vector queries close to existing product data.

**When to move beyond pgvector:**
- Vector queries exceed 100ms p95
- Vector table grows beyond millions of embeddings
- Need advanced ANN features or hybrid search not supported in Postgres

### LLM and Embeddings Tradeoffs
LLM usage is optional for v1. If used, prefer embeddings for content-based similarity and consider LLM summaries for product descriptions only if they improve recommendation relevance.

**Tradeoffs:**
- **LLM pros:** richer semantic signals, improved cold-start coverage
- **LLM cons:** cost per request, latency, ongoing API dependency

**Default stance:** Use embeddings for similarity and defer LLM summarization unless product text quality is too low for reliable embeddings.

## Cost Estimates (Monthly, v1)
Assumptions:
- 1-2 vCPU containers for API and worker
- Low traffic (tens of requests/minute)
- 10-50 GB Postgres storage
- Small Redis instance

Estimated ranges:
- App Runner / Cloud Run: $40-$120
- Managed Postgres (RDS/Cloud SQL): $80-$200
- Managed Redis (Elasticache/Memorystore): $30-$100
- Total baseline: $150-$420 per month

## Migration Triggers
Re-evaluate hosting and vector/LLM choices when any of the following occur:
- Cold starts materially impact latency or reliability
- Celery queue backlog exceeds SLA for multiple days
- Monthly infrastructure cost exceeds budget targets
- Vector query latency or storage growth becomes a bottleneck
- LLM costs exceed expected ROI for recommendation lift

## Scope Notes
This decision covers v1 hosting guidance only (dev + prod). It does not prescribe long-term multi-region or multi-environment deployments.
