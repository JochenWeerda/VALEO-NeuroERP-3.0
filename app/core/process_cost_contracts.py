"""
Process Cost Contracts — Wave 45
Kostentracking für Workflow-Ausführungen: Ressourcenkosten,
Budget-Überwachung und Abrechnungseinheiten.

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

class KostenTyp(str, Enum):
    CPU = "CPU"
    SPEICHER = "SPEICHER"
    NETZWERK = "NETZWERK"
    STORAGE = "STORAGE"
    EXTERNE_API = "EXTERNE_API"
    MANUELL = "MANUELL"


class AbrechnungsEinheit(str, Enum):
    PRO_AUSFUEHRUNG = "PRO_AUSFUEHRUNG"
    PRO_SEKUNDE = "PRO_SEKUNDE"
    PRO_MEGABYTE = "PRO_MEGABYTE"
    PRO_API_AUFRUF = "PRO_API_AUFRUF"
    PAUSCHAL = "PAUSCHAL"


class BudgetStatus(str, Enum):
    IM_RAHMEN = "IM_RAHMEN"
    WARNUNG = "WARNUNG"        # >= 80 %
    UEBERSCHRITTEN = "UEBERSCHRITTEN"  # >= 100 %
    GESPERRT = "GESPERRT"     # verbraucht > budget


# ---------------------------------------------------------------------------
# Kosten-Position
# ---------------------------------------------------------------------------

@dataclass
class KostenPosition:
    """Eine einzelne Kostenposition innerhalb einer Prozess-Kostenerfassung."""
    position_id: str
    kosten_typ: KostenTyp
    menge: float
    einheit_preis_eur: float
    abrechnungs_einheit: AbrechnungsEinheit
    beschreibung: str = ""

    @property
    def gesamt_eur(self) -> float:
        """Gesamtkosten dieser Position in EUR (4 Dezimalstellen)."""
        return round(self.menge * self.einheit_preis_eur, 4)

    def as_dict(self) -> dict[str, Any]:
        return {
            "position_id": self.position_id,
            "kosten_typ": self.kosten_typ.value,
            "menge": self.menge,
            "einheit_preis_eur": self.einheit_preis_eur,
            "abrechnungs_einheit": self.abrechnungs_einheit.value,
            "gesamt_eur": self.gesamt_eur,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Prozess-Kostenerfassung
# ---------------------------------------------------------------------------

@dataclass
class ProzessKostenErfassung:
    """Aggregierte Kostenerfassung für eine Workflow-Instanz-Ausführung."""
    erfassung_id: str
    workflow_instanz_id: str
    tenant_id: str
    erstellt_am: datetime
    positionen: list[KostenPosition] = field(default_factory=list)

    @property
    def gesamt_kosten_eur(self) -> float:
        """Summe aller Kostenposition in EUR."""
        return round(sum(p.gesamt_eur for p in self.positionen), 4)

    @property
    def positionen_nach_typ(self) -> dict[str, float]:
        """Kosten je KostenTyp aggregiert."""
        ergebnis: dict[str, float] = {}
        for p in self.positionen:
            key = p.kosten_typ.value
            ergebnis[key] = round(ergebnis.get(key, 0.0) + p.gesamt_eur, 4)
        return ergebnis

    def as_dict(self) -> dict[str, Any]:
        return {
            "erfassung_id": self.erfassung_id,
            "workflow_instanz_id": self.workflow_instanz_id,
            "tenant_id": self.tenant_id,
            "erstellt_am": self.erstellt_am.isoformat(),
            "positionen_anzahl": len(self.positionen),
            "gesamt_kosten_eur": self.gesamt_kosten_eur,
            "positionen_nach_typ": self.positionen_nach_typ,
            "positionen": [p.as_dict() for p in self.positionen],
        }


# ---------------------------------------------------------------------------
# Budget-Überwachung
# ---------------------------------------------------------------------------

@dataclass
class BudgetUeberwachung:
    """Überwacht das Kostenbudget für einen Tenant und eine Domain."""
    budget_id: str
    tenant_id: str
    domain: str
    budget_eur: float
    verbraucht_eur: float
    periode: str = ""   # z.B. "2026-Q1"

    @property
    def auslastung_pct(self) -> float:
        if self.budget_eur <= 0:
            return 0.0
        return round(self.verbraucht_eur / self.budget_eur * 100, 2)

    @property
    def verbleibend_eur(self) -> float:
        return round(self.budget_eur - self.verbraucht_eur, 4)

    @property
    def budget_status(self) -> BudgetStatus:
        if self.verbraucht_eur > self.budget_eur:
            return BudgetStatus.GESPERRT
        pct = self.auslastung_pct
        if pct >= 100:
            return BudgetStatus.UEBERSCHRITTEN
        if pct >= 80:
            return BudgetStatus.WARNUNG
        return BudgetStatus.IM_RAHMEN

    def as_dict(self) -> dict[str, Any]:
        return {
            "budget_id": self.budget_id,
            "tenant_id": self.tenant_id,
            "domain": self.domain,
            "budget_eur": self.budget_eur,
            "verbraucht_eur": self.verbraucht_eur,
            "verbleibend_eur": self.verbleibend_eur,
            "auslastung_pct": self.auslastung_pct,
            "budget_status": self.budget_status.value,
            "periode": self.periode,
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def erstelle_kosten_erfassung(
    erfassung_id: str,
    workflow_instanz_id: str,
    tenant_id: str,
    positionen: list[KostenPosition],
    erstellt_am: datetime | None = None,
) -> ProzessKostenErfassung:
    """Erstellt eine neue Prozess-Kostenerfassung."""
    return ProzessKostenErfassung(
        erfassung_id=erfassung_id,
        workflow_instanz_id=workflow_instanz_id,
        tenant_id=tenant_id,
        erstellt_am=erstellt_am or datetime.utcnow(),
        positionen=positionen,
    )


def pruefe_budget(
    budget: BudgetUeberwachung,
    neue_kosten_eur: float,
) -> BudgetStatus:
    """
    Prüft den Budget-Status nach Hinzufügen neuer Kosten.
    Simuliert die Auslastung ohne die Erfassung dauerhaft zu ändern.
    """
    simuliert = BudgetUeberwachung(
        budget_id=budget.budget_id,
        tenant_id=budget.tenant_id,
        domain=budget.domain,
        budget_eur=budget.budget_eur,
        verbraucht_eur=budget.verbraucht_eur + neue_kosten_eur,
        periode=budget.periode,
    )
    return simuliert.budget_status


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_budget_ueberwachungen(
    tenant_id: str = "TENANT-001",
) -> list[BudgetUeberwachung]:
    """Gibt 4 Standard-Budget-Überwachungen zurück."""
    return [
        BudgetUeberwachung(
            budget_id="BU-001",
            tenant_id=tenant_id,
            domain="agrar",
            budget_eur=5000.0,
            verbraucht_eur=2800.0,
            periode="2026-Q1",
        ),
        BudgetUeberwachung(
            budget_id="BU-002",
            tenant_id=tenant_id,
            domain="finance",
            budget_eur=3000.0,
            verbraucht_eur=2650.0,
            periode="2026-Q1",
        ),
        BudgetUeberwachung(
            budget_id="BU-003",
            tenant_id=tenant_id,
            domain="compliance",
            budget_eur=1000.0,
            verbraucht_eur=1050.0,
            periode="2026-Q1",
        ),
        BudgetUeberwachung(
            budget_id="BU-004",
            tenant_id=tenant_id,
            domain="system",
            budget_eur=10000.0,
            verbraucht_eur=4200.0,
            periode="2026-Q1",
        ),
    ]
