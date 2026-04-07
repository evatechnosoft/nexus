"""
Nexus embedding module: FastEmbed + chunking + caching.
Embeds fetched skill content for semantic search.
"""

import hashlib
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from nexus_utils import logger, hash_content


# ============================================================================
# EMBEDDING ENGINE (Lazy-Load FastEmbed)
# ============================================================================

class EmbeddingEngine:
    """Lazy-load FastEmbed model; cache embeddings."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initialize embedding engine.
        Model only loads on first embed() call (lazy).
        """
        self.model_name = model_name
        self.model = None  # Lazy-loaded
        self.cache: Dict[str, List[float]] = {}  # content_hash → embedding
        self._initialized = False

    def _load_model(self):
        """Load FastEmbed model (lazy initialization)."""
        if self._initialized:
            return

        try:
            from fastembed import TextEmbedding
            self.model = TextEmbedding(
                model_name=self.model_name,
                cache_dir=None,  # Use default cache
                threads=1,  # Single thread for async compatibility
            )
            self._initialized = True
            logger.info(f"FastEmbed model loaded: {self.model_name} (384-dim)")
        except ImportError:
            logger.error("fastembed not installed. Install with: pip install fastembed")
            self.model = None
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None
            self._initialized = True

    async def embed(self, text: str) -> List[float]:
        """
        Embed text to 384-dimensional vector.
        Uses cache if available.

        Args:
            text: Text to embed

        Returns:
            List of 384 floats, or empty list on error
        """
        if not text or not isinstance(text, str):
            return []

        # Check cache
        content_hash = hash_content(text)
        if content_hash in self.cache:
            return self.cache[content_hash]

        # Load model if not initialized
        if not self._initialized:
            self._load_model()

        # Embed
        if self.model is None:
            logger.warning(f"Model not available; skipping embedding for text of {len(text)} chars")
            return []

        try:
            # FastEmbed embed() returns generator; convert to list
            embeddings = list(self.model.embed(text))
            if embeddings:
                embedding = embeddings[0].tolist() if hasattr(embeddings[0], 'tolist') else list(embeddings[0])
                # Cache
                self.cache[content_hash] = embedding
                return embedding
            return []
        except Exception as e:
            logger.error(f"Embedding failed for text of {len(text)} chars: {e}")
            return []

    def clear_cache(self):
        """Clear embedding cache."""
        self.cache.clear()
        logger.debug("Embedding cache cleared")


# ============================================================================
# CHUNKING STRATEGY
# ============================================================================

def chunk_document(
    content: str,
    chunk_size: int = 512,
    overlap: int = 64,
) -> List[str]:
    """
    Split document into overlapping chunks.

    Strategy:
      1. Split by sentences (use regex for sentence boundaries)
      2. Merge small chunks to enforce chunk_size
      3. Add overlap context between chunks
      4. Trim to max 1000 chunks per document

    Args:
        content: Text to chunk
        chunk_size: Target characters per chunk
        overlap: Overlap characters between chunks

    Returns:
        List of chunk strings
    """
    if not content:
        return []

    # Split by sentence (rough: period, exclamation, question)
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    if not sentences:
        # No sentences; split by newline
        sentences = content.strip().split('\n')
    if not sentences:
        # Last resort: return whole content as one chunk
        return [content]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    # Add overlap: each chunk includes last N chars from previous
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_overlap = chunks[i - 1][-overlap:] if len(chunks[i - 1]) > overlap else chunks[i - 1]
            overlapped.append(prev_overlap + " " + chunks[i])
        chunks = overlapped

    # Limit
    chunks = chunks[:1000]

    logger.debug(f"Chunked {len(content)} chars into {len(chunks)} chunks")
    return chunks


# ============================================================================
# SKILL EMBEDDING
# ============================================================================

async def embed_skill(
    skill_name: str,
    content: str,
    title: str = "",
    embedding_engine: Optional[EmbeddingEngine] = None,
) -> Dict:
    """
    Chunk + embed skill content.

    Strategy:
      1. Chunk long content (>2000 chars)
      2. Embed title + first chunk (weighted emphasis)
      3. Embed remaining chunks
      4. Aggregate: mean of all chunk embeddings

    Args:
        skill_name: Skill identifier
        content: Full skill markdown content
        title: Optional short title for emphasis
        embedding_engine: EmbeddingEngine instance

    Returns:
        Dict with keys:
          - name, vector (384-dim aggregate), chunks, embedding_model, embedding_cached
    """
    if not embedding_engine:
        embedding_engine = EmbeddingEngine()

    # Load model if needed
    if not embedding_engine._initialized:
        embedding_engine._load_model()

    # Chunk content
    chunks = chunk_document(content, chunk_size=512, overlap=64)
    if not chunks:
        logger.warning(f"No chunks for skill '{skill_name}'")
        return {
            "name": skill_name,
            "vector": [],
            "chunks": [],
            "embedding_model": embedding_engine.model_name,
            "embedding_cached": False,
        }

    # Embed chunks
    chunk_embeddings = []
    for i, chunk in enumerate(chunks):
        try:
            vector = await embedding_engine.embed(chunk)
            if vector:
                chunk_embeddings.append({
                    "text": chunk[:200] + ("..." if len(chunk) > 200 else ""),
                    "vector": vector,
                    "chunk_index": i,
                })
        except Exception as e:
            logger.warning(f"Failed to embed chunk {i} of '{skill_name}': {e}")

    if not chunk_embeddings:
        logger.error(f"No chunks embedded for skill '{skill_name}'")
        return {
            "name": skill_name,
            "vector": [],
            "chunks": [],
            "embedding_model": embedding_engine.model_name,
            "embedding_cached": False,
        }

    # Aggregate: mean of all chunk vectors
    vector_dim = len(chunk_embeddings[0]["vector"])
    aggregate = [0.0] * vector_dim

    for chunk_emb in chunk_embeddings:
        for j, val in enumerate(chunk_emb["vector"]):
            aggregate[j] += val

    aggregate = [v / len(chunk_embeddings) for v in aggregate]

    logger.info(
        f"Embedded skill '{skill_name}': {len(chunks)} chunks, "
        f"{len(chunk_embeddings)} embedded, 384-dim aggregate"
    )

    return {
        "name": skill_name,
        "vector": aggregate,
        "chunks": chunk_embeddings,
        "embedding_model": embedding_engine.model_name,
        "embedding_cached": False,
    }


# ============================================================================
# EMBEDDING CACHE (Persistent)
# ============================================================================

class EmbeddingCache:
    """Persistent embedding cache."""

    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize cache.

        Args:
            cache_file: Optional path to JSON cache file
        """
        self.cache_file = cache_file
        self.data: Dict[str, List[float]] = {}
        if cache_file:
            self.load()

    def get(self, content_hash: str) -> Optional[List[float]]:
        """Retrieve cached embedding."""
        return self.data.get(content_hash)

    def save(self, content_hash: str, embedding: List[float]):
        """Cache embedding."""
        self.data[content_hash] = embedding
        if self.cache_file:
            self.persist()

    def persist(self):
        """Write cache to disk."""
        if not self.cache_file:
            return

        try:
            import json
            from pathlib import Path
            path = Path(self.cache_file)
            path.write_text(
                json.dumps(self.data),
                encoding="utf-8"
            )
            logger.debug(f"Embedding cache persisted: {len(self.data)} entries")
        except Exception as e:
            logger.warning(f"Failed to persist cache: {e}")

    def load(self):
        """Load cache from disk."""
        if not self.cache_file:
            return

        try:
            import json
            from pathlib import Path
            path = Path(self.cache_file)
            if path.exists():
                self.data = json.loads(path.read_text(encoding="utf-8"))
                logger.debug(f"Embedding cache loaded: {len(self.data)} entries")
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")


# ============================================================================
# MAIN (for testing)
# ============================================================================

async def main():
    """Test embedding locally."""
    print("Testing embedding...")

    engine = EmbeddingEngine()

    # Test 1: Simple embed
    text = "Docker is a containerization platform for building and deploying applications."
    vector = await engine.embed(text)
    print(f"Embedded {len(text)} chars -> {len(vector)}-dim vector")

    # Test 2: Chunk + embed
    long_text = """
    Docker containers are lightweight virtualization units.
    They package applications with all dependencies.
    Benefits include consistency, scalability, and portability.
    """ * 10

    chunks = chunk_document(long_text, chunk_size=200, overlap=32)
    print(f"Chunked {len(long_text)} chars into {len(chunks)} chunks")

    for i, chunk in enumerate(chunks[:3]):
        vector = await engine.embed(chunk)
        print(f"  Chunk {i}: {len(chunk)} chars -> {len(vector)}-dim")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
