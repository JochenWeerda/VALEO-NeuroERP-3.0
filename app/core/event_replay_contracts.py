"""
Event Replay Contracts — Wave 41
Steuerung von Event-Replay-Aufträgen, Cursor-Tracking, Snapshot-Management
und Konsistenzprüfung für den Process-Kernel Event-Store.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class ReplayStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"
    LAUFEND = "LAUFEND"
    PAUSIERT = "PAUSIERT"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    ABGEBROCHEN = "ABGEBROCHEN"


class ReplayModus(str, Enum):
    VOLLSTAENDIG = "VOLLSTAENDIG"          # Replay aller Events ab Position 0
    TEILWEISE = "TEILWEISE"                # Replay eines Positionsbereichs
    SNAPSHOT_BASIERT = "SNAPSHOT_BASIERT"  # Replay ab letztem Snapshot
    DELTA = "DELTA"                        # Nur neue Events seit Cursor-Position


class SnapshotTyp(str, Enum):
    VOLL = "VOLL"                  # Vollständiger Aggregat-Zustand
    INKREMENTELL = "INKREMENTELL"  # Delta seit letztem Snapshot
    CHECKPOINT = "CHECKPOINT"      # Kontrollpunkt für Replay-Wiederaufnahme


# ---------------------------------------------------------------------------
# Replay-Auftrag
# ---------------------------------------------------------------------------

@dataclass
class EventReplayAuftrag:
    """Steuert einen Event-Replay-Prozess für einen Stream."""
    auftrag_id: str
    tenant_id: str
    stream_id: str
    modus: ReplayModus
    status: ReplayStatus
    von_position: int = 0            # Startposition (inklusiv)
    bis_position: int | None = None  # Endposition (inklusiv); None = bis Ende
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    gestartet_am: datetime | None = None
    abgeschlossen_am: datetime | None = None
    fehler_nachricht: str = ""
    verarbeitete_ereignisse: int = 0

    @property
    def ist_abgeschlossen(self) -> bool:
        return self.status in {
            ReplayStatus.ABGESCHLOSSEN,
            ReplayStatus.FEHLGESCHLAGEN,
            ReplayStatus.ABGEBROCHEN,
        }

    @property
    def dauer_sekunden(self) -> float | None:
        """Gesamtdauer in Sekunden; None wenn noch nicht beendet oder gestartet."""
        if self.gestartet_am is None or self.abgeschlossen_am is None:
            return None
        delta = self.abgeschlossen_am - self.gestartet_am
        return round(delta.total_seconds(), 3)

    @property
    def durchsatz_pro_sekunde(self) -> float | None:
        """Verarbeitete Ereignisse pro Sekunde; None wenn Dauer nicht verfügbar."""
        dauer = self.dauer_sekunden
        if dauer is None or dauer <= 0:
            return None
        return round(self.verarbeitete_ereignisse / dauer, 2)

    def as_dict(self) -> dict[str, Any]:
        return {
            "auftrag_id": self.auftrag_id,
            "tenant_id": self.tenant_id,
            "stream_id": self.stream_id,
            "modus": self.modus.value,
            "status": self.status.value,
            "von_position": self.von_position,
            "bis_position": self.bis_position,
            "erstellt_am": self.erstellt_am.isoformat(),
            "gestartet_am": self.gestartet_am.isoformat() if self.gestartet_am else None,
            "abgeschlossen_am": self.abgeschlossen_am.isoformat() if self.abgeschlossen_am else None,
            "fehler_nachricht": self.fehler_nachricht,
            "verarbeitete_ereignisse": self.verarbeitete_ereignisse,
            "ist_abgeschlossen": self.ist_abgeschlossen,
            "dauer_sekunden": self.dauer_sekunden,
            "durchsatz_pro_sekunde": self.durchsatz_pro_sekunde,
        }


# ---------------------------------------------------------------------------
# Replay-Cursor
# ---------------------------------------------------------------------------

@dataclass
class ReplayCursor:
    """Verfolgt die aktuelle Leseposition eines Verbrauchers im Event-Stream."""
    cursor_id: str
    tenant_id: str
    stream_id: str
    aktuelle_position: int
    letzte_aktualisierung: datetime
    verbraucher_id: str   # z.B. "projection:settlement" oder "agent:kontrakt"

    def as_dict(self) -> dict[str, Any]:
        return {
            "cursor_id": self.cursor_id,
            "tenant_id": self.tenant_id,
            "stream_id": self.stream_id,
            "aktuelle_position": self.aktuelle_position,
            "letzte_aktualisierung": self.letzte_aktualisierung.isoformat(),
            "verbraucher_id": self.verbraucher_id,
        }


# ---------------------------------------------------------------------------
# Event-Snapshot
# ---------------------------------------------------------------------------

@dataclass
class EventSnapshot:
    """Gespeicherter Aggregat-Zustand zu einem bestimmten Stream-Zeitpunkt."""
    snapshot_id: str
    tenant_id: str
    stream_id: str
    position: int                 # Stream-Position des Snapshots
    snapshot_typ: SnapshotTyp
    erstellt_am: datetime
    aggregat_zustand: dict[str, Any] = field(default_factory=dict)

    @property
    def alter_stunden(self) -> float:
        """Alter des Snapshots in Stunden seit Erstellung."""
        delta = datetime.utcnow() - self.erstellt_am
        return round(delta.total_seconds() / 3600, 3)

    def as_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "tenant_id": self.tenant_id,
            "stream_id": self.stream_id,
            "position": self.position,
            "snapshot_typ": self.snapshot_typ.value,
            "erstellt_am": self.erstellt_am.isoformat(),
            "alter_stunden": self.alter_stunden,
            "aggregat_zustand_groesse": len(self.aggregat_zustand),
        }


# ---------------------------------------------------------------------------
# Konsistenzprüfung
# ---------------------------------------------------------------------------

@dataclass
class ReplayKonsistenzPruefung:
    """Ergebnis der Konsistenzprüfung eines Event-Streams in einem Positionsbereich."""
    pruefung_id: str
    stream_id: str
    von_position: int
    bis_position: int
    ist_konsistent: bool
    luecken: list[int] = field(default_factory=list)     # Fehlende Positionen
    duplikate: list[int] = field(default_factory=list)   # Doppelt vorhandene Positionen

    @property
    def hat_probleme(self) -> bool:
        return not self.ist_konsistent or len(self.luecken) > 0 or len(self.duplikate) > 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "pruefung_id": self.pruefung_id,
            "stream_id": self.stream_id,
            "von_position": self.von_position,
            "bis_position": self.bis_position,
            "ist_konsistent": self.ist_konsistent,
            "luecken": self.luecken,
            "duplikate": self.duplikate,
            "hat_probleme": self.hat_probleme,
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def pruefe_replay_konsistenz(
    pruefung_id: str,
    stream_id: str,
    positionen: list[int],
) -> ReplayKonsistenzPruefung:
    """
    Prüft ob eine sortierte Folge von Event-Positionen lückenlos und duplikatfrei ist.

    - Lücken: fehlende Positionen im Bereich [min, max]
    - Duplikate: Positionen, die mehr als einmal vorkommen
    - ist_konsistent: keine Lücken und keine Duplikate
    """
    if not positionen:
        return ReplayKonsistenzPruefung(
            pruefung_id=pruefung_id,
            stream_id=stream_id,
            von_position=0,
            bis_position=0,
            ist_konsistent=True,
            luecken=[],
            duplikate=[],
        )

    sortiert = sorted(positionen)
    von = sortiert[0]
    bis = sortiert[-1]

    # Duplikate: Positionen mit count > 1
    from collections import Counter
    zaehler = Counter(positionen)
    duplikate = sorted(p for p, c in zaehler.items() if c > 1)

    # Lücken: fehlende Positionen zwischen von und bis
    erwartete = set(range(von, bis + 1))
    vorhandene = set(positionen)
    luecken = sorted(erwartete - vorhandene)

    konsistent = len(luecken) == 0 and len(duplikate) == 0

    return ReplayKonsistenzPruefung(
        pruefung_id=pruefung_id,
        stream_id=stream_id,
        von_position=von,
        bis_position=bis,
        ist_konsistent=konsistent,
        luecken=luecken,
        duplikate=duplikate,
    )


def erstelle_replay_auftrag(
    auftrag_id: str,
    tenant_id: str,
    stream_id: str,
    modus: ReplayModus,
    von_position: int = 0,
    bis_position: int | None = None,
    erstellt_am: datetime | None = None,
) -> EventReplayAuftrag:
    """Erstellt einen neuen Replay-Auftrag mit Status AUSSTEHEND."""
    return EventReplayAuftrag(
        auftrag_id=auftrag_id,
        tenant_id=tenant_id,
        stream_id=stream_id,
        modus=modus,
        status=ReplayStatus.AUSSTEHEND,
        von_position=von_position,
        bis_position=bis_position,
        erstellt_am=erstellt_am or datetime.utcnow(),
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_replay_auftraege(
    tenant_id: str = "TENANT-001",
) -> list[EventReplayAuftrag]:
    """Gibt 3 Beispiel-Replay-Aufträge zurück."""
    basis = datetime(2026, 3, 10, 6, 0)
    return [
        EventReplayAuftrag(
            auftrag_id="RA-001",
            tenant_id=tenant_id,
            stream_id="kontrakt-annahme-stream",
            modus=ReplayModus.VOLLSTAENDIG,
            status=ReplayStatus.ABGESCHLOSSEN,
            von_position=0,
            bis_position=None,
            erstellt_am=basis,
            gestartet_am=basis.replace(hour=6, minute=5),
            abgeschlossen_am=basis.replace(hour=6, minute=47),
            verarbeitete_ereignisse=3820,
        ),
        EventReplayAuftrag(
            auftrag_id="RA-002",
            tenant_id=tenant_id,
            stream_id="settlement-stream",
            modus=ReplayModus.SNAPSHOT_BASIERT,
            status=ReplayStatus.LAUFEND,
            von_position=1500,
            bis_position=None,
            erstellt_am=basis.replace(hour=8, minute=0),
            gestartet_am=basis.replace(hour=8, minute=2),
            verarbeitete_ereignisse=240,
        ),
        EventReplayAuftrag(
            auftrag_id="RA-003",
            tenant_id=tenant_id,
            stream_id="ap-approval-stream",
            modus=ReplayModus.DELTA,
            status=ReplayStatus.AUSSTEHEND,
            von_position=800,
            bis_position=950,
            erstellt_am=basis.replace(hour=9, minute=30),
        ),
    ]
