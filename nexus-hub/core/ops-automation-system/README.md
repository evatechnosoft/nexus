# ops-automation-system (Python / NPM-Aligned)

**Production-ready automated backup, restore validation, and health monitoring** — Optimized for Nginx Proxy Manager (NPM) and Python environments.

```
Daily backup @ 02:00    ────→  ZIP checkpoint (output/shared/checkpoints/)
                               ↓
Saturday @ 03:00        ────→  Dry-run restore validation (database integrity)
                               ↓
Every 4 hours           ────→  Health probe (endpoints + NPM data freshness)
```

## ⚡ Quick Start

### 1. Requirements
Ensure Python 3.7+ is installed.

```bash
pip install -r requirements.txt
```

### 2. Configure
Edit `config/.ops-config.json` (or use defaults for NPM).

### 3. Run Commands

```bash
python ops.py backup           # Create ZIP backup of data/ and letsencrypt/
python ops.py restore-test     # Validate latest backup integrity
python ops.py health           # Probe endpoints and check NPM status
```

---

## 📋 Components

| Component | Logic | Description |
|-----------|-------|-------------|
| **Backup** | `scripts/backup.py` | ZIPs `data/` and `letsencrypt/`. Includes manifest.json. |
| **Restore Test** | `scripts/restore_checkpoint_test.py` | Extract test. Verifies `database.sqlite` exists in ZIP. |
| **Health Report** | `scripts/health.py` | Probes NPM Admin UI and Nexus endpoints. Checks git status. |
| **Main CLI** | `ops.py` | Unified entry point for all operations. |

---

## 💾 Output Locations

```
output/
  ├── shared/checkpoints/            # Backup ZIPs
  ├── results/                        # Health report JSON
  └── logs/                           # Operation logs
```

---

## 🔧 Troubleshooting

**NPM Database missing in backup?**  
→ Ensure your NPM `data` folder is in the project root or configured in `backup.py`.

**Health report shows "warn"?**  
→ Check if Nginx Proxy Manager is running on port 81 (default Admin UI).
