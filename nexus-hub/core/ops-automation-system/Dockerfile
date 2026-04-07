# Lightweight Python base image
FROM python:3.12-slim

# System dependencies (git is used in health.py)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ops.py .
COPY scripts/ ./scripts/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p data letsencrypt output/shared/checkpoints output/results output/logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Istanbul

# Volumes:
# /app/data: NPM database and config
# /app/letsencrypt: SSL certificates
# /app/output: Backups and health reports
VOLUME ["/app/data", "/app/letsencrypt", "/app/output"]

# Default command (Check health status)
ENTRYPOINT ["python", "ops.py"]
CMD ["health"]
