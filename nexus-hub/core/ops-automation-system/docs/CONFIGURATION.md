# Configuration Reference

**All tunable fields in `.ops-config.json` explained with examples.**

---

## Base Template

```json
{
  "project": {
    "name": "my-project",
    "description": "Project description"
  },
  "backup": { ... },
  "restore": { ... },
  "health": { ... },
  "reporting": { ... },
  "notifications": { ... }
}
```

---

## project

Metadata about your project.

```json
"project": {
  "name": "my-project",
  "description": "Production API backend"
}
```

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `name` | string | Required | Used in logs, reports. No spaces. |
| `description` | string | "" | For documentation only. |

---

## backup

Controls what gets backed up and when.

```json
"backup": {
  "includePaths": [".env", "src/", "config/"],
  "excludePaths": ["node_modules/", ".git/"],
  "maxCheckpoints": 7,
  "compressionLevel": 9,
  "schedule": {
    "frequency": "daily",
    "time": "02:00",
    "timezone": "UTC"
  }
}
```

### backup.includePaths

**Type**: Array of strings  
**Default**: `[]` (backs up entire repo by default)

Paths to backup. Relative to repo root. Can be:
- Files: `.env`, `secrets.json`
- Directories: `src/`, `docs/`, `src/config/`

**Examples**:
```json
"includePaths": [
  ".env",
  "src/",
  "docs/",
  "config/",
  "package.json"
]
```

**Behavior**:
- If specified, ONLY these paths are backed up
- If empty/omitted, entire repo is backed up (except `excludePaths`)

---

### backup.excludePaths

**Type**: Array of strings  
**Default**: `["node_modules/", ".git/", ".github/", "dist/", "build/"]`

Paths to NOT backup. Patterns are treated as glob-like.

**Examples**:
```json
"excludePaths": [
  "node_modules/",
  ".git/",
  ".github/",
  "dist/",
  "build/",
  ".npm-cache/",
  "__pycache__/",
  "*.log",
  ".env.local"
]
```

**Behavior**:
- Applied regardless of `includePaths`
- Superset of inclusions
- If path is both included and excluded, excluded wins

---

### backup.maxCheckpoints

**Type**: Integer  
**Default**: `7`

Maximum number of checkpoint ZIPs to keep. Oldest deleted automatically.

**Examples**:
- `3` — Keep only last 3 weeks
- `7` — Keep 1 week of daily backups (default)
- `30` — Keep 1 month
- `365` — Keep 1 year

**Behavior**:
- After creating new checkpoint, if count > maxCheckpoints, delete oldest
- Cannot delete during active backup (safe)

---

### backup.compressionLevel

**Type**: Integer (0-9)  
**Default**: `9`

ZIP compression ratio (0 = no compression, 9 = maximum).

| Level | Speed | Size | Use Case |
|-------|-------|------|----------|
| 0 | Fastest | Largest | Very large repos, network constraints |
| 5 | Balanced | Medium | Default recommendation |
| 9 | Slowest | Smallest | Small repos, bandwidth expensive |

**Behavior**:
- Higher level = slower backup but smaller ZIP
- Typical trade-off: level 9 takes 5-10% more time but saves 20-40% disk

---

### backup.schedule

**Type**: Object with `frequency`, `time`, `timezone`

When to run automated backup.

```json
"schedule": {
  "frequency": "daily",
  "time": "02:00",
  "timezone": "UTC"
}
```

| Field | Values | Examples |
|-------|--------|----------|
| `frequency` | `"daily"`, `"weekly"` | `"daily"` (every day), `"weekly"` (Saturdays) |
| `time` | HH:MM (24-hour) | `"02:00"`, `"14:30"`, `"23:59"` |
| `timezone` | IANA timezone | `"UTC"`, `"America/New_York"`, `"Europe/London"` |

**Behavior** (Windows Task Scheduler):
- Backup runs at: `time` in specified `timezone`
- If system time ≠ task scheduler time, Task Scheduler uses system time (approx)

**Behavior** (Linux/Mac cron):
- cron daemon uses server timezone (ignores `timezone` field)
- Recommend: Always use UTC for clarity

---

## restore

Controls dry-run validation behavior.

```json
"restore": {
  "dryRunByDefault": true,
  "validateManifest": true,
  "tolerateMissingPaths": true
}
```

### restore.dryRunByDefault

**Type**: Boolean  
**Default**: `true`

If `true`, restore-test.py extracts to temp, does NOT restore actual files.

| Value | Behavior |
|-------|----------|
| `true` | Extract to /tmp, validate, delete → NO disk impact |
| `false` | Not implemented yet (reserved) |

**Recommendation**: Keep `true`. Actual restore is risky; dry-run validates integrity.

---

### restore.validateManifest

**Type**: Boolean  
**Default**: `true`

Verify `manifest.json` inside checkpoint matches backup metadata.

**Behavior**:
- Checks file count, sizes, timestamps
- If mismatch, reports "FAIL" and investigation needed

**Recommendation**: Always `true`.

---

### restore.tolerateMissingPaths

**Type**: Boolean  
**Default**: `true`

If configured `includePaths` some are missing, still mark PASS (non-fatal).

**Example**:
```json
"includePaths": ["src/", "optional-data/"]
```

- If `optional-data/` doesn't exist (e.g., deleted before backup): Still PASS
- If `src/` doesn't exist: Still pass ✓ (because `tolerateMissingPaths: true`)

| Value | Behavior |
|-------|----------|
| `true` | Missing paths warn but don't fail |
| `false` | Any missing path fails dry-run |

**Recommendation**: `true` for dev/test, `false` for production.

---

## health

Endpoint monitoring and backup freshness checks.

```json
"health": {
  "enabled": true,
  "endpointTimeoutSeconds": 8,
  "backupFreshnessHours": 24,
  "endpoints": [
    {
      "name": "api",
      "url": "http://localhost:3000/health",
      "required": true
    }
  ]
}
```

### health.enabled

**Type**: Boolean  
**Default**: `true`

If `false`, health-report.ps1 exits immediately (no probes).

---

### health.endpointTimeoutSeconds

**Type**: Integer  
**Default**: `8`

How long to wait for each endpoint probe before timing out.

| Value | Use Case |
|-------|----------|
| 3 | Fast, local services only |
| 5 | Typical (local + nearby) |
| 8 | Default, allows for network jitter |
| 15 | Slow services, distant network |
| 30 | Very slow or high-latency |

**Behavior**:
- If endpoint doesn't respond in N seconds, report "timeout" / "error"
- Total time = `(timeout * endpoint count)` (sequential probes)

---

### health.backupFreshnessHours

**Type**: Integer  
**Default**: `24`

Warn if latest backup is older than N hours.

| Value | Use Case |
|-------|----------|
| 1 | Very frequent backups (e.g., every hour) |
| 6 | Multiple daily backups |
| 24 | Daily backup (default) |
| 72 | Weekly backup |
| 168 | Every 7 days |

**Behavior**:
- Latest ZIP timestamp compared to current time
- If older than threshold: health report shows `"backup": { "status": "warn" }`
- Overall report = "warn" if backup stale (even if endpoints OK)

---

### health.endpoints

**Type**: Array of endpoint objects

List of services to monitor.

```json
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
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | Yes | Identifier in report |
| `url` | string | Yes | Full URL (http://...) |
| `required` | boolean | No | If true, endpoint down = overall "warn" |

**Behavior** (URL probes):
- HTTP GET request (no body)
- Response 2xx-3xx = "ok"
- Response 4xx-5xx = "error"
- Timeout / network error = "error"

**Behavior** (`required` flag):
- If `required: true` and endpoint fails → overall report = "warn"
- If `required: false` and endpoint fails → reported but overall stays "ok" if others pass

**Good endpoint URLs**:
```json
{
  "name": "api",
  "url": "http://localhost:3000/health"
},
{
  "name": "database_tcp",
  "url": "http://localhost:5432"
},
{
  "name": "webhook",
  "url": "http://api.example.com/ping"
}
```

---

## reporting

Output configuration.

```json
"reporting": {
  "outputFormat": "json",
  "outputPath": "output/results/",
  "keepHistoryDays": 30
}
```

### reporting.outputFormat

**Type**: String  
**Values**: `"json"` (only supported)

---

### reporting.outputPath

**Type**: String  
**Default**: `"output/results/"`

Where to write health report JSON (relative to repo root).

**Behavior**:
- Directory created automatically
- Filename: `ops-health-latest.json`
- Also keeps timestamped copies if `keepHistoryDays > 0`

---

### reporting.keepHistoryDays

**Type**: Integer  
**Default**: `30`

Keep historical health reports for N days (for trend analysis).

| Value | Behavior |
|-------|----------|
| 0 | Only latest report kept |
| 7 | 1 week of daily reports |
| 30 | 1 month (default) |
| 365 | 1 year |

**Behavior**:
- Creates `ops-health-YYYYMMDD-HHMMSS.json` alongside `ops-health-latest.json`
- Older files auto-deleted after N days

---

## notifications

(Placeholder for future integration)

```json
"notifications": {
  "enabled": false,
  "onBackupFailure": false,
  "onRestoreFailed": false,
  "onHealthWarning": false,
  "webhookUrl": null
}
```

Currently not implemented. Will support:
- Slack/Teams webhook on failures
- Email alerts
- PagerDuty integration

---

## Configuration Examples

### Example 1: Minimal Setup (Local Dev)

```json
{
  "project": {
    "name": "my-app-dev"
  },
  "backup": {
    "includePaths": ["src/", ".env"],
    "maxCheckpoints": 3,
    "schedule": { "time": "02:00", "frequency": "daily" }
  },
  "restore": {
    "dryRunByDefault": true,
    "tolerateMissingPaths": true
  },
  "health": {
    "endpoints": [
      { "name": "api", "url": "http://localhost:3000/health" }
    ]
  }
}
```

### Example 2: Production Multi-Service

```json
{
  "project": {
    "name": "production-api",
    "description": "Multi-region backend"
  },
  "backup": {
    "includePaths": ["src/", "config/", "migrations/", "secrets/"],
    "excludePaths": ["node_modules/", "dist/", ".log"],
    "maxCheckpoints": 30,
    "compressionLevel": 9,
    "schedule": { "time": "00:00", "frequency": "daily", "timezone": "UTC" }
  },
  "restore": {
    "dryRunByDefault": true,
    "validateManifest": true,
    "tolerateMissingPaths": false
  },
  "health": {
    "enabled": true,
    "endpointTimeoutSeconds": 10,
    "backupFreshnessHours": 24,
    "endpoints": [
      {
        "name": "api-primary",
        "url": "http://api-1.prod.company.com/health",
        "required": true
      },
      {
        "name": "api-secondary",
        "url": "http://api-2.prod.company.com/health",
        "required": true
      },
      {
        "name": "database-master",
        "url": "http://db-1.prod.company.com:5432",
        "required": true
      },
      {
        "name": "cache-cluster",
        "url": "http://cache.prod.company.com:6379/ping",
        "required": false
      }
    ]
  },
  "reporting": {
    "outputFormat": "json",
    "outputPath": "output/results/",
    "keepHistoryDays": 90
  }
}
```

### Example 3: Hourly Light Backup

```json
{
  "project": {
    "name": "database-snapshots"
  },
  "backup": {
    "includePaths": ["data/", "config/"],
    "maxCheckpoints": 24,
    "compressionLevel": 5,
    "schedule": { "time": "00:00", "frequency": "daily" }
  },
  "health": {
    "backupFreshnessHours": 1,
    "endpoints": [
      { "name": "db", "url": "http://localhost:5432", "required": true }
    ]
  }
}
```

---

## JSON Schema

(For IDE autocomplete support)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ops-config",
  "type": "object",
  "properties": {
    "project": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "description": { "type": "string" }
      },
      "required": ["name"]
    },
    "backup": {
      "type": "object",
      "properties": {
        "includePaths": { "type": "array", "items": { "type": "string" } },
        "excludePaths": { "type": "array", "items": { "type": "string" } },
        "maxCheckpoints": { "type": "integer", "minimum": 1 },
        "compressionLevel": { "type": "integer", "minimum": 0, "maximum": 9 },
        "schedule": {
          "type": "object",
          "properties": {
            "frequency": { "enum": ["daily", "weekly"] },
            "time": { "type": "string", "pattern": "^\\d{2}:\\d{2}$" },
            "timezone": { "type": "string" }
          }
        }
      }
    }
  }
}
```

---

## Validation Checklist

Before deploying, verify:

- [ ] `project.name` has no spaces or special chars
- [ ] `backup.includePaths` all exist (test with `ls -la`)
- [ ] `backup.schedule.time` is valid HH:MM (24-hour)
- [ ] `health.endpoints` all IPs/hostnames are reachable
- [ ] `health.endpointTimeoutSeconds` ≥ 5 (avoid flakiness)
- [ ] JSON syntax valid (use `jq . < config/.ops-config.json` to validate on Linux/Mac)

---

**Need help?** See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) or [SCHEDULER-SETUP.md](./SCHEDULER-SETUP.md).
