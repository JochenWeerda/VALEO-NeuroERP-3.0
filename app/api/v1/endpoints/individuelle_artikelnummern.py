"""Individuelle Artikelnummern [INDIVART] — Kunden-/Lieferanten-spezifische Artikelnummern.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domains 06 CRM + 17 Artikelstamm):
  Individuelle Artikelnummern ermöglichen die Pflege von partner-spezifischen
  Artikelkennungen. Kunden oder Lieferanten verwenden ggf. eigene Artikelnummern,
  die auf interne Artikel gemappt werden.
  - Partner-Typ: kunden (VK), lieferanten (EK)
  - Individuelle-Artikel-Nr: externe Kennung des Partners
  - Zuordnung: interne Artikel-Nr + Partner-Nr → externe Kennung
  - Suche: Vorgang-Erfassung kann über externe Nummer gesucht werden

  SPA-Parameter steuern das Suchverhalten bei Artikelauswahl:
  - SPA 10: Individualpreise aktiv
  - SPA mit kunden-individueller Artikelnummernsuche
"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/artikel/individuelle-nummern",
                   tags=["Artikelstamm - Individuelle Artikelnummern"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class IndivArtikelNrCreate(BaseModel):
    artikel_nr: str
    partner_nr: str
    partner_typ: str = Field(default="kunden", pattern="^(kunden|lieferanten)$")
    indiv_artikel_nr: str = Field(..., max_length=50)
    indiv_bezeichnung: Optional[str] = None
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None


class IndivArtikelNrOut(BaseModel):
    id: str
    artikel_nr: str
    partner_nr: str
    partner_typ: str
    indiv_artikel_nr: str
    indiv_bezeichnung: Optional[str]
    gueltig_von: Optional[date]
    gueltig_bis: Optional[date]
    aktiv: bool
    created_at: datetime


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[IndivArtikelNrOut], summary="Individuelle nummern auflisten")
def list_individuelle_nummern(
    partner_nr: Optional[str] = Query(None),
    partner_typ: Optional[str] = Query(None, pattern="^(kunden|lieferanten)$"),
    artikel_nr: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.individuelle_artikelnummern WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if partner_nr:
        sql += " AND partner_nr = :pnr"
        params["pnr"] = partner_nr
    if partner_typ:
        sql += " AND partner_typ = :ptyp"
        params["ptyp"] = partner_typ
    if artikel_nr:
        sql += " AND artikel_nr = :anr"
        params["anr"] = artikel_nr
    sql += " ORDER BY artikel_nr, partner_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [IndivArtikelNrOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=IndivArtikelNrOut, status_code=201, summary="Individuelle nummer anlegen")
def create_individuelle_nummer(
    payload: IndivArtikelNrCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.individuelle_artikelnummern
        WHERE tenant_id = :tid AND artikel_nr = :anr AND partner_nr = :pnr AND partner_typ = :ptyp
    """), {
        "tid": tenant_id, "anr": payload.artikel_nr,
        "pnr": payload.partner_nr, "ptyp": payload.partner_typ,
    }).fetchone()
    if existing:
        raise HTTPException(409, "Individuelle Artikelnummer für diese Kombination bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.individuelle_artikelnummern
            (id, tenant_id, artikel_nr, partner_nr, partner_typ,
             indiv_artikel_nr, indiv_bezeichnung, gueltig_von, gueltig_bis)
        VALUES (:id, :tid, :anr, :pnr, :ptyp, :indiv, :ibez, :gvon, :gbis)
    """), {
        "id": new_id, "tid": tenant_id, "anr": payload.artikel_nr,
        "pnr": payload.partner_nr, "ptyp": payload.partner_typ,
        "indiv": payload.indiv_artikel_nr, "ibez": payload.indiv_bezeichnung,
        "gvon": payload.gueltig_von, "gbis": payload.gueltig_bis,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.individuelle_artikelnummern WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return IndivArtikelNrOut(**dict(row._mapping))


@router.get("/lookup", summary="Interne nummer lookup")
def lookup_interne_nummer(
    partner_nr: str = Query(...),
    indiv_artikel_nr: str = Query(...),
    partner_typ: str = Query(default="kunden", pattern="^(kunden|lieferanten)$"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Interne Artikelnummer aus externer Partnernummer ermitteln."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.individuelle_artikelnummern
        WHERE tenant_id = :tid AND partner_nr = :pnr AND partner_typ = :ptyp
          AND indiv_artikel_nr = :indiv AND aktiv = true
        LIMIT 1
    """), {
        "tid": tenant_id, "pnr": partner_nr,
        "ptyp": partner_typ, "indiv": indiv_artikel_nr,
    }).fetchone()
    if not row:
        raise HTTPException(404, "Keine interne Artikelnummer für diese externe Nummer gefunden.")
    return {"interne_artikel_nr": row.artikel_nr, "indiv_bezeichnung": row.indiv_bezeichnung}


@router.delete("/{indiv_id}", summary="Individuelle nummer löschen")
def delete_individuelle_nummer(
    indiv_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.individuelle_artikelnummern SET aktiv = false
        WHERE id = :id AND tenant_id = :tid
    """), {"id": indiv_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)
