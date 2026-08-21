"""Personal recent-document API."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.recent_documents_service import (
    RecentDocumentError,
    RecentDocumentsService,
)

router = APIRouter(prefix="/recent-documents", tags=["workspace", "l3-parity"])


class RecentDocumentTouch(BaseModel):
    screen_id: str = Field(min_length=3, max_length=160)
    document_id: str = Field(min_length=1, max_length=200)
    document_type: str = Field(min_length=1, max_length=120)
    document_number: str = Field(min_length=1, max_length=160)
    partner_id: str | None = Field(default=None, max_length=200)
    partner_name: str | None = Field(default=None, max_length=240)
    title: str = Field(min_length=1, max_length=240)
    route: str = Field(min_length=2, max_length=600)


def service(db: Session, tenant_id: str, user: User) -> RecentDocumentsService:
    return RecentDocumentsService(
        db, tenant_id, str(user.get("sub") or ""), list(user.get("roles") or [])
    )


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except RecentDocumentError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/touch", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
def touch(
    body: RecentDocumentTouch,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    return guarded(lambda: service(db, tenant_id, user).touch(body.model_dump()))


@router.get("", response_model=dict)
def list_recent(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    document_type: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    return guarded(
        lambda: service(db, tenant_id, user).list(
            page=page, page_size=page_size, document_type=document_type
        )
    )


@router.delete("/{recent_id}", response_model=dict)
def remove_one(
    recent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, int]:
    return {"deleted": service(db, tenant_id, user).remove(recent_id)}


@router.delete("", response_model=dict)
def clear_all(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, int]:
    return {"deleted": service(db, tenant_id, user).remove()}
