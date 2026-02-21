"""
Price Adjustment Service.
Handles configurable price adjustments (HL-weight, impurities, mycotoxin, etc.).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, Literal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.infrastructure.models import PriceAdjustmentRule


AdjustmentType = Literal["hl_weight", "impurity", "mycotoxin", "other"]


class PriceAdjustmentResult:
    """Ergebnis einer Preis-Anpassung."""
    adjustment_amount_eur_per_ton: Decimal
    adjustment_pct: Optional[Decimal]
    method_used: str
    rule_id: Optional[str]


def calculate_price_adjustment(
    db: Session,
    tenant_id: str,
    adjustment_type: AdjustmentType,
    parameter_value: Decimal,
    article_id: Optional[str] = None,
    warengruppe: Optional[str] = None,
    effective_date: Optional[date] = None,
) -> Optional[PriceAdjustmentResult]:
    """
    Berechnet Preis-Anpassung basierend auf konfigurierten Regeln.
    
    Args:
        db: Database session
        tenant_id: Tenant ID
        adjustment_type: Art der Anpassung (hl_weight, impurity, mycotoxin, other)
        parameter_value: Wert des Parameters (z.B. HL-Gewicht in kg/hl, Besatz in %)
        article_id: Artikel-ID (optional)
        warengruppe: Warengruppe (optional)
        effective_date: Datum für Gültigkeitsprüfung (default: heute)
    
    Returns:
        PriceAdjustmentResult oder None, wenn keine Regel gefunden
    """
    if not effective_date:
        effective_date = date.today()
    
    # Suche gültige Regel
    query = db.query(PriceAdjustmentRule).filter(
        and_(
            PriceAdjustmentRule.tenant_id == tenant_id,
            PriceAdjustmentRule.adjustment_type == adjustment_type,
            PriceAdjustmentRule.effective_from <= effective_date,
            or_(
                PriceAdjustmentRule.effective_to.is_(None),
                PriceAdjustmentRule.effective_to >= effective_date,
            ),
        )
    )
    
    # Filter nach Artikel oder Warengruppe
    if article_id:
        query = query.filter(
            or_(
                PriceAdjustmentRule.article_id == article_id,
                PriceAdjustmentRule.article_id.is_(None),
            )
        )
    elif warengruppe:
        query = query.filter(
            or_(
                PriceAdjustmentRule.warengruppe == warengruppe,
                PriceAdjustmentRule.warengruppe.is_(None),
            )
        )
    
    # Sortiere: spezifische Regel (mit article_id/warengruppe) vor allgemeiner Regel
    rule = query.order_by(
        PriceAdjustmentRule.article_id.desc().nullslast(),
        PriceAdjustmentRule.warengruppe.desc().nullslast(),
    ).first()
    
    if not rule:
        return None
    
    # Berechne Anpassung basierend auf Methode
    result = PriceAdjustmentResult()
    result.method_used = rule.method
    result.rule_id = rule.id
    
    if rule.method == "table":
        # Lookup-Tabelle aus steps (JSONB)
        steps = rule.steps or []
        adjustment = Decimal("0")
        adjustment_pct = None
        
        for step in steps:
            from_val = Decimal(str(step.get("from", 0)))
            to_val = Decimal(str(step.get("to", float("inf"))))
            
            if from_val <= parameter_value <= to_val:
                adjustment = Decimal(str(step.get("adjustment_eur_per_ton", 0)))
                adjustment_pct = Decimal(str(step.get("adjustment_pct", 0))) if step.get("adjustment_pct") else None
                break
        
        result.adjustment_amount_eur_per_ton = adjustment
        result.adjustment_pct = adjustment_pct
    
    elif rule.method == "factor":
        # Faktor-basierte Berechnung
        base_factor = Decimal(str(rule.steps.get("base_factor", 1.0))) if rule.steps else Decimal("1.0")
        factor_per_unit = Decimal(str(rule.steps.get("factor_per_unit", 0))) if rule.steps else Decimal("0")
        
        # Beispiel: HL-Gewicht: (actual_hl - base_hl) * factor_per_0.1kg
        base_value = Decimal(str(rule.steps.get("base_value", 0))) if rule.steps else Decimal("0")
        diff = parameter_value - base_value
        adjustment = diff * factor_per_unit
        
        result.adjustment_amount_eur_per_ton = adjustment
        result.adjustment_pct = None
    
    elif rule.method == "percentage":
        # Prozentuale Anpassung
        base_pct = Decimal(str(rule.steps.get("base_pct", 0))) if rule.steps else Decimal("0")
        pct_per_unit = Decimal(str(rule.steps.get("pct_per_unit", 0))) if rule.steps else Decimal("0")
        
        # Beispiel: Besatz: (impurity_pct - base_pct) * pct_per_1pct
        diff = parameter_value - base_pct
        adjustment_pct = diff * pct_per_unit
        
        result.adjustment_amount_eur_per_ton = Decimal("0")  # Wird später auf Basispreis angewendet
        result.adjustment_pct = adjustment_pct
    
    else:
        return None
    
    return result


def apply_price_adjustments(
    db: Session,
    tenant_id: str,
    base_price_eur_per_ton: Decimal,
    article_id: Optional[str] = None,
    warengruppe: Optional[str] = None,
    hl_weight_kg_per_hl: Optional[Decimal] = None,
    impurity_pct: Optional[Decimal] = None,
    mycotoxin_ppb: Optional[Decimal] = None,
    effective_date: Optional[date] = None,
) -> tuple[Decimal, list[dict]]:
    """
    Wendet alle konfigurierten Preis-Anpassungen an.
    
    Returns:
        (final_price_eur_per_ton, adjustments): Finaler Preis und Liste der Anpassungen
    """
    final_price = base_price_eur_per_ton
    adjustments = []
    
    # HL-Gewicht Anpassung
    if hl_weight_kg_per_hl:
        result = calculate_price_adjustment(
            db, tenant_id, "hl_weight", hl_weight_kg_per_hl,
            article_id, warengruppe, effective_date,
        )
        if result:
            if result.adjustment_amount_eur_per_ton:
                final_price += result.adjustment_amount_eur_per_ton
                adjustments.append({
                    "type": "hl_weight",
                    "amount_eur_per_ton": float(result.adjustment_amount_eur_per_ton),
                    "method": result.method_used,
                })
            elif result.adjustment_pct:
                adjustment = base_price_eur_per_ton * (result.adjustment_pct / Decimal("100"))
                final_price += adjustment
                adjustments.append({
                    "type": "hl_weight",
                    "amount_eur_per_ton": float(adjustment),
                    "pct": float(result.adjustment_pct),
                    "method": result.method_used,
                })
    
    # Besatz Anpassung
    if impurity_pct:
        result = calculate_price_adjustment(
            db, tenant_id, "impurity", impurity_pct,
            article_id, warengruppe, effective_date,
        )
        if result:
            if result.adjustment_amount_eur_per_ton:
                final_price += result.adjustment_amount_eur_per_ton
                adjustments.append({
                    "type": "impurity",
                    "amount_eur_per_ton": float(result.adjustment_amount_eur_per_ton),
                    "method": result.method_used,
                })
            elif result.adjustment_pct:
                adjustment = base_price_eur_per_ton * (result.adjustment_pct / Decimal("100"))
                final_price += adjustment
                adjustments.append({
                    "type": "impurity",
                    "amount_eur_per_ton": float(adjustment),
                    "pct": float(result.adjustment_pct),
                    "method": result.method_used,
                })
    
    # Mykotoxin Anpassung
    if mycotoxin_ppb:
        result = calculate_price_adjustment(
            db, tenant_id, "mycotoxin", mycotoxin_ppb,
            article_id, warengruppe, effective_date,
        )
        if result:
            if result.adjustment_amount_eur_per_ton:
                final_price += result.adjustment_amount_eur_per_ton
                adjustments.append({
                    "type": "mycotoxin",
                    "amount_eur_per_ton": float(result.adjustment_amount_eur_per_ton),
                    "method": result.method_used,
                })
            elif result.adjustment_pct:
                adjustment = base_price_eur_per_ton * (result.adjustment_pct / Decimal("100"))
                final_price += adjustment
                adjustments.append({
                    "type": "mycotoxin",
                    "amount_eur_per_ton": float(adjustment),
                    "pct": float(result.adjustment_pct),
                    "method": result.method_used,
                })
    
    return final_price, adjustments


