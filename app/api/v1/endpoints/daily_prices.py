"""
Daily Price API endpoints.
Handles daily price management for dynamic pricing.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.data_quality_enforcement import (
    build_dq_error_detail,
    evaluate_daily_price_import_datensatz,
)
from app.core.tenant import get_tenant_id
from app.domains.inventory.api.inventory_auth import require_inventory_admin
from modules.agrar.services.daily_price_service import (
    create_daily_price,
    bulk_import_prices,
    get_price_history,
    DailyPriceCreate,
    DailyPriceFilter,
)
from modules.agrar.repositories.daily_price_repo import DailyPriceRepositoryImpl

router = APIRouter()


# ── Pydantic Models ───────────────────────────────────────────────────────────────

class DailyPriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Output-Model für Tagespreis."""
    id: str
    tenant_id: str
    article_id: Optional[str] = None
    warengruppe: Optional[str] = None
    crop_code: Optional[str] = None
    price_eur_per_ton: float
    currency: str
    price_date: date
    valid_from: datetime
    valid_to: Optional[datetime] = None
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class DailyPriceCreateIn(BaseModel):
    """Input-Model für Preis-Erstellung."""
    article_id: Optional[str] = None
    warengruppe: Optional[str] = None
    crop_code: Optional[str] = None
    price_eur_per_ton: float = Field(..., gt=0)
    currency: str = "EUR"
    price_date: date
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    source_type: str = "manual"
    source_id: Optional[str] = None
    source_name: Optional[str] = None


class DailyPriceBulkCreateIn(BaseModel):
    """Input-Model für Bulk-Import."""
    prices: list[DailyPriceCreateIn] = Field(..., min_length=1)


def _build_daily_price_dq_datensatz(payload: dict) -> dict:
    return {
        "article_id": payload.get("article_id") or payload.get("articleId"),
        "warengruppe": payload.get("warengruppe"),
        "crop_code": payload.get("crop_code") or payload.get("cropCode"),
        "price_eur_per_ton": payload.get("price_eur_per_ton") or payload.get("priceEurPerTon"),
        "currency": payload.get("currency", "EUR"),
        "price_date": payload.get("price_date") or payload.get("priceDate"),
        "source_type": payload.get("source_type") or payload.get("sourceType") or "manual",
    }


def _validate_daily_price_dq_datensatz(payload: dict) -> None:
    result = evaluate_daily_price_import_datensatz(_build_daily_price_dq_datensatz(payload))
    if not result.bestanden:
        raise HTTPException(
            status_code=422,
            detail=build_dq_error_detail("DailyPriceImport", result),
        )


# ── Helper Functions ────────────────────────────────────────────────────────────

def _get_user_id_from_request(request) -> Optional[str]:
    """Holt User-ID aus Request-Header oder Bearer-Token."""
    if request is None:
        return None
    # 1. Expliziter X-User-ID Header (API-Gateway/Proxy)
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id
    # 2. Bearer-Token: sub-Claim ohne Validierung auslesen (Validierung erfolgt in get_current_user)
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        try:
            import base64
            import json as _json
            payload_b64 = token.split(".")[1]
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            claims = _json.loads(base64.urlsafe_b64decode(payload_b64))
            return claims.get("sub")
        except Exception:  # noqa: BLE001 — JWT decode failed; caller handles None return
            pass
    return None


def _to_out(price) -> DailyPriceOut:
    """Konvertiert Service-Model zu Output-Model."""
    return DailyPriceOut(
        id=price.id,
        tenant_id=price.tenant_id,
        article_id=price.article_id,
        warengruppe=price.warengruppe,
        crop_code=price.crop_code,
        price_eur_per_ton=float(price.price_eur_per_ton),
        currency=price.currency,
        price_date=price.price_date,
        valid_from=price.valid_from,
        valid_to=price.valid_to,
        source_type=price.source_type,
        source_id=price.source_id,
        source_name=price.source_name,
        created_at=price.created_at,
        created_by=price.created_by,
        updated_at=price.updated_at,
        updated_by=price.updated_by,
    )


# ── API Endpoints ───────────────────────────────────────────────────────────────

@router.get("", response_model=list[DailyPriceOut])
async def get_prices(
    article_id: Optional[str] = Query(None),
    warengruppe: Optional[str] = Query(None),
    crop_code: Optional[str] = Query(None),
    price_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft Tagespreise ab (mit Filtern)."""
    repo = DailyPriceRepositoryImpl(db)
    
    filter = DailyPriceFilter(
        tenant_id=tenant_id,
        article_id=article_id,
        warengruppe=warengruppe,
        crop_code=crop_code,
        price_date=price_date,
    )
    
    price = repo.find_price(filter)
    
    if price:
        return [_to_out(price)]
    return []


@router.get("/{price_id}", response_model=DailyPriceOut)
async def get_price(
    price_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft einen Tagespreis ab."""
    repo = DailyPriceRepositoryImpl(db)
    price = repo.get_by_id(price_id)
    
    if not price:
        raise HTTPException(status_code=404, detail=f"Daily price {price_id} not found")
    
    if price.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return _to_out(price)


@router.post("", response_model=DailyPriceOut, status_code=201)
async def create_price(
    payload: DailyPriceCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
    _: str = Depends(require_inventory_admin),
):
    """Erstellt einen neuen Tagespreis (Admin-only)."""
    user_id = _get_user_id_from_request(request)
    
    create_input = DailyPriceCreate(
        tenant_id=tenant_id,
        article_id=payload.article_id,
        warengruppe=payload.warengruppe,
        crop_code=payload.crop_code,
        price_eur_per_ton=Decimal(str(payload.price_eur_per_ton)),
        currency=payload.currency,
        price_date=payload.price_date,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        source_type=payload.source_type,
        source_id=payload.source_id,
        source_name=payload.source_name,
        created_by=user_id,
    )
    
    repo = DailyPriceRepositoryImpl(db)
    price = create_daily_price(repo, create_input)
    
    return _to_out(price)


@router.post("/bulk-import", response_model=list[DailyPriceOut], status_code=201)
async def bulk_import_prices_endpoint(
    payload: DailyPriceBulkCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
    _: str = Depends(require_inventory_admin),
):
    """Importiert mehrere Tagespreise auf einmal (Admin-only)."""
    user_id = _get_user_id_from_request(request)
    
    create_inputs = []
    for p in payload.prices:
        _validate_daily_price_dq_datensatz(p.model_dump(mode="json"))
        create_inputs.append(DailyPriceCreate(
            tenant_id=tenant_id,
            article_id=p.article_id,
            warengruppe=p.warengruppe,
            crop_code=p.crop_code,
            price_eur_per_ton=Decimal(str(p.price_eur_per_ton)),
            currency=p.currency,
            price_date=p.price_date,
            valid_from=p.valid_from,
            valid_to=p.valid_to,
            source_type=p.source_type,
            source_id=p.source_id,
            source_name=p.source_name,
            created_by=user_id,
        ))
    
    repo = DailyPriceRepositoryImpl(db)
    prices = bulk_import_prices(repo, tenant_id, create_inputs, created_by=user_id)
    
    return [_to_out(p) for p in prices]


@router.post("/import", response_model=list[DailyPriceOut], status_code=201)
async def import_prices_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
    _: str = Depends(require_inventory_admin),
):
    """Importiert Tagespreise aus CSV oder JSON-Datei."""
    user_id = _get_user_id_from_request(request)
    content = (await file.read()).decode("utf-8")
    name = file.filename or "import"

    if name.lower().endswith(".json"):
        import json
        data = json.loads(content)
        prices_list = data.get("prices", data) if isinstance(data, dict) else data
        if not isinstance(prices_list, list):
            raise HTTPException(status_code=400, detail="JSON muss 'prices'-Array enthalten oder Array sein")
    else:
        import csv
        import io
        reader = csv.DictReader(io.StringIO(content))
        prices_list = list(reader)

    from datetime import datetime, date

    create_inputs = []
    for p in prices_list:
        d = p if isinstance(p, dict) else {}
        _validate_daily_price_dq_datensatz(d)
        price_date = d.get("price_date") or d.get("priceDate")
        if isinstance(price_date, str):
            price_date = date.fromisoformat(price_date[:10])
        vf = d.get("valid_from") or d.get("validFrom")
        vt = d.get("valid_to") or d.get("validTo")
        create_inputs.append(
            DailyPriceCreate(
                tenant_id=tenant_id,
                article_id=d.get("article_id") or d.get("articleId"),
                warengruppe=d.get("warengruppe"),
                crop_code=d.get("crop_code") or d.get("cropCode"),
                price_eur_per_ton=Decimal(str(d.get("price_eur_per_ton") or d.get("priceEurPerTon") or 0)),
                currency=d.get("currency", "EUR"),
                price_date=price_date,
                valid_from=datetime.fromisoformat(str(vf)[:19]) if vf else None,
                valid_to=datetime.fromisoformat(str(vt)[:19]) if vt else None,
                source_type=d.get("source_type") or d.get("sourceType") or "manual",
                source_id=d.get("source_id") or d.get("sourceId"),
                source_name=d.get("source_name") or d.get("sourceName"),
                created_by=user_id,
            )
        )

    repo = DailyPriceRepositoryImpl(db)
    prices = bulk_import_prices(repo, tenant_id, create_inputs, created_by=user_id)
    return [_to_out(p) for p in prices]


class PriceRuleEvaluateIn(BaseModel):
    quality_values: dict = Field(..., description="z.B. moisture_pct, hl_weight, impurity_pct")
    base_price_eur_per_ton: float = Field(..., gt=0)
    commodity: Optional[str] = None
    warengruppe: Optional[str] = None


class PriceRuleEvaluateOut(BaseModel):
    base_price_eur_per_ton: float
    adjustments: list[dict]
    final_price_eur_per_ton: float


@router.post("/price-rules/evaluate", response_model=PriceRuleEvaluateOut)
async def evaluate_price_rules(
    payload: PriceRuleEvaluateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Berechnet Zu-/Abschläge basierend auf Qualität + Preisregeln."""
    # Placeholder: Nutzt price_adjustment_rules wenn vorhanden
    adjustments = []
    final_price = payload.base_price_eur_per_ton
    for k, v in (payload.quality_values or {}).items():
        if k == "moisture_pct" and v is not None:
            adj = float(v) * -0.5  # Beispiel: -0.5 EUR pro % Feuchte
            adjustments.append({"parameter": k, "value": v, "adjustment_eur": adj})
            final_price += adj
        elif k == "impurity_pct" and v is not None:
            adj = float(v) * -2
            adjustments.append({"parameter": k, "value": v, "adjustment_eur": adj})
            final_price += adj
    return PriceRuleEvaluateOut(
        base_price_eur_per_ton=payload.base_price_eur_per_ton,
        adjustments=adjustments,
        final_price_eur_per_ton=round(final_price, 2),
    )


@router.get("/{article_id}/history", response_model=list[DailyPriceOut])
async def get_price_history_endpoint(
    article_id: str,
    warengruppe: Optional[str] = Query(None),
    crop_code: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft Preis-Historie ab."""
    repo = DailyPriceRepositoryImpl(db)
    prices = get_price_history(
        repo,
        tenant_id=tenant_id,
        article_id=article_id if article_id != "all" else None,
        warengruppe=warengruppe,
        crop_code=crop_code,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )
    
    return [_to_out(p) for p in prices]


