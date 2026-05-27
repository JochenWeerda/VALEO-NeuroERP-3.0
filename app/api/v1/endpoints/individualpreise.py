"""Individualpreise [PRI/PRIE] — Kunden-/Lieferanten-spezifische Preise.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 07 Preise/Konditionen):
  Individualpreise [PRI/PRIE] sind artikel- und partnerspezifische Preise mit
  Gültigkeitszeitraum. Sie ergänzen die Listenpreise um individuelle Konditionen.
  Parameter:
  - Preis-Typ: VK (Verkauf) oder EK (Einkauf)
  - Artikel-Nr: Pflicht
  - Partner-Nr: optional (Kunden-Nr für VK, Lieferanten-Nr für EK)
  - Gültig von/bis: Zeitraum
  - Staffel-Menge: Preis ab dieser Menge (0 = Basispreis)
  - Währung: Standard EUR

  Suchreihenfolge bei Preisfindung:
  1. Artikel + Kunde + Datum + Menge (spezifischster Preis)
  2. Artikel + Datum + Menge (allgemeiner Individualpreis ohne Partner)
  3. Listenpreis als Fallback

  Steuerparameter SPA 10 aktiviert Individualpreise.
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

router = APIRouter(prefix="/preise/individualpreise",
                   tags=["Preise & Konditionen - Individualpreise"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class IndividualpreisCreate(BaseModel):
    preis_typ: str = Field(default="VK", pattern="^(VK|EK)$")
    artikel_nr: str
    partner_nr: Optional[str] = None
    gueltig_von: date
    gueltig_bis: Optional[date] = None
    preis_eur: Decimal = Field(..., gt=0)
    mengeneinheit: Optional[str] = None
    staffel_menge: Decimal = Field(default=Decimal("0"), ge=0)
    waehrung: str = Field(default="EUR", max_length=3)
    notiz: Optional[str] = None


class IndividualpreisOut(BaseModel):
    id: str
    preis_typ: str
    artikel_nr: str
    partner_nr: Optional[str]
    gueltig_von: date
    gueltig_bis: Optional[date]
    preis_eur: Decimal
    mengeneinheit: Optional[str]
    staffel_menge: Decimal
    waehrung: str
    notiz: Optional[str]
    created_at: datetime


class PreisLookupResult(BaseModel):
    artikel_nr: str
    partner_nr: Optional[str]
    preis_typ: str
    preis_eur: Decimal
    mengeneinheit: Optional[str]
    gueltig_von: date
    gueltig_bis: Optional[date]
    staffel_menge: Decimal
    quelle: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[IndividualpreisOut], summary="Individualpreise auflisten")
def list_individualpreise(
    preis_typ: Optional[str] = Query(None, pattern="^(VK|EK)$"),
    artikel_nr: Optional[str] = Query(None),
    partner_nr: Optional[str] = Query(None),
    gueltig_am: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.individualpreise WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if preis_typ:
        sql += " AND preis_typ = :pt"
        params["pt"] = preis_typ
    if artikel_nr:
        sql += " AND artikel_nr = :anr"
        params["anr"] = artikel_nr
    if partner_nr:
        sql += " AND partner_nr = :pnr"
        params["pnr"] = partner_nr
    if gueltig_am:
        sql += " AND gueltig_von <= :gam AND (gueltig_bis IS NULL OR gueltig_bis >= :gam)"
        params["gam"] = gueltig_am
    sql += " ORDER BY artikel_nr, partner_nr NULLS LAST, staffel_menge"
    rows = db.execute(text(sql), params).fetchall()
    return [IndividualpreisOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=IndividualpreisOut, status_code=201, summary="Individualpreis anlegen")
def create_individualpreis(
    payload: IndividualpreisCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if payload.gueltig_bis and payload.gueltig_bis < payload.gueltig_von:
        raise HTTPException(422, "gueltig_bis muss >= gueltig_von sein.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.individualpreise
            (id, tenant_id, preis_typ, artikel_nr, partner_nr,
             gueltig_von, gueltig_bis, preis_eur, mengeneinheit,
             staffel_menge, waehrung, notiz)
        VALUES (:id, :tid, :pt, :anr, :pnr,
                :gvon, :gbis, :preis, :me,
                :staffel, :whr, :notiz)
        ON CONFLICT (tenant_id, preis_typ, artikel_nr, partner_nr, gueltig_von, staffel_menge)
        DO UPDATE SET preis_eur = EXCLUDED.preis_eur,
                      gueltig_bis = EXCLUDED.gueltig_bis,
                      notiz = EXCLUDED.notiz
    """), {
        "id": new_id, "tid": tenant_id, "pt": payload.preis_typ,
        "anr": payload.artikel_nr, "pnr": payload.partner_nr,
        "gvon": payload.gueltig_von, "gbis": payload.gueltig_bis,
        "preis": payload.preis_eur, "me": payload.mengeneinheit,
        "staffel": payload.staffel_menge, "whr": payload.waehrung,
        "notiz": payload.notiz,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.individualpreise
        WHERE tenant_id = :tid AND preis_typ = :pt AND artikel_nr = :anr
          AND gueltig_von = :gvon AND staffel_menge = :staffel
          AND (partner_nr = :pnr OR (:pnr IS NULL AND partner_nr IS NULL))
    """), {
        "tid": tenant_id, "pt": payload.preis_typ, "anr": payload.artikel_nr,
        "gvon": payload.gueltig_von, "staffel": payload.staffel_menge,
        "pnr": payload.partner_nr,
    }).fetchone()
    return IndividualpreisOut(**dict(row._mapping))


@router.delete("/{preis_id}", summary="Individualpreis löschen",
    response_model=dict
)
def delete_individualpreis(
    preis_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        DELETE FROM domain_shared.individualpreise
        WHERE id = :id AND tenant_id = :tid
    """), {"id": preis_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


@router.get("/lookup", response_model=PreisLookupResult, summary="Lookup preis")
def preis_lookup(
    preis_typ: str = Query(..., pattern="^(VK|EK)$"),
    artikel_nr: str = Query(...),
    partner_nr: Optional[str] = Query(None),
    menge: Decimal = Query(default=Decimal("1")),
    datum: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Findet den passenden Individualpreis für Artikel+Partner+Menge+Datum.

    Suchreihenfolge: Artikel+Partner+Datum+Menge → Artikel+Datum+Menge.
    """
    check_datum = datum or date.today()

    def find_preis(with_partner: bool) -> Optional[dict]:
        partner_filter = "AND partner_nr = :pnr" if with_partner else "AND partner_nr IS NULL"
        # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        rows = db.execute(text(f"""
            SELECT * FROM domain_shared.individualpreise
            WHERE tenant_id = :tid AND preis_typ = :pt AND artikel_nr = :anr
              AND gueltig_von <= :datum
              AND (gueltig_bis IS NULL OR gueltig_bis >= :datum)
              AND staffel_menge <= :menge
              {partner_filter}
            ORDER BY staffel_menge DESC
            LIMIT 1
        """), {
            "tid": tenant_id, "pt": preis_typ, "anr": artikel_nr,
            "datum": check_datum, "menge": menge,
            **({"pnr": partner_nr} if with_partner else {}),
        }).fetchone()
        return dict(rows._mapping) if rows else None

    row = None
    quelle = "kein_preis"
    if partner_nr:
        row = find_preis(with_partner=True)
        if row:
            quelle = "artikel_partner"
    if not row:
        row = find_preis(with_partner=False)
        if row:
            quelle = "artikel_allgemein"

    if not row:
        raise HTTPException(404, "Kein Individualpreis für diese Kombination gefunden.")

    return PreisLookupResult(**{**row, "quelle": quelle})
