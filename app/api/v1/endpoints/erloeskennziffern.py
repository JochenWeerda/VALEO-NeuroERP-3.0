"""Erlöskennziffern [EKZS/EKZZ] — WaWi→FIBU Kontozuordnung.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 03 FIBU):
  Das Erlöskennziffer-System steuert die automatische Verbuchung von
  Warenwirtschafts-Vorgängen in die Finanzbuchhaltung. Direktsprünge:
  [EKZS] = Erlöskennziffer-Stamm, [EKZZ] = Erlöskontenzuordnung.

  Beteiligte Elemente:
  - Erlösklassen [ERLK]: Klassifizierung der Erlösart (EK/VK, Inland/Ausland)
  - Erlöskennziffern [EKZS]: Eindeutige Nummer, im Artikelstamm hinterlegt
  - Erlöskontenzuordnung [EKZZ]: Verknüpfung EKZ + Steuerschlüssel + Erlösklasse
    + Steuergruppe + Buchungsklasse → Erlöskonto + Aufwandskonto

  Gültig-ab-Datum: Erlaubt zukünftige Kontenänderungen vorab einzupflegen.
  Schlüsselfelder sind durch Setzen von Haken für Gruppenbearbeitung nutzbar.

  Buchungsablauf: WaWi-Vorgang → Artikel-EKZ-Nr + Steuerschlüssel + Erlösklasse
  → Erlöskontenzuordnung → FIBU-Buchung auf Erlös-/Aufwandskonto.
"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.erloeskennziffern_schemas import (
    ErloeskennzifferCreate,
    ErloeskennzifferOut,
    ErloeskontenzuordnungCreate,
    ErloeskontenzuordnungOut,
)


router = APIRouter(prefix="/fibu/erloeskennziffern",
                   tags=["FIBU - Erlöskennziffern"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class KontoLookupResult(BaseModel):
    ekz_nr: str
    konto_erloese: Optional[str]
    konto_aufwand: Optional[str]
    konto_umsatzsteuer: Optional[str]
    konto_vorsteuer: Optional[str]
    gueltig_ab: date


# ── Erlöskennziffern CRUD ─────────────────────────────────────────────────────

@router.get("", response_model=list[ErloeskennzifferOut], summary="Erloeskennziffern auflisten")
def list_erloeskennziffern(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.erloeskennziffern
        WHERE tenant_id = :tid AND aktiv = true ORDER BY ekz_nr
    """), {"tid": tenant_id}).fetchall()
    return [ErloeskennzifferOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=ErloeskennzifferOut, status_code=201, summary="Erloeskennziffer anlegen")
def create_erloeskennziffer(
    payload: ErloeskennzifferCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.erloeskennziffern
        WHERE tenant_id = :tid AND ekz_nr = :nr
    """), {"tid": tenant_id, "nr": payload.ekz_nr}).fetchone():
        raise HTTPException(409, f"Erlöskennziffer {payload.ekz_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.erloeskennziffern (id, tenant_id, ekz_nr, bezeichnung)
        VALUES (:id, :tid, :nr, :bez)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.ekz_nr, "bez": payload.bezeichnung})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.erloeskennziffern WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ErloeskennzifferOut(**dict(row._mapping))


@router.put("/{ekz_nr}", response_model=ErloeskennzifferOut, summary="Erloeskennziffer aktualisieren")
def update_erloeskennziffer(
    ekz_nr: str,
    payload: ErloeskennzifferCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    result = db.execute(text("""
        UPDATE domain_shared.erloeskennziffern SET bezeichnung = :bez
        WHERE tenant_id = :tid AND ekz_nr = :nr AND aktiv = true
    """), {"bez": payload.bezeichnung, "tid": tenant_id, "nr": ekz_nr})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, f"Erlöskennziffer {ekz_nr} nicht gefunden.")
    row = db.execute(text("""
        SELECT * FROM domain_shared.erloeskennziffern WHERE tenant_id = :tid AND ekz_nr = :nr
    """), {"tid": tenant_id, "nr": ekz_nr}).fetchone()
    return ErloeskennzifferOut(**dict(row._mapping))


@router.delete("/{ekz_nr}", summary="Erloeskennziffer löschen",
    response_model=None
)
def delete_erloeskennziffer(
    ekz_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.erloeskennziffern SET aktiv = false
        WHERE tenant_id = :tid AND ekz_nr = :nr
    """), {"tid": tenant_id, "nr": ekz_nr})
    db.commit()
    return Response(status_code=204)


# ── Erlöskontenzuordnung CRUD ─────────────────────────────────────────────────

@router.get("/zuordnungen", response_model=list[ErloeskontenzuordnungOut], summary="Zuordnungen auflisten")
def list_zuordnungen(
    ekz_id: Optional[str] = Query(None),
    steuerschluessel: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT z.* FROM domain_shared.erloeskontenzuordnung z
        JOIN domain_shared.erloeskennziffern e ON e.id = z.ekz_id
        WHERE e.tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if ekz_id:
        sql += " AND z.ekz_id = :ekzid"
        params["ekzid"] = ekz_id
    if steuerschluessel:
        sql += " AND z.steuerschluessel = :sk"
        params["sk"] = steuerschluessel
    sql += " ORDER BY z.gueltig_ab DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [ErloeskontenzuordnungOut(**dict(r._mapping)) for r in rows]


@router.post("/zuordnungen", response_model=ErloeskontenzuordnungOut, status_code=201, summary="Zuordnung anlegen")
def create_zuordnung(
    payload: ErloeskontenzuordnungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    ekz = db.execute(text("""
        SELECT id FROM domain_shared.erloeskennziffern
        WHERE id = :id AND tenant_id = :tid
    """), {"id": payload.ekz_id, "tid": tenant_id}).fetchone()
    if not ekz:
        raise HTTPException(404, "Erlöskennziffer nicht gefunden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.erloeskontenzuordnung
            (id, tenant_id, ekz_id, gueltig_ab, steuerschluessel, erlösklasse,
             steuergruppe, buchungsklasse, konto_erloese, konto_aufwand,
             konto_umsatzsteuer, konto_vorsteuer)
        VALUES (:id, :tid, :ekzid, :gab, :sk, :ek, :sg, :bk, :ke, :ka, :kust, :kvst)
        ON CONFLICT (tenant_id, ekz_id, gueltig_ab, steuerschluessel, erlösklasse, buchungsklasse)
        DO UPDATE SET
            konto_erloese = EXCLUDED.konto_erloese,
            konto_aufwand = EXCLUDED.konto_aufwand,
            konto_umsatzsteuer = EXCLUDED.konto_umsatzsteuer,
            konto_vorsteuer = EXCLUDED.konto_vorsteuer
    """), {
        "id": new_id, "tid": tenant_id, "ekzid": payload.ekz_id,
        "gab": payload.gueltig_ab, "sk": payload.steuerschluessel,
        "ek": payload.erlösklasse, "sg": payload.steuergruppe,
        "bk": payload.buchungsklasse, "ke": payload.konto_erloese,
        "ka": payload.konto_aufwand, "kust": payload.konto_umsatzsteuer,
        "kvst": payload.konto_vorsteuer,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.erloeskontenzuordnung
        WHERE ekz_id = :ekzid AND gueltig_ab = :gab
          AND (steuerschluessel = :sk OR (:sk IS NULL AND steuerschluessel IS NULL))
        ORDER BY id DESC LIMIT 1
    """), {"ekzid": payload.ekz_id, "gab": payload.gueltig_ab, "sk": payload.steuerschluessel}).fetchone()
    return ErloeskontenzuordnungOut(**dict(row._mapping))


@router.get("/lookup", response_model=KontoLookupResult, summary="Lookup konto")
def konto_lookup(
    ekz_nr: str = Query(...),
    steuerschluessel: Optional[str] = Query(None),
    erlösklasse: Optional[str] = Query(None),
    buchungsklasse: Optional[str] = Query(None),
    datum: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ermittelt FIBU-Konten für WaWi-Vorgang per EKZ + Steuerschlüssel + Erlösklasse."""
    check_datum = datum or date.today()

    ekz = db.execute(text("""
        SELECT * FROM domain_shared.erloeskennziffern
        WHERE tenant_id = :tid AND ekz_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": ekz_nr}).fetchone()
    if not ekz:
        raise HTTPException(404, f"Erlöskennziffer {ekz_nr} nicht gefunden.")

    # Beste Zuordnung: spezifischste zuerst, dann gültig_ab <= datum
    row = db.execute(text("""
        SELECT * FROM domain_shared.erloeskontenzuordnung
        WHERE ekz_id = :ekzid
          AND gueltig_ab <= :datum
          AND (steuerschluessel = :sk OR steuerschluessel IS NULL)
          AND (erlösklasse = :ek OR erlösklasse IS NULL)
          AND (buchungsklasse = :bk OR buchungsklasse IS NULL)
        ORDER BY
            (CASE WHEN steuerschluessel IS NOT NULL THEN 1 ELSE 0 END) DESC,
            (CASE WHEN erlösklasse IS NOT NULL THEN 1 ELSE 0 END) DESC,
            gueltig_ab DESC
        LIMIT 1
    """), {
        "ekzid": ekz.id, "datum": check_datum,
        "sk": steuerschluessel, "ek": erlösklasse, "bk": buchungsklasse,
    }).fetchone()

    if not row:
        raise HTTPException(404, "Keine Erlöskontenzuordnung für diese Kombination gefunden.")

    return KontoLookupResult(
        ekz_nr=ekz_nr,
        konto_erloese=row.konto_erloese,
        konto_aufwand=row.konto_aufwand,
        konto_umsatzsteuer=row.konto_umsatzsteuer,
        konto_vorsteuer=row.konto_vorsteuer,
        gueltig_ab=row.gueltig_ab,
    )
