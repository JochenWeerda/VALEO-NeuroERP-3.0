"""Role-scoped ERP mail workspace API."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mail_workspace_service import MailWorkspaceError, MailWorkspaceService

router = APIRouter(prefix="/mail-workspace", tags=["crm", "mail", "dms"])


class DraftIn(BaseModel):
    role_key: str = Field(min_length=1, max_length=80)
    from_address: EmailStr | None = None
    to_addresses: list[EmailStr] = Field(min_length=1, max_length=50)
    subject: str = Field(min_length=1, max_length=500)
    body_text: str = Field(default="", max_length=100_000)
    contact_id: str | None = None
    document_type: str | None = None
    document_ref: str | None = None
    document_route: str | None = None
    reason: str = Field(min_length=5, max_length=500)


class AssignmentIn(BaseModel):
    contact_id: str | None = None
    document_type: str | None = None
    document_ref: str | None = None
    document_route: str | None = None
    assigned_to: str | None = None
    reason: str = Field(min_length=5, max_length=500)


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "mail-workspace-user"


def roles(request: Request) -> set[str]:
    return {
        item.strip()
        for item in request.headers.get("X-Roles", "").split(",")
        if item.strip()
    }


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except MailWorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=dict)
def list_messages(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: str | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).list_page(
            allowed_roles=roles(request), page=page, page_size=page_size, status=status
        )
    )


@router.get("/attachments", response_model=list[dict])
def list_attachments(
    request: Request,
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).list_attachments(
            allowed_roles=roles(request), limit=limit
        )
    )


@router.post("/drafts", response_model=dict, status_code=201)
def create_draft(
    body: DraftIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    allowed = roles(request)
    if body.role_key not in allowed:
        raise HTTPException(status_code=403, detail="Rollenpostfach-Zugriff verweigert")
    payload = body.model_dump(exclude={"role_key", "reason"}, mode="json")
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).create_draft(
            payload, role_key=body.role_key, actor=actor(request), reason=body.reason
        )
    )


@router.post("/{message_id}/assign", response_model=dict)
def assign(
    message_id: str,
    body: AssignmentIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).assign(
            message_id,
            body.model_dump(exclude={"reason"}),
            allowed_roles=roles(request),
            actor=actor(request),
            reason=body.reason,
        )
    )


@router.post("/{message_id}/queue", response_model=dict)
def queue(
    message_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, str]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).queue_send(
            message_id,
            allowed_roles=roles(request),
            actor=actor(request),
            reason=body.reason,
        )
    )


@router.post("/attachments/{attachment_id}/transfer", response_model=dict)
def transfer_attachment(
    attachment_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, str]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).transfer_attachment(
            attachment_id,
            allowed_roles=roles(request),
            actor=actor(request),
            reason=body.reason,
        )
    )
