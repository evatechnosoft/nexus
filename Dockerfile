FROM python:3.11-slim

LABEL maintainer="evatechnosoft@gmail.com"
LABEL description="Nexus MCP Server — Skill Registry + Memory Hub"
LABEL version="2.0.0"

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer cache)
COPY nexus-hub/core/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download FastEmbed model so image works offline
RUN python3 -c "\
from fastembed import TextEmbedding; \
print('Downloading embedding model...'); \
_ = TextEmbedding('BAAI/bge-small-en-v1.5'); \
print('Model ready.')"

# Copy server source (All .py and .json in core)
COPY nexus-hub/core/*.py .
COPY nexus-hub/core/*.json .
COPY nexus-hub/templates /app/templates

# Data dirs
ENV NEXUS_DATA_DIR=/app/data
RUN mkdir -p /app/data/memory /app/data/skills /app/data/vault /app/logs

EXPOSE 8900

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:8900/health | python3 -c \
        "import sys,json; d=sys.stdin.read(); exit(0 if json.loads(d).get('status')=='ok' else 1)" \
        || exit 1

CMD ["python3", "-m", "uvicorn", "nexus_mcp_server:app", \
     "--host", "0.0.0.0", "--port", "8900"]
