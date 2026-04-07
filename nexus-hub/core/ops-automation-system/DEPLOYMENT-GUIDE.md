# Deployment Guide

**Step-by-step instructions to deploy ops-automation-system to any project.**

---

## Before You Start

Ensure you have:

- **Windows**: PowerShell 5.0+, Python 3.7+
- **Linux/Mac**: Bash 4.0+, Python 3.7+
- **1-2 GB disk** for checkpoint backups
- **Admin privileges** (one-time, for Windows Task Scheduler registration)

---

## Step 1: Copy ops-automation-system to Your Project

### Option A: Copy Entire Directory

```bash
# Clone/download this repo first
git clone <ops-automation-system-repo> /tmp/ops-automation-system

# Copy to your project
cp -r /tmp/ops-automation-system/*  /my-project/scripts/ops/
cd /my-project
```

### Option B: Copy Individual Files (Minimal Setup)

If you want just essentials (no examples, lean setup):

```bash
mkdir -p /my-project/scripts/{ops,scheduler}
mkdir -p /my-project/config

# Copy scripts
cp -r /tmp/ops-automation-system/scripts/*  /my-project/scripts/ops/
cp -r /tmp/ops-automation-system/config/    /my-project/config/

# Copy package.json (merge with yours if it exists)
# See "merge package.json" below
```

**Your project structure becomes:**

```
/my-project/
├── package.json                     (add ops scripts)
├── config/
│   └── .ops-config.json            (customize)
├── scripts/ops/
│   ├── backup-checkpoint.ps1
│   ├── restore-checkpoint-test.py
│   ├── health-report.ps1
│   ├── ops-setup.ps1
│   └── scheduler/
│       ├── ops-backup-daily.xml
│       ├── ops-restore-test-weekly.xml
│       ├── ops-health-report-periodic.xml
│       └── ops-scheduler-cron.sh
└── output/                         (created on first run)
    ├── shared/checkpoints/
    ├── results/
    └── logs/
```

---

## Step 2: Customize Configuration

Edit `config/.ops-config.json`:

```bash
nano config/.ops-config.json
# or
code config/.ops-config.json
```

### Example: Basic 3-Endpoint Setup

```json
{
  "project": {
    "name": "my-project",
    "description": "Production API + Database"
  },

  "backup": {
    "includePaths": [
      ".env",
      "src/",
      "config/",
      "docs/"
    ],
    "excludePaths": [
      "node_modules/",
      ".git/",
      "dist/"
    ],
    "maxCheckpoints": 7,
    "compressionLevel": 9,
    "schedule": {
      "frequency": "daily",
      "time": "02:00",
      "timezone": "UTC"
    }
  },

  "restore": {
    "dryRunByDefault": true,
    "validateManifest": true,
    "tolerateMissingPaths": true
  },

  "health": {
    "enabled": true,
    "endpointTimeoutSeconds": 8,
    "backupFreshnessHours": 24,
    "endpoints": [
      {
        "name": "api",
        "url": "http://127.0.0.1:3000/health",
        "required": true
      },
      {
        "name": "database",
        "url": "http://localhost:5432",
        "required": true
      },
      {
        "name": "cache",
        "url": "http://localhost:6379/ping",
        "required": false
      }
    ]
  },

  "reporting": {
    "outputFormat": "json",
    "outputPath": "output/results/",
    "keepHistoryDays": 30
  },

  "notifications": {
    "enabled": false,
    "onBackupFailure": false,
    "onRestoreFailed": false,
    "onHealthWarning": false,
    "webhookUrl": null
  }
}
```

**Key fields to customize:**

| Field | Example | What to Change |
|-------|---------|-----------------|
| `project.name` | "my-project" | Your project name |
| `backup.includePaths` | `["src/", ".env"]` | Folders/files to backup |
| `backup.schedule.time` | "02:00" | When to run daily backup |
| `health.endpoints` | Array of URLs | Your service URLs to monitor |
| `health.backupFreshnessHours` | 24 | Warn if backup older than N hours |

👉 **See [docs/CONFIGURATION.md](./docs/CONFIGURATION.md)** for all fields explained.

---

## Step 3: Add npm Commands

### Merge package.json

If you **don't** have a `package.json` yet:

```bash
# Copy ours
cp /tmp/ops-automation-system/package.json  /my-project/package.json
```

If you **already** have one, merge manually or programmatically:

Option A: **Manual merge** (easiest if 2-3 scripts)

Open your `package.json`, find `"scripts"` section, add:

```json
"scripts": {
  "ops:backup": "pwsh -NoProfile -File scripts/ops/backup-checkpoint.ps1",
  "ops:restore-test": "python scripts/ops/restore-checkpoint-test.py",
  "ops:health-report": "pwsh -NoProfile -File scripts/ops/health-report.ps1",
  "ops:setup-register": "pwsh -NoProfile -File scripts/ops/ops-setup.ps1 -RegisterTasks",
  "ops:setup-unregister": "pwsh -NoProfile -File scripts/ops/ops-setup.ps1 -UnregisterTasks",
  "ops:setup-list": "pwsh -NoProfile -File scripts/ops/ops-setup.ps1 -ListTasks",
  "ops:setup-help": "pwsh -NoProfile -File scripts/ops/ops-setup.ps1 -Help"
}
```

Option B: **Script merge** (if you want automation)

```bash
# (Provided separately if needed — ask ops team)
node merge-package-json.js
```

Test it works:

```bash
npm run ops:backup --help
# Should show PowerShell script starting
```

---

## Step 4: Test Manually (Before Scheduling)

### 4.1 Test Backup Creation

```bash
npm run ops:backup
```

**Expected output:**

```
[ops:backup] Backup checkpoint started
[ops:backup] Config: config/.ops-config.json
[ops:backup] Include paths: .env src/ config/ docs/
[ops:backup] Exclude paths: node_modules/ .git/ dist/
[ops:backup] Copying files...
Copying 1234 of 4567 files [234.5 MB of 456.7 MB (12.3 MB/s)]
...
[ops:backup] ✓ Checkpoint created: output/shared/checkpoints/checkpoint-20260331-140230.zip (456.7 MB)
```

**Verify:**

```bash
ls -lh output/shared/checkpoints/
# Should show latest ZIP file
```

### 4.2 Test Restore Validation

```bash
npm run ops:restore-test
```

**Expected output:**

```
[ops:restore-test] using output/shared/checkpoints/checkpoint-20260331-140230.zip
[ops:restore-test] extracting to [temp-dir]
[ops:restore-test] validating manifest.json
[ops:restore-test] file count: 1234 (expected 1234) ✓
[ops:restore-test] optional paths: 2 missing (OK)
[ops:restore-test] ✓ PASS
```

### 4.3 Test Health Report

```bash
npm run ops:health-report
```

**Expected output:**

```
[ops:health-report] Probing endpoints...
[ops:health-report]   api (http://127.0.0.1:3000/health): ok (45ms)
[ops:health-report]   database (http://localhost:5432): ok (2ms)
[ops:health-report]   cache (http://localhost:6379): timeout (>8s)
[ops:health-report] Backup freshness: 2h ago ✓
[ops:health-report] overall=ok
[ops:health-report] report=output/results/ops-health-latest.json
```

**Verify report:**

```bash
cat output/results/ops-health-latest.json
# Should show JSON with endpoint statuses
```

---

## Step 5: Register Scheduled Tasks

### Option A: Windows Task Scheduler

**Prerequisites:**

- Must run in Administrator PowerShell
- First time only (registration is permanent)

**Register tasks:**

```bash
# From Administrator PowerShell
npm run ops:setup-register
```

**Expected output:**

```
[ops-setup] Installing scheduled tasks...

[ops-setup] Registering ops-backup-daily...
  DONE
[ops-setup] Registering ops-restore-test-weekly...
  DONE
[ops-setup] Registering ops-health-report-periodic...
  DONE

[ops-setup] All tasks registered
```

**Verify registration:**

```bash
npm run ops:setup-list
```

Expected:

```
[ops-setup] Installed apiflow-ops scheduled tasks:
  [ENABLED] ops-backup-daily
  [ENABLED] ops-restore-test-weekly
  [ENABLED] ops-health-report-periodic
```

**Manual trigger (test before waiting for schedule):**

```powershell
Get-ScheduledTask "ops-backup-daily" | Start-ScheduledTask
# Wait 5 seconds...
ls output/shared/checkpoints/ | Sort-Object LastWriteTime -Descending | Select -First 1
# Should show newly created ZIP
```

### Option B: Linux/Mac Cron

**Install cron jobs:**

```bash
bash scripts/ops/scheduler/ops-scheduler-cron.sh install
```

**Expected output:**

```
Parsing config file: config/.ops-config.json
Setting up cron jobs...
✓ Added cron: ops-backup (daily @ 02:00)
✓ Added cron: ops-restore-test (Saturday @ 03:00)
✓ Added cron: ops-health-report (every 4 hours)
3 cron jobs installed.
```

**Verify installation:**

```bash
bash scripts/ops/scheduler/ops-scheduler-cron.sh list
```

Expected:

```
3 cron jobs found:
  0 2 * * * cd /my-project && npm run ops:backup
  0 3 * * 6 cd /my-project && npm run ops:restore-test
  0 */4 * * * cd /my-project && npm run ops:health-report
```

**View cron logs:**

```bash
tail -f output/logs/ops-backup.log
tail -f output/logs/ops-health-report.log
```

---

## Step 6: Validate End-to-End

Wait for one scheduled run cycle, then verify:

### Daily Backup (Runs @ 02:00 by default)

```bash
# Check checkpoint was created
ls -lh output/shared/checkpoints/ | head -5

# Should show recent ZIP, e.g.:
# checkpoint-20260401-020030.zip

# Check size is reasonable (not 0 MB)
```

### Weekly Restore Test (Runs Saturdays @ 03:00)

```bash
# Check last restore log
ls -lh output/logs/ops-restore-test.log 2>/dev/null || echo "Log not created yet (cron-specific)"

# Or manually trigger to verify:
npm run ops:restore-test
```

### Periodic Health Report (Every 4 hours)

```bash
# Check health report JSON
cat output/results/ops-health-report.json | jq .

# Should show:
# {
#   "timestamp": "2026-04-01T02:00:15Z",
#   "overall": "ok" or "warn",
#   "endpoints": [...],
#   "backup": { "freshness": "...", "status": "ok" }
# }
```

---

## Step 7 (Optional): Add to CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/backup.yml
name: Backup Validation

on:
  schedule:
    - cron: '0 2 * * *'  # 02:00 UTC daily
  workflow_dispatch:

jobs:
  backup:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Create checkpoint
        run: npm run ops:backup
      
      - name: Validate checkpoint
        run: npm run ops:restore-test
      
      - name: Health check
        run: npm run ops:health-report
      
      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: ops-reports
          path: output/results/
```

---

## Troubleshooting

### Backup creates 0 MB ZIP

**Cause**: No files matched `includePaths`

**Fix**:
1. Verify paths exist: `ls -la src/` (example)
2. Check `config/.ops-config.json` paths are correct
3. Verify no leading/trailing spaces in paths

### Health report shows "timeout"

**Cause**: Endpoint unreachable or slow

**Fix**:
1. Manually test: `curl http://your-endpoint/health`
2. Increase timeout: Edit `config/.ops-config.json`, set `endpointTimeoutSeconds: 15`
3. Verify service is running

### Task Scheduler registration fails

**Cause**: Not running as Administrator

**Fix**:
```powershell
# Right-click PowerShell → Run as Administrator
# Then:
npm run ops:setup-register
```

### cron jobs not running on Linux

**Cause**: cron daemon not running or permission issue

**Fix**:
```bash
# Check if cron running
sudo service cron status

# Check cron logs
sudo tail -f /var/log/syslog | grep CRON

# Reinstall cron jobs
bash scripts/ops/scheduler/ops-scheduler-cron.sh uninstall
bash scripts/ops/scheduler/ops-scheduler-cron.sh install
```

👉 **More issues?** See [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)

---

## Next Steps

✅ **Deployment complete!** Now:

1. **Monitor**: Check `output/results/ops-health-latest.json` regularly
2. **Tune**: Adjust retention, timeout, schedule in `config/.ops-config.json` if needed
3. **Integrate**: Add to CI/CD, monitoring dashboards, etc.
4. **Document**: Add ops commands to your team wiki/playbook

---

**Questions?** See:
- [README.md](./README.md) — Quick overview
- [ARCHITECTURE.md](./ARCHITECTURE.md) — Design decisions
- [docs/CONFIGURATION.md](./docs/CONFIGURATION.md) — Config fields
- [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) — Common issues
