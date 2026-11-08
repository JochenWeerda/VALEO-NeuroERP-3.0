"""Governed L3 Standard and Unimet adapter API."""

from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.legacy_interface_adapters_schemas import (
    AdapterBatchActionOut,
    AdapterConfigureOut,
    AdapterIntakeOut,
    AdapterMonitorOut,
    AdapterProfileListOut,
)
from app.auth.deps import require_roles
from app.auth.deps import get_current_user
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_commands import begruendung, statusaktion
from app.services.legacy_interface_adapter_service import (
    LegacyAdapterError,
    LegacyInterfaceAdapterService,
)

router = APIRouter(
    prefix="/legacy-interface-adapters",
    tags=["integration", "l3-parity"],
    dependencies=[
        Depends(require_roles("admin", "manager", "FINANCE_ADMIN", "LAGER_ADMIN"))
    ],
)


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class ProfileIn(ReasonIn):
    format_version: str = Field(min_length=1, max_length=40)
    mapping_version: str = Field(min_length=1, max_length=40)
    status: str = "ready"
    format_contract: dict[str, Any]
    field_mapping: dict[str, str]


class IntakeIn(BaseModel):
    external_id: str = Field(min_length=1, max_length=200)
    payload: dict[str, Any]


def actor(user: dict) -> str:
    """Urheber aus dem geprueften Token (bis 19.10.2026: Client-Header ``X-User-ID``)."""
    return gepruefter_akteur(user)


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except LegacyAdapterError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/profiles", response_model=AdapterProfileListOut, summary="Schnittstellenprofile auflisten")
def profiles(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, Any]:
    items = LegacyInterfaceAdapterService(db, tenant_id).catalog()
    return {"items": items, "total": len(items), "execution_enabled": False}


@router.put("/profiles/{profile_key}", response_model=AdapterConfigureOut, summary="Schnittstellenprofil konfigurieren")
def configure(
    profile_key: str,
    body: ProfileIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).configure(
            profile_key,
            body.model_dump(exclude={"reason"}),
            actor=actor(user),
            reason=body.reason,
        )
    )


@router.post(
    "/{profile_key}/intake", response_model=AdapterIntakeOut, status_code=status.HTTP_202_ACCEPTED
, summary="Datenlieferung entgegennehmen")
def intake(
    profile_key: str,
    body: IntakeIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).intake(
            profile_key, body.external_id, body.payload, actor=actor(user)
        )
    )


@router.get("/batches", response_model=AdapterMonitorOut, summary="Lieferstapel ueberwachen")
def monitor(
    batch_status: str | None = Query(default=None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).monitor(
            status=batch_status, page=page, page_size=page_size
        )
    )


@router.post("/batches/{batch_id}/stage", response_model=AdapterBatchActionOut, summary="Lieferstapel in die Staging-Stufe uebernehmen")
def stage(
    batch_id: str,
    body: ReasonIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).stage(
            batch_id, actor=actor(user), reason=body.reason
        )
    )


@router.post("/batches/{batch_id}/reconcile", response_model=AdapterBatchActionOut, summary="Lieferstapel abstimmen")
def reconcile(
    batch_id: str,
    body: ReasonIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).reconcile(
            batch_id, actor=actor(user), reason=body.reason
        )
    )


@router.post("/batches/{batch_id}/approve", response_model=AdapterBatchActionOut, summary="Lieferstapel freigeben")
def approve(
    batch_id: str,
    body: ReasonIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).approve(
            batch_id, actor=actor(user), reason=body.reason
        )
    )


_BATCH_ACTIONS = {"stage": {"received", "quarantine"}, "reconcile": {"staged", "quarantine"}, "approve": {"reconciled"}}


@router.post(
    "/batches/{entity_id}/actions/{action_key}",
    response_model=MaskActionResultOut,
    summary="Altsystem-Adapter: Maskenaktion (Staging, Abstimmung, Freigabe)",
)
async def run_batch_action(
    entity_id: str,
    action_key: Literal["stage", "reconcile", "approve"] = Path(...),
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Dieselben Fachwege wie die Einzelwege; Rolle prueft der Router (Leitung Finanzen/Lager)."""
    bearbeiter = actor(user)

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        result = getattr(LegacyInterfaceAdapterService(db_, tenant_id), action_key)(
            entity_id, actor=bearbeiter, reason=begruendung(body))
        return f"Lieferstapel: Status {result.get('status', action_key)}. Produktivbuchung bleibt gesperrt."

    result = await statusaktion(
        db, action_key=action_key, entity_type="legacy_adapter_batch", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt=_BATCH_ACTIONS[action_key], ausfuehren=ausfuehren,
        status_sql="SELECT status FROM domain_integration.legacy_adapter_batches WHERE id=:id AND tenant_id=:tid",
        event_type=f"integration.legacy_adapter_batch.{action_key}",
    )
    return result.model_dump()
