#!/usr/bin/env python3
"""
AI Brain MCP Server
FastMCP + ChromaDB + Ollama (semantic search & RAG)

Tools:
  list_memory   — /data/memory/ dosya listesi
  read_memory   — Dosya içeriği
  search_memory — ChromaDB semantic arama
  ask_brain     — search → Ollama LLM → cevap

Sync endpoint (HTTP, MCP dışı):
  POST /sync    — {"files": {"profile.md": "içerik", ...}}
                  X-Sync-Token header ile auth

GET /health     — sağlık kontrolü
"""

import os
import json
import asyncio
import httpx
import chromadb
from contextlib import asynccontextmanager
from pathlib import Path
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import JSONResponse

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATA_DIR    = Path(os.getenv("AI_SYNC_DATA", "/data"))
MEMORY_DIR  = DATA_DIR / "memory"
CHROMA_DIR  = DATA_DIR / "chroma"
OLLAMA_URL  = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
LLM_MODEL   = os.getenv("LLM_MODEL", "llama3.2")
SYNC_TOKEN  = os.getenv("SYNC_TOKEN", "changeme")
PORT        = int(os.getenv("AI_SYNC_PORT", "8900"))

MEMORY_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# ChromaDB (sync — thread-safe, event loop'u bloklamaz çünkü kısa op)
# ---------------------------------------------------------------------------
chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))
col    = chroma.get_or_create_collection("memory")

# ---------------------------------------------------------------------------
# Ollama helpers (async)
# ---------------------------------------------------------------------------

async def _embed(text: str) -> list[float]:
    """nomic-embed-text ile embedding al."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
        )
        r.raise_for_status()
        return r.json()["embedding"]


async def _chat(prompt: str) -> str:
    """LLM'e tek seferlik soru sor."""
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()


# ---------------------------------------------------------------------------
# ChromaDB index helpers (sync, run in thread pool)
# ---------------------------------------------------------------------------

def _index_file_sync(filename: str, content: str, embedding: list[float]):
    """Tek dosyayı ChromaDB'ye ekle / güncelle (thread pool'da çağrılır)."""
    col.upsert(
        ids=[filename],
        embeddings=[embedding],
        documents=[content],
        metadatas=[{"filename": filename}],
    )


async def _index_file(filename: str, content: str):
    """Embed + ChromaDB upsert (async)."""
    emb = await _embed(content[:4000])
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _index_file_sync, filename, content, emb)


async def _reindex_all():
    """MEMORY_DIR içindeki tüm .md dosyalarını re-index et."""
    tasks = []
    for md in MEMORY_DIR.glob("*.md"):
        content = md.read_text(encoding="utf-8")
        tasks.append(_index_file(md.name, content))
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for md, res in zip(list(MEMORY_DIR.glob("*.md")), results):
            if isinstance(res, Exception):
                print(f"[reindex] {md.name} hata: {res}")


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------
mcp = FastMCP("ai-brain")


@mcp.tool()
async def list_memory() -> dict:
    """
    /data/memory/ dizinindeki tüm .md dosyalarını listele.
    Döner: {"files": ["profile.md", "projects.md", ...], "count": N}
    """
    files = sorted(f.name for f in MEMORY_DIR.glob("*.md"))
    return {"files": files, "count": len(files)}


@mcp.tool()
async def read_memory(filename: str) -> dict:
    """
    Belirtilen dosyanın içeriğini döndür.
    Args:
        filename: Okunacak dosya adı (örn. 'profile.md')
    """
    # Path traversal koruması
    if "/" in filename or "\\" in filename or ".." in filename:
        return {"error": "Geçersiz dosya adı"}
    path = MEMORY_DIR / filename
    if not path.exists():
        available = [f.name for f in MEMORY_DIR.glob("*.md")]
        return {"error": f"Dosya bulunamadı: {filename}", "available": available}
    if path.suffix.lower() != ".md":
        return {"error": "Sadece .md dosyaları okunabilir"}
    content = path.read_text(encoding="utf-8")
    return {"filename": filename, "content": content, "size": len(content)}


@mcp.tool()
async def search_memory(query: str, n: int = 5) -> dict:
    """
    Semantic arama — ChromaDB + nomic-embed-text.
    Args:
        query: Arama sorgusu
        n: Döndürülecek sonuç sayısı (varsayılan 5)
    """
    count = col.count()
    if count == 0:
        return {"query": query, "results": [], "note": "Index boş — önce /sync ile dosya gönder"}

    try:
        emb = await _embed(query)
    except Exception as e:
        return {"error": f"Embedding hatası: {e}"}

    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: col.query(
                query_embeddings=[emb],
                n_results=min(n, count),
                include=["documents", "metadatas", "distances"],
            ),
        )
    except Exception as e:
        return {"error": f"ChromaDB hatası: {e}"}

    hits = []
    docs      = results.get("documents", [[]])[0]
    metas     = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, distances):
        hits.append({
            "filename": meta.get("filename", ""),
            "score":    round(1 - dist, 4),   # cosine distance → similarity
            "excerpt":  doc[:500],
        })

    return {"query": query, "results": hits}


@mcp.tool()
async def ask_brain(question: str) -> dict:
    """
    Hafızadaki bilgilere dayanarak soruyu yanıtla.
    search_memory → context → Ollama LLM → cevap.
    Args:
        question: Sorulacak soru
    """
    count = col.count()
    if count == 0:
        return {"answer": "Hafızada bilgi yok. Önce /sync ile dosya gönder.", "sources": []}

    # 1. Semantic arama
    try:
        emb = await _embed(question)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: col.query(
                query_embeddings=[emb],
                n_results=min(5, count),
                include=["documents", "metadatas"],
            ),
        )
        docs  = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
    except Exception as e:
        return {"error": f"Arama hatası: {e}"}

    if not docs:
        return {"answer": "İlgili bilgi bulunamadı.", "sources": []}

    # 2. Prompt oluştur
    context_parts = []
    for doc, meta in zip(docs, metas):
        context_parts.append(f"=== {meta.get('filename', 'unknown')} ===\n{doc[:1000]}")
    context = "\n\n".join(context_parts)

    prompt = f"""Sen bir AI asistanısın. Aşağıdaki hafıza dosyalarındaki bilgilere dayanarak soruyu yanıtla.
Bilmiyorsan "Bilmiyorum" de. Türkçe cevap ver.

HAFIZA:
{context}

SORU: {question}

CEVAP:"""

    # 3. LLM
    try:
        answer = await _chat(prompt)
    except Exception as e:
        return {"error": f"LLM hatası ({LLM_MODEL}): {e}"}

    sources = [m.get("filename", "") for m in metas]
    return {"question": question, "answer": answer, "sources": sources}


# ---------------------------------------------------------------------------
# Sync HTTP endpoint (MCP dışı)
# ---------------------------------------------------------------------------

async def sync_endpoint(request: Request) -> JSONResponse:
    """
    POST /sync
    Header: X-Sync-Token: <SYNC_TOKEN>
    Body: {"files": {"filename.md": "içerik", ...}}
    """
    token = request.headers.get("X-Sync-Token", "")
    if token != SYNC_TOKEN:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    files: dict = body.get("files", {})
    if not isinstance(files, dict):
        return JSONResponse({"error": "'files' dict olmalı"}, status_code=400)

    updated: list[str] = []
    errors:  list[str] = []

    for filename, content in files.items():
        # Güvenlik: sadece .md, path traversal yok
        if (not filename.endswith(".md")
                or "/" in filename
                or "\\" in filename
                or ".." in filename):
            errors.append(f"Geçersiz dosya adı: {filename}")
            continue
        try:
            path = MEMORY_DIR / filename
            path.write_text(str(content), encoding="utf-8")
            await _index_file(filename, str(content))
            updated.append(filename)
        except Exception as e:
            errors.append(f"{filename}: {e}")

    return JSONResponse({
        "updated": updated,
        "errors":  errors,
        "total":   len(updated),
        "indexed": col.count(),
    })


async def health_endpoint(request: Request) -> JSONResponse:
    """GET /health — sağlık kontrolü + Ollama erişim testi."""
    ollama_ok = False
    ollama_err = ""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            ollama_ok = r.status_code == 200
    except Exception as e:
        ollama_err = str(e)

    return JSONResponse({
        "status":       "ok" if ollama_ok else "degraded",
        "memory_files": len(list(MEMORY_DIR.glob("*.md"))),
        "indexed_docs": col.count(),
        "ollama":       "ok" if ollama_ok else f"error: {ollama_err}",
        "embed_model":  EMBED_MODEL,
        "llm_model":    LLM_MODEL,
    })


# ---------------------------------------------------------------------------
# Lifespan: startup'ta mevcut dosyaları index'le
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app):
    """Startup: mevcut .md dosyaları index'te yoksa re-index et."""
    existing = list(MEMORY_DIR.glob("*.md"))
    if existing and col.count() == 0:
        print(f"[ai-brain] {len(existing)} dosya index'leniyor...")
        await _reindex_all()
        print(f"[ai-brain] Index tamamlandı ({col.count()} doküman).")
    else:
        print(f"[ai-brain] Index hazır ({col.count()} doküman).")
    yield
    # shutdown (gerekirse cleanup)


# ---------------------------------------------------------------------------
# Uygulama bileşimi: MCP + HTTP
# ---------------------------------------------------------------------------

def build_app() -> Starlette:
    """FastMCP + Starlette birleştir."""
    # FastMCP 2.x: http_app() → ASGI app, /mcp path'te streamable-http
    mcp_asgi = mcp.http_app(path="/mcp")

    routes = [
        Route("/health", health_endpoint, methods=["GET"]),
        Route("/sync",   sync_endpoint,   methods=["POST"]),
        Mount("/",       app=mcp_asgi),
    ]

    # Tek lifespan: hem startup indexing hem FastMCP lifecycle
    app = Starlette(routes=routes, lifespan=lifespan)
    return app


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    print(f"[ai-brain] Başlatılıyor — port {PORT}")
    print(f"[ai-brain] Ollama: {OLLAMA_URL}")
    print(f"[ai-brain] Embed: {EMBED_MODEL} | LLM: {LLM_MODEL}")
    print(f"[ai-brain] Memory: {MEMORY_DIR} | Chroma: {CHROMA_DIR}")

    app = build_app()
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
