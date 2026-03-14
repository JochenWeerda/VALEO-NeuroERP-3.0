from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from app.core.edi_integration import (
    EdiNachricht, EdiNachrichtenTyp, EdiPartner, EdiNachrichtStore,
    parse_edi_nachricht, EdiVerarbeitungsStatus
)

router = APIRouter(prefix="/edi", tags=["edi"])
_store = EdiNachrichtStore()

class EdiNachrichtEmpfangRequest(BaseModel):
    typ: str
    absender_gln: str
    empfaenger_gln: str
    interchange_control_ref: str
    payload_raw: str

class EdiPartnerCreateRequest(BaseModel):
    gln: str
    name: str
    tenant_id: str
    aktive_nachrichtentypen: list[str]

@router.post("/nachrichten", status_code=201)
def empfange_nachricht(req: EdiNachrichtEmpfangRequest):
    typ = EdiNachrichtenTyp(req.typ)
    ergebnis = parse_edi_nachricht(req.payload_raw, typ)
    nachricht = EdiNachricht(
        nachricht_id=ergebnis.nachricht_id,
        typ=typ,
        absender_gln=req.absender_gln,
        empfaenger_gln=req.empfaenger_gln,
        interchange_control_ref=req.interchange_control_ref,
        empfangen_am=datetime.utcnow(),
        payload_raw=req.payload_raw,
        status=EdiVerarbeitungsStatus.VERARBEITET if ergebnis.success else EdiVerarbeitungsStatus.FEHLER,
        fehler_beschreibung=ergebnis.fehler_beschreibung,
        dokument_id=ergebnis.dokument_id,
    )
    _store.add_nachricht(nachricht)
    return {"nachricht_id": nachricht.nachricht_id, "success": ergebnis.success, "schema_version": 1}

@router.get("/nachrichten/offene")
def get_offene_nachrichten(empfaenger_gln: str):
    return _store.offene_nachrichten(empfaenger_gln)

@router.post("/partner", status_code=201)
def create_partner(req: EdiPartnerCreateRequest):
    partner = EdiPartner(
        partner_id=str(uuid.uuid4()),
        gln=req.gln,
        name=req.name,
        tenant_id=req.tenant_id,
        aktive_nachrichtentypen=[EdiNachrichtenTyp(t) for t in req.aktive_nachrichtentypen],
    )
    _store.add_partner(partner)
    return partner
