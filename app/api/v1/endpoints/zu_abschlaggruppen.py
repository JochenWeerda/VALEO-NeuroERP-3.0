"""Zu-/Abschlaggruppen [ZAGR] und Zu-/Abschlagklassen [ZAKL] — Konditionsstammdaten.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 02 WaWi/Auftrag):
  Zu-/Abschlaggruppen werden Artikeln zugeordnet (EK + VK getrennt).
  Zu-/Abschlagklassen werden Kunden/Lieferanten zugeordnet (EK + VK getrennt).
  Die Kombination Gruppe × Klasse ergibt die anzuwendenden Zu-/Abschläge.

  Direktsprünge: [ZAGR] = Zu-/Abschlaggruppe, [ZABK] = Zu-/Abschlagklasse.
  Zu-/Abschlagkonditionen [ZAK]: Verknüpfung Gruppe+Klasse+Richtung → Betrag/Prozent/Staffel.
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
from app.api.v1.schemas.zu_abschlaggruppen_schemas import (
    ZuAbschlagKonditionCreate,
    ZuAbschlagKonditionOut,
    ZuAbschlaggruppeCreate,
    ZuAbschlaggruppeOut,
    ZuAbschlagklasseCreate,
    ZuAbschlagklasseOut,
)


router = APIRouter(prefix="/preise/zu-abschlaege",
                   tags=["Preise/Konditionen - Zu-/Abschläge"])

GUELTIGE_RICHTUNG = {"ek", "vk"}
GUELTIGE_KONDITION_TYP = {"betrag", "prozent"}


# ── Schemas ───────────────────────────────────────────────────────────────────

# ── Zu-/Abschlaggruppen CRUD ──────────────────────────────────────────────────

@router.get("/gruppen", response_model=list[ZuAbschlaggruppeOut], summary="Zu abschlaggruppen auflisten")
def list_zu_abschlaggruppen(
    richtung: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.zu_abschlaggruppen WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if richtung:
        sql += " AND richtung = :richtung"
        params["richtung"] = richtung
    sql += " ORDER BY gruppe_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [ZuAbschlaggruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/gruppen", response_model=ZuAbschlaggruppeOut, status_code=201, summary="Zu abschlaggruppe anlegen")
def create_zu_abschlaggruppe(
    payload: ZuAbschlaggruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.zu_abschlaggruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND richtung = :r
    """), {"tid": tenant_id, "nr": payload.gruppe_nr, "r": payload.richtung}).fetchone():
        raise HTTPException(409, f"Zu-/Abschlaggruppe {payload.gruppe_nr}/{payload.richtung} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.zu_abschlaggruppen (id, tenant_id, gruppe_nr, bezeichnung, richtung)
        VALUES (:id, :tid, :nr, :bez, :r)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr, "bez": payload.bezeichnung, "r": payload.richtung})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.zu_abschlaggruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ZuAbschlaggruppeOut(**dict(row._mapping))


@router.delete("/gruppen/{gruppe_nr}", summary="Zu abschlaggruppe löschen",
    response_model=None
)
def delete_zu_abschlaggruppe(
    gruppe_nr: str,
    richtung: str = Query("vk"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.zu_abschlaggruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND richtung = :r
    """), {"tid": tenant_id, "nr": gruppe_nr, "r": richtung})
    db.commit()
    return Response(status_code=204)


# ── Zu-/Abschlagklassen CRUD ──────────────────────────────────────────────────

@router.get("/klassen", response_model=list[ZuAbschlagklasseOut], summary="Zu abschlagklassen auflisten")
def list_zu_abschlagklassen(
    richtung: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.zu_abschlagklassen WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if richtung:
        sql += " AND richtung = :richtung"
        params["richtung"] = richtung
    sql += " ORDER BY klasse_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [ZuAbschlagklasseOut(**dict(r._mapping)) for r in rows]


@router.post("/klassen", response_model=ZuAbschlagklasseOut, status_code=201, summary="Zu abschlagklasse anlegen")
def create_zu_abschlagklasse(
    payload: ZuAbschlagklasseCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.zu_abschlagklassen
        WHERE tenant_id = :tid AND klasse_nr = :nr AND richtung = :r
    """), {"tid": tenant_id, "nr": payload.klasse_nr, "r": payload.richtung}).fetchone():
        raise HTTPException(409, f"Zu-/Abschlagklasse {payload.klasse_nr}/{payload.richtung} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.zu_abschlagklassen (id, tenant_id, klasse_nr, bezeichnung, richtung)
        VALUES (:id, :tid, :nr, :bez, :r)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.klasse_nr, "bez": payload.bezeichnung, "r": payload.richtung})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.zu_abschlagklassen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ZuAbschlagklasseOut(**dict(row._mapping))


@router.delete("/klassen/{klasse_nr}", summary="Zu abschlagklasse löschen",
    response_model=None
)
def delete_zu_abschlagklasse(
    klasse_nr: str,
    richtung: str = Query("vk"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.zu_abschlagklassen SET aktiv = false
        WHERE tenant_id = :tid AND klasse_nr = :nr AND richtung = :r
    """), {"tid": tenant_id, "nr": klasse_nr, "r": richtung})
    db.commit()
    return Response(status_code=204)


# ── Zu-/Abschlagkonditionen (Gruppe × Klasse → Wert) ─────────────────────────

@router.get("/konditionen", response_model=list[ZuAbschlagKonditionOut], summary="Zu abschlag konditionen auflisten")
def list_zu_abschlag_konditionen(
    gruppe_id: Optional[str] = Query(None),
    klasse_id: Optional[str] = Query(None),
    datum: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    check_datum = datum or date.today()
    sql = """
        SELECT k.* FROM domain_shared.zu_abschlag_konditionen k
        JOIN domain_shared.zu_abschlaggruppen g ON g.id = k.gruppe_id
        WHERE g.tenant_id = :tid AND k.aktiv = true
          AND k.gueltig_ab <= :datum
          AND (k.gueltig_bis IS NULL OR k.gueltig_bis >= :datum)
    """
    params: dict = {"tid": tenant_id, "datum": check_datum}
    if gruppe_id:
        sql += " AND k.gruppe_id = :gid"
        params["gid"] = gruppe_id
    if klasse_id:
        sql += " AND k.klasse_id = :kid"
        params["kid"] = klasse_id
    sql += " ORDER BY k.gueltig_ab DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [ZuAbschlagKonditionOut(**dict(r._mapping)) for r in rows]


@router.post("/konditionen", response_model=ZuAbschlagKonditionOut, status_code=201, summary="Zu abschlag kondition anlegen")
def create_zu_abschlag_kondition(
    payload: ZuAbschlagKonditionCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    # Gruppe muss zum Tenant gehören
    if not db.execute(text("""
        SELECT id FROM domain_shared.zu_abschlaggruppen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": payload.gruppe_id, "tid": tenant_id}).fetchone():
        raise HTTPException(404, "Zu-/Abschlaggruppe nicht gefunden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.zu_abschlag_konditionen
            (id, gruppe_id, klasse_id, kondition_typ, wert, gueltig_ab, gueltig_bis, beschreibung)
        VALUES (:id, :gid, :kid, :kt, :wert, :gab, :gbis, :bez)
    """), {
        "id": new_id, "gid": payload.gruppe_id, "kid": payload.klasse_id,
        "kt": payload.kondition_typ, "wert": payload.wert,
        "gab": payload.gueltig_ab, "gbis": payload.gueltig_bis, "bez": payload.beschreibung,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.zu_abschlag_konditionen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ZuAbschlagKonditionOut(**dict(row._mapping))
