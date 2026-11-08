"""Authenticated native-mask baselines; no activation or release shortcut."""
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from app.auth.finance_roles import beleg_write
from app.core.tenant import get_tenant_id
from app.services import studio_native_import as service
from app.services.studio_draft_store import StudioStorageUnavailable

router = APIRouter()


class NativeSourceOut(BaseModel):
    screen_id: str
    title: str
    source_hash: str


class NativeSourcesOut(BaseModel):
    items: list[NativeSourceOut]
    total: int


class NativeImportIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    screen_id: str = Field(min_length=1, max_length=200)
    expected_source_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    idempotency_key: UUID


class NativeDraftOut(BaseModel):
    id: str
    tenant_id: str
    screen_id: str
    base_screen_id: str | None = None
    definition: dict[str, Any]
    status: str
    readiness: dict[str, Any] | None = None
    created_by: str
    updated_by: str
    updated_at: datetime
    revision: str


@router.get("/native-sources", response_model=NativeSourcesOut,
            summary="Versionierte Ausgangsquellen vorhandener Masken auflisten")
def native_sources(q: str = Query("", max_length=100), skip: int = Query(0, ge=0),
                   limit: int = Query(50, ge=1, le=100), tenant_id: str = Depends(get_tenant_id),
                   user: dict = Depends(beleg_write)):
    return service.list_sources(tenant_id, q, skip, limit)


@router.post("/native-imports", response_model=NativeDraftOut,
             summary="Vorhandene Maske als versionierte Studio-Ausgangsfassung uebernehmen")
def native_import(body: NativeImportIn, tenant_id: str = Depends(get_tenant_id),
                  user: dict = Depends(beleg_write)):
    actor = user.get("sub")
    if not isinstance(actor, str) or not actor.strip():
        raise HTTPException(403, "verified_actor_required")
    try:
        return service.import_source(tenant_id, actor.strip(), body.screen_id,
                                     body.expected_source_hash, str(body.idempotency_key))
    except KeyError as error:
        raise HTTPException(404, "native_quelle_nicht_gefunden") from error
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
    except StudioStorageUnavailable as error:
        raise HTTPException(503, "studio_persistenz_nicht_verfuegbar") from error
