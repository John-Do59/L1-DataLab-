import os
import json
import redis.asyncio as redis
from typing import Any, Optional

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def get_cache(key: str) -> Optional[Any]:
    try:
        val = await redis_client.get(key)
        if val:
            return json.loads(val)
    except Exception as e:
        print(f"Redis get error: {e}")
    return None

async def set_cache(key: str, value: Any, ttl: int = 60) -> bool:
    try:
        await redis_client.set(key, json.dumps(value), ex=ttl)
        return True
    except Exception as e:
        print(f"Redis set error: {e}")
        return False
