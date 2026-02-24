---
phase: 04-deployment-pipeline
plan: 02
subsystem: infra
tags: [aws, apprunner, ecr, github-actions, oidc, docker]

# Dependency graph
requires:
  - phase: 04-deployment-pipeline/04-01
    provides: Worker health endpoint and container entrypoint
provides:
  - CI/CD deploy job to App Runner with verification and rollback
  - Deploy scripts for ECR build/push and App Runner updates
affects:
  - phase-05-latency-hardening
  - operations

# Tech tracking
tech-stack:
  added: []
  patterns:
    - App Runner deployments via AWS CLI with GitHub OIDC
    - Health-check verification with rollback retry

key-files:
  created:
    - scripts/deploy/apprunner_deploy.sh
    - scripts/deploy/apprunner_verify.sh
    - scripts/deploy/apprunner_rollback.sh
    - .planning/phases/04-deployment-pipeline/04-USER-SETUP.md
  modified:
    - .github/workflows/main.yml

key-decisions:
  - None - followed plan as specified

patterns-established:
  - Serialized main-branch deploys using GitHub Actions concurrency
  - Rollback state stored for App Runner image updates

# Metrics
duration: 2 min
completed: 2026-02-24
---

# Phase 4 Plan 02: Deployment Pipeline Summary

**Automated App Runner deploys with ECR image updates, health verification, and rollback.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-24T09:13:27Z
- **Completed:** 2026-02-24T09:15:58Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- App Runner deploy, verify, and rollback scripts for API and worker services
- GitHub Actions deploy job with OIDC auth, ECR login, and serialized main-branch runs
- User setup checklist for required AWS/App Runner environment variables

## Task Commits

Each task was committed atomically:

1. **Task 1: Add App Runner deploy/verify/rollback scripts** - `31ed2a4` (feat)
2. **Task 2: Wire deploy job into GitHub Actions** - `9b24222` (feat)

**Plan metadata:** TBD

_Note: TDD tasks may have multiple commits (test → feat → refactor)_

## Files Created/Modified
- `scripts/deploy/apprunner_deploy.sh` - Build/push images and update App Runner services
- `scripts/deploy/apprunner_verify.sh` - Health checks with rollback and retry
- `scripts/deploy/apprunner_rollback.sh` - Roll back API and worker to prior image identifiers
- `.github/workflows/main.yml` - Deploy job with OIDC, ECR login, and serialized main deploys
- `.planning/phases/04-deployment-pipeline/04-USER-SETUP.md` - AWS/App Runner environment variable checklist

## Decisions Made
None - followed plan as specified.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required

**External services require manual configuration.** See `./04-USER-SETUP.md` for:
- Environment variables to add
- AWS resource references
- Verification expectations

## Next Phase Readiness

Phase 4 complete; ready to transition to Phase 5 (Latency Hardening).

---
*Phase: 04-deployment-pipeline*
*Completed: 2026-02-24*
