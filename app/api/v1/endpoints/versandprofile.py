"""Versandprofilstamm + Lieferavise — Belegversand-Konfiguration und Lieferavisierungen.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 10 Logistik/Transport):
  Versandprofile konfigurieren den automatischen Belegversand (Email, Fax, EDI).
  Felder: SMTP-Server, Absender, CC/BCC, Betreff-Vorlage, Archiv-Kennzeichen.
  SPA 1019 = Mailversand aktiv. SPA 668/669 = Versand Mail/Fax lokal.

  Lieferavise (Avise): Voranmeldungen von Lieferungen.
  Ein Avis enthält erwartetes Lieferdatum, Artikel und Menge. Nach Eingang
  wird der Avis mit dem tatsächlichen Lieferschein abgeglichen.
  Status: offen → bestätigt → abgeschlossen / storniert
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
from app.api.v1.schemas.versandprofile_schemas import VersandprofileOut


router = APIRouter(prefix="/logistik/versand",
                   tags=["Logistik - Versandprofile & Avise"])

GUELTIGE_VERSANDARTEN = ("email", "fax", "edi", "post", "api")
GUELTIGE_AVIS_STATUS = ("offen", "bestaetigt", "abgeschlossen", "storniert")


# ── Schemas ───────────────────────────────────────────────────────────────────

class VersandprofilCreate(BaseModel):
    profil_nr: str = Field(..., max_length=20)
    bezeichnung: str
    versandart: str = Field(default="email")
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    smtp_benutzer: Optional[str] = None
    absender_email: Optional[str] = None
    absender_name: Optional[str] = None
    cc_email: Optional[str] = None
    bcc_email: Optional[str] = None
    betreff_vorlage: Optional[str] = None
    archiv_kennzeichen: bool = True


class VersandprofilOut(BaseModel):
    id: str
    profil_nr: str
    bezeichnung: str
    versandart: str
    smtp_server: Optional[str]
    smtp_port: Optional[int]
    smtp_benutzer: Optional[str]
    absender_email: Optional[str]
    absender_name: Optional[str]
    cc_email: Optional[str]
    bcc_email: Optional[str]
    betreff_vorlage: Optional[str]
    archiv_kennzeichen: bool
    aktiv: bool
    created_at: datetime


class LieferavisCreate(BaseModel):
    avis_nr: Optional[str] = None
    lieferant_nr: Optional[str] = None
    kunden_nr: Optional[str] = None
    lieferschein_nr: Optional[str] = None
    avis_datum: date
    lieferdatum_erwartet: Optional[date] = None
    artikel_nr: Optional[str] = None
    menge: Optional[Decimal] = Field(None, gt=0)
    mengeneinheit: Optional[str] = None
    notiz: Optional[str] = None


class LieferavisOut(BaseModel):
    id: str
    avis_nr: str
    lieferant_nr: Optional[str]
    kunden_nr: Optional[str]
    lieferschein_nr: Optional[str]
    avis_datum: date
    lieferdatum_erwartet: Optional[date]
    status: str
    artikel_nr: Optional[str]
    menge: Optional[Decimal]
    mengeneinheit: Optional[str]
    notiz: Optional[str]
    created_at: datetime


# ── Versandprofile ────────────────────────────────────────────────────────────

@router.get("/profile", response_model=list[VersandprofilOut], summary="Versandprofile auflisten")
def list_versandprofile(
    versandart: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.versandprofile WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if versandart:
        sql += " AND versandart = :va"
        params["va"] = versandart
    sql += " ORDER BY profil_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [VersandprofilOut(**dict(r._mapping)) for r in rows]


@router.post("/profile", response_model=VersandprofilOut, status_code=201, summary="Versandprofil anlegen")
def create_versandprofil(
    payload: VersandprofilCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if payload.versandart not in GUELTIGE_VERSANDARTEN:
        raise HTTPException(422, f"versandart muss einer von {GUELTIGE_VERSANDARTEN} sein.")

    existing = db.execute(text("""
        SELECT id FROM domain_shared.versandprofile
        WHERE tenant_id = :tid AND profil_nr = :nr
    """), {"tid": tenant_id, "nr": payload.profil_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Versandprofil {payload.profil_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.versandprofile
            (id, tenant_id, profil_nr, bezeichnung, versandart,
             smtp_server, smtp_port, smtp_benutzer, absender_email, absender_name,
             cc_email, bcc_email, betreff_vorlage, archiv_kennzeichen)
        VALUES (:id, :tid, :nr, :bez, :va, :srv, :port, :usr, :mail, :name,
                :cc, :bcc, :bvl, :arch)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.profil_nr, "bez": payload.bezeichnung,
        "va": payload.versandart, "srv": payload.smtp_server, "port": payload.smtp_port,
        "usr": payload.smtp_benutzer, "mail": payload.absender_email, "name": payload.absender_name,
        "cc": payload.cc_email, "bcc": payload.bcc_email, "bvl": payload.betreff_vorlage,
        "arch": payload.archiv_kennzeichen,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.versandprofile WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return VersandprofilOut(**dict(row._mapping))


@router.delete("/profile/{profil_nr}", summary="Versandprofil löschen",
    response_model=None
)
def delete_versandprofil(
    profil_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.versandprofile SET aktiv = false
        WHERE tenant_id = :tid AND profil_nr = :nr
    """), {"tid": tenant_id, "nr": profil_nr})
    db.commit()
    return Response(status_code=204)


# ── Lieferavise ───────────────────────────────────────────────────────────────

@router.get("/avise", response_model=list[LieferavisOut], summary="Avise auflisten")
def list_avise(
    lieferant_nr: Optional[str] = Query(None),
    kunden_nr: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.lieferavise WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if lieferant_nr:
        sql += " AND lieferant_nr = :lnr"
        params["lnr"] = lieferant_nr
    if kunden_nr:
        sql += " AND kunden_nr = :knr"
        params["knr"] = kunden_nr
    if status:
        sql += " AND status = :status"
        params["status"] = status
    sql += " ORDER BY avis_datum DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [LieferavisOut(**dict(r._mapping)) for r in rows]


@router.post("/avise", response_model=LieferavisOut, status_code=201, summary="Avis anlegen")
def create_avis(
    payload: LieferavisCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = uuid7()
    avis_nr = payload.avis_nr or f"AV-{new_id[:8].upper()}"

    existing = db.execute(text("""
        SELECT id FROM domain_shared.lieferavise
        WHERE tenant_id = :tid AND avis_nr = :nr
    """), {"tid": tenant_id, "nr": avis_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Avis {avis_nr} bereits vorhanden.")

    db.execute(text("""
        INSERT INTO domain_shared.lieferavise
            (id, tenant_id, avis_nr, lieferant_nr, kunden_nr, lieferschein_nr,
             avis_datum, lieferdatum_erwartet, artikel_nr, menge, mengeneinheit, notiz)
        VALUES (:id, :tid, :nr, :lnr, :knr, :lsnr, :adatum, :ldatum, :anr, :menge, :me, :notiz)
    """), {
        "id": new_id, "tid": tenant_id, "nr": avis_nr,
        "lnr": payload.lieferant_nr, "knr": payload.kunden_nr,
        "lsnr": payload.lieferschein_nr, "adatum": payload.avis_datum,
        "ldatum": payload.lieferdatum_erwartet, "anr": payload.artikel_nr,
        "menge": payload.menge, "me": payload.mengeneinheit, "notiz": payload.notiz,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.lieferavise WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return LieferavisOut(**dict(row._mapping))


@router.patch("/avise/{avis_nr}/status", summary="Status avis",
    response_model=VersandprofileOut
)
def avis_status(
    avis_nr: str,
    neuer_status: str = Query(...),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if neuer_status not in GUELTIGE_AVIS_STATUS:
        raise HTTPException(422, f"Status muss einer von {GUELTIGE_AVIS_STATUS} sein.")
    row = db.execute(text("""
        SELECT * FROM domain_shared.lieferavise
        WHERE tenant_id = :tid AND avis_nr = :nr
    """), {"tid": tenant_id, "nr": avis_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Avis nicht gefunden.")
    if row.status == "abgeschlossen":
        raise HTTPException(409, "Abgeschlossene Avise können nicht mehr geändert werden.")

    db.execute(text("""
        UPDATE domain_shared.lieferavise SET status = :status
        WHERE tenant_id = :tid AND avis_nr = :nr
    """), {"status": neuer_status, "tid": tenant_id, "nr": avis_nr})
    db.commit()
    updated = db.execute(text(
        "SELECT * FROM domain_shared.lieferavise WHERE tenant_id = :tid AND avis_nr = :nr"
    ), {"tid": tenant_id, "nr": avis_nr}).fetchone()
    return LieferavisOut(**dict(updated._mapping))
