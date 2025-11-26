"""Provider für Sanktionslisten-Updates."""

from __future__ import annotations

import csv
import io
import logging
from pathlib import Path
from time import monotonic
from typing import Iterable, List

import httpx
from prometheus_client import Counter, Gauge

from app.config import settings

logger = logging.getLogger(__name__)

REFRESH_COUNTER = Counter(
    "zoll_sanctions_refresh_total",
    "Number of sanctions refresh attempts",
    labelnames=["result"],
)
BACKOFF_GAUGE = Gauge(
    "zoll_sanctions_refresh_backoff_minutes",
    "Current refresh/backoff interval in minutes",
)


class SanctionsProvider:
    """Lädt Sanktionsdaten lokal und von Remote-Endpunkten."""

    def __init__(self) -> None:
        self._cache: List[dict[str, str]] = []
        self._current_interval = settings.SANCTIONS_REFRESH_INTERVAL_MINUTES
        self._next_refresh_ts = 0.0
        self._load_local()
        BACKOFF_GAUGE.set(self._current_interval)

    def _load_local(self) -> None:
        path = Path(settings.SANCTIONS_DATA_PATH)
        if not path.exists():
            logger.warning("Lokale Sanktionsliste %s nicht vorhanden", path)
            self._cache = []
            return
        with path.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self._cache = list(reader)

    async def refresh(self) -> bool:
        now = monotonic()
        if now < self._next_refresh_ts:
            logger.debug(
                "Sanktionsrefresh übersprungen. Backoff aktiv für %.0f Sekunden",
                self._next_refresh_ts - now,
            )
            REFRESH_COUNTER.labels(result="skipped").inc()
            return False

        remote_entries, failed_sources = await self._collect_remote_entries()
        if not remote_entries:
            self._apply_backoff(now, failed_sources)
            REFRESH_COUNTER.labels(result="failed").inc()
            return False

        previous_len = len(self._cache)
        self._cache = self._merge_entries(remote_entries)
        delta = len(self._cache) - previous_len
        self._current_interval = settings.SANCTIONS_REFRESH_INTERVAL_MINUTES
        self._next_refresh_ts = now + self._current_interval * 60
        BACKOFF_GAUGE.set(self._current_interval)
        REFRESH_COUNTER.labels(result="success").inc()

        logger.info(
            "Sanktionsdaten aktualisiert (%s Einträge, Δ %+d). Nächster Lauf in %s Minuten.",
            len(self._cache),
            delta,
            self._current_interval,
        )
        if failed_sources:
            logger.warning(
                "Teilweise fehlgeschlagen: %s",
                ", ".join(failed_sources),
            )
        return True

    async def _collect_remote_entries(self) -> tuple[List[dict[str, str]], List[str]]:
        aggregated: List[dict[str, str]] = []
        failed: List[str] = []

        sources = [
            ("internal", settings.SANCTIONS_REFRESH_URL, None),
            ("ofac", settings.OFAC_API_URL, settings.OFAC_API_KEY),
            ("eu", settings.EU_API_URL, settings.EU_API_KEY),
        ]

        for label, url, api_key in sources:
            entries = await self._fetch_csv(label, url, api_key)
            if entries is None:
                failed.append(label)
                continue
            aggregated.extend(entries)

        return aggregated, failed

    async def _fetch_csv(
        self,
        source_label: str,
        url: str | None,
        api_key: str | None = None,
    ) -> List[dict[str, str]] | None:
        if not url:
            return []
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        try:
            async with httpx.AsyncClient(timeout=30.0, headers=headers or None) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.text
        except httpx.HTTPError as exc:  # noqa: BLE001
            logger.warning("Konnte Sanktionsdaten von %s nicht aktualisieren: %s", source_label, exc)
            return None
        reader = csv.DictReader(io.StringIO(data))
        return list(reader)

    def matches(self) -> Iterable[dict[str, str]]:
        return list(self._cache)

    def _merge_entries(self, new_entries: List[dict[str, str]]) -> List[dict[str, str]]:
        merged: dict[str, dict[str, str]] = {}
        for entry in self._cache:
            merged[self._entry_key(entry)] = entry
        for entry in new_entries:
            merged[self._entry_key(entry)] = entry
        return list(merged.values())

    @staticmethod
    def _entry_key(entry: dict[str, str]) -> str:
        return entry.get("id") or entry.get("name") or entry.get("list", "unknown")

    def _apply_backoff(self, now: float, failed_sources: List[str]) -> None:
        next_interval = min(
            settings.SANCTIONS_REFRESH_MAX_BACKOFF_MINUTES,
            max(self._current_interval * 2, settings.SANCTIONS_REFRESH_BACKOFF_MINUTES),
        )
        self._current_interval = next_interval
        self._next_refresh_ts = now + next_interval * 60
        BACKOFF_GAUGE.set(next_interval)
        logger.warning(
            "Sanktionsrefresh fehlgeschlagen (Quellen: %s). Backoff auf %s Minuten gesetzt.",
            ", ".join(failed_sources) or "unbekannt",
            next_interval,
        )
