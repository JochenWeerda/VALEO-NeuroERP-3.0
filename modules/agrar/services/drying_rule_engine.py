"""
Drying Rule Engine – Trocknungsschwund & Trocknungskosten.

Methoden: LOOKUP_TABLE, FACTOR_FROM_BASE, DRY_MATTER_NORMALIZATION
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP, ROUND_DOWN
from typing import Literal, Optional, Protocol, Any


def _d(value: float | Decimal | str | int) -> Decimal:
    return Decimal(str(value))


@dataclass(frozen=True)
class DryingFactorRange:
    """Stufige Faktoren (FACTOR_FROM_BASE)."""
    from_moisture_incl: Decimal
    to_moisture_incl: Decimal
    factor: Decimal


@dataclass(frozen=True)
class DryingLookupRow:
    """Lookup-Zeile (LOOKUP_TABLE)."""
    moisture_pct: Decimal
    entzug_pct_points: Decimal
    loss_pct: Decimal
    drying_fee_eur: Optional[Decimal] = None


@dataclass
class DryingRuleSet:
    """Regelsatz für Trocknungsberechnung."""
    id: str
    version: int
    crop_code: str
    site_id: Optional[str]
    valid_from: Optional[date]
    valid_to: Optional[date]
    method: Literal["LOOKUP_TABLE", "FACTOR_FROM_BASE", "DRY_MATTER_NORMALIZATION"]
    base_moisture_pct: Decimal
    rounding_mode: Literal["ROUND_NEAREST", "ROUND_UP", "ROUND_DOWN"] = "ROUND_NEAREST"
    clamp_mode: Literal["CLAMP_TO_MAX", "HARD_ERROR"] = "HARD_ERROR"
    start_threshold_moisture_pct: Optional[Decimal] = None


class DryingRuleRepository(Protocol):
    """Protocol für Drying-Rule-Repository."""

    def find_rule_set(
        self,
        *,
        crop_code: str,
        site_id: Optional[str],
        calc_date: date,
        contract_id: Optional[str] = None,
        customer_id: Optional[str] = None,
    ) -> DryingRuleSet:
        """Findet passenden Regelsatz."""
        ...

    def list_lookup_rows(self, *, rule_set_id: str) -> list[DryingLookupRow]:
        """Listet Lookup-Zeilen (LOOKUP_TABLE)."""
        ...

    def list_factor_ranges(self, *, rule_set_id: str) -> list[DryingFactorRange]:
        """Listet Faktor-Stufen (FACTOR_FROM_BASE)."""
        ...


def round_moisture_to_0_1(
    value: Decimal,
    mode: Literal["ROUND_NEAREST", "ROUND_UP", "ROUND_DOWN"],
) -> Decimal:
    """Rundet Feuchte auf 0,1%."""
    rounded = value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    if mode == "ROUND_NEAREST":
        return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    if mode == "ROUND_UP":
        return value.quantize(Decimal("0.1"), rounding=ROUND_UP)
    if mode == "ROUND_DOWN":
        return value.quantize(Decimal("0.1"), rounding=ROUND_DOWN)
    return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


@dataclass
class ComputeSettlementResult:
    """Ergebnis der Trocknungsberechnung."""
    entzug_pct_points: Decimal
    loss_pct: Decimal
    loss_kg: Decimal
    invoice_weight_kg: Decimal
    drying_fee_eur: Optional[Decimal] = None
    used_rule_set_id: str = ""
    used_rule_version: int = 0
    used_row_moisture_pct: Optional[Decimal] = None
    warnings: list[str] = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            object.__setattr__(self, "warnings", [])


def compute_settlement(
    repo: DryingRuleRepository,
    inp: dict[str, Any],
) -> ComputeSettlementResult:
    """
    Berechnet Trocknungsschwund und Rechnungsgewicht.

    inp: {
        cropCode, netWeightKg, moisturePct,
        calcDate (YYYY-MM-DD), siteId?, contractId?, customerId?
    }
    """
    crop_code = str(inp.get("cropCode", ""))
    net_kg = _d(inp.get("netWeightKg", 0))
    moisture_pct = _d(inp.get("moisturePct", 0))
    calc_date_str = inp.get("calcDate") or date.today().isoformat()
    calc_date = date.fromisoformat(str(calc_date_str)[:10]) if calc_date_str else date.today()
    site_id = inp.get("siteId")
    contract_id = inp.get("contractId")
    customer_id = inp.get("customerId")

    if net_kg <= 0:
        return ComputeSettlementResult(
            entzug_pct_points=Decimal("0"),
            loss_pct=Decimal("0"),
            loss_kg=Decimal("0"),
            invoice_weight_kg=Decimal("0"),
            warnings=["netWeightKg must be > 0"],
        )

    rs = repo.find_rule_set(
        crop_code=crop_code,
        site_id=site_id,
        calc_date=calc_date,
        contract_id=contract_id,
        customer_id=customer_id,
    )

    mo = round_moisture_to_0_1(moisture_pct, rs.rounding_mode)
    base = rs.base_moisture_pct

    if rs.method == "LOOKUP_TABLE":
        lookup = repo.list_lookup_rows(rule_set_id=rs.id)
        row = next((r for r in lookup if r.moisture_pct == mo), None)
        if row is None:
            candidates = sorted(lookup, key=lambda r: abs(r.moisture_pct - mo))
            if rs.clamp_mode == "CLAMP_TO_MAX" and candidates:
                row = candidates[-1] if mo > base else candidates[0]
            else:
                return ComputeSettlementResult(
                    entzug_pct_points=Decimal("0"),
                    loss_pct=Decimal("0"),
                    loss_kg=Decimal("0"),
                    invoice_weight_kg=net_kg,
                    used_rule_set_id=rs.id,
                    used_rule_version=rs.version,
                    warnings=[f"Keine Lookup-Zeile für Feuchte {mo}%"],
                )
        entzug = row.entzug_pct_points
        loss_pct = row.loss_pct
        drying_fee = row.drying_fee_eur

    elif rs.method == "FACTOR_FROM_BASE":
        thresh = rs.start_threshold_moisture_pct or base
        if mo <= thresh:
            entzug = Decimal("0")
            loss_pct = Decimal("0")
            drying_fee = None
        else:
            ranges = repo.list_factor_ranges(rule_set_id=rs.id)
            fac = Decimal("1.0")
            for r in ranges:
                if r.from_moisture_incl <= mo <= r.to_moisture_incl:
                    fac = r.factor
                    break
            entzug = (mo - base).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            loss_pct = (entzug * fac).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            drying_fee = None

    elif rs.method == "DRY_MATTER_NORMALIZATION":
        # Trockenmasse-Erhalt: invoice = net * (100 - moisture) / (100 - base)
        dry_ratio = (Decimal("100") - mo) / (Decimal("100") - base)
        invoice_kg = net_kg * dry_ratio
        loss_kg = net_kg - invoice_kg
        loss_pct = (loss_kg / net_kg * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        entzug = mo - base
        return ComputeSettlementResult(
            entzug_pct_points=entzug.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
            loss_pct=loss_pct,
            loss_kg=loss_kg.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP),
            invoice_weight_kg=invoice_kg.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP),
            drying_fee_eur=None,
            used_rule_set_id=rs.id,
            used_rule_version=rs.version,
            used_row_moisture_pct=mo,
        )

    else:
        return ComputeSettlementResult(
            entzug_pct_points=Decimal("0"),
            loss_pct=Decimal("0"),
            loss_kg=Decimal("0"),
            invoice_weight_kg=net_kg,
            used_rule_set_id=rs.id,
            used_rule_version=rs.version,
            warnings=[f"Unbekannte Methode: {rs.method}"],
        )

    loss_kg = net_kg * (loss_pct / Decimal("100"))
    invoice_kg = net_kg - loss_kg

    return ComputeSettlementResult(
        entzug_pct_points=entzug,
        loss_pct=loss_pct,
        loss_kg=loss_kg.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
        invoice_weight_kg=invoice_kg.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
        drying_fee_eur=drying_fee,
        used_rule_set_id=rs.id,
        used_rule_version=rs.version,
        used_row_moisture_pct=mo if rs.method == "LOOKUP_TABLE" else None,
    )


# Alias für ComputeSettlementInput (dict-basiert)
ComputeSettlementInput = dict[str, Any]
