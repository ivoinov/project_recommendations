#!/usr/bin/env bash
set -euo pipefail

log() {
  printf "[verify] %s\n" "$*"
}

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    printf "[verify] Missing required env var: %s\n" "$name" >&2
    exit 1
  fi
}

require_env API_HEALTH_URL
require_env WORKER_HEALTH_URL

ROLLBACK_STATE_FILE="${ROLLBACK_STATE_FILE:-/tmp/apprunner_previous_images.env}"

check_url() {
  local name="$1"
  local url="$2"
  local attempt=1
  local max_attempts=10

  while [[ $attempt -le $max_attempts ]]; do
    if curl --fail --silent --show-error --max-time 10 "${url}" > /dev/null; then
      log "${name} health check passed"
      return 0
    fi

    log "${name} health check failed (attempt ${attempt}/${max_attempts})"
    attempt=$((attempt + 1))
    sleep 5
  done

  return 1
}

run_checks() {
  check_url "API" "${API_HEALTH_URL}" && check_url "Worker" "${WORKER_HEALTH_URL}"
}

if run_checks; then
  log "All health checks passed"
  exit 0
fi

log "Health checks failed - initiating rollback"
ROLLBACK_STATE_FILE="${ROLLBACK_STATE_FILE}" scripts/deploy/apprunner_rollback.sh

log "Retrying health checks after rollback"
if run_checks; then
  log "Health checks passed after rollback"
  exit 0
fi

printf "[verify] Health checks failed after rollback\n" >&2
exit 1
