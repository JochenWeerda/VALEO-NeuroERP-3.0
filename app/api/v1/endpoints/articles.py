"""
Inventory Articles management endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import Article as ArticleModel
from ..schemas.base import PaginatedResponse
from ..schemas.inventory import Article

router = APIRouter()

DEFAULT_TENANT = "system"


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
            )
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse[Article](
        items=[Article.model_validate(item) for item in items],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{article_id}", response_model=Article)
async def get_article(article_id: str, db: Session = Depends(get_db)):
    """Fetch a single article by identifier."""
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return Article.model_validate(article)


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
            )
        )
        .order_by(ArticleModel.name.asc())
        .limit(limit)
    )

    return [Article.model_validate(item) for item in query.all()]

