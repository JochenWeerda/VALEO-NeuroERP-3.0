"""FIBU Stammdaten: Zahlungsformulare [FIZAF], Zinsgruppen, Leergut-Artikelklassen.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 03 FIBU):

  Zahlungsformulare [FIZAF]:
    Je Formularklasse (Eingang/Ausgang) und Bank kann es unterschiedliche
    Formulare geben. Verknüpft Formularklasse + Formulareinrichtung + Bank.
    Wird bei der Freigabe von Zahlungsvorschlägen verwendet.

  Zinsgruppen:
    Differenzieren Konten für die Kontokorrentzinsberechnung. Stammdaten der
    Zinsen: Zinsgruppe mit Zinssatz, Zinsmethode (akt./360/365), Schwellwert.
    Zinsgruppe wird im Kundenstamm hinterlegt.

  Leergut-Artikelklassen:
    Artikel, die als Leergut/Pfand fungieren, werden über die Artikelklasse
    als Leergut gekennzeichnet. Leergutarten: Palette, Big-Bag, Fass, Flasche.
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


router = APIRouter(prefix="/fibu/stammdaten", tags=["FIBU - Zusatzstammdaten"])

GUELTIGE_FORMULARKLASSEN = {"eingang", "ausgang"}
GUELTIGE_ZINSMETHODEN = {"act_act", "act_360", "act_365", "30_360"}
GUELTIGE_LEERGUT_ARTEN = {"palette", "bigbag", "fass", "flasche", "behaelter", "sonstige"}


# ── Schemas ───────────────────────────────────────────────────────────────────

class ZahlungsformularCreate(BaseModel):
    formular_nr: str = Field(..., max_length=20)
    bezeichnung: str
    formularklasse: str
    bank_blz: Optional[str] = None
    bank_iban: Optional[str] = None
    formulareinrichtung: Optional[str] = None

    def model_post_init(self, __context):
        if self.formularklasse not in GUELTIGE_FORMULARKLASSEN:
            raise ValueError(f"Ungültige Formularklasse: {self.formularklasse}")


class ZahlungsformularOut(BaseModel):
    id: str
    formular_nr: str
    bezeichnung: str
    formularklasse: str
    bank_blz: Optional[str]
    bank_iban: Optional[str]
    formulareinrichtung: Optional[str]
    aktiv: bool
    created_at: datetime


class ZinsgruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    zinssatz: Decimal = Field(..., ge=0, le=100)
    zinsmethode: str = "act_360"
    schwellwert_tage: int = Field(0, ge=0)
    konto_zinsen: Optional[str] = None
    konto_zinsabschlagsteuer: Optional[str] = None

    def model_post_init(self, __context):
        if self.zinsmethode not in GUELTIGE_ZINSMETHODEN:
            raise ValueError(f"Ungültige Zinsmethode: {self.zinsmethode}")


class ZinsgruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    zinssatz: Decimal
    zinsmethode: str
    schwellwert_tage: int
    konto_zinsen: Optional[str]
    konto_zinsabschlagsteuer: Optional[str]
    aktiv: bool
    created_at: datetime


class LeergutArtCreate(BaseModel):
    art_nr: str = Field(..., max_length=20)
    bezeichnung: str
    leergut_typ: str = "palette"
    pfandwert: Optional[Decimal] = Field(None, ge=0)
    konto_leergut: Optional[str] = None

    def model_post_init(self, __context):
        if self.leergut_typ not in GUELTIGE_LEERGUT_ARTEN:
            raise ValueError(f"Ungültiger Leergut-Typ: {self.leergut_typ}")


class LeergutArtOut(BaseModel):
    id: str
    art_nr: str
    bezeichnung: str
    leergut_typ: str
    pfandwert: Optional[Decimal]
    konto_leergut: Optional[str]
    aktiv: bool
    created_at: datetime


# ── Zahlungsformulare CRUD ────────────────────────────────────────────────────

@router.get("/zahlungsformulare", response_model=list[ZahlungsformularOut], summary="Zahlungsformulare auflisten")
def list_zahlungsformulare(
    formularklasse: Optional[str] = None,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.zahlungsformulare
        WHERE tenant_id = :tid AND aktiv = true
    """
    params: dict = {"tid": tenant_id}
    if formularklasse:
        sql += " AND formularklasse = :fk"
        params["fk"] = formularklasse
    sql += " ORDER BY formular_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [ZahlungsformularOut(**dict(r._mapping)) for r in rows]


@router.post("/zahlungsformulare", response_model=ZahlungsformularOut, status_code=201, summary="Zahlungsformular anlegen")
def create_zahlungsformular(
    payload: ZahlungsformularCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.zahlungsformulare
        WHERE tenant_id = :tid AND formular_nr = :nr
    """), {"tid": tenant_id, "nr": payload.formular_nr}).fetchone():
        raise HTTPException(409, f"Zahlungsformular {payload.formular_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.zahlungsformulare
            (id, tenant_id, formular_nr, bezeichnung, formularklasse,
             bank_blz, bank_iban, formulareinrichtung)
        VALUES (:id, :tid, :nr, :bez, :fk, :blz, :iban, :feinr)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.formular_nr, "bez": payload.bezeichnung,
        "fk": payload.formularklasse, "blz": payload.bank_blz,
        "iban": payload.bank_iban, "feinr": payload.formulareinrichtung,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.zahlungsformulare WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ZahlungsformularOut(**dict(row._mapping))


@router.delete("/zahlungsformulare/{formular_nr}", summary="Zahlungsformular löschen",
    response_model=None
)
def delete_zahlungsformular(
    formular_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.zahlungsformulare SET aktiv = false
        WHERE tenant_id = :tid AND formular_nr = :nr
    """), {"tid": tenant_id, "nr": formular_nr})
    db.commit()
    return Response(status_code=204)


# ── Zinsgruppen CRUD ──────────────────────────────────────────────────────────

@router.get("/zinsgruppen", response_model=list[ZinsgruppeOut], summary="Zinsgruppen auflisten")
def list_zinsgruppen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.zinsgruppen
        WHERE tenant_id = :tid AND aktiv = true ORDER BY gruppe_nr
    """), {"tid": tenant_id}).fetchall()
    return [ZinsgruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/zinsgruppen", response_model=ZinsgruppeOut, status_code=201, summary="Zinsgruppe anlegen")
def create_zinsgruppe(
    payload: ZinsgruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.zinsgruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone():
        raise HTTPException(409, f"Zinsgruppe {payload.gruppe_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.zinsgruppen
            (id, tenant_id, gruppe_nr, bezeichnung, zinssatz, zinsmethode,
             schwellwert_tage, konto_zinsen, konto_zinsabschlagsteuer)
        VALUES (:id, :tid, :nr, :bez, :zs, :zm, :st, :kz, :kzst)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr, "bez": payload.bezeichnung,
        "zs": payload.zinssatz, "zm": payload.zinsmethode, "st": payload.schwellwert_tage,
        "kz": payload.konto_zinsen, "kzst": payload.konto_zinsabschlagsteuer,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.zinsgruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ZinsgruppeOut(**dict(row._mapping))


@router.delete("/zinsgruppen/{gruppe_nr}", summary="Zinsgruppe löschen",
    response_model=None
)
def delete_zinsgruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.zinsgruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)


# ── Leergutarten CRUD ─────────────────────────────────────────────────────────

@router.get("/leergutarten", response_model=list[LeergutArtOut], summary="Leergutarten auflisten")
def list_leergutarten(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.leergutarten
        WHERE tenant_id = :tid AND aktiv = true ORDER BY art_nr
    """), {"tid": tenant_id}).fetchall()
    return [LeergutArtOut(**dict(r._mapping)) for r in rows]


@router.post("/leergutarten", response_model=LeergutArtOut, status_code=201, summary="Leergutart anlegen")
def create_leergutart(
    payload: LeergutArtCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.leergutarten
        WHERE tenant_id = :tid AND art_nr = :nr
    """), {"tid": tenant_id, "nr": payload.art_nr}).fetchone():
        raise HTTPException(409, f"Leergutart {payload.art_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.leergutarten
            (id, tenant_id, art_nr, bezeichnung, leergut_typ, pfandwert, konto_leergut)
        VALUES (:id, :tid, :nr, :bez, :typ, :pfw, :kl)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.art_nr, "bez": payload.bezeichnung,
        "typ": payload.leergut_typ, "pfw": payload.pfandwert, "kl": payload.konto_leergut,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.leergutarten WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return LeergutArtOut(**dict(row._mapping))


@router.delete("/leergutarten/{art_nr}", summary="Leergutart löschen",
    response_model=None
)
def delete_leergutart(
    art_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.leergutarten SET aktiv = false
        WHERE tenant_id = :tid AND art_nr = :nr
    """), {"tid": tenant_id, "nr": art_nr})
    db.commit()
    return Response(status_code=204)
