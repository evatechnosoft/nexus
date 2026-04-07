# Nexus Observability Setup — Handoff (2026-04-06)

## ✅ Completed

### Phase 1: Rebranding
- ✅ nexus-brain → nexus (Docker service, MCP config, file names)
- ✅ MCP hub: `http://192.168.1.186:8900/mcp` (endpoint live)

### Phase 2: SSH Passwordless Auth
- ✅ ED25519 key generated: `~/.ssh/zimaos_key`
- ✅ Public key added to ZimaOS: `~/.ssh/authorized_keys`
- ✅ Verified: `ssh -i ~/.ssh/zimaos_key dean@192.168.1.186` (no password)
- ✅ Rule added to memory: `~/.claude/rules/memory-decisions.md`

### Phase 3: Prometheus + Grafana
- ✅ Grafana running: `http://192.168.1.186:4500` (port 3100→4500 mapping)
- ✅ Prometheus datasource created: "prometheus" (type: Prometheus)
- ✅ Dashboard imported: "Nexus MCP Server - System Observability" (uid: nexus-observability)
- ✅ 5 visualization panels: latency, error-rate, request-volume, uptime, tool-invocations
- ✅ Refresh interval: 10 seconds
- ✅ Time range: Last 1 hour

## ✅ Session 2 Verification (2026-04-06)

### Metrics Endpoint — Verified Working ✅
```
nexus_uptime_seconds 2946
nexus_requests_total 10
nexus_request_error_rate_percent 0.00
nexus_request_latency_ms 0.08
nexus_tool_calls_total 0
```
- **Status:** `/metrics` endpoint returning valid Prometheus format
- **Command:** `curl http://192.168.1.186:8900/metrics`

### Container Status
- **nexus-mcp:** Running (logs clean, all requests 200 OK)
- **agentops-nexus-db:** Healthy
- **Datasource connectivity:** 200 OK on GET, 405 on HEAD (expected)

## ⚠️ Known Issues & Session 2 Actions

| Issue | Status | Action Taken |
|-------|--------|--------|
| **Container not running** | ⚠️ Blocker | Updated `/DATA/AppData/nexus-brain/src/mcp_server.py` with `/metrics` + `/health` endpoints |
| **Docker/pip limited** | ⚠️ ZimaOS restricted | CasaOS/Portainer UI needed for container deploy (SSH/bash insufficient) |
| **Dashboard "No data"** | ⏳ Waiting | Needs running container with working `/metrics` endpoint |

### Session 2 Completed Work
✅ **Added to mcp_server.py:**
- `/health` endpoint: returns `{"status": "ok", "uptime_seconds": N}`
- `/metrics` endpoint: complete Prometheus format with nexus_* metrics
- Updated `docker-compose.yml`: removed `:ro` (read-only) mounts

✅ **Files modified:**
- `/DATA/AppData/nexus-brain/src/mcp_server.py` — added endpoints
- `/DATA/AppData/nexus-brain/docker-compose.yml` — removed RO constraints

### ✅ Session 2 DEPLOYED: Container Running

**Method:** docker run CLI (docker-compose binary not available, but docker CLI works via socket)

```bash
docker run -d --name nexus-mcp --restart always -p 8900:8900 \
  -v /DATA/AppData/nexus/src:/app/src:ro \
  -v /DATA/AppData/nexus/requirements.txt:/app/requirements.txt:ro \
  -w /app python:3.12-slim \
  bash -c "pip install -q fastapi uvicorn && python src/mcp_server.py"
```

**Live Status (2026-04-06):**
- ✅ Container: nexus-mcp (Up, port 8900 listening)
- ✅ `/health` → `{"status": "ok", "uptime_seconds": N}`
- ✅ `/metrics` → Prometheus format streaming live

**Directory Structure Updated:**
- `/DATA/AppData/nexus-brain/` → `/DATA/AppData/nexus/` ✅

**Next Session:**
1. Grafana dashboard auto-refresh (F5) → panels populate from Prometheus datasource
2. If "No data" persists: verify datasource URL in Grafana UI (admin auth required)

## 🔧 Verification Steps (Token-efficient)

### Quick Check (SSH only, no browser)
```bash
# Metrics flowing?
ssh -i ~/.ssh/zimaos_key dean@192.168.1.186 \
  "curl -s http://192.168.1.186:8900/metrics | grep nexus_uptime"

# Container healthy?
ssh -i ~/.ssh/zimaos_key dean@192.168.1.186 \
  "docker ps --filter name=nexus --format 'table {{.Names}}\t{{.Status}}'"
```

### Manual Dashboard Refresh (Browser)
1. Open: `http://192.168.1.186:4500/d/nexus-observability/`
2. Press F5 or click refresh button
3. Wait 30 seconds
4. If "No data" persists, check datasource URL in Connections menu

### Optional Enhancements
- Add Grafana alert rule: error_rate > 5%
- Export metrics to external monitoring (Datadog, New Relic, etc.)
- Configure InfluxDB alongside Prometheus for time-series backup

## 📁 Key Files

| File | Purpose |
|------|---------|
| `~/.ssh/zimaos_key` | ED25519 private key (passwordless SSH) |
| `~/.ssh/zimaos_key.pub` | Public key (already on ZimaOS) |
| `~/.claude/mcp_servers.json` | MCP hub config (nexus) |
| `~/.claude/rules/memory-decisions.md` | SSH rule + setup notes |
| `C:\Users\Deacjx\grafana_nexus_dashboard.json` | Pre-built dashboard JSON |
| `C:\Users\Deacjx\prometheus_nexus_config.yml` | Prometheus scrape config (optional) |
| `C:\Users\Deacjx\NEXUS_OBSERVABILITY_SETUP.md` | Full setup guide |

## 🎯 Current Status

**Ready for metrics flow** — Dashboard structure is complete. Just needs:
1. Prometheus datasource URL verification (already created in Grafana UI)
2. Metrics to start flowing from nexus-mcp

Once verified, all 5 panels will display live metrics with 10-second refresh.

---

**Next session**: Verify datasource + test metrics flow. If successful, setup complete. If "No data" persists, investigate nexus-mcp /metrics endpoint health.
