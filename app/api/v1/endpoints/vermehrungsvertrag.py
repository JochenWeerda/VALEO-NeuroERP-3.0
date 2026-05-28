"""Vermehrungsvertrag [SAATV] — Saatgut-Anbauverträge mit Vermehrern.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 01 Kontrakt/Rohware):
  Vermehrungsverträge [SAATV] werden im Bereich Saatzucht für Anbauverträge
  mit Saatgut-Vermehrern angelegt. Sie verknüpfen:
  - Vermehrer (= Kundennummer aus Kundenstamm)
  - Sorte (aus Saatgutstamm)
  - Erntejahr
  - Anbaufläche, Vertragsmenge, Kategorie (Z1/Z2/SE)
  - LWK-Anerkennungsstelle, Vermehrerkennziffer (VMKz)

  Nach dem Anlegen muss ein Schlag zugeordnet werden (Feldbuch-Integration).
  Danach im Vermehrungsvertrag auf "Übernehmen" klicken.

  Prozess: Vertrag anlegen → Schlag zuordnen → Wiegung (OWAAGE Vermehrungsvertrag) →
           Qualitätsdaten erfassen → Anerkennungsantrag LWK
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
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/saatzucht/vermehrungsvertraege",
                   tags=["Saatzucht - Vermehrungsverträge"])

GUELTIGE_STATUS = ("angelegt", "aktiv", "beendet", "storniert")


# ── Schemas ───────────────────────────────────────────────────────────────────

class VermehrungsvertragCreate(BaseModel):
    vertrag_nr: str = Field(..., max_length=30)
    erntejahr: int = Field(..., ge=1990, le=2100)
    vermehrer_kunden_nr: str
    sorte_nr: Optional[str] = None
    sorte_bezeichnung: Optional[str] = None
    kategorie: Optional[str] = Field(None, description="Z1, Z2, SE, E, B")
    vertragsart: Optional[str] = None
    vertrags_menge_t: Optional[Decimal] = Field(None, ge=0)
    anbauflaeche_ha: Optional[Decimal] = Field(None, ge=0)
    lwk_anerkennungsstelle: Optional[str] = None
    vmkz: Optional[str] = Field(None, description="Vermehrerkennziffer")
    registriernummer: Optional[str] = None
    bemerkung: Optional[str] = None


class VermehrungsvertragOut(BaseModel):
    id: str
    vertrag_nr: str
    erntejahr: int
    vermehrer_kunden_nr: str
    sorte_nr: Optional[str]
    sorte_bezeichnung: Optional[str]
    kategorie: Optional[str]
    vertragsart: Optional[str]
    vertrags_menge_t: Optional[Decimal]
    anbauflaeche_ha: Optional[Decimal]
    lwk_anerkennungsstelle: Optional[str]
    vmkz: Optional[str]
    registriernummer: Optional[str]
    status: str
    bemerkung: Optional[str]
    created_at: datetime
    updated_at: datetime


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[VermehrungsvertragOut], summary="Vermehrungsvertraege auflisten")
def list_vermehrungsvertraege(
    erntejahr: Optional[int] = Query(None),
    vermehrer_kunden_nr: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sorte_nr: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.saatzucht_vermehrungsvertraege
        WHERE tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if erntejahr:
        sql += " AND erntejahr = :ej"
        params["ej"] = erntejahr
    if vermehrer_kunden_nr:
        sql += " AND vermehrer_kunden_nr = :vkn"
        params["vkn"] = vermehrer_kunden_nr
    if status:
        sql += " AND status = :status"
        params["status"] = status
    if sorte_nr:
        sql += " AND sorte_nr = :snr"
        params["snr"] = sorte_nr
    sql += " ORDER BY erntejahr DESC, vertrag_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [VermehrungsvertragOut(**dict(r._mapping)) for r in rows]


@router.get("/{vertrag_nr}", response_model=VermehrungsvertragOut, summary="Vermehrungsvertrag abrufen")
def get_vermehrungsvertrag(
    vertrag_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.saatzucht_vermehrungsvertraege
        WHERE tenant_id = :tid AND vertrag_nr = :nr
    """), {"tid": tenant_id, "nr": vertrag_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Vermehrungsvertrag nicht gefunden.")
    return VermehrungsvertragOut(**dict(row._mapping))


@router.post("", response_model=VermehrungsvertragOut, status_code=201, summary="Vermehrungsvertrag anlegen")
def create_vermehrungsvertrag(
    payload: VermehrungsvertragCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.saatzucht_vermehrungsvertraege
        WHERE tenant_id = :tid AND vertrag_nr = :nr
    """), {"tid": tenant_id, "nr": payload.vertrag_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Vermehrungsvertrag {payload.vertrag_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.saatzucht_vermehrungsvertraege
            (id, tenant_id, vertrag_nr, erntejahr, vermehrer_kunden_nr,
             sorte_nr, sorte_bezeichnung, kategorie, vertragsart,
             vertrags_menge_t, anbauflaeche_ha, lwk_anerkennungsstelle,
             vmkz, registriernummer, status, bemerkung)
        VALUES (:id, :tid, :nr, :ej, :vkn, :snr, :sbez, :kat, :vart,
                :vmenge, :ha, :lwk, :vmkz, :regnr, 'angelegt', :bem)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.vertrag_nr,
        "ej": payload.erntejahr, "vkn": payload.vermehrer_kunden_nr,
        "snr": payload.sorte_nr, "sbez": payload.sorte_bezeichnung,
        "kat": payload.kategorie, "vart": payload.vertragsart,
        "vmenge": payload.vertrags_menge_t, "ha": payload.anbauflaeche_ha,
        "lwk": payload.lwk_anerkennungsstelle, "vmkz": payload.vmkz,
        "regnr": payload.registriernummer, "bem": payload.bemerkung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.saatzucht_vermehrungsvertraege WHERE id = :id
    """), {"id": new_id}).fetchone()
    return VermehrungsvertragOut(**dict(row._mapping))


@router.put("/{vertrag_nr}", response_model=VermehrungsvertragOut, summary="Vermehrungsvertrag aktualisieren")
def update_vermehrungsvertrag(
    vertrag_nr: str,
    payload: VermehrungsvertragCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id, status FROM domain_shared.saatzucht_vermehrungsvertraege
        WHERE tenant_id = :tid AND vertrag_nr = :nr
    """), {"tid": tenant_id, "nr": vertrag_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Vermehrungsvertrag nicht gefunden.")
    if row.status == "storniert":
        raise HTTPException(409, "Stornierte Verträge können nicht bearbeitet werden.")

    db.execute(text("""
        UPDATE domain_shared.saatzucht_vermehrungsvertraege
        SET erntejahr = :ej, vermehrer_kunden_nr = :vkn,
            sorte_nr = :snr, sorte_bezeichnung = :sbez,
            kategorie = :kat, vertragsart = :vart,
            vertrags_menge_t = :vmenge, anbauflaeche_ha = :ha,
            lwk_anerkennungsstelle = :lwk, vmkz = :vmkz,
            registriernummer = :regnr, bemerkung = :bem,
            updated_at = now()
        WHERE tenant_id = :tid AND vertrag_nr = :nr
    """), {
        "tid": tenant_id, "nr": vertrag_nr, "ej": payload.erntejahr,
        "vkn": payload.vermehrer_kunden_nr, "snr": payload.sorte_nr,
        "sbez": payload.sorte_bezeichnung, "kat": payload.kategorie,
        "vart": payload.vertragsart, "vmenge": payload.vertrags_menge_t,
        "ha": payload.anbauflaeche_ha, "lwk": payload.lwk_anerkennungsstelle,
        "vmkz": payload.vmkz, "regnr": payload.registriernummer,
        "bem": payload.bemerkung,
    })
    db.commit()
    updated = db.execute(text("""
        SELECT * FROM domain_shared.saatzucht_vermehrungsvertraege
        WHERE tenant_id = :tid AND vertrag_nr = :nr
    """), {"tid": tenant_id, "nr": vertrag_nr}).fetchone()
    return VermehrungsvertragOut(**dict(updated._mapping))


@router.post("/{vertrag_nr}/status", response_model=VermehrungsvertragOut, summary="Status setzen")
def set_status(
    vertrag_nr: str,
    neuer_status: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Status des Vermehrungsvertrags ändern (angelegt → aktiv → beendet / storniert)."""
    if neuer_status not in GUELTIGE_STATUS:
        raise HTTPException(422, f"Ungültiger Status. Erlaubt: {GUELTIGE_STATUS}")

    row = db.execute(text("""
        SELECT status FROM domain_shared.saatzucht_vermehrungsvertraege
        WHERE tenant_id = :tid AND vertrag_nr = :nr
    """), {"tid": tenant_id, "nr": vertrag_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Vermehrungsvertrag nicht gefunden.")
    if row.status == "storniert":
        raise HTTPException(409, "Stornierte Verträge können nicht mehr geändert werden.")

    db.execute(text("""
        UPDATE domain_shared.saatzucht_vermehrungsvertraege
        SET status = :status, updated_at = now()
        WHERE tenant_id = :tid AND vertrag_nr = :nr
    """), {"tid": tenant_id, "nr": vertrag_nr, "status": neuer_status})
    db.commit()
    updated = db.execute(text("""
        SELECT * FROM domain_shared.saatzucht_vermehrungsvertraege
        WHERE tenant_id = :tid AND vertrag_nr = :nr
    """), {"tid": tenant_id, "nr": vertrag_nr}).fetchone()
    return VermehrungsvertragOut(**dict(updated._mapping))
