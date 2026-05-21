import json
from typing import AsyncIterator

def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

async def wrap_token_stream(token_stream: AsyncIterator[str], meta: dict) -> AsyncIterator[str]:
    yield sse_event("meta", meta)
    buffer = []
    async for token in token_stream:
        buffer.append(token)
        yield sse_event("token", {"t": token, "full": "".join(buffer)})
    yield sse_event("done", {"answer": "".join(buffer), **meta})
