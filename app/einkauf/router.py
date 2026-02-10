"""
VALEO-NeuroERP - Einkauf Router
REST API Endpoints für Einkauf/Beschaffung
"""

import uuid
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from app.core.database_pg import get_db
from app.einkauf import schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/einkauf", tags=["Einkauf"])


***REMOVED*** ============================================================================
***REMOVED*** LIEFERANTEN
***REMOVED*** ============================================================================

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
        ***REMOVED*** Prüfe ob Lieferantennummer bereits existiert
        check_query = "SELECT id FROM einkauf_lieferanten WHERE lieferantennummer = :nummer"
        existing = db.execute(text(check_query), {"nummer": lieferant.lieferantennummer}).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Lieferantennummer {lieferant.lieferantennummer} existiert bereits"
            )
        
        ***REMOVED*** Neuen Lieferanten einfügen
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
        ***REMOVED*** Prüfe ob Lieferant existiert
        check_query = "SELECT id FROM einkauf_lieferanten WHERE id = :id"
        existing = db.execute(text(check_query), {"id": lieferant_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Lieferant nicht gefunden")
        
        ***REMOVED*** Nur gesetzte Felder aktualisieren
        update_data = {k: v for k, v in lieferant.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Keine Daten zum Aktualisieren")
        
        ***REMOVED*** UPDATE Query bauen
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
        ***REMOVED*** Prüfe ob Lieferant existiert
        check_query = "SELECT id FROM einkauf_lieferanten WHERE id = :id"
        existing = db.execute(text(check_query), {"id": lieferant_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Lieferant nicht gefunden")
        
        ***REMOVED*** Lösche Lieferanten
        delete_query = "DELETE FROM einkauf_lieferanten WHERE id = :id"
        db.execute(text(delete_query), {"id": lieferant_id})
        db.commit()
        
        return {"message": "Lieferant erfolgreich gelöscht"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen: {str(e)}")


***REMOVED*** ============================================================================
***REMOVED*** BESTELLUNGEN
***REMOVED*** ============================================================================

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
        ***REMOVED*** Prüfe ob Bestellnummer bereits existiert
        check_query = "SELECT id FROM einkauf_bestellungen WHERE bestellnummer = :nummer"
        existing = db.execute(text(check_query), {"nummer": bestellung.bestellnummer}).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Bestellnummer {bestellung.bestellnummer} existiert bereits"
            )
        
        ***REMOVED*** Neue Bestellung einfügen
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
        ***REMOVED*** Prüfe ob Bestellung existiert
        check_query = "SELECT id FROM einkauf_bestellungen WHERE id = :id"
        existing = db.execute(text(check_query), {"id": bestellung_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
        
        ***REMOVED*** Nur gesetzte Felder aktualisieren
        update_data = {k: v for k, v in bestellung.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Keine Daten zum Aktualisieren")
        
        ***REMOVED*** UPDATE Query bauen
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
        ***REMOVED*** Prüfe ob Bestellung existiert
        check_query = "SELECT id FROM einkauf_bestellungen WHERE id = :id"
        existing = db.execute(text(check_query), {"id": bestellung_id}).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
        
        ***REMOVED*** Lösche Bestellung
        delete_query = "DELETE FROM einkauf_bestellungen WHERE id = :id"
        db.execute(text(delete_query), {"id": bestellung_id})
        db.commit()
        
        return {"message": "Bestellung erfolgreich gelöscht"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen: {str(e)}")


***REMOVED*** ============================================================================
***REMOVED*** ANFRAGEN / BEDARFSMELDUNGEN (Requisitions) - PROC-REQ-01
***REMOVED*** ============================================================================

@router.get("/anfragen", response_model=dict)
async def get_anfragen(
    status: Optional[str] = None,
    typ: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Holt Anfragen/Bedarfsmeldungen"""
    try:
        query = "SELECT * FROM einkauf_anfragen"
        params: dict = {"limit": limit, "skip": skip}
        conditions = []

        if status:
            conditions.append("status = :status")
            params["status"] = status
        if typ:
            conditions.append("typ = :typ")
            params["typ"] = typ

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"

        result = db.execute(text(query), params)
        anfragen = [dict(row._mapping) for row in result]

        return {"total": len(anfragen), "items": anfragen}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.get("/anfragen/{anfrage_id}")
async def get_anfrage(anfrage_id: str, db: Session = Depends(get_db)):
    """Holt einzelne Anfrage"""
    try:
        row = db.execute(
            text("SELECT * FROM einkauf_anfragen WHERE id = :id OR anfrage_nummer = :id"),
            {"id": anfrage_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        anfrage = dict(row._mapping)

        ***REMOVED*** Positionen laden
        pos_rows = db.execute(
            text("SELECT * FROM einkauf_anfragen_positionen WHERE anfrage_id = :id"),
            {"id": anfrage["id"]},
        ).fetchall()
        anfrage["positionen"] = [dict(p._mapping) for p in pos_rows]

        return anfrage
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.post("/anfragen", status_code=201)
async def create_anfrage(
    anfrage: schemas.AnfrageCreate,
    db: Session = Depends(get_db)
):
    """Erstellt neue Anfrage/Bedarfsmeldung"""
    try:
        anfrage_id = str(uuid.uuid4())
        anfrage_nummer = anfrage.anfrageNummer or f"BANF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        db.execute(
            text("""
                INSERT INTO einkauf_anfragen (
                    id, anfrage_nummer, typ, anforderer, abteilung, datum,
                    prioritaet, status, begruendung, kostenstelle, projekt_id,
                    artikel, menge, einheit, budget, notizen
                ) VALUES (
                    :id, :nummer, :typ, :anforderer, :abteilung, :datum,
                    :prioritaet, :status, :begruendung, :kostenstelle, :projekt_id,
                    :artikel, :menge, :einheit, :budget, :notizen
                )
            """),
            {
                "id": anfrage_id,
                "nummer": anfrage_nummer,
                "typ": anfrage.typ,
                "anforderer": anfrage.anforderer,
                "abteilung": anfrage.abteilung,
                "datum": anfrage.datum,
                "prioritaet": anfrage.prioritaet,
                "status": anfrage.status,
                "begruendung": anfrage.begruendung,
                "kostenstelle": anfrage.kostenstelle,
                "projekt_id": anfrage.projekt_id,
                "artikel": anfrage.artikel,
                "menge": anfrage.menge,
                "einheit": anfrage.einheit,
                "budget": anfrage.budget,
                "notizen": anfrage.notizen,
            },
        )

        ***REMOVED*** Positionen anlegen
        if anfrage.positionen:
            for pos in anfrage.positionen:
                pos_id = str(uuid.uuid4())
                db.execute(
                    text("""
                        INSERT INTO einkauf_anfragen_positionen (
                            id, anfrage_id, article_id, artikel, quantity, unit, due_date, notes
                        ) VALUES (
                            :id, :anfrage_id, :article_id, :artikel, :qty, :unit, :due_date, :notes
                        )
                    """),
                    {
                        "id": pos_id,
                        "anfrage_id": anfrage_id,
                        "article_id": pos.article_id,
                        "artikel": pos.artikel,
                        "qty": pos.quantity,
                        "unit": pos.unit,
                        "due_date": pos.due_date,
                        "notes": pos.notes,
                    },
                )

        db.commit()
        return {"id": anfrage_id, "anfrageNummer": anfrage_nummer, "message": "Anfrage erfolgreich erstellt"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen: {str(e)}")


@router.put("/anfragen/{anfrage_id}")
async def update_anfrage(
    anfrage_id: str,
    anfrage: schemas.AnfrageUpdate,
    db: Session = Depends(get_db)
):
    """Aktualisiert Anfrage"""
    try:
        existing = db.execute(
            text("SELECT id FROM einkauf_anfragen WHERE id = :id OR anfrage_nummer = :id"),
            {"id": anfrage_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        real_id = existing[0]
        update_data = {k: v for k, v in anfrage.model_dump(exclude={"positionen"}).items() if v is not None}

        if update_data:
            set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
            update_query = f"UPDATE einkauf_anfragen SET {set_clause}, updated_at = now() WHERE id = :id"
            update_data["id"] = real_id
            db.execute(text(update_query), update_data)

        db.commit()
        return {"message": "Anfrage erfolgreich aktualisiert"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren: {str(e)}")


@router.delete("/anfragen/{anfrage_id}")
async def delete_anfrage(anfrage_id: str, db: Session = Depends(get_db)):
    """Loescht Anfrage"""
    try:
        existing = db.execute(
            text("SELECT id FROM einkauf_anfragen WHERE id = :id OR anfrage_nummer = :id"),
            {"id": anfrage_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        real_id = existing[0]
        ***REMOVED*** Positionen loeschen
        db.execute(text("DELETE FROM einkauf_anfragen_positionen WHERE anfrage_id = :id"), {"id": real_id})
        ***REMOVED*** Anfrage loeschen
        db.execute(text("DELETE FROM einkauf_anfragen WHERE id = :id"), {"id": real_id})
        db.commit()
        return {"message": "Anfrage erfolgreich geloescht"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Loeschen: {str(e)}")


@router.post("/anfragen/{anfrage_id}/send")
async def send_anfrage(anfrage_id: str, db: Session = Depends(get_db)):
    """Versendet Anfrage an Lieferanten / setzt Status auf FREIGEGEBEN"""
    try:
        existing = db.execute(
            text("SELECT id, status FROM einkauf_anfragen WHERE id = :id OR anfrage_nummer = :id"),
            {"id": anfrage_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        real_id = existing[0]
        db.execute(
            text("UPDATE einkauf_anfragen SET status = 'FREIGEGEBEN', updated_at = now() WHERE id = :id"),
            {"id": real_id},
        )
        db.commit()
        return {"message": "Anfrage erfolgreich freigegeben", "status": "FREIGEGEBEN"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Freigeben: {str(e)}")


***REMOVED*** ============================================================================
***REMOVED*** RECHNUNGSEINGAENGE (Invoice Receipts) - PROC-IV-02
***REMOVED*** ============================================================================

@router.get("/rechnungseingaenge", response_model=dict)
async def get_rechnungseingaenge(
    status: Optional[str] = None,
    bestellung_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Holt Rechnungseingaenge"""
    try:
        query = "SELECT * FROM einkauf_rechnungseingaenge"
        params: dict = {"limit": limit, "skip": skip}
        conditions = []

        if status:
            conditions.append("status = :status")
            params["status"] = status
        if bestellung_id:
            conditions.append("bestellung_id = :bestellung_id")
            params["bestellung_id"] = bestellung_id

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"

        result = db.execute(text(query), params)
        rechnungen = [dict(row._mapping) for row in result]

        return {"total": len(rechnungen), "items": rechnungen}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.get("/rechnungseingaenge/{rechnung_id}")
async def get_rechnungseingang(rechnung_id: str, db: Session = Depends(get_db)):
    """Holt einzelnen Rechnungseingang"""
    try:
        row = db.execute(
            text("SELECT * FROM einkauf_rechnungseingaenge WHERE id = :id OR rechnungs_nummer = :id"),
            {"id": rechnung_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")

        rechnung = dict(row._mapping)

        ***REMOVED*** Positionen laden
        pos_rows = db.execute(
            text("SELECT * FROM einkauf_rechnungseingang_positionen WHERE rechnungseingang_id = :id"),
            {"id": rechnung["id"]},
        ).fetchall()
        rechnung["positionen"] = [dict(p._mapping) for p in pos_rows]

        return rechnung
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.post("/rechnungseingaenge", status_code=201)
async def create_rechnungseingang(
    rechnung: schemas.RechnungseingangCreate,
    db: Session = Depends(get_db)
):
    """Erstellt neuen Rechnungseingang"""
    try:
        rechnung_id = str(uuid.uuid4())

        db.execute(
            text("""
                INSERT INTO einkauf_rechnungseingaenge (
                    id, rechnungs_nummer, lieferant_id, lieferant_name,
                    bestellung_id, wareneingang_id, rechnungs_datum,
                    faelligkeits_datum, netto_betrag, mwst_betrag, brutto_betrag,
                    waehrung, status, zahlungsreferenz, notizen
                ) VALUES (
                    :id, :nummer, :lid, :lname, :bid, :wid, :rdatum,
                    :fdatum, :netto, :mwst, :brutto,
                    :waehrung, :status, :zref, :notizen
                )
            """),
            {
                "id": rechnung_id,
                "nummer": rechnung.rechnungsNummer,
                "lid": rechnung.lieferantId,
                "lname": rechnung.lieferantName,
                "bid": rechnung.bestellungId,
                "wid": rechnung.wareneingangId,
                "rdatum": rechnung.rechnungsDatum,
                "fdatum": rechnung.faelligkeitsDatum,
                "netto": rechnung.nettoBetrag,
                "mwst": rechnung.mwstBetrag,
                "brutto": rechnung.bruttoBetrag,
                "waehrung": rechnung.waehrung,
                "status": rechnung.status,
                "zref": rechnung.zahlungsreferenz,
                "notizen": rechnung.notizen,
            },
        )

        ***REMOVED*** Positionen anlegen
        if rechnung.positionen:
            for pos in rechnung.positionen:
                pos_id = str(uuid.uuid4())
                gesamtpreis = pos.gesamtpreis or (pos.menge * pos.einzelpreis)
                db.execute(
                    text("""
                        INSERT INTO einkauf_rechnungseingang_positionen (
                            id, rechnungseingang_id, artikel_id, artikel_name,
                            menge, einzelpreis, gesamtpreis, mwst_satz
                        ) VALUES (
                            :id, :re_id, :art_id, :art_name,
                            :menge, :epreis, :gpreis, :mwst
                        )
                    """),
                    {
                        "id": pos_id,
                        "re_id": rechnung_id,
                        "art_id": pos.artikelId,
                        "art_name": pos.artikelName,
                        "menge": pos.menge,
                        "epreis": pos.einzelpreis,
                        "gpreis": gesamtpreis,
                        "mwst": pos.mwstSatz,
                    },
                )

        db.commit()
        return {"id": rechnung_id, "message": "Rechnungseingang erfolgreich erstellt"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen: {str(e)}")


@router.put("/rechnungseingaenge/{rechnung_id}")
async def update_rechnungseingang(
    rechnung_id: str,
    rechnung: schemas.RechnungseingangUpdate,
    db: Session = Depends(get_db)
):
    """Aktualisiert Rechnungseingang"""
    try:
        existing = db.execute(
            text("SELECT id FROM einkauf_rechnungseingaenge WHERE id = :id OR rechnungs_nummer = :id"),
            {"id": rechnung_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")

        real_id = existing[0]

        ***REMOVED*** Map camelCase to snake_case for DB columns
        field_mapping = {
            "lieferantId": "lieferant_id",
            "lieferantName": "lieferant_name",
            "bestellungId": "bestellung_id",
            "wareneingangId": "wareneingang_id",
            "rechnungsDatum": "rechnungs_datum",
            "faelligkeitsDatum": "faelligkeits_datum",
            "nettoBetrag": "netto_betrag",
            "mwstBetrag": "mwst_betrag",
            "bruttoBetrag": "brutto_betrag",
            "zahlungsreferenz": "zahlungsreferenz",
            "notizen": "notizen",
            "status": "status",
            "abgleichErgebnis": "abgleich_ergebnis",
            "abweichungsBegruendung": "abweichungs_begruendung",
        }

        raw_data = rechnung.model_dump(exclude={"positionen"})
        update_data = {}
        for key, val in raw_data.items():
            if val is not None:
                db_col = field_mapping.get(key, key)
                update_data[db_col] = val

        if update_data:
            set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
            update_query = f"UPDATE einkauf_rechnungseingaenge SET {set_clause}, updated_at = now() WHERE id = :id"
            update_data["id"] = real_id
            db.execute(text(update_query), update_data)

        db.commit()
        return {"message": "Rechnungseingang erfolgreich aktualisiert"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren: {str(e)}")


@router.delete("/rechnungseingaenge/{rechnung_id}")
async def delete_rechnungseingang(rechnung_id: str, db: Session = Depends(get_db)):
    """Loescht Rechnungseingang"""
    try:
        existing = db.execute(
            text("SELECT id FROM einkauf_rechnungseingaenge WHERE id = :id OR rechnungs_nummer = :id"),
            {"id": rechnung_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")

        real_id = existing[0]
        db.execute(text("DELETE FROM einkauf_rechnungseingang_positionen WHERE rechnungseingang_id = :id"), {"id": real_id})
        db.execute(text("DELETE FROM einkauf_rechnungseingaenge WHERE id = :id"), {"id": real_id})
        db.commit()
        return {"message": "Rechnungseingang erfolgreich geloescht"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Loeschen: {str(e)}")

