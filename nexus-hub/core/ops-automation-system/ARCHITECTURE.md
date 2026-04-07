# Architecture

**How ops-automation-system is designed, why, and how the pieces fit together.**

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  CONFIGURATION LAYER                                        │
│  ├─ .ops-config.json (tunable: paths, endpoints, times)   │
│  └─ All ops commands read config, no hardcoding             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  OPERATIONAL LAYER (3 independent systems)                 │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 1. BACKUP    │  │ 2. RESTORE   │  │ 3. HEALTH    │      │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤      │
│  │ PowerShell   │  │ Python       │  │ PowerShell   │      │
│  │ -Compress    │  │ zipfile.py   │  │ WebRequest   │      │
│  │ Archive      │  │ manifest.json│  │ JSON report  │      │
│  │ Creates ZIP  │  │ Validates    │  │ Probes       │      │
│  │ + manifest   │  │ checkpoints  │  │ endpoints    │      │
│  │ in seconds   │  │ (dry-run)    │  │ (no threshol│      │
│  │              │  │              │  │  hardcoded)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│       ↓                  ↓                  ↓               │
│   output/shared/     output/results/    output/results/    │
│   checkpoints/       ops-restore-      ops-health-        │
│   (ZIP files)        test-latest.json   latest.json       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SCHEDULER LAYER (choose one: Windows OR Linux/Mac)        │
│                                                             │
│  ┌─ Windows ──────────────────┐  ┌─ Unix/Linux ────────┐   │
│  │ Task Scheduler             │  │ cron (via shell)     │   │
│  │ ├─ ops-backup-daily.xml    │  │ ├─ backup entry     │   │
│  │ ├─ ops-restore-test        │  │ ├─ restore entry    │   │
│  │ │  -weekly.xml             │  │ ├─ health entry     │   │
│  │ └─ ops-health-report       │  │ ├─ Generated from   │   │
│  │    -periodic.xml           │  │ │  .ops-config.json  │   │
│  │ Setup: ops-setup.ps1       │  │ │  schedule times    │   │
│  │        -RegisterTasks      │  │ │  (automatic)        │   │
│  └────────────────────────────┘  │ Setup: cron shell   │   │
│                                  │        install      │   │
│                                  └─────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Decision Log

### Why 3 Separate Scripts?

| Script | Why | Not Monolithic? |
|--------|-----|-----------------|
| **backup-checkpoint.ps1** | PowerShell `Compress-Archive` is battle-tested, idiomatic on Windows | Python zipfile is cross-platform but less intuitive for Windows users |
| **restore-checkpoint-test.py** | Python handles ZIP + JSON manifest cleanly. Avoids PowerShell Assembly loading deadlock issue | PowerShell `Expand-Archive` had threading issues in testing (Ctrl-C timeout) |
| **health-report.ps1** | Simple WebRequest + JSON output. Stays in PowerShell for Windows consistency | Could be Python but no advantage, adds dependency |

**Design principle**: Each script does ONE thing well. No god-objects.

---

### Why Configuration ≠ Hardcoding?

All 3 scripts read `.ops-config.json` at runtime:

```powershell
# backup-checkpoint.ps1, health-report.ps1 both do:
function Read-OpsConfig {
  $json = Get-Content $configFile -Raw | ConvertFrom-Json
  return $json
}

# Access config like:
$config.backup.maxCheckpoints         # 7 (retention)
$config.health.endpointTimeoutSeconds # 8 (timeout per probe)
$config.health.endpoints              # Array of endpoints
```

**Benefits**:
- Deploy same code to 100 projects, each with different backup paths/endpoints
- No recompiling, no code changes, just JSON tuning
- Non-technical users can adjust thresholds (no coding needed)

---

### Why Separate Scheduler Templates?

**Windows Task Scheduler XML templates** (`ops-backup-daily.xml` etc):

```xml
<Task>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-03-31T02:00:00</StartBoundary>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>npm run ops:backup</Command>
    </Exec>
  </Actions>
</Task>
```

**Why XML?** Task Scheduler is **THE** Windows automation framework. No `schedule` gem (Ruby), no cron (Linux utility). Pure Windows-native.

**ops-scheduler-cron.sh** (Linux/Mac):

```bash
# Parses .ops-config.json, generates cron entries
# 0 2 * * * cd /project && npm run ops:backup
# 0 3 * * 6 cd /project && npm run ops:restore-test
```

**Why separate?** cron is Unix-native. One line per job.

---

### Why .ops-config.json at Repo Root?

```
/my-project/
├── .ops-config.json         ← Easy to find, customize, version-control
├── config/.ops-config.json  ← NO (too nested, easy to overlook)
└── .config/ops.json         ← NO (inconsistent naming)
```

All 3 scripts look for `config/.ops-config.json` relative to script directory:

```powershell
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$configFile = Join-Path $repoRoot 'config\.ops-config.json'
```

Path resolution handles:
- Direct PowerShell execution: `.\scripts\backup-checkpoint.ps1`
- npm invocation: `npm run ops:backup`
- Scheduled task: Task Scheduler runs from system context
- cron: Bash cd's to repo first

---

### Why manifest.json Inside ZIP?

Each backup ZIP includes `manifest.json`:

```json
{
  "timestamp": "2026-03-31T20:15:30Z",
  "includePaths": [".claude", ".copilot", "src/"],
  "fileCount": 30027,
  "sizeBytes": 907000000,
  "checksumMethods": ["file-count", "manifest-integrity"]
}
```

**Why?**
- `restore-checkpoint-test.py` validates ZIP **integrity** without extracting entire 867 MB  
- Detects corrupted ZIPs on Day 1, not Day 100  
- Dry-run (no actual restore) means rapid feedback  

---

### Why npm Commands Wrapper?

Instead of:

```bash
pwsh -NoProfile -File scripts/backup-checkpoint.ps1
python scripts/restore-checkpoint-test.py
npm install ./custom-wheels/  # etc
```

Users type:

```bash
npm run ops:backup
npm run ops:restore-test
```

**package.json**:

```json
{
  "scripts": {
    "ops:backup": "pwsh -NoProfile -File scripts/backup-checkpoint.ps1",
    "ops:restore-test": "python scripts/restore-checkpoint-test.py",
    "ops:health-report": "pwsh -NoProfile ...",
    "ops:setup-register": "pwsh -NoProfile -File scripts/ops-setup.ps1 -RegisterTasks"
  }
}
```

**Benefits**:
- One canonical command per operation (no memorizing file paths)
- Cross-platform abstraction (same `npm run` on Windows/Linux)
- Dependencies declared in `package.json` (version pinning, reproducibility)
- Easy CI/CD integration: `npm run ops:backup` in GitHub Actions

---

## Data Flow

### Backup Flow

```
(scheduled or manual)
     ↓
npm run ops:backup
     ↓
backup-checkpoint.ps1
  ├─ Read config (.ops-config.json)
  ├─ Expand include paths (substitute $home, etc)
  ├─ Check disk space (abort if <1 GB free)
  ├─ Get latest checkpoint + cleanup old ones (max 7)
  ├─ Compress-Archive to ZIP
  ├─ Generate manifest.json
  └─ Write to output/shared/checkpoints/checkpoint-YYYYMMDD-HHMMSS.zip
     ↓
(879 MB checkpoint ready for validation)
```

### Validate Flow

```
(scheduled or manual)
     ↓
npm run ops:restore-test
     ↓
restore-checkpoint-test.py
  ├─ Find latest ZIP in output/shared/checkpoints/
  ├─ Extract to temp directory
  ├─ Load manifest.json
  ├─ Validate file count matches
  ├─ Check optional paths (if missing, warn but pass)
  ├─ Cleanup temp directory
  └─ Exit 0 (PASS) or exit 1 (FAIL)
     ↓
(Dry-run complete; actual restore never happens)
```

### Health Flow

```
(scheduled every 4h or manual)
     ↓
npm run ops:health-report
     ↓
health-report.ps1
  ├─ Read config (.ops-config.json)
  ├─ For each endpoint:
  │  ├─ WebRequest with timeout
  │  ├─ Record response time + status
  │  └─ Report as "ok" or "error"
  ├─ Check latest backup
  │  ├─ Get ZIP timestamp
  │  ├─ Compare to "now"
  │  └─ Report freshness vs threshold (24h default)
  ├─ Aggregate: overall = "ok" if all checks pass, else "warn"
  └─ Write JSON to output/results/ops-health-latest.json
     ↓
Example output:
{
  "timestamp": "2026-03-31T20:15:30Z",
  "overall": "ok",
  "endpoints": [
    { "name": "api", "status": "ok", "responseTime": 45 }
  ],
  "backup": {
    "lastBackupTime": "2026-03-31T02:00:00Z",
    "freshness": "27 hours ago",
    "status": "warn" (over 24h threshold)
  }
}
```

---

## Error Handling

Each script has defensive checks:

| Check | Why | Action |
|-------|-----|--------|
| Config file missing | Typo in path | Throw error + debug path |
| Include path doesn't exist | Config wrong | Warn but continue (non-fatal) |
| Disk space <1 GB | Safety | Abort backup, don't create corrupted ZIP |
| WebRequest timeout | Endpoint slow/dead | Report "error", don't block health script |
| ZIP corrupted | Disk corruption | Exit 1, alert admin |

---

## Deployment Patterns

### Single-Project Setup

```
/my-project/
├── package.json                    (add ops scripts)
├── config/.ops-config.json         (customize)
└── scripts/                         (copy all)
```

One-time: `npm run ops:setup-register` (Windows) or `cron install` (Linux)

Then: Automated backups run on schedule.

### Multi-Project Reuse

```
/projects/
├── ops-automation-system/          (this repo)
├── project-a/
│   └── config/.ops-config.json     (customized for A)
└── project-b/
    └── config/.ops-config.json     (customized for B)
```

Copy scripts once, customize config per project.

---

## Testing Strategy

Each script tested:

1. **Standalone**: `pwsh -File scripts/backup-checkpoint.ps1` directly
2. **npm wrapper**: `npm run ops:backup` (npm context differs)
3. **Scheduled**: Registered to Task Scheduler, let it run
4. **Config tuning**: Try different thresholds, verify output changes

See [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md) for full test checklist.

---

## Known Limitations

| Limitation | Why | Workaround |
|------------|-----|-----------|
| Max ZIP size ~2GB | ZIP format limit + Windows Compress-Archive | Use 7-Zip or split backup scope |
| No encryption in ZIPs | ~design choice for speed | Add external encryption (GPG, BitLocker, etc) |
| Local backups only | Not S3/cloud | Add post-backup sync script or modify config |
| Single health report | One JSON per run, not time-series | Redirect logs to ELK/DataDog for history |

---

## Next Steps

- **Deploy**: [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md)
- **Configure**: [docs/CONFIGURATION.md](./docs/CONFIGURATION.md)
- **Troubleshoot**: [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)
