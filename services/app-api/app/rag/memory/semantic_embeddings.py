"""Embeddings sémantiques (nomic-embed via Ollama) avec repli hash 64D."""

import os
from typing import List, Optional, Tuple

import httpx

from .embeddings import EMBED_DIM, embed_text as embed_text_hash

EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))
OLLAMA_URL = os.getenv("OLLAMA_URL", "").rstrip("/")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")


async def embed_semantic(text: str) -> Tuple[List[float], str]:
    """
    Retourne (vecteur, source).
    source: 'nomic' si Ollama/embed OK, sinon 'hash' (64D, pas pgvector).
    """
    if not text or not text.strip():
        return [0.0] * EMBEDDING_DIM, "empty"

    if OLLAMA_URL:
        vec = await _embed_ollama(text.strip())
        if vec and len(vec) == EMBEDDING_DIM:
            return vec, "nomic"
        if vec:
            return _normalize(vec), "nomic-partial"

    return embed_text_hash(text), "hash"


async def _embed_ollama(text: str) -> Optional[List[float]]:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBEDDING_MODEL, "prompt": text},
            )
            res.raise_for_status()
            data = res.json()
            emb = data.get("embedding")
            if isinstance(emb, list) and emb:
                return [float(x) for x in emb]
    except Exception:
        return None
    return None


def _normalize(vec: List[float]) -> List[float]:
    import math

    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]
