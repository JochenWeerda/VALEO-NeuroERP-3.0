"""
dashboard_read_model_contracts.py — Read-Models für Dashboards (Wave 83, Gap 033)

Pre-aggregierte Dashboard-Snapshots statt teurer Live-Joins auf jede Anfrage.
Ziel: p95 Dashboard-API < 250ms durch vorberechnete Read-Models.

Gap 033: Read-Models für Dashboards statt teurer Live-Joins
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ReadModelFreshness(str, Enum):
    """Aktualitätszustand eines Read-Models."""
    FRISCH      = "FRISCH"      # Jünger als max_alter_sekunden
    VERALTET    = "VERALTET"    # Älter als max_alter_sekunden, aber vorhanden
    LEER        = "LEER"        # Noch kein Snapshot vorhanden
    WIRD_GEBAUT = "WIRD_GEBAUT" # Snapshot wird gerade erzeugt


class DashboardTyp(str, Enum):
    """Typ des Dashboards."""
    CONTROLLING     = "CONTROLLING"   # KPIs, Umsatz, Marge
    AGRAR           = "AGRAR"         # Ernte, Lagerbestand, Kampagne
    FINANCE         = "FINANCE"       # Zahlungsläufe, OP, Konten
    LOGISTIK        = "LOGISTIK"      # Lieferkette, Fahrzeuge, ETA
    COMPLIANCE      = "COMPLIANCE"    # GoBD, Intrastat, Fristen
    OPERATIONS      = "OPERATIONS"    # Prozess-SLA, Queue-Länge


# ---------------------------------------------------------------------------
# KPI-Tile im Dashboard
# ---------------------------------------------------------------------------

@dataclass
class DashboardKpiTile:
    """
    Eine einzelne KPI-Kachel im Dashboard-Read-Model.

    Enthält bereits berechneten Wert, Ampel und Trend —
    kein Join zur Laufzeit nötig.
    """
    kpi_code: str
    titel: str
    wert: float | None
    einheit: str
    ampel: str              # "GRUEN" | "GELB" | "ROT" | "UNBEKANNT"
    trend: str              # "STEIGEND" | "FALLEND" | "STABIL" | "UNBEKANNT"
    veraenderung_pct: float | None = None   # vs. Vorperiode
    zielwert: float | None = None
    periode: str = ""

    def as_dict(self) -> dict:
        return {
            "kpi_code": self.kpi_code,
            "titel": self.titel,
            "wert": self.wert,
            "einheit": self.einheit,
            "ampel": self.ampel,
            "trend": self.trend,
            "veraenderung_pct": self.veraenderung_pct,
            "zielwert": self.zielwert,
            "periode": self.periode,
        }


# ---------------------------------------------------------------------------
# Dashboard Snapshot
# ---------------------------------------------------------------------------

@dataclass
class DashboardSnapshot:
    """
    Vollständiger, vorberechneter Dashboard-Zustand.

    Wird beim Build (Hintergrundjob oder Event-Trigger) einmal erzeugt
    und dann direkt ausgeliefert — kein DB-Join zur Laufzeit.
    """
    snapshot_id: str
    tenant_id: str
    dashboard_typ: DashboardTyp
    kpi_tiles: list[DashboardKpiTile]
    erstellt_am: datetime
    gueltig_bis: datetime | None = None     # None = kein Ablauf
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: int = 1

    @property
    def alter_sekunden(self) -> float:
        jetzt = datetime.now(timezone.utc)
        erstellt = self.erstellt_am
        if erstellt.tzinfo is None:
            erstellt = erstellt.replace(tzinfo=timezone.utc)
        return (jetzt - erstellt).total_seconds()

    @property
    def anzahl_tiles(self) -> int:
        return len(self.kpi_tiles)

    @property
    def tiles_gruen(self) -> int:
        return sum(1 for t in self.kpi_tiles if t.ampel == "GRUEN")

    @property
    def tiles_rot(self) -> int:
        return sum(1 for t in self.kpi_tiles if t.ampel == "ROT")

    def get_tile(self, kpi_code: str) -> DashboardKpiTile | None:
        return next((t for t in self.kpi_tiles if t.kpi_code == kpi_code), None)

    def freshness(self, max_alter_sekunden: int = 300) -> ReadModelFreshness:
        if not self.kpi_tiles:
            return ReadModelFreshness.LEER
        if self.alter_sekunden <= max_alter_sekunden:
            return ReadModelFreshness.FRISCH
        return ReadModelFreshness.VERALTET

    def as_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "tenant_id": self.tenant_id,
            "dashboard_typ": self.dashboard_typ.value,
            "kpi_tiles": [t.as_dict() for t in self.kpi_tiles],
            "erstellt_am": self.erstellt_am.isoformat(),
            "alter_sekunden": round(self.alter_sekunden, 1),
            "anzahl_tiles": self.anzahl_tiles,
            "tiles_gruen": self.tiles_gruen,
            "tiles_rot": self.tiles_rot,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Read-Model Store (In-Memory, wird in Produktion durch Redis ersetzt)
# ---------------------------------------------------------------------------

@dataclass
class DashboardReadModelStore:
    """
    In-Memory Store für Dashboard-Snapshots.

    In Produktion durch Redis-backed Store ersetzt.
    API ist identisch — kein App-Code-Umbau nötig.
    """
    _store: dict[str, DashboardSnapshot] = field(default_factory=dict)

    def _key(self, tenant_id: str, dashboard_typ: DashboardTyp) -> str:
        return f"{tenant_id}::{dashboard_typ.value}"

    def put(self, snapshot: DashboardSnapshot) -> None:
        key = self._key(snapshot.tenant_id, snapshot.dashboard_typ)
        self._store[key] = snapshot

    def get(
        self,
        tenant_id: str,
        dashboard_typ: DashboardTyp,
        max_alter_sekunden: int = 300,
    ) -> DashboardSnapshot | None:
        """
        Gibt Snapshot zurück wenn vorhanden und frisch genug.
        Gibt None zurück wenn nicht vorhanden oder zu alt.
        """
        key = self._key(tenant_id, dashboard_typ)
        snap = self._store.get(key)
        if snap is None:
            return None
        if snap.freshness(max_alter_sekunden) == ReadModelFreshness.VERALTET:
            return None
        return snap

    def get_or_stale(
        self,
        tenant_id: str,
        dashboard_typ: DashboardTyp,
    ) -> tuple[DashboardSnapshot | None, ReadModelFreshness]:
        """
        Gibt Snapshot + Freshness-Status zurück — auch veraltete Snapshots.
        Nützlich für "stale-while-revalidate"-Muster.
        """
        key = self._key(tenant_id, dashboard_typ)
        snap = self._store.get(key)
        if snap is None:
            return None, ReadModelFreshness.LEER
        freshness = snap.freshness()
        return snap, freshness

    def invalidate(self, tenant_id: str, dashboard_typ: DashboardTyp) -> bool:
        key = self._key(tenant_id, dashboard_typ)
        if key in self._store:
            del self._store[key]
            return True
        return False

    def invalidate_tenant(self, tenant_id: str) -> int:
        keys = [k for k in self._store if k.startswith(f"{tenant_id}::")]
        for k in keys:
            del self._store[k]
        return len(keys)

    @property
    def size(self) -> int:
        return len(self._store)


# ---------------------------------------------------------------------------
# Read-Model Builder Contract
# ---------------------------------------------------------------------------

@dataclass
class ReadModelBuildJob:
    """
    Auftrag zum (Neu-)Aufbau eines Dashboard-Read-Models.

    Wird von Event-Triggers oder dem Scheduler erzeugt.
    """
    job_id: str
    tenant_id: str
    dashboard_typ: DashboardTyp
    ausgeloest_durch: str       # z.B. "SETTLEMENT_ABGESCHLOSSEN", "SCHEDULER_5MIN"
    erstellt_am: datetime
    prioritaet: int = 2         # 1 = hoch, 5 = niedrig
    versuche: int = 0

    def __post_init__(self) -> None:
        if not (1 <= self.prioritaet <= 5):
            raise ValueError(f"Prioritaet muss 1-5 sein, nicht {self.prioritaet}")

    def as_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "tenant_id": self.tenant_id,
            "dashboard_typ": self.dashboard_typ.value,
            "ausgeloest_durch": self.ausgeloest_durch,
            "erstellt_am": self.erstellt_am.isoformat(),
            "prioritaet": self.prioritaet,
            "versuche": self.versuche,
        }


# ---------------------------------------------------------------------------
# Performance-Contract
# ---------------------------------------------------------------------------

@dataclass
class DashboardPerformanceContract:
    """
    Messe und bewerte ob das Dashboard-API das p95 < 250ms Ziel einhält.
    """
    p95_ziel_ms: float = 250.0
    gemessene_p95_ms: float = 0.0
    stichproben: int = 0

    @property
    def kpi_erfuellt(self) -> bool:
        return self.gemessene_p95_ms <= self.p95_ziel_ms and self.stichproben > 0

    @property
    def headroom_ms(self) -> float:
        return self.p95_ziel_ms - self.gemessene_p95_ms

    def as_dict(self) -> dict:
        return {
            "p95_ziel_ms": self.p95_ziel_ms,
            "gemessene_p95_ms": self.gemessene_p95_ms,
            "stichproben": self.stichproben,
            "kpi_erfuellt": self.kpi_erfuellt,
            "headroom_ms": self.headroom_ms,
        }
