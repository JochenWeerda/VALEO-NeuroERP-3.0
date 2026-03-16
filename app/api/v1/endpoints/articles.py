"""Inventory Articles management endpoints."""

from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_, func, text
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.data_quality_enforcement import build_dq_error_detail, evaluate_article_datensatz
from ....core.database import get_db
from ....infrastructure.models import Article as ArticleModel
from ....infrastructure.models import BusinessPartnerDiscountItem, BusinessPartnerPriceAgreement, ArticleSupplier, ArticleDocument
from ....infrastructure.models import StockMovement
from ..schemas.base import PaginatedResponse
from ..schemas.inventory import Article, ArticleCreate, ArticleUpdate

router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


def _build_article_dq_datensatz(data: dict) -> dict[str, object]:
    return {
        "artikel_nr": data.get("article_number"),
        "bezeichnung": data.get("name"),
        "einheit": data.get("unit"),
        "mehrwertsteuersatz_pct": float(data["mehrwertsteuer_prozent"]) if data.get("mehrwertsteuer_prozent") is not None else None,
        "ean_code": data.get("ean_code") or data.get("barcode"),
    }


def _fulltext_filter(query, search_term: str):
    """Apply PostgreSQL fulltext search with relevance ranking.

    For terms >= 2 chars, uses plainto_tsquery against the GIN-indexed
    search_vector column.  Falls back to ILIKE for very short terms
    where stemming adds no value.

    Returns (filtered_query, rank_column_or_None).
    """
    if len(search_term) < 2:
        like = f"%{search_term}%"
        return query.filter(
            or_(
                ArticleModel.name.ilike(like),
                ArticleModel.article_number.ilike(like),
            )
        ), None

    ts_query = func.plainto_tsquery(text("'german'"), search_term)
    rank = func.ts_rank(ArticleModel.search_vector, ts_query)

    # Fulltext match OR ILIKE fallback (covers partial matches the stemmer misses)
    like = f"%{search_term}%"
    filtered = query.filter(
        or_(
            ArticleModel.search_vector.op("@@")(ts_query),
            ArticleModel.name.ilike(like),
            ArticleModel.article_number.ilike(like),
            ArticleModel.barcode.ilike(like),
        )
    )
    return filtered, rank


def _to_article_schema(row: ArticleModel) -> Article:
    return Article.model_validate(
        {
            "id": str(row.id),
            "tenant_id": str(row.tenant_id),
            "article_number": row.article_number,
            "name": row.name,
            "description": row.description,
            "description2": getattr(row, 'description2', None),
            "short_description": getattr(row, 'short_description', None),
            "suchbegriff": row.suchbegriff,
            "matchcode2": getattr(row, 'matchcode2', None),
            "hersteller": row.hersteller,
            "herkunftsland": row.herkunftsland,
            "naehrwertangaben": row.naehrwertangaben,
            "mhd_erforderlich": bool(row.mhd_erforderlich),
            "lagerartikel": bool(row.lagerartikel),
            "mehrwertsteuer_prozent": row.mehrwertsteuer_prozent,
            "warengruppe": row.warengruppe,
            "gefahrgutklasse": row.gefahrgutklasse,
            # Extended dangerous goods fields
            "gefahrgut_un_nummer": getattr(row, 'gefahrgut_un_nummer', None),
            "gefahrgut_verpackungsgruppe": getattr(row, 'gefahrgut_verpackungsgruppe', None),
            "gefahrgut_anhaenge": getattr(row, 'gefahrgut_anhaenge', None),
            "lagerorte": row.lagerorte or [],
            "chargenpflicht": bool(row.chargenpflicht),
            "qs_pruefung_erforderlich": bool(row.qs_pruefung_erforderlich),
            "zolltarifnummer": row.zolltarifnummer,
            "bio_kennzeichnung": bool(row.bio_kennzeichnung),
            "gmp_plus_relevanz": bool(row.gmp_plus_relevanz),
            # Extended labeling fields
            "kennzeichnung_bio": getattr(row, 'kennzeichnung_bio', None),
            "kennzeichnung_vegan": getattr(row, 'kennzeichnung_vegan', None),
            "kennzeichnung_vegetarisch": getattr(row, 'kennzeichnung_vegetarisch', None),
            "kennzeichnung_allergene": getattr(row, 'kennzeichnung_allergene', None),
            "kennzeichnung_herkunft": getattr(row, 'kennzeichnung_herkunft', None),
            # Extended storage fields
            "lager_min_temperatur": getattr(row, 'lager_min_temperatur', None),
            "lager_max_temperatur": getattr(row, 'lager_max_temperatur', None),
            "lager_lagerdauer_tage": getattr(row, 'lager_lagerdauer_tage', None),
            "lager_zentral": getattr(row, 'lager_zentral', False),
            "lager_silo": getattr(row, 'lager_silo', False),
            # Extended analysis fields
            "analyse_protein": getattr(row, 'analyse_protein', None),
            "analyse_feuchtigkeit": getattr(row, 'analyse_feuchtigkeit', None),
            "analyse_schadex": getattr(row, 'analyse_schadex', None),
            "analyse_fremdstoffe": getattr(row, 'analyse_fremdstoffe', None),
            "analyse_sonstiges": getattr(row, 'analyse_sonstiges', None),
            # Search filter fields
            "ean_code": getattr(row, 'ean_code', None),
            "alt_ean_code": getattr(row, 'alt_ean_code', None),
            "lieferanten_artikelnummer": getattr(row, 'lieferanten_artikelnummer', None),
            "kunden_artikelnummer": getattr(row, 'kunden_artikelnummer', None),
            "verwendungszweck": getattr(row, 'verwendungszweck', None),
            "nachhaltige_biomasse": getattr(row, 'nachhaltige_biomasse', False),
            "pool_artikel": getattr(row, 'pool_artikel', False),
            # Discount/Surcharge fields
            "rabatt_auftrag_rechnung": getattr(row, 'rabatt_auftrag_rechnung', None),
            "rabatt_lose": getattr(row, 'rabatt_lose', None),
            "rabatt_selbstabholer": getattr(row, 'rabatt_selbstabholer', None),
            "zu_abschlag_1_code": getattr(row, 'zu_abschlag_1_code', None),
            "zu_abschlag_1_prozent": getattr(row, 'zu_abschlag_1_prozent', None),
            "zu_abschlag_2_code": getattr(row, 'zu_abschlag_2_code', None),
            "zu_abschlag_2_prozent": getattr(row, 'zu_abschlag_2_prozent', None),
            "berechne_zu_abschlag_auf_netto": getattr(row, 'berechne_zu_abschlag_auf_netto', False),
            "einfuegen_summe_nach_zu_abschlag": getattr(row, 'einfuegen_summe_nach_zu_abschlag', False),
            # Discount flags
            "skontofaehig": getattr(row, 'skontofaehig', True),
            "warenrueckverguetung": getattr(row, 'warenrueckverguetung', False),
            "bonus_faehig": getattr(row, 'bonus_faehig', False),
            "rabattfaehig": getattr(row, 'rabattfaehig', True),
            "lieferantennummer": row.lieferantennummer,
            "unit": row.unit,
            "category": row.category,
            "subcategory": row.subcategory,
            "barcode": row.barcode,
            "supplier_number": row.supplier_number,
            "customer_article_number": getattr(row, 'customer_article_number', None),
            "purchase_price": row.purchase_price,
            "sales_price": row.sales_price,
            "currency": row.currency or "EUR",
            "min_stock": row.min_stock,
            "max_stock": row.max_stock,
            "weight": row.weight,
            "dimensions": row.dimensions,
            "current_stock": row.current_stock or 0,
            "reserved_stock": row.reserved_stock or 0,
            "available_stock": row.available_stock or 0,
            "is_active": row.is_active,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "deleted_at": row.deleted_at,
        }
    )


@router.get("/", response_model=PaginatedResponse[Article])
async def list_articles(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    search: Optional[str] = Query(None, description="Search in name, number or barcode"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of articles."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(ArticleModel).filter(ArticleModel.is_active == True)  # noqa: E712
    query = query.filter(ArticleModel.tenant_id == effective_tenant)

    rank = None
    if search:
        query, rank = _fulltext_filter(query, search)

    total = query.count()
    if rank is not None:
        query = query.order_by(rank.desc())
    items = query.offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse[Article](
        items=[_to_article_schema(item) for item in items],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/search", response_model=list[Article])
async def search_articles(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
):
    """Lightweight search endpoint used by the POS to power autocomplete."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    query = (
        db.query(ArticleModel)
        .filter(ArticleModel.is_active == True)  # noqa: E712
        .filter(ArticleModel.tenant_id == effective_tenant)
    )

    query, rank = _fulltext_filter(query, q)

    if rank is not None:
        query = query.order_by(rank.desc())
    else:
        query = query.order_by(ArticleModel.name.asc())

    query = query.limit(limit)

    return [_to_article_schema(item) for item in query.all()]


@router.get("/{article_id}", response_model=Article)
async def get_article(
    article_id: str,
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    db: Session = Depends(get_db),
):
    """Fetch a single article by identifier."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    article = (
        db.query(ArticleModel)
        .filter(
            ArticleModel.id == article_id,
            ArticleModel.tenant_id == effective_tenant,
            ArticleModel.is_active == True,  # noqa: E712
            ArticleModel.deleted_at.is_(None),
        )
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return _to_article_schema(article)


@router.post("/", response_model=Article, status_code=status.HTTP_201_CREATED)
async def create_article(article_data: ArticleCreate, db: Session = Depends(get_db)):
    """Create a new article."""
    dq_result = evaluate_article_datensatz(_build_article_dq_datensatz(article_data.model_dump()))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("Artikel", dq_result))

    duplicate = (
        db.query(ArticleModel)
        .filter(
            ArticleModel.tenant_id == article_data.tenant_id,
            ArticleModel.article_number == article_data.article_number,
            ArticleModel.deleted_at.is_(None),
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Article number already exists")

    article = ArticleModel(
        tenant_id=article_data.tenant_id,
        article_number=article_data.article_number,
        name=article_data.name,
        description=article_data.description,
        description2=article_data.description2,
        short_description=article_data.short_description,
        suchbegriff=article_data.suchbegriff,
        matchcode2=article_data.matchcode2,
        hersteller=article_data.hersteller,
        herkunftsland=article_data.herkunftsland,
        naehrwertangaben=article_data.naehrwertangaben,
        mhd_erforderlich=article_data.mhd_erforderlich,
        lagerartikel=article_data.lagerartikel,
        mehrwertsteuer_prozent=article_data.mehrwertsteuer_prozent,
        warengruppe=article_data.warengruppe,
        gefahrgutklasse=article_data.gefahrgutklasse,
        gefahrgut_un_nummer=article_data.gefahrgut_un_nummer,
        gefahrgut_verpackungsgruppe=article_data.gefahrgut_verpackungsgruppe,
        gefahrgut_anhaenge=article_data.gefahrgut_anhaenge,
        lagerorte=article_data.lagerorte,
        chargenpflicht=article_data.chargenpflicht,
        qs_pruefung_erforderlich=article_data.qs_pruefung_erforderlich,
        zolltarifnummer=article_data.zolltarifnummer,
        bio_kennzeichnung=article_data.bio_kennzeichnung,
        gmp_plus_relevanz=article_data.gmp_plus_relevanz,
        kennzeichnung_bio=article_data.kennzeichnung_bio,
        kennzeichnung_vegan=article_data.kennzeichnung_vegan,
        kennzeichnung_vegetarisch=article_data.kennzeichnung_vegetarisch,
        kennzeichnung_allergene=article_data.kennzeichnung_allergene,
        kennzeichnung_herkunft=article_data.kennzeichnung_herkunft,
        lager_min_temperatur=article_data.lager_min_temperatur,
        lager_max_temperatur=article_data.lager_max_temperatur,
        lager_lagerdauer_tage=article_data.lager_lagerdauer_tage,
        lager_zentral=article_data.lager_zentral,
        lager_silo=article_data.lager_silo,
        analyse_protein=article_data.analyse_protein,
        analyse_feuchtigkeit=article_data.analyse_feuchtigkeit,
        analyse_schadex=article_data.analyse_schadex,
        analyse_fremdstoffe=article_data.analyse_fremdstoffe,
        analyse_sonstiges=article_data.analyse_sonstiges,
        # New search filter fields
        ean_code=article_data.ean_code,
        alt_ean_code=article_data.alt_ean_code,
        lieferanten_artikelnummer=article_data.lieferanten_artikelnummer,
        kunden_artikelnummer=article_data.kunden_artikelnummer,
        verwendungszweck=article_data.verwendungszweck,
        nachhaltige_biomasse=article_data.nachhaltige_biomasse,
        pool_artikel=article_data.pool_artikel,
        # Discount/Surcharge fields
        rabatt_auftrag_rechnung=article_data.rabatt_auftrag_rechnung,
        rabatt_lose=article_data.rabatt_lose,
        rabatt_selbstabholer=article_data.rabatt_selbstabholer,
        zu_abschlag_1_code=article_data.zu_abschlag_1_code,
        zu_abschlag_1_prozent=article_data.zu_abschlag_1_prozent,
        zu_abschlag_2_code=article_data.zu_abschlag_2_code,
        zu_abschlag_2_prozent=article_data.zu_abschlag_2_prozent,
        berechne_zu_abschlag_auf_netto=article_data.berechne_zu_abschlag_auf_netto,
        einfuegen_summe_nach_zu_abschlag=article_data.einfuegen_summe_nach_zu_abschlag,
        # Discount flags
        skontofaehig=article_data.skontofaehig,
        warenrueckverguetung=article_data.warenrueckverguetung,
        bonus_faehig=article_data.bonus_faehig,
        rabattfaehig=article_data.rabattfaehig,
        # Basic fields
        lieferantennummer=article_data.lieferantennummer,
        unit=article_data.unit,
        category=article_data.category,
        subcategory=article_data.subcategory,
        barcode=article_data.barcode,
        supplier_number=article_data.supplier_number,
        customer_article_number=article_data.customer_article_number,
        purchase_price=article_data.purchase_price,
        sales_price=article_data.sales_price,
        currency=article_data.currency,
        min_stock=article_data.min_stock,
        max_stock=article_data.max_stock,
        weight=article_data.weight,
        dimensions=article_data.dimensions,
        current_stock=0,
        reserved_stock=0,
        available_stock=0,
        is_active=True,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return _to_article_schema(article)


@router.put("/{article_id}", response_model=Article)
async def update_article(
    article_id: str,
    article_data: ArticleUpdate,
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    db: Session = Depends(get_db),
):
    """Update an existing article."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    article = (
        db.query(ArticleModel)
        .filter(
            ArticleModel.id == article_id,
            ArticleModel.tenant_id == effective_tenant,
            ArticleModel.is_active == True,  # noqa: E712
            ArticleModel.deleted_at.is_(None),
        )
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    payload = article_data.model_dump(exclude_unset=True)
    new_number = payload.get("article_number")
    if new_number and new_number != article.article_number:
        duplicate = (
            db.query(ArticleModel)
            .filter(
                ArticleModel.tenant_id == effective_tenant,
                ArticleModel.article_number == new_number,
                ArticleModel.id != article_id,
                ArticleModel.deleted_at.is_(None),
            )
            .first()
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Article number already exists")

    effective_payload = {
        "article_number": payload.get("article_number", article.article_number),
        "name": payload.get("name", article.name),
        "unit": payload.get("unit", article.unit),
        "mehrwertsteuer_prozent": payload.get("mehrwertsteuer_prozent", article.mehrwertsteuer_prozent),
        "ean_code": payload.get("ean_code", getattr(article, "ean_code", None)),
        "barcode": payload.get("barcode", article.barcode),
    }
    dq_result = evaluate_article_datensatz(_build_article_dq_datensatz(effective_payload))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("Artikel", dq_result))

    for key, value in payload.items():
        setattr(article, key, value)

    db.commit()
    db.refresh(article)
    return _to_article_schema(article)


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_article(
    article_id: str,
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    db: Session = Depends(get_db),
) -> Response:
    """Soft-delete an article."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    article = (
        db.query(ArticleModel)
        .filter(
            ArticleModel.id == article_id,
            ArticleModel.tenant_id == effective_tenant,
            ArticleModel.is_active == True,  # noqa: E712
            ArticleModel.deleted_at.is_(None),
        )
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.is_active = False
    article.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================================================
# Article Extended Data Endpoints (Suppliers, Discounts, Prices, Documents)
# ============================================================================

from ....infrastructure.models import BusinessPartnerDiscountItem, BusinessPartnerPriceAgreement


@router.get("/{article_id}/suppliers", response_model=dict)
async def get_article_suppliers(
    article_id: str,
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    db: Session = Depends(get_db),
):
    """Get suppliers for an article."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    # Query article suppliers
    suppliers = db.query(ArticleSupplier).filter(
        ArticleSupplier.article_id == article_id
    ).all()
    
    return {
        "items": [
            {
                "id": s.id,
                "article_id": s.article_id,
                "partner_id": s.partner_id,
                "supplier_number": s.partner_id,  # Would join with business partner
                "supplier_name": None,  # Would join with business partner
                "supplier_article_number": s.supplier_article_number,
                "purchase_price": float(s.purchase_price or 0) if s.purchase_price else None,
                "price_valid_from": s.price_valid_from.isoformat() if s.price_valid_from else None,
                "price_valid_to": s.price_valid_to.isoformat() if s.price_valid_to else None,
                "lead_time_days": s.lead_time_days,
                "min_order_quantity": float(s.min_order_quantity or 0) if s.min_order_quantity else None,
                "is_preferred": s.is_preferred,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in suppliers
        ]
    }


@router.get("/{article_id}/discounts", response_model=dict)
async def get_article_discounts(
    article_id: str,
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    db: Session = Depends(get_db),
):
    """Get discounts for an article."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    # Get article number first
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    if not article:
        return {"items": []}
    
    # Query discount items by article number
    discounts = db.query(BusinessPartnerDiscountItem).filter(
        BusinessPartnerDiscountItem.article_number == article.article_number
    ).all()
    
    return {
        "items": [
            {
                "id": d.id,
                "article_id": article_id,
                "partner_id": d.partner_id,
                "discount_percent": float(d.discount_percent or 0),
                "valid_from": d.valid_from.isoformat() if d.valid_from else None,
                "valid_to": d.valid_to.isoformat() if d.valid_to else None,
                "discount_list_number": d.discount_list_number,
                "customer_name": None,  # Would join with business partner
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "updated_at": d.updated_at.isoformat() if d.updated_at else None,
            }
            for d in discounts
        ]
    }


@router.get("/{article_id}/prices", response_model=dict)
async def get_article_prices(
    article_id: str,
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    db: Session = Depends(get_db),
):
    """Get price agreements for an article."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    # Get article number first
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    if not article:
        return {"items": []}
    
    # Query price agreements by article number
    prices = db.query(BusinessPartnerPriceAgreement).filter(
        BusinessPartnerPriceAgreement.article_number == article.article_number
    ).all()
    
    return {
        "items": [
            {
                "id": p.id,
                "article_id": article_id,
                "price_net": float(p.price_net or 0),
                "price_incl_freight": float(p.price_incl_freight or 0) if p.price_incl_freight else None,
                "price_unit": p.price_unit,
                "valid_from": p.valid_from.isoformat() if p.valid_from else None,
                "valid_to": p.valid_to.isoformat() if p.valid_to else None,
                "customer_name": None,  # Would join with business partner
                "partner_id": p.partner_id,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in prices
        ]
    }


@router.get("/{article_id}/documents", response_model=dict)
async def get_article_documents(
    article_id: str,
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    db: Session = Depends(get_db),
):
    """Get documents for an article."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    # Query article documents
    documents = db.query(ArticleDocument).filter(
        ArticleDocument.article_id == article_id
    ).all()
    
    return {
        "items": [
            {
                "id": d.id,
                "article_id": d.article_id,
                "document_id": d.document_id,
                "document_name": d.document_name,
                "document_type": d.document_type,
                "document_category": d.document_category,
                "description": d.description,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "updated_at": d.updated_at.isoformat() if d.updated_at else None,
            }
            for d in documents
        ]
    }


@router.get("/{article_id}/stock", response_model=dict)
async def get_article_stock(
    article_id: str,
    branch_id: Optional[str] = Query(None, description="Filter by branch"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    db: Session = Depends(get_db),
):
    """Get stock summary for an article per branch/warehouse."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    # Get article first
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    if not article:
        return {"items": []}
    
    # Query stock movements to calculate stock per warehouse
    query = db.query(StockMovement).filter(
        StockMovement.article_id == article_id
    )
    
    if branch_id:
        query = query.filter(StockMovement.warehouse_id == branch_id)
    
    movements = query.all()
    
    # Aggregate by warehouse
    stock_by_warehouse = {}
    for m in movements:
        wh = m.warehouse_id
        if wh not in stock_by_warehouse:
            stock_by_warehouse[wh] = {
                "warehouse_id": wh,
                "available": 0,
                "reserved": 0,
                "incoming": 0,
                "outgoing": 0,
            }
        
        qty = float(m.quantity or 0)
        if m.movement_type in ("in", "adjustment_in"):
            stock_by_warehouse[wh]["available"] += qty
            stock_by_warehouse[wh]["incoming"] += qty
        elif m.movement_type in ("out", "adjustment_out"):
            stock_by_warehouse[wh]["available"] -= qty
            stock_by_warehouse[wh]["outgoing"] += abs(qty)
        elif m.movement_type == "reservation":
            stock_by_warehouse[wh]["reserved"] += qty
    
    # Get warehouse info and format response
    from ....infrastructure.models import Warehouse
    warehouses = db.query(Warehouse).filter(
        Warehouse.tenant_id == effective_tenant,
        Warehouse.is_active == True
    ).all()
    
    warehouse_map = {w.id: w.name for w in warehouses}
    
    return {
        "article_id": article_id,
        "article_number": article.article_number,
        "article_name": article.name,
        "total_available": float(article.available_stock or 0),
        "total_reserved": float(article.reserved_stock or 0),
        "total_physical": float(article.current_stock or 0),
        "by_warehouse": [
            {
                "warehouse_id": data["warehouse_id"],
                "warehouse_name": warehouse_map.get(data["warehouse_id"], data["warehouse_id"]),
                "available": data["available"],
                "reserved": data["reserved"],
                "incoming": data["incoming"],
                "outgoing": data["outgoing"],
            }
            for data in stock_by_warehouse.values()
        ]
    }


@router.get("/{article_id}/stock-movements", response_model=dict)
async def get_article_stock_movements(
    article_id: str,
    from_date: Optional[str] = Query(None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="To date (YYYY-MM-DD)"),
    warehouse_id: Optional[str] = Query(None, description="Filter by warehouse"),
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get stock movements for an article."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    # Query stock movements
    query = db.query(StockMovement).filter(
        StockMovement.article_id == article_id
    )
    
    if warehouse_id:
        query = query.filter(StockMovement.warehouse_id == warehouse_id)
    
    # Calculate total before pagination
    total = query.count()
    
    # Apply date filters
    if from_date:
        query = query.filter(StockMovement.movement_date >= from_date)
    if to_date:
        query = query.filter(StockMovement.movement_date <= to_date)
    
    # Order by date descending and paginate
    movements = query.order_by(StockMovement.movement_date.desc()).offset(skip).limit(limit).all()
    
    # Get warehouse info
    from ....infrastructure.models import Warehouse
    warehouses = db.query(Warehouse).filter(
        Warehouse.tenant_id == effective_tenant,
        Warehouse.is_active == True
    ).all()
    warehouse_map = {w.id: w.name for w in warehouses}
    
    return {
        "items": [
            {
                "id": m.id,
                "movement_type": m.movement_type,
                "movement_number": m.movement_number,
                "reference_number": m.reference_number,
                "movement_date": m.movement_date.isoformat() if m.movement_date else None,
                "quantity": float(m.quantity or 0),
                "unit": m.unit,
                "warehouse_id": m.warehouse_id,
                "warehouse_name": warehouse_map.get(m.warehouse_id, m.warehouse_id),
                "charge": m.charge,
                "notes": m.notes,
            }
            for m in movements
        ],
        "total": total,
        "page": (skip // limit) + 1,
        "size": limit,
    }
