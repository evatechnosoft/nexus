"""
nexus-dream.py — Nightly autodream analyzer (03:00) + daytime --light mode
Scans Nexus memory index, detects patterns, generates promotion suggestions.

Usage:
  python nexus-dream.py           # Full scan (nightly 03:00)
  python nexus-dream.py --light   # Last 4 hours only (daytime 08/12/16/20:00)

Checks recurring keys, topic clusters, workflow sequences.
Run via Windows Task Scheduler — no Claude Code required.
"""
import argparse, json, sys, time, re, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter

# ── args ──────────────────────────────────────────────────────────────────────

_parser = argparse.ArgumentParser(description="Nexus autodream analyzer")
_parser.add_argument("--light", action="store_true",
                     help="Light mode: only analyze entries modified in last 4h")
_args = _parser.parse_args()
LIGHT_MODE = _args.light

# ── config ────────────────────────────────────────────────────────────────────

NEXUS_URL    = "http://192.168.1.186:8900"
GH_OWNER     = "evatechnosoft"
GH_REPO      = "nexus"
GH_BRANCH    = "prod"
LOG_DIR      = Path.home() / ".claude" / "logs"
LIGHT_HOURS  = 4   # how far back --light mode looks
LOG_DIR.mkdir(exist_ok=True)

# Minimum occurrences of a prefix cluster to suggest promotion
RULE_THRESHOLD  = 3
SKILL_THRESHOLD = 3

# Topic cluster keywords → cluster label
TOPIC_MAP: dict[str, str] = {
    "error":      "error_fixes",
    "fix":        "error_fixes",
    "bug":        "error_fixes",
    "deploy":     "deployments",
    "release":    "deployments",
    "docker":     "deployments",
    "decision":   "decisions",
    "decided":    "decisions",
    "choice":     "decisions",
    "infra":      "infrastructure",
    "server":     "infrastructure",
    "port":       "infrastructure",
    "ssh":        "infrastructure",
    "workflow":   "workflows",
    "pipeline":   "workflows",
    "ci":         "workflows",
    "reconcile":  "automation",
    "dream":      "automation",
    "sync":       "automation",
    "skill":      "skills",
    "rule":       "skills",
    "memory":     "knowledge",
    "guide":      "knowledge",
}


# ── helpers ───────────────────────────────────────────────────────────────────

def nexus_alive() -> bool:
    try:
        with urllib.request.urlopen(f"{NEXUS_URL}/health", timeout=4) as r:
            return r.status == 200
    except Exception:
        return False


def nexus_get(path: str) -> dict | list | None:
    try:
        with urllib.request.urlopen(f"{NEXUS_URL}{path}", timeout=8) as r:
            return json.loads(r.read())
    except Exception:
        return None


def nexus_put(key: str, content: str) -> bool:
    safe = (key.replace("/", "--").replace(".", "-")
               .replace(" ", "-").replace("_", "-"))
    try:
        body = json.dumps({"content": content}).encode()
        req  = urllib.request.Request(
            f"{NEXUS_URL}/api/memory/{safe}", data=body, method="PUT",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status < 300
    except Exception:
        return False


def nexus_post_dream(payload: dict) -> int:
    """POST structured dream metrics to /api/dream/report. Returns run number."""
    try:
        body = json.dumps(payload).encode()
        req  = urllib.request.Request(
            f"{NEXUS_URL}/api/dream/report", data=body, method="POST",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            return data.get("run", 0)
    except Exception:
        return 0


# ── memory fetching ───────────────────────────────────────────────────────────

def fetch_memory_index() -> list[dict]:
    """Fetch all memory entries from Nexus index endpoint."""
    data = nexus_get("/api/memory/index")
    if not data or not isinstance(data, dict):
        return []
    return data.get("files", [])


def fetch_memory_content(key: str) -> str:
    """Fetch content for a single memory key."""
    data = nexus_get(f"/api/memory/{key}")
    if data and isinstance(data, dict):
        return data.get("content", "")
    return ""


# ── pattern analysis ──────────────────────────────────────────────────────────

def extract_prefix(key: str) -> str:
    """Return the first segment of a hyphen-separated memory key."""
    return key.split("-")[0] if "-" in key else key


def classify_topics(keys: list[str]) -> Counter:
    """Count occurrences of each topic cluster across all keys."""
    counts: Counter = Counter()
    for key in keys:
        key_lower = key.lower()
        for keyword, cluster in TOPIC_MAP.items():
            if keyword in key_lower:
                counts[cluster] += 1
                break  # each key counted once per cluster
    return counts


def find_recurring_prefixes(keys: list[str]) -> dict[str, list[str]]:
    """Group keys by prefix, return groups with count >= RULE_THRESHOLD."""
    grouped: dict[str, list[str]] = {}
    for key in keys:
        prefix = extract_prefix(key)
        grouped.setdefault(prefix, []).append(key)
    return {p: ks for p, ks in grouped.items() if len(ks) >= RULE_THRESHOLD}


def find_workflow_sequences(keys: list[str]) -> list[tuple[str, ...]]:
    """
    Detect ordered sequences: keys that share a prefix and have numeric
    or step-like suffixes (step1, step2, 01, 02, etc.).
    Returns list of (key_a, key_b, ...) tuples.
    """
    _step_re = re.compile(r"(?:step|phase|part|s|p)?(\d+)$", re.IGNORECASE)
    sequences: list[tuple[str, ...]] = []
    grouped = find_recurring_prefixes(keys)
    for prefix, group_keys in grouped.items():
        ordered = sorted(
            [(int(m.group(1)), k) for k in group_keys
             if (m := _step_re.search(k))]
        )
        if len(ordered) >= 2:
            sequences.append(tuple(k for _, k in ordered))
    return sequences


def near_duplicate_check(keys: list[str]) -> list[tuple[str, str]]:
    """
    Simple near-duplicate heuristic: pairs of keys where one is a prefix
    substring of the other (e.g., reconcile-2024 vs reconcile-2025).
    """
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for i, ka in enumerate(keys):
        for kb in keys[i + 1:]:
            if ka in kb or kb in ka:
                combo = tuple(sorted([ka, kb]))
                if combo not in seen:
                    seen.add(combo)  # type: ignore[arg-type]
                    pairs.append((ka, kb))
    return pairs


# ── report generation ─────────────────────────────────────────────────────────

def build_report(
    today: str,
    memory_entries: list[dict],
    topic_counts: Counter,
    recurring: dict[str, list[str]],
    sequences: list[tuple[str, ...]],
    duplicates: list[tuple[str, str]],
    promotions_total: int,
) -> str:
    lines: list[str] = [
        f"# Nexus Autodream Report — {today}",
        f"Generated: {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC",
        f"Memories analyzed: {len(memory_entries)}",
        "",
        "## Topic Clusters",
    ]

    if topic_counts:
        for cluster, count in topic_counts.most_common():
            lines.append(f"- `{cluster}`: {count} entries")
    else:
        lines.append("- No notable clusters detected")

    lines += ["", "## Recurring Key Prefixes (potential rules)"]
    if recurring:
        for prefix, group_keys in sorted(recurring.items(), key=lambda x: -len(x[1])):
            lines.append(f"- `{prefix}` ({len(group_keys)} entries): {', '.join(group_keys[:5])}")
    else:
        lines.append("- None detected")

    lines += ["", "## Workflow Sequences (potential skills)"]
    if sequences:
        for seq in sequences:
            lines.append(f"- Sequence: {' → '.join(seq)}")
    else:
        lines.append("- None detected")

    lines += ["", "## Near-Duplicate Entries (consolidation candidates)"]
    if duplicates:
        for ka, kb in duplicates[:10]:  # cap at 10
            lines.append(f"- `{ka}` ↔ `{kb}`")
    else:
        lines.append("- No near-duplicates found")

    lines += ["", "## Promotion Suggestions"]
    suggestions: list[str] = []
    for prefix, group_keys in recurring.items():
        suggestions.append(
            f"- [{prefix}] {len(group_keys)} recurring entries → candidate for a **rule**"
        )
    for seq in sequences:
        suggestions.append(
            f"- [{seq[0].split('-')[0]}] step sequence detected → candidate for a **skill**"
        )
    if suggestions:
        lines.extend(suggestions)
    else:
        lines.append("- No promotions suggested this cycle")

    lines += [
        "",
        "## Autodream System",
        "Gece 3'te nexus-dream.py çalışır → dream raporu sabah SessionStart'ta yüklenir.",
        "",
        f"Total promotions suggested: {promotions_total}",
    ]

    return "\n".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────

started_at = time.time()
now_utc    = datetime.now(timezone.utc)
today      = now_utc.strftime("%Y-%m-%d")
hour_tag   = now_utc.strftime("%H")
mode_label = "light" if LIGHT_MODE else "full"
nexus_up   = nexus_alive()

log_lines: list[str] = [
    f"[dream] starting {today} mode={mode_label} — Nexus: {'online' if nexus_up else 'offline'}",
]

if not nexus_up:
    log_lines.append("[dream] Nexus offline — aborting (no failure)")
    log_name = f"dream-light-{today}-{hour_tag}.md" if LIGHT_MODE else f"dream-{today}.md"
    (LOG_DIR / log_name).write_text("\n".join(log_lines), encoding="utf-8")
    raise SystemExit(0)

# 1. fetch memory index
all_entries = fetch_memory_index()

# --light: filter to entries modified in last LIGHT_HOURS hours
if LIGHT_MODE:
    cutoff_ts = time.time() - (LIGHT_HOURS * 3600)
    # 'modified' field is ISO8601 string from Nexus — convert to epoch
    def _iso_to_ts(s: str) -> float:
        try:
            return datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp()
        except Exception:
            return 0.0
    memory_entries = [
        e for e in all_entries
        if _iso_to_ts(e.get("modified", "")) >= cutoff_ts
    ]
    log_lines.append(f"[dream] light mode: last {LIGHT_HOURS}h window")
    log_lines.append(f"[dream] total={len(all_entries)}, recent={len(memory_entries)}")
else:
    memory_entries = all_entries

keys = [e["key"] for e in memory_entries]
log_lines.append(f"[dream] memories to analyze: {len(keys)}")

# 2. pattern analysis
topic_counts  = classify_topics(keys)
recurring     = find_recurring_prefixes(keys)
sequences     = find_workflow_sequences(keys)
duplicates    = near_duplicate_check(keys)
promotions    = len(recurring) + len(sequences)

log_lines.append(f"[dream] topic clusters  : {len(topic_counts)}")
log_lines.append(f"[dream] recurring prfx  : {len(recurring)}")
log_lines.append(f"[dream] sequences       : {len(sequences)}")
log_lines.append(f"[dream] near-duplicates : {len(duplicates)}")
log_lines.append(f"[dream] promotions      : {promotions}")

# 3. build report
report = build_report(
    today, memory_entries, topic_counts, recurring, sequences, duplicates, promotions
)

# 4. save local report
if LIGHT_MODE:
    local_path = LOG_DIR / f"dream-light-{today}-{hour_tag}.md"
else:
    local_path = LOG_DIR / f"dream-{today}.md"
local_path.write_text(report, encoding="utf-8")
log_lines.append(f"[dream] saved: {local_path}")

# 5. push report to Nexus memory
dream_key = f"dream-light-{today}-{hour_tag}" if LIGHT_MODE else f"dream--{today}"
if nexus_put(dream_key, report):
    log_lines.append(f"[dream] pushed to Nexus memory: {dream_key}")
else:
    log_lines.append(f"[dream] WARN: failed to push memory key {dream_key}")

# 6. POST structured metrics to /api/dream/report
elapsed = round(time.time() - started_at, 1)
run_num = nexus_post_dream({
    "ts":                   int(time.time()),
    "patterns_detected":    len(topic_counts) + len(recurring),
    "promotions_suggested": promotions,
    "memories_analyzed":    len(memory_entries),
    "duration_s":           elapsed,
})
log_lines.append(f"[dream] metrics -> Nexus /api/dream/report: run #{run_num}")
log_lines.append(f"[dream] done in {elapsed}s")

sys.stdout.buffer.write(("\n".join(log_lines) + "\n" + report).encode("utf-8", errors="replace"))
