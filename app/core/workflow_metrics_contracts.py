"""
Workflow Metrics Contracts — Wave 50
KPI-Tracking fuer Workflow-Performance: Durchlaufzeiten,
SLA-Einhaltungsraten und Prozesseffizienz-Kennzahlen.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MetrikTyp(str, Enum):
    DURCHLAUFZEIT = "DURCHLAUFZEIT"       # Minuten von Start bis Ende
    SLA_EINHALTUNG = "SLA_EINHALTUNG"     # Prozentsatz SLA-konformer Instanzen
    FEHLERRATE = "FEHLERRATE"             # Prozentsatz fehlgeschlagener Instanzen
    DURCHSATZ = "DURCHSATZ"               # Instanzen pro Stunde
    WARTEZEIT = "WARTEZEIT"               # Minuten in Wartezustand


class MetrikAggregation(str, Enum):
    MINIMUM = "MINIMUM"
    MAXIMUM = "MAXIMUM"
    DURCHSCHNITT = "DURCHSCHNITT"
    MEDIAN = "MEDIAN"
    SUMME = "SUMME"


class PerformanzBewertung(str, Enum):
    AUSGEZEICHNET = "AUSGEZEICHNET"   # >= 95% SLA
    GUT = "GUT"                       # >= 80% SLA
    AKZEPTABEL = "AKZEPTABEL"         # >= 60% SLA
    KRITISCH = "KRITISCH"             # < 60% SLA


@dataclass
class MetrikMesspunkt:
    """Ein einzelner Metrik-Messpunkt."""
    messpunkt_id: str
    workflow_typ: str
    metrik_typ: MetrikTyp
    wert: float
    einheit: str   # z.B. "Minuten", "Prozent", "Instanzen/h"
    gemessen_am: datetime
    tenant_id: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "messpunkt_id": self.messpunkt_id,
            "workflow_typ": self.workflow_typ,
            "metrik_typ": self.metrik_typ.value,
            "wert": self.wert,
            "einheit": self.einheit,
            "gemessen_am": self.gemessen_am.isoformat(),
            "tenant_id": self.tenant_id,
        }


@dataclass
class WorkflowKpiSummary:
    """
    Aggregierte KPI-Zusammenfassung fuer einen Workflow-Typ.

    sla_einhaltung_pct: Anteil SLA-konformer Instanzen (0–100).
    performanz_bewertung wird daraus abgeleitet.
    """
    workflow_typ: str
    tenant_id: str
    periode: str           # z.B. "2026-Q1"
    instanzen_gesamt: int
    instanzen_erfolgreich: int
    instanzen_fehlgeschlagen: int
    durchlaufzeit_avg_min: float
    sla_einhaltung_pct: float
    durchsatz_pro_stunde: float
    berechnet_am: datetime = field(default_factory=datetime.utcnow)

    @property
    def fehlerrate_pct(self) -> float:
        if self.instanzen_gesamt == 0:
            return 0.0
        return round(self.instanzen_fehlgeschlagen / self.instanzen_gesamt * 100, 2)

    @property
    def erfolgsrate_pct(self) -> float:
        if self.instanzen_gesamt == 0:
            return 0.0
        return round(self.instanzen_erfolgreich / self.instanzen_gesamt * 100, 2)

    @property
    def performanz_bewertung(self) -> PerformanzBewertung:
        if self.sla_einhaltung_pct >= 95:
            return PerformanzBewertung.AUSGEZEICHNET
        if self.sla_einhaltung_pct >= 80:
            return PerformanzBewertung.GUT
        if self.sla_einhaltung_pct >= 60:
            return PerformanzBewertung.AKZEPTABEL
        return PerformanzBewertung.KRITISCH

    def as_dict(self) -> dict[str, Any]:
        return {
            "workflow_typ": self.workflow_typ,
            "tenant_id": self.tenant_id,
            "periode": self.periode,
            "instanzen_gesamt": self.instanzen_gesamt,
            "instanzen_erfolgreich": self.instanzen_erfolgreich,
            "instanzen_fehlgeschlagen": self.instanzen_fehlgeschlagen,
            "durchlaufzeit_avg_min": self.durchlaufzeit_avg_min,
            "sla_einhaltung_pct": self.sla_einhaltung_pct,
            "durchsatz_pro_stunde": self.durchsatz_pro_stunde,
            "fehlerrate_pct": self.fehlerrate_pct,
            "erfolgsrate_pct": self.erfolgsrate_pct,
            "performanz_bewertung": self.performanz_bewertung.value,
            "berechnet_am": self.berechnet_am.isoformat(),
        }


def aggregiere_messpunkte(
    messpunkte: list[MetrikMesspunkt],
    workflow_typ: str,
    metrik_typ: MetrikTyp,
    aggregation: MetrikAggregation,
) -> float:
    """
    Aggregiert Messpunkte fuer einen Workflow-Typ und Metrik-Typ.

    Gibt 0.0 zurueck wenn keine passenden Messpunkte vorhanden.
    """
    werte = [
        m.wert for m in messpunkte
        if m.workflow_typ == workflow_typ and m.metrik_typ == metrik_typ
    ]
    if not werte:
        return 0.0
    if aggregation == MetrikAggregation.MINIMUM:
        return min(werte)
    if aggregation == MetrikAggregation.MAXIMUM:
        return max(werte)
    if aggregation == MetrikAggregation.SUMME:
        return sum(werte)
    if aggregation == MetrikAggregation.MEDIAN:
        sortiert = sorted(werte)
        n = len(sortiert)
        mitte = n // 2
        if n % 2 == 1:
            return sortiert[mitte]
        return (sortiert[mitte - 1] + sortiert[mitte]) / 2
    # DURCHSCHNITT (default)
    return round(sum(werte) / len(werte), 4)


def get_default_kpi_summaries(tenant_id: str = "TENANT-001") -> list[WorkflowKpiSummary]:
    """Gibt 4 Standard-KPI-Zusammenfassungen zurueck."""
    ts = datetime(2026, 3, 15, 12, 0)
    return [
        WorkflowKpiSummary(
            workflow_typ="kontrakt_freigabe",
            tenant_id=tenant_id,
            periode="2026-Q1",
            instanzen_gesamt=320,
            instanzen_erfolgreich=304,
            instanzen_fehlgeschlagen=16,
            durchlaufzeit_avg_min=187.5,
            sla_einhaltung_pct=95.0,
            durchsatz_pro_stunde=4.2,
            berechnet_am=ts,
        ),
        WorkflowKpiSummary(
            workflow_typ="settlement_abrechnung",
            tenant_id=tenant_id,
            periode="2026-Q1",
            instanzen_gesamt=150,
            instanzen_erfolgreich=135,
            instanzen_fehlgeschlagen=15,
            durchlaufzeit_avg_min=320.0,
            sla_einhaltung_pct=82.0,
            durchsatz_pro_stunde=1.8,
            berechnet_am=ts,
        ),
        WorkflowKpiSummary(
            workflow_typ="ap_rechnungseingang",
            tenant_id=tenant_id,
            periode="2026-Q1",
            instanzen_gesamt=500,
            instanzen_erfolgreich=450,
            instanzen_fehlgeschlagen=50,
            durchlaufzeit_avg_min=55.0,
            sla_einhaltung_pct=58.0,
            durchsatz_pro_stunde=12.5,
            berechnet_am=ts,
        ),
        WorkflowKpiSummary(
            workflow_typ="qualitaets_freigabe",
            tenant_id=tenant_id,
            periode="2026-Q1",
            instanzen_gesamt=200,
            instanzen_erfolgreich=186,
            instanzen_fehlgeschlagen=14,
            durchlaufzeit_avg_min=42.0,
            sla_einhaltung_pct=88.0,
            durchsatz_pro_stunde=6.0,
            berechnet_am=ts,
        ),
    ]
