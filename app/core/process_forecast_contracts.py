from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta


class PrognoseTyp(str, Enum):
    LAST = "LAST"                   # Load forecast
    DURCHLAUFZEIT = "DURCHLAUFZEIT" # Throughput time
    FEHLERRATE = "FEHLERRATE"       # Error rate
    KAPAZITAET = "KAPAZITAET"       # Capacity needed


class PrognoseMethode(str, Enum):
    GLEITENDER_DURCHSCHNITT = "GLEITENDER_DURCHSCHNITT"
    GEWICHTETER_DURCHSCHNITT = "GEWICHTETER_DURCHSCHNITT"
    LINEARE_REGRESSION = "LINEARE_REGRESSION"
    SAISONBEREINIGT = "SAISONBEREINIGT"


class KonfidenzNiveau(str, Enum):
    NIEDRIG = "NIEDRIG"     # < 60%
    MITTEL = "MITTEL"       # 60–80%
    HOCH = "HOCH"           # > 80%


@dataclass
class Datenpunkt:
    zeitstempel: datetime
    wert: float


@dataclass
class PrognoseErgebnis:
    prognose_id: str
    prognose_typ: PrognoseTyp
    methode: PrognoseMethode
    prognostizierter_wert: float
    konfidenz_pct: float
    prognose_zeitraum_stunden: int
    erstellt_am: datetime = field(default_factory=datetime.utcnow)

    @property
    def konfidenz_niveau(self) -> KonfidenzNiveau:
        if self.konfidenz_pct > 80:
            return KonfidenzNiveau.HOCH
        elif self.konfidenz_pct >= 60:
            return KonfidenzNiveau.MITTEL
        return KonfidenzNiveau.NIEDRIG


def berechne_gleitenden_durchschnitt(datenpunkte: list, fenster: int) -> float:
    """
    Calculates moving average of last `fenster` values.
    Returns 0.0 for empty list or fenster <= 0.
    If len(datenpunkte) < fenster, uses all available points.
    """
    if not datenpunkte or fenster <= 0:
        return 0.0
    werte = [d.wert for d in sorted(datenpunkte, key=lambda d: d.zeitstempel)]
    relevante = werte[-fenster:] if len(werte) >= fenster else werte
    return sum(relevante) / len(relevante)


def berechne_gewichteten_durchschnitt(datenpunkte: list) -> float:
    """
    Weighted average where more recent points get higher weight.
    Weight = position index (1-based, latest has highest weight).
    Returns 0.0 for empty list.
    """
    if not datenpunkte:
        return 0.0
    sortiert = sorted(datenpunkte, key=lambda d: d.zeitstempel)
    gesamt_gewicht = sum(i + 1 for i in range(len(sortiert)))
    if gesamt_gewicht == 0:
        return 0.0
    return sum((i + 1) * d.wert for i, d in enumerate(sortiert)) / gesamt_gewicht


def erstelle_prognose(
    prognose_id: str,
    prognose_typ: PrognoseTyp,
    methode: PrognoseMethode,
    datenpunkte: list,
    prognose_zeitraum_stunden: int,
    konfidenz_pct: float,
) -> PrognoseErgebnis:
    """Creates forecast using the specified method."""
    if methode == PrognoseMethode.GLEITENDER_DURCHSCHNITT:
        wert = berechne_gleitenden_durchschnitt(datenpunkte, 3)
    elif methode == PrognoseMethode.GEWICHTETER_DURCHSCHNITT:
        wert = berechne_gewichteten_durchschnitt(datenpunkte)
    else:
        wert = berechne_gleitenden_durchschnitt(datenpunkte, len(datenpunkte) or 1)
    return PrognoseErgebnis(
        prognose_id=prognose_id,
        prognose_typ=prognose_typ,
        methode=methode,
        prognostizierter_wert=wert,
        konfidenz_pct=konfidenz_pct,
        prognose_zeitraum_stunden=prognose_zeitraum_stunden,
    )


def get_default_prognosen() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)
    punkte = [
        Datenpunkt(now - timedelta(hours=5), 80.0),
        Datenpunkt(now - timedelta(hours=4), 95.0),
        Datenpunkt(now - timedelta(hours=3), 110.0),
        Datenpunkt(now - timedelta(hours=2), 105.0),
        Datenpunkt(now - timedelta(hours=1), 120.0),
    ]
    return [
        erstelle_prognose("PG-001", PrognoseTyp.LAST, PrognoseMethode.GLEITENDER_DURCHSCHNITT, punkte, 4, 75.0),
        erstelle_prognose("PG-002", PrognoseTyp.DURCHLAUFZEIT, PrognoseMethode.GEWICHTETER_DURCHSCHNITT, punkte, 8, 85.0),
        erstelle_prognose("PG-003", PrognoseTyp.FEHLERRATE, PrognoseMethode.GLEITENDER_DURCHSCHNITT, punkte[:2], 24, 55.0),
        erstelle_prognose("PG-004", PrognoseTyp.KAPAZITAET, PrognoseMethode.GEWICHTETER_DURCHSCHNITT, [], 12, 40.0),
    ]
