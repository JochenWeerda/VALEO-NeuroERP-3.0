from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.edi_integration import (
    EdiNachrichtenTyp,
    EdiVerarbeitungsStatus,
    parse_edi_nachricht,
)
from app.domains.operations.models import EdiNachrichtDB, EdiPartnerDB

router = APIRouter(prefix="/edi", tags=["edi"])


class EdiNachrichtEmpfangRequest(BaseModel):
    typ: str
    absender_gln: str
    empfaenger_gln: str
    interchange_control_ref: str
    payload_raw: str
    tenant_id: str = "default"


class EdiPartnerCreateRequest(BaseModel):
    gln: str
    name: str
    tenant_id: str
    aktive_nachrichtentypen: list[str]


@router.post("/nachrichten", status_code=201, summary="Nachricht empfange",
    response_model=dict
)
def empfange_nachricht(req: EdiNachrichtEmpfangRequest, db: Session = Depends(get_db)):
    typ = EdiNachrichtenTyp(req.typ)
    ergebnis = parse_edi_nachricht(req.payload_raw, typ)
    row = EdiNachrichtDB(
        nachricht_id=ergebnis.nachricht_id,
        typ=req.typ,
        absender_gln=req.absender_gln,
        empfaenger_gln=req.empfaenger_gln,
        interchange_control_ref=req.interchange_control_ref,
        empfangen_am=datetime.utcnow(),
        payload_raw=req.payload_raw,
        status=EdiVerarbeitungsStatus.VERARBEITET.value if ergebnis.success else EdiVerarbeitungsStatus.FEHLER.value,
        fehler_beschreibung=ergebnis.fehler_beschreibung,
        dokument_id=ergebnis.dokument_id,
        tenant_id=req.tenant_id,
    )
    db.add(row)
    db.commit()
    return {"nachricht_id": ergebnis.nachricht_id, "success": ergebnis.success, "schema_version": 1}


@router.get("/nachrichten/offene", summary="Offene nachrichten abrufen",
    response_model=dict
)
def get_offene_nachrichten(empfaenger_gln: str, db: Session = Depends(get_db)):
    rows = db.query(EdiNachrichtDB).filter(
        EdiNachrichtDB.empfaenger_gln == empfaenger_gln,
        EdiNachrichtDB.status == EdiVerarbeitungsStatus.ERHALTEN.value,
    ).all()
    return [
        {
            "nachricht_id": r.nachricht_id,
            "typ": r.typ,
            "absender_gln": r.absender_gln,
            "empfangen_am": r.empfangen_am.isoformat() if r.empfangen_am else None,
            "status": r.status,
        }
        for r in rows
    ]


@router.post("/partner", status_code=201, summary="Partner anlegen",
    response_model=dict
)
def create_partner(req: EdiPartnerCreateRequest, db: Session = Depends(get_db)):
    pid = str(uuid.uuid4())
    row = EdiPartnerDB(
        partner_id=pid,
        gln=req.gln,
        name=req.name,
        tenant_id=req.tenant_id,
        aktive_nachrichtentypen=req.aktive_nachrichtentypen,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"partner_id": row.partner_id, "gln": row.gln, "name": row.name}


@router.get("/partner", summary="Partner auflisten",
    response_model=dict
)
def list_partner(tenant_id: str, db: Session = Depends(get_db)):
    rows = db.query(EdiPartnerDB).filter(EdiPartnerDB.tenant_id == tenant_id).all()
    return [{"partner_id": r.partner_id, "gln": r.gln, "name": r.name, "aktive_nachrichtentypen": r.aktive_nachrichtentypen} for r in rows]
