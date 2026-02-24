# Phase 4: Deployment Pipeline - Research

**Researched:** 2026-02-24
**Domain:** CI/CD deployment for FastAPI API + Celery worker to AWS App Runner (container-based)
**Confidence:** MEDIUM

## Summary

This phase is about a fully automated CI/CD pipeline that deploys the API and the worker on every merge to `main`, with serialized deploys, automated verification, and rollback on failed checks. The repo already uses GitHub Actions and Docker, so the standard approach is to extend the workflow to build/push container images to a registry and update App Runner services via AWS CLI.

AWS App Runner supports services sourced from ECR images, with health check configuration and automated deployments when new images are pushed. The CI/CD workflow should explicitly update both the API and worker services to the new image identifiers, wait for App Runner operations to finish, then run health/status checks against each service and rollback if needed.

**Primary recommendation:** Use GitHub Actions + AWS OIDC credentials to build/push API and worker images to ECR, update both App Runner services via `aws apprunner update-service`, then run automated health checks with rollback to the previous image tags on failure.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| AWS App Runner | Managed service | Host API + worker containers | Official AWS managed web service for container deployments |
| Amazon ECR | Managed service | Container registry for images | Native App Runner image source |
| AWS CLI | v2 | Deploy/update App Runner services | Official CLI for App Runner operations |
| GitHub Actions | SaaS | CI/CD orchestration | Already used in repo and supports AWS OIDC |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| aws-actions/configure-aws-credentials | v6 | OIDC auth to AWS in CI | Required for secure CI deploys |
| aws-actions/amazon-ecr-login | v2 | Docker login to ECR | Required before pushing images |
| docker/setup-buildx-action | v3 | Buildx for Docker builds | If multi-platform or build cache desired |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| AWS App Runner + ECR | Cloud Run + Artifact Registry | GCP-native stack; requires gcloud auth and different deploy commands |

**Installation:**
```bash
# GitHub Actions runners include Docker and AWS CLI v2
# Local dev install (optional): https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
```

## Architecture Patterns

### Recommended Project Structure
```
.github/
└── workflows/
    └── deploy.yml      # build/push + App Runner updates + verification
infra/
└── deploy/             # scripts for update/rollback/verify (optional)
```

### Pattern 1: Build + Push API and Worker Images to ECR
**What:** Build two images (API, worker), tag with commit SHA, push to ECR.
**When to use:** Every merge to `main`, prior to updating App Runner.
**Example:**
```yaml
# Source: https://github.com/aws-actions/amazon-ecr-login
- name: Login to Amazon ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Build, tag, and push docker image to Amazon ECR
  env:
    REGISTRY: ${{ steps.login-ecr.outputs.registry }}
    REPOSITORY: recommendation-api
    IMAGE_TAG: ${{ github.sha }}
  run: |
    docker build -t $REGISTRY/$REPOSITORY:$IMAGE_TAG .
    docker push $REGISTRY/$REPOSITORY:$IMAGE_TAG
```

### Pattern 2: Update App Runner Service with New Image Identifier
**What:** Use `aws apprunner update-service` to point the service at the new ECR image.
**When to use:** After pushing images; repeat for API and worker services.
**Example:**
```bash
# Source: https://docs.aws.amazon.com/cli/latest/reference/apprunner/update-service.html
aws apprunner update-service \
  --service-arn "$SERVICE_ARN" \
  --source-configuration "ImageRepository={ImageIdentifier=$IMAGE_URI,ImageRepositoryType=ECR}"
```

### Pattern 3: Health Check Configuration and Verification
**What:** Configure App Runner health checks to use HTTP endpoints, then verify with CI.
**When to use:** Configure on service creation or update; verify after each deploy.
**Example:**
```bash
# Source: https://docs.aws.amazon.com/cli/latest/reference/apprunner/update-service.html
aws apprunner update-service \
  --service-arn "$SERVICE_ARN" \
  --health-check-configuration "Protocol=HTTP,Path=/health"
```

### Anti-Patterns to Avoid
- **Relying on App Runner auto-deploy without CI verification:** Auto-deploy on image push skips explicit verification and rollback logic.
- **Deploying only the changed service:** Phase decisions require deploying API and worker together every merge.
- **Using long-lived AWS keys in GitHub Secrets:** Prefer OIDC for short-lived credentials.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| AWS auth in CI | Custom credential scripts | `aws-actions/configure-aws-credentials` (OIDC) | Secure, short-lived creds; standard practice |
| ECR login | Manual `aws ecr get-login-password` in workflow | `aws-actions/amazon-ecr-login` | Handles registry login and outputs cleanly |
| Health checks | Custom cron/polling service | App Runner health checks + CI `curl` | Built-in health check + explicit deploy verification |

**Key insight:** Leverage official GitHub Actions + AWS CLI to keep CI/CD minimal, auditable, and consistent with AWS guidance.

## Common Pitfalls

### Pitfall 1: Worker has no HTTP health endpoint
**What goes wrong:** App Runner health checks fail or default TCP check fails if no port is open.
**Why it happens:** Celery workers are long-running processes without an HTTP server.
**How to avoid:** Add a lightweight HTTP health endpoint in the worker container or run a health-probe sidecar; configure App Runner health checks to that path.
**Warning signs:** App Runner service stuck in `CREATE_FAILED` or `OPERATION_IN_PROGRESS` with unhealthy status.

### Pitfall 2: Deploy verification runs before App Runner update completes
**What goes wrong:** Health checks hit the old revision or a still-starting service.
**Why it happens:** `update-service` is asynchronous.
**How to avoid:** Poll App Runner operations or service status until `RUNNING` before verification.
**Warning signs:** Flaky deploys that pass on retry without changes.

### Pitfall 3: Auto-deploy enabled + CI deploy causes duplicate rollouts
**What goes wrong:** An ECR push triggers an automatic App Runner deploy, and CI triggers another.
**Why it happens:** App Runner `AutoDeploymentsEnabled` defaults to `true` for same-account ECR.
**How to avoid:** Disable auto-deploy and control deployments from CI, or keep auto-deploy and skip CI update-service calls.
**Warning signs:** Multiple App Runner operations per merge.

## Code Examples

Verified patterns from official sources:

### Configure AWS OIDC in GitHub Actions
```yaml
# Source: https://github.com/aws-actions/configure-aws-credentials
permissions:
  id-token: write

steps:
  - name: Configure AWS Credentials
    uses: aws-actions/configure-aws-credentials@v6
    with:
      role-to-assume: arn:aws:iam::<AWS_ACCOUNT_ID>:role/<ROLE_NAME>
      aws-region: us-east-1
```

### Push Image to Amazon ECR
```bash
# Source: https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html
aws ecr get-login-password --region <region> | \
  docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Long-lived AWS keys in GitHub Secrets | OIDC with `configure-aws-credentials` | 2021+ (OIDC support in GitHub Actions) | Short-lived, least-privilege credentials |

**Deprecated/outdated:**
- **Static AWS access keys in CI:** OIDC is the standard and safer approach for AWS deployments.

## Open Questions

1. **Final hosting target (AWS App Runner vs GCP Cloud Run)**
   - What we know: Phase 1 decision allows either App Runner or Cloud Run.
   - What's unclear: Which provider is selected for v1.
   - Recommendation: Confirm target now; this determines CI auth (AWS OIDC vs GCP Workload Identity) and deploy commands.

## Sources

### Primary (HIGH confidence)
- https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html - App Runner overview
- https://docs.aws.amazon.com/cli/latest/reference/apprunner/update-service.html - App Runner update-service, health check config
- https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html - ECR push workflow
- https://github.com/aws-actions/configure-aws-credentials - OIDC action usage
- https://github.com/aws-actions/amazon-ecr-login - ECR login action usage

### Secondary (MEDIUM confidence)
- https://cloud.google.com/run/docs/deploying - Cloud Run deploy command (alternative)

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - AWS sources verified; final provider choice pending.
- Architecture: MEDIUM - Based on App Runner CLI and AWS Actions docs.
- Pitfalls: MEDIUM - Derived from App Runner behavior and workflow async deploys.

**Research date:** 2026-02-24
**Valid until:** 2026-03-26
