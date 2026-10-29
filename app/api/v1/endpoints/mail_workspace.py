"""Role-scoped ERP mail workspace API."""

from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.crm_channel_bundle_schemas import (
    MailAssignOut,
    MailAttachmentOut,
    MailDraftCreatedOut,
    MailMessagePageOut,
    MailQueueOut,
    MailTransferOut,
)
from app.auth.deps import get_current_user
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mail_workspace_service import MailWorkspaceError, MailWorkspaceService
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_commands import begruendung, statusaktion
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

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


def actor(user: dict) -> str:
    """Urheber aus dem geprueften Token (bis 19.10.2026: Client-Header ``X-User-ID``)."""
    return gepruefter_akteur(user)


def roles(user: dict) -> set[str]:
    """Rollenpostfaecher, die die angemeldete Person sehen darf: ihre Rollen aus dem geprueften Token.

    Bis zum 19.10.2026 kamen sie aus dem Client-Header ``X-Roles``. Wer ihn setzte, las, schrieb und
    versandte aus jedem Rollenpostfach des Mandanten.
    """
    return {str(role).strip() for role in (user.get("roles") or []) if str(role).strip()}


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except MailWorkspaceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=MailMessagePageOut, summary="Nachrichten des Mailarbeitsplatzes auflisten")
def list_messages(
    user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: str | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).list_page(
            allowed_roles=roles(user), page=page, page_size=page_size, status=status
        )
    )


@router.get("/attachments", response_model=list[MailAttachmentOut], summary="Anhaenge auflisten")
def list_attachments(
    user: dict = Depends(get_current_user),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).list_attachments(
            allowed_roles=roles(user), limit=limit
        )
    )


@router.post("/drafts", response_model=MailDraftCreatedOut, status_code=201, summary="Entwurf anlegen", dependencies=SCHREIBEN["CRM"])
def create_draft(
    body: DraftIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    allowed = roles(user)
    if body.role_key not in allowed:
        raise HTTPException(status_code=403, detail="Rollenpostfach-Zugriff verweigert")
    payload = body.model_dump(exclude={"role_key", "reason"}, mode="json")
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).create_draft(
            payload, role_key=body.role_key, actor=actor(user), reason=body.reason
        )
    )


@router.post("/{message_id}/assign", response_model=MailAssignOut, summary="Nachricht zuweisen", dependencies=SCHREIBEN["CRM"])
def assign(
    message_id: str,
    body: AssignmentIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).assign(
            message_id,
            body.model_dump(exclude={"reason"}),
            allowed_roles=roles(user),
            actor=actor(user),
            reason=body.reason,
        )
    )


@router.post("/{message_id}/queue", response_model=MailQueueOut, summary="Nachricht zum Versand einreihen", dependencies=SCHREIBEN["CRM"])
def queue(
    message_id: str,
    body: ReasonIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, str]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).queue_send(
            message_id,
            allowed_roles=roles(user),
            actor=actor(user),
            reason=body.reason,
        )
    )


@router.post("/attachments/{attachment_id}/transfer", response_model=MailTransferOut, summary="Anhang uebernehmen", dependencies=SCHREIBEN["CRM"])
def transfer_attachment(
    attachment_id: str,
    body: ReasonIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, str]:
    return guarded(
        lambda: MailWorkspaceService(db, tenant_id).transfer_attachment(
            attachment_id,
            allowed_roles=roles(user),
            actor=actor(user),
            reason=body.reason,
        )
    )



@router.post(
    "/{entity_id}/actions/queue",
    response_model=MaskActionResultOut,
    summary="Mailarbeitsplatz: Nachricht zum Versand einreihen (Maskenaktion)", dependencies=SCHREIBEN["CRM"])
async def queue_action(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Derselbe Fachweg wie ``/queue``; nur Entwuerfe und Fehlversuche, nur aus eigenen Rollenpostfaechern."""
    erlaubt = roles(user)
    bearbeiter = actor(user)

    def postfach(row: dict[str, Any]) -> str | None:
        return None if row.get("role_key") in erlaubt else "Rollenpostfach-Zugriff verweigert."

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        MailWorkspaceService(db_, tenant_id).queue_send(entity_id, allowed_roles=erlaubt, actor=bearbeiter,
                                                        reason=begruendung(body))
        return "Nachricht zum Versand eingereiht."

    result = await statusaktion(
        db, action_key="queue", entity_type="mail_workspace_message", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt={"draft", "error"}, ausfuehren=ausfuehren, zusatzpruefung=postfach,
        status_sql="SELECT status, role_key FROM domain_crm.mail_workspace_messages WHERE id=:id AND tenant_id=:tid",
        event_type="crm.mail_workspace.queue",
    )
    return result.model_dump()


@router.post(
    "/attachments/{entity_id}/actions/transfer",
    response_model=MaskActionResultOut,
    summary="Mailarbeitsplatz: Anhang ins DMS uebernehmen (Maskenaktion)", dependencies=SCHREIBEN["CRM"])
async def transfer_action(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    erlaubt = roles(user)
    bearbeiter = actor(user)

    def postfach(row: dict[str, Any]) -> str | None:
        return None if row.get("role_key") in erlaubt else "Rollenpostfach-Zugriff verweigert."

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        MailWorkspaceService(db_, tenant_id).transfer_attachment(entity_id, allowed_roles=erlaubt, actor=bearbeiter,
                                                                 reason=begruendung(body))
        return "Anhang uebernommen."

    result = await statusaktion(
        db, action_key="transfer", entity_type="mail_workspace_attachment", entity_id=entity_id,
        tenant_id=tenant_id, body=body, erlaubt={"available"}, ausfuehren=ausfuehren, zusatzpruefung=postfach,
        status_sql="SELECT a.transfer_status AS status, m.role_key FROM domain_crm.mail_workspace_attachments a "
                   "JOIN domain_crm.mail_workspace_messages m ON m.id = a.message_id AND m.tenant_id = a.tenant_id "
                   "WHERE a.id=:id AND a.tenant_id=:tid",
        event_type="crm.mail_workspace.attachment_transfer",
    )
    return result.model_dump()
