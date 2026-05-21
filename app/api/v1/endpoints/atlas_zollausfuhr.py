"""ATLAS Zollausfuhr — German customs export declaration (ECS Phase 2)."""

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.atlas_customs_service import ATLASCustomsService

router = APIRouter(prefix="/zoll", tags=["zoll", "atlas", "customs"])

# ── Schemas ───────────────────────────────────────────────────────────────────

class WarenPosition(BaseModel):
    warennummer_hs8: str
    bezeichnung: str
    menge: float
    einheit: str
    statistischer_wert_eur: float
    ursprungsland: str


class ZollausfuhrAnmeldungCreate(BaseModel):
    referenz_nr: str
    ausfuhrland_code: str = "DE"
    bestimmungsland_code: str
    anmelder_eori: str
    waren_positionen: list[WarenPosition]
    befoerderungsart: int = 30  # 10=See/20=Schiene/30=Strasse/40=Luft/50=Post
    ausfuehrender_nr: str
    ausfuhrdatum: str
    lieferbedingung: str


class ZollausfuhrAnmeldungOut(ZollausfuhrAnmeldungCreate):
    id: str
    status: str = "ENTWURF"  # ENTWURF/UEBERMITTELT/BEWILLIGT/ABGELEHNT/ERLEDIGT
    atlas_mrn: Optional[str] = None
    erstellt_am: str


class ZollausfuhrStatusUpdate(BaseModel):
    mrn: str
    neuer_status: str
    atlas_meldung: Optional[str] = None


# ── Static HS-tariff seed data ─────────────────────────────────────────────

_HS_SEED = [
    {"hs8": "10019900", "bezeichnung": "Weizen, andere"},
    {"hs8": "10059000", "bezeichnung": "Mais, andere"},
    {"hs8": "12019000", "bezeichnung": "Sojabohnen, andere"},
    {"hs8": "12060010", "bezeichnung": "Sonnenblumenkerne, zur Aussaat"},
    {"hs8": "12060091", "bezeichnung": "Sonnenblumenkerne, andere"},
    {"hs8": "10039000", "bezeichnung": "Gerste, andere"},
    {"hs8": "10051000", "bezeichnung": "Mais, Saatgut"},
    {"hs8": "15079010", "bezeichnung": "Sojaöl, raffiniert"},
    {"hs8": "23040000", "bezeichnung": "Sojaschrot"},
    {"hs8": "10011900", "bezeichnung": "Hartweizen, andere"},
]

# In-memory store (fallback when DB table absent)
_store: dict[str, dict] = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _row_to_out(row) -> ZollausfuhrAnmeldungOut:
    import json
    waren = row.waren_positionen
    if isinstance(waren, str):
        waren = json.loads(waren)
    return ZollausfuhrAnmeldungOut(
        id=str(row.id),
        referenz_nr=row.referenz_nr,
        ausfuhrland_code=row.ausfuhrland_code,
        bestimmungsland_code=row.bestimmungsland_code,
        anmelder_eori=row.anmelder_eori,
        waren_positionen=[WarenPosition(**w) for w in (waren or [])],
        befoerderungsart=row.befoerderungsart,
        ausfuehrender_nr=row.ausfuehrender_nr,
        ausfuhrdatum=str(row.ausfuhrdatum),
        lieferbedingung=row.lieferbedingung,
        status=row.status,
        atlas_mrn=row.atlas_mrn,
        erstellt_am=str(row.erstellt_am),
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/ausfuhranmeldungen", response_model=list[ZollausfuhrAnmeldungOut])
def list_anmeldungen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        rows = db.execute(
            text(
                "SELECT * FROM domain_compliance.zollausfuhr_anmeldungen "
                "WHERE tenant_id = :tid ORDER BY erstellt_am DESC LIMIT 200"
            ),
            {"tid": tenant_id},
        ).fetchall()
        return [_row_to_out(r) for r in rows]
    except Exception:
        return list(_store.values())


@router.post("/ausfuhranmeldungen", response_model=ZollausfuhrAnmeldungOut, status_code=201)
def create_anmeldung(
    payload: ZollausfuhrAnmeldungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    import json
    new_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    record = ZollausfuhrAnmeldungOut(
        id=new_id,
        **payload.model_dump(),
        status="ENTWURF",
        atlas_mrn=None,
        erstellt_am=now,
    )
    try:
        db.execute(
            text(
                "INSERT INTO domain_compliance.zollausfuhr_anmeldungen "
                "(id, tenant_id, referenz_nr, ausfuhrland_code, bestimmungsland_code, "
                "anmelder_eori, waren_positionen, befoerderungsart, ausfuehrender_nr, "
                "ausfuhrdatum, lieferbedingung, status, atlas_mrn, erstellt_am) "
                "VALUES (:id, :tid, :ref, :aus, :best, :eori, :waren::jsonb, "
                ":bef, :nr, :datum, :lb, 'ENTWURF', NULL, :now)"
            ),
            {
                "id": new_id,
                "tid": tenant_id,
                "ref": payload.referenz_nr,
                "aus": payload.ausfuhrland_code,
                "best": payload.bestimmungsland_code,
                "eori": payload.anmelder_eori,
                "waren": json.dumps([w.model_dump() for w in payload.waren_positionen]),
                "bef": payload.befoerderungsart,
                "nr": payload.ausfuehrender_nr,
                "datum": payload.ausfuhrdatum,
                "lb": payload.lieferbedingung,
                "now": now,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        _store[new_id] = record.model_dump()
    return record


@router.get("/ausfuhranmeldungen/{id}", response_model=ZollausfuhrAnmeldungOut)
def get_anmeldung(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        row = db.execute(
            text(
                "SELECT * FROM domain_compliance.zollausfuhr_anmeldungen "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": id, "tid": tenant_id},
        ).fetchone()
        if row:
            return _row_to_out(row)
    except Exception:
        pass
    if id in _store:
        return ZollausfuhrAnmeldungOut(**_store[id])
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Anmeldung nicht gefunden")


@router.put("/ausfuhranmeldungen/{id}", response_model=ZollausfuhrAnmeldungOut)
def update_anmeldung(
    id: str,
    payload: ZollausfuhrAnmeldungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Update only allowed for ENTWURF status."""
    import json
    try:
        db.execute(
            text(
                "UPDATE domain_compliance.zollausfuhr_anmeldungen SET "
                "referenz_nr=:ref, bestimmungsland_code=:best, anmelder_eori=:eori, "
                "waren_positionen=:waren::jsonb, befoerderungsart=:bef, "
                "ausfuehrender_nr=:nr, ausfuhrdatum=:datum, lieferbedingung=:lb "
                "WHERE id=:id AND tenant_id=:tid AND status='ENTWURF'"
            ),
            {
                "ref": payload.referenz_nr,
                "best": payload.bestimmungsland_code,
                "eori": payload.anmelder_eori,
                "waren": json.dumps([w.model_dump() for w in payload.waren_positionen]),
                "bef": payload.befoerderungsart,
                "nr": payload.ausfuehrender_nr,
                "datum": payload.ausfuhrdatum,
                "lb": payload.lieferbedingung,
                "id": id,
                "tid": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        if id in _store:
            _store[id].update(payload.model_dump())
    return get_anmeldung(id, db, tenant_id)


@router.delete("/ausfuhranmeldungen/{id}", status_code=204, response_class=Response, response_model=None)
def delete_anmeldung(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Cancel (ENTWURF only) — sets status=ERLEDIGT."""
    try:
        db.execute(
            text(
                "UPDATE domain_compliance.zollausfuhr_anmeldungen "
                "SET status='ERLEDIGT' WHERE id=:id AND tenant_id=:tid AND status='ENTWURF'"
            ),
            {"id": id, "tid": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
        if id in _store:
            _store[id]["status"] = "ERLEDIGT"
    return Response(status_code=204)


@router.post("/ausfuhranmeldungen/{id}/uebermitteln")
def uebermitteln(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Überträgt Ausfuhranmeldung an ATLAS — ECS Phase 2, vollständige Simulation."""
    # Fallback: In-Memory-Store der Service-Instanz mit Endpunkt-Store synchronisieren
    svc = ATLASCustomsService(db=db, tenant_id=tenant_id)
    svc._fallback_store = _store  # type: ignore[attr-defined]
    try:
        return svc.submit_to_atlas(anmeldung_id=id, db=db)
    except Exception as exc:
        from app.core.exceptions import EntityNotFoundError, ValidationFailedError
        if isinstance(exc, EntityNotFoundError):
            raise HTTPException(status_code=404, detail=str(exc))
        if isinstance(exc, ValidationFailedError):
            raise HTTPException(status_code=422, detail=str(exc))
        raise


@router.post("/ausfuhranmeldungen/{id}/vorab-validieren")
def vorab_validieren(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Vorab-Validierung einer Anmeldung ohne ATLAS-Übermittlung (TARIC + Pflichtfelder)."""
    svc = ATLASCustomsService(db=db, tenant_id=tenant_id)
    svc._fallback_store = _store  # type: ignore[attr-defined]
    anmeldung = svc._load_anmeldung(id, db)
    if not anmeldung:
        raise HTTPException(status_code=404, detail="Anmeldung nicht gefunden")
    return svc.validate_anmeldung(anmeldung)


@router.get("/ausfuhrnachrichten/{mrn}")
def ausfuhrnachricht(
    mrn: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft Ausfuhrnachricht (IE529/IE518) für eine MRN ab."""
    svc = ATLASCustomsService(db=db, tenant_id=tenant_id)
    svc._fallback_store = _store  # type: ignore[attr-defined]
    return svc.get_ausfuhrnachricht(mrn=mrn, db=db)


@router.post("/atlas-callback")
def atlas_callback(
    body: ZollausfuhrStatusUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Receive ATLAS status webhook."""
    try:
        db.execute(
            text(
                "UPDATE domain_compliance.zollausfuhr_anmeldungen "
                "SET status=:status WHERE atlas_mrn=:mrn AND tenant_id=:tid"
            ),
            {"status": body.neuer_status, "mrn": body.mrn, "tid": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
        for v in _store.values():
            if v.get("atlas_mrn") == body.mrn:
                v["status"] = body.neuer_status
    return {"empfangen": True}


@router.get("/warennummern/suche")
def warennummern_suche(q: str = Query(default="")):
    """HS tariff number search (static agricultural seed data)."""
    q_lower = q.lower()
    if not q_lower:
        return _HS_SEED
    return [
        item for item in _HS_SEED
        if q_lower in item["hs8"] or q_lower in item["bezeichnung"].lower()
    ]
