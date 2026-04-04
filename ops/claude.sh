#!/bin/bash
# Nexus Brain - Universal Dockerized CLI (ZimaOS Survival)
# Bu script, host sisteme dokunmadan izole Node.js ortamında Claude Code çalıştırır.

# Config
CONFIG_DIR="/DATA/AppData/claude-config"
OLLAMA_HOST="http://192.168.1.186:4602" # Nexus Port
# ANTHROPIC_API_KEY="sk-..." (Gerekli olduğunda eklenecek)
# GOOGLE_GENERATIVE_AI_API_KEY="..." (Gerekli olduğunda eklenecek)

# Docker İzin Hatalarını Gizle & Yazılabilir Alanı Göster
export DOCKER_CONFIG="${CONFIG_DIR}/.docker"

docker run -it --rm \
  -v "${CONFIG_DIR}:/root" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
  -e GOOGLE_GENERATIVE_AI_API_KEY="${GOOGLE_GENERATIVE_AI_API_KEY}" \
  -e OLLAMA_HOST="${OLLAMA_HOST}" \
  -e DOCKER_CONFIG="/root/.docker" \
  node:20-slim \
  sh -c "npm list -g @anthropic-ai/claude-code || npm install -g @anthropic-ai/claude-code && claude --model ollama/qwen3.5:9b"
