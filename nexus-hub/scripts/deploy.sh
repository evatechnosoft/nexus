#!/usr/bin/env bash
# Manual deploy helper — mirrors what cd-prod.yml does
# Usage: ./scripts/deploy.sh [test|prod]
set -euo pipefail

ENV="${1:-test}"
ZIMAOS_USER="${ZIMAOS_USER:-dean}"
ZIMAOS_HOST="${ZIMAOS_HOST:-192.168.1.186}"
ZIMAOS_KEY="${HOME}/.ssh/zimaos_key"
REMOTE_SRC="/DATA/AppData/nexus/src"
LOCAL_SRC="nexus-hub/core"

echo "[deploy] Target: ${ENV} @ ${ZIMAOS_HOST}"

# Send source files
scp -i "${ZIMAOS_KEY}" -o StrictHostKeyChecking=no \
  "${LOCAL_SRC}"/*.py \
  "${LOCAL_SRC}/requirements.txt" \
  "${ZIMAOS_USER}@${ZIMAOS_HOST}:${REMOTE_SRC}/"

# Restart container
ssh -i "${ZIMAOS_KEY}" -o StrictHostKeyChecking=no \
  "${ZIMAOS_USER}@${ZIMAOS_HOST}" \
  "docker restart nexus-mcp"

echo "[deploy] Waiting for health..."
for i in $(seq 1 10); do
  STATUS=$(curl -sf "http://${ZIMAOS_HOST}:8900/health" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
  [ "$STATUS" = "ok" ] && echo "[deploy] ✓ Healthy (${ENV})" && exit 0
  sleep 2
done

echo "[deploy] ERROR: Health check failed" >&2
exit 1
