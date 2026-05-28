"""Frachttabellen — Frachtkosten-Stammdaten und Zuordnungen.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 10 Logistik/Transport):
  Frachttabellen [FRA] definieren Frachtkosten in Staffelform (ab_menge → Frachtsatz).
  Frachttabellenzuordnungen verbinden Frachtklasse (aus Kundenstamm) mit
  Frachtgruppe (aus Artikelstamm) und Versandart zu einer konkreten Frachttabelle.

  Prozess der Frachtermittlung (SPA 29 aktiv):
  1. Frachtklasse des Kunden ermitteln
  2. Frachtgruppe des Artikels ermitteln
  3. Frachttabellen-Zuordnung [FTA] nach Frachtklasse x Frachtgruppe x Versandart suchen
  4. Frachtsatz aus Tabelle nach Liefermenge (Staffel) bestimmen

  Skontierung von Frachten (SPA 187), separate Steuer auf Frachten (SPA 331),
  kalkulatorische Frachten mit Skontierung (SPA 315) werden über SPA-Flags gesteuert.
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
from app.api.v1.schemas.logistik_frachttabellen_schemas import (
    FrachttabelleCreate,
    FrachttabelleOut,
    FrachttabellePositionCreate,
    FrachttabellePositionOut,
    FrachttabelleZuordnungCreate,
    FrachttabelleZuordnungOut,
)


router = APIRouter(prefix="/logistik/frachttabellen",
                   tags=["Logistik - Frachttabellen & Zuordnungen"])


# ── Schemas ───────────────────────────────────────────────────────────────────

# ── Frachttabellen ────────────────────────────────────────────────────────────

@router.get("", response_model=list[FrachttabelleOut], summary="Frachttabellen auflisten")
def list_frachttabellen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.logistik_frachttabellen
        WHERE tenant_id = :tid AND aktiv = true
        ORDER BY tabelle_nr
    """), {"tid": tenant_id}).fetchall()
    return [FrachttabelleOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=FrachttabelleOut, status_code=201, summary="Frachttabelle anlegen")
def create_frachttabelle(
    payload: FrachttabelleCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.logistik_frachttabellen
        WHERE tenant_id = :tid AND tabelle_nr = :nr
    """), {"tid": tenant_id, "nr": payload.tabelle_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Frachttabelle {payload.tabelle_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.logistik_frachttabellen
            (id, tenant_id, tabelle_nr, bezeichnung, einheit, waehrung, aktiv)
        VALUES (:id, :tid, :nr, :bez, :eh, :whr, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.tabelle_nr,
        "bez": payload.bezeichnung, "eh": payload.einheit, "whr": payload.waehrung,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.logistik_frachttabellen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return FrachttabelleOut(**dict(row._mapping))


@router.delete("/{tabelle_nr}", summary="Frachttabelle löschen",
    response_model=None
)
def delete_frachttabelle(
    tabelle_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.logistik_frachttabellen SET aktiv = false
        WHERE tenant_id = :tid AND tabelle_nr = :nr
    """), {"tid": tenant_id, "nr": tabelle_nr})
    db.commit()
    return Response(status_code=204)


# ── Positionen (Staffelwerte) ─────────────────────────────────────────────────

@router.get("/{tabelle_nr}/positionen",
            response_model=list[FrachttabellePositionOut], summary="Positionen auflisten")
def list_positionen(
    tabelle_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.logistik_frachttabellen_positionen
        WHERE tenant_id = :tid AND tabelle_nr = :nr
        ORDER BY ab_menge
    """), {"tid": tenant_id, "nr": tabelle_nr}).fetchall()
    return [FrachttabellePositionOut(**dict(r._mapping)) for r in rows]


@router.post("/{tabelle_nr}/positionen",
             response_model=FrachttabellePositionOut, status_code=201, summary="Position anlegen")
def create_position(
    tabelle_nr: str,
    payload: FrachttabellePositionCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    tabelle = db.execute(text("""
        SELECT id FROM domain_shared.logistik_frachttabellen
        WHERE tenant_id = :tid AND tabelle_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": tabelle_nr}).fetchone()
    if not tabelle:
        raise HTTPException(404, "Frachttabelle nicht gefunden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.logistik_frachttabellen_positionen
            (id, tenant_id, tabelle_nr, ab_menge, frachtsatz_eur, mindestfracht_eur)
        VALUES (:id, :tid, :nr, :ab, :satz, :mind)
    """), {
        "id": new_id, "tid": tenant_id, "nr": tabelle_nr,
        "ab": payload.ab_menge, "satz": payload.frachtsatz_eur,
        "mind": payload.mindestfracht_eur,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.logistik_frachttabellen_positionen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return FrachttabellePositionOut(**dict(row._mapping))


@router.delete("/{tabelle_nr}/positionen/{pos_id}", summary="Position löschen",
    response_model=None
)
def delete_position(
    tabelle_nr: str,
    pos_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        DELETE FROM domain_shared.logistik_frachttabellen_positionen
        WHERE id = :id AND tenant_id = :tid AND tabelle_nr = :nr
    """), {"id": pos_id, "tid": tenant_id, "nr": tabelle_nr})
    db.commit()
    return Response(status_code=204)


# ── Frachttabellen-Zuordnungen ────────────────────────────────────────────────

@router.get("/zuordnungen", response_model=list[FrachttabelleZuordnungOut], summary="Zuordnungen auflisten")
def list_zuordnungen(
    frachtklasse: Optional[str] = Query(None),
    frachtgruppe: Optional[str] = Query(None),
    stichtag: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.logistik_frachttabellen_zuordnung
        WHERE tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if frachtklasse:
        sql += " AND frachtklasse = :fkl"
        params["fkl"] = frachtklasse
    if frachtgruppe:
        sql += " AND frachtgruppe = :fgrp"
        params["fgrp"] = frachtgruppe
    if stichtag:
        sql += " AND (gueltig_ab IS NULL OR gueltig_ab <= :s) AND (gueltig_bis IS NULL OR gueltig_bis >= :s)"
        params["s"] = stichtag
    sql += " ORDER BY frachtklasse, frachtgruppe"
    rows = db.execute(text(sql), params).fetchall()
    return [FrachttabelleZuordnungOut(**dict(r._mapping)) for r in rows]


@router.post("/zuordnungen",
             response_model=FrachttabelleZuordnungOut, status_code=201, summary="Zuordnung anlegen")
def create_zuordnung(
    payload: FrachttabelleZuordnungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.logistik_frachttabellen_zuordnung
            (id, tenant_id, frachtklasse, frachtgruppe, versandart,
             tabelle_nr, sperre, gueltig_ab, gueltig_bis)
        VALUES (:id, :tid, :fkl, :fgrp, :vart, :tnr, :sperre, :von, :bis)
    """), {
        "id": new_id, "tid": tenant_id, "fkl": payload.frachtklasse,
        "fgrp": payload.frachtgruppe, "vart": payload.versandart,
        "tnr": payload.tabelle_nr, "sperre": payload.sperre,
        "von": payload.gueltig_ab, "bis": payload.gueltig_bis,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.logistik_frachttabellen_zuordnung WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return FrachttabelleZuordnungOut(**dict(row._mapping))


@router.delete("/zuordnungen/{zuordnung_id}", summary="Zuordnung löschen",
    response_model=None
)
def delete_zuordnung(
    zuordnung_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        DELETE FROM domain_shared.logistik_frachttabellen_zuordnung
        WHERE id = :id AND tenant_id = :tid
    """), {"id": zuordnung_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


@router.get("/zuordnungen/lookup", summary="Frachttabelle lookup",
    response_model=None
)
def lookup_frachttabelle(
    frachtklasse: str,
    frachtgruppe: str,
    versandart: Optional[str] = Query(None),
    menge: Optional[Decimal] = Query(None),
    stichtag: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Frachtsatz für gegebene Frachtklasse x Frachtgruppe x Versandart ermitteln."""
    check_date = stichtag or date.today()
    sql = """
        SELECT z.tabelle_nr
        FROM domain_shared.logistik_frachttabellen_zuordnung z
        WHERE z.tenant_id = :tid AND z.frachtklasse = :fkl AND z.frachtgruppe = :fgrp
          AND z.sperre = false
          AND (z.gueltig_ab IS NULL OR z.gueltig_ab <= :s)
          AND (z.gueltig_bis IS NULL OR z.gueltig_bis >= :s)
    """
    params: dict = {"tid": tenant_id, "fkl": frachtklasse,
                    "fgrp": frachtgruppe, "s": check_date}
    if versandart:
        sql += " AND (z.versandart IS NULL OR z.versandart = :vart)"
        params["vart"] = versandart
    sql += " ORDER BY z.versandart DESC NULLS LAST LIMIT 1"
    zuordnung = db.execute(text(sql), params).fetchone()
    if not zuordnung:
        return {"frachtsatz_eur": None, "gefunden": False,
                "hinweis": "Keine Frachttabellen-Zuordnung gefunden."}

    tabelle_nr = zuordnung.tabelle_nr
    pos_sql = """
        SELECT frachtsatz_eur, mindestfracht_eur, ab_menge
        FROM domain_shared.logistik_frachttabellen_positionen
        WHERE tenant_id = :tid AND tabelle_nr = :tnr
    """
    pos_params: dict = {"tid": tenant_id, "tnr": tabelle_nr}
    if menge is not None:
        pos_sql += " AND ab_menge <= :menge"
        pos_params["menge"] = menge
    pos_sql += " ORDER BY ab_menge DESC LIMIT 1"
    pos = db.execute(text(pos_sql), pos_params).fetchone()
    if not pos:
        return {"frachtsatz_eur": None, "tabelle_nr": tabelle_nr, "gefunden": False,
                "hinweis": "Keine Staffelposition für diese Menge."}

    p = dict(pos._mapping)
    frachtsatz = float(p["frachtsatz_eur"])
    if menge is not None:
        frachtkost = frachtsatz * float(menge)
        if p.get("mindestfracht_eur"):
            frachtkost = max(frachtkost, float(p["mindestfracht_eur"]))
    else:
        frachtkost = None

    return {
        "tabelle_nr": tabelle_nr,
        "frachtsatz_eur": frachtsatz,
        "frachtkosten_gesamt_eur": frachtkost,
        "ab_menge": float(p["ab_menge"]),
        "gefunden": True,
    }
