"""
FastAPI Router für Verkauf
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from app.core.database import get_db
from app.verkauf import models, schemas

router = APIRouter()


@router.get("/kunden", response_model=List[schemas.KundeResponse])
async def list_kunden(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Liste aller Kunden"""
    kunden = db.query(models.Kunde).filter(
        models.Kunde.geloescht == False
    ).offset(skip).limit(limit).all()
    return kunden


@router.get("/kunden/{kunden_nr}", response_model=schemas.KundeResponse)
async def get_kunde(kunden_nr: str, db: Session = Depends(get_db)):
    """Kunde abrufen"""
    kunde = db.query(models.Kunde).filter(
        models.Kunde.kunden_nr == kunden_nr,
        models.Kunde.geloescht == False
    ).first()
    
    if not kunde:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    
    return kunde


@router.get("/kunden/{kunden_nr}/full", response_model=schemas.KundenStammAggregatedResponse)
async def get_kundenstamm_full(kunden_nr: str, db: Session = Depends(get_db)):
    """Kompletten Kundenstamm (alle Tabellen) laden"""
    kunde = (
        db.query(models.Kunde)
        .options(
            selectinload(models.Kunde.profil),
            selectinload(models.Kunde.versand),
            selectinload(models.Kunde.lieferung_zahlung),
            selectinload(models.Kunde.datenschutz),
            selectinload(models.Kunde.genossenschaft),
            selectinload(models.Kunde.freitext),
            selectinload(models.Kunde.allgemein_erweitert),
            selectinload(models.Kunde.ansprechpartner),
            selectinload(models.Kunde.email_verteiler),
            selectinload(models.Kunde.betriebs_gemeinschaften),
            selectinload(models.Kunde.cpd_konten),
            selectinload(models.Kunde.rabatt_details),
            selectinload(models.Kunde.preis_details),
        )
        .filter(
            models.Kunde.kunden_nr == kunden_nr,
            models.Kunde.geloescht == False,
        )
        .first()
    )

    if not kunde:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    return schemas.KundenStammAggregatedResponse(
        kunde=kunde,
        profil=kunde.profil,
        versand=kunde.versand,
        lieferung_zahlung=kunde.lieferung_zahlung,
        datenschutz=kunde.datenschutz,
        genossenschaft=kunde.genossenschaft,
        freitext=kunde.freitext,
        allgemein_erweitert=kunde.allgemein_erweitert,
        ansprechpartner=list(kunde.ansprechpartner),
        email_verteiler=list(kunde.email_verteiler),
        betriebs_gemeinschaften=list(kunde.betriebs_gemeinschaften),
        cpd_konten=list(kunde.cpd_konten),
        rabatte_detail=list(kunde.rabatt_details),
        preise_detail=list(kunde.preis_details),
    )


@router.post("/kunden", response_model=schemas.KundeResponse)
async def create_kunde(kunde_data: schemas.KundeCreate, db: Session = Depends(get_db)):
    """Neuen Kunden erstellen"""
    # Prüfe ob Kunde bereits existiert
    existing = db.query(models.Kunde).filter(
        models.Kunde.kunden_nr == kunde_data.kunden_nr
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Kunde existiert bereits")
    
    # Erstelle neuen Kunden
    kunde = models.Kunde(**kunde_data.model_dump())
    db.add(kunde)
    db.commit()
    db.refresh(kunde)
    
    return kunde


@router.put("/kunden/{kunden_nr}", response_model=schemas.KundeResponse)
async def update_kunde(
    kunden_nr: str,
    kunde_data: schemas.KundeUpdate,
    db: Session = Depends(get_db)
):
    """Kunde aktualisieren"""
    kunde = db.query(models.Kunde).filter(
        models.Kunde.kunden_nr == kunden_nr,
        models.Kunde.geloescht == False
    ).first()
    
    if not kunde:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    
    # Update Felder
    for field, value in kunde_data.model_dump(exclude_unset=True).items():
        setattr(kunde, field, value)
    
    db.commit()
    db.refresh(kunde)
    
    return kunde


@router.delete("/kunden/{kunden_nr}")
async def delete_kunde(kunden_nr: str, db: Session = Depends(get_db)):
    """Kunde löschen (Soft Delete)"""
    kunde = db.query(models.Kunde).filter(
        models.Kunde.kunden_nr == kunden_nr,
        models.Kunde.geloescht == False
    ).first()
    
    if not kunde:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    
    kunde.geloescht = True
    db.commit()
    
    return {"message": "Kunde gelöscht"}


# Untertabellen-Routes

@router.get("/kunden/{kunden_nr}/ansprechpartner", response_model=List[schemas.KundenAnsprechpartnerResponse])
async def list_ansprechpartner(kunden_nr: str, db: Session = Depends(get_db)):
    """Liste aller Ansprechpartner für einen Kunden"""
    ansprechpartner = db.query(models.KundenAnsprechpartner).filter(
        models.KundenAnsprechpartner.kunden_nr == kunden_nr
    ).all()
    return ansprechpartner


@router.post("/kunden/{kunden_nr}/ansprechpartner", response_model=schemas.KundenAnsprechpartnerResponse)
async def create_ansprechpartner(
    kunden_nr: str,
    ansprechpartner_data: schemas.KundenAnsprechpartnerCreate,
    db: Session = Depends(get_db)
):
    """Neuen Ansprechpartner erstellen"""
    ansprechpartner = models.KundenAnsprechpartner(
        kunden_nr=kunden_nr,
        **ansprechpartner_data.model_dump(exclude={'kunden_nr'})
    )
    db.add(ansprechpartner)
    db.commit()
    db.refresh(ansprechpartner)
    
    return ansprechpartner


@router.get("/kunden/{kunden_nr}/profil", response_model=schemas.KundenProfilResponse)
async def get_profil(kunden_nr: str, db: Session = Depends(get_db)):
    """Kundenprofil abrufen"""
    profil = db.query(models.KundenProfil).filter(
        models.KundenProfil.kunden_nr == kunden_nr
    ).first()
    
    if not profil:
        raise HTTPException(status_code=404, detail="Profil nicht gefunden")
    
    return profil


@router.post("/kunden/{kunden_nr}/profil", response_model=schemas.KundenProfilResponse)
async def create_profil(
    kunden_nr: str,
    profil_data: schemas.KundenProfilCreate,
    db: Session = Depends(get_db)
):
    """Kundenprofil erstellen"""
    profil = models.KundenProfil(
        kunden_nr=kunden_nr,
        **profil_data.model_dump(exclude={'kunden_nr'})
    )
    db.add(profil)
    db.commit()
    db.refresh(profil)
    
    return profil

