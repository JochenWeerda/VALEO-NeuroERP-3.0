"""Warengruppen 3-stufig — Hauptwarengruppe / Oberwarengruppe / Warengruppe.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 15 Compliance/Qualität):
  Warengruppen dienen der inhaltlichen Gliederung des Artikelstamms in
  Auswertungen und Selektionen. Dreistufiges hierarchisches Konzept:
  - Hauptwarengruppe: oberste Ebene (z.B. "Getreide", "Düngemittel")
  - Oberwarengruppe: mittlere Ebene (z.B. "Brotgetreide", "Futtergetreide")
  - Warengruppe: unterste Ebene (z.B. "Weizen A", "Gerste")

  Beziehungen sind eindeutig: Artikel → Warengruppe → Oberwarengruppe →
  Hauptwarengruppe. Erfassung in dieser Reihenfolge.

  Verwendung: Artikelstamm, Auswertungen/Selektion, Preisfindung, Statistik.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.warengruppen_schemas import (
    HauptwarengruppeCreate,
    HauptwarengruppeOut,
    OberwarengruppeCreate,
    OberwarengruppeOut,
    WarengruppeCreate,
    WarengruppeHierarchieOut,
    WarengruppeOut,
)


router = APIRouter(prefix="/stammdaten/warengruppen",
                   tags=["Stammdaten - Warengruppen"])


# ── Schemas ───────────────────────────────────────────────────────────────────

# ── Hauptwarengruppen ─────────────────────────────────────────────────────────

@router.get("/haupt", response_model=list[HauptwarengruppeOut], summary="Hauptwarengruppen auflisten")
def list_hauptwarengruppen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.hauptwarengruppen
        WHERE tenant_id = :tid AND aktiv = true ORDER BY gruppe_nr
    """), {"tid": tenant_id}).fetchall()
    return [HauptwarengruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/haupt", response_model=HauptwarengruppeOut, status_code=201, summary="Hauptwarengruppe anlegen")
def create_hauptwarengruppe(
    payload: HauptwarengruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.hauptwarengruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone():
        raise HTTPException(409, f"Hauptwarengruppe {payload.gruppe_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.hauptwarengruppen (id, tenant_id, gruppe_nr, bezeichnung)
        VALUES (:id, :tid, :nr, :bez)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr, "bez": payload.bezeichnung})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.hauptwarengruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return HauptwarengruppeOut(**dict(row._mapping))


@router.put("/haupt/{gruppe_nr}", response_model=HauptwarengruppeOut, summary="Hauptwarengruppe aktualisieren")
def update_hauptwarengruppe(
    gruppe_nr: str,
    payload: HauptwarengruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    result = db.execute(text("""
        UPDATE domain_shared.hauptwarengruppen SET bezeichnung = :bez
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND aktiv = true
    """), {"bez": payload.bezeichnung, "tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, f"Hauptwarengruppe {gruppe_nr} nicht gefunden.")
    row = db.execute(text("""
        SELECT * FROM domain_shared.hauptwarengruppen WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr}).fetchone()
    return HauptwarengruppeOut(**dict(row._mapping))


@router.delete("/haupt/{gruppe_nr}", summary="Hauptwarengruppe löschen",
    response_model=None
)
def delete_hauptwarengruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.hauptwarengruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)


# ── Oberwarengruppen ──────────────────────────────────────────────────────────

@router.get("/ober", response_model=list[OberwarengruppeOut], summary="Oberwarengruppen auflisten")
def list_oberwarengruppen(
    haupt_id: Optional[str] = None,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.oberwarengruppen WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if haupt_id:
        sql += " AND haupt_id = :hid"
        params["hid"] = haupt_id
    sql += " ORDER BY gruppe_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [OberwarengruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/ober", response_model=OberwarengruppeOut, status_code=201, summary="Oberwarengruppe anlegen")
def create_oberwarengruppe(
    payload: OberwarengruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if not db.execute(text("""
        SELECT id FROM domain_shared.hauptwarengruppen
        WHERE id = :hid AND tenant_id = :tid
    """), {"hid": payload.haupt_id, "tid": tenant_id}).fetchone():
        raise HTTPException(404, "Hauptwarengruppe nicht gefunden.")
    if db.execute(text("""
        SELECT id FROM domain_shared.oberwarengruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone():
        raise HTTPException(409, f"Oberwarengruppe {payload.gruppe_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.oberwarengruppen (id, tenant_id, gruppe_nr, bezeichnung, haupt_id)
        VALUES (:id, :tid, :nr, :bez, :hid)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr,
           "bez": payload.bezeichnung, "hid": payload.haupt_id})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.oberwarengruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return OberwarengruppeOut(**dict(row._mapping))


@router.put("/ober/{gruppe_nr}", response_model=OberwarengruppeOut, summary="Oberwarengruppe aktualisieren")
def update_oberwarengruppe(
    gruppe_nr: str,
    payload: OberwarengruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    result = db.execute(text("""
        UPDATE domain_shared.oberwarengruppen SET bezeichnung = :bez, haupt_id = :hid
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND aktiv = true
    """), {"bez": payload.bezeichnung, "hid": payload.haupt_id, "tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, f"Oberwarengruppe {gruppe_nr} nicht gefunden.")
    row = db.execute(text("""
        SELECT * FROM domain_shared.oberwarengruppen WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr}).fetchone()
    return OberwarengruppeOut(**dict(row._mapping))


@router.delete("/ober/{gruppe_nr}", summary="Oberwarengruppe löschen",
    response_model=None
)
def delete_oberwarengruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.oberwarengruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)


# ── Warengruppen ──────────────────────────────────────────────────────────────

@router.get("", response_model=list[WarengruppeOut], summary="Warengruppen auflisten")
def list_warengruppen(
    ober_id: Optional[str] = None,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.warengruppen WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if ober_id:
        sql += " AND ober_id = :oid"
        params["oid"] = ober_id
    sql += " ORDER BY gruppe_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [WarengruppeOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=WarengruppeOut, status_code=201, summary="Warengruppe anlegen")
def create_warengruppe(
    payload: WarengruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if not db.execute(text("""
        SELECT id FROM domain_shared.oberwarengruppen
        WHERE id = :oid AND tenant_id = :tid
    """), {"oid": payload.ober_id, "tid": tenant_id}).fetchone():
        raise HTTPException(404, "Oberwarengruppe nicht gefunden.")
    if db.execute(text("""
        SELECT id FROM domain_shared.warengruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone():
        raise HTTPException(409, f"Warengruppe {payload.gruppe_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.warengruppen (id, tenant_id, gruppe_nr, bezeichnung, ober_id)
        VALUES (:id, :tid, :nr, :bez, :oid)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr,
           "bez": payload.bezeichnung, "oid": payload.ober_id})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.warengruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return WarengruppeOut(**dict(row._mapping))


@router.put("/{gruppe_nr}", response_model=WarengruppeOut, summary="Warengruppe aktualisieren")
def update_warengruppe(
    gruppe_nr: str,
    payload: WarengruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    result = db.execute(text("""
        UPDATE domain_shared.warengruppen SET bezeichnung = :bez, ober_id = :oid
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND aktiv = true
    """), {"bez": payload.bezeichnung, "oid": payload.ober_id, "tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, f"Warengruppe {gruppe_nr} nicht gefunden.")
    row = db.execute(text("""
        SELECT * FROM domain_shared.warengruppen WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr}).fetchone()
    return WarengruppeOut(**dict(row._mapping))


@router.delete("/{gruppe_nr}", summary="Warengruppe löschen",
    response_model=None
)
def delete_warengruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.warengruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)


@router.get("/{gruppe_nr}/hierarchie", response_model=WarengruppeHierarchieOut, summary="Warengruppe hierarchie abrufen")
def get_warengruppe_hierarchie(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Gibt Warengruppe mit vollständiger Hierarchie zurück."""
    wg = db.execute(text("""
        SELECT * FROM domain_shared.warengruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr}).fetchone()
    if not wg:
        raise HTTPException(404, "Warengruppe nicht gefunden.")
    ow = db.execute(text(
        "SELECT * FROM domain_shared.oberwarengruppen WHERE id = :id"
    ), {"id": wg.ober_id}).fetchone()
    hw = db.execute(text(
        "SELECT * FROM domain_shared.hauptwarengruppen WHERE id = :id"
    ), {"id": ow.haupt_id}).fetchone()
    return WarengruppeHierarchieOut(
        warengruppe=WarengruppeOut(**dict(wg._mapping)),
        oberwarengruppe=OberwarengruppeOut(**dict(ow._mapping)),
        hauptwarengruppe=HauptwarengruppeOut(**dict(hw._mapping)),
    )
