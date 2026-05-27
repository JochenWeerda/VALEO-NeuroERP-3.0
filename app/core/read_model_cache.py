"""
read_model_cache.py — Redis-backed Read-Model Cache für Dashboard-Endpoints

TTL-Strategie:
  - Dashboard-Listen (KPIs, Dashboards): 30s — ändert sich selten
  - Timeseries: 60s — aggregierte historische Daten
  - Actions: 15s — aktiver Status, öfter aktualisiert

Invalidierung: Jeder schreibende Zugriff (POST/PUT/DELETE) löscht den
zugehörigen Tenant-Cache-Key.
"""
from __future__ import annotations

import json
import logging
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Redis-Client (lazy init, graceful degradation wenn nicht erreichbar)
# ---------------------------------------------------------------------------
_redis = None

def _get_redis():
    global _redis
    if _redis is not None:
        return _redis
    try:
        import redis as _redis_lib
        from app.core.config import settings
        _redis = _redis_lib.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        _redis.ping()
        logger.info("Read-model cache: Redis verbunden (%s)", settings.REDIS_URL)
    except Exception as exc:
        logger.warning("Read-model cache: Redis nicht erreichbar (%s) — Caching deaktiviert", exc)
        _redis = None
    return _redis


def _cache_key(prefix: str, tenant_id: str, **kwargs) -> str:
    suffix = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
    return f"rm:{prefix}:{tenant_id}:{suffix}" if suffix else f"rm:{prefix}:{tenant_id}"


def cached_read_model(prefix: str, ttl: int = 30):
    """
    Dekorator für synchrone und asynchrone GET-Handler. Cached das Ergebnis in Redis.

    Verwendung (sync):
        @router.get("/controlling/kpis")
        @cached_read_model("kpis", ttl=30)
        def list_kpis(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
            ...

    Verwendung (async):
        @router.get("/articles/")
        @cached_read_model("articles", ttl=300)
        async def list_articles(tenant_id: str = Depends(get_tenant_id), ...):
            ...
    """
    import inspect

    def decorator(fn: Callable) -> Callable:
        if inspect.iscoroutinefunction(fn):
            @wraps(fn)
            async def async_wrapper(*args, **kwargs):
                tenant_id = kwargs.get("tenant_id", "unknown")
                cache_kwargs = {k: v for k, v in kwargs.items() if k not in ("db", "tenant_id")}
                key = _cache_key(prefix, tenant_id, **cache_kwargs)
                r = _get_redis()
                if r is not None:
                    try:
                        hit = r.get(key)
                        if hit is not None:
                            return json.loads(hit)
                    except Exception as exc:
                        logger.debug("Cache-read fehlgeschlagen: %s", exc)
                result = await fn(*args, **kwargs)
                if r is not None:
                    try:
                        r.setex(key, ttl, json.dumps(result, default=str))
                    except Exception as exc:
                        logger.debug("Cache-write fehlgeschlagen: %s", exc)
                return result
            return async_wrapper

        @wraps(fn)
        def wrapper(*args, **kwargs):
            tenant_id = kwargs.get("tenant_id", "unknown")
            cache_kwargs = {k: v for k, v in kwargs.items() if k not in ("db", "tenant_id")}
            key = _cache_key(prefix, tenant_id, **cache_kwargs)
            r = _get_redis()
            if r is not None:
                try:
                    hit = r.get(key)
                    if hit is not None:
                        return json.loads(hit)
                except Exception as exc:
                    logger.debug("Cache-read fehlgeschlagen: %s", exc)
            result = fn(*args, **kwargs)
            if r is not None:
                try:
                    r.setex(key, ttl, json.dumps(result, default=str))
                except Exception as exc:
                    logger.debug("Cache-write fehlgeschlagen: %s", exc)
            return result
        return wrapper
    return decorator


def invalidate_tenant_prefix(prefix: str, tenant_id: str) -> None:
    """Löscht alle Cache-Einträge eines Tenants für einen Prefix (nach Mutationen)."""
    r = _get_redis()
    if r is None:
        return
    try:
        pattern = f"rm:{prefix}:{tenant_id}:*"
        keys = r.keys(pattern)
        base_key = f"rm:{prefix}:{tenant_id}"
        if r.exists(base_key):
            keys.append(base_key)
        if keys:
            r.delete(*keys)
    except Exception as exc:
        logger.debug("Cache-invalidierung fehlgeschlagen: %s", exc)
