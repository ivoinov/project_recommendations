#!/usr/bin/env bash
set -euo pipefail

log() {
  printf "[deploy] %s\n" "$*"
}

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    printf "[deploy] Missing required env var: %s\n" "$name" >&2
    exit 1
  fi
}

require_env AWS_REGION
require_env ECR_API_REPOSITORY
require_env ECR_WORKER_REPOSITORY
require_env APP_RUNNER_API_SERVICE_ARN
require_env APP_RUNNER_WORKER_SERVICE_ARN

IMAGE_TAG="${GITHUB_SHA:-}"
if [[ -z "$IMAGE_TAG" ]]; then
  IMAGE_TAG="$(git rev-parse HEAD)"
fi

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
API_IMAGE_URI="${REGISTRY}/${ECR_API_REPOSITORY}:${IMAGE_TAG}"
WORKER_IMAGE_URI="${REGISTRY}/${ECR_WORKER_REPOSITORY}:${IMAGE_TAG}"

ROLLBACK_STATE_FILE="${ROLLBACK_STATE_FILE:-/tmp/apprunner_previous_images.env}"

log "Building API image: ${API_IMAGE_URI}"
docker build -f Dockerfile -t "${API_IMAGE_URI}" .

log "Building worker image: ${WORKER_IMAGE_URI}"
docker build -f Dockerfile_celery -t "${WORKER_IMAGE_URI}" .

log "Pushing API image to ECR"
docker push "${API_IMAGE_URI}"

log "Pushing worker image to ECR"
docker push "${WORKER_IMAGE_URI}"

log "Capturing previous App Runner image identifiers"
PREV_API_IMAGE_IDENTIFIER="$(aws apprunner describe-service \
  --service-arn "${APP_RUNNER_API_SERVICE_ARN}" \
  --query "Service.SourceConfiguration.ImageRepository.ImageIdentifier" \
  --output text)"
PREV_WORKER_IMAGE_IDENTIFIER="$(aws apprunner describe-service \
  --service-arn "${APP_RUNNER_WORKER_SERVICE_ARN}" \
  --query "Service.SourceConfiguration.ImageRepository.ImageIdentifier" \
  --output text)"

cat > "${ROLLBACK_STATE_FILE}" <<EOF
PREV_API_IMAGE_IDENTIFIER="${PREV_API_IMAGE_IDENTIFIER}"
PREV_WORKER_IMAGE_IDENTIFIER="${PREV_WORKER_IMAGE_IDENTIFIER}"
APP_RUNNER_API_SERVICE_ARN="${APP_RUNNER_API_SERVICE_ARN}"
APP_RUNNER_WORKER_SERVICE_ARN="${APP_RUNNER_WORKER_SERVICE_ARN}"
EOF

log "Updating App Runner API service"
aws apprunner update-service \
  --service-arn "${APP_RUNNER_API_SERVICE_ARN}" \
  --source-configuration "ImageRepository={ImageIdentifier=${API_IMAGE_URI},ImageRepositoryType=ECR}"

log "Updating App Runner worker service"
aws apprunner update-service \
  --service-arn "${APP_RUNNER_WORKER_SERVICE_ARN}" \
  --source-configuration "ImageRepository={ImageIdentifier=${WORKER_IMAGE_URI},ImageRepositoryType=ECR}"

wait_for_running() {
  local arn="$1"
  local name="$2"
  local attempt=1
  local max_attempts=60

  while [[ $attempt -le $max_attempts ]]; do
    local status
    status="$(aws apprunner describe-service --service-arn "${arn}" --query "Service.Status" --output text)"
    log "${name} status: ${status} (attempt ${attempt}/${max_attempts})"

    if [[ "${status}" == "RUNNING" ]]; then
      return 0
    fi

    if [[ "${status}" == "FAILED" || "${status}" == "CREATE_FAILED" || "${status}" == "DELETED" ]]; then
      printf "[deploy] %s failed with status: %s\n" "${name}" "${status}" >&2
      return 1
    fi

    attempt=$((attempt + 1))
    sleep 10
  done

  printf "[deploy] %s did not reach RUNNING in time\n" "${name}" >&2
  return 1
}

wait_for_running "${APP_RUNNER_API_SERVICE_ARN}" "API service"
wait_for_running "${APP_RUNNER_WORKER_SERVICE_ARN}" "Worker service"

log "Deploy update complete"
