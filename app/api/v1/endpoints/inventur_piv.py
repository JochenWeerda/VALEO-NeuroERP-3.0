"""Permanente Inventur (PIV) — Rollierender Bestandsabschluss.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 08 Lager):
  Die permanente Inventur (PIV) ersetzt die jährliche Stichtagsinventur durch
  rollierende Einzelzählungen je Artikel/Lagerplatz. Artikel werden über das
  Jahr verteilt gezählt, sobald sie ihren Inventurgruppen-Zyklus erreicht haben.

  PIV-Belege können Partien ignorieren (SPA 1083 / Permanente Inventur
  Bewertungsverhalten). Zählmenge wird auch vor der Bewertung angezeigt.

  Prozess: Abschluss anlegen → Positionen erfassen → Differenzen prüfen →
           Abschluss buchen (Bestand korrigieren)
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.inventur_piv_schemas import InventurPivOut


router = APIRouter(prefix="/inventur/piv", tags=["Lager - Permanente Inventur (PIV)"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class PIVZaehlmenge(BaseModel):
    zaehlmenge: Decimal
    ignoriert: bool = False

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[PIVAbschlussOut], summary="Piv abschluesse auflisten")
def list_piv_abschluesse(
    status: Optional[str] = Query(None),
    lager_nr: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.inventur_piv_abschluesse
        WHERE tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if status:
        sql += " AND status = :status"
        params["status"] = status
    if lager_nr:
        sql += " AND lager_nr = :lager_nr"
        params["lager_nr"] = lager_nr
    sql += " ORDER BY abschluss_datum DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [PIVAbschlussOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=PIVAbschlussOut, status_code=201, summary="Piv abschluss anlegen")
def create_piv_abschluss(
    payload: PIVAbschlussCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Neuen PIV-Abschluss eröffnen."""
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.inventur_piv_abschluesse
            (id, tenant_id, abschluss_datum, inventurgruppe_nr,
             lager_nr, status, anzahl_positionen, bemerkung)
        VALUES (:id, :tid, :datum, :inv_grp, :lager, 'offen', 0, :bem)
    """), {
        "id": new_id, "tid": tenant_id,
        "datum": payload.abschluss_datum,
        "inv_grp": payload.inventurgruppe_nr,
        "lager": payload.lager_nr,
        "bem": payload.bemerkung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.inventur_piv_abschluesse WHERE id = :id
    """), {"id": new_id}).fetchone()
    return PIVAbschlussOut(**dict(row._mapping))


@router.post("/{abschluss_id}/positionen",
             response_model=PIVPositionOut, status_code=201, summary="Piv position hinzufügen")
def add_piv_position(
    abschluss_id: str,
    payload: PIVPositionCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Artikel-Position zur Inventur hinzufügen."""
    abschluss = db.execute(text("""
        SELECT status FROM domain_shared.inventur_piv_abschluesse
        WHERE id = :id AND tenant_id = :tid
    """), {"id": abschluss_id, "tid": tenant_id}).fetchone()
    if not abschluss:
        raise HTTPException(404, "PIV-Abschluss nicht gefunden.")
    if abschluss.status == "abgeschlossen":
        raise HTTPException(409, "Abgeschlossene Inventuren können nicht mehr bearbeitet werden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.inventur_piv_positionen
            (id, tenant_id, abschluss_id, artikel_nr, lagerplatz,
             buchbestand, bewertungspreis_eur, erfasst, ignoriert)
        VALUES (:id, :tid, :abschluss_id, :art_nr, :lagerplatz,
                :buchbestand, :bewertung, false, false)
    """), {
        "id": new_id, "tid": tenant_id, "abschluss_id": abschluss_id,
        "art_nr": payload.artikel_nr, "lagerplatz": payload.lagerplatz,
        "buchbestand": payload.buchbestand, "bewertung": payload.bewertungspreis_eur,
    })
    # Positionszähler aktualisieren
    db.execute(text("""
        UPDATE domain_shared.inventur_piv_abschluesse
        SET anzahl_positionen = anzahl_positionen + 1
        WHERE id = :id
    """), {"id": abschluss_id})
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.inventur_piv_positionen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return PIVPositionOut(**dict(row._mapping))


@router.get("/{abschluss_id}/positionen", response_model=list[PIVPositionOut], summary="Piv positionen auflisten")
def list_piv_positionen(
    abschluss_id: str,
    nur_nicht_erfasst: bool = Query(False),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.inventur_piv_positionen
        WHERE abschluss_id = :id AND tenant_id = :tid
    """
    params: dict = {"id": abschluss_id, "tid": tenant_id}
    if nur_nicht_erfasst:
        sql += " AND erfasst = false AND ignoriert = false"
    sql += " ORDER BY artikel_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [PIVPositionOut(**dict(r._mapping)) for r in rows]


@router.patch("/{abschluss_id}/positionen/{pos_id}/zaehlen",
              response_model=PIVPositionOut, summary="Zaehlen")
def zaehlen(
    abschluss_id: str,
    pos_id: str,
    payload: PIVZaehlmenge,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zählmenge für eine Inventurposition erfassen.

    Die Differenz (Zählmenge - Buchbestand) und der Differenzwert werden
    automatisch berechnet.
    """
    pos = db.execute(text("""
        SELECT * FROM domain_shared.inventur_piv_positionen
        WHERE id = :id AND abschluss_id = :abschluss_id AND tenant_id = :tid
    """), {"id": pos_id, "abschluss_id": abschluss_id, "tid": tenant_id}).fetchone()
    if not pos:
        raise HTTPException(404, "PIV-Position nicht gefunden.")

    p = dict(pos._mapping)
    differenz = payload.zaehlmenge - p["buchbestand"]
    bewertung = p.get("bewertungspreis_eur") or Decimal("0")
    differenzwert = (differenz * bewertung).quantize(Decimal("0.01")) if bewertung else None

    db.execute(text("""
        UPDATE domain_shared.inventur_piv_positionen
        SET zaehlmenge = :zaehl, differenz = :diff,
            differenzwert_eur = :diffwert,
            erfasst = true, ignoriert = :ignoriert
        WHERE id = :id
    """), {
        "zaehl": payload.zaehlmenge, "diff": differenz,
        "diffwert": differenzwert, "ignoriert": payload.ignoriert,
        "id": pos_id,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.inventur_piv_positionen WHERE id = :id
    """), {"id": pos_id}).fetchone()
    return PIVPositionOut(**dict(row._mapping))


@router.post("/{abschluss_id}/abschliessen", response_model=PIVAbschlussOut, summary="Abschliessen")
def abschliessen(
    abschluss_id: str,
    abgeschlossen_von: Optional[str] = None,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """PIV-Abschluss finalisieren — Differenzen festschreiben.

    Fachlich: Nach dem Abschluss werden die Bestandsdifferenzen in den
    Buchbestand übernommen. Ignorierte PIV-Belege werden nicht gebucht.
    """
    abschluss = db.execute(text("""
        SELECT * FROM domain_shared.inventur_piv_abschluesse
        WHERE id = :id AND tenant_id = :tid
    """), {"id": abschluss_id, "tid": tenant_id}).fetchone()
    if not abschluss:
        raise HTTPException(404)
    if abschluss.status == "abgeschlossen":
        raise HTTPException(409, "PIV-Abschluss ist bereits abgeschlossen.")

    # Gesamtdifferenzwert berechnen
    result = db.execute(text("""
        SELECT COALESCE(SUM(differenzwert_eur), 0) as gesamt_diff
        FROM domain_shared.inventur_piv_positionen
        WHERE abschluss_id = :id AND NOT ignoriert
    """), {"id": abschluss_id}).fetchone()

    db.execute(text("""
        UPDATE domain_shared.inventur_piv_abschluesse
        SET status = 'abgeschlossen',
            abgeschlossen_von = :von,
            abgeschlossen_am = now(),
            differenzwert_eur = :diffwert
        WHERE id = :id
    """), {
        "id": abschluss_id,
        "von": abgeschlossen_von or "System",
        "diffwert": result.gesamt_diff,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.inventur_piv_abschluesse WHERE id = :id
    """), {"id": abschluss_id}).fetchone()
    return PIVAbschlussOut(**dict(row._mapping))


@router.get("/{abschluss_id}/differenzliste", summary="Differenzliste",
    response_model=InventurPivOut
)
def differenzliste(
    abschluss_id: str,
    nur_mit_differenz: bool = Query(True),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Differenzliste: Artikel mit Abweichung zwischen Buch- und Zählbestand."""
    sql = """
        SELECT artikel_nr, lagerplatz, buchbestand, zaehlmenge,
               differenz, bewertungspreis_eur, differenzwert_eur, ignoriert
        FROM domain_shared.inventur_piv_positionen
        WHERE abschluss_id = :id AND tenant_id = :tid AND erfasst = true
    """
    params: dict = {"id": abschluss_id, "tid": tenant_id}
    if nur_mit_differenz:
        sql += " AND differenz != 0 AND NOT ignoriert"
    sql += " ORDER BY artikel_nr"
    rows = db.execute(text(sql), params).fetchall()
    items = [dict(r._mapping) for r in rows]
    return {
        "abschluss_id": abschluss_id,
        "anzahl_positionen_mit_differenz": len(items),
        "gesamt_differenzwert_eur": sum(
            float(i["differenzwert_eur"] or 0) for i in items
        ),
        "positionen": items,
    }
