"""Pricing calculation endpoints with hierarchical cascade logic."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/pricing", tags=["pricing"])

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class PriceCalculationRequest(BaseModel):
    article_id: str
    customer_id: Optional[str] = None
    quantity: Decimal = Field(default=Decimal("1"), ge=Decimal("0"))
    contract_id: Optional[str] = None
    user_role: Optional[str] = None


class PriceCalculationResponse(BaseModel):
    list_price: Decimal
    discount: Decimal
    net_price: Decimal
    source: str  # 'base', 'price_list', 'contract', 'customer_discount', 'employee_discount'
    price_list_id: Optional[str] = None
    contract_id: Optional[str] = None


@router.get("/calculate", response_model=PriceCalculationResponse, summary="Price berechnen")
async def calculate_price(
    article_id: str = Query(..., description="Article ID"),
    customer_id: Optional[str] = Query(None, description="Customer ID"),
    quantity: Decimal = Query(Decimal("1"), ge=Decimal("0"), description="Quantity"),
    contract_id: Optional[str] = Query(None, description="Contract ID"),
    user_role: Optional[str] = Query(None, description="User role for employee discounts"),
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """
    Calculate price with hierarchical cascade logic (like zvoove/Landhandel):
    
    Priority:
    1. Price list (highest priority, replaces base price)
    2. Contract discount (if contract_id provided)
    3. Customer discount (from customer master data)
    4. Employee role discount (if user_role provided)
    5. Base price (fallback)
    
    Only ONE discount is applied (not additive).
    """
    # 1. Get base price from article
    article = db.execute(
        text("""
            SELECT sales_price, warengruppe, category 
            FROM domain_inventory.articles 
            WHERE id = :id AND tenant_id = :tenant_id AND is_active = TRUE
        """),
        {"id": article_id, "tenant_id": tenant_id}
    ).mappings().first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    base_price = Decimal(str(article["sales_price"] or 0))
    article_group = article["warengruppe"] or article["category"]
    
    list_price = base_price
    discount = Decimal("0")
    source = "base"
    price_list_id = None
    contract_id_result = None
    
    # 2. Check for price list (highest priority - replaces base price)
    # Suche nach Preisliste für Artikel-ID, Artikelnummer oder Artikelgruppe
    article_number = db.execute(
        text("""
            SELECT article_number 
            FROM domain_inventory.articles 
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": article_id, "tenant_id": tenant_id}
    ).scalar()
    
    if article_number or article_group:
        # Suche Preisliste nach Artikelnummer, Artikel-ID oder Artikelgruppe
        price_list = db.execute(
            text("""
                SELECT id, lines::jsonb 
                FROM domain_pricing.price_lists 
                WHERE tenant_id = :tenant_id 
                AND status = 'Active'
                AND valid_from <= NOW()
                AND (valid_to IS NULL OR valid_to >= NOW())
                ORDER BY valid_from DESC
                LIMIT 1
            """),
            {"tenant_id": tenant_id}
        ).mappings().first()
        
        if price_list:
            lines = price_list["lines"]
            if isinstance(lines, str):
                lines = json.loads(lines)
            
            # Suche passende Line: zuerst nach Artikel-ID, dann Artikelnummer, dann Artikelgruppe
            matching_line = None
            if isinstance(lines, list):
                for line in lines:
                    # Prüfe ob Line aktiv ist
                    if not line.get("active", True):
                        continue
                    
                    # Prüfe nach Artikel-ID (wenn in Line gespeichert)
                    if line.get("article_id") == article_id:
                        matching_line = line
                        break
                    
                    # Prüfe nach Artikelnummer (sku)
                    if line.get("sku") == article_number:
                        matching_line = line
                        break
                    
                    # Prüfe nach Artikelgruppe (wenn in Line gespeichert)
                    if article_group and line.get("article_group") == article_group:
                        matching_line = line
                        break
            
            if matching_line:
                # Basispreis aus Line
                base_price_from_line = Decimal(str(matching_line.get("basePrice", base_price)))
                
                # Prüfe Mengenstaffeln (tier breaks)
                tier_breaks = matching_line.get("tierBreaks", [])
                if tier_breaks and isinstance(tier_breaks, list):
                    # Sortiere Staffeln nach minQty (absteigend), um die höchste passende zu finden
                    applicable_tier = None
                    for tier in sorted(tier_breaks, key=lambda t: t.get("minQty", 0), reverse=True):
                        min_qty = Decimal(str(tier.get("minQty", 0)))
                        max_qty = tier.get("maxQty")
                        
                        if quantity >= min_qty:
                            if max_qty is None or quantity <= Decimal(str(max_qty)):
                                applicable_tier = tier
                                break
                    
                    if applicable_tier:
                        # Verwende Preis aus Staffel
                        list_price = Decimal(str(applicable_tier.get("price", base_price_from_line)))
                    else:
                        # Keine passende Staffel, verwende Basispreis
                        list_price = base_price_from_line
                else:
                    # Keine Staffeln, verwende Basispreis
                    list_price = base_price_from_line
                
                source = "price_list"
                price_list_id = price_list["id"]
    
    # 3. Check for contract discount (if contract_id provided)
    if contract_id:
        contract = db.execute(
            text("""
                SELECT discount_percent, discount_amount 
                FROM domain_contracts.contracts 
                WHERE id = :id AND tenant_id = :tenant_id AND status = 'active'
            """),
            {"id": contract_id, "tenant_id": tenant_id}
        ).mappings().first()
        
        if contract:
            if contract["discount_percent"]:
                discount = Decimal(str(contract["discount_percent"]))
                source = "contract"
                contract_id_result = contract_id
            elif contract["discount_amount"]:
                # Convert fixed amount to percentage (simplified)
                discount = (Decimal(str(contract["discount_amount"])) / list_price) * 100
                source = "contract"
                contract_id_result = contract_id
    
    # 4. Check for customer discount (only if no contract discount)
    if source == "base" and customer_id:
        customer = db.execute(
            text("""
                SELECT discount, discount_percent 
                FROM domain_crm.customers 
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {"id": customer_id, "tenant_id": tenant_id}
        ).mappings().first()
        
        if customer:
            if customer["discount_percent"]:
                discount = Decimal(str(customer["discount_percent"]))
                source = "customer_discount"
            elif customer["discount"]:
                discount = Decimal(str(customer["discount"]))
                source = "customer_discount"
    
    # 5. Check for employee role discount (only if no customer discount)
    if source in ("base", "price_list") and user_role:
        role_discount = db.execute(
            text("""
                SELECT discount_percent 
                FROM domain_pricing.discount_rules 
                WHERE tenant_id = :tenant_id 
                AND role = :role 
                AND is_active = TRUE
                LIMIT 1
            """),
            {"tenant_id": tenant_id, "role": user_role}
        ).scalar()
        
        if role_discount:
            discount = Decimal(str(role_discount))
            source = "employee_discount"
    
    # Calculate net price
    net_price = list_price * (1 - discount / 100)
    
    return PriceCalculationResponse(
        list_price=list_price,
        discount=discount,
        net_price=net_price,
        source=source,
        price_list_id=price_list_id,
        contract_id=contract_id_result,
    )


