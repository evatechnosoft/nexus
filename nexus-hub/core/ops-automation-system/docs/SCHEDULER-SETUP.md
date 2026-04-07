# Scheduler Setup Guide

**Platform-specific instructions for automating ops scripts: Windows Task Scheduler vs Linux cron.**

---

## Overview: Two Paths

| Platform | Tool | Method | Automation |
|----------|------|--------|-----------|
| **Windows** | Task Scheduler | XML templates + PowerShell registry | `npm run ops:setup-register` |
| **Linux/Mac** | cron | Bash wrapper + crontab entries | `bash scripts/scheduler/ops-scheduler-cron.sh install` |

---

## Windows Task Scheduler Setup

### Automated Setup (Recommended)

```bash
npm run ops:setup-register
```

This command:
1. Reads `.ops-config.json` for schedule times
2. Generates 3 Task Scheduler XML files
3. Registers all tasks using `schtasks.exe /create`
4. Verifies registration
5. Shows next scheduled runs

**Requirements**:
- PowerShell 7.x or later (or 5.1 with .NET Framework)
- Admin privileges (required to register tasks)
- `schtasks.exe` available (Windows built-in)

---

### Manual Setup (Troubleshooting)

If `npm run ops:setup-register` fails:

#### Step 1: Check Prerequisites

```powershell
# Verify you're running as admin
[Security.Principal.WindowsIdentity]::GetCurrent().Groups.Where({ $_.ISWellKnownSid -eq $true }) | Where-Object { $_.Value -eq 'S-1-5-32-544' }
# If empty = NOT admin. Right-click PowerShell → "Run as administrator"

# Verify schtasks.exe exists
Get-Command schtasks.exe
```

#### Step 2: Register Each Task Manually

```powershell
# 1. Daily Backup (02:00)
$xml = Get-Content "scripts/scheduler/ops-backup-daily.xml" -Raw
$xml | Out-File -Encoding ASCII "ops-backup-daily.xml"
schtasks.exe /create /tn "ops\backup-daily" /xml "ops-backup-daily.xml" /f

# 2. Weekly Restore Test (Saturday 03:00)
$xml = Get-Content "scripts/scheduler/ops-restore-test-weekly.xml" -Raw
$xml | Out-File -Encoding ASCII "ops-restore-test-weekly.xml"
schtasks.exe /create /tn "ops\restore-test-weekly" /xml "ops-restore-test-weekly.xml" /f

# 3. Periodic Health Report (every 4 hours @ 06:00+)
$xml = Get-Content "scripts/scheduler/ops-health-report-periodic.xml" -Raw
$xml | Out-File -Encoding ASCII "ops-health-report-periodic.xml"
schtasks.exe /create /tn "ops\health-report-periodic" /xml "ops-health-report-periodic.xml" /f
```

#### Step 3: Verify Registration

```powershell
schtasks.exe /query /tn "ops\*" /v
```

Expected output: 3 tasks listed with status "Ready" (or "Enabled").

---

### Task Details

#### Task 1: Daily Backup

```
Task Name:    ops\backup-daily
Trigger:      Daily @ 02:00 UTC
Action:       npm run ops:backup
Repeat:       Every day
Retention:    Keep running until stopped
```

**Executed Command**:
```powershell
npm run ops:backup
```

**Output**:
- Checkpoint ZIP created in `output/shared/checkpoints/`
- Manifest JSON with file list + sizes
- Event logged to Task Scheduler history

**If it fails**:
- Check `npm run ops:backup` manually first
- Check C:\projects\apiflow-monitor-mvp\output\shared\checkpoints\ for ZIP files
- Check Project\folder has write permissions

---

#### Task 2: Weekly Restore Test

```
Task Name:    ops\restore-test-weekly
Trigger:      Weekly Saturday @ 03:00 UTC
Action:       npm run ops:restore-test
Repeat:       Every Saturday
```

**Executed Command**:
```python
python scripts/restore-checkpoint-test.py
```

**Output**:
- Dry-run validation (extract to temp, check manifest, delete)
- Report in `output/results/restore-test-latest.json`
- Status: "PASS" or "FAIL"

**If it fails**:
- Manual test: `npm run ops:restore-test`
- Check `output/shared/checkpoints/` has ZIP files
- Check Python path: `python --version` should return 3.7+

---

#### Task 3: Periodic Health Report

```
Task Name:    ops\health-report-periodic
Trigger:      Every 4 hours @ 06:00, 10:00, 14:00, 18:00, 22:00 UTC
Action:       npm run ops:health-report
Repeat:       5 times per day
```

**Executed Command**:
```powershell
npm run ops:health-report
```

**Output**:
- JSON report: Endpoint status + backup freshness
- Saved to `output/results/ops-health-latest.json`
- Timestamped copy: `ops-health-YYYYMMDD-HHMMSS.json`

**If it fails**:
- Manual test: `npm run ops:health-report`
- Check endpoints in `.ops-config.json` are reachable (curl/Invoke-WebRequest)

---

### Monitoring Task Status

#### View Task History

```powershell
# All ops tasks
Get-ScheduledTask -TaskPath "\ops\*" | Select TaskName, State, LastTaskResult

# Specific task
Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily" | Get-ScheduledTaskInfo

# Event log (Task Scheduler events)
Get-EventLog -LogName "System" -Source "TaskScheduler" -Newest 20
```

#### Check Last Run Result

```powershell
$task = Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily"
$info = $task | Get-ScheduledTaskInfo
Write-Host "Last Run: $($info.LastRunTime)"
Write-Host "Last Result: $($info.LastTaskResult)"
# 0 = Success, 1 = Error, others = specific codes
```

#### Disable / Re-enable Task

```powershell
# Disable (don't delete)
Disable-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily"

# Re-enable
Enable-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily"
```

#### Delete All ops Tasks

```powershell
Get-ScheduledTask -TaskPath "\ops\*" | Unregister-ScheduledTask -Confirm:$false
# Or use:
npm run ops:setup-unregister
```

---

### Troubleshooting Windows Tasks

#### Issue: "Access Denied" During Registration

**Cause**: Not running as administrator.  
**Fix**: Right-click PowerShell → "Run as Administrator"

```powershell
# Verify admin:
[Security.Principal.WindowsIdentity]::GetCurrent().Groups -match 'S-1-5-32-544'
# Returns SID if admin
```

#### Issue: Task Registered But Never Runs

**Cause**: Trigger disabled, or scheduled condition not met.  
**Fix**: Check task properties UI or via PowerShell

```powershell
$task = Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily"
$task.Triggers | Select-Object -Property StartBoundary, Enabled, Schedule
# Should show: StartBoundary e.g. "2024-01-15T02:00:00" and Enabled = True
```

#### Issue: Task Runs But Command Fails

**Cause**: npm run context different (working dir, PATH env).  
**Fix**: Check task action details and ensure full path

```powershell
$task = Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily"
$action = $task.Actions[0]
Write-Host "Executable: $($action.Execute)"
Write-Host "Arguments: $($action.Arguments)"
Write-Host "Working Dir: $($action.WorkingDirectory)"
```

Expected:
```
Executable: C:\Program Files\nodejs\npm.cmd
Arguments: run ops:backup
Working Dir: C:\projects\apiflow-monitor-mvp
```

If working directory is wrong, re-register task with correct path.

---

## Linux/Mac Cron Setup

### Automated Setup

```bash
cd /path/to/ops-automation-system
bash scripts/scheduler/ops-scheduler-cron.sh install
```

This script:
1. Reads `.ops-config.json` for schedule times
2. Generates 3 cron entries
3. Adds to user's crontab
4. Verifies installation
5. Shows next scheduled runs

**Requirements**:
- Bash shell
- `cron` daemon running (`sudo service cron status`)
- `crontab` command available
- User permissions to edit crontab

---

### Manual Setup (Troubleshooting)

#### Step 1: Check cron Status

```bash
# Linux
sudo service cron status

# Mac
sudo launchctl list | grep cron

# Or check if cron is running
ps aux | grep cron
```

If cron not running:
```bash
# Linux
sudo service cron start

# Mac (cron was replaced by launchd, but cron still works)
sudo defaults write /System/Library/LaunchDaemons/com.vix.cron.plist Disabled -bool false
sudo launchctl load /System/Library/LaunchDaemons/com.vix.cron.plist
```

#### Step 2: Create Manual cron Entries

```bash
# Edit your crontab
crontab -e

# Add entries (replace /path/to with actual path):
```

Insert these lines (using your actual project path):

```bash
# Daily backup @ 02:00 UTC
0 2 * * * cd /path/to/ops-automation-system && npm run ops:backup >> output/results/cron-backup.log 2>&1

# Weekly restore test @ 03:00 UTC Saturday
0 3 * * 6 cd /path/to/ops-automation-system && npm run ops:restore-test >> output/results/cron-restore.log 2>&1

# Periodic health report @ 06:00, 10:00, 14:00, 18:00, 22:00 UTC
0 6,10,14,18,22 * * * cd /path/to/ops-automation-system && npm run ops:health-report >> output/results/cron-health.log 2>&1
```

**Save and exit**:
- Nano: `Ctrl+X` → `Y` → `Enter`
- Vim: `:wq` → `Enter`

#### Step 3: Verify Installation

```bash
# View your crontab
crontab -l

# Should output 3 entries starting with "0 2 *...", "0 3 *...", "0 6,10..."
```

---

### Cron Expressions Explained

**Format**: `minute hour day-of-month month day-of-week command`

#### Daily Backup @ 02:00

```
0 2 * * * npm run ops:backup
│ │ │ │ │
0 = minute 0 (top of hour, 'O'clock)
  2 = hour 2 (02:00 in 24-hour format)
    * = any day of month
      * = any month
        * = any day of week
```

**Result**: Every day at 02:00

#### Weekly Restore @ Saturday 03:00

```
0 3 * * 6 npm run ops:restore-test
│ │ │ │ │
0 = minute 0
  3 = hour 3 (03:00 UTC)
    * = any day of month
      * = any month
        6 = Saturday (0=Sunday, 1=Monday, ..., 6=Saturday)
```

**Result**: Every Saturday at 03:00

#### Every 4 Hours @ 06:00, 10:00, 14:00, 18:00, 22:00

```
0 6,10,14,18,22 * * * npm run ops:health-report
│ │            │ │ │
0 = minute 0
  6,10,14,18,22 = hours 6, 10, 14, 18, 22 (separated by comma)
               * = any day of month
                 * = any month
                   * = any day of week
```

**Result**: Every day at 06:00, 10:00, 14:00, 18:00, 22:00 UTC

---

### Monitoring cron Execution

#### View cron Logs

```bash
# Linux
grep CRON /var/log/syslog | tail -20

# Mac
log show --predicate 'process == "cron"' --last 1h

# Or check output files (if you added logging)
tail output/results/cron-backup.log
tail output/results/cron-restore.log
tail output/results/cron-health.log
```

#### Check Next Scheduled Runs (Estimated)

```bash
# Install croniter (Python, optional but helpful)
pip install croniter

# Python script to show next 5 runs:
python3 -c "
from croniter import croniter
from datetime import datetime

schedule = '0 2 * * *'  # daily backup
cron = croniter(schedule, datetime.now())
for i in range(5):
    print(cron.get_next(datetime))
"
```

#### Disable/Re-enable cron Entry

```bash
# Edit crontab and comment out (add # to start of line)
crontab -e

# Example: Disable backup
# 0 2 * * * cd /path/to && npm run ops:backup

# To re-enable, remove the # and save
```

---

### Troubleshooting cron (Linux/Mac)

#### Issue: cron Job Never Executes

**Possible Causes**:
1. cron daemon not running
2. Cron syntax error
3. Working directory doesn't exist
4. npm/node not in PATH

**Fixes**:

```bash
# 1. Check cron daemon
sudo service cron status

# 2. Validate cron syntax (use online tool or croniter)
# 3. Test command manually
cd /path/to/ops-automation-system && npm run ops:backup

# 4. Check npm path in cron context
which npm
# If npm not found in cron, use full path:
/usr/bin/npm run ops:backup
# or:
/usr/local/bin/npm run ops:backup
```

#### Issue: cron Job Fails but Manual Test Works

**Cause**: Different environment in cron context (PATH, HOME, NODE_ENV).  
**Fix**: Add env vars to crontab

```bash
# Edit crontab
crontab -e

# Add at top:
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
HOME=/home/your-user
NODE_ENV=production

# Then add your entries
0 2 * * * cd /path/to && npm run ops:backup
```

#### Issue: Permission Denied When Running cron Job

**Cause**: cron runs as your user; output directory might not have write permissions.  
**Fix**: Check directory permissions

```bash
# Verify output/ is writable
ls -ld output/
# Should show: drwxrwxr-x or similar (user has write 'w')

# If not, fix permissions
chmod -R u+w output/

# Or run as specific user (advanced)
sudo crontab -e  # as root, if needed
```

---

## Comparing Windows vs Linux Scheduling

| Feature | Windows Task Scheduler | Linux cron |
|---------|------------------------|-----------|
| **GUI** | Yes (eventvwr.msc) | No (crontab -e) |
| **Timezone Support** | Native (timezone field) | Server timezone only |
| **Run Conditions** | CPU/network conditions | Simple time only |
| **Retry Logic** | Yes (built-in) | No, must script |
| **Event Notifications** | Email/webhook (advanced) | None built-in |
| **Historical Data** | Event log (searchable) | Syslog entries |
| **Ease of Setup** | GUI or PowerShell | Text editor (crontab) |

**Recommendation**:
- **Windows**: Use GUI (taskscheduler.msc) for troubleshooting
- **Linux/Mac**: Use `crontab -e` editor

---

## Timezone Considerations

### Windows

Windows Task Scheduler XML specifies timezone explicitly:

```xml
<StartBoundary>2024-01-15T02:00:00</StartBoundary>
<Timezone>UTC</Timezone>
```

**If timezone mismatch**:
- Task may run at different actual time than expected
- Verify system time: `Get-Date`
- Verify Task Scheduler XML: `Get-ScheduledTask -TaskPath "\ops\" -TaskName "backup-daily" | fl *`

### Linux/Mac

cron uses server's system timezone (no override possible):

```bash
# Check system timezone
timedatectl          # Linux
date +%Z             # Mac/Linux

# To use UTC consistently, set system time:
sudo timedatectl set-timezone UTC
```

**Best practice**: Always configure backups in UTC (00:00-23:59 UTC) for clarity.

---

## Migration: Windows ↔ Linux

If moving project from Windows to Linux (or vice versa):

### Windows → Linux

1. **Export Windows Task Scheduler times**:
   ```powershell
   Get-ScheduledTask -TaskPath "\ops\*" | Select TaskName, @{
     Name="NextRunTime"; Expression={ ($_ | Get-ScheduledTaskInfo).NextRunTime }
   }
   ```

2. **Delete Windows tasks**:
   ```powershell
   npm run ops:setup-unregister
   ```

3. **Set up cron on Linux**:
   ```bash
   bash scripts/scheduler/ops-scheduler-cron.sh install
   ```

### Linux → Windows

1. **Export cron times**:
   ```bash
   crontab -l > cron-backup.txt
   ```

2. **Remove cron entries**:
   ```bash
   bash scripts/scheduler/ops-scheduler-cron.sh uninstall
   ```

3. **Set up Task Scheduler on Windows**:
   ```powershell
   npm run ops:setup-register
   ```

---

## Advanced: Custom Schedules

### Windows: Modify XML Directly

Edit `scripts/scheduler/ops-backup-daily.xml`:

```xml
<!-- Current -->
<StartBoundary>2024-01-15T02:00:00</StartBoundary>
<Timezone>UTC</Timezone>

<!-- To change to 14:30 UTC -->
<StartBoundary>2024-01-15T14:30:00</StartBoundary>
<Timezone>UTC</Timezone>
```

Then re-register:
```powershell
schtasks.exe /delete /tn "ops\backup-daily" /f
schtasks.exe /create /tn "ops\backup-daily" /xml "scripts/scheduler/ops-backup-daily.xml" /f
```

### Linux: crontab Custom Entry

Add arbitrary schedule to crontab:

```bash
crontab -e

# Edit schedule (e.g., every 30 minutes instead of daily)
*/30 * * * * cd /path/to && npm run ops:backup
```

---

**Need help?** See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) or [CONFIGURATION.md](./CONFIGURATION.md).
