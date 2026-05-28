"""
Produktion – Mischfutter: Verfuegbarkeit, Rezepte & Produktionsauftraege

Liest Komponentenbestaende aus futtermittel_einzelfutter,
Rezepturen aus futtermittel_rezepte und persistiert Produktionsauftraege
in futtermittel_produktionsauftraege mit echtem Bestandsabzug.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.infrastructure.models.futtermittel_models import (
    Einzelfuttermittel,
    FuttermittelRezept,
    ProduktionsAuftrag,
)


from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/produktion/mischfutter", tags=["Produktion - Mischfutter"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class KomponenteVerfuegbarkeit(BaseModel):
    id: str
    name: str
    verfuegbar_t: float
    einheit: str = "t"
    min_bestand_t: Optional[float] = None
    unter_minimum: bool = False


class RezeptKomponenteOut(BaseModel):
    komponente_name: str
    anteil: float
    einzelfutter_id: Optional[str] = None


class RezeptOut(BaseModel):
    id: str
    name: str
    rezept_code: str
    tierart: str
    protein_ziel: Optional[float] = None
    energie_ziel: Optional[float] = None
    komponenten: list[RezeptKomponenteOut] = []


class ProduktionsauftragIn(BaseModel):
    rezept_id: str = Field(..., min_length=1)
    menge_t: float = Field(..., gt=0)
    chargen_id: str = ""
    bemerkung: str = ""


class ProduktionsauftragOut(BaseModel):
    id: str
    chargen_id: str
    rezept_id: Optional[str]
    rezept_name: str
    menge_t: float
    status: str
    bestands_abzug_erfolgt: bool
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProduktionsauftragStatusIn(BaseModel):
    status: str = Field(..., pattern="^(freigegeben|in_produktion|fertig|storniert)$")
    freigegeben_von: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/verfuegbarkeit", response_model=list[KomponenteVerfuegbarkeit], summary="Verfuegbarkeit abrufen")
async def get_verfuegbarkeit(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Aktuelle Komponentenverfuegbarkeit aus Einzelfuttermittel-Bestaenden."""
    try:
        items = db.query(Einzelfuttermittel).filter(
            and_(Einzelfuttermittel.tenant_id == tenant_id, Einzelfuttermittel.aktiv.is_(True))
        ).order_by(Einzelfuttermittel.name).all()
    except Exception:
        db.rollback()
        return []

    return [
        KomponenteVerfuegbarkeit(
            id=item.id,
            name=item.name,
            verfuegbar_t=float(item.verfuegbar_t or 0),
            einheit=item.einheit or "t",
            min_bestand_t=float(item.min_bestand_t) if item.min_bestand_t else None,
            unter_minimum=(
                item.min_bestand_t is not None
                and item.verfuegbar_t is not None
                and item.verfuegbar_t < item.min_bestand_t
            ),
        )
        for item in items
    ]


@router.get("/rezepte", response_model=list[RezeptOut], summary="Rezepte abrufen")
async def get_rezepte(
    tierart: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste aller aktiven Mischfutter-Rezepturen mit Komponentenanteilen."""
    try:
        q = db.query(FuttermittelRezept).options(
            joinedload(FuttermittelRezept.komponenten)
        ).filter(
            and_(FuttermittelRezept.tenant_id == tenant_id, FuttermittelRezept.aktiv.is_(True))
        )
        if tierart:
            q = q.filter(FuttermittelRezept.tierart == tierart)
        rezepte = q.order_by(FuttermittelRezept.name).all()
    except Exception:
        db.rollback()
        return []
    return [
        RezeptOut(
            id=r.id,
            name=r.name,
            rezept_code=r.rezept_code,
            tierart=r.tierart,
            protein_ziel=float(r.protein_ziel) if r.protein_ziel else None,
            energie_ziel=float(r.energie_ziel) if r.energie_ziel else None,
            komponenten=[
                RezeptKomponenteOut(
                    komponente_name=k.komponente_name,
                    anteil=float(k.anteil),
                    einzelfutter_id=k.einzelfutter_id,
                )
                for k in sorted(r.komponenten, key=lambda x: x.sortierung)
            ],
        )
        for r in rezepte
    ]


@router.post("/auftrag", response_model=ProduktionsauftragOut, status_code=201, summary="Produktionsauftrag anlegen")
async def create_produktionsauftrag(
    payload: ProduktionsauftragIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Mischfutter-Produktionsauftrag erstellen und Bestand reservieren."""
    # Validate recipe exists
    try:
        rezept = db.query(FuttermittelRezept).options(
            joinedload(FuttermittelRezept.komponenten)
        ).filter(
            and_(FuttermittelRezept.id == payload.rezept_id, FuttermittelRezept.tenant_id == tenant_id)
        ).first()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=404, detail=f"Rezept '{payload.rezept_id}' nicht gefunden")
    if not rezept:
        raise HTTPException(status_code=404, detail=f"Rezept '{payload.rezept_id}' nicht gefunden")

    # Check component availability
    menge = Decimal(str(payload.menge_t))
    fehlend = []
    for komp in rezept.komponenten:
        benoetigte_menge = menge * komp.anteil
        if komp.einzelfutter_id:
            ef = db.query(Einzelfuttermittel).filter(
                and_(Einzelfuttermittel.id == komp.einzelfutter_id, Einzelfuttermittel.tenant_id == tenant_id)
            ).first()
            if ef and (ef.verfuegbar_t or 0) < benoetigte_menge:
                fehlend.append(f"{komp.komponente_name}: benötigt {float(benoetigte_menge):.2f}t, verfügbar {float(ef.verfuegbar_t or 0):.2f}t")

    if fehlend:
        raise HTTPException(
            status_code=409,
            detail={"message": "Unzureichende Komponentenbestände", "fehlend": fehlend},
        )

    chargen_id = payload.chargen_id or f"MF-{datetime.now().strftime('%y%m%d')}-{uuid7()[:6].upper()}"

    auftrag = ProduktionsAuftrag(
        id=uuid7(),
        tenant_id=tenant_id,
        chargen_id=chargen_id,
        rezept_id=rezept.id,
        rezept_name=rezept.name,
        menge_t=menge,
        status="erstellt",
        bemerkung=payload.bemerkung or None,
    )
    db.add(auftrag)
    db.commit()
    db.refresh(auftrag)

    return ProduktionsauftragOut(
        id=auftrag.id,
        chargen_id=auftrag.chargen_id,
        rezept_id=auftrag.rezept_id,
        rezept_name=auftrag.rezept_name,
        menge_t=float(auftrag.menge_t),
        status=auftrag.status,
        bestands_abzug_erfolgt=auftrag.bestands_abzug_erfolgt,
        created_at=auftrag.created_at.isoformat() if auftrag.created_at else None,
    )


@router.patch("/auftrag/{auftrag_id}/status", response_model=ProduktionsauftragOut, summary="Auftrag status aktualisieren")
async def update_auftrag_status(
    auftrag_id: str,
    payload: ProduktionsauftragStatusIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Produktionsauftrag-Status ändern. Bei 'freigegeben' wird Bestand abgezogen."""
    auftrag = db.query(ProduktionsAuftrag).filter(
        and_(ProduktionsAuftrag.id == auftrag_id, ProduktionsAuftrag.tenant_id == tenant_id)
    ).first()
    if not auftrag:
        raise HTTPException(status_code=404, detail=f"Auftrag '{auftrag_id}' nicht gefunden")

    # Validate state transition
    valid_transitions = {
        "erstellt": ["freigegeben", "storniert"],
        "freigegeben": ["in_produktion", "storniert"],
        "in_produktion": ["fertig", "storniert"],
    }
    if payload.status not in valid_transitions.get(auftrag.status, []):
        raise HTTPException(
            status_code=409,
            detail=f"Ungültiger Statusübergang: {auftrag.status} → {payload.status}",
        )

    # Deduct inventory on 'freigegeben'
    if payload.status == "freigegeben" and not auftrag.bestands_abzug_erfolgt and auftrag.rezept_id:
        rezept = db.query(FuttermittelRezept).options(
            joinedload(FuttermittelRezept.komponenten)
        ).filter(FuttermittelRezept.id == auftrag.rezept_id).first()
        if rezept:
            menge = auftrag.menge_t
            for komp in rezept.komponenten:
                if komp.einzelfutter_id:
                    ef = db.query(Einzelfuttermittel).filter(
                        Einzelfuttermittel.id == komp.einzelfutter_id
                    ).with_for_update().first()
                    if ef:
                        ef.verfuegbar_t = (ef.verfuegbar_t or 0) - (menge * komp.anteil)
            auftrag.bestands_abzug_erfolgt = True
        auftrag.freigegeben_von = payload.freigegeben_von
        auftrag.freigegeben_am = datetime.now()

    # Return inventory on 'storniert' if already deducted
    if payload.status == "storniert" and auftrag.bestands_abzug_erfolgt and auftrag.rezept_id:
        rezept = db.query(FuttermittelRezept).options(
            joinedload(FuttermittelRezept.komponenten)
        ).filter(FuttermittelRezept.id == auftrag.rezept_id).first()
        if rezept:
            menge = auftrag.menge_t
            for komp in rezept.komponenten:
                if komp.einzelfutter_id:
                    ef = db.query(Einzelfuttermittel).filter(
                        Einzelfuttermittel.id == komp.einzelfutter_id
                    ).with_for_update().first()
                    if ef:
                        ef.verfuegbar_t = (ef.verfuegbar_t or 0) + (menge * komp.anteil)
            auftrag.bestands_abzug_erfolgt = False

    if payload.status == "fertig":
        auftrag.fertig_am = datetime.now()

    auftrag.status = payload.status
    db.commit()
    db.refresh(auftrag)

    return ProduktionsauftragOut(
        id=auftrag.id,
        chargen_id=auftrag.chargen_id,
        rezept_id=auftrag.rezept_id,
        rezept_name=auftrag.rezept_name,
        menge_t=float(auftrag.menge_t),
        status=auftrag.status,
        bestands_abzug_erfolgt=auftrag.bestands_abzug_erfolgt,
        created_at=auftrag.created_at.isoformat() if auftrag.created_at else None,
    )


@router.get("/auftraege", response_model=list[ProduktionsauftragOut], summary="Auftraege auflisten")
async def list_auftraege(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Alle Produktionsauftraege auflisten."""
    q = db.query(ProduktionsAuftrag).filter(ProduktionsAuftrag.tenant_id == tenant_id)
    if status:
        q = q.filter(ProduktionsAuftrag.status == status)
    auftraege = q.order_by(ProduktionsAuftrag.created_at.desc()).all()
    return [
        ProduktionsauftragOut(
            id=a.id,
            chargen_id=a.chargen_id,
            rezept_id=a.rezept_id,
            rezept_name=a.rezept_name,
            menge_t=float(a.menge_t),
            status=a.status,
            bestands_abzug_erfolgt=a.bestands_abzug_erfolgt,
            created_at=a.created_at.isoformat() if a.created_at else None,
        )
        for a in auftraege
    ]
