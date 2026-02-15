"""Inventory Articles management endpoints."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import Article as ArticleModel
from ..schemas.base import PaginatedResponse
from ..schemas.inventory import Article, ArticleCreate, ArticleUpdate

router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


def _to_article_schema(row: ArticleModel) -> Article:
    return Article.model_validate(
        {
            "id": str(row.id),
            "tenant_id": str(row.tenant_id),
            "article_number": row.article_number,
            "name": row.name,
            "description": row.description,
            "suchbegriff": row.suchbegriff,
            "hersteller": row.hersteller,
            "herkunftsland": row.herkunftsland,
            "naehrwertangaben": row.naehrwertangaben,
            "mhd_erforderlich": bool(row.mhd_erforderlich),
            "lagerartikel": bool(row.lagerartikel),
            "mehrwertsteuer_prozent": row.mehrwertsteuer_prozent,
            "warengruppe": row.warengruppe,
            "gefahrgutklasse": row.gefahrgutklasse,
            "lagerorte": row.lagerorte or [],
            "chargenpflicht": bool(row.chargenpflicht),
            "qs_pruefung_erforderlich": bool(row.qs_pruefung_erforderlich),
            "zolltarifnummer": row.zolltarifnummer,
            "bio_kennzeichnung": bool(row.bio_kennzeichnung),
            "gmp_plus_relevanz": bool(row.gmp_plus_relevanz),
            "lieferantennummer": row.lieferantennummer,
            "unit": row.unit,
            "category": row.category,
            "subcategory": row.subcategory,
            "barcode": row.barcode,
            "supplier_number": row.supplier_number,
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

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                ArticleModel.name.ilike(like),
                ArticleModel.article_number.ilike(like),
                ArticleModel.barcode.ilike(like),
                ArticleModel.suchbegriff.ilike(like),
                ArticleModel.hersteller.ilike(like),
                ArticleModel.warengruppe.ilike(like),
            )
        )

    total = query.count()
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
    like = f"%{q}%"
    query = (
        db.query(ArticleModel)
        .filter(ArticleModel.is_active == True)  # noqa: E712
        .filter(ArticleModel.tenant_id == effective_tenant)
        .filter(
            or_(
                ArticleModel.name.ilike(like),
                ArticleModel.article_number.ilike(like),
                ArticleModel.barcode.ilike(like),
                ArticleModel.suchbegriff.ilike(like),
                ArticleModel.hersteller.ilike(like),
                ArticleModel.warengruppe.ilike(like),
            )
        )
        .order_by(ArticleModel.name.asc())
        .limit(limit)
    )

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
        suchbegriff=article_data.suchbegriff,
        hersteller=article_data.hersteller,
        herkunftsland=article_data.herkunftsland,
        naehrwertangaben=article_data.naehrwertangaben,
        mhd_erforderlich=article_data.mhd_erforderlich,
        lagerartikel=article_data.lagerartikel,
        mehrwertsteuer_prozent=article_data.mehrwertsteuer_prozent,
        warengruppe=article_data.warengruppe,
        gefahrgutklasse=article_data.gefahrgutklasse,
        lagerorte=article_data.lagerorte,
        chargenpflicht=article_data.chargenpflicht,
        qs_pruefung_erforderlich=article_data.qs_pruefung_erforderlich,
        zolltarifnummer=article_data.zolltarifnummer,
        bio_kennzeichnung=article_data.bio_kennzeichnung,
        gmp_plus_relevanz=article_data.gmp_plus_relevanz,
        lieferantennummer=article_data.lieferantennummer,
        unit=article_data.unit,
        category=article_data.category,
        subcategory=article_data.subcategory,
        barcode=article_data.barcode,
        supplier_number=article_data.supplier_number,
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

