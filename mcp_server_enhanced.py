#!/usr/bin/env python3
"""
AI Brain MCP Server (Enhanced with Live Memory)
FastMCP + ChromaDB + Ollama

Tools:
  list_memory   — List stored memory files
  read_memory   — Read a specific memory file
  save_memory   — SAVE NEW MEMORY (Cerrahi Mühürleme)
  search_memory — Semantic search across memories
  ask_brain     — Ask questions based on stored knowledge
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
# ChromaDB
# ---------------------------------------------------------------------------
chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))
col    = chroma.get_or_create_collection("memory")

# ---------------------------------------------------------------------------
# Ollama helpers
# ---------------------------------------------------------------------------

async def _embed(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
        )
        r.raise_for_status()
        return r.json()["embedding"]

async def _chat(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()

# ---------------------------------------------------------------------------
# Index helpers
# ---------------------------------------------------------------------------

def _index_file_sync(filename: str, content: str, embedding: list[float]):
    col.upsert(
        ids=[filename],
        embeddings=[embedding],
        documents=[content],
        metadatas=[{"filename": filename}],
    )

async def _index_file(filename: str, content: str):
    emb = await _embed(content[:4000])
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _index_file_sync, filename, content, emb)

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------
mcp = FastMCP("ai-brain")

@mcp.tool()
async def save_memory(filename: str, content: str) -> dict:
    """
    Yeni bir bilgi kaydet veya mevcut bilgiyi güncelle. (Live Memory)
    Claude veya kullanıcı bir şey öğrendiğinde bu aracı kullanmalıdır.
    Args:
        filename: Kaydedilecek dosya adı (örn. 'zimaos_lessons.md')
        content: Öğrenilen bilgi veya kural
    """
    if not filename.endswith(".md"):
        filename += ".md"
    
    # Path traversal protection
    safe_name = os.path.basename(filename)
    path = MEMORY_DIR / safe_name
    
    try:
        path.write_text(content, encoding="utf-8")
        await _index_file(safe_name, content)
        return {
            "status": "success",
            "message": f"Hafıza mühürlendi: {safe_name}",
            "size": len(content)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def list_memory() -> dict:
    files = sorted(f.name for f in MEMORY_DIR.glob("*.md"))
    return {"files": files, "count": len(files)}

@mcp.tool()
async def read_memory(filename: str) -> dict:
    safe_name = os.path.basename(filename)
    path = MEMORY_DIR / safe_name
    if not path.exists():
        return {"error": f"Dosya bulunamadı: {safe_name}"}
    content = path.read_text(encoding="utf-8")
    return {"filename": safe_name, "content": content}

@mcp.tool()
async def search_memory(query: str, n: int = 5) -> dict:
    count = col.count()
    if count == 0: return {"results": [], "note": "Index boş"}
    emb = await _embed(query)
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None, lambda: col.query(query_embeddings=[emb], n_results=min(n, count), include=["documents", "metadatas", "distances"])
    )
    hits = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        hits.append({"filename": meta["filename"], "score": round(1-dist, 4), "excerpt": doc[:500]})
    return {"results": hits}

@mcp.tool()
async def ask_brain(question: str) -> dict:
    count = col.count()
    if count == 0: return {"answer": "Hafıza boş."}
    emb = await _embed(question)
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, lambda: col.query(query_embeddings=[emb], n_results=min(3, count)))
    context = "\n\n".join(results["documents"][0])
    prompt = f"Hafızadaki bilgilere göre yanıtla:\n\n{context}\n\nSoru: {question}"
    answer = await _chat(prompt)
    return {"answer": answer}

# Starlette App Logic (Sync/Health)
async def health_endpoint(request: Request):
    return JSONResponse({"status": "ok", "indexed": col.count()})

async def sync_endpoint(request: Request):
    token = request.headers.get("X-Sync-Token")
    if token != SYNC_TOKEN:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    try:
        data = await request.json()
        files = data.get("files", {})
        updated = []
        errors = []
        
        for filename, content in files.items():
            if not filename.endswith(".md"): filename += ".md"
            safe_name = os.path.basename(filename)
            path = MEMORY_DIR / safe_name
            try:
                path.write_text(content, encoding="utf-8")
                await _index_file(safe_name, content)
                updated.append(safe_name)
            except Exception as e:
                errors.append(f"{safe_name}: {str(e)}")
        
        return JSONResponse({
            "status": "success",
            "updated": updated,
            "errors": errors,
            "indexed": col.count()
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

app = Starlette(routes=[
    Route("/health", health_endpoint, methods=["GET"]),
    Route("/sync", sync_endpoint, methods=["POST"]),
    Mount("/", app=mcp.http_app(path="/mcp")),
], lifespan=asynccontextmanager(lambda app: (yield)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
