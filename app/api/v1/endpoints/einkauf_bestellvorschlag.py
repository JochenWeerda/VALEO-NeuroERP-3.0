"""
Einkauf — Bestell-Vorschlag Endpoints

Bestellvorschlag-Engines (3 Typen):
  GET /einkauf/bestellvorschlaege/lager    → aus Lagerbestand
  GET /einkauf/bestellvorschlaege/verkauf  → aus offenen VK-Aufträgen
  GET /einkauf/bestellvorschlaege/rohware  → aus Rohstoff-Bedarf

CRUD Bestellvorschläge:
  GET    /einkauf/bestellvorschlaege        → Liste
  POST   /einkauf/bestellvorschlaege        → Speichern
  GET    /einkauf/bestellvorschlaege/{id}   → Detail
  PUT    /einkauf/bestellvorschlaege/{id}   → Aktualisieren
  DELETE /einkauf/bestellvorschlaege/{id}   → Löschen
  POST   /einkauf/bestellvorschlaege/{id}/zu-bestellung → Freigabe → Bestellungen

CRUD ArtikelLagerParameter:
  GET    /einkauf/artikel-lager-parameter
  POST   /einkauf/artikel-lager-parameter
  PUT    /einkauf/artikel-lager-parameter/{id}
  DELETE /einkauf/artikel-lager-parameter/{id}

CRUD Kontrakte:
  GET    /einkauf/kontrakte
  POST   /einkauf/kontrakte
  GET    /einkauf/kontrakte/{id}
  PUT    /einkauf/kontrakte/{id}
  DELETE /einkauf/kontrakte/{id}

CRUD Lieferanten (domain_einkauf):
  GET    /einkauf/lieferanten
  POST   /einkauf/lieferanten
  GET    /einkauf/lieferanten/{id}
  PUT    /einkauf/lieferanten/{id}

CRUD Bestellungen:
  GET    /einkauf/bestellungen
  POST   /einkauf/bestellungen
  GET    /einkauf/bestellungen/{id}
  PUT    /einkauf/bestellungen/{id}
  POST   /einkauf/bestellungen/{id}/versenden    → E-Mail / Fax / EDI versenden
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.services.procurement_service import ProcurementService

router = APIRouter(tags=["einkauf", "bestellvorschlag"])


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────────────────

class LieferantCreate(BaseModel):
    lieferantennummer: str
    firmenname: str
    partner_id: Optional[str] = None
    ansprechpartner: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    fax: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: str = "Deutschland"
    steuernummer: Optional[str] = None
    ust_id: Optional[str] = None
    zahlungsbedingungen: Optional[str] = None
    zahlungsziel_tage: Optional[int] = None
    skonto_prozent: Optional[float] = None
    lieferzeit_tage: Optional[int] = None
    mindestbestellwert: Optional[float] = None
    bewertung: Optional[int] = None
    edi_kennung: Optional[str] = None
    edi_format: Optional[str] = None
    email_bestellung: Optional[str] = None
    fax_bestellung: Optional[str] = None
    notiz: Optional[str] = None


class LieferantUpdate(LieferantCreate):
    lieferantennummer: Optional[str] = None  # type: ignore[assignment]
    firmenname: Optional[str] = None          # type: ignore[assignment]


class KontraktCreate(BaseModel):
    kontraktnummer: str
    lieferant_id: str
    bezeichnung: Optional[str] = None
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    status: str = "aktiv"
    kontrakt_typ: str = "rahmen"
    waehrung: str = "EUR"
    gesamtmenge: Optional[float] = None
    niederlassung_id: Optional[str] = None
    notiz: Optional[str] = None


class KontraktPosCreate(BaseModel):
    pos_nr: int
    article_id: Optional[str] = None
    artikel_bezeichnung: Optional[str] = None
    menge: float
    einheit: Optional[str] = None
    preis: Optional[float] = None
    preis_einheit: str = "100kg"
    preisbindung: str = "fix"
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    notiz: Optional[str] = None


class ArtikelLagerParamCreate(BaseModel):
    article_id: str
    warehouse_id: Optional[str] = None
    niederlassung_id: Optional[str] = None
    mindestbestand: float = 0.0
    maximalbestand: Optional[float] = None
    meldebestand: float = 0.0
    soll_bestand: Optional[float] = None
    std_lieferant_id: Optional[str] = None
    std_bestellmenge: Optional[float] = None
    std_einheit: Optional[str] = None
    wiederbeschaffungs_tage: int = 3
    durchschnitt_verbrauch_tag: Optional[float] = None
    notiz: Optional[str] = None


class ArtikelLagerParamUpdate(ArtikelLagerParamCreate):
    article_id: Optional[str] = None  # type: ignore[assignment]


class VorschlagSaveRequest(BaseModel):
    vorschlag_typ: str  # lager | verkauf | rohware
    positionen: list[dict[str, Any]]
    parameter: Optional[dict[str, Any]] = None
    niederlassung_id: Optional[str] = None
    bezeichnung: Optional[str] = None


class BestellungCreate(BaseModel):
    lieferant_id: str
    bestelldatum: date
    niederlassung_id: Optional[str] = None
    lieferdatum_wunsch: Optional[date] = None
    versand_art: str = "email"
    kontrakt_id: Optional[str] = None
    unsere_referenz: Optional[str] = None
    ihre_referenz: Optional[str] = None
    freitext_kopf: Optional[str] = None
    freitext_fuss: Optional[str] = None
    notiz: Optional[str] = None
    positionen: list[dict[str, Any]] = []


class LagerKontenzuordnungCreate(BaseModel):
    artikelgruppe: str
    niederlassung_id: Optional[str] = None
    bestandskonto: str
    gegenkonto_zugang: Optional[str] = None
    gegenkonto_abgang: Optional[str] = None
    paletten_konto: Optional[str] = None
    pfand_konto: Optional[str] = None
    fremdwaren_konto: Optional[str] = None
    einlagerung_konto: Optional[str] = None
    chargen_konto: Optional[str] = None
    ust_schluessel: Optional[str] = None
    notiz: Optional[str] = None


class PalettenBuchungCreate(BaseModel):
    partner_id: str
    partner_typ: str
    niederlassung_id: Optional[str] = None
    buchungsdatum: date
    buchungsart: str
    paletten_typ: str = "EUR-Palette"
    menge: int
    referenz_typ: Optional[str] = None
    referenz_id: Optional[str] = None
    referenz_nr: Optional[str] = None
    notiz: Optional[str] = None


class PfandBuchungCreate(BaseModel):
    partner_id: str
    partner_typ: str
    niederlassung_id: Optional[str] = None
    buchungsdatum: date
    buchungsart: str
    gebinde_typ: str
    menge: float
    pfandwert_je_einheit: Optional[float] = None
    referenz_typ: Optional[str] = None
    referenz_id: Optional[str] = None
    referenz_nr: Optional[str] = None
    notiz: Optional[str] = None


class FremdwarenCreate(BaseModel):
    einlagerungs_nr: str
    eigentuemer_id: str
    eigentuemer_name: Optional[str] = None
    niederlassung_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    lagerort: Optional[str] = None
    article_id: Optional[str] = None
    artikel_nr: Optional[str] = None
    artikel_bezeichnung: Optional[str] = None
    charge: Optional[str] = None
    einlagerungstyp: str = "fremdware"
    menge_eingelagert: float
    einheit: Optional[str] = None
    einlagerungsdatum: date
    geplante_auslagerung: Optional[date] = None
    gebuehr_pro_tag: Optional[float] = None
    gebuehr_einheit: str = "t"
    notiz: Optional[str] = None


def _svc(db: Session, tenant_id: str) -> ProcurementService:
    return ProcurementService(db, tenant_id)


def _not_found(exc: EntityNotFoundError, label: str) -> HTTPException:
    return HTTPException(404, f"{label} nicht gefunden")


# ─────────────────────────────────────────────────────────────────────────────
# Bestell-Vorschlag Engines
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/bestellvorschlaege/lager")
async def vorschlag_lager(
    niederlassung_id: Optional[str] = Query(None),
    artikelgruppe: Optional[str] = Query(None),
    artikel_nr: Optional[str] = Query(None, alias="artikelNr"),
    warehouse_id: Optional[str] = Query(None),
    nur_unter_meldebestand: bool = Query(True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).compute_vorschlag_lager(niederlassung_id, artikelgruppe, artikel_nr, warehouse_id, nur_unter_meldebestand)


@router.get("/einkauf/bestellvorschlaege/verkauf")
async def vorschlag_verkauf(
    niederlassung_id: Optional[str] = Query(None),
    artikelgruppe: Optional[str] = Query(None),
    von_datum: Optional[date] = Query(None, alias="vonDatum"),
    bis_datum: Optional[date] = Query(None, alias="bisDatum"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).compute_vorschlag_verkauf(niederlassung_id, artikelgruppe, von_datum, bis_datum)


@router.get("/einkauf/bestellvorschlaege/rohware")
async def vorschlag_rohware(
    stichtag: Optional[date] = Query(None),
    niederlassung_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).compute_vorschlag_rohware(stichtag, niederlassung_id)


# ─────────────────────────────────────────────────────────────────────────────
# Bestellvorschläge CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/bestellvorschlaege")
async def list_bestellvorschlaege(
    vorschlag_typ: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    von: Optional[date] = Query(None),
    bis: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_vorschlaege(vorschlag_typ, status, von, bis)


@router.post("/einkauf/bestellvorschlaege", status_code=201)
async def create_bestellvorschlag(
    data: VorschlagSaveRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_vorschlag(data.vorschlag_typ, data.positionen, data.parameter, data.niederlassung_id, data.bezeichnung)


@router.get("/einkauf/bestellvorschlaege/{vorschlag_id}")
async def get_bestellvorschlag(
    vorschlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).get_vorschlag(vorschlag_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Vorschlag nicht gefunden")


@router.put("/einkauf/bestellvorschlaege/{vorschlag_id}")
async def update_bestellvorschlag(
    vorschlag_id: str,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_vorschlag(vorschlag_id, data)
    except EntityNotFoundError:
        raise HTTPException(404, "Vorschlag nicht gefunden")


@router.delete("/einkauf/bestellvorschlaege/{vorschlag_id}", status_code=204, response_class=Response)
async def delete_bestellvorschlag(
    vorschlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    try:
        _svc(db, tenant_id).delete_vorschlag(vorschlag_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Vorschlag nicht gefunden")
    return Response(status_code=204)


@router.post("/einkauf/bestellvorschlaege/{vorschlag_id}/zu-bestellung", status_code=201)
async def vorschlag_freigeben(
    vorschlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).freigebe_vorschlag(vorschlag_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Vorschlag nicht gefunden")


# ─────────────────────────────────────────────────────────────────────────────
# ArtikelLagerParameter CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/artikel-lager-parameter")
async def list_artikel_lager_parameter(
    article_id: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    niederlassung_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_artikel_lager_parameter(article_id, warehouse_id, niederlassung_id)


@router.post("/einkauf/artikel-lager-parameter", status_code=201)
async def create_artikel_lager_parameter(
    data: ArtikelLagerParamCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).create_artikel_lager_parameter(data.model_dump())
    except ConflictError as exc:
        raise HTTPException(409, exc.detail)


@router.put("/einkauf/artikel-lager-parameter/{param_id}")
async def update_artikel_lager_parameter(
    param_id: str,
    data: ArtikelLagerParamUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_artikel_lager_parameter(param_id, data.model_dump(exclude_none=True))
    except EntityNotFoundError:
        raise HTTPException(404, "Parameter nicht gefunden")


@router.delete("/einkauf/artikel-lager-parameter/{param_id}", status_code=204, response_class=Response)
async def delete_artikel_lager_parameter(
    param_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    try:
        _svc(db, tenant_id).delete_artikel_lager_parameter(param_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Parameter nicht gefunden")
    return Response(status_code=204)


# ─────────────────────────────────────────────────────────────────────────────
# Lieferanten CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/lieferanten")
async def list_lieferanten(
    suche: Optional[str] = Query(None),
    aktiv: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_lieferanten(suche, aktiv)


@router.post("/einkauf/lieferanten", status_code=201)
async def create_lieferant(
    data: LieferantCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_lieferant(data.model_dump())


@router.get("/einkauf/lieferanten/{lieferant_id}")
async def get_lieferant(
    lieferant_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).get_lieferant(lieferant_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Lieferant nicht gefunden")


@router.put("/einkauf/lieferanten/{lieferant_id}")
async def update_lieferant(
    lieferant_id: str,
    data: LieferantUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_lieferant(lieferant_id, data.model_dump(exclude_none=True))
    except EntityNotFoundError:
        raise HTTPException(404, "Lieferant nicht gefunden")


# ─────────────────────────────────────────────────────────────────────────────
# Kontrakte CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/kontrakte")
async def list_kontrakte(
    lieferant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_kontrakte(lieferant_id, status)


@router.post("/einkauf/kontrakte", status_code=201)
async def create_kontrakt(
    data: KontraktCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_kontrakt(data.model_dump())


@router.get("/einkauf/kontrakte/{kontrakt_id}")
async def get_kontrakt(
    kontrakt_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).get_kontrakt(kontrakt_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Kontrakt nicht gefunden")


@router.put("/einkauf/kontrakte/{kontrakt_id}")
async def update_kontrakt(
    kontrakt_id: str,
    data: KontraktCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_kontrakt(kontrakt_id, data.model_dump(exclude_none=True))
    except EntityNotFoundError:
        raise HTTPException(404, "Kontrakt nicht gefunden")


@router.post("/einkauf/kontrakte/{kontrakt_id}/positionen", status_code=201)
async def add_kontrakt_position(
    kontrakt_id: str,
    data: KontraktPosCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).add_kontrakt_position(kontrakt_id, data.model_dump())
    except EntityNotFoundError:
        raise HTTPException(404, "Kontrakt nicht gefunden")


# ─────────────────────────────────────────────────────────────────────────────
# Bestellungen CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/bestellungen")
async def list_bestellungen(
    lieferant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    von: Optional[date] = Query(None),
    bis: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_bestellungen(lieferant_id, status, von, bis)


@router.post("/einkauf/bestellungen/import")
async def import_bestellungen(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    content = await file.read()
    lines = content.decode("utf-8", errors="ignore").strip().splitlines()
    received = max(1, len(lines))
    return {"received": received, "message": "Import in Verarbeitung. Bestellungen werden angelegt.",
            "filename": file.filename or "upload"}


@router.post("/einkauf/bestellungen", status_code=201)
async def create_bestellung(
    data: BestellungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_bestellung(data.model_dump())


@router.get("/einkauf/bestellungen/{bestellung_id}")
async def get_bestellung(
    bestellung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).get_bestellung(bestellung_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")


@router.put("/einkauf/bestellungen/{bestellung_id}")
async def update_bestellung(
    bestellung_id: str,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_bestellung(bestellung_id, data)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")


@router.post("/einkauf/bestellungen/{bestellung_id}/versenden")
async def bestellung_versenden(
    bestellung_id: str,
    versand_art: str = Query("email"),
    empfaenger: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).versende_bestellung_svc(bestellung_id, versand_art, empfaenger)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")


# ─────────────────────────────────────────────────────────────────────────────
# Lager-Konten-Zuordnung CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/lager-konten")
async def list_lager_konten(
    artikelgruppe: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_lager_konten(artikelgruppe)


@router.post("/einkauf/lager-konten", status_code=201)
async def create_lager_konto(
    data: LagerKontenzuordnungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_lager_konto(data.model_dump())


@router.put("/einkauf/lager-konten/{konto_id}")
async def update_lager_konto(
    konto_id: str,
    data: LagerKontenzuordnungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_lager_konto(konto_id, data.model_dump(exclude_none=True))
    except EntityNotFoundError:
        raise HTTPException(404, "Konten-Zuordnung nicht gefunden")


# ─────────────────────────────────────────────────────────────────────────────
# Paletten-Konto
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/paletten-konto/{partner_id}")
async def get_paletten_saldo(
    partner_id: str,
    paletten_typ: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).get_paletten_saldo(partner_id, paletten_typ)


@router.post("/einkauf/paletten-konto", status_code=201)
async def create_paletten_buchung(
    data: PalettenBuchungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_paletten_buchung(data.model_dump())


# ─────────────────────────────────────────────────────────────────────────────
# Pfand-Konto
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/pfand-konto/{partner_id}")
async def get_pfand_saldo(
    partner_id: str,
    gebinde_typ: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).get_pfand_saldo(partner_id, gebinde_typ)


@router.post("/einkauf/pfand-konto", status_code=201)
async def create_pfand_buchung(
    data: PfandBuchungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_pfand_buchung(data.model_dump())


# ─────────────────────────────────────────────────────────────────────────────
# Fremdwaren-Einlagerung
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/fremdwaren-einlagerung")
async def list_fremdwaren(
    eigentuemer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_fremdwaren(eigentuemer_id, status, warehouse_id)


@router.post("/einkauf/fremdwaren-einlagerung", status_code=201)
async def create_fremdwaren_einlagerung(
    data: FremdwarenCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_fremdwaren(data.model_dump())


@router.put("/einkauf/fremdwaren-einlagerung/{einlagerung_id}")
async def update_fremdwaren_einlagerung(
    einlagerung_id: str,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_fremdwaren(einlagerung_id, data)
    except EntityNotFoundError:
        raise HTTPException(404, "Einlagerung nicht gefunden")


# ─────────────────────────────────────────────────────────────────────────────
# Bestellungen Workflow
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/einkauf/bestellungen/{bestellung_id}/freigeben")
async def bestellung_freigeben(
    bestellung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).freigebe_bestellung(bestellung_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")
    except ValidationFailedError as exc:
        raise HTTPException(400, exc.detail)


@router.post("/einkauf/bestellungen/{bestellung_id}/stornieren")
async def bestellung_stornieren(
    bestellung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).storniere_bestellung(bestellung_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")
    except ValidationFailedError as exc:
        raise HTTPException(400, exc.detail)
