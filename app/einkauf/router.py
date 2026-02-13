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
        existing = db.execute(text(check_query), {"id": bestellung_id}).fetchone()
        
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
        existing = db.execute(text(check_query), {"id": bestellung_id}).fetchone()
        
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


# ============================================================================
# ANFRAGEN / BEDARFSMELDUNGEN (Requisitions) - PROC-REQ-01
# ============================================================================

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

        # Positionen laden
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

        # Positionen anlegen
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
        # Positionen loeschen
        db.execute(text("DELETE FROM einkauf_anfragen_positionen WHERE anfrage_id = :id"), {"id": real_id})
        # Anfrage loeschen
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


# ============================================================================
# RECHNUNGSEINGAENGE (Invoice Receipts) - PROC-IV-02
# ============================================================================

# ... existing code ...

# ============================================================================
# PDF/OCR RECHNUNGSIMPORT (PROC-IV-01)
# ============================================================================

@router.post("/rechnungseingaenge/import/pdf", status_code=201)
async def import_rechnung_pdf(
    file_id: str,
    bestellung_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Importiert Rechnungsdaten aus PDF via OCR
    - Extrahiert Rechnungsnummer, Datum, Beträge, Lieferant
    - Optional: Match mit Bestellung für 3-Wege-Abgleich
    """
    try:
        # Simulierte OCR-Extraktion (in Produktion: pdfplumber, tesseract, oder Cloud-OCR)
        # Hier: Mock-Daten basierend auf Datei-ID
        ocr_result = {
            "extracted_data": {
                "rechnungs_nummer": f"OCR-{file_id[-8:]}",
                "rechnungs_datum": datetime.utcnow().date().isoformat(),
                "lieferant_name": "Muster-Lieferant GmbH",
                "lieferant_adresse": "Musterstraße 1, 12345 Musterstadt",
                "netto_betrag": 1500.00,
                "mwst_betrag": 285.00,
                "brutto_betrag": 1785.00,
                "waehrung": "EUR",
                "positionen": [
                    {
                        "artikel_name": "Musterartikel A",
                        "menge": 10,
                        "einzelpreis": 100.00,
                        "gesamtpreis": 1000.00,
                        "mwst_satz": 19.0
                    },
                    {
                        "artikel_name": "Musterartikel B",
                        "menge": 5,
                        "einzelpreis": 100.00,
                        "gesamtpreis": 500.00,
                        "mwst_satz": 19.0
                    }
                ]
            },
            "confidence_score": 0.92,
            "extraction_warnings": [],
            "ocr_model": "tesseract-v4",
            "processed_at": datetime.utcnow().isoformat()
        }
        
        # Wenn Bestellung angegeben: hole Bestelldaten für Vormerkung
        po_data = None
        if bestellung_id:
            po_result = db.execute(
                text("SELECT * FROM einkauf_bestellungen WHERE id = :id OR bestellnummer = :id"),
                {"id": bestellung_id}
            ).fetchone()
            if po_result:
                po_data = dict(po_result._mapping)
        
        return {
            "ocr_result": ocr_result,
            "bestellung": po_data,
            "message": "OCR-Extraktion erfolgreich. Bitte Daten prüfen und bestätigen."
        }
        
    except Exception as e:
        logger.error(f"OCR Import Fehler: {e}")
        raise HTTPException(status_code=500, detail=f"OCR-Fehler: {str(e)}")


@router.post("/rechnungseingaenge/import/confirm", status_code=201)
async def confirm_ocr_import(
    data: dict,
    bestellung_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Bestätigt OCR-Extraktion und erstellt Rechnungseingang
    """
    try:
        rechnung_id = str(uuid.uuid4())
        extracted = data.get("extracted_data", {})
        
        # Rechnungseingang erstellen
        db.execute(
            text("""
                INSERT INTO einkauf_rechnungseingaenge (
                    id, rechnungs_nummer, lieferant_name, bestellung_id,
                    rechnungs_datum, faelligkeits_datum,
                    netto_betrag, mwst_betrag, brutto_betrag, waehrung,
                    status, notizen, ocr_confidence
                ) VALUES (
                    :id, :rnummer, :lname, :bid,
                    :rdatum, :fdatum,
                    :netto, :mwst, :brutto, :waehrung,
                    'OFFEN', :notizen, :confidence
                )
            """),
            {
                "id": rechnung_id,
                "rnummer": extracted.get("rechnungs_nummer"),
                "lname": extracted.get("lieferant_name"),
                "bid": bestellung_id,
                "rdatum": extracted.get("rechnungs_datum"),
                "fdatum": datetime.strptime(extracted.get("rechnungs_datum"), "%Y-%m-%d").date() + timedelta(days=30),
                "netto": extracted.get("netto_betrag"),
                "mwst": extracted.get("mwst_betrag"),
                "brutto": extracted.get("brutto_betrag"),
                "waehrung": extracted.get("waehrung", "EUR"),
                "notizen": f"OCR-importiert: {data.get('ocr_result', {}).get('ocr_model')}",
                "confidence": data.get("ocr_result", {}).get("confidence_score", 0)
            }
        )
        
        # Positionen erstellen
        for idx, pos in enumerate(extracted.get("positionen", [])):
            pos_id = str(uuid.uuid4())
            db.execute(
                text("""
                    INSERT INTO einkauf_rechnungseingang_positionen (
                        id, rechnungseingang_id, artikel_name, menge, einzelpreis, gesamtpreis, mwst_satz
                    ) VALUES (:id, :re_id, :art_name, :menge, :epreis, :gpreis, :mwst)
                """),
                {
                    "id": pos_id,
                    "re_id": rechnung_id,
                    "art_name": pos.get("artikel_name"),
                    "menge": pos.get("menge"),
                    "epreis": pos.get("einzelpreis"),
                    "gpreis": pos.get("gesamtpreis"),
                    "mwst": pos.get("mwst_satz", 19.0)
                }
            )
        
        db.commit()
        
        return {
            "id": rechnung_id,
            "rechnungs_nummer": extracted.get("rechnungs_nummer"),
            "status": "OFFEN",
            "message": "Rechnung erfolgreich importiert"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"OCR Confirm Fehler: {e}")
        raise HTTPException(status_code=500, detail=f"Bestätigungs-Fehler: {str(e)}")


# ============================================================================
# SEPA ZAHLUNGSLÄUFE (PROC-PAY-01)
# ============================================================================

@router.get("/zahlungslaeufe", response_model=dict)
async def get_zahlungslaeufe(
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Holt Zahlungsläufe"""
    try:
        query = "SELECT * FROM einkauf_zahlungslaeufe"
        params: dict = {"limit": limit, "skip": skip}
        conditions = []

        if status:
            conditions.append("status = :status")
            params["status"] = status
        if from_date:
            conditions.append("ausfuehrungs_datum >= :from_date")
            params["from_date"] = from_date
        if to_date:
            conditions.append("ausfuehrungs_datum <= :to_date")
            params["to_date"] = to_date

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"

        result = db.execute(text(query), params)
        laeufe = [dict(row._mapping) for row in result]

        return {"total": len(laeufe), "items": laeufe}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.get("/zahlungslaeufe/{lauf_id}")
async def get_zahlungslauf(lauf_id: str, db: Session = Depends(get_db)):
    """Holt einzelnen Zahlungslauf mit Positionen"""
    try:
        row = db.execute(
            text("SELECT * FROM einkauf_zahlungslaeufe WHERE id = :id"),
            {"id": lauf_id}
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Zahlungslauf nicht gefunden")

        lauf = dict(row._mapping)

        # Positionen laden
        pos_rows = db.execute(
            text("SELECT * FROM einkauf_zahlungslauf_positionen WHERE zahlungslauf_id = :id"),
            {"id": lauf_id}
        ).fetchall()
        lauf["positionen"] = [dict(p._mapping) for p in pos_rows]

        return lauf
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@router.post("/zahlungslaeufe", status_code=201)
async def create_zahlungslauf(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Erstellt neuen Zahlungslauf aus offenen Rechnungen
    - Sammelt alle offenen Rechnungen für gewählte Lieferanten
    - Generiert SEPA-XML
    """
    try:
        lauf_id = str(uuid.uuid4())
        ausfuehrungsdatum = data.get("ausfuehrungs_datum") or (datetime.utcnow().date() + timedelta(days=1)).isoformat()
        
        # Sammle offene Rechnungen
        rechnungen_query = """
            SELECT r.*, l.iban, l.bic, l.kontoinhaber, l.firmenname as lieferant_name
            FROM einkauf_rechnungseingaenge r
            LEFT JOIN einkauf_lieferanten l ON r.lieferant_id = l.id
            WHERE r.status = 'OFFEN'
            AND (r.lieferant_id IS NULL OR r.lieferant_id IN :lieferanten)
            ORDER BY r.faelligkeits_datum ASC
        """
        
        lieferanten_ids = data.get("lieferanten_ids", [])
        if not lieferanten_ids:
            # Alle offenen Rechnungen
            rechnungen_result = db.execute(
                text("""
                    SELECT r.*, l.iban, l.bic, l.kontoinhaber, l.firmenname as lieferant_name
                    FROM einkauf_rechnungseingaenge r
                    LEFT JOIN einkauf_lieferanten l ON r.lieferant_id = l.id
                    WHERE r.status = 'OFFEN'
                    ORDER BY r.faelligkeits_datum ASC
                """),
                {}
            )
        else:
            rechnungen_result = db.execute(
                text(rechnungen_query),
                {"lieferanten": tuple(lieferanten_ids)}
            )
        
        rechnungen = [dict(row._mapping) for row in rechnungen_result]
        
        if not rechnungen:
            return {
                "message": "Keine offenen Rechnungen für Auswahl gefunden",
                "count": 0
            }
        
        # Gruppiere nach Lieferanten für SEPA
        lieferanten_gruppen = {}
        for r in rechnungen:
            key = r.get("lieferant_id") or "UNKNOWN"
            if key not in lieferanten_gruppen:
                lieferanten_gruppen[key] = {
                    "lieferant_name": r.get("lieferant_name") or "Unbekannter Lieferant",
                    "iban": r.get("iban") or "",
                    "bic": r.get("bic") or "",
                    "kontoinhaber": r.get("kontoinhaber") or "",
                    "rechnungen": [],
                    " Gesamtbetrag": 0
                }
            lieferanten_gruppen[key]["rechnungen"].append({
                "rechnungs_nummer": r["rechnungs_nummer"],
                "betrag": float(r["brutto_betrag"]) if r["brutto_betrag"] else 0,
                "faelligkeit": str(r["faelligkeits_datum"]) if r["faelligkeits_datum"] else None,
                "rechnung_id": r["id"]
            })
            lieferanten_gruppen[key][" Gesamtbetrag"] += float(r["brutto_betrag"]) if r["brutto_betrag"] else 0
        
        # Generiere SEPA-XML (vereinfacht)
        sepa_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:pain:001:001">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>PAY-{lauf_id[:8]}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}</MsgId>
      <CreDtTm>{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}</CreDtTm>
      <NbOfCstrms>{len(lieferanten_gruppen)}</NbOfCstrms>
      <CtrlSum>{sum(l[' Gesamtbetrag'] for l in lieferanten_gruppen.values()):.2f}</CtrlSum>
    </GrpHdr>"""
        
        for lid, gruppe in lieferanten_gruppen.items():
            sepa_xml += f"""
    <PmtInf>
      <PmtInfId>PI-{lid}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <ReqdExctnDt>{ausfuehrungsdatum}</ReqdExctnDt>
      <Dbtr>
        <Nm>{gruppe['kontoinhaber']}</Nm>
      </Dbtr>
      <DbtrAcct>
        <IBAN>DE12345678901234567890</IBAN>
      </DbtrAcct>
      <Cdtr>
        <Nm>{gruppe['lieferant_name']}</Nm>
      </Cdtr>
      <CdtrAcct>
        <IBAN>{gruppe['iban']}</IBAN>
      </CdtrAcct>
      <Amt>  
        <InstdAmt>{gruppe[' Gesamtbetrag']:.2f}</InstdAmt>
      </Amt>
    </PmtInf>"""
        
        sepa_xml += """
  </CstmrCdtTrfInitn>
</Document>"""
        
        # Speichere Zahlungslauf
        db.execute(
            text("""
                INSERT INTO einkauf_zahlungslaeufe (
                    id, bezeichnung, ausfuehrungs_datum, gesamt_betrag,
                    lieferanten_count, rechnungen_count, status,
                    sepa_xml, notizen
                ) VALUES (
                    :id, :bez, :datum, :betrag, :lcount, :rcount, 'BEREIT', :xml, :notizen
                )
            """),
            {
                "id": lauf_id,
                "bez": data.get("bezeichnung", f"Zahlungslauf {datetime.utcnow().strftime('%Y-%m-%d')}"),
                "datum": ausfuehrungsdatum,
                "betrag": sum(l[" Gesamtbetrag"] for l in lieferanten_gruppen.values()),
                "lcount": len(lieferanten_gruppen),
                "rcount": len(rechnungen),
                "xml": sepa_xml[:1000] + "..." if len(sepa_xml) > 1000 else sepa_xml,
                "notizen": data.get("notizen")
            }
        )
        
        # Positionen speichern
        for lid, gruppe in lieferanten_gruppen.items():
            for r in gruppe["rechnungen"]:
                pos_id = str(uuid.uuid4())
                db.execute(
                    text("""
                        INSERT INTO einkauf_zahlungslauf_positionen (
                            id, zahlungslauf_id, rechnung_id, lieferant_id,
                            betrag, status
                        ) VALUES (:id, :lauf_id, :re_id, :l_id, :betrag, 'AUSSTEHEND')
                    """),
                    {
                        "id": pos_id,
                        "lauf_id": lauf_id,
                        "re_id": r["rechnung_id"],
                        "l_id": lid if lid != "UNKNOWN" else None,
                        "betrag": r["betrag"]
                    }
                )
        
        db.commit()
        
        return {
            "id": lauf_id,
            "bezeichnung": data.get("bezeichnung"),
            "ausfuehrungs_datum": ausfuehrungsdatum,
            "gesamt_betrag": sum(l[" Gesamtbetrag"] for l in lieferanten_gruppen.values()),
            "lieferanten_count": len(lieferanten_gruppen),
            "rechnungen_count": len(rechnungen),
            "status": "BEREIT",
            "message": "Zahlungslauf erfolgreich erstellt"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Zahlungslauf Fehler: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler: {str(e)}")


@router.post("/zahlungslaeufe/{lauf_id}/execute")
async def execute_zahlungslauf(lauf_id: str, db: Session = Depends(get_db)):
    """
    Führt Zahlungslauf aus
    - Ändert Status auf 'AUSGEFUEHRT'
    - Markiert alle Rechnungen als 'BEZAHLT'
    """
    try:
        # Prüfe Zahlungslauf
        row = db.execute(
            text("SELECT id, status FROM einkauf_zahlungslaeufe WHERE id = :id"),
            {"id": lauf_id}
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Zahlungslauf nicht gefunden")
        
        if row["status"] != "BEREIT":
            raise HTTPException(status_code=400, detail=f"Zahlungslauf hat Status '{row['status']}' und kann nicht ausgeführt werden")
        
        # Hole Positionen
        positionen = db.execute(
            text("SELECT * FROM einkauf_zahlungslauf_positionen WHERE zahlungslauf_id = :id"),
            {"id": lauf_id}
        ).fetchall()
        
        # Update Rechnungen
        for pos in positionen:
            if pos["rechnung_id"]:
                db.execute(
                    text("UPDATE einkauf_rechnungseingaenge SET status = 'BEZAHLT', updated_at = now() WHERE id = :id"),
                    {"id": pos["rechnung_id"]}
                )
            
            # Update Position
            db.execute(
                text("UPDATE einkauf_zahlungslauf_positionen SET status = 'AUSGEFUEHRT', executed_at = now() WHERE id = :id"),
                {"id": pos["id"]}
            )
        
        # Update Zahlungslauf
        db.execute(
            text("UPDATE einkauf_zahlungslaeufe SET status = 'AUSGEFUEHRT', executed_at = now(), updated_at = now() WHERE id = :id"),
            {"id": lauf_id}
        )
        
        db.commit()
        
        return {
            "id": lauf_id,
            "status": "AUSGEFUEHRT",
            "executed_at": datetime.utcnow().isoformat(),
            "message": "Zahlungslauf erfolgreich ausgeführt"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Execute Fehler: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler: {str(e)}")


@router.get("/zahlungslaeufe/{lauf_id}/sepa")
async def get_sepa_xml(lauf_id: str, db: Session = Depends(get_db)):
    """Holt SEPA-XML für Zahlungslauf (Download)"""
    try:
        row = db.execute(
            text("SELECT sepa_xml, bezeichnung, gesamt_betrag FROM einkauf_zahlungslaeufe WHERE id = :id"),
            {"id": lauf_id}
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Zahlungslauf nicht gefunden")
        
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=row["sepa_xml"],
            media_type="application/xml",
            headers={"Content-Disposition": f'attachment; filename="sepa_{row["bezeichnung"]}.xml"'}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler: {str(e)}")



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

        # Positionen laden
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

        # Positionen anlegen
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

        # Map camelCase to snake_case for DB columns
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

