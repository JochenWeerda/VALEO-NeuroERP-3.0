"""Safe user query-center API."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.query_center_service import QueryCenterError, QueryCenterService

router = APIRouter(prefix="/query-center", tags=["reporting", "query-center"])


class DefinitionIn(BaseModel):
    id: str | None = None
    name: str = Field(min_length=1, max_length=160)
    data_product_id: str
    selected_fields: list[str] = Field(min_length=1, max_length=30)
    filter_spec: dict[str, Any] = Field(default_factory=dict)
    aggregations: list[str] = Field(default_factory=list, max_length=10)
    is_favorite: bool = False


class SaveIn(DefinitionIn):
    reason: str = Field(min_length=5, max_length=500)


class PreviewIn(DefinitionIn):
    limit: int = Field(default=100, ge=1, le=200)


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class ImportIn(BaseModel):
    bundle: dict[str, Any]
    reason: str = Field(min_length=5, max_length=500)


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "query-center-user"


def service(db: Session, tenant_id: str) -> QueryCenterService:
    return QueryCenterService(db, tenant_id, signing_key=settings.SECRET_KEY)


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except QueryCenterError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/catalog", response_model=dict)
def catalog(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, Any]:
    items = service(db, tenant_id).catalog()
    return {"items": items, "count": len(items)}


@router.get("", response_model=dict)
def list_definitions(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    favorite: bool | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return service(db, tenant_id).list_page(
        owner_id=actor(request), page=page, page_size=page_size, favorite=favorite
    )


@router.post("/preview", response_model=dict)
def preview(
    body: PreviewIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: service(db, tenant_id).preview(
            body.model_dump(exclude={"limit"}), limit=body.limit
        )
    )


@router.post("", response_model=dict, status_code=201)
def save(
    body: SaveIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: service(db, tenant_id).save(
            body.model_dump(exclude={"reason"}),
            actor=actor(request),
            reason=body.reason,
        )
    )


@router.post("/{definition_id}/export", response_model=dict)
def export_definition(
    definition_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: service(db, tenant_id).export_signed(
            definition_id, actor=actor(request), reason=body.reason
        )
    )


@router.post("/import", response_model=dict, status_code=201)
def import_definition(
    body: ImportIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: service(db, tenant_id).import_signed(
            body.bundle, actor=actor(request), reason=body.reason
        )
    )
