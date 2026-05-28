"""
Futtermittel-Stammdaten & Rezepte API

Vollstaendiges CRUD fuer Einzelfuttermittel, Mischfuttermittel und Rezepte.
Persistenz ueber SQLAlchemy-Modelle in domain_shared.
"""

from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.infrastructure.models.futtermittel_models import (
    Einzelfuttermittel,
    Mischfuttermittel,
    FuttermittelRezept,
    RezeptKomponente,
)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(tags=["futter", "stammdaten"])


# ── Schemas ─────────────────────────────────────────────────────

class EinzelfuttermittelIn(BaseModel):
    artikel_nummer: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    art: str = Field(..., min_length=1, max_length=100)
    herkunft: Optional[str] = None
    lieferant: Optional[str] = None
    protein: Optional[float] = None
    energie: Optional[float] = None
    faser: Optional[float] = None
    fett: Optional[float] = None
    asche: Optional[float] = None
    trockensubstanz: Optional[float] = None
    gvo_status: Optional[str] = None
    qs_milch: bool = False
    gmp_plus: bool = False
    bio_zertifiziert: bool = False
    verfuegbar_t: float = 0
    einheit: str = "t"
    min_bestand_t: Optional[float] = None
    preis_pro_t: Optional[float] = None


class EinzelfuttermittelOut(EinzelfuttermittelIn):
    id: str
    aktiv: bool = True

    model_config = ConfigDict(from_attributes=True)


class MischfuttermittelIn(BaseModel):
    produkt_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    tierart: str = Field(..., min_length=1, max_length=100)
    leistungsstufe: Optional[str] = None
    protein: Optional[float] = None
    energie: Optional[float] = None
    beschreibung: Optional[str] = None


class MischfuttermittelOut(MischfuttermittelIn):
    id: str
    aktiv: bool = True

    model_config = ConfigDict(from_attributes=True)


class RezeptKomponenteIn(BaseModel):
    einzelfutter_id: Optional[str] = None
    komponente_name: str = Field(..., min_length=1)
    anteil: float = Field(..., gt=0, le=1)
    min_anteil: Optional[float] = None
    max_anteil: Optional[float] = None
    sortierung: int = 0


class RezeptKomponenteOut(RezeptKomponenteIn):
    id: str

    model_config = ConfigDict(from_attributes=True)


class RezeptIn(BaseModel):
    rezept_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    tierart: str = Field(..., min_length=1, max_length=100)
    mischfutter_id: Optional[str] = None
    protein_ziel: Optional[float] = None
    energie_ziel: Optional[float] = None
    bemerkung: Optional[str] = None
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None
    komponenten: list[RezeptKomponenteIn] = []


class RezeptOut(BaseModel):
    id: str
    rezept_code: str
    name: str
    tierart: str
    mischfutter_id: Optional[str] = None
    version: int = 1
    protein_ziel: Optional[float] = None
    energie_ziel: Optional[float] = None
    bemerkung: Optional[str] = None
    aktiv: bool = True
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None
    komponenten: list[RezeptKomponenteOut] = []

    model_config = ConfigDict(from_attributes=True)


# ── Einzelfuttermittel CRUD ────────────────────────────────────

@router.get("/einzelfuttermittel", response_model=list[EinzelfuttermittelOut],
            summary="Alle Einzelfuttermittel auflisten")
async def list_einzelfuttermittel(
    art: Optional[str] = Query(None, description="Filtern nach Art"),
    aktiv: bool = Query(True, description="Nur aktive"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(Einzelfuttermittel).filter(Einzelfuttermittel.tenant_id == tenant_id)
        if aktiv:
            q = q.filter(Einzelfuttermittel.aktiv.is_(True))
        if art:
            q = q.filter(Einzelfuttermittel.art == art)
        return q.order_by(Einzelfuttermittel.name).all()
    except Exception:
        db.rollback()
        return []


@router.get("/einzelfuttermittel/{futter_id}", response_model=EinzelfuttermittelOut,
            summary="Einzelfuttermittel-Stammdaten abrufen")
async def get_einzelfuttermittel(
    futter_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = db.query(Einzelfuttermittel).filter(
        and_(Einzelfuttermittel.id == futter_id, Einzelfuttermittel.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Einzelfuttermittel '{futter_id}' nicht gefunden")
    return item


@router.post("/einzelfuttermittel", response_model=EinzelfuttermittelOut, status_code=201,
             summary="Einzelfuttermittel anlegen")
async def create_einzelfuttermittel(
    payload: EinzelfuttermittelIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = Einzelfuttermittel(id=uuid7(), tenant_id=tenant_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/einzelfuttermittel/{futter_id}", response_model=EinzelfuttermittelOut,
            summary="Einzelfuttermittel aktualisieren")
async def update_einzelfuttermittel(
    futter_id: str,
    payload: EinzelfuttermittelIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = db.query(Einzelfuttermittel).filter(
        and_(Einzelfuttermittel.id == futter_id, Einzelfuttermittel.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Einzelfuttermittel '{futter_id}' nicht gefunden")
    for k, v in payload.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/einzelfuttermittel/{futter_id}", status_code=204,
               summary="Einzelfuttermittel deaktivieren", response_class=Response, response_model=None)
async def delete_einzelfuttermittel(
    futter_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = db.query(Einzelfuttermittel).filter(
        and_(Einzelfuttermittel.id == futter_id, Einzelfuttermittel.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Einzelfuttermittel '{futter_id}' nicht gefunden")
    item.aktiv = False
    db.commit()
    return Response(status_code=204)


# ── Mischfuttermittel CRUD ─────────────────────────────────────

@router.get("/mischfuttermittel", response_model=list[MischfuttermittelOut],
            summary="Alle Mischfuttermittel auflisten")
async def list_mischfuttermittel(
    tierart: Optional[str] = Query(None),
    aktiv: bool = Query(True),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(Mischfuttermittel).filter(Mischfuttermittel.tenant_id == tenant_id)
        if aktiv:
            q = q.filter(Mischfuttermittel.aktiv.is_(True))
        if tierart:
            q = q.filter(Mischfuttermittel.tierart == tierart)
        return q.order_by(Mischfuttermittel.name).all()
    except Exception:
        db.rollback()
        return []


@router.get("/mischfuttermittel/{misch_id}", response_model=MischfuttermittelOut,
            summary="Mischfuttermittel-Stammdaten abrufen")
async def get_mischfuttermittel(
    misch_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = db.query(Mischfuttermittel).filter(
        and_(Mischfuttermittel.id == misch_id, Mischfuttermittel.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Mischfuttermittel '{misch_id}' nicht gefunden")
    return item


@router.post("/mischfuttermittel", response_model=MischfuttermittelOut, status_code=201,
             summary="Mischfuttermittel anlegen")
async def create_mischfuttermittel(
    payload: MischfuttermittelIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = Mischfuttermittel(id=uuid7(), tenant_id=tenant_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/mischfuttermittel/{misch_id}", response_model=MischfuttermittelOut,
            summary="Mischfuttermittel aktualisieren")
async def update_mischfuttermittel(
    misch_id: str,
    payload: MischfuttermittelIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = db.query(Mischfuttermittel).filter(
        and_(Mischfuttermittel.id == misch_id, Mischfuttermittel.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Mischfuttermittel '{misch_id}' nicht gefunden")
    for k, v in payload.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/mischfuttermittel/{misch_id}", status_code=204,
               summary="Mischfuttermittel deaktivieren", response_class=Response, response_model=None)
async def delete_mischfuttermittel(
    misch_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = db.query(Mischfuttermittel).filter(
        and_(Mischfuttermittel.id == misch_id, Mischfuttermittel.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Mischfuttermittel '{misch_id}' nicht gefunden")
    item.aktiv = False
    db.commit()
    return Response(status_code=204)


# ── Rezepte CRUD ───────────────────────────────────────────────

@router.get("/rezepte", response_model=list[RezeptOut],
            summary="Alle Rezepte auflisten")
async def list_rezepte(
    tierart: Optional[str] = Query(None),
    aktiv: bool = Query(True),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(FuttermittelRezept).options(
            joinedload(FuttermittelRezept.komponenten)
        ).filter(FuttermittelRezept.tenant_id == tenant_id)
        if aktiv:
            q = q.filter(FuttermittelRezept.aktiv.is_(True))
        if tierart:
            q = q.filter(FuttermittelRezept.tierart == tierart)
        return q.order_by(FuttermittelRezept.name).all()
    except Exception:
        db.rollback()
        return []


@router.get("/rezepte/{rezept_id}", response_model=RezeptOut,
            summary="Rezept-Stammdaten abrufen")
async def get_rezept(
    rezept_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = db.query(FuttermittelRezept).options(
        joinedload(FuttermittelRezept.komponenten)
    ).filter(
        and_(FuttermittelRezept.id == rezept_id, FuttermittelRezept.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Rezept '{rezept_id}' nicht gefunden")
    return item


@router.post("/rezepte", response_model=RezeptOut, status_code=201,
             summary="Rezept anlegen")
async def create_rezept(
    payload: RezeptIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rezept = FuttermittelRezept(
        id=uuid7(),
        tenant_id=tenant_id,
        rezept_code=payload.rezept_code,
        name=payload.name,
        tierart=payload.tierart,
        mischfutter_id=payload.mischfutter_id,
        protein_ziel=payload.protein_ziel,
        energie_ziel=payload.energie_ziel,
        bemerkung=payload.bemerkung,
        gueltig_ab=payload.gueltig_ab,
        gueltig_bis=payload.gueltig_bis,
    )
    for komp in payload.komponenten:
        rezept.komponenten.append(RezeptKomponente(
            id=uuid7(),
            komponente_name=komp.komponente_name,
            einzelfutter_id=komp.einzelfutter_id,
            anteil=komp.anteil,
            min_anteil=komp.min_anteil,
            max_anteil=komp.max_anteil,
            sortierung=komp.sortierung,
        ))
    db.add(rezept)
    db.commit()
    db.refresh(rezept)
    return rezept


@router.put("/rezepte/{rezept_id}", response_model=RezeptOut,
            summary="Rezept aktualisieren (inkl. Komponenten)")
async def update_rezept(
    rezept_id: str,
    payload: RezeptIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rezept = db.query(FuttermittelRezept).options(
        joinedload(FuttermittelRezept.komponenten)
    ).filter(
        and_(FuttermittelRezept.id == rezept_id, FuttermittelRezept.tenant_id == tenant_id)
    ).first()
    if not rezept:
        raise HTTPException(status_code=404, detail=f"Rezept '{rezept_id}' nicht gefunden")

    rezept.rezept_code = payload.rezept_code
    rezept.name = payload.name
    rezept.tierart = payload.tierart
    rezept.mischfutter_id = payload.mischfutter_id
    rezept.protein_ziel = payload.protein_ziel
    rezept.energie_ziel = payload.energie_ziel
    rezept.bemerkung = payload.bemerkung
    rezept.gueltig_ab = payload.gueltig_ab
    rezept.gueltig_bis = payload.gueltig_bis
    rezept.version = (rezept.version or 1) + 1

    # Replace components
    for old in rezept.komponenten:
        db.delete(old)
    db.flush()
    for komp in payload.komponenten:
        rezept.komponenten.append(RezeptKomponente(
            id=uuid7(),
            komponente_name=komp.komponente_name,
            einzelfutter_id=komp.einzelfutter_id,
            anteil=komp.anteil,
            min_anteil=komp.min_anteil,
            max_anteil=komp.max_anteil,
            sortierung=komp.sortierung,
        ))
    db.commit()
    db.refresh(rezept)
    return rezept


@router.delete("/rezepte/{rezept_id}", status_code=204,
               summary="Rezept deaktivieren", response_class=Response, response_model=None)
async def delete_rezept(
    rezept_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = db.query(FuttermittelRezept).filter(
        and_(FuttermittelRezept.id == rezept_id, FuttermittelRezept.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Rezept '{rezept_id}' nicht gefunden")
    item.aktiv = False
    db.commit()
    return Response(status_code=204)
