# Nexus Project Handoff — 2026-04-07

## Durum: PRODUCTION ✅

---

## Bu Oturumda Tamamlananlar

### 1. CI/CD Pipeline (tam otomatik)
- `ci.yml` → dev: ruff + pytest
- `cd-test.yml` → test: ZimaOS deploy + integration tests + memory backup
- `cd-prod.yml` → prod: deploy + smoke + rollback + Docker Hub publish + release
- Self-hosted runner: ZimaOS 192.168.1.186
- Docker Hub: `deancjx/nexus-mcp:latest`
- Offline kurulum: `setup.sh --offline nexus-mcp.tar.gz`

### 2. `pipeline` Skill
- `~/.claude/skills/pipeline/SKILL.md`
- "cicd kur", "pipeline", "devops" ile tetiklenir
- Herhangi bir projeye CI/CD kurar, onaysız sonuna kadar
- Template'ler: `patterns/cicd/`

### 3. Sync Hook Zinciri
| Hook | Script | Ne Zaman |
|---|---|---|
| SessionStart | `nexus-discover.py` | Oturum açılınca |
| Stop | `nexus-sync.py` | Oturum kapanınca |
| Task Scheduler | `nexus-reconcile.py` | Her gün 20:00 |

**Akış:**
```
SessionStart: proje dizinleri + ~/.claude/ → Nexus API (hash bazlı)
Stop: değişen ~/.claude/ dosyaları → Nexus API + GitHub data/claude-config/
20:00: Local ↔ GitHub diff → eksik push → Nexus sync → Grafana metrics → rapor
```

### 4. Grafana Reconcile Panelleri
- Dashboard: `nexus-observability` @ http://192.168.1.186:4500
- 5 yeni panel: Last Reconcile, Runs, Files, Duration, Time Series
- Metrics endpoint'e reconcile state eklendi
- Run count persist: `/DATA/AppData/nexus/data/data/reconcile_runs.txt`

---

## Devam Edilecekler

### Açık Konu: Sync Stratejisi
- A seçeneği seçildi: Stop hook (anlık, yerel ağ)
- B seçeneği (GitHub üzerinden) kısmen uygulandı: reconcile + nexus-sync GitHub'a da yazar
- Sonuç: ikisi de aktif, A birincil / B gece yedek

### Opsiyonel
- `nexus-fetcher` ve `nexus-sales` projelerine `pipeline` skill uygulanabilir
- Grafana şifresini `GF_SECURITY_ADMIN_PASSWORD=admin123` olarak compose'a yazılabilir (restart'ta sıfırlanmasın)

---

## Kritik Bilgiler

```
GitHub token    : gh auth token
Docker Hub user : deancjx
Docker Hub token: <DOCKERHUB_TOKEN_IN_GITHUB_SECRETS>
Grafana         : admin:admin123 @ 192.168.1.186:4500
Nexus API       : 192.168.1.186:8900
SSH             : ssh -i ~/.ssh/zimaos_key dean@192.168.1.186
```

## GitHub Push Kuralı
`git push` çalışmaz (HTTP 408). Python REST API kullan:
```bash
cd C:/projects/skills
python3 <push_script.py>
```

## Ruff Kuralı
Server değişikliğinde önce format:
```bash
python3 -m ruff format C:/projects/skills/nexus-hub/core/nexus_mcp_server.py
```
