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

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/pricing", tags=["pricing"])

# Alias-Prefix für Frontend-Konvention /preise/* — wird in api.py parallel eingebunden.

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
        # Suche Preislisten-Item für diesen Artikel (echtes Schema: price_list_items)
        price_item = db.execute(
            text("""
                SELECT pli.id, pli.price_list_id, pli.unit_price, pli.discount_percent,
                       pl.name AS pl_name
                FROM domain_pricing.price_list_items pli
                JOIN domain_pricing.price_lists pl ON pl.id = pli.price_list_id
                WHERE pl.tenant_id = :tenant_id
                  AND pl.is_active = TRUE
                  AND (pl.valid_from IS NULL OR pl.valid_from <= CURRENT_DATE)
                  AND (pl.valid_until IS NULL OR pl.valid_until >= CURRENT_DATE)
                  AND (pli.article_id = :article_id OR pli.article_number = :article_number)
                  AND (pli.valid_from IS NULL OR pli.valid_from <= CURRENT_DATE)
                  AND (pli.valid_until IS NULL OR pli.valid_until >= CURRENT_DATE)
                  AND (pli.min_quantity IS NULL OR pli.min_quantity <= :quantity)
                ORDER BY pli.min_quantity DESC NULLS LAST
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id,
                "article_id": article_id,
                "article_number": article_number or "",
                "quantity": float(quantity),
            }
        ).mappings().first()

        if price_item:
            if price_item["unit_price"] is not None:
                list_price = Decimal(str(price_item["unit_price"]))
            if price_item["discount_percent"] is not None:
                discount = Decimal(str(price_item["discount_percent"]))
            source = "price_list"
            price_list_id = price_item["price_list_id"]
    
    # 3. Check for contract discount (if contract_id provided)
    # domain_contracts schema may not exist — skip gracefully
    if contract_id:
        try:
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
                elif contract["discount_amount"] and list_price > 0:
                    discount = (Decimal(str(contract["discount_amount"])) / list_price) * 100
                    source = "contract"
                    contract_id_result = contract_id
        except Exception:
            db.rollback()

    # 4. Check for customer discount (only if no contract discount)
    if source in ("base", "price_list") and customer_id:
        try:
            from app.services.business_partner_service import BusinessPartnerService
            cust_discount = BusinessPartnerService(db, tenant_id).get_customer_discount(customer_id)
            if cust_discount is not None:
                discount = cust_discount
                source = "customer_discount"
        except Exception:
            db.rollback()

    # 5. Check for employee role discount — domain_pricing.discount_rules may not exist
    if source in ("base", "price_list") and user_role:
        try:
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
        except Exception:
            db.rollback()
    
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


@router.get(
    "/find",
    response_model=PriceCalculationResponse,
    summary="Preisfindung (Frontend-Alias für /calculate)",
)
async def find_price(
    article_id: str = Query(...),
    customer_id: Optional[str] = Query(None),
    quantity: Decimal = Query(Decimal("1"), ge=Decimal("0")),
    contract_id: Optional[str] = Query(None),
    user_role: Optional[str] = Query(None),
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Frontend-Alias für /pricing/calculate — identische Logik."""
    return await calculate_price(
        article_id=article_id,
        customer_id=customer_id,
        quantity=quantity,
        contract_id=contract_id,
        user_role=user_role,
        tenant_id=tenant_id,
        db=db,
    )


# ---------------------------------------------------------------------------
# Staffelrabatte  GET/POST /pricing/staffelrabatte
# ---------------------------------------------------------------------------

class StaffelStufe(BaseModel):
    ab_menge: Decimal = Field(..., ge=Decimal("0"), description="Ab dieser Menge gilt der Rabatt")
    rabatt_prozent: Optional[Decimal] = Field(None, description="Rabatt in Prozent")
    festpreis: Optional[Decimal] = Field(None, description="Festpreis statt Rabatt")


class StaffelrabattIn(BaseModel):
    artikel_id: Optional[str] = Field(None)
    artikel_ids: Optional[list[str]] = Field(None, description="Mehrere Artikel gleichzeitig zuordnen (M2M)")
    artikelgruppe: Optional[str] = Field(None)
    kunden_id: Optional[str] = Field(None)
    kundengruppe: Optional[str] = Field(None)
    gueltig_von: Optional[str] = Field(None)
    gueltig_bis: Optional[str] = Field(None)
    stufen: list[StaffelStufe] = Field(..., min_length=1)
    bezeichnung: Optional[str] = Field(None)


class StaffelrabattOut(BaseModel):
    id: str
    artikel_id: Optional[str]
    artikel_ids: list[str] = Field(default_factory=list)
    artikelgruppe: Optional[str]
    kunden_id: Optional[str]
    kundengruppe: Optional[str]
    gueltig_von: Optional[str]
    gueltig_bis: Optional[str]
    stufen: list[StaffelStufe]
    bezeichnung: Optional[str]
    tenant_id: str
    status: str


@router.get(
    "/staffelrabatte",
    response_model=list[StaffelrabattOut],
    summary="Staffelrabatte auflisten",
)
async def list_staffelrabatte(
    artikel_id: Optional[str] = Query(None),
    kunden_id: Optional[str] = Query(None),
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
) -> list[StaffelrabattOut]:
    """Staffelrabatte abfragen — filterbar nach Artikel und Kunde."""
    import json as _json

    conditions = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id}
    if artikel_id:
        conditions.append("artikel_id = :artikel_id")
        params["artikel_id"] = artikel_id
    if kunden_id:
        conditions.append("kunden_id = :kunden_id")
        params["kunden_id"] = kunden_id

    where = " AND ".join(conditions)
    rows = db.execute(
        # nosec S608 — where besteht nur aus festen Literalen dieser Funktion, alle Werte via Bind-Params
        text(f"SELECT * FROM domain_pricing.staffelrabatte WHERE {where} ORDER BY created_at DESC"),
        params,
    ).mappings().all()

    ids = [r["id"] for r in rows]
    artikel_ids_by_staffel: dict[str, list[str]] = {i: [] for i in ids}
    if ids:
        m2m_rows = db.execute(
            text("""
                SELECT staffelrabatt_id, artikel_id FROM domain_pricing.staffelrabatt_artikel
                WHERE tenant_id = :tenant_id AND staffelrabatt_id = ANY(:ids)
            """),
            {"tenant_id": tenant_id, "ids": ids},
        ).mappings().all()
        for m in m2m_rows:
            artikel_ids_by_staffel.setdefault(m["staffelrabatt_id"], []).append(m["artikel_id"])

    result = []
    for r in rows:
        stufen_raw = r["stufen"]
        if isinstance(stufen_raw, str):
            stufen_raw = _json.loads(stufen_raw)
        result.append(
            StaffelrabattOut(
                id=r["id"],
                artikel_id=r.get("artikel_id"),
                artikel_ids=artikel_ids_by_staffel.get(r["id"], []),
                artikelgruppe=r.get("artikelgruppe"),
                kunden_id=r.get("kunden_id"),
                kundengruppe=r.get("kundengruppe"),
                gueltig_von=str(r["gueltig_von"]) if r.get("gueltig_von") else None,
                gueltig_bis=str(r["gueltig_bis"]) if r.get("gueltig_bis") else None,
                stufen=[StaffelStufe(**s) for s in stufen_raw],
                bezeichnung=r.get("bezeichnung"),
                tenant_id=r["tenant_id"],
                status=r.get("status", "aktiv"),
            )
        )
    return result


@router.post(
    "/staffelrabatte",
    response_model=StaffelrabattOut,
    status_code=201,
    summary="Staffelrabatt anlegen",
)
async def create_staffelrabatt(
    payload: StaffelrabattIn,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
) -> StaffelrabattOut:
    """Staffelrabatt anlegen (Mengen-/Preisstufen für Artikel oder Artikelgruppe)."""
    import json as _json
    from uuid import uuid4 as _uuid4

    if not payload.artikel_id and not payload.artikelgruppe:
        raise HTTPException(status_code=422, detail="artikel_id oder artikelgruppe erforderlich")

    new_id = str(_uuid4())
    stufen_json = _json.dumps([s.model_dump(mode="json") for s in payload.stufen])

    try:
        db.execute(
            text("""
                INSERT INTO domain_pricing.staffelrabatte
                    (id, tenant_id, artikel_id, artikelgruppe, kunden_id, kundengruppe,
                     gueltig_von, gueltig_bis, stufen, bezeichnung, status)
                VALUES
                    (:id, :tenant_id, :artikel_id, :artikelgruppe, :kunden_id, :kundengruppe,
                     :gueltig_von, :gueltig_bis, CAST(:stufen AS jsonb), :bezeichnung, 'aktiv')
            """),
            {
                "id": new_id,
                "tenant_id": tenant_id,
                "artikel_id": payload.artikel_id,
                "artikelgruppe": payload.artikelgruppe,
                "kunden_id": payload.kunden_id,
                "kundengruppe": payload.kundengruppe,
                "gueltig_von": payload.gueltig_von,
                "gueltig_bis": payload.gueltig_bis,
                "stufen": stufen_json,
                "bezeichnung": payload.bezeichnung,
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return StaffelrabattOut(
        id=new_id,
        artikel_id=payload.artikel_id,
        artikelgruppe=payload.artikelgruppe,
        kunden_id=payload.kunden_id,
        kundengruppe=payload.kundengruppe,
        gueltig_von=payload.gueltig_von,
        gueltig_bis=payload.gueltig_bis,
        stufen=payload.stufen,
        bezeichnung=payload.bezeichnung,
        tenant_id=tenant_id,
        status="aktiv",
    )

