"""
Numbering Service
Automatische Belegnummern-Generierung mit ENV-konfigurierbaren Nummernkreisen
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import threading
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class NumberSeries:
    """Nummernkreis für eine Belegart"""

    prefix: str
    width: int = 5
    start: int = 1
    value: int = 0

    def next(self) -> str:
        """Generiert nächste Nummer"""
        if self.value < self.start:
            self.value = self.start
        out = f"{self.prefix}{self.value:0{self.width}d}"
        self.value += 1
        return out


class NumberingService:
    """Nummernkreis-Service mit JSON-Persistenz und ENV-Overrides"""

    def __init__(self, store_path: str = "data/series.json") -> None:
        self.path = Path(store_path)
        self.lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._series: dict[str, NumberSeries] = {}
        self._load()

    def _default_series(self) -> dict[str, NumberSeries]:
        """Standard-Nummernkreise mit ENV-Overrides"""
        return {
            "sales_order": NumberSeries(
                os.environ.get("NUMBER_PREFIX_SALES_ORDER", "SO-"),
                int(os.environ.get("NUMBER_WIDTH_SALES_ORDER", "5")),
                int(os.environ.get("NUMBER_START_SALES_ORDER", "1")),
            ),
            "delivery": NumberSeries(
                os.environ.get("NUMBER_PREFIX_DELIVERY", "DL-"),
                int(os.environ.get("NUMBER_WIDTH_DELIVERY", "5")),
                int(os.environ.get("NUMBER_START_DELIVERY", "1")),
            ),
            "invoice": NumberSeries(
                os.environ.get("NUMBER_PREFIX_INVOICE", "INV-"),
                int(os.environ.get("NUMBER_WIDTH_INVOICE", "5")),
                int(os.environ.get("NUMBER_START_INVOICE", "1")),
            ),
            "purchase_order": NumberSeries(
                os.environ.get("NUMBER_PREFIX_PURCHASE_ORDER", "PO-"),
                int(os.environ.get("NUMBER_WIDTH_PURCHASE_ORDER", "5")),
                int(os.environ.get("NUMBER_START_PURCHASE_ORDER", "1")),
            ),
            "goods_receipt": NumberSeries(
                os.environ.get("NUMBER_PREFIX_GOODS_RECEIPT", "GR-"),
                int(os.environ.get("NUMBER_WIDTH_GOODS_RECEIPT", "5")),
                int(os.environ.get("NUMBER_START_GOODS_RECEIPT", "1")),
            ),
            "supplier_invoice": NumberSeries(
                os.environ.get("NUMBER_PREFIX_SUPPLIER_INVOICE", "PINV-"),
                int(os.environ.get("NUMBER_WIDTH_SUPPLIER_INVOICE", "5")),
                int(os.environ.get("NUMBER_START_SUPPLIER_INVOICE", "1")),
            ),
        }

    def _apply_overrides(
        self, base: dict[str, NumberSeries]
    ) -> dict[str, NumberSeries]:
        """Wendet JSON-Overrides aus ENV an"""
        # NUMBERING_OVERRIDES='{"invoice":{"prefix":"RE-","start":1000,"width":6}}'
        overrides = os.environ.get("NUMBERING_OVERRIDES")
        if overrides:
            try:
                data = json.loads(overrides)
                for k, v in data.items():
                    cur = base.get(k) or NumberSeries(
                        prefix=v.get("prefix", f"{k.upper()}-")
                    )
                    base[k] = NumberSeries(
                        prefix=v.get("prefix", cur.prefix),
                        width=int(v.get("width", cur.width)),
                        start=int(v.get("start", cur.start)),
                        value=int(v.get("value", cur.value)),
                    )
            except Exception as e:
                logger.warning(f"Failed to apply numbering overrides: {e}")
        return base

    def _load(self) -> None:
        """Lädt Nummernkreise aus Datei"""
        if not self.path.exists():
            self._series = self._apply_overrides(self._default_series())
            self._save()
        else:
            raw = json.loads(self.path.read_text())
            self._series = {k: NumberSeries(**v) for k, v in raw.items()}
            # Apply runtime overrides ohne Counter zu verlieren
            self._series = self._apply_overrides(self._series)

    def _save(self) -> None:
        """Speichert Nummernkreise in Datei"""
        self.path.write_text(
            json.dumps({k: vars(v) for k, v in self._series.items()}, indent=2)
        )

    def next_number(self, domain: str) -> str:
        """Generiert nächste Belegnummer (thread-safe)"""
        with self.lock:
            if domain not in self._series:
                self._series[domain] = NumberSeries(
                    prefix=os.environ.get(
                        f"NUMBER_PREFIX_{domain.upper()}", domain.upper() + "-"
                    )
                )
            num = self._series[domain].next()
            self._save()
            logger.info(f"Generated number: {num} for domain: {domain}")
            return num

    def peek(self, domain: str) -> str:
        """Gibt nächste Nummer zurück ohne zu incrementieren"""
        s = self._series.get(domain) or NumberSeries(
            prefix=os.environ.get(f"NUMBER_PREFIX_{domain.upper()}", domain.upper() + "-")
        )
        v = s.value if s.value >= s.start else s.start
        return f"{s.prefix}{v:0{s.width}d}"


# Singleton factory
_numbering_singleton: NumberingService | None = None


def get_numbering() -> NumberingService:
    """Holt globale NumberingService-Instanz"""
    global _numbering_singleton
    if _numbering_singleton is None:
        _numbering_singleton = NumberingService(
            os.environ.get("NUMBERING_STORE", "data/series.json")
        )
    return _numbering_singleton
