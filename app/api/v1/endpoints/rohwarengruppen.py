"""Rohwarengruppen [RWG] — Stammdaten für Rohwarenabrechnung.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 01 Kontrakt/Rohware):
  Rohwarengruppen [RWG] gruppieren Artikel, die im Einkauf und/oder Verkauf per
  Rohwarenabrechnung behandelt werden. Direktsprung: [RWG].

  Aufbau:
  1. Rohwarengruppe: Hauptkategorie (z.B. "Getreide EK", "Raps VK")
  2. Abrechnungsschema (Sorte): Unterebene je Rohwarengruppe
     (z.B. "Gerste normal", "Weizen B-Qualität")
  3. Qualitätsdefinitionen: Analysewerte je Schema mit Basiswert
     (z.B. Feuchtigkeit Basis 15,0–15,5 %, Protein Basis 12,5 %)
  4. Zu-/Abschlag-Staffeln: Preis-/Mengenkorrektur basierend auf Analysewert-
     Abweichungen vom Basiswert (EPA ROHQU)
  5. Analysewert-Korrektur-Tabellen: Korrektur eines Analysewertes anhand
     anderer Analysewerte (z.B. Feuchtigkeit korrigiert Proteinwert)

  Staffel-Typen:
  - einfacher_umrechnungsfaktor: Δ × Faktor = Ergebnis in %
  - gestaffelte_abrechnung: Summe über Intervalle (Δ × Intervall-Faktor)

  Ergebnis-Typen: preiszuschlag, mengenzuschlag, preisabschlag, mengenabschlag
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/rohware/gruppen",
                   tags=["Rohware - Gruppen & Abrechnungsschemata"])

GUELTIGE_ERGEBNIS_TYPEN = ("preiszuschlag", "mengenzuschlag", "preisabschlag", "mengenabschlag")
GUELTIGE_ABRECHNUNG_TYPEN = ("einfacher_umrechnungsfaktor", "gestaffelte_abrechnung")
GUELTIGE_POSITIONS_TYPEN = ("qualitaet", "kosten", "verguetung", "ware")


# ── Schemas ───────────────────────────────────────────────────────────────────

class RohwarengruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    artikel_nr: Optional[str] = None
    ek_aktiv: bool = True
    vk_aktiv: bool = False
    waehrung: str = Field(default="EUR", max_length=3)
    mengeneinheit: Optional[str] = None


class RohwarengruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    artikel_nr: Optional[str]
    ek_aktiv: bool
    vk_aktiv: bool
    waehrung: str
    mengeneinheit: Optional[str]
    aktiv: bool
    created_at: datetime


class AbrechnungsschemaCreate(BaseModel):
    schema_nr: str = Field(..., max_length=20)
    bezeichnung: str
    gruppe_id: str
    artikel_nr: Optional[str] = None


class AbrechnungsschemaOut(BaseModel):
    id: str
    schema_nr: str
    bezeichnung: str
    gruppe_id: str
    artikel_nr: Optional[str]
    aktiv: bool
    created_at: datetime


class RohwareQualitaetCreate(BaseModel):
    qualitaet_nr: str = Field(..., max_length=20)
    bezeichnung: str
    gruppe_id: str
    schema_id: Optional[str] = None
    basis_wert: Optional[Decimal] = None
    basis_wert_bis: Optional[Decimal] = None
    einheit: Optional[str] = None
    position_typ: str = Field(default="qualitaet")


class RohwareQualitaetOut(BaseModel):
    id: str
    qualitaet_nr: str
    bezeichnung: str
    gruppe_id: str
    schema_id: Optional[str]
    basis_wert: Optional[Decimal]
    basis_wert_bis: Optional[Decimal]
    einheit: Optional[str]
    position_typ: str
    aktiv: bool
    created_at: datetime


class StaffelZeileCreate(BaseModel):
    zeile_nr: int
    bis_wert: Decimal
    umrechnungsfaktor: Decimal = Field(..., description="Faktor für dieses Intervall")


class ZaStaffelCreate(BaseModel):
    staffel_nr: str = Field(..., max_length=20)
    bezeichnung: str
    gruppe_id: str
    qualitaet_id: Optional[str] = None
    ergebnis_typ: str = Field(default="preiszuschlag")
    abrechnung_typ: str = Field(default="einfacher_umrechnungsfaktor")
    basiserweiterung: Decimal = Field(default=Decimal("0"), ge=0)
    zeilen: list[StaffelZeileCreate] = []

    @model_validator(mode="after")
    def check_typen(self) -> "ZaStaffelCreate":
        if self.ergebnis_typ not in GUELTIGE_ERGEBNIS_TYPEN:
            raise ValueError(f"ergebnis_typ muss einer von {GUELTIGE_ERGEBNIS_TYPEN} sein.")
        if self.abrechnung_typ not in GUELTIGE_ABRECHNUNG_TYPEN:
            raise ValueError(f"abrechnung_typ muss einer von {GUELTIGE_ABRECHNUNG_TYPEN} sein.")
        return self


class StaffelZeileOut(BaseModel):
    id: str
    zeile_nr: int
    bis_wert: Decimal
    umrechnungsfaktor: Decimal


class ZaStaffelOut(BaseModel):
    id: str
    staffel_nr: str
    bezeichnung: str
    gruppe_id: str
    qualitaet_id: Optional[str]
    ergebnis_typ: str
    abrechnung_typ: str
    basiserweiterung: Decimal
    aktiv: bool
    created_at: datetime
    zeilen: list[StaffelZeileOut] = []


class StaffelBerechnungResult(BaseModel):
    analysewert: Decimal
    basiswert: Decimal
    basiserweiterung: Decimal
    delta: Decimal
    ergebnis_prozent: Decimal
    ergebnis_typ: str
    abrechnung_typ: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _berechne_staffel(zeilen: list, delta: Decimal, abrechnung_typ: str) -> Decimal:
    """Berechnet Ergebnis-Prozentwert aus Staffelzeilen."""
    if abrechnung_typ == "einfacher_umrechnungsfaktor":
        # Nächst höheren Faktor für delta finden
        zeilen_sorted = sorted(zeilen, key=lambda z: z["bis_wert"])
        for z in zeilen_sorted:
            if delta <= Decimal(str(z["bis_wert"])):
                return (delta * Decimal(str(z["umrechnungsfaktor"]))).quantize(Decimal("0.0001"))
        # Größtes Intervall
        if zeilen_sorted:
            return (delta * Decimal(str(zeilen_sorted[-1]["umrechnungsfaktor"]))).quantize(Decimal("0.0001"))
        return Decimal("0")
    else:
        # gestaffelte_abrechnung: Summe über Intervalle
        zeilen_sorted = sorted(zeilen, key=lambda z: z["bis_wert"])
        ergebnis = Decimal("0")
        verbleibend = delta
        vorheriger = Decimal("0")
        for z in zeilen_sorted:
            bis = Decimal(str(z["bis_wert"]))
            faktor = Decimal(str(z["umrechnungsfaktor"]))
            intervall = min(verbleibend, bis - vorheriger)
            if intervall <= 0:
                break
            ergebnis += (intervall * faktor).quantize(Decimal("0.0001"))
            verbleibend -= intervall
            vorheriger = bis
            if verbleibend <= 0:
                break
        return ergebnis


def _load_staffel_zeilen(db, staffel_id: str) -> list:
    rows = db.execute(text("""
        SELECT * FROM domain_shared.rohware_za_staffel_zeilen
        WHERE staffel_id = :sid ORDER BY zeile_nr
    """), {"sid": staffel_id}).fetchall()
    return [StaffelZeileOut(**dict(r._mapping)) for r in rows]


# ── Rohwarengruppen CRUD ──────────────────────────────────────────────────────

@router.get("", response_model=list[RohwarengruppeOut])
def list_rohwarengruppen(
    nur_aktive: bool = Query(True),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.rohwarengruppen WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if nur_aktive:
        sql += " AND aktiv = true"
    sql += " ORDER BY gruppe_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [RohwarengruppeOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=RohwarengruppeOut, status_code=201)
def create_rohwarengruppe(
    payload: RohwarengruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.rohwarengruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Rohwarengruppe {payload.gruppe_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.rohwarengruppen
            (id, tenant_id, gruppe_nr, bezeichnung, artikel_nr, ek_aktiv, vk_aktiv, waehrung, mengeneinheit)
        VALUES (:id, :tid, :nr, :bez, :anr, :ek, :vk, :whr, :me)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr,
        "bez": payload.bezeichnung, "anr": payload.artikel_nr,
        "ek": payload.ek_aktiv, "vk": payload.vk_aktiv,
        "whr": payload.waehrung, "me": payload.mengeneinheit,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.rohwarengruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return RohwarengruppeOut(**dict(row._mapping))


@router.delete("/{gruppe_nr}")
def delete_rohwarengruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.rohwarengruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)


# ── Abrechnungsschemata ───────────────────────────────────────────────────────

@router.get("/schemata", response_model=list[AbrechnungsschemaOut])
def list_schemata(
    gruppe_id: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.rohware_abrechnungsschemata WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if gruppe_id:
        sql += " AND gruppe_id = :gid"
        params["gid"] = gruppe_id
    sql += " ORDER BY schema_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [AbrechnungsschemaOut(**dict(r._mapping)) for r in rows]


@router.post("/schemata", response_model=AbrechnungsschemaOut, status_code=201)
def create_schema(
    payload: AbrechnungsschemaCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    gruppe = db.execute(text("""
        SELECT id FROM domain_shared.rohwarengruppen
        WHERE id = :gid AND tenant_id = :tid
    """), {"gid": payload.gruppe_id, "tid": tenant_id}).fetchone()
    if not gruppe:
        raise HTTPException(404, "Rohwarengruppe nicht gefunden.")

    existing = db.execute(text("""
        SELECT id FROM domain_shared.rohware_abrechnungsschemata
        WHERE tenant_id = :tid AND schema_nr = :nr
    """), {"tid": tenant_id, "nr": payload.schema_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Abrechnungsschema {payload.schema_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.rohware_abrechnungsschemata
            (id, tenant_id, schema_nr, bezeichnung, gruppe_id, artikel_nr)
        VALUES (:id, :tid, :nr, :bez, :gid, :anr)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.schema_nr,
        "bez": payload.bezeichnung, "gid": payload.gruppe_id, "anr": payload.artikel_nr,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.rohware_abrechnungsschemata WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return AbrechnungsschemaOut(**dict(row._mapping))


# ── Qualitätsdefinitionen ─────────────────────────────────────────────────────

@router.get("/qualitaeten", response_model=list[RohwareQualitaetOut])
def list_qualitaeten(
    gruppe_id: Optional[str] = Query(None),
    schema_id: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.rohware_qualitaeten WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if gruppe_id:
        sql += " AND gruppe_id = :gid"
        params["gid"] = gruppe_id
    if schema_id:
        sql += " AND schema_id = :sid"
        params["sid"] = schema_id
    sql += " ORDER BY qualitaet_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [RohwareQualitaetOut(**dict(r._mapping)) for r in rows]


@router.post("/qualitaeten", response_model=RohwareQualitaetOut, status_code=201)
def create_qualitaet(
    payload: RohwareQualitaetCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if payload.position_typ not in GUELTIGE_POSITIONS_TYPEN:
        raise HTTPException(422, f"position_typ muss einer von {GUELTIGE_POSITIONS_TYPEN} sein.")

    existing = db.execute(text("""
        SELECT id FROM domain_shared.rohware_qualitaeten
        WHERE tenant_id = :tid AND qualitaet_nr = :nr
    """), {"tid": tenant_id, "nr": payload.qualitaet_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Qualität {payload.qualitaet_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.rohware_qualitaeten
            (id, tenant_id, qualitaet_nr, bezeichnung, gruppe_id, schema_id,
             basis_wert, basis_wert_bis, einheit, position_typ)
        VALUES (:id, :tid, :nr, :bez, :gid, :sid, :bw, :bwb, :ein, :ptyp)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.qualitaet_nr,
        "bez": payload.bezeichnung, "gid": payload.gruppe_id, "sid": payload.schema_id,
        "bw": payload.basis_wert, "bwb": payload.basis_wert_bis,
        "ein": payload.einheit, "ptyp": payload.position_typ,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.rohware_qualitaeten WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return RohwareQualitaetOut(**dict(row._mapping))


# ── Zu-/Abschlag-Staffeln ─────────────────────────────────────────────────────

@router.get("/staffeln", response_model=list[ZaStaffelOut])
def list_staffeln(
    gruppe_id: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.rohware_za_staffeln WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if gruppe_id:
        sql += " AND gruppe_id = :gid"
        params["gid"] = gruppe_id
    sql += " ORDER BY staffel_nr"
    rows = db.execute(text(sql), params).fetchall()
    result = []
    for r in rows:
        d = dict(r._mapping)
        d["zeilen"] = _load_staffel_zeilen(db, d["id"])
        result.append(ZaStaffelOut(**d))
    return result


@router.post("/staffeln", response_model=ZaStaffelOut, status_code=201)
def create_staffel(
    payload: ZaStaffelCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.rohware_za_staffeln
        WHERE tenant_id = :tid AND staffel_nr = :nr
    """), {"tid": tenant_id, "nr": payload.staffel_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Staffel {payload.staffel_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.rohware_za_staffeln
            (id, tenant_id, staffel_nr, bezeichnung, gruppe_id, qualitaet_id,
             ergebnis_typ, abrechnung_typ, basiserweiterung)
        VALUES (:id, :tid, :nr, :bez, :gid, :qid, :etyp, :atyp, :bext)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.staffel_nr,
        "bez": payload.bezeichnung, "gid": payload.gruppe_id, "qid": payload.qualitaet_id,
        "etyp": payload.ergebnis_typ, "atyp": payload.abrechnung_typ,
        "bext": payload.basiserweiterung,
    })

    for zeile in payload.zeilen:
        db.execute(text("""
            INSERT INTO domain_shared.rohware_za_staffel_zeilen
                (id, tenant_id, staffel_id, zeile_nr, bis_wert, umrechnungsfaktor)
            VALUES (:id, :tid, :sid, :znr, :bw, :uf)
        """), {
            "id": uuid7(), "tid": tenant_id, "sid": new_id,
            "znr": zeile.zeile_nr, "bw": zeile.bis_wert, "uf": zeile.umrechnungsfaktor,
        })

    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.rohware_za_staffeln WHERE id = :id"
    ), {"id": new_id}).fetchone()
    d = dict(row._mapping)
    d["zeilen"] = _load_staffel_zeilen(db, new_id)
    return ZaStaffelOut(**d)


@router.post("/staffeln/{staffel_nr}/berechnen", response_model=StaffelBerechnungResult)
def staffel_berechnen(
    staffel_nr: str,
    analysewert: Decimal,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Berechnet Zu-/Abschlag-Ergebnis für einen gegebenen Analysewert."""
    row = db.execute(text("""
        SELECT s.*, q.basis_wert
        FROM domain_shared.rohware_za_staffeln s
        LEFT JOIN domain_shared.rohware_qualitaeten q ON q.id = s.qualitaet_id
        WHERE s.tenant_id = :tid AND s.staffel_nr = :nr AND s.aktiv = true
    """), {"tid": tenant_id, "nr": staffel_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Staffel nicht gefunden.")

    d = dict(row._mapping)
    basiswert = Decimal(str(d["basis_wert"] or 0))
    basiserweiterung = Decimal(str(d["basiserweiterung"]))
    delta = (analysewert - basiswert + basiserweiterung).quantize(Decimal("0.0001"))

    if delta < 0:
        delta = Decimal("0")

    zeilen = db.execute(text("""
        SELECT * FROM domain_shared.rohware_za_staffel_zeilen
        WHERE staffel_id = :sid ORDER BY zeile_nr
    """), {"sid": d["id"]}).fetchall()
    zeilen_dicts = [dict(z._mapping) for z in zeilen]

    ergebnis_prozent = _berechne_staffel(zeilen_dicts, delta, d["abrechnung_typ"])

    return StaffelBerechnungResult(
        analysewert=analysewert,
        basiswert=basiswert,
        basiserweiterung=basiserweiterung,
        delta=delta,
        ergebnis_prozent=ergebnis_prozent,
        ergebnis_typ=d["ergebnis_typ"],
        abrechnung_typ=d["abrechnung_typ"],
    )
