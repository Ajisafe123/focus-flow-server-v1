import asyncio
from functools import wraps
from typing import Callable, Any, Dict
from datetime import datetime, timedelta

_cache_store: Dict[str, dict] = {}

def cache(ttl: int = 300):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            now = datetime.utcnow()
            if key in _cache_store:
                entry = _cache_store[key]
                if entry["expires_at"] > now:
                    return entry["value"]

            value = await func(*args, **kwargs)
            _cache_store[key] = {
                "value": value,
                "expires_at": now + timedelta(seconds=ttl)
            }
            return value
        return wrapper
    return decorator

async def clear_expired_cache():
    while True:
        now = datetime.utcnow()
        expired_keys = [k for k, v in _cache_store.items() if v["expires_at"] < now]
        for k in expired_keys:
            _cache_store.pop(k, None)
        await asyncio.sleep(60)  