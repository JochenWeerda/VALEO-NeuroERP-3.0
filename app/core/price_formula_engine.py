"""
Kontrakt-Preisformel-Engine — Wave 21 AP1/AP5

Einheitliche Preislogik fuer alle Kontrakttypen (Gap 006):
- FixedPrice: unveraenderlicher Festpreis
- FormulaPrice: Basis ± Aufschlag/Abschlag (z.B. MATIF + X EUR/t)
- TerminmarktPrice: Terminmarkt-Referenz mit Basis-Spread

Jede Bewertung erzeugt eine PriceEvaluation mit vollstaendiger Audit-Spur.
PriceDeviationAlert wird ausgeloest, wenn der berechnete Preis mehr als
DEVIATION_THRESHOLD_PCT vom Referenzpreis abweicht.

Rechtsgrundlage: keine spezifische AO-Pflicht, aber Grundsatz der
Nachvollziehbarkeit (GoBD Rz. 45 — Belege müssen Buchungsgrund erkennen lassen).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional


PRICE_SCHEMA_VERSION = 1
DEVIATION_THRESHOLD_PCT = Decimal("5.0")   # 5 % → Alert


class PriceType(str, Enum):
    FIXED = "FIXED"            # unveraenderlicher Festpreis
    FORMULA = "FORMULA"        # Basis ± Aufschlag/Abschlag
    TERMINMARKT = "TERMINMARKT"  # MATIF/CBOT-Referenz + Spread


@dataclass
class FixedPriceSpec:
    price_eur_per_ton: Decimal
    currency: str = "EUR"


@dataclass
class FormulaPriceSpec:
    """Preis = base_price ± surcharge (positiv = Aufschlag, negativ = Abschlag)."""
    base_price_eur_per_ton: Decimal
    surcharge_eur_per_ton: Decimal = Decimal("0.00")  # kann negativ sein
    currency: str = "EUR"

    @property
    def effective_price(self) -> Decimal:
        raw = self.base_price_eur_per_ton + self.surcharge_eur_per_ton
        return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class TerminmarktPriceSpec:
    """Preis = Terminmarkt-Referenzkurs + Basis-Spread."""
    market_reference_id: str          # z.B. "MATIF_WEIZEN_MAR26"
    settlement_price_eur_per_ton: Decimal   # aktueller Kurs zum Bewertungszeitpunkt
    basis_spread_eur_per_ton: Decimal = Decimal("0.00")  # Auf-/Abschlag auf Kurs
    currency: str = "EUR"

    @property
    def effective_price(self) -> Decimal:
        raw = self.settlement_price_eur_per_ton + self.basis_spread_eur_per_ton
        return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class PriceEvaluation:
    """Ergebnis einer Preis-Bewertung inkl. vollstaendiger Audit-Spur."""

    price_type: PriceType
    effective_price_eur_per_ton: Decimal
    currency: str
    reference_price_eur_per_ton: Optional[Decimal]  # Vergleichswert; None wenn kein Referenz
    deviation_pct: Optional[Decimal]                # % Abweichung von Referenz; None wenn kein Referenz
    deviation_alert: bool
    audit_trail: dict                # Maschinenlesbarer Berechnungsweg
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    process_definition_key: str = "agrar_settlement"
    workflow_version: str = "1.0"
    schema_version: int = PRICE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "price_type": self.price_type.value,
            "effective_price_eur_per_ton": str(self.effective_price_eur_per_ton),
            "currency": self.currency,
            "reference_price_eur_per_ton": (
                str(self.reference_price_eur_per_ton)
                if self.reference_price_eur_per_ton is not None else None
            ),
            "deviation_pct": (
                str(self.deviation_pct) if self.deviation_pct is not None else None
            ),
            "deviation_alert": self.deviation_alert,
            "audit_trail": self.audit_trail,
            "evaluated_at": self.evaluated_at,
            "process_definition_key": self.process_definition_key,
            "workflow_version": self.workflow_version,
            "schema_version": self.schema_version,
        }


@dataclass
class PriceDeviationAlert:
    """Alert bei Preisabweichung > DEVIATION_THRESHOLD_PCT vom Referenzpreis."""

    settlement_id: str
    price_type: PriceType
    effective_price: Decimal
    reference_price: Decimal
    deviation_pct: Decimal
    threshold_pct: Decimal = DEVIATION_THRESHOLD_PCT
    triggered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: int = PRICE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "price_type": self.price_type.value,
            "effective_price": str(self.effective_price),
            "reference_price": str(self.reference_price),
            "deviation_pct": str(self.deviation_pct),
            "threshold_pct": str(self.threshold_pct),
            "triggered_at": self.triggered_at,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Kern-Evaluierungs-Funktion
# ---------------------------------------------------------------------------

def evaluate_price(
    spec: FixedPriceSpec | FormulaPriceSpec | TerminmarktPriceSpec,
    *,
    reference_price: Optional[Decimal] = None,
) -> PriceEvaluation:
    """
    Bewertet eine Preisspezifikation und erzeugt eine PriceEvaluation.

    Args:
        spec: FixedPriceSpec, FormulaPriceSpec oder TerminmarktPriceSpec
        reference_price: optionaler Referenzpreis fuer Abweichungspruefung

    Returns:
        PriceEvaluation mit Audit-Spur und ggf. Abweichungs-Flag
    """
    if isinstance(spec, FixedPriceSpec):
        price_type = PriceType.FIXED
        effective = spec.price_eur_per_ton.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        currency = spec.currency
        trail = {
            "type": "fixed",
            "price_eur_per_ton": str(spec.price_eur_per_ton),
        }

    elif isinstance(spec, FormulaPriceSpec):
        price_type = PriceType.FORMULA
        effective = spec.effective_price
        currency = spec.currency
        trail = {
            "type": "formula",
            "base_price_eur_per_ton": str(spec.base_price_eur_per_ton),
            "surcharge_eur_per_ton": str(spec.surcharge_eur_per_ton),
            "effective_price_eur_per_ton": str(effective),
        }

    elif isinstance(spec, TerminmarktPriceSpec):
        price_type = PriceType.TERMINMARKT
        effective = spec.effective_price
        currency = spec.currency
        trail = {
            "type": "terminmarkt",
            "market_reference_id": spec.market_reference_id,
            "settlement_price_eur_per_ton": str(spec.settlement_price_eur_per_ton),
            "basis_spread_eur_per_ton": str(spec.basis_spread_eur_per_ton),
            "effective_price_eur_per_ton": str(effective),
        }

    else:
        raise TypeError(f"Unbekannter Preis-Spec-Typ: {type(spec)}")

    # Abweichungsberechnung
    deviation_pct: Optional[Decimal] = None
    deviation_alert = False
    if reference_price is not None and reference_price != Decimal("0"):
        deviation_pct = (
            abs(effective - reference_price) / reference_price * Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        deviation_alert = deviation_pct > DEVIATION_THRESHOLD_PCT
        trail["reference_price_eur_per_ton"] = str(reference_price)
        trail["deviation_pct"] = str(deviation_pct)
        trail["deviation_alert"] = deviation_alert

    return PriceEvaluation(
        price_type=price_type,
        effective_price_eur_per_ton=effective,
        currency=currency,
        reference_price_eur_per_ton=reference_price,
        deviation_pct=deviation_pct,
        deviation_alert=deviation_alert,
        audit_trail=trail,
    )


def build_deviation_alert(
    settlement_id: str,
    evaluation: PriceEvaluation,
) -> Optional[PriceDeviationAlert]:
    """Erzeugt einen PriceDeviationAlert wenn die Evaluation ein Alert-Flag traegt."""
    if not evaluation.deviation_alert or evaluation.reference_price_eur_per_ton is None:
        return None
    return PriceDeviationAlert(
        settlement_id=settlement_id,
        price_type=evaluation.price_type,
        effective_price=evaluation.effective_price_eur_per_ton,
        reference_price=evaluation.reference_price_eur_per_ton,
        deviation_pct=evaluation.deviation_pct,  # type: ignore[arg-type]
    )
