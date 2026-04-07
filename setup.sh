#!/usr/bin/env bash
# Nexus MCP Server — setup script
# Works online (Docker Hub) and offline (local tar)
#
# Usage:
#   ./setup.sh                        # default port 8900, data in ~/.nexus/data
#   ./setup.sh --port 9000            # custom port
#   ./setup.sh --data /my/path        # custom data dir
#   ./setup.sh --offline nexus-mcp.tar.gz  # offline install from tar

set -euo pipefail

IMAGE="evatechnosoft/nexus-mcp:latest"
CONTAINER="nexus-mcp"
PORT=8900
DATA_DIR="$HOME/.nexus/data"
OFFLINE_TAR=""

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --port)    PORT="$2"; shift 2 ;;
        --data)    DATA_DIR="$2"; shift 2 ;;
        --offline) OFFLINE_TAR="$2"; shift 2 ;;
        --image)   IMAGE="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

echo ""
echo "  Nexus MCP Server Setup"
echo "  Image:    $IMAGE"
echo "  Port:     $PORT"
echo "  Data dir: $DATA_DIR"
echo ""

# --- Check Docker ---
if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker is not installed."
    echo "  Install: https://docs.docker.com/get-docker/"
    exit 1
fi

# --- Load or pull image ---
if docker image inspect "$IMAGE" &>/dev/null; then
    echo "[1/4] Image found locally, skipping pull."

elif [[ -n "$OFFLINE_TAR" ]]; then
    # Offline install from tar file
    if [[ ! -f "$OFFLINE_TAR" ]]; then
        echo "ERROR: File not found: $OFFLINE_TAR"
        exit 1
    fi
    echo "[1/4] Loading image from $OFFLINE_TAR ..."
    docker load < "$OFFLINE_TAR"

elif curl -sf --connect-timeout 5 https://hub.docker.com &>/dev/null; then
    echo "[1/4] Pulling from Docker Hub ..."
    docker pull "$IMAGE"

elif [[ -f "nexus-mcp.tar.gz" ]]; then
    echo "[1/4] No internet. Loading from nexus-mcp.tar.gz ..."
    docker load < "nexus-mcp.tar.gz"

else
    echo "ERROR: Cannot reach Docker Hub and no local image found."
    echo ""
    echo "  Offline install options:"
    echo "  1. Copy nexus-mcp.tar.gz to this directory and re-run"
    echo "  2. Run: ./setup.sh --offline /path/to/nexus-mcp.tar.gz"
    echo ""
    echo "  Get the offline package from:"
    echo "  https://github.com/evatechnosoft/nexus/releases/latest"
    exit 1
fi

# --- Prepare data directory ---
echo "[2/4] Preparing data directory ..."
mkdir -p "$DATA_DIR/memory" "$DATA_DIR/skills"

# --- Stop existing container ---
echo "[3/4] Starting container ..."
docker stop "$CONTAINER" 2>/dev/null || true
docker rm   "$CONTAINER" 2>/dev/null || true

docker run -d \
    --name "$CONTAINER" \
    --restart unless-stopped \
    -p "${PORT}:8900" \
    -v "${DATA_DIR}:/app/data" \
    "$IMAGE"

# --- Health check ---
echo "[4/4] Waiting for server to be ready ..."
for i in $(seq 1 20); do
    STATUS=$(curl -sf "http://localhost:${PORT}/health" 2>/dev/null \
        | python3 -c "import sys,json; d=sys.stdin.read(); print(json.loads(d).get('status','') if d else '')" \
        2>/dev/null) || true
    if [[ "$STATUS" == "ok" ]]; then
        echo ""
        echo "  Nexus MCP is running!"
        echo "  Health:  http://localhost:${PORT}/health"
        echo "  Metrics: http://localhost:${PORT}/metrics"
        echo "  MCP:     http://localhost:${PORT}/mcp"
        echo ""
        echo "  Add to Claude Code:"
        echo "  claude mcp add nexus --scope user -- npx -y @modelcontextprotocol/server-sse http://localhost:${PORT}/mcp"
        echo ""
        exit 0
    fi
    echo "  Attempt $i/20..."
    sleep 3
done

echo "ERROR: Server did not become healthy. Check logs:"
echo "  docker logs $CONTAINER"
exit 1
