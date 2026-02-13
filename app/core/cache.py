"""
Small Redis-backed JSON cache with in-memory fallback.
"""

from __future__ import annotations

import json
import logging
import time
from threading import Lock
from typing import Any

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_mem_store: dict[str, tuple[float, str]] = {}
_mem_lock = Lock()
_redis_client: redis.Redis | None = None
_redis_init_failed = False


def _get_redis() -> redis.Redis | None:
    global _redis_client, _redis_init_failed
    if _redis_client is not None:
        return _redis_client
    if _redis_init_failed or not settings.ENABLE_CACHE:
        return None
    try:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.5)
        _redis_client.ping()
        return _redis_client
    except Exception as exc:
        _redis_init_failed = True
        logger.warning("Redis cache unavailable, using in-memory fallback: %s", exc)
        return None


def cache_get_json(key: str) -> Any | None:
    client = _get_redis()
    if client is not None:
        try:
            raw = client.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    with _mem_lock:
        item = _mem_store.get(key)
        if not item:
            return None
        expires_at, payload = item
        if expires_at < time.time():
            _mem_store.pop(key, None)
            return None
        try:
            return json.loads(payload)
        except Exception:
            return None


def cache_set_json(key: str, value: Any, ttl_seconds: int | None = None) -> None:
    ttl = int(ttl_seconds or settings.REDIS_CACHE_TTL)
    payload = json.dumps(value, default=str)
    client = _get_redis()
    if client is not None:
        try:
            client.setex(key, ttl, payload)
            return
        except Exception:
            pass

    with _mem_lock:
        _mem_store[key] = (time.time() + ttl, payload)


def cache_delete_prefix(prefix: str) -> None:
    client = _get_redis()
    if client is not None:
        try:
            cursor = 0
            while True:
                cursor, keys = client.scan(cursor=cursor, match=f"{prefix}*")
                if keys:
                    client.delete(*keys)
                if cursor == 0:
                    break
            return
        except Exception:
            pass

    with _mem_lock:
        for key in [k for k in _mem_store.keys() if k.startswith(prefix)]:
            _mem_store.pop(key, None)

