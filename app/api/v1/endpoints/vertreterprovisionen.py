"""Vertreterprovisionsgruppen und -staffeln — Provisionsabrechnung Außendienst.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 02 WaWi/Auftrag):
  Vertreterprovisionsgruppen definieren, wie ein Vertreter an Umsätzen beteiligt
  wird: fixer Prozentsatz, Staffelprovision nach OPT-Preis oder nach Preis+ZuAB.
  Vertreterprovisionsstaffeln legen die Staffelzeilen für Staffel-Provisionstypen fest.

  Provisionstypen:
  - fix: Fester Prozentsatz vom Umsatz
  - staffel_optpreis: Staffelprovision auf OPT-Preis-Basis
  - staffel_preis_zuab: Staffelprovision auf (Preis + Zu-/Abschläge)-Basis

  Eine Vertreterklasse verknüpft Vertreter mit Provisionsgruppe.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.vertreterprovisionen_schemas import (
    ProvisionsGruppeCreate,
    ProvisionsGruppeOut,
    ProvisionsStaffelCreate,
    ProvisionsStaffelOut,
    ProvisionsStaffelZeileCreate,
    ProvisionsStaffelZeileOut,
)


router = APIRouter(prefix="/crm/vertreter/provisionen",
                   tags=["CRM - Vertreterprovisionen"])

GUELTIGE_PROVISIONSTYPEN = {"fix", "staffel_optpreis", "staffel_preis_zuab"}
GUELTIGE_RICHTUNG = {"ek", "vk"}


# ── Schemas ───────────────────────────────────────────────────────────────────

# ── Provisionsgruppen CRUD ────────────────────────────────────────────────────

@router.get("/gruppen", response_model=list[ProvisionsGruppeOut], summary="Provisionsgruppen auflisten")
def list_provisionsgruppen(
    richtung: Optional[str] = None,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.vertreter_provisionsgruppen
        WHERE tenant_id = :tid AND aktiv = true
    """
    params: dict = {"tid": tenant_id}
    if richtung:
        sql += " AND richtung = :r"
        params["r"] = richtung
    sql += " ORDER BY gruppe_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [ProvisionsGruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/gruppen", response_model=ProvisionsGruppeOut, status_code=201, summary="Provisionsgruppe anlegen")
def create_provisionsgruppe(
    payload: ProvisionsGruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.vertreter_provisionsgruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND richtung = :r
    """), {"tid": tenant_id, "nr": payload.gruppe_nr, "r": payload.richtung}).fetchone():
        raise HTTPException(409, f"Provisionsgruppe {payload.gruppe_nr}/{payload.richtung} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.vertreter_provisionsgruppen
            (id, tenant_id, gruppe_nr, bezeichnung, richtung, provisionstyp, provisionssatz)
        VALUES (:id, :tid, :nr, :bez, :r, :pt, :ps)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr, "bez": payload.bezeichnung,
        "r": payload.richtung, "pt": payload.provisionstyp, "ps": payload.provisionssatz,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.vertreter_provisionsgruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ProvisionsGruppeOut(**dict(row._mapping))


@router.delete("/gruppen/{gruppe_nr}", summary="Provisionsgruppe löschen",
    response_model=None
)
def delete_provisionsgruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.vertreter_provisionsgruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)


# ── Provisionsstaffeln CRUD ───────────────────────────────────────────────────

@router.get("/staffeln", response_model=list[ProvisionsStaffelOut], summary="Provisionsstaffeln auflisten")
def list_provisionsstaffeln(
    gruppe_id: Optional[str] = None,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT s.* FROM domain_shared.vertreter_provisionsstaffeln s
        JOIN domain_shared.vertreter_provisionsgruppen g ON g.id = s.gruppe_id
        WHERE g.tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if gruppe_id:
        sql += " AND s.gruppe_id = :gid"
        params["gid"] = gruppe_id
    sql += " ORDER BY s.created_at DESC"
    staffeln = db.execute(text(sql), params).fetchall()
    result = []
    for s in staffeln:
        zeilen = db.execute(text("""
            SELECT * FROM domain_shared.vertreter_staffel_zeilen
            WHERE staffel_id = :sid ORDER BY zeile_nr
        """), {"sid": s.id}).fetchall()
        staffel_dict = dict(s._mapping)
        staffel_dict["zeilen"] = [ProvisionsStaffelZeileOut(**dict(z._mapping)) for z in zeilen]
        result.append(ProvisionsStaffelOut(**staffel_dict))
    return result


@router.post("/staffeln", response_model=ProvisionsStaffelOut, status_code=201, summary="Provisionsstaffel anlegen")
def create_provisionsstaffel(
    payload: ProvisionsStaffelCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if not db.execute(text("""
        SELECT id FROM domain_shared.vertreter_provisionsgruppen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": payload.gruppe_id, "tid": tenant_id}).fetchone():
        raise HTTPException(404, "Provisionsgruppe nicht gefunden.")
    staffel_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.vertreter_provisionsstaffeln (id, gruppe_id, vertreterklasse)
        VALUES (:id, :gid, :vk)
    """), {"id": staffel_id, "gid": payload.gruppe_id, "vk": payload.vertreterklasse})
    for z in payload.zeilen:
        db.execute(text("""
            INSERT INTO domain_shared.vertreter_staffel_zeilen
                (id, staffel_id, zeile_nr, ab_wert, provisionssatz)
            VALUES (:id, :sid, :zn, :av, :ps)
        """), {
            "id": uuid7(), "sid": staffel_id, "zn": z.zeile_nr,
            "av": z.ab_wert, "ps": z.provisionssatz,
        })
    db.commit()
    staffel = db.execute(text(
        "SELECT * FROM domain_shared.vertreter_provisionsstaffeln WHERE id = :id"
    ), {"id": staffel_id}).fetchone()
    zeilen = db.execute(text("""
        SELECT * FROM domain_shared.vertreter_staffel_zeilen
        WHERE staffel_id = :sid ORDER BY zeile_nr
    """), {"sid": staffel_id}).fetchall()
    staffel_dict = dict(staffel._mapping)
    staffel_dict["zeilen"] = [ProvisionsStaffelZeileOut(**dict(z._mapping)) for z in zeilen]
    return ProvisionsStaffelOut(**staffel_dict)
