"""
VALEO-NeuroERP - Einkauf Router
REST API Endpoints für Einkauf/Beschaffung
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from app.core.database_pg import get_db
from app.einkauf import schemas

router = APIRouter(prefix="/einkauf", tags=["Einkauf"])


# ============================================================================
# LIEFERANTEN
# ============================================================================

@router.get("/lieferanten", response_model=dict)
async def get_lieferanten(
    aktiv: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Holt Lieferantenliste"""
    try:
        query = "SELECT * FROM einkauf_lieferanten"
        params = {"limit": limit, "skip": skip}
        
        if aktiv is not None:
            query += " WHERE aktiv = :aktiv"
            params["aktiv"] = aktiv
        
        query += " ORDER BY firmenname LIMIT :limit OFFSET :skip"
        
        result = db.execute(text(query), params)
        lieferanten = [dict(row) for row in result]
        
        return {
            "total": len(lieferanten),
            "items": lieferanten
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.get("/lieferanten/{lieferant_id}")
async def get_lieferant(lieferant_id: int, db: Session = Depends(get_db)):
    """Holt einzelnen Lieferanten"""
    try:
        query = "SELECT * FROM einkauf_lieferanten WHERE id = :id"
        result = db.execute(text(query), {"id": lieferant_id})
        lieferant = result.fetchone()
        
        if not lieferant:
            raise HTTPException(status_code=404, detail="Lieferant nicht gefunden")
        
        return dict(lieferant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.post("/lieferanten", status_code=201)
async def create_lieferant(
    lieferant: schemas.LieferantCreate,
    db: Session = Depends(get_db)
):
    """Erstellt neuen Lieferanten"""
    try:
        # Prüfe ob Lieferantennummer bereits existiert
        check_query = "SELECT id FROM einkauf_lieferanten WHERE lieferantennummer = :nummer"
        existing = db.execute(text(check_query), {"nummer": lieferant.lieferantennummer}).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Lieferantennummer {lieferant.lieferantennummer} existiert bereits"
            )
        
        # Neuen Lieferanten einfügen
        insert_query = """
            INSERT INTO einkauf_lieferanten (
                lieferantennummer, firmenname, ansprechpartner, email, telefon,
                strasse, plz, ort, land, zahlungsbedingungen, lieferzeit_tage,
                bewertung, aktiv
            ) VALUES (
                :lieferantennummer, :firmenname, :ansprechpartner, :email, :telefon,
                :strasse, :plz, :ort, :land, :zahlungsbedingungen, :lieferzeit_tage,
                :bewertung, :aktiv
            ) RETURNING id
        """
        
        result = db.execute(text(insert_query), lieferant.dict())
        lieferant_id = result.fetchone()[0]
        db.commit()
        
        return {"id": lieferant_id, "message": "Lieferant erfolgreich erstellt"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen: {str(e)}")


@router.put("/lieferanten/{lieferant_id}")
async def update_lieferant(
    lieferant_id: int,
    lieferant: schemas.LieferantUpdate,
    db: Session = Depends(get_db)
):
    """Aktualisiert Lieferanten"""
    try:
        # Prüfe ob Lieferant existiert
        check_query = "SELECT id FROM einkauf_lieferanten WHERE id = :id"
        existing = db.execute(text(check_query), {"id": lieferant_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Lieferant nicht gefunden")
        
        # Nur gesetzte Felder aktualisieren
        update_data = {k: v for k, v in lieferant.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Keine Daten zum Aktualisieren")
        
        # UPDATE Query bauen
        set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
        update_query = f"UPDATE einkauf_lieferanten SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = :id"
        
        update_data["id"] = lieferant_id
        db.execute(text(update_query), update_data)
        db.commit()
        
        return {"message": "Lieferant erfolgreich aktualisiert"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren: {str(e)}")


@router.delete("/lieferanten/{lieferant_id}")
async def delete_lieferant(lieferant_id: int, db: Session = Depends(get_db)):
    """Löscht Lieferanten"""
    try:
        # Prüfe ob Lieferant existiert
        check_query = "SELECT id FROM einkauf_lieferanten WHERE id = :id"
        existing = db.execute(text(check_query), {"id": lieferant_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Lieferant nicht gefunden")
        
        # Lösche Lieferanten
        delete_query = "DELETE FROM einkauf_lieferanten WHERE id = :id"
        db.execute(text(delete_query), {"id": lieferant_id})
        db.commit()
        
        return {"message": "Lieferant erfolgreich gelöscht"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen: {str(e)}")


# ============================================================================
# BESTELLUNGEN
# ============================================================================

@router.get("/bestellungen", response_model=dict)
async def get_bestellungen(
    status: Optional[str] = None,
    lieferant_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Holt Bestellungsliste"""
    try:
        query = "SELECT * FROM einkauf_bestellungen"
        params = {"limit": limit, "skip": skip}
        conditions = []
        
        if status:
            conditions.append("status = :status")
            params["status"] = status
        
        if lieferant_id:
            conditions.append("lieferant_id = :lieferant_id")
            params["lieferant_id"] = lieferant_id
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY bestelldatum DESC LIMIT :limit OFFSET :skip"
        
        result = db.execute(text(query), params)
        bestellungen = [dict(row) for row in result]
        
        return {
            "total": len(bestellungen),
            "items": bestellungen
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.get("/bestellungen/{bestellung_id}")
async def get_bestellung(bestellung_id: int, db: Session = Depends(get_db)):
    """Holt einzelne Bestellung"""
    try:
        query = "SELECT * FROM einkauf_bestellungen WHERE id = :id"
        result = db.execute(text(query), {"id": bestellung_id})
        bestellung = result.fetchone()
        
        if not bestellung:
            raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
        
        return dict(bestellung)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.post("/bestellungen", status_code=201)
async def create_bestellung(
    bestellung: schemas.BestellungCreate,
    db: Session = Depends(get_db)
):
    """Erstellt neue Bestellung"""
    try:
        # Prüfe ob Bestellnummer bereits existiert
        check_query = "SELECT id FROM einkauf_bestellungen WHERE bestellnummer = :nummer"
        existing = db.execute(text(check_query), {"nummer": bestellung.bestellnummer}).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Bestellnummer {bestellung.bestellnummer} existiert bereits"
            )
        
        # Neue Bestellung einfügen
        insert_query = """
            INSERT INTO einkauf_bestellungen (
                bestellnummer, lieferant_id, bestelldatum, gewuenschtes_lieferdatum,
                status, netto_summe, mwst_betrag, brutto_summe, erstellt_von
            ) VALUES (
                :bestellnummer, :lieferant_id, :bestelldatum, :gewuenschtes_lieferdatum,
                :status, :netto_summe, :mwst_betrag, :brutto_summe, :erstellt_von
            ) RETURNING id
        """
        
        result = db.execute(text(insert_query), bestellung.dict())
        bestellung_id = result.fetchone()[0]
        db.commit()
        
        return {"id": bestellung_id, "message": "Bestellung erfolgreich erstellt"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen: {str(e)}")


@router.put("/bestellungen/{bestellung_id}")
async def update_bestellung(
    bestellung_id: int,
    bestellung: schemas.BestellungUpdate,
    db: Session = Depends(get_db)
):
    """Aktualisiert Bestellung"""
    try:
        # Prüfe ob Bestellung existiert
        check_query = "SELECT id FROM einkauf_bestellungen WHERE id = :id"
        existing = db.execute(check_query, {"id": bestellung_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
        
        # Nur gesetzte Felder aktualisieren
        update_data = {k: v for k, v in bestellung.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Keine Daten zum Aktualisieren")
        
        # UPDATE Query bauen
        set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
        update_query = f"UPDATE einkauf_bestellungen SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = :id"
        
        update_data["id"] = bestellung_id
        db.execute(text(update_query), update_data)
        db.commit()
        
        return {"message": "Bestellung erfolgreich aktualisiert"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren: {str(e)}")


@router.delete("/bestellungen/{bestellung_id}")
async def delete_bestellung(bestellung_id: int, db: Session = Depends(get_db)):
    """Löscht Bestellung"""
    try:
        # Prüfe ob Bestellung existiert
        check_query = "SELECT id FROM einkauf_bestellungen WHERE id = :id"
        existing = db.execute(check_query, {"id": bestellung_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
        
        # Lösche Bestellung
        delete_query = "DELETE FROM einkauf_bestellungen WHERE id = :id"
        db.execute(text(delete_query), {"id": bestellung_id})
        db.commit()
        
        return {"message": "Bestellung erfolgreich gelöscht"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen: {str(e)}")

