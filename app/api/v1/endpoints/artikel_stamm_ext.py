"""Artikelstamm-Erweiterungen: Folgeartikel, Inventurgruppen, Wiegungsgruppen.

Fachlicher Hintergrund (aus Referenz-ERP Wissensbasis, Domain 17):

  Folgeartikel: Wenn ein Artikel ausläuft oder umbenannt wird, wird ein
  Nachfolgeartikel hinterlegt. Bei der Vorgangserfassung kann automatisch
  auf den Folgeartikel gewechselt werden. Dies verhindert Fehleingaben bei
  ausgelaufenen Artikeln.

  Inventurgruppen: Artikel werden Inventurgruppen zugeordnet (z.B. Jahrlich,
  Halbjährlich, Rollierend). Die Inventurgruppe steuert, wann und wie oft
  ein Artikel inventiert wird.

  Wiegungsgruppen (Raffen/Aufteilen): Mehrere Wiegungen können zu einer
  Abrechnungseinheit zusammengefasst (gerafft) oder eine Wiegung auf
  mehrere Kontrakte/Partien aufgeteilt werden.
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

router = APIRouter(prefix="/artikel", tags=["Artikelstamm - Erweiterungen"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class FolgeartikelCreate(BaseModel):
    artikel_nr: str
    folge_artikel_nr: str
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None
    grund: Optional[str] = Field(None, description="Auslauf, Sortimentswechsel, Umbenennung")
    automatisch_ersetzen: bool = False


class FolgeartikelOut(BaseModel):
    id: str
    artikel_nr: str
    folge_artikel_nr: str
    gueltig_ab: Optional[date]
    gueltig_bis: Optional[date]
    grund: Optional[str]
    automatisch_ersetzen: bool
    aktiv: bool
    created_at: datetime


class InventurgruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    inventur_zyklus: Optional[str] = Field(None,
        description="jaehrlich, halbjaehrlich, quartalsweise, rollierend")
    naechste_inventur: Optional[date] = None


class InventurgruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    inventur_zyklus: Optional[str]
    naechste_inventur: Optional[date]
    aktiv: bool
    created_at: datetime


class WiegungsgruppeCreate(BaseModel):
    typ: str = Field(..., description="gerafft oder aufgeteilt")
    wiegeschein_ids: list[str] = Field(default_factory=list)
    kontrakt_nr: Optional[str] = None
    bemerkung: Optional[str] = None


class WiegungsgruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    typ: str
    wiegeschein_ids: Optional[list]
    gesamt_netto_kg: Optional[Decimal]
    kontrakt_nr: Optional[str]
    beleg_nr: Optional[str]
    status: str
    bemerkung: Optional[str]
    created_at: datetime


# ── Folgeartikel ──────────────────────────────────────────────────────────────

@router.get("/folgeartikel", response_model=list[FolgeartikelOut])
def list_folgeartikel(
    artikel_nr: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.artikel_folgeartikel
        WHERE tenant_id = :tid AND aktiv = true
    """
    params: dict = {"tid": tenant_id}
    if artikel_nr:
        sql += " AND artikel_nr = :artikel_nr"
        params["artikel_nr"] = artikel_nr
    sql += " ORDER BY artikel_nr, gueltig_ab"
    rows = db.execute(text(sql), params).fetchall()
    return [FolgeartikelOut(**dict(r._mapping)) for r in rows]


@router.get("/folgeartikel/{artikel_nr}/aktuell")
def get_aktueller_folgeartikel(
    artikel_nr: str,
    stichtag: Optional[date] = Query(None, description="Stichtag für Gültigkeit (default: heute)"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Aktuellen Folgeartikel für einen Artikel ermitteln."""
    check_date = stichtag or date.today()
    row = db.execute(text("""
        SELECT * FROM domain_shared.artikel_folgeartikel
        WHERE tenant_id = :tid AND artikel_nr = :art_nr AND aktiv = true
          AND (gueltig_ab IS NULL OR gueltig_ab <= :stichtag)
          AND (gueltig_bis IS NULL OR gueltig_bis >= :stichtag)
        ORDER BY gueltig_ab DESC NULLS LAST
        LIMIT 1
    """), {"tid": tenant_id, "art_nr": artikel_nr, "stichtag": check_date}).fetchone()
    if not row:
        return {"artikel_nr": artikel_nr, "folgeartikel": None,
                "hinweis": "Kein aktiver Folgeartikel vorhanden."}
    r = dict(row._mapping)
    return {
        "artikel_nr": artikel_nr,
        "folgeartikel": r["folge_artikel_nr"],
        "automatisch_ersetzen": r["automatisch_ersetzen"],
        "grund": r["grund"],
        "gueltig_ab": str(r["gueltig_ab"]) if r["gueltig_ab"] else None,
    }


@router.post("/folgeartikel", response_model=FolgeartikelOut, status_code=201)
def create_folgeartikel(
    payload: FolgeartikelCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if payload.artikel_nr == payload.folge_artikel_nr:
        raise HTTPException(422, "Artikel und Folgeartikel dürfen nicht identisch sein.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.artikel_folgeartikel
            (id, tenant_id, artikel_nr, folge_artikel_nr,
             gueltig_ab, gueltig_bis, grund, automatisch_ersetzen, aktiv)
        VALUES (:id, :tid, :art_nr, :folge_nr,
                :ab, :bis, :grund, :auto, true)
    """), {
        "id": new_id, "tid": tenant_id,
        "art_nr": payload.artikel_nr, "folge_nr": payload.folge_artikel_nr,
        "ab": payload.gueltig_ab, "bis": payload.gueltig_bis,
        "grund": payload.grund, "auto": payload.automatisch_ersetzen,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.artikel_folgeartikel WHERE id = :id
    """), {"id": new_id}).fetchone()
    return FolgeartikelOut(**dict(row._mapping))


@router.delete("/folgeartikel/{folgeartikel_id}")
def delete_folgeartikel(
    folgeartikel_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.artikel_folgeartikel
        SET aktiv = false WHERE id = :id AND tenant_id = :tid
    """), {"id": folgeartikel_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


# ── Inventurgruppen ───────────────────────────────────────────────────────────

@router.get("/inventurgruppen", response_model=list[InventurgruppeOut])
def list_inventurgruppen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.artikel_inventurgruppen
        WHERE tenant_id = :tid AND aktiv = true
        ORDER BY gruppe_nr
    """), {"tid": tenant_id}).fetchall()
    return [InventurgruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/inventurgruppen", response_model=InventurgruppeOut, status_code=201)
def create_inventurgruppe(
    payload: InventurgruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.artikel_inventurgruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Inventurgruppe {payload.gruppe_nr} existiert bereits.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.artikel_inventurgruppen
            (id, tenant_id, gruppe_nr, bezeichnung,
             inventur_zyklus, naechste_inventur, aktiv)
        VALUES (:id, :tid, :nr, :bez, :zyklus, :naechste, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr,
        "bez": payload.bezeichnung, "zyklus": payload.inventur_zyklus,
        "naechste": payload.naechste_inventur,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.artikel_inventurgruppen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return InventurgruppeOut(**dict(row._mapping))


@router.delete("/inventurgruppen/{gruppe_id}")
def delete_inventurgruppe(
    gruppe_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.artikel_inventurgruppen
        SET aktiv = false WHERE id = :id AND tenant_id = :tid
    """), {"id": gruppe_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


# ── Wiegungsgruppen (Raffen / Aufteilen) ─────────────────────────────────────

@router.get("/wiegungsgruppen", response_model=list[WiegungsgruppeOut])
def list_wiegungsgruppen(
    typ: Optional[str] = Query(None, description="gerafft oder aufgeteilt"),
    status: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.waage_wiegungsgruppen
        WHERE tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if typ:
        sql += " AND typ = :typ"
        params["typ"] = typ
    if status:
        sql += " AND status = :status"
        params["status"] = status
    sql += " ORDER BY created_at DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [WiegungsgruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/wiegungsgruppen", response_model=WiegungsgruppeOut, status_code=201)
def create_wiegungsgruppe(
    payload: WiegungsgruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Wiegungen raffen (zusammenfassen) oder aufteilen."""
    if payload.typ not in ("gerafft", "aufgeteilt"):
        raise HTTPException(422, "typ muss 'gerafft' oder 'aufgeteilt' sein.")

    new_id = uuid7()
    gruppe_nr = f"WG-{new_id[:8].upper()}"
    db.execute(text("""
        INSERT INTO domain_shared.waage_wiegungsgruppen
            (id, tenant_id, gruppe_nr, typ, wiegeschein_ids,
             kontrakt_nr, status, bemerkung)
        VALUES (:id, :tid, :gruppe_nr, :typ, :ids::jsonb,
                :ktr_nr, 'offen', :bem)
    """), {
        "id": new_id, "tid": tenant_id, "gruppe_nr": gruppe_nr,
        "typ": payload.typ,
        "ids": str(payload.wiegeschein_ids).replace("'", '"'),
        "ktr_nr": payload.kontrakt_nr, "bem": payload.bemerkung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.waage_wiegungsgruppen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return WiegungsgruppeOut(**dict(row._mapping))
