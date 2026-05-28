"""Hofliste — Fahrzeugvormeldungen und Status am Waagenterminal.

Fachlicher Hintergrund (aus Referenz-ERP Wissensbasis):
  Die Hofliste (EPA OWAAGE71) verwaltet angemeldete Fahrzeuge am Betriebsgelände
  der Waage. Landwirte oder Spediteure können sich voranmelden, bevor sie zur
  Waage fahren. Der Disponente sieht alle Fahrzeuge im Hof und deren Status.

  Status-Workflow: vorgemeldet → auf_hof → in_waegung → gewogen → abgefahren

  Einrichtungsparameter 'Partievorerfassung zulassen' ermöglicht das
  vorherige Anlegen einer Partie im System vor der physischen Anlieferung.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/waage/hofliste", tags=["Waage - Hofliste"])

VALID_STATUS = ("vorgemeldet", "auf_hof", "in_waegung", "gewogen", "abgefahren")


# ── Schemas ───────────────────────────────────────────────────────────────────

class HoflisteCreate(BaseModel):
    kfz_kennzeichen: str = Field(..., min_length=1, max_length=20)
    fahrer_name: Optional[str] = None
    lieferant_nr: Optional[str] = None
    lieferant_name: Optional[str] = None
    kontrakt_nr: Optional[str] = None
    artikel_nr: Optional[str] = None
    artikel_name: Optional[str] = None
    geplante_menge_t: Optional[Decimal] = None
    standort_id: Optional[str] = None
    partievorerfassung: bool = False
    bemerkung: Optional[str] = None


class HoflisteOut(BaseModel):
    id: str
    kfz_kennzeichen: str
    fahrer_name: Optional[str]
    lieferant_nr: Optional[str]
    lieferant_name: Optional[str]
    kontrakt_nr: Optional[str]
    artikel_nr: Optional[str]
    artikel_name: Optional[str]
    geplante_menge_t: Optional[Decimal]
    standort_id: Optional[str]
    status: str
    ankunft_zeit: Optional[datetime]
    wiegung_start: Optional[datetime]
    abfahrt_zeit: Optional[datetime]
    wiegeschein_id: Optional[str]
    partievorerfassung: bool
    bemerkung: Optional[str]
    created_at: datetime


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[HoflisteOut], summary="Hofliste abrufen")
def get_hofliste(
    status: Optional[str] = Query(None, description="vorgemeldet,auf_hof,in_waegung,gewogen,abgefahren"),
    standort_id: Optional[str] = Query(None),
    aktiv: bool = Query(True, description="Nur aktive Einträge (nicht abgefahren)"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Aktuelle Hofliste — alle Fahrzeuge am Waagenterminal."""
    sql = """
        SELECT * FROM domain_shared.waage_hofliste
        WHERE tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if aktiv:
        sql += " AND status != 'abgefahren'"
    if status:
        sql += " AND status = :status"
        params["status"] = status
    if standort_id:
        sql += " AND standort_id = :standort_id"
        params["standort_id"] = standort_id
    sql += " ORDER BY created_at"
    rows = db.execute(text(sql), params).fetchall()
    return [HoflisteOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=HoflisteOut, status_code=201, summary="Anmelden")
def anmelden(
    payload: HoflisteCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Fahrzeug zur Hofliste anmelden (Voranmeldung)."""
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.waage_hofliste
            (id, tenant_id, kfz_kennzeichen, fahrer_name,
             lieferant_nr, lieferant_name, kontrakt_nr,
             artikel_nr, artikel_name, geplante_menge_t,
             standort_id, status, partievorerfassung, bemerkung)
        VALUES
            (:id, :tid, :kfz, :fahrer,
             :lief_nr, :lief_name, :ktr_nr,
             :art_nr, :art_name, :menge,
             :standort, 'vorgemeldet', :partie, :bem)
    """), {
        "id": new_id, "tid": tenant_id,
        "kfz": payload.kfz_kennzeichen.upper(), "fahrer": payload.fahrer_name,
        "lief_nr": payload.lieferant_nr, "lief_name": payload.lieferant_name,
        "ktr_nr": payload.kontrakt_nr,
        "art_nr": payload.artikel_nr, "art_name": payload.artikel_name,
        "menge": payload.geplante_menge_t, "standort": payload.standort_id,
        "partie": payload.partievorerfassung, "bem": payload.bemerkung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.waage_hofliste WHERE id = :id
    """), {"id": new_id}).fetchone()
    return HoflisteOut(**dict(row._mapping))


@router.post("/{eintrag_id}/status", summary="Aendern status",
    response_model=CompatFlexOut
)
def status_aendern(
    eintrag_id: str,
    neuer_status: str,
    wiegeschein_id: Optional[str] = None,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Status eines Hoflisteneintrags ändern."""
    if neuer_status not in VALID_STATUS:
        raise HTTPException(422, f"Ungültiger Status. Erlaubt: {', '.join(VALID_STATUS)}")

    row = db.execute(text("""
        SELECT * FROM domain_shared.waage_hofliste
        WHERE id = :id AND tenant_id = :tid
    """), {"id": eintrag_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Hoflisteneintrag nicht gefunden.")

    updates: dict = {"id": eintrag_id, "status": neuer_status}
    extra_sql = ""
    if neuer_status == "auf_hof":
        extra_sql = ", ankunft_zeit = now()"
    elif neuer_status == "in_waegung":
        extra_sql = ", wiegung_start = now()"
    elif neuer_status == "gewogen" and wiegeschein_id:
        extra_sql = ", wiegeschein_id = :wiegeschein_id"
        updates["wiegeschein_id"] = wiegeschein_id
    elif neuer_status == "abgefahren":
        extra_sql = ", abfahrt_zeit = now()"

    # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
    db.execute(text(f"""
        UPDATE domain_shared.waage_hofliste
        SET status = :status {extra_sql}, updated_at = now()
        WHERE id = :id
    """), updates)
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.waage_hofliste WHERE id = :id
    """), {"id": eintrag_id}).fetchone()
    return HoflisteOut(**dict(row._mapping))


@router.delete("/{eintrag_id}", summary="Abmelden",
    response_model=CompatFlexOut
)
def abmelden(
    eintrag_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Hoflisteneintrag löschen (nur vorgemeldete Einträge)."""
    row = db.execute(text("""
        SELECT status FROM domain_shared.waage_hofliste
        WHERE id = :id AND tenant_id = :tid
    """), {"id": eintrag_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Hoflisteneintrag nicht gefunden.")
    if row.status not in ("vorgemeldet",):
        raise HTTPException(409, "Nur vorgemeldete Einträge können gelöscht werden.")

    db.execute(text("""
        DELETE FROM domain_shared.waage_hofliste WHERE id = :id
    """), {"id": eintrag_id})
    db.commit()
    return Response(status_code=204)


@router.get("/statistik", summary="Statistik hofliste",
    response_model=None
)
def hofliste_statistik(
    standort_id: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Tagesstatistik der Hofliste: Fahrzeuge je Status."""
    sql = """
        SELECT status, COUNT(*) as anzahl,
               COALESCE(SUM(geplante_menge_t), 0) as geplante_menge_gesamt
        FROM domain_shared.waage_hofliste
        WHERE tenant_id = :tid
          AND created_at >= CURRENT_DATE
    """
    params: dict = {"tid": tenant_id}
    if standort_id:
        sql += " AND standort_id = :standort_id"
        params["standort_id"] = standort_id
    sql += " GROUP BY status"
    rows = db.execute(text(sql), params).fetchall()
    return {r.status: {"anzahl": r.anzahl, "geplante_menge_t": float(r.geplante_menge_gesamt)}
            for r in rows}
