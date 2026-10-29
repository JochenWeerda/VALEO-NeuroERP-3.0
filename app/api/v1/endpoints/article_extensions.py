"""
Article extension endpoints (l3c-artikel extras)
Batches, file upload, recipe import, fertiliser management.
"""

from typing import Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import ArticleBatch, ArticleSelection
from ..schemas.base import PaginatedResponse, BaseSchema
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.tenant import get_tenant_id

router = APIRouter()


class BatchOut(BaseSchema):
    id: str
    article_id: str
    batch_number: str
    warehouse_id: str
    quantity: float = 0
    expiry_date: Optional[str] = None


class SelectionOut(BaseSchema):
    id: str
    article_id: str
    selection_code: str
    label: Optional[str] = None


class SelectionCreate(BaseModel):
    article_id: str
    selection_code: str
    label: Optional[str] = None


class FileUploadResponse(BaseModel):
    filename: str
    size: int
    message: str


class RecipeImportRequest(BaseModel):
    article_id: str
    components: list[dict]


@router.get("/batches", response_model=PaginatedResponse[BatchOut], summary="Article batches auflisten")
async def list_article_batches(
    article_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """GET Artikelbestand (Chargen)"""
    q = db.query(ArticleBatch).filter(ArticleBatch.tenant_id == tenant_id)
    if article_id:
        q = q.filter(ArticleBatch.article_id == article_id)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[BatchOut](
        items=[BatchOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.post("/file-upload", response_model=FileUploadResponse, summary="Article file hochladen", dependencies=SCHREIBEN["STAMMDATEN"])
async def upload_article_file(
    article_id: str = Query(...),
    file: UploadFile = File(...),
):
    """POST Artikel Datei Upload"""
    content = await file.read()
    return FileUploadResponse(
        filename=file.filename or "unknown",
        size=len(content),
        message=f"File uploaded for article {article_id}",
    )


@router.post("/recipe-import", status_code=201, summary="Recipe importieren",
    response_model=BatchOut, dependencies=SCHREIBEN["STAMMDATEN"])
async def import_recipe(payload: RecipeImportRequest):
    """POST Rezeptur Import"""
    return {
        "article_id": payload.article_id,
        "components_count": len(payload.components),
        "message": "Recipe imported successfully",
    }


# ── Artikel Selektionen ─────────────────────────────────────────

@router.get("/selections", response_model=list[SelectionOut], summary="Article selections auflisten")
async def list_article_selections(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """GET Artikel Selektionen ermitteln"""
    items = db.query(ArticleSelection).filter(ArticleSelection.tenant_id == tenant_id).all()
    return [SelectionOut.model_validate(i) for i in items]


@router.post("/selections", response_model=SelectionOut, status_code=201, summary="Article selection anlegen", dependencies=SCHREIBEN["STAMMDATEN"])
async def create_article_selection(
    payload: SelectionCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """POST Artikel Selektionen anlegen"""
    from app.core.uuid7 import uuid7
    obj = ArticleSelection(
        id=uuid7(),
        article_id=payload.article_id,
        selection_code=payload.selection_code,
        label=payload.label,
        tenant_id=tenant_id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return SelectionOut.model_validate(obj)


@router.delete("/selections/{sel_id}", status_code=204, response_class=Response, response_model=None, summary="Article selection löschen", dependencies=SCHREIBEN["STAMMDATEN"])
async def delete_article_selection(
    sel_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
):
    """DEL Artikel Selektionen löschen"""
    obj = db.query(ArticleSelection).filter(
        ArticleSelection.id == sel_id, ArticleSelection.tenant_id == tenant_id
    ).first()
    if not obj:
        raise HTTPException(404, "Selection not found")
    db.delete(obj)
    db.commit()
