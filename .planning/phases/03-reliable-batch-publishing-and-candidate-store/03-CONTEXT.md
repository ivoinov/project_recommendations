# Phase 3: Reliable Batch Publishing and Candidate Store - Context

**Gathered:** 2026-02-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver daily recommendation refreshes that publish versioned, cached, precomputed candidate lists for PDP and cart. This phase focuses on reliable batch publishing, candidate store behavior, and cache freshness; new recommendation types or ranking approaches are out of scope.

</domain>

<decisions>
## Implementation Decisions

### Batch cadence & coverage
- Single fixed UTC schedule around 02:00 UTC.
- Run only for shops with new data; report per-shop and overall status.
- Late runs warn and keep serving the previous version.
- Missed days auto-run ASAP, then resume schedule.
- Backfill is latest-day only (no multi-day backfill).
- Partial failures publish successful shops; failed shops stay on prior version.
- Data cutoff is "up to run start time."
- No same-day reruns for failed shops; retry next day only.
- Status reports success/failure only (no timing metrics).
- No automatic retries within a run.

### Publish versioning & rollback behavior
- Versions are per-shop and labeled with incrementing numbers.
- Successful runs auto-promote to current.
- Rollback targets the immediately previous version only.
- Retain last 2 versions per shop.
- Rollback is automatic on failure.
- Status exposes current and previous versions.
- Promotion/rollback is atomic at the shop level.

### Candidate list shape & limits
- Precomputed lists are stored raw; business rules applied at serve time.
- Ordering is score-descending with popularity tie-breaks.
- PDP cap: 20 items; Cart cap: 50 items (different caps).
- If fewer candidates exist, serve fewer (no backfill).
- PDP never includes the current item in its own recommendations.

### Cache freshness behavior
- Cache entries live until the next publish.
- Serve stale data if cache is stale/missing.
- Invalidate cache immediately on publish.
- Warm cache after publish.

### OpenCode's Discretion
None specified.

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

*Phase: 03-reliable-batch-publishing-and-candidate-store*
*Context gathered: 2026-02-23*
