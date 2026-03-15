"""
Branchenbenchmarking-Cockpit — Wave 38, Gap 047
Kennzahlenvergleich je Genossenschaft, Branchendurchschnitt,
Perzentil-Ranking und monatliche Benchmark-Reports.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class BenchmarkKategorie(str, Enum):
    LOGISTIK = "LOGISTIK"
    FINANZEN = "FINANZEN"
    AGRAR = "AGRAR"
    NACHHALTIGKEIT = "NACHHALTIGKEIT"
    QUALITAET = "QUALITAET"
    KUNDENZUFRIEDENHEIT = "KUNDENZUFRIEDENHEIT"


class PerzentilStufe(str, Enum):
    TOP_10 = "TOP_10"        # >= 90. Perzentil
    TOP_25 = "TOP_25"        # >= 75. Perzentil
    MITTELFELD = "MITTELFELD"  # 25.–74. Perzentil
    UNTERES_VIERTEL = "UNTERES_VIERTEL"  # < 25. Perzentil


class BenchmarkTrend(str, Enum):
    STARK_VERBESSERND = "STARK_VERBESSERND"   # > +5 %
    VERBESSERND = "VERBESSERND"               # +1 – +5 %
    STABIL = "STABIL"                          # -1 – +1 %
    VERSCHLECHTERND = "VERSCHLECHTERND"        # -1 – -5 %
    STARK_VERSCHLECHTERND = "STARK_VERSCHLECHTERND"  # < -5 %


class ReportFrequenz(str, Enum):
    MONATLICH = "MONATLICH"
    QUARTAL = "QUARTAL"
    JAEHRLICH = "JAEHRLICH"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkKennzahl:
    """Eine einzelne Benchmark-Kennzahl mit Branchenwert und Eigenposition."""
    kennzahl_id: str
    bezeichnung: str
    kategorie: BenchmarkKategorie
    eigenwert: float
    einheit: str
    branche_mittelwert: float
    branche_p25: float    # 25. Perzentil (schlechteres Viertel)
    branche_p75: float    # 75. Perzentil (oberes Viertel)
    branche_p90: float    # 90. Perzentil (Top 10 %)
    hoeher_ist_besser: bool = True   # False für Kosten, CO2 etc.

    @property
    def abweichung_vom_mittel_pct(self) -> float:
        """Prozentuale Abweichung vom Branchenmittel."""
        if self.branche_mittelwert == 0:
            return 0.0
        return (self.eigenwert - self.branche_mittelwert) / self.branche_mittelwert * 100.0

    @property
    def perzentil_stufe(self) -> PerzentilStufe:
        """Einordnung ins Branchenperzentil."""
        if self.hoeher_ist_besser:
            if self.eigenwert >= self.branche_p90:
                return PerzentilStufe.TOP_10
            if self.eigenwert >= self.branche_p75:
                return PerzentilStufe.TOP_25
            if self.eigenwert >= self.branche_p25:
                return PerzentilStufe.MITTELFELD
            return PerzentilStufe.UNTERES_VIERTEL
        else:
            # Niedrigerer Wert = besser (Kosten, CO2, Fehlerquoten)
            if self.eigenwert <= self.branche_p90:
                return PerzentilStufe.TOP_10
            if self.eigenwert <= self.branche_p75:
                return PerzentilStufe.TOP_25
            if self.eigenwert <= self.branche_p25:
                return PerzentilStufe.MITTELFELD
            return PerzentilStufe.UNTERES_VIERTEL

    def as_dict(self) -> dict[str, Any]:
        return {
            "kennzahl_id": self.kennzahl_id,
            "bezeichnung": self.bezeichnung,
            "kategorie": self.kategorie.value,
            "eigenwert": round(self.eigenwert, 4),
            "einheit": self.einheit,
            "branche_mittelwert": round(self.branche_mittelwert, 4),
            "branche_p25": round(self.branche_p25, 4),
            "branche_p75": round(self.branche_p75, 4),
            "branche_p90": round(self.branche_p90, 4),
            "hoeher_ist_besser": self.hoeher_ist_besser,
            "abweichung_vom_mittel_pct": round(self.abweichung_vom_mittel_pct, 2),
            "perzentil_stufe": self.perzentil_stufe.value,
        }


@dataclass
class BenchmarkTrendPunkt:
    """Ein Datenpunkt in einer Trend-Zeitreihe."""
    periode: str    # z.B. "2026-Q1", "2026-03"
    wert: float
    branche_mittelwert: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "periode": self.periode,
            "wert": round(self.wert, 4),
            "branche_mittelwert": round(self.branche_mittelwert, 4),
        }


@dataclass
class BenchmarkReport:
    """Vollständiger Benchmark-Report für eine Genossenschaft."""
    report_id: str
    tenant_id: str
    genossenschaft_name: str
    berichtsmonat: date
    frequenz: ReportFrequenz
    kennzahlen: list[BenchmarkKennzahl]
    trend_daten: dict[str, list[BenchmarkTrendPunkt]] = field(default_factory=dict)
    kommentar: str = ""

    @property
    def top10_kennzahlen(self) -> list[BenchmarkKennzahl]:
        return [k for k in self.kennzahlen if k.perzentil_stufe == PerzentilStufe.TOP_10]

    @property
    def verbesserungspotenzial(self) -> list[BenchmarkKennzahl]:
        return [k for k in self.kennzahlen if k.perzentil_stufe == PerzentilStufe.UNTERES_VIERTEL]

    @property
    def gesamtbewertung_score(self) -> float:
        """
        Durchschnittlicher Benchmark-Score [0–100].
        TOP_10=95, TOP_25=75, MITTELFELD=50, UNTERES_VIERTEL=20
        """
        if not self.kennzahlen:
            return 0.0
        _PUNKTE = {
            PerzentilStufe.TOP_10: 95.0,
            PerzentilStufe.TOP_25: 75.0,
            PerzentilStufe.MITTELFELD: 50.0,
            PerzentilStufe.UNTERES_VIERTEL: 20.0,
        }
        return sum(_PUNKTE[k.perzentil_stufe] for k in self.kennzahlen) / len(self.kennzahlen)

    def as_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "tenant_id": self.tenant_id,
            "genossenschaft_name": self.genossenschaft_name,
            "berichtsmonat": self.berichtsmonat.isoformat(),
            "frequenz": self.frequenz.value,
            "kennzahlen_anzahl": len(self.kennzahlen),
            "gesamtbewertung_score": round(self.gesamtbewertung_score, 2),
            "top10_anzahl": len(self.top10_kennzahlen),
            "verbesserungspotenzial_anzahl": len(self.verbesserungspotenzial),
            "kennzahlen": [k.as_dict() for k in self.kennzahlen],
            "trend_daten": {
                kid: [p.as_dict() for p in punkte]
                for kid, punkte in self.trend_daten.items()
            },
            "kommentar": self.kommentar,
        }


# ---------------------------------------------------------------------------
# Trend-Berechnung
# ---------------------------------------------------------------------------

def berechne_trend(werte: list[float]) -> BenchmarkTrend:
    """
    Berechnet den Trend aus einer Zeitreihe von Werten (ältester zuerst).

    Vergleicht letzten Wert mit Durchschnitt der ersten 2/3 der Reihe.
    Veränderung > +5 % → STARK_VERBESSERND usw.
    Mindestlänge: 2 Werte.
    """
    if len(werte) < 2:
        return BenchmarkTrend.STABIL

    n_basis = max(1, len(werte) * 2 // 3)
    basis = werte[:n_basis]
    basis_avg = sum(basis) / len(basis)
    aktuell = werte[-1]

    if basis_avg == 0:
        return BenchmarkTrend.STABIL

    veraenderung_pct = (aktuell - basis_avg) / abs(basis_avg) * 100.0

    if veraenderung_pct > 5.0:
        return BenchmarkTrend.STARK_VERBESSERND
    if veraenderung_pct > 1.0:
        return BenchmarkTrend.VERBESSERND
    if veraenderung_pct >= -1.0:
        return BenchmarkTrend.STABIL
    if veraenderung_pct >= -5.0:
        return BenchmarkTrend.VERSCHLECHTERND
    return BenchmarkTrend.STARK_VERSCHLECHTERND


def berechne_branchenperzentile(werte: list[float]) -> dict[str, float]:
    """
    Berechnet Branchenperzentile aus einer Verteilung.

    Gibt p25, p50 (Median), p75, p90, Mittelwert zurück.
    Mindestens 2 Werte erforderlich.
    """
    if not werte:
        raise ValueError("Werte-Liste darf nicht leer sein")
    if len(werte) < 2:
        wert = werte[0]
        return {"p25": wert, "p50": wert, "p75": wert, "p90": wert, "mittelwert": wert}

    sortiert = sorted(werte)
    n = len(sortiert)

    def perzentil(p: float) -> float:
        idx = p / 100.0 * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        frac = idx - lo
        return sortiert[lo] * (1 - frac) + sortiert[hi] * frac

    return {
        "p25": round(perzentil(25), 4),
        "p50": round(perzentil(50), 4),
        "p75": round(perzentil(75), 4),
        "p90": round(perzentil(90), 4),
        "mittelwert": round(sum(werte) / n, 4),
    }


# ---------------------------------------------------------------------------
# Beispieldaten
# ---------------------------------------------------------------------------

def get_example_benchmark_report(
    tenant_id: str = "TENANT-001",
    genossenschaft_name: str = "Agrargenossenschaft Muster eG",
) -> BenchmarkReport:
    """Gibt einen Beispiel-Benchmark-Report zurück."""
    kennzahlen = [
        BenchmarkKennzahl(
            "BK-001", "Umschlagsgeschwindigkeit Getreide", BenchmarkKategorie.LOGISTIK,
            eigenwert=8.2, einheit="t/h",
            branche_mittelwert=7.0, branche_p25=5.5, branche_p75=8.0, branche_p90=9.5,
            hoeher_ist_besser=True,
        ),
        BenchmarkKennzahl(
            "BK-002", "Lagerkosten je Tonne", BenchmarkKategorie.FINANZEN,
            eigenwert=12.50, einheit="€/t",
            branche_mittelwert=14.80, branche_p25=17.00, branche_p75=13.00, branche_p90=11.00,
            hoeher_ist_besser=False,
        ),
        BenchmarkKennzahl(
            "BK-003", "Trocknungskosten je Prozentpunkt Feuchte", BenchmarkKategorie.AGRAR,
            eigenwert=4.80, einheit="€/%·t",
            branche_mittelwert=5.20, branche_p25=6.00, branche_p75=4.90, branche_p90=4.20,
            hoeher_ist_besser=False,
        ),
        BenchmarkKennzahl(
            "BK-004", "CO2e-Intensität Durchsatz", BenchmarkKategorie.NACHHALTIGKEIT,
            eigenwert=0.185, einheit="t CO2e/t Ware",
            branche_mittelwert=0.220, branche_p25=0.280, branche_p75=0.200, branche_p90=0.160,
            hoeher_ist_besser=False,
        ),
        BenchmarkKennzahl(
            "BK-005", "Reklamationsquote", BenchmarkKategorie.QUALITAET,
            eigenwert=1.8, einheit="%",
            branche_mittelwert=2.5, branche_p25=3.5, branche_p75=2.0, branche_p90=1.2,
            hoeher_ist_besser=False,
        ),
        BenchmarkKennzahl(
            "BK-006", "Lieferantenzufriedenheit", BenchmarkKategorie.KUNDENZUFRIEDENHEIT,
            eigenwert=78.0, einheit="Punkte (0–100)",
            branche_mittelwert=72.0, branche_p25=60.0, branche_p75=76.0, branche_p90=85.0,
            hoeher_ist_besser=True,
        ),
    ]
    trend_daten: dict[str, list[BenchmarkTrendPunkt]] = {
        "BK-001": [
            BenchmarkTrendPunkt("2025-Q3", 7.5, 6.8),
            BenchmarkTrendPunkt("2025-Q4", 7.9, 6.9),
            BenchmarkTrendPunkt("2026-Q1", 8.2, 7.0),
        ],
        "BK-002": [
            BenchmarkTrendPunkt("2025-Q3", 13.80, 15.00),
            BenchmarkTrendPunkt("2025-Q4", 13.10, 14.90),
            BenchmarkTrendPunkt("2026-Q1", 12.50, 14.80),
        ],
    }
    return BenchmarkReport(
        report_id=f"BMK-{tenant_id}-2026-03",
        tenant_id=tenant_id,
        genossenschaft_name=genossenschaft_name,
        berichtsmonat=date(2026, 3, 1),
        frequenz=ReportFrequenz.MONATLICH,
        kennzahlen=kennzahlen,
        trend_daten=trend_daten,
        kommentar="Gesamtperformance über Branchendurchschnitt; Optimierungspotenzial bei CO2-Intensität.",
    )
