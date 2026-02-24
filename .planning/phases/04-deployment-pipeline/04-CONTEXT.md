# Phase 4: Deployment Pipeline - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

CI/CD deploys the API and worker to the initial hosting environment and provides a way to verify they are running.

</domain>

<decisions>
## Implementation Decisions

### Deployment trigger
- Deploy on merge to main.
- Deploy on every merge (no batching).
- Fully automated (no manual approval gate).
- Use latest main build (no versioned release identifiers).
- Deploys can happen anytime.
- Always deploy on every merge, even for non-runtime changes.
- Queue deploys serially; do not skip older merges.
- Block deploys if required checks are pending or skipped.

### Environment scope
- Single production environment initially.
- If staging is introduced later, production deploys must follow successful staging deploys.
- Deploy API and worker together.
- Redeploy both components even if only one changed.

### Verification checks
- Health/status endpoints only are sufficient.
- Verification is automated in CI/CD.
- Verify both API and worker on every deploy.
- Record verification results (report/status).

### Failure handling
- Auto rollback on failed verification.
- One automatic retry on failure.
- Failures surfaced via CI/CD status only.
- Pause deployments after repeated failures.

### OpenCode's Discretion
- None — decisions specified.

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

*Phase: 04-deployment-pipeline*
*Context gathered: 2026-02-24*
