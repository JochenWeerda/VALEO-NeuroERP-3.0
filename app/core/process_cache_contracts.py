"""
Process Cache Contracts — Wave 67
Pure Python, no app/api imports.
"""
from enum import Enum
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional, Any, List


class CacheStrategie(Enum):
    LRU = "LRU"                      # Least Recently Used eviction
    TTL = "TTL"                      # Time-To-Live expiration
    WRITE_THROUGH = "WRITE_THROUGH"  # Write to cache + backing store simultaneously
    WRITE_BACK = "WRITE_BACK"        # Write to cache, flush later


class CacheStatus(Enum):
    TREFFER = "TREFFER"            # Cache hit
    VERFEHLT = "VERFEHLT"          # Cache miss
    VERALTET = "VERALTET"          # Stale (TTL expired but not yet evicted)
    INVALIDIERT = "INVALIDIERT"    # Explicitly invalidated


@dataclass
class CacheEintrag:
    schluessel: str
    wert: Any
    erstellt_am: datetime
    letzter_zugriff: datetime
    ttl_sekunden: Optional[int]  # None = no expiry
    zugriffe: int = 0
    tags: List[str] = field(default_factory=list)  # for tag-based invalidation

    def status(self, jetzt: datetime) -> CacheStatus:
        """Returns VERALTET if TTL expired, TREFFER otherwise."""
        if self.ttl_sekunden is not None:
            alter = (jetzt - self.erstellt_am).total_seconds()
            if alter > self.ttl_sekunden:
                return CacheStatus.VERALTET
        return CacheStatus.TREFFER

    def aktualisiere_zugriff(self, jetzt: datetime) -> "CacheEintrag":
        return replace(self, letzter_zugriff=jetzt, zugriffe=self.zugriffe + 1)


@dataclass
class CacheKonfiguration:
    name: str
    max_eintraege: int
    default_ttl_sekunden: Optional[int]
    strategie: CacheStrategie


@dataclass
class CacheStatistik:
    treffer: int
    verfehlt: int
    invalidierungen: int
    evictions: int

    def trefferquote_pct(self) -> float:
        gesamt = self.treffer + self.verfehlt
        if gesamt == 0:
            return 0.0
        return round(self.treffer / gesamt * 100, 2)


@dataclass
class CacheInvalidierungsRegel:
    regel_id: str
    tags: List[str]  # invalidate all entries with any of these tags
    muster: Optional[str] = None  # key prefix pattern
    beschreibung: str = ""

    def trifft_zu(self, eintrag: CacheEintrag) -> bool:
        """Returns True if entry should be invalidated by this rule."""
        # Check tag overlap
        for tag in self.tags:
            if tag in eintrag.tags:
                return True
        # Check key prefix
        if self.muster and eintrag.schluessel.startswith(self.muster):
            return True
        return False


# 5 default cache configurations
CACHE_REGELN = [
    CacheKonfiguration("Prozessdaten-Cache", max_eintraege=1000, default_ttl_sekunden=300, strategie=CacheStrategie.TTL),
    CacheKonfiguration("Stammdaten-Cache", max_eintraege=500, default_ttl_sekunden=None, strategie=CacheStrategie.LRU),
    CacheKonfiguration("Echtzeit-Cache", max_eintraege=100, default_ttl_sekunden=60, strategie=CacheStrategie.WRITE_THROUGH),
    CacheKonfiguration("Bericht-Cache", max_eintraege=2000, default_ttl_sekunden=3600, strategie=CacheStrategie.WRITE_BACK),
    CacheKonfiguration("Session-Cache", max_eintraege=200, default_ttl_sekunden=900, strategie=CacheStrategie.TTL),
]
