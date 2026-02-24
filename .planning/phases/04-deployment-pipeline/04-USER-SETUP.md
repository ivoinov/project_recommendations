# Phase 4: User Setup Required

**Generated:** 2026-02-24
**Phase:** 04-deployment-pipeline
**Status:** Incomplete

Complete these items for the App Runner deploy pipeline to function. OpenCode automated everything possible; these items require human access to external dashboards/accounts.

## Environment Variables

| Status | Variable | Source | Add to |
|--------|----------|--------|--------|
| [ ] | `AWS_ROLE_ARN` | AWS IAM → Roles (OIDC trust for GitHub Actions) | GitHub Actions secret |
| [ ] | `AWS_REGION` | AWS Console → Region for App Runner and ECR | GitHub Actions variable |
| [ ] | `ECR_API_REPOSITORY` | Amazon ECR → Repositories (API image repo name) | GitHub Actions variable |
| [ ] | `ECR_WORKER_REPOSITORY` | Amazon ECR → Repositories (worker image repo name) | GitHub Actions variable |
| [ ] | `APP_RUNNER_API_SERVICE_ARN` | App Runner → API service → Service ARN | GitHub Actions variable |
| [ ] | `APP_RUNNER_WORKER_SERVICE_ARN` | App Runner → Worker service → Service ARN | GitHub Actions variable |
| [ ] | `API_HEALTH_URL` | App Runner → API service URL + /health | GitHub Actions variable |
| [ ] | `WORKER_HEALTH_URL` | App Runner → Worker service URL + /health | GitHub Actions variable |

## Verification

After completing setup, verify with:

```bash
# Trigger a merge to main or rerun the latest workflow
# Confirm the deploy job runs and reaches the health verification step
```

Expected results:
- Deploy job configures AWS credentials via OIDC
- API and worker App Runner services update to the commit SHA image tag
- Health checks pass for both services

---

**Once all items complete:** Mark status as "Complete" at top of file.
