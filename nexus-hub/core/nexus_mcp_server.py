"""
Nexus MCP Server — Model-Agnostic Skill Registry + Memory Hub
Endpoints:
  /health, /metrics — monitoring
  /api/skills/index — skill manifest
  /api/skills/{name} — skill content
  /api/skills/search?q= — search
  /api/memory/index — memory file list
  /api/memory/{key} — memory content (read/write)
  /api/capabilities — model capabilities map
  /api/vault/{key} — secret vault (LAN-only, bearer auth)
  /mcp — MCP protocol endpoint
"""

import asyncio
import hmac
import json
import os
import re
import secrets
import shutil
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

# Ensure sibling modules (nexus_fetch, nexus_embed, nexus_store) are importable
sys.path.insert(0, str(Path(__file__).parent))


# --- Helpers ---


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two vectors. Returns 0.0 on mismatch."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(x * x for x in b) ** 0.5
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0


_embedding_engine = None


def get_embedding_engine():
    """Return singleton EmbeddingEngine (lazy-load FastEmbed)."""
    global _embedding_engine
    if _embedding_engine is None:
        from nexus_embed import EmbeddingEngine

        _embedding_engine = EmbeddingEngine()
    return _embedding_engine


app = FastAPI(title="nexus", description="Model-Agnostic Skill Registry + Memory Hub")


# ============================================================================
# FETCH JOB STATE (Phase 2)
# ============================================================================


@dataclass
class FetchJobState:
    """In-memory fetch job tracking."""

    job_id: str
    status: str  # queued, running, completed, failed
    categories: list
    progress: dict = field(default_factory=dict)  # {category: count}
    skills_added: int = 0
    errors: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "categories": self.categories,
            "progress": self.progress,
            "skills_added": self.skills_added,
            "errors": self.errors,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


# In-memory job tracking
fetch_jobs: Dict[str, FetchJobState] = {}


# Configuration — override with NEXUS_DATA_DIR env var (e.g. for CI/testing)
DATA_DIR = Path(os.environ.get("NEXUS_DATA_DIR", "/app"))
SKILLS_INDEX_PATH = DATA_DIR / "data" / "skill-index.json"
MEMORY_DIR = DATA_DIR / "data" / "memory"
SKILLS_CONTENT_DIR = DATA_DIR / "data" / "skills"
VAULT_DIR = DATA_DIR / "data" / "vault"

# Vault token — set via NEXUS_VAULT_TOKEN env var.
# If unset, a random token is generated at startup (shown in logs once, then inaccessible).
_VAULT_TOKEN_ENV = os.environ.get("NEXUS_VAULT_TOKEN", "")
if not _VAULT_TOKEN_ENV:
    _VAULT_TOKEN_ENV = secrets.token_hex(32)
    print(
        f"[nexus-vault] No NEXUS_VAULT_TOKEN set — generated ephemeral token: {_VAULT_TOKEN_ENV}",
        flush=True,
    )
VAULT_TOKEN: str = _VAULT_TOKEN_ENV

# Ensure directories exist
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
SKILLS_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "data").mkdir(parents=True, exist_ok=True)

# Metrics state
metrics_state = {
    "start_time": time.time(),
    "requests": 0,
    "errors": 0,
    "latencies": [],
    "skill_loads": 0,
    "skill_searches": 0,
    "memory_reads": 0,
    "memory_writes": 0,
    # Phase 2: Fetch + Hybrid Search
    "fetch_runs": 0,
    "fetch_skills_added": 0,
    "fetch_errors": 0,
    "hybrid_searches": 0,
    "vector_searches": 0,
    # Phase 3: Reconcile (nightly sync)
    "reconcile_last_ts": 0,
    "reconcile_files_local": 0,
    "reconcile_files_github": 0,
    "reconcile_pushed": 0,
    "reconcile_nexus_synced": 0,
    "reconcile_duration_s": 0.0,
    "reconcile_runs": 0,
    # Phase 4: Autodream (nightly pattern analysis)
    "dream_last_ts": 0,
    "dream_runs": 0,
    "dream_patterns_detected": 0,
    "dream_promotions_suggested": 0,
    "dream_memories_analyzed": 0,
    "dream_duration_s": 0.0,
    # Phase 5: Vault (secret storage)
    "vault_reads": 0,
    "vault_writes": 0,
    "vault_auth_failures": 0,
}

# Load persisted reconcile run count
try:
    _runs_file = DATA_DIR / "data" / "reconcile_runs.txt"
    if _runs_file.exists():
        metrics_state["reconcile_runs"] = int(_runs_file.read_text())
except Exception:
    pass

# Load persisted dream run count
try:
    _dream_runs_file = DATA_DIR / "data" / "dream_runs.txt"
    if _dream_runs_file.exists():
        metrics_state["dream_runs"] = int(_dream_runs_file.read_text())
except Exception:
    pass

# Model capabilities
MODEL_CAPABILITIES = {
    "claude": {
        "mcp": True,
        "skills": True,
        "hooks": True,
        "plugins": True,
        "agents": True,
    },
    "gemini": {
        "mcp": True,
        "skills": True,
        "hooks": False,
        "plugins": False,
        "agents": False,
    },
    "gpt": {
        "mcp": True,
        "skills": False,
        "hooks": False,
        "plugins": False,
        "agents": False,
    },
    "ollama": {
        "mcp": False,
        "skills": False,
        "hooks": False,
        "plugins": False,
        "agents": False,
    },
}


# --- Middleware ---


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        latency_ms = (time.time() - start_time) * 1000
        metrics_state["requests"] += 1
        metrics_state["latencies"].append(latency_ms)
        if len(metrics_state["latencies"]) > 100:
            metrics_state["latencies"].pop(0)
        return response
    except Exception:
        metrics_state["errors"] += 1
        raise


# --- Health & Metrics ---


@app.get("/")
async def root():
    return {"status": "Nexus MCP Server running", "version": "3.0.0"}


@app.get("/health")
async def health():
    uptime = int(time.time() - metrics_state["start_time"])
    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "version": "3.0.0",
        "features": ["skills", "memory", "capabilities", "vault"],
    }


@app.post("/api/doctor/report")
async def doctor_report(request: Request):
    """Receive health check report from Nexus Doctor."""
    data = await request.json()
    metrics_state["doctor_issues"] = data.get("issues_count", 0)
    metrics_state["doctor_last_ts"] = int(time.time())
    return {"status": "ok", "issues": metrics_state["doctor_issues"]}


@app.post("/api/reconcile/report")
async def reconcile_report(request: Request):
    """Receive nightly reconcile stats from Windows client."""
    data = await request.json()
    metrics_state["reconcile_last_ts"] = data.get("ts", int(time.time()))
    metrics_state["reconcile_files_local"] = data.get("files_local", 0)
    metrics_state["reconcile_files_github"] = data.get("files_github", 0)
    metrics_state["reconcile_pushed"] = data.get("pushed", 0)
    metrics_state["reconcile_nexus_synced"] = data.get("nexus_synced", 0)
    metrics_state["reconcile_duration_s"] = data.get("duration_s", 0.0)
    metrics_state["reconcile_runs"] += 1
    # Persist run count so restarts don't lose history
    try:
        runs_file = DATA_DIR / "data" / "reconcile_runs.txt"
        runs_file.parent.mkdir(parents=True, exist_ok=True)
        prev = int(runs_file.read_text()) if runs_file.exists() else 0
        total = prev + 1
        runs_file.write_text(str(total))
        metrics_state["reconcile_runs"] = total
    except Exception:
        pass
    return {"status": "ok", "run": metrics_state["reconcile_runs"]}


@app.post("/api/dream/report")
async def dream_report(request: Request):
    """Receive nightly autodream stats from Windows client."""
    data = await request.json()
    metrics_state["dream_last_ts"] = data.get("ts", int(time.time()))
    metrics_state["dream_patterns_detected"] = data.get("patterns_detected", 0)
    metrics_state["dream_promotions_suggested"] = data.get("promotions_suggested", 0)
    metrics_state["dream_memories_analyzed"] = data.get("memories_analyzed", 0)
    metrics_state["dream_duration_s"] = data.get("duration_s", 0.0)
    # Persist run count so restarts don't lose history
    try:
        dream_runs_file = DATA_DIR / "data" / "dream_runs.txt"
        dream_runs_file.parent.mkdir(parents=True, exist_ok=True)
        prev = int(dream_runs_file.read_text()) if dream_runs_file.exists() else 0
        total = prev + 1
        dream_runs_file.write_text(str(total))
        metrics_state["dream_runs"] = total
    except Exception:
        metrics_state["dream_runs"] += 1
    return {"status": "ok", "run": metrics_state["dream_runs"]}


@app.get("/metrics")
async def metrics():
    uptime_s = int(time.time() - metrics_state["start_time"])
    avg_latency = (
        sum(metrics_state["latencies"]) / len(metrics_state["latencies"])
        if metrics_state["latencies"]
        else 0
    )
    error_rate = (metrics_state["errors"] / max(metrics_state["requests"], 1)) * 100

    # Disk usage
    try:
        _, disk_used, _ = shutil.disk_usage(DATA_DIR)
    except Exception:
        disk_used = 0

    # Category counts
    index = load_skill_index()
    category_counts = index.get("categories", {})
    category_metrics = ""
    for cat, count in category_counts.items():
        category_metrics += (
            f'nexus_skills_by_category_total{{category="{cat}"}} {count}\n'
        )

    return PlainTextResponse(
        f"""# HELP nexus_uptime_seconds Server uptime in seconds
# TYPE nexus_uptime_seconds gauge
nexus_uptime_seconds {uptime_s}
# HELP nexus_requests_total Total HTTP requests
# TYPE nexus_requests_total counter
nexus_requests_total {metrics_state["requests"]}
# HELP nexus_request_errors_total Total request errors
# TYPE nexus_request_errors_total counter
nexus_request_errors_total {metrics_state["errors"]}
# HELP nexus_request_error_rate_percent Error rate percentage
# TYPE nexus_request_error_rate_percent gauge
nexus_request_error_rate_percent {error_rate:.2f}
# HELP nexus_request_latency_ms Average request latency in ms
# TYPE nexus_request_latency_ms gauge
nexus_request_latency_ms {avg_latency:.2f}
# HELP nexus_data_disk_usage_bytes Total disk usage of data directory in bytes
# TYPE nexus_data_disk_usage_bytes gauge
nexus_data_disk_usage_bytes {disk_used}
# HELP nexus_skills_by_category_total Total skills by category
# TYPE nexus_skills_by_category_total gauge
{category_metrics}
# HELP nexus_skill_loads_total Total skill load requests
# TYPE nexus_skill_loads_total counter
nexus_skill_loads_total {metrics_state["skill_loads"]}
# HELP nexus_skill_searches_total Total skill search requests
# TYPE nexus_skill_searches_total counter
nexus_skill_searches_total {metrics_state["skill_searches"]}
# HELP nexus_memory_reads_total Total memory read requests
# TYPE nexus_memory_reads_total counter
nexus_memory_reads_total {metrics_state["memory_reads"]}
# HELP nexus_memory_writes_total Total memory write requests
# TYPE nexus_memory_writes_total counter
nexus_memory_writes_total {metrics_state["memory_writes"]}
# HELP nexus_fetch_runs_total Total fetch job runs (Phase 2)
# TYPE nexus_fetch_runs_total counter
nexus_fetch_runs_total {metrics_state["fetch_runs"]}
# HELP nexus_fetch_skills_added_total Total skills added from fetch
# TYPE nexus_fetch_skills_added_total counter
nexus_fetch_skills_added_total {metrics_state["fetch_skills_added"]}
# HELP nexus_fetch_errors_total Total fetch errors
# TYPE nexus_fetch_errors_total counter
nexus_fetch_errors_total {metrics_state["fetch_errors"]}
# HELP nexus_hybrid_searches_total Total hybrid search requests
# TYPE nexus_hybrid_searches_total counter
nexus_hybrid_searches_total {metrics_state["hybrid_searches"]}
# HELP nexus_vector_searches_total Total vector search requests
# TYPE nexus_vector_searches_total counter
nexus_vector_searches_total {metrics_state["vector_searches"]}
# HELP nexus_reconcile_last_timestamp Unix timestamp of last nightly reconcile
# TYPE nexus_reconcile_last_timestamp gauge
nexus_reconcile_last_timestamp {metrics_state["reconcile_last_ts"]}
# HELP nexus_reconcile_runs_total Total reconcile runs since restart
# TYPE nexus_reconcile_runs_total counter
nexus_reconcile_runs_total {metrics_state["reconcile_runs"]}
# HELP nexus_reconcile_files_local Files found locally in last reconcile
# TYPE nexus_reconcile_files_local gauge
nexus_reconcile_files_local {metrics_state["reconcile_files_local"]}
# HELP nexus_reconcile_files_github Files found on GitHub in last reconcile
# TYPE nexus_reconcile_files_github gauge
nexus_reconcile_files_github {metrics_state["reconcile_files_github"]}
# HELP nexus_reconcile_pushed_total Files pushed to GitHub in last reconcile
# TYPE nexus_reconcile_pushed_total gauge
nexus_reconcile_pushed_total {metrics_state["reconcile_pushed"]}
# HELP nexus_reconcile_nexus_synced_total Files synced to Nexus in last reconcile
# TYPE nexus_reconcile_nexus_synced_total gauge
nexus_reconcile_nexus_synced_total {metrics_state["reconcile_nexus_synced"]}
# HELP nexus_reconcile_duration_seconds Duration of last reconcile in seconds
# TYPE nexus_reconcile_duration_seconds gauge
nexus_reconcile_duration_seconds {metrics_state["reconcile_duration_s"]:.1f}
# HELP nexus_dream_last_timestamp Unix timestamp of last nightly autodream
# TYPE nexus_dream_last_timestamp gauge
nexus_dream_last_timestamp {metrics_state["dream_last_ts"]}
# HELP nexus_dream_runs_total Total autodream runs since restart
# TYPE nexus_dream_runs_total counter
nexus_dream_runs_total {metrics_state["dream_runs"]}
# HELP nexus_dream_patterns_detected Patterns detected in last autodream
# TYPE nexus_dream_patterns_detected gauge
nexus_dream_patterns_detected {metrics_state["dream_patterns_detected"]}
# HELP nexus_dream_promotions_suggested Promotions suggested in last autodream
# TYPE nexus_dream_promotions_suggested gauge
nexus_dream_promotions_suggested {metrics_state["dream_promotions_suggested"]}
# HELP nexus_dream_memories_analyzed Memories analyzed in last autodream
# TYPE nexus_dream_memories_analyzed gauge
nexus_dream_memories_analyzed {metrics_state["dream_memories_analyzed"]}
# HELP nexus_vault_reads_total Total vault secret reads
# TYPE nexus_vault_reads_total counter
nexus_vault_reads_total {metrics_state["vault_reads"]}
# HELP nexus_vault_writes_total Total vault secret writes
# TYPE nexus_vault_writes_total counter
nexus_vault_writes_total {metrics_state["vault_writes"]}
# HELP nexus_vault_auth_failures_total Total vault auth failures
# TYPE nexus_vault_auth_failures_total counter
nexus_vault_auth_failures_total {metrics_state["vault_auth_failures"]}
# HELP nexus_doctor_issues_total Total health issues detected by Nexus Doctor
# TYPE nexus_doctor_issues_total gauge
nexus_doctor_issues_total {metrics_state["doctor_issues"]}
# HELP nexus_doctor_last_timestamp Unix timestamp of last doctor run
# TYPE nexus_doctor_last_timestamp gauge
nexus_doctor_last_timestamp {metrics_state["doctor_last_ts"]}
"""
    )


# --- Helpers: Key sanitization ---

_SAFE_KEY_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


def sanitize_memory_key(key: str) -> str:
    """Validate memory key — alphanumeric, hyphens, underscores only."""
    if not key or not _SAFE_KEY_RE.match(key):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid memory key: '{key}'. Use only a-z, 0-9, _, -",
        )
    return key


# --- Skill Registry (in-memory cache) ---

_index_cache: Optional[dict] = None
_index_mtime: float = 0.0


def load_skill_index() -> dict:
    """Load skill index with mtime-based cache. Disk read only when file changes."""
    global _index_cache, _index_mtime
    if SKILLS_INDEX_PATH.exists():
        current_mtime = SKILLS_INDEX_PATH.stat().st_mtime
        if _index_cache is not None and current_mtime == _index_mtime:
            return _index_cache
        _index_cache = json.loads(SKILLS_INDEX_PATH.read_text(encoding="utf-8"))
        _index_mtime = current_mtime
        return _index_cache
    return {"version": "1.0", "total": 0, "skills": []}


@app.get("/api/skills/index")
async def skills_index():
    """Return lightweight skill manifest."""
    index = load_skill_index()
    # Return only essential fields for each skill
    lightweight = []
    for skill in index.get("skills", []):
        lightweight.append(
            {
                "name": skill["name"],
                "description": skill.get("description", "")[:100],
                "category": skill.get("category", "general"),
                "triggers": skill.get("triggers", [])[:5],
            }
        )
    return {
        "total": len(lightweight),
        "categories": index.get("categories", {}),
        "skills": lightweight,
    }


# IMPORTANT: /search MUST be before /{name} — FastAPI matches routes in order
@app.get("/api/skills/search")
async def skills_search(q: str = Query(..., min_length=1)):
    """Search skills by query string (BM25)."""
    metrics_state["skill_searches"] += 1
    index = load_skill_index()
    query_lower = q.lower()

    results = []
    for skill in index.get("skills", []):
        if skill.get("category") == "archived":
            continue
        score = 0
        name = skill.get("name", "").lower()
        desc = skill.get("description", "").lower()
        triggers = [t.lower() for t in skill.get("triggers", [])]

        # Exact name match
        if query_lower == name:
            score = 100
        elif query_lower in name:
            score = 80
        # Description match
        elif query_lower in desc:
            score = 60
        # Trigger match
        elif any(query_lower in t for t in triggers):
            score = 70
        # Partial word match
        else:
            query_words = query_lower.split()
            matched = sum(1 for w in query_words if w in name or w in desc)
            if matched > 0:
                score = 40 + (matched * 10)

        if score > 0:
            results.append({**skill, "_score": score})

    results.sort(key=lambda x: x["_score"], reverse=True)
    # Remove score from output
    for r in results:
        r.pop("_score", None)

    return {"query": q, "total": len(results), "results": results[:10]}


@app.get("/api/skills/{name}")
async def skill_detail(name: str):
    """Return full SKILL.md content for a specific skill."""
    metrics_state["skill_loads"] += 1

    # Check local content cache first
    cached = SKILLS_CONTENT_DIR / f"{name}.md"
    if cached.exists():
        return {
            "name": name,
            "content": cached.read_text(encoding="utf-8"),
            "source": "cache",
        }

    # Check index for embedded content or path info
    index = load_skill_index()
    for skill in index.get("skills", []):
        if skill["name"] == name:
            # Check if content is embedded in index
            if "content" in skill:
                content = skill["content"]
                # Cache it
                cached.write_text(content, encoding="utf-8")
                return {"name": name, "content": content, "source": "embedded"}

            # Try filesystem path
            skill_path = skill.get("path", "")
            if skill_path and skill_path.startswith("/"):
                skill_md = Path(skill_path)
                if skill_md.exists():
                    content = skill_md.read_text(encoding="utf-8")
                    cached.write_text(content, encoding="utf-8")
                    return {"name": name, "content": content, "source": "local"}

    raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")


@app.get("/api/search/hybrid")
async def search_hybrid(
    q: str = Query(..., min_length=1),
    top_k: int = Query(10, ge=1, le=50),
    use_vector: bool = Query(True),
    use_external: bool = Query(False),
) -> dict:
    """
    Hybrid search: BM25 (keyword) + vector (semantic) + optional DDGS fetch.

    Flow:
      1. BM25 search on local index
      2. Vector search (if use_vector=true and embeddings present)
      3. Merge by weighted score: (0.6 * BM25) + (0.4 * vector)
      4. Optional: DDGS fetch if local results < threshold

    Query params:
      - q: Search query
      - top_k: Max results (1-50)
      - use_vector: Include vector search (default: true)
      - use_external: Allow DDGS fetch on-demand (default: false)

    Returns:
      {
        query, total, results: [{name, score, source}, ...], elapsed_ms
      }
    """
    start = time.time()

    metrics_state["hybrid_searches"] += 1
    index = load_skill_index()
    query_lower = q.lower()

    # Step 1: BM25 keyword search
    bm25_results = {}
    for skill in index.get("skills", []):
        if skill.get("category") == "archived":
            continue
        score = 0
        name = skill.get("name", "").lower()
        desc = skill.get("description", "").lower()
        triggers = [t.lower() for t in skill.get("triggers", [])]

        if query_lower == name:
            score = 100
        elif query_lower in name:
            score = 80
        elif query_lower in desc:
            score = 60
        elif any(query_lower in t for t in triggers):
            score = 70
        else:
            query_words = query_lower.split()
            matched = sum(1 for w in query_words if w in name or w in desc)
            if matched > 0:
                score = 40 + (matched * 10)

        if score > 0:
            bm25_results[skill.get("name", "")] = {
                "skill": skill,
                "bm25_score": score,
                "vector_score": 0,
            }

    # Step 2: Vector search (if use_vector and embeddings present in index)
    if use_vector:
        metrics_state["vector_searches"] += 1
        try:
            engine = get_embedding_engine()
            query_vector = await engine.embed(q)
            if query_vector:
                for skill in index.get("skills", []):
                    if skill.get("category") == "archived":
                        continue
                    skill_vector = skill.get("vector", [])
                    if not skill_vector:
                        continue
                    sim = cosine_similarity(query_vector, skill_vector)
                    skill_name = skill.get("name", "")
                    if skill_name in bm25_results:
                        bm25_results[skill_name]["vector_score"] = sim * 100
                    elif sim > 0.35:  # Surface semantically related skills not in BM25
                        bm25_results[skill_name] = {
                            "skill": skill,
                            "bm25_score": 0,
                            "vector_score": sim * 100,
                        }
        except Exception:
            # Vector search is optional — degrade gracefully to BM25-only
            pass

    # Step 3: Merge and rank
    merged = []
    for name, scores in bm25_results.items():
        combined_score = (0.6 * scores["bm25_score"]) + (0.4 * scores["vector_score"])
        merged.append(
            {
                "name": scores["skill"].get("name", ""),
                "description": scores["skill"].get("description", "")[:100],
                "category": scores["skill"].get("category", ""),
                "score": round(combined_score, 2),
                "source": scores["skill"].get("source", "local"),
            }
        )

    merged.sort(key=lambda x: x["score"], reverse=True)

    elapsed = (time.time() - start) * 1000  # ms

    return {
        "query": q,
        "total": len(merged),
        "results": merged[:top_k],
        "elapsed_ms": round(elapsed, 2),
    }


@app.post("/api/skills/upload")
async def skills_upload(request: Request):
    """Upload skill index from build script."""
    body = await request.json()
    skills = body.get("skills", [])

    index = {
        "version": "1.0",
        "uploaded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(skills),
        "categories": {},
        "skills": skills,
    }

    # Count categories
    for skill in skills:
        cat = skill.get("category", "general")
        index["categories"][cat] = index["categories"].get(cat, 0) + 1

    SKILLS_INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"status": "ok", "total": len(skills)}


# --- Memory ---


@app.get("/api/memory/index")
async def memory_index():
    """List all memory files."""
    metrics_state["memory_reads"] += 1
    files = []
    if MEMORY_DIR.exists():
        for f in sorted(MEMORY_DIR.iterdir()):
            if f.is_file() and f.suffix == ".md":
                files.append(
                    {
                        "key": f.stem,
                        "size": f.stat().st_size,
                        "modified": time.strftime(
                            "%Y-%m-%dT%H:%M:%S", time.localtime(f.stat().st_mtime)
                        ),
                    }
                )
    return {"total": len(files), "files": files}


@app.get("/api/memory/{key}")
async def memory_read(key: str):
    """Read a memory file."""
    key = sanitize_memory_key(key)
    metrics_state["memory_reads"] += 1
    filepath = MEMORY_DIR / f"{key}.md"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Memory '{key}' not found")
    return {"key": key, "content": filepath.read_text(encoding="utf-8")}


@app.post("/api/memory/{key}")
@app.put("/api/memory/{key}")
@app.patch("/api/memory/{key}")
async def memory_write(key: str, request: Request):
    """Write/update a memory file.

    Accepts any JSON payload:
      - {"content": "markdown string"}  — stored as-is
      - {"data": <any>}                 — JSON-serialized to string
      - Any other JSON object/array     — JSON-serialized to string
    """
    key = sanitize_memory_key(key)
    metrics_state["memory_writes"] += 1

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if isinstance(body, dict):
        if "content" in body:
            content = str(body["content"])
        elif "data" in body:
            val = body["data"]
            content = val if isinstance(val, str) else json.dumps(val, ensure_ascii=False, indent=2)
        else:
            content = json.dumps(body, ensure_ascii=False, indent=2)
    elif isinstance(body, (list, int, float, bool)):
        content = json.dumps(body, ensure_ascii=False, indent=2)
    elif isinstance(body, str):
        content = body
    else:
        raise HTTPException(status_code=400, detail="Unsupported body type")

    if not content:
        raise HTTPException(status_code=400, detail="Content is empty")

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    filepath = MEMORY_DIR / f"{key}.md"
    filepath.write_text(content, encoding="utf-8")
    return {"status": "ok", "key": key, "size": len(content)}


@app.delete("/api/memory/{key}")
async def memory_delete(key: str):
    """Delete a memory file."""
    key = sanitize_memory_key(key)
    metrics_state["memory_writes"] += 1
    filepath = MEMORY_DIR / f"{key}.md"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Memory '{key}' not found")
    filepath.unlink()
    return {"status": "ok", "key": key, "deleted": True}


# --- Vault (Phase 5) ---

_VAULT_KEY_RE = re.compile(r"^[a-zA-Z0-9_\-\.]{1,64}$")


def _vault_authorize(request: Request) -> None:
    """Check bearer token. Raise 401 on failure."""
    auth = request.headers.get("Authorization", "")
    token = auth.removeprefix("Bearer ").strip()
    if not hmac.compare_digest(token, VAULT_TOKEN):
        metrics_state["vault_auth_failures"] += 1
        raise HTTPException(status_code=401, detail="Vault: invalid or missing token")


def _vault_key_file(key: str) -> Path:
    """Validate and return vault file path. Raise 400 on bad key."""
    if not key or not _VAULT_KEY_RE.match(key):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid vault key: '{key}'. Use a-z, A-Z, 0-9, _, -, . (max 64 chars)",
        )
    return VAULT_DIR / f"{key}.json"


@app.get("/api/vault/")
async def vault_list(request: Request):
    """List vault keys (no values). Requires bearer auth."""
    _vault_authorize(request)
    keys = []
    for f in sorted(VAULT_DIR.iterdir()):
        if f.is_file() and f.suffix == ".json":
            try:
                meta = json.loads(f.read_text(encoding="utf-8"))
                keys.append(
                    {
                        "key": f.stem,
                        "updated": meta.get("updated", 0),
                        "tags": meta.get("tags", []),
                    }
                )
            except Exception:
                keys.append({"key": f.stem, "updated": 0, "tags": []})
    return {"total": len(keys), "keys": keys}


@app.get("/api/vault/{key}")
async def vault_get(key: str, request: Request):
    """Read a vault secret. Requires bearer auth."""
    _vault_authorize(request)
    vault_file = _vault_key_file(key)
    if not vault_file.exists():
        raise HTTPException(status_code=404, detail=f"Vault key '{key}' not found")
    metrics_state["vault_reads"] += 1
    meta = json.loads(vault_file.read_text(encoding="utf-8"))
    return {"key": key, "value": meta["value"], "updated": meta.get("updated", 0)}


@app.put("/api/vault/{key}")
@app.post("/api/vault/{key}")
async def vault_put(key: str, request: Request):
    """Write a vault secret. Requires bearer auth.

    Body: {"value": "secret-string", "tags": ["optional", "list"]}
    """
    _vault_authorize(request)
    vault_file = _vault_key_file(key)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    if "value" not in body:
        raise HTTPException(status_code=400, detail="Missing 'value' field")
    metrics_state["vault_writes"] += 1
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    vault_file.write_text(
        json.dumps(
            {
                "key": key,
                "value": body["value"],
                "tags": body.get("tags", []),
                "updated": time.time(),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return {"status": "ok", "key": key}


@app.delete("/api/vault/{key}")
async def vault_delete(key: str, request: Request):
    """Delete a vault secret. Requires bearer auth."""
    _vault_authorize(request)
    vault_file = _vault_key_file(key)
    if not vault_file.exists():
        raise HTTPException(status_code=404, detail=f"Vault key '{key}' not found")
    vault_file.unlink()
    return {"status": "ok", "key": key, "deleted": True}


# --- Capabilities ---


@app.get("/api/capabilities")
async def capabilities(model: Optional[str] = None):
    """Return model capabilities map."""
    if model:
        caps = MODEL_CAPABILITIES.get(model.lower())
        if not caps:
            raise HTTPException(status_code=404, detail=f"Model '{model}' not found")
        return {"model": model, "capabilities": caps}
    return {"models": MODEL_CAPABILITIES}


# --- Fetch Pipeline (Phase 2) ---


async def execute_fetch_job(job_id: str, categories: list, limit: int = 20) -> None:
    """Background task: DDGS fetch → embed → merge into skill index."""
    job = fetch_jobs.get(job_id)
    if not job:
        return

    job.status = "running"
    total_added = 0

    try:
        from nexus_embed import EmbeddingEngine, embed_skill
        from nexus_fetch import fetch_by_category
        from nexus_store import merge_fetched_skills, save_index

        engine = EmbeddingEngine()
        current_index = load_skill_index()

        for category in categories:
            try:
                report = await fetch_by_category(
                    category,
                    current_index,
                    limit_per_query=limit,
                    max_new_skills=limit * 3,
                )
                job.progress[category] = len(report.candidates)

                # Convert FetchResult → embedded dicts
                embedded: list = []
                for result in report.candidates:
                    try:
                        content = result.snippet or result.title
                        emb = await embed_skill(
                            skill_name=result.title,
                            content=content,
                            title=result.title,
                            embedding_engine=engine,
                        )
                        skill_dict = {
                            "name": result.title,
                            "description": result.snippet[:150] if result.snippet else "",
                            "category": category,
                            "source": "ddgs",
                            "url": result.url,
                            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        }
                        skill_dict.update(emb)
                        embedded.append(skill_dict)
                    except Exception:
                        pass

                added = await merge_fetched_skills(embedded, current_index)
                await save_index(current_index, SKILLS_INDEX_PATH)
                total_added += added
                metrics_state["fetch_skills_added"] += added

            except Exception as e:
                job.errors.append(f"{category}: {str(e)[:120]}")
                metrics_state["fetch_errors"] += 1

        job.skills_added = total_added
        job.status = "completed"

    except ImportError as e:
        job.status = "failed"
        job.errors.append(f"Import error: {e}")
        metrics_state["fetch_errors"] += 1
    except Exception as e:
        job.status = "failed"
        job.errors.append(str(e)[:200])
        metrics_state["fetch_errors"] += 1
    finally:
        job.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")


@app.post("/api/fetch/update")
async def fetch_update(request: Request):
    """
    Trigger fetch cycle manually.

    Body:
    {
      "categories": ["devops", "general"],  # optional; default=all
      "sources": ["ddgs"],                   # optional; default=["ddgs"]
      "limit_per_category": 50,
      "force": false
    }

    Returns:
    {
      "status": "queued",
      "job_id": "uuid"
    }
    """
    metrics_state["fetch_runs"] += 1

    try:
        body = await request.json()
    except Exception:
        body = {}

    # Generate job ID
    job_id = str(uuid.uuid4())[:8]

    # Create job state
    index = load_skill_index()
    categories = body.get("categories", list(index.get("categories", {}).keys()))

    limit = body.get("limit_per_category", 20)

    job = FetchJobState(
        job_id=job_id,
        status="queued",
        categories=categories,
    )
    fetch_jobs[job_id] = job

    # Dispatch background task — non-blocking
    asyncio.create_task(execute_fetch_job(job_id, categories, limit))

    return {
        "status": "queued",
        "job_id": job_id,
    }


@app.get("/api/fetch/status/{job_id}")
async def fetch_status(job_id: str):
    """
    Poll fetch job progress.

    Returns:
    {
      "status": "queued|running|completed|failed",
      "progress": {category: count, ...},
      "skills_added": 12,
      "errors": [...]
    }
    """
    if job_id not in fetch_jobs:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    job = fetch_jobs[job_id]
    return job.to_dict()


# --- MCP Protocol ---


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP protocol endpoint — handles tool calls."""
    body = await request.json()

    method = body.get("method", "")
    params = body.get("params", {})

    # Handle MCP tool calls
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "nexus_discover",
                        "description": "Search skill registry for relevant skills",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query",
                                },
                            },
                            "required": ["query"],
                        },
                    },
                    {
                        "name": "nexus_load",
                        "description": "Load a specific skill's full content",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Skill name"},
                            },
                            "required": ["name"],
                        },
                    },
                    {
                        "name": "nexus_memory",
                        "description": "Read or write shared memory",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "Memory key"},
                                "content": {
                                    "type": "string",
                                    "description": "Content to write (omit for read)",
                                },
                            },
                            "required": ["key"],
                        },
                    },
                    {
                        "name": "nexus_capabilities",
                        "description": "Get model capabilities",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model": {
                                    "type": "string",
                                    "description": "Model name",
                                },
                            },
                        },
                    },
                    {
                        "name": "nexus_vault_get",
                        "description": "Read a secret from the Nexus vault",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "description": "Vault key (e.g. 'dockerhub-token')",
                                },
                            },
                            "required": ["key"],
                        },
                    },
                    {
                        "name": "nexus_vault_put",
                        "description": "Write a secret to the Nexus vault",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "Vault key"},
                                "value": {"type": "string", "description": "Secret value"},
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Optional tags",
                                },
                            },
                            "required": ["key", "value"],
                        },
                    },
                ],
            },
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        if tool_name == "nexus_discover":
            query = tool_args.get("query", "")
            # Reuse search logic
            index = load_skill_index()
            query_lower = query.lower()
            results = []
            for skill in index.get("skills", []):
                if skill.get("category") == "archived":
                    continue
                name = skill.get("name", "").lower()
                desc = skill.get("description", "").lower()
                if query_lower in name or query_lower in desc:
                    results.append(
                        {
                            "name": skill["name"],
                            "description": skill.get("description", "")[:100],
                            "category": skill.get("category", ""),
                        }
                    )
            metrics_state["skill_searches"] += 1
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(results[:5], ensure_ascii=False),
                        }
                    ],
                },
            }

        if tool_name == "nexus_load":
            skill_name = tool_args.get("name", "")
            metrics_state["skill_loads"] += 1
            # Check cached content
            cached = SKILLS_CONTENT_DIR / f"{skill_name}.md"
            if cached.exists():
                content = cached.read_text(encoding="utf-8")
            else:
                # Try index for embedded content or path
                index = load_skill_index()
                content = None
                for skill in index.get("skills", []):
                    if skill["name"] == skill_name:
                        # Check embedded content first
                        if "content" in skill:
                            content = skill["content"]
                            cached.write_text(content, encoding="utf-8")
                            break
                        # Try filesystem path
                        skill_path = skill.get("path", "")
                        if skill_path and skill_path.startswith("/"):
                            skill_md = Path(skill_path)
                            if skill_md.exists():
                                content = skill_md.read_text(encoding="utf-8")
                                cached.write_text(content, encoding="utf-8")
                                break
                if not content:
                    content = f"Skill '{skill_name}' not found"

            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [{"type": "text", "text": content}],
                },
            }

        if tool_name == "nexus_memory":
            key = tool_args.get("key", "")
            if not key or not _SAFE_KEY_RE.match(key):
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {"code": -32602, "message": f"Invalid key: '{key}'"},
                }
            content = tool_args.get("content")
            filepath = MEMORY_DIR / f"{key}.md"

            if content:
                # Write
                metrics_state["memory_writes"] += 1
                filepath.write_text(content, encoding="utf-8")
                result_text = f"Memory '{key}' written ({len(content)} chars)"
            else:
                # Read
                metrics_state["memory_reads"] += 1
                if filepath.exists():
                    result_text = filepath.read_text(encoding="utf-8")
                else:
                    result_text = f"Memory '{key}' not found"

            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [{"type": "text", "text": result_text}],
                },
            }

        if tool_name == "nexus_capabilities":
            model = tool_args.get("model", "")
            if model:
                caps = MODEL_CAPABILITIES.get(model.lower(), {})
            else:
                caps = MODEL_CAPABILITIES
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [{"type": "text", "text": json.dumps(caps, ensure_ascii=False)}],
                },
            }

        if tool_name == "nexus_vault_get":
            vault_key = tool_args.get("key", "")
            # Validate key
            if not vault_key or not _VAULT_KEY_RE.match(vault_key):
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {"code": -32602, "message": f"Invalid vault key: '{vault_key}'"},
                }
            vault_file = VAULT_DIR / f"{vault_key}.json"
            if not vault_file.exists():
                result_text = f"Vault key '{vault_key}' not found"
            else:
                metrics_state["vault_reads"] += 1
                meta = json.loads(vault_file.read_text(encoding="utf-8"))
                result_text = meta["value"]
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {"content": [{"type": "text", "text": result_text}]},
            }

        if tool_name == "nexus_vault_put":
            vault_key = tool_args.get("key", "")
            vault_value = tool_args.get("value", "")
            vault_tags = tool_args.get("tags", [])
            if not vault_key or not _VAULT_KEY_RE.match(vault_key):
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {"code": -32602, "message": f"Invalid vault key: '{vault_key}'"},
                }
            if not vault_value:
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {"code": -32602, "message": "Missing 'value'"},
                }
            metrics_state["vault_writes"] += 1
            VAULT_DIR.mkdir(parents=True, exist_ok=True)
            vault_file = VAULT_DIR / f"{vault_key}.json"
            vault_file.write_text(
                json.dumps(
                    {
                        "key": vault_key,
                        "value": vault_value,
                        "tags": vault_tags,
                        "updated": time.time(),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {"content": [{"type": "text", "text": f"Vault '{vault_key}' written"}]},
            }

    # Default response
    return {"jsonrpc": "2.0", "id": body.get("id"), "result": {"received": True}}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8900)
