"""HTTP-Read fuer Agrar-Ketten-Hint — kein Schreiben, keine Modell-Vereinheitlichung.

Statusfelder kommen als optionale Query-Projektion vom Aufrufer.
Mandant nur ueber ``get_tenant_id``. Fuer ``source_model=agrar`` kann
``quality_is_final`` per Join Annahme→Protokoll nachgeladen werden
(``read_agrar_quality_is_final``). Kon-Lookup bleibt verboten. Pure bekommt
den Bool von aussen — kein Fake.
"""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.workspace.agrar_chain import (
    SourceModel,
    read_agrar_quality_is_final,
    resolve_next_step,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspace", tags=["workspace", "agrar-chain"])

SourceModelQuery = Literal["kon", "agrar"]


class AgrarChainOut(BaseModel):
    """Exakte Antwort-Shape — keine Zusatzfelder."""

    contract_ref: str
    source_model: SourceModel
    next_step: str
    reason: str


def build_agrar_chain_response(
    *,
    contract_ref: str,
    source_model: SourceModel,
    contract_status: str | None = None,
    disposition_status: str | None = None,
    weighing_present: bool = False,
    weighing_status: str | None = None,
    quality_is_final: bool = False,
    settlement_status: str | None = None,
    allocation_status: str | None = None,
    harvest_release_status: str | None = None,
    quality_status: str | None = None,
) -> AgrarChainOut:
    """Pure Aufbau der Response (ohne Request/DB) — fuer Router und Unit-Tests."""
    ref = (contract_ref or "").strip()
    if not ref:
        raise ValueError("contract_ref_required")
    fields: dict[str, object] = {
        "contract_status": contract_status or "",
        "weighing_present": weighing_present,
        "quality_is_final": quality_is_final,
    }
    if disposition_status is not None:
        fields["disposition_status"] = disposition_status
    if weighing_status is not None:
        fields["weighing_status"] = weighing_status
    if settlement_status is not None:
        fields["settlement_status"] = settlement_status
    if allocation_status is not None:
        fields["allocation_status"] = allocation_status
    if harvest_release_status is not None:
        fields["harvest_release_status"] = harvest_release_status
    if quality_status is not None:
        fields["quality_status"] = quality_status
    hint = resolve_next_step(contract_ref=ref, source_model=source_model, fields=fields)
    return AgrarChainOut(**hint.as_dict())


def _resolve_agrar_quality_flag(
    *,
    db: Session,
    tenant_id: str,
    contract_ref: str,
    quality_is_final_query: bool,
) -> tuple[bool, bool]:
    """(effective_quality_is_final, qs_lookup_failed).

    Explizites Query-True gewinnt. Sonst DB-Read fuer AgrarContract.
    Lookup-Fehler → Flag False + failed=True (reason qs_unbekannt).
    """
    if quality_is_final_query:
        return True, False
    try:
        loaded = read_agrar_quality_is_final(
            db,
            tenant_id=tenant_id,
            agrar_contract_id=contract_ref,
        )
    except Exception:
        logger.exception(
            "agrar_chain QS-Read fehlgeschlagen contract_ref=%s tenant_id=%s",
            contract_ref,
            tenant_id,
        )
        return False, True
    if loaded is True:
        return True, False
    return False, False


@router.get(
    "/agrar-chain",
    response_model=AgrarChainOut,
    summary="Naechster Agrar-Prozessschritt (Read-Model)",
)
def get_agrar_chain(
    contract_ref: str = Query(..., min_length=1, max_length=128),
    source_model: SourceModelQuery = Query(...),
    contract_status: str | None = Query(None, max_length=64),
    disposition_status: str | None = Query(None, max_length=64),
    weighing_present: bool = Query(False),
    weighing_status: str | None = Query(None, max_length=64),
    quality_is_final: bool = Query(False),
    settlement_status: str | None = Query(None, max_length=64),
    allocation_status: str | None = Query(None, max_length=64),
    harvest_release_status: str | None = Query(None, max_length=64),
    quality_status: str | None = Query(None, max_length=64),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> AgrarChainOut:
    """GET /api/v1/workspace/agrar-chain — nur Lesen, keine Buchung."""
    effective_qs = quality_is_final
    qs_failed = False
    if source_model == "agrar":
        effective_qs, qs_failed = _resolve_agrar_quality_flag(
            db=db,
            tenant_id=tenant_id,
            contract_ref=contract_ref,
            quality_is_final_query=quality_is_final,
        )
    try:
        out = build_agrar_chain_response(
            contract_ref=contract_ref,
            source_model=source_model,
            contract_status=contract_status,
            disposition_status=disposition_status,
            weighing_present=weighing_present,
            weighing_status=weighing_status,
            quality_is_final=effective_qs,
            settlement_status=settlement_status,
            allocation_status=allocation_status,
            harvest_release_status=harvest_release_status,
            quality_status=quality_status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if qs_failed:
        return AgrarChainOut(
            contract_ref=out.contract_ref,
            source_model=out.source_model,
            next_step=out.next_step,
            reason="qs_unbekannt",
        )
    return out
