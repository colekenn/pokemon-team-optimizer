import hashlib
import json
from typing import Any, Optional

import redis

from app.config import settings

_client: Optional[redis.Redis] = None


def get_client() -> Optional[redis.Redis]:
    global _client
    if _client is None:
        try:
            _client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=1)
            _client.ping()
        except redis.RedisError:
            _client = None
    return _client


def cache_key(prefix: str, payload: Any) -> str:
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return f"{prefix}:{digest}"


def get_json(key: str) -> Optional[Any]:
    client = get_client()
    if not client:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw else None
    except redis.RedisError:
        return None


def set_json(key: str, value: Any) -> None:
    client = get_client()
    if not client:
        return
    try:
        client.setex(key, settings.cache_ttl_seconds, json.dumps(value))
    except redis.RedisError:
        pass
