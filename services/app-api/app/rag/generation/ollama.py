import json
import os
from typing import AsyncIterator, Optional
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

async def stream_ollama(prompt: str, system: str) -> AsyncIterator[str]:
    if not OLLAMA_URL:
        return
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "system": system, "stream": True},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                chunk = data.get("response") or ""
                if chunk:
                    yield chunk
                if data.get("done"):
                    break

async def generate_ollama_once(prompt: str, system: str) -> Optional[str]:
    parts = []
    async for token in stream_ollama(prompt, system):
        parts.append(token)
    return "".join(parts).strip() or None
