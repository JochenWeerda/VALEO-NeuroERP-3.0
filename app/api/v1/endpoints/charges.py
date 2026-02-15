"""
Charges API - Lot/Batch Management (SQLAlchemy)
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.repository import ChargeRepository
from app.domains.operations.models import ChargeStatus

router = APIRouter(prefix="/chargen", tags=["Charges"])


def _parse_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class ChargeCreate(BaseModel):
    artikel_id: str = Field(..., description="Article ID")
    artikel: str = Field(..., description="Article name")
    chargen_id: str = Field(..., description="Batch number")
    menge: float = Field(..., gt=0, description="Quantity in tons")
    lagerort: str = Field(..., description="Storage location")
    eingang: str = Field(..., description="Receipt date ISO format")
    herstellungsdatum: Optional[str] = Field(default=None, description="Production date ISO format")
    losnummer: Optional[str] = None
    produktbezeichnung: Optional[str] = None
    rueckverfolgbar_bis_stunden: int = Field(default=4, ge=1, le=24)
    herkunft: Optional[str] = None
    qualitaetsstatus: str = Field(default=ChargeStatus.IN_PRUEFUNG.value)
    bemerkungen: Optional[str] = None
    rohstoffe: Optional[list[dict]] = None
    lieferant_info: Optional[dict] = None
    kunden_info: Optional[dict] = None
    produktionsprozess: Optional[dict] = None
    digitales_mischbuch: Optional[dict] = None
    haccp_system: Optional[dict] = None
    eigenkontrollen: Optional[list[dict]] = None
    warentrennung_qs_nicht_qs: bool = False
    krisenmanagement: Optional[dict] = None
    futtermittelmonitoring: Optional[dict] = None
    qualitaetspersonal: Optional[dict] = None
    qs_datenbank: Optional[dict] = None


class ChargeUpdate(BaseModel):
    menge: Optional[float] = None
    lagerort: Optional[str] = None
    qualitaetsstatus: Optional[str] = None
    freigabe_datum: Optional[str] = None
    bemerkungen: Optional[str] = None
    status: Optional[str] = None
    herstellungsdatum: Optional[str] = None
    losnummer: Optional[str] = None
    produktbezeichnung: Optional[str] = None
    rueckverfolgbar_bis_stunden: Optional[int] = Field(default=None, ge=1, le=24)
    rohstoffe: Optional[list[dict]] = None
    lieferant_info: Optional[dict] = None
    kunden_info: Optional[dict] = None
    produktionsprozess: Optional[dict] = None
    digitales_mischbuch: Optional[dict] = None
    haccp_system: Optional[dict] = None
    eigenkontrollen: Optional[list[dict]] = None
    warentrennung_qs_nicht_qs: Optional[bool] = None
    krisenmanagement: Optional[dict] = None
    futtermittelmonitoring: Optional[dict] = None
    qualitaetspersonal: Optional[dict] = None
    qs_datenbank: Optional[dict] = None


def _to_dict(charge) -> dict:
    return {
        "id": charge.id,
        "chargenId": charge.chargen_id,
        "losnummer": charge.losnummer,
        "artikel": charge.artikel,
        "artikelId": charge.artikel_id,
        "produktbezeichnung": charge.produktbezeichnung,
        "menge": float(charge.menge),
        "lagerort": charge.lagerort,
        "eingang": charge.eingang.isoformat() if charge.eingang else None,
        "herstellungsdatum": charge.herstellungsdatum.isoformat() if charge.herstellungsdatum else None,
        "status": charge.status,
        "qualitaetsstatus": charge.qualitaetsstatus,
        "freigabeDatum": charge.freigabe_datum.isoformat() if charge.freigabe_datum else None,
        "herkunft": charge.herkunft,
        "bemerkungen": charge.bemerkungen,
        "rueckverfolgbar_bis_stunden": charge.rueckverfolgbar_bis_stunden,
        "rohstoffe": charge.rohstoffe or [],
        "lieferant_info": charge.lieferant_info or {},
        "kunden_info": charge.kunden_info or {},
        "produktionsprozess": charge.produktionsprozess or {},
        "digitales_mischbuch": charge.digitales_mischbuch or {},
        "haccp_system": charge.haccp_system or {},
        "eigenkontrollen": charge.eigenkontrollen or [],
        "warentrennung_qs_nicht_qs": bool(charge.warentrennung_qs_nicht_qs),
        "krisenmanagement": charge.krisenmanagement or {},
        "futtermittelmonitoring": charge.futtermittelmonitoring or {},
        "qualitaetspersonal": charge.qualitaetspersonal or {},
        "qs_datenbank": charge.qs_datenbank or {},
        "createdAt": charge.created_at.isoformat() if charge.created_at else None,
        "updatedAt": charge.updated_at.isoformat() if charge.updated_at else None,
    }


@router.get("", response_model=dict)
async def list_charges(
    search: Optional[str] = Query(None, description="Search term"),
    status: Optional[str] = Query(None, description="Filter by status"),
    lagerort: Optional[str] = Query(None, description="Filter by storage location"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    repo = ChargeRepository(db)
    items = repo.get_all(skip=offset, limit=limit, search=search, status=status, lagerort=lagerort)
    total = repo.count(search=search, status=status, lagerort=lagerort)
    return {"items": [_to_dict(i) for i in items], "total": total, "limit": limit, "offset": offset}


@router.get("/{charge_id}", response_model=dict)
async def get_charge(charge_id: str, db: Session = Depends(get_db)) -> dict:
    repo = ChargeRepository(db)
    charge = repo.get_by_id(charge_id)
    if not charge:
        raise HTTPException(status_code=404, detail="Charge not found")
    return _to_dict(charge)


@router.post("", response_model=dict, status_code=201)
async def create_charge(data: ChargeCreate, db: Session = Depends(get_db)) -> dict:
    repo = ChargeRepository(db)
    if repo.get_by_chargen_id(data.chargen_id):
        raise HTTPException(status_code=409, detail="Charge with this chargen_id already exists")

    payload = data.model_dump()
    payload["eingang"] = _parse_iso_datetime(payload["eingang"])
    if payload.get("herstellungsdatum"):
        payload["herstellungsdatum"] = _parse_iso_datetime(payload["herstellungsdatum"])
    payload["status"] = ChargeStatus.ERFASST.value
    charge = repo.create(payload)
    return _to_dict(charge)


@router.patch("/{charge_id}", response_model=dict)
async def update_charge(charge_id: str, data: ChargeUpdate, db: Session = Depends(get_db)) -> dict:
    repo = ChargeRepository(db)
    payload = data.model_dump(exclude_unset=True)
    if "freigabe_datum" in payload and payload["freigabe_datum"]:
        payload["freigabe_datum"] = _parse_iso_datetime(payload["freigabe_datum"])
    if "herstellungsdatum" in payload and payload["herstellungsdatum"]:
        payload["herstellungsdatum"] = _parse_iso_datetime(payload["herstellungsdatum"])
    charge = repo.update(charge_id, payload)
    if not charge:
        raise HTTPException(status_code=404, detail="Charge not found")
    return _to_dict(charge)


@router.post("/{charge_id}/freigabe", response_model=dict)
async def freigabe_charge(charge_id: str, db: Session = Depends(get_db)) -> dict:
    repo = ChargeRepository(db)
    charge = repo.get_by_id(charge_id)
    if not charge:
        raise HTTPException(status_code=404, detail="Charge not found")
    if charge.qualitaetsstatus != ChargeStatus.FREIGEGEBEN.value:
        raise HTTPException(status_code=400, detail="Charge must be quality approved first")

    updated = repo.update(
        charge_id,
        {
            "status": ChargeStatus.FREIGEGEBEN.value,
            "freigabe_datum": datetime.utcnow(),
        },
    )
    return _to_dict(updated)


@router.delete("/{charge_id}", status_code=204)
async def delete_charge(charge_id: str, db: Session = Depends(get_db)):
    repo = ChargeRepository(db)
    if not repo.delete(charge_id):
        raise HTTPException(status_code=404, detail="Charge not found")


@router.get("/stats/summary", response_model=dict)
async def get_charge_stats(db: Session = Depends(get_db)) -> dict:
    repo = ChargeRepository(db)
    return repo.get_stats()


@router.get("/{charge_id}/qs-readiness", response_model=dict)
async def get_qs_readiness(charge_id: str, db: Session = Depends(get_db)) -> dict:
    repo = ChargeRepository(db)
    charge = repo.get_by_id(charge_id)
    if not charge:
        raise HTTPException(status_code=404, detail="Charge not found")

    checks = {
        "rueckverfolgbarkeit": bool(charge.chargen_id and charge.herstellungsdatum and charge.rohstoffe and charge.lieferant_info and charge.kunden_info),
        "produktionsdokumentation": bool(charge.produktionsprozess and charge.digitales_mischbuch),
        "haccp_und_eigenkontrollen": bool(charge.haccp_system and charge.eigenkontrollen),
        "lieferanten_und_kundenmanagement": bool(charge.lieferant_info and charge.kunden_info and charge.warentrennung_qs_nicht_qs),
        "krisenmanagement": bool(charge.krisenmanagement),
        "futtermittelmonitoring": bool(charge.futtermittelmonitoring),
        "schulungen_und_zustaendigkeiten": bool(charge.qualitaetspersonal),
        "qs_datenbank_integration": bool(charge.qs_datenbank),
    }
    score = sum(1 for x in checks.values() if x)
    return {
        "charge_id": charge.id,
        "checks": checks,
        "score": score,
        "max_score": len(checks),
        "ready": score == len(checks),
    }
