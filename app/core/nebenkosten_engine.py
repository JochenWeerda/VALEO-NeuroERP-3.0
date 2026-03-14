"""
Nebenkosten-Engine — Wave 23 AP1/AP6

Automatische Berechnung von Nebenkosten im Agrar-Settlement-Prozess (Gap 007).
Unterstuetzte Kostenarten:
  - FRACHT: km-basiert (EUR/km) oder Pauschale (EUR fest)
  - LAGERGELD: tagesbasiert (EUR/Tonne/Tag)
  - VERWIEGUNG: Pauschale pro Wiegevorgang
  - REINIGUNG: EUR/Tonne oder Pauschale
  - SONSTIGE: beliebige Freipositionen

Ziel: >=90% automatische Kostenzuordnung ohne manuelle Eingabe.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional


NEBENKOSTEN_SCHEMA_VERSION = 1


class NebenkostenArt(str, Enum):
    FRACHT = "FRACHT"
    LAGERGELD = "LAGERGELD"
    VERWIEGUNG = "VERWIEGUNG"
    REINIGUNG = "REINIGUNG"
    SONSTIGE = "SONSTIGE"


class NebenkostenModus(str, Enum):
    PRO_TONNE = "PRO_TONNE"                # EUR/Tonne
    PRO_KM = "PRO_KM"                      # EUR/km (Fracht)
    PRO_TAG_TONNE = "PRO_TAG_TONNE"        # EUR/Tonne/Tag (Lagergeld, tagesbasiert)
    PRO_MONAT_TONNE = "PRO_MONAT_TONNE"   # EUR/dt/Monat (Lagergeld, monatsbasiert; Stichtag: 1. des Monats)
    PAUSCHALE = "PAUSCHALE"                # fester EUR-Betrag


@dataclass
class NebenkostenRule:
    """Eine einzelne Nebenkostenregel in einem Regelset."""

    rule_id: str
    art: NebenkostenArt
    modus: NebenkostenModus
    rate: Decimal          # Satz gemaess Modus
    min_amount: Decimal = Decimal("0.00")   # Mindestbetrag
    max_amount: Optional[Decimal] = None    # Maximalbetrag (None = unbegrenzt)
    description: str = ""
    active: bool = True

    def as_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "art": self.art.value,
            "modus": self.modus.value,
            "rate": str(self.rate),
            "min_amount": str(self.min_amount),
            "max_amount": str(self.max_amount) if self.max_amount is not None else None,
            "description": self.description,
            "active": self.active,
        }


@dataclass
class NebenkostenPosition:
    """Berechnete Einzelposition im Nebenkosten-Breakdown."""

    art: NebenkostenArt
    rule_id: str
    description: str
    basis_value: Decimal    # Eingangsgröße (Tonnen, km, Tage etc.)
    basis_unit: str         # "t", "km", "Tage x t", "Stück"
    rate: Decimal
    amount: Decimal
    currency: str = "EUR"

    def as_dict(self) -> dict:
        return {
            "art": self.art.value,
            "rule_id": self.rule_id,
            "description": self.description,
            "basis_value": str(self.basis_value),
            "basis_unit": self.basis_unit,
            "rate": str(self.rate),
            "amount": str(self.amount),
            "currency": self.currency,
        }


@dataclass
class NebenkostenBreakdown:
    """Vollstaendige Nebenkosten-Aufschluesselung fuer ein Settlement."""

    settlement_id: str
    tenant_id: str
    positions: list[NebenkostenPosition] = field(default_factory=list)
    currency: str = "EUR"
    schema_version: int = NEBENKOSTEN_SCHEMA_VERSION

    @property
    def total(self) -> Decimal:
        return _round(sum((p.amount for p in self.positions), Decimal("0")))

    @property
    def total_by_art(self) -> dict[str, Decimal]:
        result: dict[str, Decimal] = {}
        for p in self.positions:
            key = p.art.value
            result[key] = _round(result.get(key, Decimal("0")) + p.amount)
        return result

    def as_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "tenant_id": self.tenant_id,
            "total": str(self.total),
            "currency": self.currency,
            "position_count": len(self.positions),
            "total_by_art": {k: str(v) for k, v in self.total_by_art.items()},
            "positions": [p.as_dict() for p in self.positions],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Berechnungs-Hilfsfunktionen
# ---------------------------------------------------------------------------

def _round(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _apply_limits(amount: Decimal, rule: NebenkostenRule) -> Decimal:
    amount = max(amount, rule.min_amount)
    if rule.max_amount is not None:
        amount = min(amount, rule.max_amount)
    return _round(amount)


# ---------------------------------------------------------------------------
# Kern-Berechnungsfunktion
# ---------------------------------------------------------------------------

@dataclass
class NebenkostenInput:
    """Eingabeparameter fuer die Nebenkostenberechnung."""

    settlement_id: str
    tenant_id: str
    billing_qty_tons: Decimal               # Abrechnungsmenge in Tonnen
    transport_km: Decimal = Decimal("0")    # Transportstrecke in km
    storage_days: Decimal = Decimal("0")    # Lagerzeit in Tagen
    storage_months: Decimal = Decimal("0")  # Lagerzeit in angefangenen Monaten (PRO_MONAT_TONNE)
    weighing_count: int = 1                 # Anzahl Wiegevorgaenge
    currency: str = "EUR"


def compute_nebenkosten(
    inp: NebenkostenInput,
    rules: list[NebenkostenRule],
) -> NebenkostenBreakdown:
    """
    Berechnet alle aktiven Nebenkosten auf Basis der Regelsets.

    Nur aktive Regeln werden beruecksichtigt.
    Jede Regel erzeugt eine NebenkostenPosition.
    """
    breakdown = NebenkostenBreakdown(
        settlement_id=inp.settlement_id,
        tenant_id=inp.tenant_id,
        currency=inp.currency,
    )

    for rule in rules:
        if not rule.active:
            continue

        if rule.modus == NebenkostenModus.PRO_TONNE:
            basis = inp.billing_qty_tons
            unit = "t"
            raw = _round(basis * rule.rate)

        elif rule.modus == NebenkostenModus.PRO_KM:
            basis = inp.transport_km
            unit = "km"
            raw = _round(basis * rule.rate)

        elif rule.modus == NebenkostenModus.PRO_TAG_TONNE:
            basis = inp.storage_days * inp.billing_qty_tons
            unit = "Tage × t"
            raw = _round(basis * rule.rate)

        elif rule.modus == NebenkostenModus.PRO_MONAT_TONNE:
            # Monatsbasiertes Lagergeld: EUR/dt/Monat; zahlbar zum Monatsersten
            # 1 Tonne = 10 Dezitonne (dt)
            basis_dt = inp.billing_qty_tons * Decimal("10")   # Umrechnung t → dt
            basis = inp.storage_months * basis_dt
            unit = "Monate × dt"
            raw = _round(basis * rule.rate)

        elif rule.modus == NebenkostenModus.PAUSCHALE:
            if rule.art == NebenkostenArt.VERWIEGUNG:
                basis = Decimal(inp.weighing_count)
                unit = "Stück"
            else:
                basis = Decimal("1")
                unit = "Pauschale"
            raw = _round(basis * rule.rate)

        else:
            continue

        amount = _apply_limits(raw, rule)

        breakdown.positions.append(NebenkostenPosition(
            art=rule.art,
            rule_id=rule.rule_id,
            description=rule.description,
            basis_value=basis,
            basis_unit=unit,
            rate=rule.rate,
            amount=amount,
            currency=inp.currency,
        ))

    return breakdown


# ---------------------------------------------------------------------------
# AP6: Standard-Regelset (versioniert, Tenant-ueberschreibbar)
# ---------------------------------------------------------------------------

def get_default_nebenkosten_rules() -> list[NebenkostenRule]:
    """
    Standard-Nebenkosten-Regelset fuer Agrar-Landhandel.

    Sätze sind Richtwerte; Tenants koennen eigene Regelsets hinterlegen.
    """
    return [
        NebenkostenRule(
            rule_id="NB-FRACHT-KM",
            art=NebenkostenArt.FRACHT,
            modus=NebenkostenModus.PRO_KM,
            rate=Decimal("0.18"),
            min_amount=Decimal("10.00"),
            description="Frachtkosten EUR/km",
        ),
        NebenkostenRule(
            rule_id="NB-LAGER-TAG-T",
            art=NebenkostenArt.LAGERGELD,
            modus=NebenkostenModus.PRO_TAG_TONNE,
            rate=Decimal("0.15"),
            description="Lagergeld EUR/Tonne/Tag",
        ),
        NebenkostenRule(
            rule_id="NB-VERWIEG-PAUSCHAL",
            art=NebenkostenArt.VERWIEGUNG,
            modus=NebenkostenModus.PAUSCHALE,
            rate=Decimal("12.00"),
            description="Verwiegepauschale EUR/Vorgang",
        ),
        NebenkostenRule(
            rule_id="NB-REINIGUNG-T",
            art=NebenkostenArt.REINIGUNG,
            modus=NebenkostenModus.PRO_TONNE,
            rate=Decimal("0.80"),
            min_amount=Decimal("5.00"),
            description="Reinigungskosten EUR/Tonne",
        ),
    ]
