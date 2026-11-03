"""Marketingkampagnen (Betriebsplanung) im Mandanten.

Bis 03.11.2026 (Batch 8) legte jeder Lesezugriff per ``_seed`` zwei erfundene Kampagnen an, kein Weg kannte einen
Mandanten, Aendern/Loeschen/KPIs nahmen die Kennung als Zahl an (Kennungen sind ``MK-...``, also immer 422), und
die KPI-Sicht meldete ein Ist-Budget von 0 ohne Kostenquelle. Jetzt: Mandant aus der Anmeldung, RLS auf
``domain_ops.ops_marketing_kampagnen`` (Migration ``scheinwege_mandant_20261103``), Ist-Werte ``None`` bis es eine
Quelle gibt.

Offen (Workboard): Kampagnen gibt es zusaetzlich im CRM (``/crm/campaigns``); welche Quelle fuehrt, ist eine
Fachentscheidung.
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.marketing_schemas import (
    MarketingKampagneListOut,
    MarketingKampagneOut,
    MarketingKpiOut,
    MarketingStatsOut,
)
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.operations.models import MarketingKampagneEntry

router = APIRouter(prefix="/marketing", tags=["Marketing"])

STATUS = ("geplant", "aktiv", "beendet", "abgebrochen")


class MarketingKampagneCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=255)
    typ: str = Field(min_length=1, max_length=80)
    zielgruppe: str = Field(default="", max_length=120)
    startdatum: date
    enddatum: Optional[date] = None
    budget: float = Field(default=0, ge=0)
    status: str = "geplant"


class MarketingKampagneUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    typ: Optional[str] = Field(default=None, min_length=1, max_length=80)
    zielgruppe: Optional[str] = Field(default=None, max_length=120)
    startdatum: Optional[date] = None
    enddatum: Optional[date] = None
    budget: Optional[float] = Field(default=None, ge=0)
    status: Optional[str] = None


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _als_zeit(v: Optional[date]) -> Optional[datetime]:
    return datetime.combine(v, datetime.min.time()) if v else None


def _out(k: MarketingKampagneEntry) -> dict:
    return {"id": k.id, "name": k.name, "typ": k.typ, "zielgruppe": k.zielgruppe, "startdatum": _dt(k.startdatum),
            "enddatum": _dt(k.enddatum), "budget": float(k.budget or 0), "status": k.status}


def _pruefen(status: Optional[str], start: Optional[datetime], ende: Optional[datetime]) -> None:
    if status is not None and status not in STATUS:
        raise HTTPException(status_code=422, detail=f"status muss einer von {', '.join(STATUS)} sein")
    if start and ende and ende < start:
        raise HTTPException(status_code=422, detail="enddatum liegt vor startdatum")


def _eigene(db: Session, tenant_id: str, kampagne_id: str) -> MarketingKampagneEntry:
    k = db.query(MarketingKampagneEntry).filter(
        MarketingKampagneEntry.tenant_id == tenant_id, MarketingKampagneEntry.id == kampagne_id).first()
    if not k:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    return k


@router.get("/kampagnen", response_model=MarketingKampagneListOut, summary="Kampagnen auflisten")
async def list_kampagnen(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(500, ge=1, le=2000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    query = db.query(MarketingKampagneEntry).filter(MarketingKampagneEntry.tenant_id == tenant_id)
    if status:
        query = query.filter(MarketingKampagneEntry.status == status)
    items = [_out(k) for k in query.order_by(MarketingKampagneEntry.startdatum.desc()).limit(limit).all()]
    return {"items": items, "total": len(items)}


@router.get("/stats", response_model=MarketingStatsOut, summary="Marketing stats abrufen")
async def get_marketing_stats(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    items = db.query(MarketingKampagneEntry.status, MarketingKampagneEntry.budget).filter(
        MarketingKampagneEntry.tenant_id == tenant_id).limit(10000).all()
    return {
        "aktiv": sum(1 for s, _ in items if s == "aktiv"),
        "geplant": sum(1 for s, _ in items if s == "geplant"),
        "beendet": sum(1 for s, _ in items if s == "beendet"),
        "budget_aktiv": sum(float(b or 0) for s, b in items if s == "aktiv"),
    }


@router.get("/kampagnen/{kampagne_id}/kpis", response_model=MarketingKpiOut, summary="Kampagne kpis abrufen")
async def get_kampagne_kpis(kampagne_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    """Plan aus der Kampagne. Ist, Oeffnungs-, Klick- und Abschlussrate sowie ROI brauchen eine Kosten- und
    Versandquelle, die es nicht gibt - deshalb ``None`` (unbekannt), nicht 0 (gemessen und leer)."""
    k = _eigene(db, tenant_id, kampagne_id)
    return {"id": k.id, "name": k.name, "status": k.status, "budget_plan": float(k.budget or 0), "budget_ist": None,
            "open_rate": None, "click_rate": None, "conversion_rate": None, "roi": None}


@router.post("/kampagnen", response_model=MarketingKampagneOut, status_code=201, summary="Kampagne anlegen", dependencies=SCHREIBEN["CRM"])
async def create_kampagne(body: MarketingKampagneCreate, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    start, ende = _als_zeit(body.startdatum), _als_zeit(body.enddatum)
    _pruefen(body.status, start, ende)
    kampagne = MarketingKampagneEntry(tenant_id=tenant_id, name=body.name, typ=body.typ, zielgruppe=body.zielgruppe,
                                      startdatum=start, enddatum=ende, budget=body.budget, status=body.status)
    db.add(kampagne)
    db.commit()
    db.refresh(kampagne)
    return _out(kampagne)


@router.put("/kampagnen/{kampagne_id}", response_model=MarketingKampagneOut, summary="Kampagne aktualisieren", dependencies=SCHREIBEN["CRM"])
async def update_kampagne(
    kampagne_id: str, body: MarketingKampagneUpdate, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
) -> dict:
    k = _eigene(db, tenant_id, kampagne_id)
    update_data = body.model_dump(exclude_unset=True)
    for feld in ("startdatum", "enddatum"):
        if feld in update_data:
            update_data[feld] = _als_zeit(update_data[feld])
    _pruefen(update_data.get("status"), update_data.get("startdatum", k.startdatum), update_data.get("enddatum", k.enddatum))
    for field, value in update_data.items():
        setattr(k, field, value)
    db.commit()
    db.refresh(k)
    return _out(k)


@router.delete("/kampagnen/{kampagne_id}", response_class=Response, status_code=204, response_model=None, summary="Kampagne löschen", dependencies=SCHREIBEN["CRM"])
async def delete_kampagne(kampagne_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> Response:
    """Nur geplante Kampagnen; eine laufende oder beendete ist ein Vorgang mit Wirkung beim Kunden."""
    k = _eigene(db, tenant_id, kampagne_id)
    if k.status not in ("geplant", "abgebrochen"):
        raise HTTPException(status_code=409, detail="Nur geplante oder abgebrochene Kampagnen können gelöscht werden")
    db.delete(k)
    db.commit()
    return Response(status_code=204)
