"""Mengeneinheiten und Mengeneinheitengruppen — Artikelstamm.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 17 Artikelstamm):
  Mengeneinheitengruppen steuern die Mengeneinheiten eines Artikels für
  Einkauf (EK), Verkauf (VK), Bestandsführung und Preisfindung. Sie können
  unterschiedliche Einheiten für EK/VK/Bestand haben (z.B. EK in t, VK in kg).

  Mengeneinheiten-Stamm: Basis-Einheiten mit Umrechnungsfaktoren.
  Beispiel: t → kg (Faktor 1000), Kar → Stk (Faktor 24 bei 24er-Karton).

  Die Zuordnung einer Mengeneinheitengruppe im Artikelstamm steuert automatisch
  die Umrechnung bei Vorgangserfassung. Dezimalstellen je Einheit konfigurierbar.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


router = APIRouter(prefix="/artikel/mengeneinheiten",
                   tags=["Artikelstamm - Mengeneinheiten & Gruppen"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class MengeneinheitCreate(BaseModel):
    """Grundmengeneinheit nach a.eins (Nutzerauftrag 24.11.2026)."""

    einheit_kuerzel: str = Field(..., max_length=10, description="Kurztext, wie er gedruckt wird (kg, Stück, Ltr.)")
    bezeichnung: str
    basis_einheit: Optional[str] = Field(None, max_length=10)
    umrechnungsfaktor: Optional[Decimal] = Field(None, gt=0)
    # Rundung bei Umrechnung: 0 bis 4; bei aktiven Einheiten nur nach oben aenderbar.
    dezimalstellen: int = Field(default=3, ge=0, le=4)
    nummer: Optional[int] = Field(None, ge=1, le=9999, description="Nummer der Mengeneinheit (hoechstens 4 Stellen)")
    langtext: Optional[str] = Field(None, max_length=80, description="Langtext, der anstelle des Kurztexts gedruckt werden kann")
    iso_name: Optional[str] = Field(None, max_length=20)
    datanorm_kurz: Optional[str] = Field(None, max_length=10, description="Kurzbezeichnung im DataNorm-Verfahren")
    statistikkennzeichen: Optional[str] = Field(None, max_length=20)
    preisbezug_einheit: Optional[str] = Field(None, max_length=10, description="Mengeneinheit des Preisbezugs")
    preisbezug_menge: Optional[Decimal] = Field(None, gt=0, description="Preisbezug, z. B. 100 bei Preis je 100 kg")
    un_code: Optional[str] = Field(None, pattern=r"^[A-Z0-9]{2,3}$",
                                   description="UN-Mengeneinheit (UN/ECE Rec. 20) fuer E-Rechnung und openTRANS")


class MengeneinheitOut(BaseModel):
    id: str
    einheit_kuerzel: str
    bezeichnung: str
    basis_einheit: Optional[str]
    umrechnungsfaktor: Optional[Decimal]
    dezimalstellen: int
    nummer: Optional[int] = None
    langtext: Optional[str] = None
    iso_name: Optional[str] = None
    datanorm_kurz: Optional[str] = None
    statistikkennzeichen: Optional[str] = None
    preisbezug_einheit: Optional[str] = None
    preisbezug_menge: Optional[Decimal] = None
    un_code: Optional[str] = None
    aktiv: bool
    created_at: datetime


ZUSATZFELDER = ("nummer", "langtext", "iso_name", "datanorm_kurz", "statistikkennzeichen", "preisbezug_einheit",
                "preisbezug_menge", "un_code")


class MengeneinheitengruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    bestand_einheit: str = Field(..., max_length=10)
    ek_einheit: Optional[str] = Field(None, max_length=10)
    vk_einheit: Optional[str] = Field(None, max_length=10)
    preis_einheit: Optional[str] = Field(None, max_length=10)


class MengeneinheitengruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    bestand_einheit: str
    ek_einheit: Optional[str]
    vk_einheit: Optional[str]
    preis_einheit: Optional[str]
    aktiv: bool
    created_at: datetime


# ── Mengeneinheiten ───────────────────────────────────────────────────────────

@router.get("/stamm", response_model=list[MengeneinheitOut], summary="Mengeneinheiten auflisten")
def list_mengeneinheiten(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.artikel_mengeneinheiten
        WHERE tenant_id = :tid AND aktiv = true
        ORDER BY einheit_kuerzel
    """), {"tid": tenant_id}).fetchall()
    return [MengeneinheitOut(**dict(r._mapping)) for r in rows]


@router.post("/stamm", response_model=MengeneinheitOut, status_code=201, summary="Mengeneinheit anlegen", dependencies=SCHREIBEN["STAMMDATEN"])
def create_mengeneinheit(
    payload: MengeneinheitCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.artikel_mengeneinheiten
        WHERE tenant_id = :tid AND einheit_kuerzel = :kz
    """), {"tid": tenant_id, "kz": payload.einheit_kuerzel}).fetchone()
    if existing:
        raise HTTPException(409, f"Mengeneinheit '{payload.einheit_kuerzel}' bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.artikel_mengeneinheiten
            (id, tenant_id, einheit_kuerzel, bezeichnung, basis_einheit,
             umrechnungsfaktor, dezimalstellen, nummer, langtext, iso_name, datanorm_kurz,
             statistikkennzeichen, preisbezug_einheit, preisbezug_menge, un_code, aktiv)
        VALUES (:id, :tid, :kz, :bez, :basis, :faktor, :dez, :nummer, :langtext, :iso_name, :datanorm_kurz,
                :statistikkennzeichen, :preisbezug_einheit, :preisbezug_menge, :un_code, true)
    """), {
        "id": new_id, "tid": tenant_id, "kz": payload.einheit_kuerzel,
        "bez": payload.bezeichnung, "basis": payload.basis_einheit,
        "faktor": payload.umrechnungsfaktor, "dez": payload.dezimalstellen,
        **{feld: getattr(payload, feld) for feld in ZUSATZFELDER},
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.artikel_mengeneinheiten WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return MengeneinheitOut(**dict(row._mapping))


@router.put("/stamm/{einheit_kuerzel}", response_model=MengeneinheitOut, summary="Mengeneinheit aktualisieren", dependencies=SCHREIBEN["STAMMDATEN"])
def update_mengeneinheit(
    einheit_kuerzel: str,
    payload: MengeneinheitCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id, dezimalstellen, aktiv FROM domain_shared.artikel_mengeneinheiten
        WHERE tenant_id = :tid AND einheit_kuerzel = :kz
    """), {"tid": tenant_id, "kz": einheit_kuerzel}).fetchone()
    if not row:
        raise HTTPException(404, "Mengeneinheit nicht gefunden.")
    if row.aktiv and payload.dezimalstellen < int(row.dezimalstellen or 0):
        # a.eins: bei aktiven Einheiten nur nach oben, damit geschriebene Belege nicht nachtraeglich anders runden.
        raise HTTPException(409, f"Rundung einer aktiven Mengeneinheit nur nach oben aenderbar "
                                 f"(bisher {row.dezimalstellen}).")

    db.execute(text("""
        UPDATE domain_shared.artikel_mengeneinheiten
        SET bezeichnung = :bez, basis_einheit = :basis,
            umrechnungsfaktor = :faktor, dezimalstellen = :dez,
            nummer = :nummer, langtext = :langtext, iso_name = :iso_name, datanorm_kurz = :datanorm_kurz,
            statistikkennzeichen = :statistikkennzeichen, preisbezug_einheit = :preisbezug_einheit,
            preisbezug_menge = :preisbezug_menge, un_code = :un_code
        WHERE tenant_id = :tid AND einheit_kuerzel = :kz
    """), {
        "tid": tenant_id, "kz": einheit_kuerzel, "bez": payload.bezeichnung,
        "basis": payload.basis_einheit, "faktor": payload.umrechnungsfaktor,
        "dez": payload.dezimalstellen,
        **{feld: getattr(payload, feld) for feld in ZUSATZFELDER},
    })
    db.commit()
    updated = db.execute(text("""
        SELECT * FROM domain_shared.artikel_mengeneinheiten
        WHERE tenant_id = :tid AND einheit_kuerzel = :kz
    """), {"tid": tenant_id, "kz": einheit_kuerzel}).fetchone()
    return MengeneinheitOut(**dict(updated._mapping))


@router.delete("/stamm/{einheit_kuerzel}", summary="Mengeneinheit löschen",
    response_model=None, dependencies=SCHREIBEN["STAMMDATEN"])
def delete_mengeneinheit(
    einheit_kuerzel: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.artikel_mengeneinheiten SET aktiv = false
        WHERE tenant_id = :tid AND einheit_kuerzel = :kz
    """), {"tid": tenant_id, "kz": einheit_kuerzel})
    db.commit()
    return Response(status_code=204)


@router.post("/stamm/grundeinheiten", response_model=list[str], status_code=201,
             summary="Mitgelieferte Grundeinheiten einrichten", dependencies=SCHREIBEN["STAMMDATEN"])
def grundeinheiten_einrichten(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Legt die gaengigen Grundmengeneinheiten (Stueck, kg, dt, t, l ... mit UN/ECE-Code) an, soweit sie fehlen."""
    from app.services.mengeneinheiten_grund import richte_grundeinheiten_ein

    angelegt = richte_grundeinheiten_ein(db, tenant_id)
    db.commit()
    return angelegt


@router.get("/stamm/umrechnen", summary="Umrechnen",
    response_model=None
)
def umrechnen(
    wert: Decimal,
    von_einheit: str,
    nach_einheit: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Mengenumrechnung zwischen zwei Einheiten über gemeinsame Basiseinheit."""
    def get_me(kz: str):
        return db.execute(text("""
            SELECT * FROM domain_shared.artikel_mengeneinheiten
            WHERE tenant_id = :tid AND einheit_kuerzel = :kz AND aktiv = true
        """), {"tid": tenant_id, "kz": kz}).fetchone()

    von = get_me(von_einheit)
    nach = get_me(nach_einheit)
    if not von or not nach:
        raise HTTPException(404, "Mindestens eine Mengeneinheit nicht gefunden.")

    von_d = dict(von._mapping)
    nach_d = dict(nach._mapping)

    # Direkte Umrechnung wenn Basis gleich
    von_faktor = Decimal(str(von_d["umrechnungsfaktor"] or 1))
    nach_faktor = Decimal(str(nach_d["umrechnungsfaktor"] or 1))

    if von_d.get("basis_einheit") == nach_d.get("basis_einheit"):
        ergebnis = (wert * von_faktor / nach_faktor).quantize(Decimal("0.000001"))
        return {"ergebnis": float(ergebnis), "von": von_einheit, "nach": nach_einheit}

    raise HTTPException(422, "Keine gemeinsame Basiseinheit für Umrechnung gefunden.")


# ── Mengeneinheitengruppen ────────────────────────────────────────────────────

@router.get("/gruppen", response_model=list[MengeneinheitengruppeOut], summary="Mengeneinheitengruppen auflisten")
def list_mengeneinheitengruppen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.artikel_mengeneinheitengruppen
        WHERE tenant_id = :tid AND aktiv = true
        ORDER BY gruppe_nr
    """), {"tid": tenant_id}).fetchall()
    return [MengeneinheitengruppeOut(**dict(r._mapping)) for r in rows]


@router.get("/gruppen/{gruppe_nr}", response_model=MengeneinheitengruppeOut, summary="Mengeneinheitengruppe abrufen")
def get_mengeneinheitengruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.artikel_mengeneinheitengruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Mengeneinheitengruppe nicht gefunden.")
    return MengeneinheitengruppeOut(**dict(row._mapping))


@router.post("/gruppen", response_model=MengeneinheitengruppeOut, status_code=201, summary="Mengeneinheitengruppe anlegen", dependencies=SCHREIBEN["STAMMDATEN"])
def create_mengeneinheitengruppe(
    payload: MengeneinheitengruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.artikel_mengeneinheitengruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Mengeneinheitengruppe {payload.gruppe_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.artikel_mengeneinheitengruppen
            (id, tenant_id, gruppe_nr, bezeichnung, bestand_einheit,
             ek_einheit, vk_einheit, preis_einheit, aktiv)
        VALUES (:id, :tid, :nr, :bez, :best, :ek, :vk, :preis, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr,
        "bez": payload.bezeichnung, "best": payload.bestand_einheit,
        "ek": payload.ek_einheit, "vk": payload.vk_einheit,
        "preis": payload.preis_einheit,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.artikel_mengeneinheitengruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return MengeneinheitengruppeOut(**dict(row._mapping))


@router.put("/gruppen/{gruppe_nr}", response_model=MengeneinheitengruppeOut, summary="Mengeneinheitengruppe aktualisieren", dependencies=SCHREIBEN["STAMMDATEN"])
def update_mengeneinheitengruppe(
    gruppe_nr: str,
    payload: MengeneinheitengruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id FROM domain_shared.artikel_mengeneinheitengruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Mengeneinheitengruppe nicht gefunden.")

    db.execute(text("""
        UPDATE domain_shared.artikel_mengeneinheitengruppen
        SET bezeichnung = :bez, bestand_einheit = :best,
            ek_einheit = :ek, vk_einheit = :vk, preis_einheit = :preis
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {
        "tid": tenant_id, "nr": gruppe_nr, "bez": payload.bezeichnung,
        "best": payload.bestand_einheit, "ek": payload.ek_einheit,
        "vk": payload.vk_einheit, "preis": payload.preis_einheit,
    })
    db.commit()
    updated = db.execute(text("""
        SELECT * FROM domain_shared.artikel_mengeneinheitengruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr}).fetchone()
    return MengeneinheitengruppeOut(**dict(updated._mapping))


@router.delete("/gruppen/{gruppe_nr}", summary="Mengeneinheitengruppe löschen",
    response_model=None, dependencies=SCHREIBEN["STAMMDATEN"])
def delete_mengeneinheitengruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.artikel_mengeneinheitengruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)


@router.get("/stamm/{einheit_kuerzel}", response_model=MengeneinheitOut, summary="Mengeneinheit lesen")
def get_mengeneinheit(
    einheit_kuerzel: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Single record for the shared Human/CLI/MCP screen data source."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.artikel_mengeneinheiten
        WHERE tenant_id = :tid AND einheit_kuerzel = :key AND aktiv = true
    """), {"tid": tenant_id, "key": einheit_kuerzel}).fetchone()
    if row is None:
        raise HTTPException(404, "Mengeneinheit nicht gefunden.")
    return MengeneinheitOut(**dict(row._mapping))
