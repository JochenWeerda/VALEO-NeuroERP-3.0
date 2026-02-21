"""
Harvest Acceptance (Ernte-Annahme) Berechnungslogik.
Berechnet die 14 Abrechnungs-Positionen basierend auf Wiegeschein, Laborwerten und Eingaben.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Protocol
from datetime import date


def round_money(value: Decimal | float | int) -> Decimal:
    """Rundet auf 2 Dezimalstellen (EUR)."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def round_qty(value: Decimal | float | int) -> Decimal:
    """Rundet auf 3 Dezimalstellen (kg)."""
    return Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def round_pct(value: Decimal | float | int) -> Decimal:
    """Rundet auf 2 Dezimalstellen (%)."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class DryingRuleRepository(Protocol):
    """Protocol für Drying Rule Repository (optional, für Feuchte-Berechnung)."""
    def find_rule_set(self, *, crop_code: str, site_id: Optional[str], contract_id: Optional[str], customer_id: Optional[str], calc_date: date): ...
    def list_lookup_rows(self, *, rule_set_id: str): ...
    def list_factor_ranges(self, *, rule_set_id: str): ...


@dataclass
class HarvestCalculationInput:
    """Eingabedaten für Berechnung."""
    # Basis-Menge
    delivered_quantity_kg: Decimal  # Pos. 10: Angelieferte Menge (aus Wiegeschein)
    
    # Laborwerte
    windage_pct: Optional[Decimal] = None  # Pos. 15: Windabgang (%)
    impurities_pct: Optional[Decimal] = None  # Pos. 20: Besatz (%)
    moisture_pct: Optional[Decimal] = None  # Pos. 40: Feuchte (%)
    hl_weight_kg_per_hl: Optional[Decimal] = None  # Pos. 60: Hektolitergewicht (kg/hl)
    storage_shrinkage_pct: Optional[Decimal] = None  # Pos. 63: Lagerschwund (%)
    
    # Eingaben (EUR)
    storage_fee_per_month: Optional[Decimal] = None  # Pos. 75: Lagergeld (EUR/Monat)
    storage_months: Optional[int] = None  # Anzahl Monate für Lagergeld
    freight_costs: Optional[Decimal] = None  # Pos. 78: Frachtkosten (EUR)
    weighing_fees: Optional[Decimal] = None  # Pos. 80: Wiegegebühren (EUR)
    
    # Besatz "2% frei" Regel
    impurities_free_pct: Decimal = Decimal("2.0")  # Standard: 2% frei
    
    # Preis (für Gutschriftsbetrag)
    unit_price_eur_per_ton: Optional[Decimal] = None
    
    # Drying Rule Engine (optional)
    use_drying_rule_engine: bool = False  # Soll Drying Rule Engine verwendet werden?
    crop_code: Optional[str] = None  # Für Drying Rule Engine (z.B. "MAIZE", "WHEAT")
    site_id: Optional[str] = None  # Für Drying Rule Engine
    contract_id: Optional[str] = None  # Für Drying Rule Engine
    customer_id: Optional[str] = None  # Für Drying Rule Engine
    calc_date: Optional[date] = None  # Für Drying Rule Engine
    drying_repo: Optional[DryingRuleRepository] = None  # Drying Rule Repository


@dataclass
class HarvestPositionResult:
    """Ergebnis einer Abrechnungs-Position."""
    position_number: int
    description: str
    quantity_kg: Optional[Decimal] = None
    quantity_pct: Optional[Decimal] = None
    amount_eur: Optional[Decimal] = None
    unit: Optional[str] = None
    calculation_formula: Optional[str] = None


@dataclass
class HarvestCalculationResult:
    """Gesamtergebnis der Berechnung."""
    positions: list[HarvestPositionResult]
    total_net_amount_eur: Decimal
    total_vat_amount_eur: Decimal
    total_gross_amount_eur: Decimal
    vat_rate_percent: Optional[Decimal] = None
    warnings: list[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


def calculate_harvest_settlement(inp: HarvestCalculationInput, vat_rate_percent: Optional[Decimal] = None) -> HarvestCalculationResult:
    """
    Berechnet alle Abrechnungs-Positionen für Ernte-Annahme.
    
    Berechnungsreihenfolge:
    1. Angelieferte Menge (Pos. 10) = delivered_quantity_kg
    2. Windabgang (Pos. 15) = delivered_quantity_kg × (windage_pct / 100)
    3. Besatz 2% frei (Pos. 20) = max(0, impurities_pct - 2%) × delivered_quantity_kg / 100
    4. Gereinigte Menge (Pos. 30) = delivered_quantity_kg - Besatz_Abzug
    5. Feuchte/Tr.verlust (Pos. 40) = Gereinigte Menge × (moisture_pct / 100) [oder aus Drying Rule Engine]
    6. Zwischenmenge (Pos. 50) = Gereinigte Menge - Feuchte/Tr.verlust
    7. Hektolitergewicht (Pos. 60) = hl_weight_kg_per_hl (Info)
    8. Lagerschwund (Pos. 63) = Zwischenmenge × (storage_shrinkage_pct / 100)
    9. Nettogewicht (Pos. 65) = Zwischenmenge - Lagerschwund
    10. Feuchtigkeitsabzug (Pos. 70) = Berechnet aus Feuchte (kann identisch mit Pos. 40 sein)
    11. Lagergeld (Pos. 75) = storage_fee_per_month × storage_months
    12. Frachtkosten (Pos. 78) = freight_costs
    13. Wiegegebühren (Pos. 80) = weighing_fees
    14. Gutschriftsbetrag (Pos. 110) = (Nettogewicht × Preis) - Abzüge + Zuschläge
    """
    warnings: list[str] = []
    positions: list[HarvestPositionResult] = []
    
    # Pos. 10: Angelieferte Menge
    delivered_qty = round_qty(inp.delivered_quantity_kg)
    positions.append(HarvestPositionResult(
        position_number=10,
        description="Angelieferte Menge",
        quantity_kg=delivered_qty,
        unit="kg",
        calculation_formula="Aus Wiegeschein (Nettogewicht)"
    ))
    
    # Pos. 15: Windabgang (optional, nur Info wenn vorhanden)
    windage_kg = Decimal("0")
    if inp.windage_pct is not None and inp.windage_pct > 0:
        windage_pct = round_pct(inp.windage_pct)
        windage_kg = round_qty(delivered_qty * (windage_pct / Decimal("100")))
        positions.append(HarvestPositionResult(
            position_number=15,
            description="Windabgang",
            quantity_kg=windage_kg,
            quantity_pct=windage_pct,
            unit="kg / %",
            calculation_formula=f"Angelieferte Menge × ({windage_pct}% / 100)"
        ))
    
    # Pos. 20: Besatz 2% frei
    impurities_abzug_kg = Decimal("0")
    if inp.impurities_pct is not None:
        impurities_pct = round_pct(inp.impurities_pct)
        # "2% frei" bedeutet: nur der Anteil über 2% wird abgezogen
        impurities_abzug_pct = max(Decimal("0"), impurities_pct - inp.impurities_free_pct)
        if impurities_abzug_pct > 0:
            impurities_abzug_kg = round_qty(delivered_qty * (impurities_abzug_pct / Decimal("100")))
        positions.append(HarvestPositionResult(
            position_number=20,
            description="Besatz 2% frei",
            quantity_kg=impurities_abzug_kg,
            quantity_pct=impurities_pct,
            unit="kg / %",
            calculation_formula=f"max(0, {impurities_pct}% - {inp.impurities_free_pct}%) × Angelieferte Menge / 100"
        ))
    
    # Pos. 30: Gereinigte Menge
    cleaned_qty = round_qty(delivered_qty - impurities_abzug_kg)
    positions.append(HarvestPositionResult(
        position_number=30,
        description="Gereinigte Menge",
        quantity_kg=cleaned_qty,
        unit="kg",
        calculation_formula="Angelieferte Menge - Besatz_Abzug"
    ))
    
    # Pos. 40: Feuchte/Tr.verlust
    moisture_loss_kg = Decimal("0")
    moisture_loss_pct = Decimal("0")
    drying_fee_eur: Optional[Decimal] = None
    drying_calculation_formula = ""
    used_rule_set_id: Optional[str] = None
    
    if inp.moisture_pct is not None:
        moisture_pct = round_pct(inp.moisture_pct)
        
        # Verwende Drying Rule Engine, falls aktiviert und verfügbar
        if inp.use_drying_rule_engine and inp.drying_repo and inp.crop_code and inp.calc_date:
            try:
                from modules.agrar.services.drying_rule_engine import compute_settlement as compute_drying_settlement
                
                drying_input = {
                    "cropCode": inp.crop_code,
                    "siteId": inp.site_id,
                    "netWeightKg": float(cleaned_qty),
                    "moisturePct": float(moisture_pct),
                    "calcDate": inp.calc_date.isoformat(),
                    "contractId": inp.contract_id,
                    "customerId": inp.customer_id,
                }
                
                drying_result = compute_drying_settlement(inp.drying_repo, drying_input)
                
                # Verwende invoice_weight_kg als Basis für weitere Berechnungen
                invoice_weight_kg = round_qty(Decimal(str(drying_result.invoice_weight_kg)))
                moisture_loss_kg = round_qty(cleaned_qty - invoice_weight_kg)
                moisture_loss_pct = round_pct(drying_result.loss_pct)
                drying_fee_eur = round_money(drying_result.drying_fee_eur) if drying_result.drying_fee_eur else None
                used_rule_set_id = drying_result.used_rule_set_id
                
                drying_calculation_formula = (
                    f"Drying Rule Engine ({drying_result.used_rule_set_id}, v{drying_result.used_rule_version}): "
                    f"loss_pct={moisture_loss_pct}%, invoice_weight={invoice_weight_kg}kg"
                )
                
                if drying_result.warnings:
                    warnings.extend(drying_result.warnings)
                    
            except Exception as e:
                warnings.append(f"Drying Rule Engine Fehler: {str(e)}. Fallback auf vereinfachte Berechnung.")
                # Fallback auf vereinfachte Berechnung
                moisture_loss_kg = round_qty(cleaned_qty * (moisture_pct / Decimal("100")))
                moisture_loss_pct = moisture_pct
                drying_calculation_formula = f"Vereinfacht: Gereinigte Menge × ({moisture_pct}% / 100)"
        else:
            # Vereinfachte Berechnung: Feuchte als Mengenabzug
            moisture_loss_kg = round_qty(cleaned_qty * (moisture_pct / Decimal("100")))
            moisture_loss_pct = moisture_pct
            drying_calculation_formula = f"Vereinfacht: Gereinigte Menge × ({moisture_pct}% / 100)"
        
        positions.append(HarvestPositionResult(
            position_number=40,
            description="Feuchte/Tr.verlust",
            quantity_kg=moisture_loss_kg,
            quantity_pct=moisture_loss_pct,
            unit="kg / %",
            calculation_formula=drying_calculation_formula
        ))
        
        # Pos. 70: Trocknungskosten (falls vorhanden)
        if drying_fee_eur and drying_fee_eur > 0:
            positions.append(HarvestPositionResult(
                position_number=70,
                description="Trocknungskosten",
                amount_eur=drying_fee_eur,
                unit="EUR",
                calculation_formula=f"Aus Drying Rule Engine (Regel-ID: {used_rule_set_id or 'N/A'})"
            ))
    
    # Pos. 50: Zwischenmenge
    intermediate_qty = round_qty(cleaned_qty - moisture_loss_kg)
    positions.append(HarvestPositionResult(
        position_number=50,
        description="Zwischenmenge",
        quantity_kg=intermediate_qty,
        unit="kg",
        calculation_formula="Gereinigte Menge - Feuchte/Tr.verlust"
    ))
    
    # Pos. 60: Hektolitergewicht (Info, kein Abzug)
    if inp.hl_weight_kg_per_hl is not None:
        hl_weight = round_qty(inp.hl_weight_kg_per_hl)
        positions.append(HarvestPositionResult(
            position_number=60,
            description="Hektolitergewicht",
            quantity_kg=hl_weight,
            unit="kg/hl",
            calculation_formula="Aus Laborwert"
        ))
    
    # Pos. 63: Lagerschwund
    storage_shrinkage_kg = Decimal("0")
    if inp.storage_shrinkage_pct is not None and inp.storage_shrinkage_pct > 0:
        storage_shrinkage_pct = round_pct(inp.storage_shrinkage_pct)
        storage_shrinkage_kg = round_qty(intermediate_qty * (storage_shrinkage_pct / Decimal("100")))
        positions.append(HarvestPositionResult(
            position_number=63,
            description="Lagerschwund",
            quantity_kg=storage_shrinkage_kg,
            quantity_pct=storage_shrinkage_pct,
            unit="kg / %",
            calculation_formula=f"Zwischenmenge × ({storage_shrinkage_pct}% / 100)"
        ))
    
    # Pos. 65: Nettogewicht (Endgültiges Nettogewicht)
    final_net_weight_kg = round_qty(intermediate_qty - storage_shrinkage_kg)
    positions.append(HarvestPositionResult(
        position_number=65,
        description="Nettogewicht",
        quantity_kg=final_net_weight_kg,
        unit="kg",
        calculation_formula="Zwischenmenge - Lagerschwund"
    ))
    
    # Pos. 70: Feuchtigkeitsabzug (wird nur angezeigt, wenn keine Trocknungskosten vorhanden)
    # Wenn Trocknungskosten vorhanden, wird Pos. 70 bereits oben erstellt
    if inp.moisture_pct is not None and (not drying_fee_eur or drying_fee_eur == 0):
        positions.append(HarvestPositionResult(
            position_number=70,
            description="Feuchtigkeitsabzug",
            quantity_kg=moisture_loss_kg,
            quantity_pct=moisture_loss_pct if moisture_loss_pct > 0 else round_pct(inp.moisture_pct),
            unit="kg / %",
            calculation_formula="Gleiche Berechnung wie Pos. 40"
        ))
    
    # Pos. 75: Lagergeld
    storage_fee_eur = Decimal("0")
    if inp.storage_fee_per_month is not None and inp.storage_months is not None:
        storage_fee_eur = round_money(inp.storage_fee_per_month * Decimal(str(inp.storage_months)))
        positions.append(HarvestPositionResult(
            position_number=75,
            description="Lagergeld",
            amount_eur=storage_fee_eur,
            unit="EUR",
            calculation_formula=f"{inp.storage_fee_per_month} EUR/Monat × {inp.storage_months} Monate"
        ))
    
    # Pos. 78: Frachtkosten
    if inp.freight_costs is not None:
        freight_eur = round_money(inp.freight_costs)
        positions.append(HarvestPositionResult(
            position_number=78,
            description="Frachtkosten",
            amount_eur=freight_eur,
            unit="EUR",
            calculation_formula="Eingabe"
        ))
    
    # Pos. 80: Wiegegebühren
    if inp.weighing_fees is not None:
        weighing_fee_eur = round_money(inp.weighing_fees)
        positions.append(HarvestPositionResult(
            position_number=80,
            description="Wiegegebühren",
            amount_eur=weighing_fee_eur,
            unit="EUR",
            calculation_formula="Eingabe"
        ))
    
    # Pos. 110: Gutschriftsbetrag
    # Berechnung: (Nettogewicht × Preis) - Abzüge + Zuschläge
    # Abzüge: Lagergeld, Frachtkosten, Wiegegebühren, Trocknungskosten (falls vorhanden)
    # Zuschläge: keine (falls später benötigt)
    total_deductions_eur = (
        storage_fee_eur +
        (round_money(inp.freight_costs) if inp.freight_costs else Decimal("0")) +
        (round_money(inp.weighing_fees) if inp.weighing_fees else Decimal("0")) +
        (drying_fee_eur if drying_fee_eur else Decimal("0"))
    )
    
    gross_amount_eur = Decimal("0")
    if inp.unit_price_eur_per_ton is not None:
        final_net_weight_tons = round_qty(final_net_weight_kg / Decimal("1000"))
        gross_amount_eur = round_money(final_net_weight_tons * inp.unit_price_eur_per_ton)
    
    net_amount_eur = round_money(gross_amount_eur - total_deductions_eur)
    
    positions.append(HarvestPositionResult(
        position_number=110,
        description="Gutschriftsbetrag",
        amount_eur=net_amount_eur,
        unit="EUR",
        calculation_formula=f"(Nettogewicht × Preis) - Abzüge = {gross_amount_eur} - {total_deductions_eur}"
    ))
    
    # MWSt-Berechnung
    vat_amount_eur = Decimal("0")
    if vat_rate_percent is not None:
        vat_rate = round_pct(vat_rate_percent)
        vat_amount_eur = round_money(net_amount_eur * (vat_rate / Decimal("100")))
    
    gross_with_vat_eur = round_money(net_amount_eur + vat_amount_eur)
    
    return HarvestCalculationResult(
        positions=positions,
        total_net_amount_eur=net_amount_eur,
        total_vat_amount_eur=vat_amount_eur,
        total_gross_amount_eur=gross_with_vat_eur,
        vat_rate_percent=vat_rate_percent,
        warnings=warnings
    )

