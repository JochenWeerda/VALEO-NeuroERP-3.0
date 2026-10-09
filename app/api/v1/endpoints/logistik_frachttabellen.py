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
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/logistik/frachttabellen",
                   tags=["Logistik - Frachttabellen & Zuordnungen"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class FrachttabelleCreate(BaseModel):
    tabelle_nr: str = Field(..., max_length=20)
    bezeichnung: str
    einheit: Optional[str] = Field(None, max_length=20,
                                   description="t, km, Palette, Stück")
    waehrung: str = Field(default="EUR", max_length=3)


class FrachttabelleOut(BaseModel):
    id: str
    tabelle_nr: str
    bezeichnung: str
    einheit: Optional[str]
    waehrung: str
    aktiv: bool
    created_at: datetime


class FrachttabellePositionCreate(BaseModel):
    ab_menge: Decimal = Field(..., ge=0,
                              description="Menge ab der dieser Satz gilt")
    frachtsatz_eur: Decimal = Field(..., ge=0)
    mindestfracht_eur: Optional[Decimal] = None


class FrachttabellePositionOut(BaseModel):
    id: str
    tabelle_nr: str
    ab_menge: Decimal
    frachtsatz_eur: Decimal
    mindestfracht_eur: Optional[Decimal]
    created_at: datetime


class FrachttabelleZuordnungCreate(BaseModel):
    frachtklasse: str = Field(..., max_length=20)
    frachtgruppe: str = Field(..., max_length=20)
    versandart: Optional[str] = Field(None, max_length=30)
    tabelle_nr: str
    sperre: bool = False
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None


class FrachttabelleZuordnungOut(BaseModel):
    id: str
    frachtklasse: str
    frachtgruppe: str
    versandart: Optional[str]
    tabelle_nr: str
    sperre: bool
    gueltig_ab: Optional[date]
    gueltig_bis: Optional[date]
    created_at: datetime


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


def insert_frachttabelle(
    db,
    *,
    tenant_id: str,
    tabelle_nr: str,
    bezeichnung: str,
    einheit: Optional[str],
    waehrung: str,
    commit: bool = True,
) -> dict:
    """Mandantengebundene Neuanlage; 409 bei Doppelnummer."""
    existing = db.execute(text("""
        SELECT id FROM domain_shared.logistik_frachttabellen
        WHERE tenant_id = :tid AND tabelle_nr = :nr
    """), {"tid": tenant_id, "nr": tabelle_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Frachttabelle {tabelle_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.logistik_frachttabellen
            (id, tenant_id, tabelle_nr, bezeichnung, einheit, waehrung, aktiv)
        VALUES (:id, :tid, :nr, :bez, :eh, :whr, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": tabelle_nr,
        "bez": bezeichnung, "eh": einheit, "whr": waehrung,
    })
    if commit:
        db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.logistik_frachttabellen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return dict(row._mapping)


@router.post("", response_model=FrachttabelleOut, status_code=201, summary="Frachttabelle anlegen")
def create_frachttabelle(
    payload: FrachttabelleCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    return FrachttabelleOut(**insert_frachttabelle(
        db,
        tenant_id=tenant_id,
        tabelle_nr=payload.tabelle_nr,
        bezeichnung=payload.bezeichnung,
        einheit=payload.einheit,
        waehrung=payload.waehrung,
        commit=True,
    ))


@router.post(
    "/actions/anlegen",
    response_model=MaskActionResult,
    summary="Frachttabelle anlegen als Masken-CommandEndpoint",
)
def action_anlegen(
    body: dict[str, Any] = Body(default_factory=dict),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    """CE fuer logistik/frachttabellen:anlegen — dryRun ohne INSERT."""
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="anlegen",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )

    tabelle_nr = str(payload.get("tabelle_nr") or "").strip()
    bezeichnung = str(payload.get("bezeichnung") or "").strip()
    einheit_raw = payload.get("einheit")
    einheit = str(einheit_raw).strip() if einheit_raw not in (None, "") else None
    waehrung = str(payload.get("waehrung") or "EUR").strip() or "EUR"
    errors: list[dict[str, Any]] = []
    if not tabelle_nr:
        errors.append({"field": "tabelle_nr", "message": "Pflichtfeld", "severity": "blocking"})
    if not bezeichnung:
        errors.append({"field": "bezeichnung", "message": "Pflichtfeld", "severity": "blocking"})
    if errors:
        return MaskActionResult(
            actionKey="anlegen",
            mode=mode,
            success=False,
            error=errors[0]["message"],
            validationErrors=errors,
        )

    preview = {
        "tabelle_nr": tabelle_nr,
        "bezeichnung": bezeichnung,
        "einheit": einheit,
        "waehrung": waehrung,
        "tenant_id": tenant_id,
    }

    existing = db.execute(text("""
        SELECT id FROM domain_shared.logistik_frachttabellen
        WHERE tenant_id = :tid AND tabelle_nr = :nr
    """), {"tid": tenant_id, "nr": tabelle_nr}).fetchone()
    db.rollback()
    if existing:
        return MaskActionResult(
            actionKey="anlegen",
            mode=mode,
            success=False,
            error=f"Frachttabelle {tabelle_nr} bereits vorhanden.",
            validationErrors=[{
                "field": "tabelle_nr",
                "message": f"Frachttabelle {tabelle_nr} bereits vorhanden.",
                "severity": "blocking",
            }],
        )

    if mode != "execute":
        return MaskActionResult(
            actionKey="anlegen",
            mode=mode,
            success=True,
            summary="Frachttabelle wuerde angelegt — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )

    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        row = insert_frachttabelle(
            db,
            tenant_id=tenant_id,
            tabelle_nr=tabelle_nr,
            bezeichnung=bezeichnung,
            einheit=einheit,
            waehrung=waehrung,
            commit=False,
        )
        entity_id = str(row["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="anlegen",
            entity_type="frachttabelle",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Frachttabelle {tabelle_nr} angelegt",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="logistik.frachttabelle.created",
            aggregate_id=entity_id,
            payload={"tabelle_nr": tabelle_nr, "tenant_id": tenant_id, "id": entity_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(
            actionKey="anlegen", mode=mode, success=False, error=detail,
        )
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        return MaskActionResult(
            actionKey="anlegen",
            mode=mode,
            success=False,
            error="Frachttabelle konnte nicht angelegt werden.",
        )

    return MaskActionResult(
        actionKey="anlegen",
        mode=mode,
        success=True,
        summary=f"Frachttabelle {tabelle_nr} angelegt.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


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
