"""
VALEO-NeuroERP - Einkauf Router
REST API Endpoints für Einkauf/Beschaffung

SEC-008: Tenant-Isolation + Mass-Assignment-Whitelist + Information-Disclosure-Fix
"""

import logging
import os
from app.core.uuid7 import uuid7
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header, Request, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from app.core.database import get_db
from app.auth.deps import get_tenant_id
from app.einkauf import schemas
from app.einkauf.ocr_invoice import extract_invoice_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/einkauf", tags=["Einkauf"])

# ── Mass-Assignment Whitelists ───────────────────────────────────────────────
_LIEFERANT_UPDATABLE = frozenset({
    "firmenname", "ansprechpartner", "email", "telefon",
    "strasse", "plz", "ort", "land", "zahlungsbedingungen",
    "lieferzeit_tage", "bewertung", "aktiv",
})

_BESTELLUNG_UPDATABLE = frozenset({
    "lieferant_id", "gewuenschtes_lieferdatum", "status",
    "netto_summe", "mwst_betrag", "brutto_summe",
})

_ANFRAGE_UPDATABLE = frozenset({
    "typ", "anforderer", "abteilung", "datum", "prioritaet", "status",
    "begruendung", "kostenstelle", "projekt_id", "artikel", "menge",
    "einheit", "budget", "notizen",
})


def _safe_update_data(raw: dict, whitelist: frozenset) -> dict:
    """Filter update payload against whitelist — prevents mass-assignment attacks."""
    return {k: v for k, v in raw.items() if v is not None and k in whitelist}


# ============================================================================
# LIEFERANTEN
# ============================================================================

@router.get("/lieferanten", response_model=dict)
async def get_lieferanten(
    aktiv: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt Lieferantenliste"""
    try:
        query = "SELECT * FROM einkauf_lieferanten WHERE tenant_id = :tenant_id"
        params = {"limit": limit, "skip": skip, "tenant_id": tenant_id}

        if aktiv is not None:
            query += " AND aktiv = :aktiv"
            params["aktiv"] = aktiv

        query += " ORDER BY firmenname LIMIT :limit OFFSET :skip"

        result = db.execute(text(query), params)
        lieferanten = [dict(row) for row in result]

        return {
            "total": len(lieferanten),
            "items": lieferanten
        }
    except Exception:
        logger.exception("Lieferantenliste laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Laden der Lieferanten")


@router.get("/lieferanten/{lieferant_id}")
async def get_lieferant(
    lieferant_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt einzelnen Lieferanten"""
    try:
        query = "SELECT * FROM einkauf_lieferanten WHERE id = :id AND tenant_id = :tenant_id"
        result = db.execute(text(query), {"id": lieferant_id, "tenant_id": tenant_id})
        lieferant = result.fetchone()

        if not lieferant:
            raise HTTPException(status_code=404, detail="Lieferant nicht gefunden")

        return dict(lieferant)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Lieferant laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Laden des Lieferanten")


@router.post("/lieferanten", status_code=201)
async def create_lieferant(
    lieferant: schemas.LieferantCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Erstellt neuen Lieferanten"""
    try:
        check_query = "SELECT id FROM einkauf_lieferanten WHERE lieferantennummer = :nummer AND tenant_id = :tenant_id"
        existing = db.execute(text(check_query), {"nummer": lieferant.lieferantennummer, "tenant_id": tenant_id}).fetchone()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Lieferantennummer {lieferant.lieferantennummer} existiert bereits"
            )

        insert_query = """
            INSERT INTO einkauf_lieferanten (
                lieferantennummer, firmenname, ansprechpartner, email, telefon,
                strasse, plz, ort, land, zahlungsbedingungen, lieferzeit_tage,
                bewertung, aktiv, tenant_id
            ) VALUES (
                :lieferantennummer, :firmenname, :ansprechpartner, :email, :telefon,
                :strasse, :plz, :ort, :land, :zahlungsbedingungen, :lieferzeit_tage,
                :bewertung, :aktiv, :tenant_id
            ) RETURNING id
        """

        params = lieferant.model_dump()
        params["tenant_id"] = tenant_id
        result = db.execute(text(insert_query), params)
        lieferant_id = result.fetchone()[0]
        db.commit()

        return {"id": lieferant_id, "message": "Lieferant erfolgreich erstellt"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Lieferant erstellen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen des Lieferanten")


@router.put("/lieferanten/{lieferant_id}")
async def update_lieferant(
    lieferant_id: int,
    lieferant: schemas.LieferantUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Aktualisiert Lieferanten"""
    try:
        check_query = "SELECT id FROM einkauf_lieferanten WHERE id = :id AND tenant_id = :tenant_id"
        existing = db.execute(text(check_query), {"id": lieferant_id, "tenant_id": tenant_id}).fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Lieferant nicht gefunden")

        update_data = _safe_update_data(lieferant.model_dump(), _LIEFERANT_UPDATABLE)

        if not update_data:
            raise HTTPException(status_code=400, detail="Keine Daten zum Aktualisieren")

        set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
        update_query = f"UPDATE einkauf_lieferanten SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = :id AND tenant_id = :tenant_id"

        update_data["id"] = lieferant_id
        update_data["tenant_id"] = tenant_id
        db.execute(text(update_query), update_data)
        db.commit()

        return {"message": "Lieferant erfolgreich aktualisiert"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Lieferant aktualisieren fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren des Lieferanten")


@router.delete("/lieferanten/{lieferant_id}")
async def delete_lieferant(
    lieferant_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Löscht Lieferanten"""
    try:
        check_query = "SELECT id FROM einkauf_lieferanten WHERE id = :id AND tenant_id = :tenant_id"
        existing = db.execute(text(check_query), {"id": lieferant_id, "tenant_id": tenant_id}).fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Lieferant nicht gefunden")

        delete_query = "DELETE FROM einkauf_lieferanten WHERE id = :id AND tenant_id = :tenant_id"
        db.execute(text(delete_query), {"id": lieferant_id, "tenant_id": tenant_id})
        db.commit()

        return {"message": "Lieferant erfolgreich gelöscht"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Lieferant löschen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Löschen des Lieferanten")


# ============================================================================
# BESTELLUNGEN
# ============================================================================

@router.get("/bestellungen", response_model=dict)
async def get_bestellungen(
    status: Optional[str] = None,
    lieferant_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt Bestellungsliste"""
    try:
        query = "SELECT * FROM einkauf_bestellungen WHERE tenant_id = :tenant_id"
        params = {"limit": limit, "skip": skip, "tenant_id": tenant_id}

        if status:
            query += " AND status = :status"
            params["status"] = status

        if lieferant_id:
            query += " AND lieferant_id = :lieferant_id"
            params["lieferant_id"] = lieferant_id

        query += " ORDER BY bestelldatum DESC LIMIT :limit OFFSET :skip"

        result = db.execute(text(query), params)
        bestellungen = [dict(row) for row in result]

        return {
            "total": len(bestellungen),
            "items": bestellungen
        }
    except Exception:
        logger.exception("Bestellungsliste laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Laden der Bestellungen")


@router.get("/bestellungen/{bestellung_id}")
async def get_bestellung(
    bestellung_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt einzelne Bestellung"""
    try:
        query = "SELECT * FROM einkauf_bestellungen WHERE id = :id AND tenant_id = :tenant_id"
        result = db.execute(text(query), {"id": bestellung_id, "tenant_id": tenant_id})
        bestellung = result.fetchone()

        if not bestellung:
            raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")

        return dict(bestellung)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Bestellung laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Laden der Bestellung")


@router.post("/bestellungen", status_code=201)
async def create_bestellung(
    bestellung: schemas.BestellungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Erstellt neue Bestellung"""
    try:
        check_query = "SELECT id FROM einkauf_bestellungen WHERE bestellnummer = :nummer AND tenant_id = :tenant_id"
        existing = db.execute(text(check_query), {"nummer": bestellung.bestellnummer, "tenant_id": tenant_id}).fetchone()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Bestellnummer {bestellung.bestellnummer} existiert bereits"
            )

        insert_query = """
            INSERT INTO einkauf_bestellungen (
                bestellnummer, lieferant_id, bestelldatum, gewuenschtes_lieferdatum,
                status, netto_summe, mwst_betrag, brutto_summe, erstellt_von, tenant_id
            ) VALUES (
                :bestellnummer, :lieferant_id, :bestelldatum, :gewuenschtes_lieferdatum,
                :status, :netto_summe, :mwst_betrag, :brutto_summe, :erstellt_von, :tenant_id
            ) RETURNING id
        """

        params = bestellung.model_dump()
        params["tenant_id"] = tenant_id
        result = db.execute(text(insert_query), params)
        bestellung_id = result.fetchone()[0]
        db.commit()

        return {"id": bestellung_id, "message": "Bestellung erfolgreich erstellt"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Bestellung erstellen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen der Bestellung")


@router.put("/bestellungen/{bestellung_id}")
async def update_bestellung(
    bestellung_id: int,
    bestellung: schemas.BestellungUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Aktualisiert Bestellung"""
    try:
        check_query = "SELECT id FROM einkauf_bestellungen WHERE id = :id AND tenant_id = :tenant_id"
        existing = db.execute(text(check_query), {"id": bestellung_id, "tenant_id": tenant_id}).fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")

        update_data = _safe_update_data(bestellung.model_dump(), _BESTELLUNG_UPDATABLE)

        if not update_data:
            raise HTTPException(status_code=400, detail="Keine Daten zum Aktualisieren")

        set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
        update_query = f"UPDATE einkauf_bestellungen SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = :id AND tenant_id = :tenant_id"

        update_data["id"] = bestellung_id
        update_data["tenant_id"] = tenant_id
        db.execute(text(update_query), update_data)
        db.commit()

        return {"message": "Bestellung erfolgreich aktualisiert"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Bestellung aktualisieren fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren der Bestellung")


@router.delete("/bestellungen/{bestellung_id}")
async def delete_bestellung(
    bestellung_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Löscht Bestellung"""
    try:
        check_query = "SELECT id FROM einkauf_bestellungen WHERE id = :id AND tenant_id = :tenant_id"
        existing = db.execute(text(check_query), {"id": bestellung_id, "tenant_id": tenant_id}).fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")

        delete_query = "DELETE FROM einkauf_bestellungen WHERE id = :id AND tenant_id = :tenant_id"
        db.execute(text(delete_query), {"id": bestellung_id, "tenant_id": tenant_id})
        db.commit()

        return {"message": "Bestellung erfolgreich gelöscht"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Bestellung löschen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Löschen der Bestellung")


# ============================================================================
# ANFRAGEN / BEDARFSMELDUNGEN (Requisitions) - PROC-REQ-01
# ============================================================================

@router.get("/anfragen", response_model=dict)
async def get_anfragen(
    status: Optional[str] = None,
    typ: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt Anfragen/Bedarfsmeldungen"""
    try:
        query = "SELECT * FROM einkauf_anfragen WHERE tenant_id = :tenant_id"
        params: dict = {"limit": limit, "skip": skip, "tenant_id": tenant_id}

        if status:
            query += " AND status = :status"
            params["status"] = status
        if typ:
            query += " AND typ = :typ"
            params["typ"] = typ

        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"

        result = db.execute(text(query), params)
        anfragen = [dict(row._mapping) for row in result]

        return {"total": len(anfragen), "items": anfragen}
    except Exception:
        logger.exception("Anfragenliste laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Laden der Anfragen")


@router.get("/anfragen/{anfrage_id}")
async def get_anfrage(
    anfrage_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt einzelne Anfrage"""
    try:
        row = db.execute(
            text("SELECT * FROM einkauf_anfragen WHERE (id = :id OR anfrage_nummer = :id) AND tenant_id = :tenant_id"),
            {"id": anfrage_id, "tenant_id": tenant_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        anfrage = dict(row._mapping)

        pos_rows = db.execute(
            text("SELECT * FROM einkauf_anfragen_positionen WHERE anfrage_id = :id"),
            {"id": anfrage["id"]},
        ).fetchall()
        anfrage["positionen"] = [dict(p._mapping) for p in pos_rows]

        return anfrage
    except HTTPException:
        raise
    except Exception:
        logger.exception("Anfrage laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Laden der Anfrage")


@router.post("/anfragen", status_code=201)
async def create_anfrage(
    anfrage: schemas.AnfrageCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Erstellt neue Anfrage/Bedarfsmeldung"""
    try:
        anfrage_id = uuid7()
        anfrage_nummer = anfrage.anfrageNummer or f"BANF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        db.execute(
            text("""
                INSERT INTO einkauf_anfragen (
                    id, anfrage_nummer, typ, anforderer, abteilung, datum,
                    prioritaet, status, begruendung, kostenstelle, projekt_id,
                    artikel, menge, einheit, budget, notizen, tenant_id
                ) VALUES (
                    :id, :nummer, :typ, :anforderer, :abteilung, :datum,
                    :prioritaet, :status, :begruendung, :kostenstelle, :projekt_id,
                    :artikel, :menge, :einheit, :budget, :notizen, :tenant_id
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
                "tenant_id": tenant_id,
            },
        )

        if anfrage.positionen:
            for pos in anfrage.positionen:
                pos_id = uuid7()
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
    except Exception:
        db.rollback()
        logger.exception("Anfrage erstellen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen der Anfrage")


@router.put("/anfragen/{anfrage_id}")
async def update_anfrage(
    anfrage_id: str,
    anfrage: schemas.AnfrageUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Aktualisiert Anfrage"""
    try:
        existing = db.execute(
            text("SELECT id FROM einkauf_anfragen WHERE (id = :id OR anfrage_nummer = :id) AND tenant_id = :tenant_id"),
            {"id": anfrage_id, "tenant_id": tenant_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        real_id = existing[0]
        update_data = _safe_update_data(
            anfrage.model_dump(exclude={"positionen"}), _ANFRAGE_UPDATABLE
        )

        if update_data:
            set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
            update_query = f"UPDATE einkauf_anfragen SET {set_clause}, updated_at = now() WHERE id = :id AND tenant_id = :tenant_id"
            update_data["id"] = real_id
            update_data["tenant_id"] = tenant_id
            db.execute(text(update_query), update_data)

        db.commit()
        return {"message": "Anfrage erfolgreich aktualisiert"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Anfrage aktualisieren fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren der Anfrage")


@router.delete("/anfragen/{anfrage_id}")
async def delete_anfrage(
    anfrage_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Loescht Anfrage"""
    try:
        existing = db.execute(
            text("SELECT id FROM einkauf_anfragen WHERE (id = :id OR anfrage_nummer = :id) AND tenant_id = :tenant_id"),
            {"id": anfrage_id, "tenant_id": tenant_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        real_id = existing[0]
        db.execute(text("DELETE FROM einkauf_anfragen_positionen WHERE anfrage_id = :id"), {"id": real_id})
        db.execute(text("DELETE FROM einkauf_anfragen WHERE id = :id AND tenant_id = :tenant_id"), {"id": real_id, "tenant_id": tenant_id})
        db.commit()
        return {"message": "Anfrage erfolgreich geloescht"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Anfrage löschen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Loeschen der Anfrage")


@router.post("/anfragen/{anfrage_id}/send")
async def send_anfrage(
    anfrage_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Versendet Anfrage an Lieferanten / setzt Status auf FREIGEGEBEN"""
    try:
        existing = db.execute(
            text("SELECT id, status FROM einkauf_anfragen WHERE (id = :id OR anfrage_nummer = :id) AND tenant_id = :tenant_id"),
            {"id": anfrage_id, "tenant_id": tenant_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        real_id = existing[0]
        db.execute(
            text("UPDATE einkauf_anfragen SET status = 'FREIGEGEBEN', updated_at = now() WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": real_id, "tenant_id": tenant_id},
        )
        db.commit()
        return {"message": "Anfrage erfolgreich freigegeben", "status": "FREIGEGEBEN"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Anfrage freigeben fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Freigeben der Anfrage")


# ============================================================================
# RECHNUNGSEINGAENGE (Invoice Receipts) - PROC-IV-02
# ============================================================================

# ... existing code ...

# ============================================================================
# PDF/OCR RECHNUNGSIMPORT (PROC-IV-01)
# Engine: env EINKAUF_OCR_ENGINE=stub|pdfplumber|… — Upload-Pfad via EINKAUF_OCR_UPLOAD_DIR
# ============================================================================

EINKAUF_OCR_ENGINE = os.getenv("EINKAUF_OCR_ENGINE", "stub")

@router.post("/rechnungseingaenge/import/pdf", status_code=201)
async def import_rechnung_pdf(
    file_id: str,
    bestellung_id: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Importiert Rechnungsdaten aus PDF via OCR
    - Extrahiert Rechnungsnummer, Datum, Beträge, Lieferant
    - Optional: Match mit Bestellung für 3-Wege-Abgleich
    """
    try:
        ocr_result = extract_invoice_pdf(file_id=file_id, engine=EINKAUF_OCR_ENGINE, pdf_bytes=None)

        po_data = None
        if bestellung_id:
            po_result = db.execute(
                text("SELECT * FROM einkauf_bestellungen WHERE (id = :id OR bestellnummer = :id) AND tenant_id = :tenant_id"),
                {"id": bestellung_id, "tenant_id": tenant_id}
            ).fetchone()
            if po_result:
                po_data = dict(po_result._mapping)

        return {
            "ocr_result": ocr_result,
            "bestellung": po_data,
            "message": "OCR-Extraktion erfolgreich. Bitte Daten prüfen und bestätigen."
        }

    except Exception:
        logger.exception("OCR Import fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim OCR-Import")


@router.post("/rechnungseingaenge/import/pdf-upload", status_code=201)
async def import_rechnung_pdf_upload(
    file: UploadFile = File(...),
    bestellung_id: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Multipart-Upload eines PDF; OCR wie import/pdf (EINKAUF_OCR_ENGINE)."""
    try:
        content = await file.read()
        fid = (file.filename or "upload.pdf")[:160]
        ocr_result = extract_invoice_pdf(file_id=fid, engine=EINKAUF_OCR_ENGINE, pdf_bytes=content)

        po_data = None
        if bestellung_id:
            po_result = db.execute(
                text(
                    "SELECT * FROM einkauf_bestellungen WHERE (id = :id OR bestellnummer = :id) "
                    "AND tenant_id = :tenant_id"
                ),
                {"id": bestellung_id, "tenant_id": tenant_id},
            ).fetchone()
            if po_result:
                po_data = dict(po_result._mapping)

        return {
            "ocr_result": ocr_result,
            "bestellung": po_data,
            "message": "OCR-Extraktion erfolgreich (Upload). Bitte Daten prüfen und bestätigen.",
        }
    except Exception:
        logger.exception("OCR Upload fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim OCR-Upload")


@router.post("/rechnungseingaenge/import/confirm", status_code=201)
async def confirm_ocr_import(
    data: dict,
    bestellung_id: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Bestätigt OCR-Extraktion und erstellt Rechnungseingang"""
    try:
        from datetime import timedelta
        rechnung_id = uuid7()
        extracted = data.get("extracted_data", {})

        db.execute(
            text("""
                INSERT INTO einkauf_rechnungseingaenge (
                    id, rechnungs_nummer, lieferant_name, bestellung_id,
                    rechnungs_datum, faelligkeits_datum,
                    netto_betrag, mwst_betrag, brutto_betrag, waehrung,
                    status, notizen, ocr_confidence, tenant_id
                ) VALUES (
                    :id, :rnummer, :lname, :bid,
                    :rdatum, :fdatum,
                    :netto, :mwst, :brutto, :waehrung,
                    'OFFEN', :notizen, :confidence, :tenant_id
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
                "confidence": data.get("ocr_result", {}).get("confidence_score", 0),
                "tenant_id": tenant_id,
            }
        )

        for idx, pos in enumerate(extracted.get("positionen", [])):
            pos_id = uuid7()
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

    except Exception:
        db.rollback()
        logger.exception("OCR Bestätigung fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler bei der OCR-Bestätigung")


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
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt Zahlungsläufe"""
    try:
        query = "SELECT * FROM einkauf_zahlungslaeufe WHERE tenant_id = :tenant_id"
        params: dict = {"limit": limit, "skip": skip, "tenant_id": tenant_id}

        if status:
            query += " AND status = :status"
            params["status"] = status
        if from_date:
            query += " AND ausfuehrungs_datum >= :from_date"
            params["from_date"] = from_date
        if to_date:
            query += " AND ausfuehrungs_datum <= :to_date"
            params["to_date"] = to_date

        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"

        result = db.execute(text(query), params)
        laeufe = [dict(row._mapping) for row in result]

        return {"total": len(laeufe), "items": laeufe}
    except Exception:
        logger.exception("Zahlungsläufe laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Laden der Zahlungsläufe")


@router.get("/zahlungslaeufe/{lauf_id}")
async def get_zahlungslauf(
    lauf_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt einzelnen Zahlungslauf mit Positionen"""
    try:
        row = db.execute(
            text("SELECT * FROM einkauf_zahlungslaeufe WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": lauf_id, "tenant_id": tenant_id}
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Zahlungslauf nicht gefunden")

        lauf = dict(row._mapping)

        pos_rows = db.execute(
            text("SELECT * FROM einkauf_zahlungslauf_positionen WHERE zahlungslauf_id = :id"),
            {"id": lauf_id}
        ).fetchall()
        lauf["positionen"] = [dict(p._mapping) for p in pos_rows]

        return lauf
    except HTTPException:
        raise
    except Exception:
        logger.exception("Zahlungslauf laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Laden des Zahlungslaufs")


@router.post("/zahlungslaeufe", status_code=201)
async def create_zahlungslauf(
    data: dict,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Erstellt neuen Zahlungslauf aus offenen Rechnungen
    - Sammelt alle offenen Rechnungen für gewählte Lieferanten
    - Generiert SEPA-XML
    """
    try:
        from datetime import timedelta
        lauf_id = uuid7()
        ausfuehrungsdatum = data.get("ausfuehrungs_datum") or (datetime.utcnow().date() + timedelta(days=1)).isoformat()

        lieferanten_ids = data.get("lieferanten_ids", [])
        if not lieferanten_ids:
            rechnungen_result = db.execute(
                text("""
                    SELECT r.*, l.iban, l.bic, l.kontoinhaber, l.firmenname as lieferant_name
                    FROM einkauf_rechnungseingaenge r
                    LEFT JOIN einkauf_lieferanten l ON r.lieferant_id = l.id
                    WHERE r.status = 'OFFEN' AND r.tenant_id = :tenant_id
                    ORDER BY r.faelligkeits_datum ASC
                """),
                {"tenant_id": tenant_id}
            )
        else:
            rechnungen_result = db.execute(
                text("""
                    SELECT r.*, l.iban, l.bic, l.kontoinhaber, l.firmenname as lieferant_name
                    FROM einkauf_rechnungseingaenge r
                    LEFT JOIN einkauf_lieferanten l ON r.lieferant_id = l.id
                    WHERE r.status = 'OFFEN' AND r.tenant_id = :tenant_id
                    AND (r.lieferant_id IS NULL OR r.lieferant_id IN :lieferanten)
                    ORDER BY r.faelligkeits_datum ASC
                """),
                {"lieferanten": tuple(lieferanten_ids), "tenant_id": tenant_id}
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
                    "gesamtbetrag": 0
                }
            lieferanten_gruppen[key]["rechnungen"].append({
                "rechnungs_nummer": r["rechnungs_nummer"],
                "betrag": float(r["brutto_betrag"]) if r["brutto_betrag"] else 0,
                "faelligkeit": str(r["faelligkeits_datum"]) if r["faelligkeits_datum"] else None,
                "rechnung_id": r["id"]
            })
            lieferanten_gruppen[key]["gesamtbetrag"] += float(r["brutto_betrag"]) if r["brutto_betrag"] else 0

        # Generiere SEPA-XML (vereinfacht)
        from xml.sax.saxutils import escape as xml_escape
        sepa_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:pain:001:001">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>PAY-{xml_escape(str(lauf_id)[:8])}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}</MsgId>
      <CreDtTm>{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}</CreDtTm>
      <NbOfCstrms>{len(lieferanten_gruppen)}</NbOfCstrms>
      <CtrlSum>{sum(l['gesamtbetrag'] for l in lieferanten_gruppen.values()):.2f}</CtrlSum>
    </GrpHdr>"""

        for lid, gruppe in lieferanten_gruppen.items():
            sepa_xml += f"""
    <PmtInf>
      <PmtInfId>PI-{xml_escape(str(lid))}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <ReqdExctnDt>{xml_escape(str(ausfuehrungsdatum))}</ReqdExctnDt>
      <Dbtr>
        <Nm>{xml_escape(gruppe['kontoinhaber'])}</Nm>
      </Dbtr>
      <DbtrAcct>
        <IBAN>DE12345678901234567890</IBAN>
      </DbtrAcct>
      <Cdtr>
        <Nm>{xml_escape(gruppe['lieferant_name'])}</Nm>
      </Cdtr>
      <CdtrAcct>
        <IBAN>{xml_escape(gruppe['iban'])}</IBAN>
      </CdtrAcct>
      <Amt>
        <InstdAmt>{gruppe['gesamtbetrag']:.2f}</InstdAmt>
      </Amt>
    </PmtInf>"""

        sepa_xml += """
  </CstmrCdtTrfInitn>
</Document>"""

        db.execute(
            text("""
                INSERT INTO einkauf_zahlungslaeufe (
                    id, bezeichnung, ausfuehrungs_datum, gesamt_betrag,
                    lieferanten_count, rechnungen_count, status,
                    sepa_xml, notizen, tenant_id
                ) VALUES (
                    :id, :bez, :datum, :betrag, :lcount, :rcount, 'BEREIT', :xml, :notizen, :tenant_id
                )
            """),
            {
                "id": lauf_id,
                "bez": data.get("bezeichnung", f"Zahlungslauf {datetime.utcnow().strftime('%Y-%m-%d')}"),
                "datum": ausfuehrungsdatum,
                "betrag": sum(l["gesamtbetrag"] for l in lieferanten_gruppen.values()),
                "lcount": len(lieferanten_gruppen),
                "rcount": len(rechnungen),
                "xml": sepa_xml[:1000] + "..." if len(sepa_xml) > 1000 else sepa_xml,
                "notizen": data.get("notizen"),
                "tenant_id": tenant_id,
            }
        )

        for lid, gruppe in lieferanten_gruppen.items():
            for r in gruppe["rechnungen"]:
                pos_id = uuid7()
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
            "gesamt_betrag": sum(l["gesamtbetrag"] for l in lieferanten_gruppen.values()),
            "lieferanten_count": len(lieferanten_gruppen),
            "rechnungen_count": len(rechnungen),
            "status": "BEREIT",
            "message": "Zahlungslauf erfolgreich erstellt"
        }

    except Exception:
        db.rollback()
        logger.exception("Zahlungslauf erstellen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen des Zahlungslaufs")


@router.post("/zahlungslaeufe/{lauf_id}/execute")
async def execute_zahlungslauf(
    lauf_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Führt Zahlungslauf aus — Status auf AUSGEFUEHRT, Rechnungen auf BEZAHLT"""
    try:
        row = db.execute(
            text("SELECT id, status FROM einkauf_zahlungslaeufe WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": lauf_id, "tenant_id": tenant_id}
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Zahlungslauf nicht gefunden")

        if row["status"] != "BEREIT":
            raise HTTPException(status_code=400, detail=f"Zahlungslauf hat Status '{row['status']}' und kann nicht ausgeführt werden")

        positionen = db.execute(
            text("SELECT * FROM einkauf_zahlungslauf_positionen WHERE zahlungslauf_id = :id"),
            {"id": lauf_id}
        ).fetchall()

        for pos in positionen:
            if pos["rechnung_id"]:
                db.execute(
                    text("UPDATE einkauf_rechnungseingaenge SET status = 'BEZAHLT', updated_at = now() WHERE id = :id AND tenant_id = :tenant_id"),
                    {"id": pos["rechnung_id"], "tenant_id": tenant_id}
                )

            db.execute(
                text("UPDATE einkauf_zahlungslauf_positionen SET status = 'AUSGEFUEHRT', executed_at = now() WHERE id = :id"),
                {"id": pos["id"]}
            )

        db.execute(
            text("UPDATE einkauf_zahlungslaeufe SET status = 'AUSGEFUEHRT', executed_at = now(), updated_at = now() WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": lauf_id, "tenant_id": tenant_id}
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
    except Exception:
        db.rollback()
        logger.exception("Zahlungslauf ausführen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Ausführen des Zahlungslaufs")


@router.get("/zahlungslaeufe/{lauf_id}/sepa")
async def get_sepa_xml(
    lauf_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt SEPA-XML für Zahlungslauf (Download)"""
    try:
        row = db.execute(
            text("SELECT sepa_xml, bezeichnung, gesamt_betrag FROM einkauf_zahlungslaeufe WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": lauf_id, "tenant_id": tenant_id}
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
    except Exception:
        logger.exception("SEPA-XML laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Laden des SEPA-XML")


@router.get("/rechnungseingaenge/{rechnung_id}")
async def get_rechnungseingang(
    rechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Holt einzelnen Rechnungseingang"""
    try:
        row = db.execute(
            text("SELECT * FROM einkauf_rechnungseingaenge WHERE (id = :id OR rechnungs_nummer = :id) AND tenant_id = :tenant_id"),
            {"id": rechnung_id, "tenant_id": tenant_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")

        rechnung = dict(row._mapping)

        pos_rows = db.execute(
            text("SELECT * FROM einkauf_rechnungseingang_positionen WHERE rechnungseingang_id = :id"),
            {"id": rechnung["id"]},
        ).fetchall()
        rechnung["positionen"] = [dict(p._mapping) for p in pos_rows]

        return rechnung
    except HTTPException:
        raise
    except Exception:
        logger.exception("Rechnungseingang laden fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Datenbankfehler beim Laden des Rechnungseingangs")


def _get_audit_user(request: Request) -> str:
    """User ID for audit fields (sub or preferred_username from token, or 'system')."""
    claims = getattr(request.state, "token_claims", None) or {}
    return claims.get("sub") or claims.get("preferred_username") or "system"


@router.post("/rechnungseingaenge/{rechnung_id}/pruefen")
async def rechnungseingang_pruefen(
    rechnung_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Setzt Status auf GEPRUEFT (nur aus ENTWURF/ERFASST/OFFEN). Speichert checked_by/checked_at."""
    row = db.execute(
        text("SELECT id, status FROM einkauf_rechnungseingaenge WHERE (id = :id OR rechnungs_nummer = :id) AND tenant_id = :tenant_id"),
        {"id": rechnung_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")
    status = (row._mapping.get("status") or "").upper()
    allowed = ("ENTWURF", "ERFASST", "OFFEN")
    if status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Prüfen nur möglich bei Status {', '.join(allowed)}. Aktuell: {status}",
        )
    user = _get_audit_user(request)
    db.execute(
        text("""
            UPDATE einkauf_rechnungseingaenge
            SET status = 'GEPRUEFT', checked_by = :user, checked_at = now(), updated_at = now()
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": row._mapping["id"], "user": user, "tenant_id": tenant_id},
    )
    db.commit()
    return {"message": "Rechnungseingang geprüft", "status": "GEPRUEFT"}


@router.post("/rechnungseingaenge/{rechnung_id}/freigeben")
async def rechnungseingang_freigeben(
    rechnung_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Setzt Status auf FREIGEGEBEN (nur aus GEPRUEFT). Speichert approved_by/approved_at."""
    row = db.execute(
        text("SELECT id, status FROM einkauf_rechnungseingaenge WHERE (id = :id OR rechnungs_nummer = :id) AND tenant_id = :tenant_id"),
        {"id": rechnung_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")
    status = (row._mapping.get("status") or "").upper()
    if status != "GEPRUEFT":
        raise HTTPException(
            status_code=400,
            detail=f"Freigeben nur möglich bei Status GEPRUEFT. Aktuell: {status}",
        )
    user = _get_audit_user(request)
    db.execute(
        text("""
            UPDATE einkauf_rechnungseingaenge
            SET status = 'FREIGEGEBEN', approved_by = :user, approved_at = now(), updated_at = now()
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": row._mapping["id"], "user": user, "tenant_id": tenant_id},
    )
    db.commit()
    return {"message": "Rechnungseingang freigegeben", "status": "FREIGEGEBEN"}


@router.post("/rechnungseingaenge/{rechnung_id}/verbuchen")
async def rechnungseingang_verbuchen(
    rechnung_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Setzt Status auf VERBUCHT (nur aus FREIGEGEBEN). Speichert posted_by/posted_at."""
    row = db.execute(
        text("SELECT id, status FROM einkauf_rechnungseingaenge WHERE (id = :id OR rechnungs_nummer = :id) AND tenant_id = :tenant_id"),
        {"id": rechnung_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")
    status = (row._mapping.get("status") or "").upper()
    if status != "FREIGEGEBEN":
        raise HTTPException(
            status_code=400,
            detail=f"Verbuchen nur möglich bei Status FREIGEGEBEN. Aktuell: {status}",
        )
    user = _get_audit_user(request)
    db.execute(
        text("""
            UPDATE einkauf_rechnungseingaenge
            SET status = 'VERBUCHT', posted_by = :user, posted_at = now(), updated_at = now()
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": row._mapping["id"], "user": user, "tenant_id": tenant_id},
    )
    db.commit()
    return {"message": "Rechnungseingang verbucht", "status": "VERBUCHT"}


@router.post("/rechnungseingaenge", status_code=201)
async def create_rechnungseingang(
    rechnung: schemas.RechnungseingangCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Erstellt neuen Rechnungseingang"""
    try:
        rechnung_id = uuid7()

        db.execute(
            text("""
                INSERT INTO einkauf_rechnungseingaenge (
                    id, rechnungs_nummer, lieferant_id, lieferant_name,
                    bestellung_id, wareneingang_id, rechnungs_datum,
                    faelligkeits_datum, netto_betrag, mwst_betrag, brutto_betrag,
                    waehrung, status, zahlungsreferenz, notizen, tenant_id
                ) VALUES (
                    :id, :nummer, :lid, :lname, :bid, :wid, :rdatum,
                    :fdatum, :netto, :mwst, :brutto,
                    :waehrung, :status, :zref, :notizen, :tenant_id
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
                "tenant_id": tenant_id,
            },
        )

        if rechnung.positionen:
            for pos in rechnung.positionen:
                pos_id = uuid7()
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
    except Exception:
        db.rollback()
        logger.exception("Rechnungseingang erstellen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen des Rechnungseingangs")


_RECHNUNGSEINGANG_UPDATABLE_COLS = frozenset({
    "lieferant_id", "lieferant_name", "bestellung_id", "wareneingang_id",
    "rechnungs_datum", "faelligkeits_datum", "netto_betrag", "mwst_betrag",
    "brutto_betrag", "zahlungsreferenz", "notizen", "status",
    "abgleich_ergebnis", "abweichungs_begruendung",
})


@router.put("/rechnungseingaenge/{rechnung_id}")
async def update_rechnungseingang(
    rechnung_id: str,
    rechnung: schemas.RechnungseingangUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Aktualisiert Rechnungseingang"""
    try:
        existing = db.execute(
            text("SELECT id FROM einkauf_rechnungseingaenge WHERE (id = :id OR rechnungs_nummer = :id) AND tenant_id = :tenant_id"),
            {"id": rechnung_id, "tenant_id": tenant_id},
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
                if db_col in _RECHNUNGSEINGANG_UPDATABLE_COLS:
                    update_data[db_col] = val

        if update_data:
            set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
            update_query = f"UPDATE einkauf_rechnungseingaenge SET {set_clause}, updated_at = now() WHERE id = :id AND tenant_id = :tenant_id"
            update_data["id"] = real_id
            update_data["tenant_id"] = tenant_id
            db.execute(text(update_query), update_data)

        db.commit()
        return {"message": "Rechnungseingang erfolgreich aktualisiert"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Rechnungseingang aktualisieren fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren des Rechnungseingangs")


@router.delete("/rechnungseingaenge/{rechnung_id}")
async def delete_rechnungseingang(
    rechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Loescht Rechnungseingang"""
    try:
        existing = db.execute(
            text("SELECT id FROM einkauf_rechnungseingaenge WHERE (id = :id OR rechnungs_nummer = :id) AND tenant_id = :tenant_id"),
            {"id": rechnung_id, "tenant_id": tenant_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")

        real_id = existing[0]
        db.execute(text("DELETE FROM einkauf_rechnungseingang_positionen WHERE rechnungseingang_id = :id"), {"id": real_id})
        db.execute(text("DELETE FROM einkauf_rechnungseingaenge WHERE id = :id AND tenant_id = :tenant_id"), {"id": real_id, "tenant_id": tenant_id})
        db.commit()
        return {"message": "Rechnungseingang erfolgreich geloescht"}

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.exception("Rechnungseingang löschen fehlgeschlagen")
        raise HTTPException(status_code=500, detail="Fehler beim Loeschen des Rechnungseingangs")
