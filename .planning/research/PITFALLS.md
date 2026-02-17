# Pitfalls Research

**Domain:** ecommerce recommendation service (upsell + content-based)
**Researched:** 2026-02-17
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Training on noisy or inconsistent catalog data

**What goes wrong:**
Recommendations surface out-of-stock, deactivated, or miscategorized items, tanking CTR and trust.

**Why it happens:**
Magento catalog hygiene issues (stale status, missing category mapping, variant duplication) flow into PostgreSQL without validation.

**How to avoid:**
Add a catalog validation pipeline: enforce active/in-stock filters, deduplicate variants, normalize categories/brands, and drop items missing required fields before feature generation.

**Warning signs:**
High bounce on rec clicks, customer support reports for unavailable items, batch output count spikes/drops after catalog sync.

**Phase to address:**
Phase 1 (Data ingestion + quality gates)

---

### Pitfall 2: Cold-start left as a fallback afterthought

**What goes wrong:**
New products/users get empty or irrelevant recs; engagement stalls for new inventory.

**Why it happens:**
Teams focus on historical co-purchase and ignore content-based or popularity-by-category baselines.

**How to avoid:**
Implement explicit cold-start strategy: content-based similarity (text + attributes), category-level popularity, and rules for first exposure thresholds.

**Warning signs:**
Low rec fill rate for new SKUs, long tail items never appearing, high proportion of “no recs” responses.

**Phase to address:**
Phase 2 (Content-based + cold-start)

---

### Pitfall 3: Batch jobs overwrite live quality with stale or partial data

**What goes wrong:**
Daily batch refresh replaces good recs with incomplete outputs, degrading relevance for hours.

**Why it happens:**
Celery job failures, partial writes, or timeouts are not guarded by atomic swap logic.

**How to avoid:**
Write batch outputs to versioned tables/keys and atomically promote when full job success is verified. Keep last-known-good outputs.

**Warning signs:**
Sharp CTR drop after batch window, partial table row counts, increased cache misses after refresh.

**Phase to address:**
Phase 3 (Batch reliability + publish/rollback)

---

### Pitfall 4: Serving layer ignores latency budgets

**What goes wrong:**
<200ms p95 target fails under load, leading to timeouts and PDP/cart latency regressions.

**Why it happens:**
Online path performs Postgres joins or recomputes features per request instead of precomputing and caching.

**How to avoid:**
Precompute rec lists daily; serve from Redis or denormalized tables. Add request-level timeouts and fallback to cached popular/category lists.

**Warning signs:**
p95 response spikes during traffic peaks, increased DB CPU/IO, timeouts in PDP/cart logs.

**Phase to address:**
Phase 3 (Serving optimization + caching)

---

### Pitfall 5: Evaluation uses offline metrics only

**What goes wrong:**
Models look better offline but reduce revenue or cart size in production.

**Why it happens:**
No online A/B testing, no guardrails for negative business metrics.

**How to avoid:**
Add online evaluation: A/B or interleaving, track conversion rate, AOV, attach rate, and “hide recs” feedback. Define rollout gates.

**Warning signs:**
Offline improvements but flat/negative revenue metrics, stakeholder skepticism about recommendation value.

**Phase to address:**
Phase 4 (Experimentation + measurement)

---

### Pitfall 6: Co-purchase graph is biased by promotions and bundles

**What goes wrong:**
Upsell recs push promo bundles or out-of-context items, reducing trust.

**Why it happens:**
Events are dominated by short-lived campaigns or bulk orders, skewing co-purchase signals.

**How to avoid:**
Down-weight promo periods, exclude bulk order patterns, and apply time decay or campaign-aware filtering.

**Warning signs:**
Recs over-index on a promo SKU, high bounce on recs during/after campaigns.

**Phase to address:**
Phase 2 (Signal engineering)

---

### Pitfall 7: Missing personalization boundaries

**What goes wrong:**
Recs appear creepy or off-brand (e.g., sensitive items displayed on PDP).

**Why it happens:**
No category exclusions, no per-page rules, or insufficient privacy controls.

**How to avoid:**
Define category allow/deny lists per placement and include “safe mode” policies for PDP/cart.

**Warning signs:**
Merchandising team complaints, customer feedback about inappropriate recs.

**Phase to address:**
Phase 3 (Serving rules + merchandising controls)

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoding category rules in code | Faster launch | Requires deploys for changes | MVP only if rules are stable |
| Single-table rec storage without versioning | Easy queries | No rollback or audit | Never |
| Skipping data validation on Magento ingest | Faster sync | Bad recs, unstable jobs | Never |
| Ignoring feature drift checks | Less complexity | Gradual quality decay | MVP only with manual reviews |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Magento catalog sync | Assuming “status=enabled” means sellable | Combine status + stock + visibility + channel filters |
| Magento order data | Treating refunds/returns as purchases | Exclude refunded/returned lines from co-purchase |
| Redis broker (Celery) | No retry/backoff strategy | Use exponential backoff, dead-letter/failed task queues |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Per-request Postgres joins for recs | p95 latency spikes | Precompute + cache + denormalize | At high PDP/cart concurrency |
| Full-dataset daily rebuild without partitioning | Batch windows grow | Incremental updates + partitioning | When catalog > 100k SKUs |
| Redis cache without TTL + invalidation | Stale recs persist | TTL + versioned cache keys | After price/stock changes |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing internal SKU IDs in client logs | Data leakage to third parties | Use public product IDs, scrub logs |
| Logging full user query/behavior with PII | Compliance exposure | Pseudonymize IDs, minimize fields |
| Unauthenticated rec endpoints | Scraping competitive data | Require auth or signed requests |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Recs include out-of-stock items | Frustration, trust loss | Filter by stock + channel visibility |
| Recs ignore price sensitivity | Lower conversion | Same-price-band or configurable price delta |
| “People also bought” on single-item carts | Feels random | Use cart-aware context or fallback to category popularity |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Cold-start:** Often missing explicit fallback logic — verify fill rate for new SKUs/users.
- [ ] **Batch refresh:** Often missing atomic publish/rollback — verify last-known-good switch.
- [ ] **Latency target:** Often missing load test data — verify p95 under peak traffic.
- [ ] **Merchandising rules:** Often missing allow/deny category controls — verify per-placement filters.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Stale/partial batch publish | MEDIUM | Roll back to previous versioned output, re-run failed tasks |
| Low relevance from promo bias | LOW | Temporarily down-weight recent orders, apply time decay |
| Latency regression | HIGH | Switch to cached fallbacks, disable heavy features, optimize DB |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Noisy catalog data | Phase 1 | Data quality checks + rec output validation |
| Cold-start gaps | Phase 2 | Fill rate for new SKUs/users >= target |
| Partial batch publish | Phase 3 | Atomic promote + last-known-good rollback |
| Latency regressions | Phase 3 | p95 < 200ms under load test |
| Offline-only evaluation | Phase 4 | Online experiment reports with business metrics |
| Promo bias in co-purchase | Phase 2 | Time-decay/filters + CTR stability across campaigns |
| Missing merchandising boundaries | Phase 3 | Category allow/deny rules in place |

## Sources

- Personal experience / known issues in ecommerce recommendation systems (LOW confidence, validate during discovery)

---
*Pitfalls research for: ecommerce recommendation service*
*Researched: 2026-02-17*
