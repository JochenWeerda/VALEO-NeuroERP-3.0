from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.reklamation import (
    Reklamation,
    ReklamationStore,
    ReklamationZustandsmaschine,
    ReklamationsCRMReferenz,
    ReklamationsDMSReferenz,
    ReklamationsPosition,
    ReklamationsStatus,
    ReklamationsTyp,
)

router = APIRouter(prefix="/reklamationen", tags=["reklamationen"])
_store = ReklamationStore()


class ReklamationsCRMReferenzRequest(BaseModel):
    crm_system: str
    crm_case_id: str
    crm_ticket_id: Optional[str] = None
    crm_status: Optional[str] = None
    crm_url: Optional[str] = None


class ReklamationsDMSReferenzRequest(BaseModel):
    dokument_id: str
    dokument_typ: Optional[str] = None
    dateiname: Optional[str] = None
    checksum: Optional[str] = None
    source_uri: Optional[str] = None


class ReklamationCreateRequest(BaseModel):
    tenant_id: str
    lieferant_id: str
    typ: str
    positionen: list[dict]
    zustaendiger: str
    frist_datum: str
    kontrakt_id: Optional[str] = None
    crm_referenz: Optional[ReklamationsCRMReferenzRequest] = None
    dms_referenzen: list[ReklamationsDMSReferenzRequest] = Field(default_factory=list)
    gobd_beleg_id: Optional[str] = None
    aktor_id: str = "system"


class ReklamationTransitionRequest(BaseModel):
    neuer_status: str
    aktor_id: str = "system"
    kommentar: Optional[str] = None


class ReklamationReferenzUpdateRequest(BaseModel):
    aktor_id: str = "system"
    crm_referenz: Optional[ReklamationsCRMReferenzRequest] = None
    dms_referenzen: list[ReklamationsDMSReferenzRequest] = Field(default_factory=list)


def _build_reklamation_payload(rek: Reklamation) -> dict:
    return rek.as_dict()


@router.post("", status_code=201)
def create_reklamation(req: ReklamationCreateRequest):
    positionen = [ReklamationsPosition(**p) for p in req.positionen]
    crm_referenz = ReklamationsCRMReferenz(**req.crm_referenz.model_dump()) if req.crm_referenz else None
    dms_referenzen = [ReklamationsDMSReferenz(**d.model_dump()) for d in req.dms_referenzen]
    gobd_beleg_id = req.gobd_beleg_id or (dms_referenzen[0].dokument_id if dms_referenzen else None)
    rek = Reklamation(
        reklamation_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        lieferant_id=req.lieferant_id,
        typ=ReklamationsTyp(req.typ),
        positionen=positionen,
        zustaendiger=req.zustaendiger,
        frist_datum=date.fromisoformat(req.frist_datum),
        erstellt_am=datetime.utcnow(),
        kontrakt_id=req.kontrakt_id,
        crm_referenz=None,
        dms_referenzen=[],
        gobd_beleg_id=gobd_beleg_id,
    )
    _store.add(rek, aktor_id=req.aktor_id)
    if crm_referenz is not None:
        _store.set_crm_referenz(rek.reklamation_id, crm_referenz, aktor_id=req.aktor_id)
    if dms_referenzen:
        # The initial add event captures the complaint creation; attach DMS refs after that.
        _store.add_dms_referenzen(rek.reklamation_id, dms_referenzen, aktor_id=req.aktor_id)
    return _build_reklamation_payload(rek)


@router.get("/{reklamation_id}")
def get_reklamation(reklamation_id: str):
    rek = _store.get(reklamation_id)
    if rek is None:
        raise HTTPException(status_code=404, detail="Reklamation nicht gefunden")
    return _build_reklamation_payload(rek)


@router.get("/{reklamation_id}/audit")
def get_audit_trail(reklamation_id: str):
    rek = _store.get(reklamation_id)
    if rek is None:
        raise HTTPException(status_code=404, detail="Reklamation nicht gefunden")
    audit_trail = rek.audit_trail
    return {
        "reklamation_id": reklamation_id,
        "count": len(audit_trail),
        "audit_integritaet_ok": rek.audit_integritaet_ok(),
        "audit_trail": [eintrag.model_dump(mode="json") for eintrag in audit_trail],
    }


@router.get("/{reklamation_id}/e2e")
def get_e2e_overview(reklamation_id: str):
    rek = _store.get(reklamation_id)
    if rek is None:
        raise HTTPException(status_code=404, detail="Reklamation nicht gefunden")
    return {
        "reklamation": _build_reklamation_payload(rek),
        "crm_case_id": rek.crm_referenz.crm_case_id if rek.crm_referenz else None,
        "dms_document_ids": [ref.dokument_id for ref in rek.dms_referenzen],
        "sla_status": rek.berechne_sla_status().value,
        "audit_count": len(rek.audit_trail),
        "e2e_complete": rek.hat_crm_bezug and rek.hat_dms_bezug,
    }


@router.post("/{reklamation_id}/transition")
def transition_status(
    reklamation_id: str,
    neuer_status: str,
    aktor_id: str = "system",
    kommentar: str | None = None,
):
    rek = _store.get(reklamation_id)
    if rek is None:
        raise HTTPException(status_code=404, detail="Reklamation nicht gefunden")
    try:
        _store.transition(
            reklamation_id,
            ReklamationsStatus(neuer_status),
            aktor_id=aktor_id,
            kommentar=kommentar,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return _build_reklamation_payload(rek)


@router.post("/{reklamation_id}/crm-reference")
def update_crm_reference(reklamation_id: str, req: ReklamationReferenzUpdateRequest):
    rek = _store.get(reklamation_id)
    if rek is None:
        raise HTTPException(status_code=404, detail="Reklamation nicht gefunden")
    if req.crm_referenz is None:
        raise HTTPException(status_code=422, detail="crm_referenz ist erforderlich")
    _store.set_crm_referenz(
        reklamation_id,
        ReklamationsCRMReferenz(**req.crm_referenz.model_dump()),
        aktor_id=req.aktor_id,
    )
    return _build_reklamation_payload(rek)


@router.post("/{reklamation_id}/dms-referenzen")
def add_dms_referenzen(reklamation_id: str, req: ReklamationReferenzUpdateRequest):
    rek = _store.get(reklamation_id)
    if rek is None:
        raise HTTPException(status_code=404, detail="Reklamation nicht gefunden")
    if not req.dms_referenzen:
        raise HTTPException(status_code=422, detail="dms_referenzen ist erforderlich")
    _store.add_dms_referenzen(
        reklamation_id,
        [ReklamationsDMSReferenz(**ref.model_dump()) for ref in req.dms_referenzen],
        aktor_id=req.aktor_id,
    )
    return _build_reklamation_payload(rek)


@router.get("/crm/{crm_case_id}")
def get_by_crm_case(crm_case_id: str):
    return [_build_reklamation_payload(rek) for rek in _store.by_crm_case(crm_case_id)]


@router.get("/offene/{tenant_id}")
def get_offene(tenant_id: str):
    return [_build_reklamation_payload(rek) for rek in _store.offene(tenant_id)]


@router.get("/ueberfaellige/{tenant_id}")
def get_ueberfaellige(tenant_id: str):
    return [_build_reklamation_payload(rek) for rek in _store.ueberfaellige(tenant_id)]
