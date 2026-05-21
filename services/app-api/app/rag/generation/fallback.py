import asyncio
from typing import AsyncIterator
from ..retrieval.context_builder import build_fallback_answer

async def stream_fallback_tokens(answer: str, delay: float = 0.018) -> AsyncIterator[str]:
    words = answer.split(" ")
    for i, word in enumerate(words):
        yield (" " if i else "") + word
        await asyncio.sleep(delay)

async def build_fallback_stream(question: str, context_block: str, hint: str) -> AsyncIterator[str]:
    answer = build_fallback_answer(question, context_block, hint)
    async for token in stream_fallback_tokens(answer):
        yield token
