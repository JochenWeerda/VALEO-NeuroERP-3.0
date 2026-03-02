"""
Agrar Maschinen — CRUD für Maschinenpark (Landhandel + Lohnunternehmer)

Endpoints:
  GET    /agrar/maschinen               Liste aller Maschinen (Filter: typ, status, customer_id)
  POST   /agrar/maschinen               Maschine anlegen
  GET    /agrar/maschinen/{id}          Maschine Detail
  PATCH  /agrar/maschinen/{id}          Maschine aktualisieren
  DELETE /agrar/maschinen/{id}          Maschine deaktivieren (soft-delete)
  PATCH  /agrar/maschinen/{id}/stunden  Betriebsstunden buchen
  PATCH  /agrar/maschinen/{id}/status   Status-Wechsel (verfuegbar/im-einsatz/werkstatt)
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.infrastructure.models.agrar_models import AgrarMaschine

router = APIRouter(tags=["agrar", "maschinen"])


# ────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ────────────────────────────────────────────────────────────────────────────

class MaschineCreate(BaseModel):
    name: str
    typ: str                         # Traktor | Mähdrescher | Anhänger | Spritze | Grubber | Sonstiges
    hersteller: Optional[str] = None
    modell: Optional[str] = None
    baujahr: Optional[int] = None
    kennzeichen: Optional[str] = None
    fahrgestellnummer: Optional[str] = None
    leistung_kw: Optional[float] = None
    betriebsstunden: float = 0.0
    naechste_wartung_stunden: Optional[float] = None
    naechste_wartung_datum: Optional[datetime] = None
    status: str = "verfuegbar"       # verfuegbar | im-einsatz | werkstatt | stillgelegt
    standort: Optional[str] = None
    customer_id: Optional[str] = None  # None = eigene Maschine des Landhandels
    notiz: Optional[str] = None


class MaschineUpdate(BaseModel):
    name: Optional[str] = None
    typ: Optional[str] = None
    hersteller: Optional[str] = None
    modell: Optional[str] = None
    baujahr: Optional[int] = None
    kennzeichen: Optional[str] = None
    fahrgestellnummer: Optional[str] = None
    leistung_kw: Optional[float] = None
    naechste_wartung_stunden: Optional[float] = None
    naechste_wartung_datum: Optional[datetime] = None
    standort: Optional[str] = None
    customer_id: Optional[str] = None
    notiz: Optional[str] = None


class StundenBuchung(BaseModel):
    stunden: float                   # Delta-Stunden (positiv = Buchung)
    bemerkung: Optional[str] = None


class StatusWechsel(BaseModel):
    status: str                      # verfuegbar | im-einsatz | werkstatt | stillgelegt
    bemerkung: Optional[str] = None


def _to_dict(m: AgrarMaschine) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "typ": m.typ,
        "hersteller": m.hersteller,
        "modell": m.modell,
        "baujahr": m.baujahr,
        "kennzeichen": m.kennzeichen,
        "fahrgestellnummer": m.fahrgestellnummer,
        "leistung_kw": float(m.leistung_kw) if m.leistung_kw is not None else None,
        "betriebsstunden": float(m.betriebsstunden or 0),
        "naechste_wartung_stunden": float(m.naechste_wartung_stunden) if m.naechste_wartung_stunden else None,
        "naechste_wartung_datum": m.naechste_wartung_datum.isoformat() if m.naechste_wartung_datum else None,
        "status": m.status,
        "standort": m.standort,
        "customer_id": m.customer_id,
        "notiz": m.notiz,
        "ist_aktiv": m.ist_aktiv,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        # Berechnete Felder
        "wartung_faellig": (
            m.naechste_wartung_stunden is not None
            and float(m.betriebsstunden or 0) >= float(m.naechste_wartung_stunden)
        ),
        "auslastung": None,  # Wird ggf. aus Einsatzstunden berechnet (Phase 2)
    }


# ────────────────────────────────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────────────────────────────────

@router.get("/maschinen")
def list_maschinen(
    typ: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    customer_id: Optional[str] = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste aller Maschinen mit optionalen Filtern."""
    q = db.query(AgrarMaschine).filter(
        AgrarMaschine.tenant_id == tenant_id,
        AgrarMaschine.ist_aktiv == True,
    )
    if typ:
        q = q.filter(AgrarMaschine.typ == typ)
    if status:
        q = q.filter(AgrarMaschine.status == status)
    if customer_id:
        q = q.filter(AgrarMaschine.customer_id == customer_id)

    maschinen = q.order_by(AgrarMaschine.name).all()
    items = [_to_dict(m) for m in maschinen]

    return {
        "items": items,
        "total": len(items),
        "stats": {
            "gesamt": len(items),
            "im_einsatz": sum(1 for m in maschinen if m.status == "im-einsatz"),
            "verfuegbar": sum(1 for m in maschinen if m.status == "verfuegbar"),
            "werkstatt": sum(1 for m in maschinen if m.status == "werkstatt"),
            "wartung_faellig": sum(
                1 for m in maschinen
                if m.naechste_wartung_stunden
                and float(m.betriebsstunden or 0) >= float(m.naechste_wartung_stunden)
            ),
        },
    }


@router.post("/maschinen", status_code=201)
def create_maschine(
    body: MaschineCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neue Maschine anlegen."""
    m = AgrarMaschine(
        tenant_id=tenant_id,
        **body.model_dump(exclude_none=True),
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return _to_dict(m)


@router.get("/maschinen/{maschine_id}")
def get_maschine(
    maschine_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Maschine Detail."""
    m = db.query(AgrarMaschine).filter(
        AgrarMaschine.id == maschine_id,
        AgrarMaschine.tenant_id == tenant_id,
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="Maschine nicht gefunden")
    return _to_dict(m)


@router.patch("/maschinen/{maschine_id}")
def update_maschine(
    maschine_id: str,
    body: MaschineUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Maschinendaten aktualisieren."""
    m = db.query(AgrarMaschine).filter(
        AgrarMaschine.id == maschine_id,
        AgrarMaschine.tenant_id == tenant_id,
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="Maschine nicht gefunden")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(m, field, value)

    db.commit()
    db.refresh(m)
    return _to_dict(m)


@router.delete("/maschinen/{maschine_id}", response_class=Response)
def delete_maschine(
    maschine_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Maschine deaktivieren (Soft-Delete)."""
    m = db.query(AgrarMaschine).filter(
        AgrarMaschine.id == maschine_id,
        AgrarMaschine.tenant_id == tenant_id,
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="Maschine nicht gefunden")
    m.ist_aktiv = False
    db.commit()
    return Response(status_code=204)


@router.patch("/maschinen/{maschine_id}/stunden")
def buch_betriebsstunden(
    maschine_id: str,
    body: StundenBuchung,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Betriebsstunden hinzubuchen (z.B. nach Einsatz)."""
    m = db.query(AgrarMaschine).filter(
        AgrarMaschine.id == maschine_id,
        AgrarMaschine.tenant_id == tenant_id,
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="Maschine nicht gefunden")

    m.betriebsstunden = float(m.betriebsstunden or 0) + body.stunden
    db.commit()
    db.refresh(m)
    return _to_dict(m)


@router.patch("/maschinen/{maschine_id}/status")
def set_maschine_status(
    maschine_id: str,
    body: StatusWechsel,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Maschinenstatus wechseln."""
    gueltige_status = {"verfuegbar", "im-einsatz", "werkstatt", "stillgelegt"}
    if body.status not in gueltige_status:
        raise HTTPException(status_code=400, detail=f"Ungültiger Status. Erlaubt: {gueltige_status}")

    m = db.query(AgrarMaschine).filter(
        AgrarMaschine.id == maschine_id,
        AgrarMaschine.tenant_id == tenant_id,
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="Maschine nicht gefunden")

    m.status = body.status
    db.commit()
    db.refresh(m)
    return _to_dict(m)
