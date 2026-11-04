"""Laborproben, Laborauftraege und Befunde im Mandanten.

Mounted under `/labor` and `/qualitaet` in api.py (identische Pfade: .../labor-auftraege).

Bis 03.11.2026 (Batch 8) legte jeder Zugriff per ``_seed`` erfundene Proben und Auftraege an, kein Weg kannte einen
Mandanten, ein Auftrag liess sich zu einer beliebigen (auch fremden oder erfundenen) Charge anlegen, und der Befund
gab Analysewerte, Grenzwerte und Bemerkung zurueck, ohne sie zu speichern. Jetzt: Mandant aus der Anmeldung, RLS
(Migration ``scheinwege_mandant_20261103``), Charge muss im Mandanten existieren, der Befund speichert, was er meldet.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.labor_schemas import LaborAuftragListOut, LaborAuftragOut, LaborProbeListOut, LaborStatsOut
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.operations.models import Charge, LaborAuftragEntry, LaborProbe

router = APIRouter(tags=["Labor"])

ENTSCHEIDUNGEN = ("freigeben", "sperren", "nachpruefung")


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _folgeaktion_for_entscheidung(entscheidung: Optional[str]) -> str:
    """Naechster Schritt fuer die Bedienung; der Befund selbst sperrt oder gibt die Charge nicht frei."""
    if entscheidung == "sperren":
        return "charge_sperren"
    if entscheidung == "freigeben":
        return "qs_freigeben"
    if entscheidung == "nachpruefung":
        return "nachpruefung_anlegen"
    return "befund_erfassen"


def _auftrag_to_dict(i: LaborAuftragEntry, befund: Optional[LaborProbe] = None) -> dict[str, Any]:
    """Frontend erwartet camelCase fuer chargenId."""
    entscheidung = befund.status if befund and befund.status in ENTSCHEIDUNGEN else None
    return {
        "id": i.id,
        "chargenId": i.chargen_id,
        "chargen_id": i.chargen_id,
        "charge": i.chargen_id,
        "labor": i.labor,
        "analysen": int(i.analysen or 0),
        "auftragsdatum": _dt(i.auftragsdatum) or "",
        "status": i.status,
        "befund": {
            "id": befund.id,
            "probennummer": befund.probennummer,
            "entscheidung": entscheidung,
            "datum": _dt(befund.datum),
            "labor": befund.labor,
        } if befund else None,
        "qs_entscheidung": entscheidung,
        "folgeaktion": _folgeaktion_for_entscheidung(entscheidung),
        "analysewerte": (befund.analysewerte or {}) if befund else {},
        "grenzwerte": (befund.grenzwerte or {}) if befund else {},
        "bemerkung": befund.bemerkung if befund else None,
    }


class LaborAuftragCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    chargenId: Optional[str] = None  # noqa: N815 - Schluessel des Wizards
    chargen_id: Optional[str] = None
    artikel: Optional[str] = None
    labor: str = ""
    analysen: Optional[list[str]] = None
    prioritaet: Optional[str] = None
    bemerkungen: Optional[str] = None


class LaborBefundCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entscheidung: str
    analysewerte: dict[str, Any] = Field(default_factory=dict)
    grenzwerte: dict[str, Any] = Field(default_factory=dict)
    bemerkung: Optional[str] = None


def _befund_map(db: Session, tenant_id: str, auftrag_ids: list[str]) -> dict[str, LaborProbe]:
    if not auftrag_ids:
        return {}
    probennummern = [f"BEF-{item_id}" for item_id in auftrag_ids]
    rows = (db.query(LaborProbe)
            .filter(LaborProbe.tenant_id == tenant_id, LaborProbe.probennummer.in_(probennummern))
            .order_by(LaborProbe.datum.desc()).all())
    result: dict[str, LaborProbe] = {}
    for row in rows:
        result.setdefault(row.probennummer.removeprefix("BEF-"), row)
    return result


def _eigener_auftrag(db: Session, tenant_id: str, entry_id: str) -> LaborAuftragEntry:
    row = db.query(LaborAuftragEntry).filter(LaborAuftragEntry.tenant_id == tenant_id, LaborAuftragEntry.id == entry_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Labor-Auftrag nicht gefunden")
    return row


@router.get("/proben", response_model=LaborProbeListOut, summary="Proben auflisten")
async def list_proben(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(500, ge=1, le=2000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    query = db.query(LaborProbe).filter(LaborProbe.tenant_id == tenant_id)
    if status:
        query = query.filter(LaborProbe.status == status)
    items = query.order_by(LaborProbe.datum.desc()).limit(limit).all()
    return {
        "items": [{"id": i.id, "probennummer": i.probennummer, "typ": i.typ, "artikel": i.artikel, "datum": _dt(i.datum),
                   "labor": i.labor, "status": i.status} for i in items],
        "total": len(items),
    }


@router.get("/labor-auftraege", response_model=LaborAuftragListOut, summary="Labor auftraege auflisten")
async def list_labor_auftraege(
    limit: int = Query(500, ge=1, le=2000), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
) -> dict:
    items = (db.query(LaborAuftragEntry).filter(LaborAuftragEntry.tenant_id == tenant_id)
             .order_by(LaborAuftragEntry.auftragsdatum.desc()).limit(limit).all())
    befunde = _befund_map(db, tenant_id, [i.id for i in items])
    return {"items": [_auftrag_to_dict(i, befunde.get(i.id)) for i in items], "total": len(items)}


@router.get("/labor-auftraege/{entry_id}", response_model=LaborAuftragOut, summary="Labor auftrag abrufen")
async def get_labor_auftrag(entry_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    """Einzelner Labor-Auftrag fuer Detail-UI."""
    row = _eigener_auftrag(db, tenant_id, entry_id)
    return _auftrag_to_dict(row, _befund_map(db, tenant_id, [entry_id]).get(entry_id))


@router.post("/labor-auftraege", response_model=LaborAuftragOut, status_code=201, summary="Labor auftrag anlegen", dependencies=SCHREIBEN["AGRAR"])
async def create_labor_auftrag(body: LaborAuftragCreate, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    """Neuen Labor-Auftrag anlegen (Wizard `labor-auftrag.tsx`); die Charge muss im Mandanten existieren."""
    chargen = (body.chargenId or body.chargen_id or "").strip()
    if not chargen:
        raise HTTPException(status_code=422, detail="chargenId erforderlich")
    labor_name = (body.labor or "").strip()
    if not labor_name:
        raise HTTPException(status_code=422, detail="labor erforderlich")
    if db.query(Charge.id).filter(Charge.tenant_id == tenant_id, Charge.chargen_id == chargen).first() is None:
        raise HTTPException(status_code=404, detail="Charge nicht gefunden")

    analysen_list = body.analysen if isinstance(body.analysen, list) else []
    status = "in-bearbeitung" if (body.prioritaet or "").lower() == "express" else "offen"
    entry = LaborAuftragEntry(tenant_id=tenant_id, chargen_id=chargen, labor=labor_name, analysen=len(analysen_list),
                              auftragsdatum=datetime.now(timezone.utc), status=status)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _auftrag_to_dict(entry)


@router.post("/labor-auftraege/{entry_id}/befund", response_model=LaborAuftragOut, summary="Labor befund uebernehmen", dependencies=SCHREIBEN["AGRAR"])
async def create_labor_befund(
    entry_id: str, body: LaborBefundCreate, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
) -> dict:
    row = _eigener_auftrag(db, tenant_id, entry_id)
    if body.entscheidung not in ENTSCHEIDUNGEN:
        raise HTTPException(status_code=422, detail="entscheidung muss freigeben, sperren oder nachpruefung sein")

    row.status = "abgeschlossen" if body.entscheidung in {"freigeben", "sperren"} else "in-bearbeitung"
    befund = LaborProbe(
        tenant_id=tenant_id, probennummer=f"BEF-{entry_id}", typ="Laborbefund", artikel=row.chargen_id,
        datum=datetime.now(timezone.utc), labor=row.labor, status=body.entscheidung,
        analysewerte=body.analysewerte, grenzwerte=body.grenzwerte, bemerkung=body.bemerkung,
    )
    db.add(befund)
    db.commit()
    db.refresh(row)
    db.refresh(befund)
    return _auftrag_to_dict(row, befund)


@router.get("/stats", response_model=LaborStatsOut, summary="Labor stats abrufen")
async def get_labor_stats(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    stati = [s for (s,) in db.query(LaborProbe.status).filter(LaborProbe.tenant_id == tenant_id).limit(10000).all()]
    return {"abgeschlossen": stati.count("abgeschlossen"), "in-bearbeitung": stati.count("in-bearbeitung"),
            "ausstehend": stati.count("ausstehend")}
