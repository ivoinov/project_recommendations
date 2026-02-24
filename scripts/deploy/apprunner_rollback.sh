#!/usr/bin/env bash
set -euo pipefail

log() {
  printf "[rollback] %s\n" "$*"
}

ROLLBACK_STATE_FILE="${ROLLBACK_STATE_FILE:-/tmp/apprunner_previous_images.env}"

if [[ ! -f "${ROLLBACK_STATE_FILE}" ]]; then
  printf "[rollback] Rollback state file not found: %s\n" "${ROLLBACK_STATE_FILE}" >&2
  exit 1
fi

source "${ROLLBACK_STATE_FILE}"

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    printf "[rollback] Missing required value: %s\n" "$name" >&2
    exit 1
  fi
}

require_env PREV_API_IMAGE_IDENTIFIER
require_env PREV_WORKER_IMAGE_IDENTIFIER
require_env APP_RUNNER_API_SERVICE_ARN
require_env APP_RUNNER_WORKER_SERVICE_ARN

log "Rolling back API service"
aws apprunner update-service \
  --service-arn "${APP_RUNNER_API_SERVICE_ARN}" \
  --source-configuration "ImageRepository={ImageIdentifier=${PREV_API_IMAGE_IDENTIFIER},ImageRepositoryType=ECR}"

log "Rolling back worker service"
aws apprunner update-service \
  --service-arn "${APP_RUNNER_WORKER_SERVICE_ARN}" \
  --source-configuration "ImageRepository={ImageIdentifier=${PREV_WORKER_IMAGE_IDENTIFIER},ImageRepositoryType=ECR}"

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
      printf "[rollback] %s failed with status: %s\n" "${name}" "${status}" >&2
      return 1
    fi

    attempt=$((attempt + 1))
    sleep 10
  done

  printf "[rollback] %s did not reach RUNNING in time\n" "${name}" >&2
  return 1
}

wait_for_running "${APP_RUNNER_API_SERVICE_ARN}" "API service"
wait_for_running "${APP_RUNNER_WORKER_SERVICE_ARN}" "Worker service"

log "Rollback complete"
