"""
BVL PSM API client
Runtime fetch from BVL ORDS API with in-memory TTL cache,
retry logic (B3), and monitoring counters (B4).
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

# B4: Monitoring-Zähler
psm_api_metrics: dict[str, int] = {
    "requests": 0,
    "cache_hits": 0,
    "retries": 0,
    "failures": 0,
    "success": 0,
}


class BVLPSMClient:
    MAX_RETRIES = 3
    RETRY_BACKOFF = (0.5, 1.0, 2.0)

    def __init__(self) -> None:
        base_url = os.getenv("BVL_PSM_API_BASE_URL", "https://psm-api.bvl.bund.de/ords/psm/api-v1")
        self.base_url = base_url.rstrip("/")
        self.timeout = float(os.getenv("BVL_PSM_API_TIMEOUT_SECONDS", "20"))
        self.ttl_seconds = int(os.getenv("BVL_PSM_CACHE_TTL_SECONDS", "43200"))  # 12h
        self._cache: Dict[str, Tuple[float, Any]] = {}

    def _cache_get(self, key: str) -> Optional[Any]:
        cached = self._cache.get(key)
        if not cached:
            return None
        ts, data = cached
        if (time.time() - ts) > self.ttl_seconds:
            self._cache.pop(key, None)
            return None
        psm_api_metrics["cache_hits"] += 1
        return data

    def _cache_set(self, key: str, value: Any) -> None:
        self._cache[key] = (time.time(), value)

    async def _get_json(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        query = "&".join(sorted(f"{k}={v}" for k, v in (params or {}).items() if v is not None))
        cache_key = f"{path}?{query}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        psm_api_metrics["requests"] += 1
        url = f"{self.base_url}{path}"
        last_exc: Optional[Exception] = None

        for attempt in range(self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.get(url, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                psm_api_metrics["success"] += 1
                self._cache_set(cache_key, data)
                return data
            except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.ConnectError) as exc:
                last_exc = exc
                psm_api_metrics["retries"] += 1
                wait = self.RETRY_BACKOFF[min(attempt, len(self.RETRY_BACKOFF) - 1)]
                logger.warning(
                    "BVL PSM API attempt %d/%d failed (%s), retrying in %.1fs",
                    attempt + 1, self.MAX_RETRIES, exc, wait,
                )
                import asyncio
                await asyncio.sleep(wait)

        psm_api_metrics["failures"] += 1
        logger.error("BVL PSM API exhausted %d retries: %s", self.MAX_RETRIES, last_exc)
        raise last_exc  # type: ignore[misc]

    async def list_mittel(self, *, search: Optional[str], skip: int, limit: int) -> dict[str, Any]:
        params: dict[str, Any] = {
            "offset": skip,
            "limit": limit,
        }
        if search:
            # ORDS endpoint supports mittelname filter (partial match)
            params["mittelname"] = search

        data = await self._get_json("/mittel/", params=params)
        items = data.get("items", []) if isinstance(data, dict) else []
        return {"items": items, "total": len(items)}

    async def get_mittel_by_kennr(self, kennr: str) -> Optional[dict[str, Any]]:
        data = await self._get_json("/mittel/", params={"kennr": kennr})
        items = data.get("items", []) if isinstance(data, dict) else []
        if not items:
            return None
        return items[0]


def parse_bvl_datetime(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        # BVL returns e.g. 2035-01-29T23:00:00Z
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def map_bvl_mittel_to_psm_payload(item: dict[str, Any], tenant_id: str) -> dict[str, Any]:
    kennr = str(item.get("kennr") or "")
    name = str(item.get("mittelname") or "")
    wirkstoff = str(item.get("versuchsbez") or "")
    mittel_typ = str(item.get("formulierung_art") or "PSM")

    return {
        "id": kennr or name,
        "tenant_id": tenant_id,
        "artikelnummer": kennr or name,
        "name": name,
        "wirkstoff": wirkstoff,
        "mittel_typ": mittel_typ,
        "bvl_nummer": kennr,
        "zulassung_ablauf": parse_bvl_datetime(item.get("zul_ende")),
        "eu_zulassung": False,
        "kulturen": [],
        "indikationen": [],
        "dosierung_min": None,
        "dosierung_max": None,
        "wartezeit": None,
        "bienenschutz": False,
        "wasserschutz_gebiet": False,
        "abstand_wohngebaeude": None,
        "abstand_gewaesser": None,
        "auflagen": [],
        "ausgangsstoff_explosivstoffe": False,
        "erklaerung_landwirt_erforderlich": False,
        "erklaerung_landwirt_status": None,
        "wirkstoff_gruppe": None,
        "rotations_empfehlung": None,
        "ek_preis": None,
        "vk_preis": None,
        "waehrung": "EUR",
        "lagerbestand": 0,
    }
