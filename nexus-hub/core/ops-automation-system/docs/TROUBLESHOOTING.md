# Troubleshooting Guide

**Solutions for common ops-automation-system problems.**

---

## General Troubleshooting Flow

1. **Manual Test First**: Always run the command manually before blaming scheduler
   ```bash
   npm run ops:backup
   npm run ops:restore-test
   npm run ops:health-report
   npm run ops:setup-list
   ```

2. **Check Configuration**: Verify `.ops-config.json` syntax and paths
   ```bash
   # Windows PowerShell
   Get-Content config/.ops-config.json | ConvertFrom-Json | Out-Host

   # Linux/Mac
   jq . config/.ops-config.json
   ```

3. **Check Logs**: See what the script actually reported
   ```bash
   cat output/results/restore-test-latest.json       # Restore status
   cat output/results/ops-health-latest.json         # Health status
   dir output/shared/checkpoints/                    # Backup ZIPs
   ```

4. **Check Permissions**: Verify write access to output/
   ```powershell
   # Windows
   Get-Acl output/ | Select-Object -ExpandProperty Access

   # Linux/Mac
   ls -ld output/
   ```

---

## Problem: "Config file not found"

### Symptom

```
ERROR: Config file not found: C:\projects\config\.ops-config.json
```

### Root Cause

ops-setup.ps1 (or other scripts) can't find `.ops-config.json` because script is invoked from different working directory.

### Solution

#### Option 1: Check File Actually Exists

```powershell
# Windows
Test-Path config/.ops-config.json
Test-Path .\config\.ops-config.json
Test-Path "C:\projects\apiflow-monitor-mvp\config\.ops-config.json"

# If all return $false, file missing — copy from template:
Copy-Item config/.ops-config-template.json config/.ops-config.json
```

#### Option 2: Update Config Path in ops-setup.ps1

If file exists but script can't find it, edit the path calculation:

**File**: `scripts/ops-setup.ps1`

```powershell
# Current code (around line 5):
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path $scriptPath -Parent
$projectDir = Split-Path $scriptDir -Parent
$configPath = Join-Path $projectDir "config" ".ops-config.json"

# If still not found, add debug:
Write-Host "Config search paths:"
Write-Host "  $projectDir\config\.ops-config.json exists: $(Test-Path "$projectDir\config\.ops-config.json")"
Write-Host "  $(Get-Location)\config\.ops-config.json exists: $(Test-Path "$(Get-Location)\config\.ops-config.json")"

# Or use explicit path:
$configPath = "C:\projects\apiflow-monitor-mvp\config\.ops-config.json"
```

#### Option 3: Create Symlink

If you keep config in different location, create shortcut:

```powershell
# Windows (requires admin)
New-Item -ItemType SymbolicLink -Path "config/.ops-config.json" -Target "C:\actual\location\.ops-config.json" -Force

# Linux/Mac
ln -sf /actual/location/.ops-config.json config/.ops-config.json
```

---

## Problem: "npm run ops:backup" Hangs or Times Out

### Symptom

```
npm run ops:backup
# ... no output for 5+ minutes, then:
Error: Command timed out
```

### Root Cause

1. Large directory being backed up (10GB+) → compression slow
2. Slow disk (HDD, network mount)
3. ZIP library deadlock (rare)
4. High CPU/disk I/O by other processes

### Solution

#### Option 1: Reduce includePaths

Edit `.ops-config.json`:

```json
"backup": {
  "includePaths": ["src/", "config/"],
  "excludePaths": ["node_modules/", ".git/", "dist/"]
}
```

Backup only essential folders, not entire repo.

#### Option 2: Lower Compression Level

```json
"backup": {
  "compressionLevel": 3
}
```

Lower values (0-3) compress faster but larger ZIP files.

#### Option 3: Increase Timeout (package.json)

Edit `package.json`:

```json
"scripts": {
  "ops:backup": "timeout 300 powershell -File scripts/backup-checkpoint.ps1"
}
```

increases timeout from 120s to 300s (5 minutes).

#### Option 4: Check System Load

```powershell
# Windows
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5

# Linux/Mac
top -n 1 | head -10
```

If CPU/disk busy, wait or close competing processes.

#### Option 5: Manual Backup Test

```powershell
# Direct test without npm wrapper
powershell -File scripts/backup-checkpoint.ps1 -Verbose

# If hangs, PowerShell issue (rare). Try:
powershell -Version 5.1 -File scripts/backup-checkpoint.ps1
```

---

## Problem: Backup Creates ZIP But It's Corrupted

### Symptom

```
npm run ops:backup            # Succeeds
npm run ops:restore-test      # Fails
# Error: "ZIP file is invalid" or "Manifest missing"
```

### Root Cause

1. Backup interrupted (disk full, power loss, killed process)
2. ZIP library bug (rare)
3. File locked while copying (e.g., open DB file)

### Solution

#### Option 1: Delete Corrupted ZIP, Retry

```powershell
# Windows
rm output/shared/checkpoints/* -Force -Confirm:$false

# Linux/Mac
rm output/shared/checkpoints/*

# Then retry backup
npm run ops:backup
```

#### Option 2: Exclude Locked Files

Edit `.ops-config.json`:

```json
"backup": {
  "excludePaths": ["*.ldb", "*.lock", ".sqlite-journal"]
}
```

Some processes (databases, VS Code) lock files. Exclude during backup.

#### Option 3: Use Try-Catch in Backup Script

Edit `scripts/backup-checkpoint.ps1`:

Around line 80 (after Compress-Archive):

```powershell
try {
    Compress-Archive -Path $filesToArchive -DestinationPath $zipPath -CompressionLevel $level -ErrorAction Stop
} catch {
    Write-Error "Backup failed: $_"
    # Cleanup partial ZIP
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    exit 1
}
```

---

## Problem: Health Report Always Shows "error" for Endpoint

### Symptom

```json
{
  "endpoints": [
    {
      "name": "api",
      "url": "http://localhost:3000/health",
      "status": "error"
    }
  ]
}
```

But endpoint is running fine (can access in browser).

### Root Cause

1. Endpoint URL wrong (typo, wrong port)
2. Endpoint requires authentication
3. Firewall blocking request from task scheduler context
4. Timeout too short

### Solution

#### Option 1: Verify Endpoint URL

Test manually:

```powershell
# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:3000/health" -TimeoutSec 5

# Linux/Mac curl
curl -i http://localhost:3000/health
```

If fails, URL is wrong. Check:
- Hostname: localhost vs 127.0.0.1 vs external IP
- Port: 3000 vs 3001 vs other
- Path: /health vs /api/health vs /status

#### Option 2: Increase Timeout

Edit `.ops-config.json`:

```json
"health": {
  "endpointTimeoutSeconds": 15
}
```

Increase if endpoint responds slowly.

#### Option 3: Use IP Instead of Hostname

Change `.ops-config.json`:

```json
"endpoints": [
  {
    "name": "api",
    "url": "http://127.0.0.1:3000/health"
  }
]
```

Sometimes `localhost` resolves unexpectedly in Task Scheduler context.

#### Option 4: Check Firewall

```powershell
# Windows Firewall
Get-NetFirewallRule -DisplayName "*3000*" | Select-Object DisplayName, Enabled

# Or allow Node.js through firewall
New-NetFirewallRule -DisplayName "Node.js Dev" -Direction Inbound -Program "C:\Program Files\nodejs\node.exe" -Action Allow
```

#### Option 5: Add Auth Headers (Advanced)

Edit `scripts/health-report.ps1`:

Around line 50 (modify probe logic):

```powershell
$headers = @{
    "Authorization" = "Bearer YOUR_TOKEN"
}

Invoke-WebRequest -Uri $endpoint.url -Headers $headers -TimeoutSec $timeoutSeconds -ErrorAction SilentlyContinue
```

---

## Problem: Task Scheduler or cron Job Doesn't Run

### Symptom

Task shows "Enabled" but never executes, or task runs but output is empty.

### Root Cause (Windows Task Scheduler)

1. Task disabled (manually turned off)
2. Wrong trigger time (e.g., 02:00 but system in different timezone)
3. Working directory doesn't exist
4. npm not in PATH for Task Scheduler context

### Root Cause (Linux cron)

1. cron daemon not running
2. Syntax error in crontab entry
3. User permissions missing
4. npm/node not in PATH for cron context

### Solution (Windows)

#### Step 1: Check Task Is Enabled

```powershell
Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily" | Select-Object State, Enabled
# Output should show: State = Ready, Enabled = True
```

If disabled:
```powershell
Enable-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily"
```

#### Step 2: Verify Trigger

```powershell
$task = Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily"
$task.Triggers | Select-Object StartBoundary, Enabled, NextRunTime
```

Expected: `StartBoundary = 2024-01-15T02:00:00`, `Enabled = true`

If wrong time, re-register task or edit XML and re-import.

#### Step 3: Test Task Manually

```powershell
# Run task immediately (don't wait for scheduled time)
Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily" | Start-ScheduledTask

# Wait a few seconds, check result
Start-Sleep -Seconds 3
Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily" | Get-ScheduledTaskInfo | Select-Object LastTaskResult, LastRunTime
```

If LastTaskResult = 0, task works. If other code, see Windows Task Scheduler error codes.

#### Step 4: Check Working Directory

```powershell
$task = Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily"
$action = $task.Actions[0]
Write-Host "Working Dir: $($action.WorkingDirectory)"
Write-Host "Executable: $($action.Execute)"
Write-Host "Arguments: $($action.Arguments)"
```

If working directory empty or wrong:

```powershell
# Delete and re-register with correct path
Unregister-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily" -Confirm:$false
npm run ops:setup-register
```

### Solution (Linux cron)

#### Step 1: Check cron Daemon

```bash
sudo service cron status

# If not running:
sudo service cron start
```

#### Step 2: Verify crontab Syntax

```bash
crontab -l
```

Each line should be: `minute hour day month dow command`

**Common errors**:
- Extra spaces: `0  2  *  *  *` (OK) vs `0 2 * * *` (OK)
- Dayofweek as letter: `* * * * MON` (SyntaxError) use `1` instead
- Missing command: `0 2 * * *` (no command)

#### Step 3: Test Command Manually

```bash
# Run the exact command from crontab
cd /path/to/ops-automation-system && npm run ops:backup

# If it works manually but not in cron, it's a PATH/ENV issue
```

#### Step 4: Add Full Paths to crontab

Edit crontab:

```bash
crontab -e
```

Change:
```bash
0 2 * * * cd /path/to && npm run ops:backup
```

To:
```bash
0 2 * * * /usr/bin/bash -c "cd /path/to && /usr/local/bin/npm run ops:backup"
```

Or add PATH at top of crontab:

```bash
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
SHELL=/bin/bash

0 2 * * * cd /path/to && npm run ops:backup
```

#### Step 5: Check cron Logs

```bash
# Linux
sudo grep CRON /var/log/syslog | tail -20

# Mac
log show --predicate 'process == "cron"' --last 1h

# Or check if output files exist
ls -la output/results/cron-*.log
```

---

## Problem: Python "ModuleNotFoundError" in restore-checkpoint-test.py

### Symptom

```
Error: ModuleNotFoundError: No module named 'zipfile'  (or 'json', 'pathlib')
```

### Root Cause

1. Python not installed
2. Wrong Python version (2.x instead of 3.x)
3. Task Scheduler / cron using wrong Python

### Solution

#### Option 1: Check Python Installation

```powershell
# Windows
python --version
python -c "import zipfile; import json; print('OK')"

# Linux/Mac
python3 --version
python3 -c "import zipfile; import json; print('OK')"
```

If error, install Python 3.7+:
- Windows: https://www.python.org/downloads/
- Linux: `sudo apt-get install python3`
- Mac: `brew install python3`

#### Option 2: Use Python 3 Explicitly

Edit `package.json`:

```json
"scripts": {
  "ops:restore-test": "python3 scripts/restore-checkpoint-test.py"
}
```

or

```json
"scripts": {
  "ops:restore-test": "C:\\Python312\\python.exe scripts/restore-checkpoint-test.py"
}
```

#### Option 3: Check Task Scheduler PATH

```powershell
# Windows
$task = Get-ScheduledTask -TaskPath "\ops\" -TaskName "restore-test-weekly"
$task.Actions[0] | Select-Object Execute, Arguments
```

If it shows python but not python3, update to full path:

```powershell
Unregister-ScheduledTask -TaskPath "\ops\" -TaskName "restore-test-weekly" -Confirm:$false
# Edit scripts/scheduler/ops-restore-test-weekly.xml to use C:\Python312\python.exe
npm run ops:setup-register
```

---

## Problem: Disk Space Running Out (Too Many Checkpoints)

### Symptom

```
Error: Not enough space on disk. CheckPoint creation failed.
```

Or checkpoints directory grows to 100GB+.

### Root Cause

`maxCheckpoints` set too high, or old checkpoints not being deleted.

### Solution

#### Option 1: Set Reasonable maxCheckpoints

Edit `.ops-config.json`:

```json
"backup": {
  "maxCheckpoints": 7,
  "compressionLevel": 9
}
```

Values:
- 3 = 3 backups (3 days if daily, 3 weeks if weekly)
- 7 = 1 week of daily backups
- 30 = 1 month

#### Option 2: Manual Cleanup

```powershell
# Windows — List checkpoints by size
Get-ChildItem output/shared/checkpoints/ -File | Sort-Object Length -Descending | Select-Object Name, @{Name="SizeMB"; Expression={[math]::Round($_.Length/1MB, 2)}}

# Delete oldest files
Get-ChildItem output/shared/checkpoints/ -File | Sort-Object CreationTime | Select-Object -First 5 | Remove-Item -Force
```

Or:

```bash
# Linux/Mac — List and delete
ls -lhS output/shared/checkpoints/ | head -10
rm -f $(ls -t output/shared/checkpoints/ | tail -n +8)  # Keep 7, delete rest
```

#### Option 3: Increase Retention / Archive Old Backups

Add script to move old checkpoints to archive:

```powershell
# scripts/archive-old-checkpoints.ps1
param([int]$DaysOld = 30)

$archiveDir = "output/archive/"
$checkpointDir = "output/shared/checkpoints/"

if (-not (Test-Path $archiveDir)) {
    New-Item $archiveDir -ItemType Directory
}

Get-ChildItem $checkpointDir -File | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-$DaysOld) } | ForEach-Object {
    Move-Item $_.FullName "$archiveDir$($_.Name)" -Force
}
```

Add to package.json:

```json
"scripts": {
  "ops:archive-old": "powershell -File scripts/archive-old-checkpoints.ps1 -DaysOld 30"
}
```

Then run periodic: `npm run ops:archive-old`

---

## Problem: Health Report Backup Freshness Check Always Fails

### Symptom

```json
{
  "backup": {
    "status": "warn",
    "freshness": "FAIL",
    "latestCheckpointTime": null,
    "reason": "No checkpoints found"
  }
}
```

Even though backups were taken.

### Root Cause

1. Backup output path wrong in config
2. Backup never actually ran (scheduled task didn't execute)
3. Backup succeeded but ZIP not moved to expected location

### Solution

#### Option 1: Check Backup Output Path

Edit `.ops-config.json`:

```json
"backup": {
  "outputPath": "output/shared/checkpoints/"
}
```

Verify path exists and has ZIP files:

```powershell
# Windows
Get-ChildItem output/shared/checkpoints/ -Filter "*.zip"

# Linux/Mac
ls output/shared/checkpoints/*.zip
```

#### Option 2: Verify Backup Actually Ran

```powershell
# Windows
Get-ChildItem output/shared/checkpoints/ -File | Select-Object Name, CreationTime, Length | Sort-Object CreationTime -Descending | Select-Object -First 3

# Linux/Mac
ls -lh output/shared/checkpoints/ | head -5
```

If no recent files, backup task didn't execute. Check Task Scheduler or cron.

#### Option 3: Manually Force Backup

```bash
npm run ops:backup
npm run ops:health-report
```

Then check health report — should show recent backup.

---

## Problem: npm Commands Not Recognized

### Symptom

```
npm run ops:backup
> unknown script "ops:backup"
```

### Root Cause

1. package.json missing ops scripts
2. Running from wrong directory
3. npm not installed

### Solution

#### Step 1: Check package.json

```powershell
# Windows
Get-Content package.json | Select-String "ops:" -Context 5

# Linux/Mac
grep "ops:" package.json
```

Should see: `"ops:backup"`, `"ops:restore-test"`, etc.

#### Step 2: Check Working Directory

```powershell
# Windows
Get-Location    # Should be C:\projects\apiflow-monitor-mvp

# Linux/Mac
pwd             # Should be /path/to/project
```

If wrong:
```powershell
cd C:\projects\apiflow-monitor-mvp
npm run ops:backup
```

#### Step 3: Update package.json

If scripts missing, copy from standalone project:

```
ops-automation-system\package.json → your-project\package.json
```

Merge scripts section:

```json
"scripts": {
  "ops:backup": "powershell -File scripts/backup-checkpoint.ps1",
  "ops:restore-test": "python scripts/restore-checkpoint-test.py",
  "ops:health-report": "powershell -File scripts/health-report.ps1",
  "ops:setup-register": "powershell -File scripts/ops-setup.ps1 -RegisterTasks",
  "ops:setup-unregister": "powershell -File scripts/ops-setup.ps1 -UnregisterTasks",
  "ops:setup-list": "powershell -File scripts/ops-setup.ps1 -ListTasks",
  "ops:setup-help": "powershell -File scripts/ops-setup.ps1 -Help"
}
```

---

## Need More Help?

See:
- [CONFIGURATION.md](./CONFIGURATION.md) — All config options explained
- [SCHEDULER-SETUP.md](./SCHEDULER-SETUP.md) — Windows Task Scheduler / Linux cron setup
- [DEPLOYMENT-GUIDE.md](../DEPLOYMENT-GUIDE.md) — Step-by-step deployment

Or check specific op files:
- `scripts/backup-checkpoint.ps1` — Backup logic
- `scripts/restore-checkpoint-test.py` — Restore validation
- `scripts/health-report.ps1` — Health probing
- `scripts/ops-setup.ps1` — Task registration

