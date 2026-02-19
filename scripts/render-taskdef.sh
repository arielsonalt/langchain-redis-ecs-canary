#!/usr/bin/env bash
set -euo pipefail

TASKDEF_TEMPLATE="taskdef.json"
OUT="taskdef.rendered.json"

sed \
  -e "s|IMAGE_URI|${IMAGE_URI}|g" \
  -e "s|ECS_EXECUTION_ROLE_ARN|${ECS_EXECUTION_ROLE_ARN}|g" \
  -e "s|ECS_TASK_ROLE_ARN|${ECS_TASK_ROLE_ARN}|g" \
  -e "s|OPENAI_API_KEY_SECRET_ARN|${OPENAI_API_KEY_SECRET_ARN}|g" \
  -e "s|REDIS_URL_SECRET_ARN|${REDIS_URL_SECRET_ARN}|g" \
  "${TASKDEF_TEMPLATE}" > "${OUT}"

echo "${OUT}"
