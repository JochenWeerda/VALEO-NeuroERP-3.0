"""
Process Timeout Contracts — Wave 48
Timeout-Management für Workflow-Schritte: Fristenüberwachung,
Mahnzyklen und automatische Eskalation bei Zeitüberschreitung.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class TimeoutTyp(str, Enum):
    ABSOLUT = "ABSOLUT"          # Feste Deadline (z.B. 2026-03-31)
    RELATIV = "RELATIV"          # X Minuten ab Erstellung
    GESCHAEFTSZEIT = "GESCHAEFTSZEIT"  # Nur Geschäftszeiten zählen
    SLA_GEBUNDEN = "SLA_GEBUNDEN"      # Aus SLA-Definition abgeleitet


class TimeoutAktion(str, Enum):
    ESKALIEREN = "ESKALIEREN"
    ABBRECHEN = "ABBRECHEN"
    BENACHRICHTIGEN = "BENACHRICHTIGEN"
    AUTOMATISCH_FORTFAHREN = "AUTOMATISCH_FORTFAHREN"


class TimeoutStatus(str, Enum):
    AUSSTEHEND = "AUSSTEHEND"    # Noch innerhalb der Frist
    MAHNPHASE = "MAHNPHASE"      # Warnung ausgelöst (z.B. 80% der Zeit verbraucht)
    ABGELAUFEN = "ABGELAUFEN"    # Timeout überschritten
    AUFGEHOBEN = "AUFGEHOBEN"    # Manuell aufgehoben
    ERLEDIGT = "ERLEDIGT"        # Aufgabe vor Timeout abgeschlossen


# ---------------------------------------------------------------------------
# Timeout-Regel
# ---------------------------------------------------------------------------

@dataclass
class TimeoutRegel:
    """
    Definiert das Timeout-Verhalten für einen Workflow-Schritt.

    `mahngrenze_pct`: Ab welchem Prozentsatz der verbrauchten Zeit die
    Mahnphase beginnt (0–100). Default 80.
    """
    regel_id: str
    schritt_id: str             # Workflow-Schritt-ID oder "*" für alle
    timeout_typ: TimeoutTyp
    timeout_minuten: int        # Dauer; bei ABSOLUT ignoriert
    aktion_bei_timeout: TimeoutAktion
    mahngrenze_pct: int = 80    # Mahnphase ab X% verbrauchter Zeit
    beschreibung: str = ""

    def berechne_deadline(self, erstellt_am: datetime) -> datetime:
        """Berechnet die absolute Deadline ausgehend vom Erstellzeitpunkt."""
        return erstellt_am + timedelta(minutes=self.timeout_minuten)

    def berechne_mahnzeitpunkt(self, erstellt_am: datetime) -> datetime:
        """Berechnet den Zeitpunkt für die Mahnphase."""
        minuten_bis_mahnung = self.timeout_minuten * self.mahngrenze_pct / 100
        return erstellt_am + timedelta(minutes=minuten_bis_mahnung)

    def as_dict(self) -> dict[str, Any]:
        return {
            "regel_id": self.regel_id,
            "schritt_id": self.schritt_id,
            "timeout_typ": self.timeout_typ.value,
            "timeout_minuten": self.timeout_minuten,
            "aktion_bei_timeout": self.aktion_bei_timeout.value,
            "mahngrenze_pct": self.mahngrenze_pct,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Timeout-Prüfung
# ---------------------------------------------------------------------------

@dataclass
class TimeoutPruefung:
    """Ergebnis der Timeout-Auswertung für einen Workflow-Schritt."""
    instanz_id: str
    schritt_id: str
    timeout_status: TimeoutStatus
    aktion: TimeoutAktion | None
    erstellt_am: datetime
    deadline: datetime
    mahnzeitpunkt: datetime
    verbrauchte_minuten: float
    verbleibende_minuten: float
    auslastung_pct: float
    geprueft_am: datetime = field(default_factory=datetime.utcnow)

    @property
    def ist_abgelaufen(self) -> bool:
        return self.timeout_status == TimeoutStatus.ABGELAUFEN

    @property
    def ist_in_mahnphase(self) -> bool:
        return self.timeout_status == TimeoutStatus.MAHNPHASE

    def as_dict(self) -> dict[str, Any]:
        return {
            "instanz_id": self.instanz_id,
            "schritt_id": self.schritt_id,
            "timeout_status": self.timeout_status.value,
            "aktion": self.aktion.value if self.aktion else None,
            "erstellt_am": self.erstellt_am.isoformat(),
            "deadline": self.deadline.isoformat(),
            "mahnzeitpunkt": self.mahnzeitpunkt.isoformat(),
            "verbrauchte_minuten": round(self.verbrauchte_minuten, 2),
            "verbleibende_minuten": round(self.verbleibende_minuten, 2),
            "auslastung_pct": round(self.auslastung_pct, 2),
            "ist_abgelaufen": self.ist_abgelaufen,
            "ist_in_mahnphase": self.ist_in_mahnphase,
            "geprueft_am": self.geprueft_am.isoformat(),
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def pruefe_timeout(
    instanz_id: str,
    schritt_id: str,
    regel: TimeoutRegel,
    erstellt_am: datetime,
    jetzt: datetime | None = None,
) -> TimeoutPruefung:
    """
    Prüft den Timeout-Status einer Workflow-Instanz anhand einer Regel.

    Logik:
    - jetzt >= deadline → ABGELAUFEN, aktion = regel.aktion_bei_timeout
    - jetzt >= mahnzeitpunkt → MAHNPHASE, aktion = BENACHRICHTIGEN
    - sonst → AUSSTEHEND, aktion = None
    """
    ts = jetzt or datetime.utcnow()
    deadline = regel.berechne_deadline(erstellt_am)
    mahnzeitpunkt = regel.berechne_mahnzeitpunkt(erstellt_am)

    verbrauchte = (ts - erstellt_am).total_seconds() / 60
    verbleibende = (deadline - ts).total_seconds() / 60
    auslastung = (verbrauchte / regel.timeout_minuten * 100) if regel.timeout_minuten > 0 else 0.0

    if ts >= deadline:
        status = TimeoutStatus.ABGELAUFEN
        aktion = regel.aktion_bei_timeout
    elif ts >= mahnzeitpunkt:
        status = TimeoutStatus.MAHNPHASE
        aktion = TimeoutAktion.BENACHRICHTIGEN
    else:
        status = TimeoutStatus.AUSSTEHEND
        aktion = None

    return TimeoutPruefung(
        instanz_id=instanz_id,
        schritt_id=schritt_id,
        timeout_status=status,
        aktion=aktion,
        erstellt_am=erstellt_am,
        deadline=deadline,
        mahnzeitpunkt=mahnzeitpunkt,
        verbrauchte_minuten=verbrauchte,
        verbleibende_minuten=verbleibende,
        auslastung_pct=auslastung,
        geprueft_am=ts,
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_timeout_regeln() -> list[TimeoutRegel]:
    """Gibt 5 Standard-Timeout-Regeln zurück."""
    return [
        TimeoutRegel(
            regel_id="TR-001",
            schritt_id="kontrakt_freigabe",
            timeout_typ=TimeoutTyp.RELATIV,
            timeout_minuten=240,
            aktion_bei_timeout=TimeoutAktion.ESKALIEREN,
            mahngrenze_pct=75,
            beschreibung="Kontrakt-Freigabe: 4h, ab 75% eskalieren",
        ),
        TimeoutRegel(
            regel_id="TR-002",
            schritt_id="settlement_freigabe",
            timeout_typ=TimeoutTyp.GESCHAEFTSZEIT,
            timeout_minuten=480,
            aktion_bei_timeout=TimeoutAktion.ESKALIEREN,
            mahngrenze_pct=80,
            beschreibung="Settlement-Freigabe: 1 Geschäftstag, ab 80% eskalieren",
        ),
        TimeoutRegel(
            regel_id="TR-003",
            schritt_id="ap_rechnungseingang",
            timeout_typ=TimeoutTyp.SLA_GEBUNDEN,
            timeout_minuten=2880,
            aktion_bei_timeout=TimeoutAktion.BENACHRICHTIGEN,
            mahngrenze_pct=90,
            beschreibung="AP-Rechnungseingang: 2 Tage SLA, ab 90% mahnen",
        ),
        TimeoutRegel(
            regel_id="TR-004",
            schritt_id="qualitaets_freigabe",
            timeout_typ=TimeoutTyp.RELATIV,
            timeout_minuten=60,
            aktion_bei_timeout=TimeoutAktion.AUTOMATISCH_FORTFAHREN,
            mahngrenze_pct=80,
            beschreibung="Qualitäts-Freigabe: 1h, danach automatisch fortfahren",
        ),
        TimeoutRegel(
            regel_id="TR-005",
            schritt_id="*",
            timeout_typ=TimeoutTyp.RELATIV,
            timeout_minuten=1440,
            aktion_bei_timeout=TimeoutAktion.ABBRECHEN,
            mahngrenze_pct=85,
            beschreibung="Globaler Fallback: 24h, danach abbrechen",
        ),
    ]
