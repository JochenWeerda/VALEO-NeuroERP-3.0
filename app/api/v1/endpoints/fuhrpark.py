"""
Fuhrpark API Endpoints - zvoove style master data mask.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional
import uuid

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.repository import (
    FahrzeugRepository,
    FuhrparkAusgehendesDokumentRepository,
    FuhrparkRechnungRepository,
    FuhrparkTerminartRepository,
)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class FuhrparkOut(BaseSchema):
    """Typed response schema for FuhrparkOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/fuhrpark", tags=["Fuhrpark"])


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _to_dict(model: Any) -> dict:
    mapper = sa_inspect(model.__class__)
    data = {}
    for column in mapper.columns:
        key = column.key
        data[key] = _serialize_value(getattr(model, key))
    return data


class FuhrparkFahrzeugPayload(BaseModel):
    ro_nummer: Optional[str] = None
    is_neu: bool = False
    betrieb: Optional[str] = None
    bereich: Optional[str] = None
    pol_kennzeichen: Optional[str] = None
    kennzeichen: str = Field(..., min_length=2, max_length=20)
    typ: str = Field(..., min_length=2, max_length=50)
    marke: Optional[str] = None
    modell: Optional[str] = None
    baujahr: Optional[int] = None
    verwendung: Optional[str] = None
    kfz_brief_nummer: Optional[str] = None
    schadstoffgruppe: Optional[str] = None
    leistung_kw: Optional[float] = None
    kraftstoff: Optional[str] = None
    fahrgestellnummer: Optional[str] = None
    erstzulassung: Optional[datetime] = None
    ausstattung: Optional[str] = None
    fahrtenschreiber_vorhanden: bool = False
    ahk_vorhanden: bool = False
    ladekran_vorhanden: bool = False
    fahrer_name: Optional[str] = None
    fahrer_vorname: Optional[str] = None
    kilometerstand: float = 0
    km_stand_alle_eintraege: bool = False
    bestellnummer: Optional[str] = None
    bestelldatum: Optional[datetime] = None
    haendler: Optional[str] = None
    zustand: Optional[str] = "neu"
    kaufsumme_eur: Optional[float] = None
    kaufdatum: Optional[datetime] = None
    verkaufsdatum: Optional[datetime] = None
    abmeldedatum: Optional[datetime] = None
    kostenstelle: Optional[str] = None
    abschreibungsart: Optional[str] = None
    afa_jahre: Optional[int] = None
    afa_eur_jaehrlich: Optional[float] = None
    afa_eur_monatlich: Optional[float] = None
    leasingdauer_monate: Optional[int] = None
    leasinggesellschaft: Optional[str] = None
    leasingrate_eur: Optional[float] = None
    kfz_steuer_eur: Optional[float] = None
    kfz_steuernummer: Optional[str] = None
    kontierung: Optional[str] = None
    finanzamt: Optional[str] = None
    versicherungs_gesellschaft: Optional[str] = None
    versicherungsschein_nr: Optional[str] = None
    versicherung_satz_eur_monat: Optional[float] = None
    versicherung_haftpflicht: bool = False
    versicherung_kasko: bool = False
    naechster_tuev_termin: Optional[datetime] = None
    naechster_asu_termin: Optional[datetime] = None
    naechste_inspektion: Optional[datetime] = None
    leergewicht_kg: Optional[float] = None
    nutzlast_kg: Optional[float] = None
    gesamtgewicht_kg: Optional[float] = None
    anhaengerlast_kg: Optional[float] = None
    winterreifen_vorhanden: bool = False
    winterreifen_eingelagert: bool = False
    handy_freisprecheinrichtung: bool = False
    handy_fabrikat: Optional[str] = None
    handy_rufnummer: Optional[str] = None
    status: Optional[str] = "verfuegbar"


class DruckerSetupPayload(BaseModel):
    drucker_name: str = Field(..., min_length=2, max_length=255)


class UnfallAnzeigePayload(BaseModel):
    datum: datetime
    ort: str = Field(..., min_length=2, max_length=255)
    beschreibung: str = Field(..., min_length=3)


class FuhrparkTerminartPayload(BaseModel):
    terminart: str = Field(..., min_length=2, max_length=120)
    intervall_monate: int = Field(0, ge=0, le=1200)
    intervall_km: int = Field(0, ge=0, le=2_000_000)


class FuhrparkRechnungPayload(BaseModel):
    rechnungs_nr: str = Field(..., min_length=3, max_length=80)
    datum: datetime
    fahrzeug_id: Optional[str] = None
    fahrzeug_kennzeichen: Optional[str] = None
    sachkonto: Optional[str] = None
    kostenart: Optional[str] = None
    betrag_eur: float = Field(..., ge=0)
    notiz: Optional[str] = None


class FuhrparkAusgehendesDokumentPayload(BaseModel):
    beleg_typ: str = Field(..., min_length=2, max_length=120)
    formular: Optional[str] = Field(default=None, max_length=80)
    ziel_modul: Optional[str] = Field(default=None, max_length=255)
    beschreibung: Optional[str] = None
    aktiv: bool = True
    letzter_druck: Optional[datetime] = None


@router.get("/fahrzeuge", response_model=list[FuhrparkOut], summary="Fahrzeuge auflisten")
async def list_fahrzeuge(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    repo = FahrzeugRepository(db)
    if status:
        return [_to_dict(x) for x in repo.get_by_status(status)]
    return [_to_dict(x) for x in repo.get_all(skip=skip, limit=limit)]


@router.get("/fahrzeuge/{fahrzeug_id}", response_model=FuhrparkOut, summary="Fahrzeug abrufen")
async def get_fahrzeug(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return _to_dict(fahrzeug)


@router.post("/fahrzeuge", response_model=FuhrparkOut, status_code=201, summary="Fahrzeug anlegen")
async def create_fahrzeug(payload: FuhrparkFahrzeugPayload, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    existing = repo.get_by_kennzeichen(payload.kennzeichen)
    if existing:
        raise HTTPException(status_code=409, detail="Kennzeichen already exists")
    fahrzeug = repo.create(payload.model_dump(exclude_none=True))
    return _to_dict(fahrzeug)


@router.patch("/fahrzeuge/{fahrzeug_id}", response_model=FuhrparkOut, summary="Fahrzeug aktualisieren")
async def update_fahrzeug(
    fahrzeug_id: str,
    payload: FuhrparkFahrzeugPayload,
    db: Session = Depends(get_db),
):
    repo = FahrzeugRepository(db)
    existing = repo.get_by_id(fahrzeug_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    if payload.kennzeichen and payload.kennzeichen != existing.kennzeichen:
        duplicate = repo.get_by_kennzeichen(payload.kennzeichen)
        if duplicate:
            raise HTTPException(status_code=409, detail="Kennzeichen already exists")
    fahrzeug = repo.update(fahrzeug_id, payload.model_dump(exclude_none=True))
    return _to_dict(fahrzeug)


@router.delete("/fahrzeuge/{fahrzeug_id}", status_code=204, response_class=Response, response_model=None, summary="Fahrzeug löschen")
async def delete_fahrzeug(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    if not repo.delete(fahrzeug_id):
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")


@router.post("/fahrzeuge/{fahrzeug_id}/drucker-einrichten", response_model=FuhrparkOut, summary="Fahrzeug printer setup")
async def setup_fahrzeug_printer(
    fahrzeug_id: str,
    payload: DruckerSetupPayload,
    db: Session = Depends(get_db),
):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return {"ok": True, "fahrzeug_id": fahrzeug_id, "drucker_name": payload.drucker_name}


@router.post("/fahrzeuge/{fahrzeug_id}/drucken", response_model=FuhrparkOut, summary="Fahrzeugakte drucken")
async def print_fahrzeugakte(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return {"ok": True, "fahrzeug_id": fahrzeug_id, "aktion": "fahrzeugakte_gedruckt"}


@router.post("/fahrzeuge/{fahrzeug_id}/unfall-anzeige", response_model=FuhrparkOut, summary="Unfall anzeige anlegen")
async def create_unfall_anzeige(
    fahrzeug_id: str,
    payload: UnfallAnzeigePayload,
    db: Session = Depends(get_db),
):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return {
        "ok": True,
        "fahrzeug_id": fahrzeug_id,
        "datum": payload.datum.isoformat(),
        "ort": payload.ort,
        "beschreibung": payload.beschreibung,
    }


@router.get("/terminarten", response_model=list[FuhrparkOut], summary="Terminarten auflisten")
async def list_terminarten(db: Session = Depends(get_db)):
    repo = FuhrparkTerminartRepository(db)
    return [_to_dict(row) for row in repo.get_all()]


@router.post("/terminarten", response_model=FuhrparkOut, status_code=201, summary="Terminart anlegen")
async def create_terminart(payload: FuhrparkTerminartPayload, db: Session = Depends(get_db)):
    repo = FuhrparkTerminartRepository(db)
    duplicate = repo.get_by_name(payload.terminart)
    if duplicate:
        raise HTTPException(status_code=409, detail="Terminart already exists")
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/terminarten/{terminart_id}", response_model=FuhrparkOut, summary="Terminart aktualisieren")
async def update_terminart(
    terminart_id: str,
    payload: FuhrparkTerminartPayload,
    db: Session = Depends(get_db),
):
    repo = FuhrparkTerminartRepository(db)
    existing = repo.get_by_id(terminart_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Terminart {terminart_id} not found")
    if payload.terminart != existing.terminart:
        duplicate = repo.get_by_name(payload.terminart)
        if duplicate:
            raise HTTPException(status_code=409, detail="Terminart already exists")
    updated = repo.update(terminart_id, payload.model_dump())
    return _to_dict(updated)


@router.delete("/terminarten/{terminart_id}", status_code=204, response_class=Response, response_model=None, summary="Terminart löschen")
async def delete_terminart(terminart_id: str, db: Session = Depends(get_db)):
    repo = FuhrparkTerminartRepository(db)
    if not repo.delete(terminart_id):
        raise HTTPException(status_code=404, detail=f"Terminart {terminart_id} not found")


@router.get("/rechnungen", response_model=list[FuhrparkOut], summary="Rechnungen auflisten")
async def list_rechnungen(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    repo = FuhrparkRechnungRepository(db)
    return [_to_dict(row) for row in repo.get_all(skip=skip, limit=limit)]


@router.post("/rechnungen", response_model=FuhrparkOut, status_code=201, summary="Rechnung anlegen")
async def create_rechnung(payload: FuhrparkRechnungPayload, db: Session = Depends(get_db)):
    repo = FuhrparkRechnungRepository(db)
    duplicate = repo.get_by_rechnungs_nr(payload.rechnungs_nr)
    if duplicate:
        raise HTTPException(status_code=409, detail="Rechnungsnummer already exists")
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/rechnungen/{rechnung_id}", response_model=FuhrparkOut, summary="Rechnung aktualisieren")
async def update_rechnung(
    rechnung_id: str,
    payload: FuhrparkRechnungPayload,
    db: Session = Depends(get_db),
):
    repo = FuhrparkRechnungRepository(db)
    existing = repo.get_by_id(rechnung_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Rechnung {rechnung_id} not found")
    if payload.rechnungs_nr != existing.rechnungs_nr:
        duplicate = repo.get_by_rechnungs_nr(payload.rechnungs_nr)
        if duplicate:
            raise HTTPException(status_code=409, detail="Rechnungsnummer already exists")
    updated = repo.update(rechnung_id, payload.model_dump())
    return _to_dict(updated)


@router.delete("/rechnungen/{rechnung_id}", status_code=204, response_class=Response, response_model=None, summary="Rechnung löschen")
async def delete_rechnung(rechnung_id: str, db: Session = Depends(get_db)):
    repo = FuhrparkRechnungRepository(db)
    if not repo.delete(rechnung_id):
        raise HTTPException(status_code=404, detail=f"Rechnung {rechnung_id} not found")


@router.get("/ausgehende-dokumente", response_model=list[FuhrparkOut], summary="Ausgehende dokumente auflisten")
async def list_ausgehende_dokumente(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    return [_to_dict(row) for row in repo.get_all(skip=skip, limit=limit)]


@router.post("/ausgehende-dokumente", response_model=FuhrparkOut, status_code=201, summary="Ausgehendes dokument anlegen")
async def create_ausgehendes_dokument(
    payload: FuhrparkAusgehendesDokumentPayload,
    db: Session = Depends(get_db),
):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/ausgehende-dokumente/{dokument_id}", response_model=FuhrparkOut, summary="Ausgehendes dokument aktualisieren")
async def update_ausgehendes_dokument(
    dokument_id: str,
    payload: FuhrparkAusgehendesDokumentPayload,
    db: Session = Depends(get_db),
):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    existing = repo.get_by_id(dokument_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Ausgehendes Dokument {dokument_id} not found")
    updated = repo.update(dokument_id, payload.model_dump())
    return _to_dict(updated)


@router.delete("/ausgehende-dokumente/{dokument_id}", status_code=204, response_class=Response, response_model=None, summary="Ausgehendes dokument löschen")
async def delete_ausgehendes_dokument(dokument_id: str, db: Session = Depends(get_db)):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    if not repo.delete(dokument_id):
        raise HTTPException(status_code=404, detail=f"Ausgehendes Dokument {dokument_id} not found")


# ─────────────────────────────────────────────────────────────────────────────
# VERTIEFUNG: Statushistorie, Schadensfälle, Bußgeld, Wartungsvorhersage,
#             Leasing-Rückgabe  (FUHRPARK-VERTIEFUNG-001)
# ─────────────────────────────────────────────────────────────────────────────

def _new_id(prefix: str) -> str:
    return f"{prefix}-{str(uuid.uuid4())[:8].upper()}"


def _ensure_fahrzeug(fahrzeug_id: str, db: Session):
    repo = FahrzeugRepository(db)
    fz = repo.get_by_id(fahrzeug_id)
    if not fz:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} nicht gefunden")
    return fz


# ── Payloads ──────────────────────────────────────────────────────────────────

class StatusWechselPayload(BaseModel):
    zu_status: str = Field(..., description="verfuegbar|unterwegs|wartung|ausgeschieden")
    grund: Optional[str] = None
    benutzer: Optional[str] = None
    km_stand: Optional[float] = None


class SchadenPayload(BaseModel):
    datum: datetime
    ort: str = Field(..., min_length=2, max_length=255)
    beschreibung: str = Field(..., min_length=3)
    schadenhoehe_eur: Optional[float] = None
    versicherung_gemeldet: bool = False
    versicherungs_nr: Optional[str] = None
    gegner_kennzeichen: Optional[str] = None
    polizei_aktenzeichen: Optional[str] = None
    status: str = "offen"
    erstellt_von: Optional[str] = None


class SchadenUpdatePayload(BaseModel):
    schadenhoehe_eur: Optional[float] = None
    versicherung_gemeldet: Optional[bool] = None
    versicherungs_nr: Optional[str] = None
    status: Optional[str] = None
    abgeschlossen_am: Optional[datetime] = None
    polizei_aktenzeichen: Optional[str] = None
    notiz: Optional[str] = None


class BussgeldPayload(BaseModel):
    datum: datetime
    tatbestand: str = Field(..., min_length=3, max_length=255)
    betrag_eur: float = Field(..., ge=0)
    fahrer_id: Optional[str] = None
    ort: Optional[str] = None
    faellig_am: Optional[datetime] = None
    aktenzeichen: Optional[str] = None
    notiz: Optional[str] = None


class BussgeldUpdatePayload(BaseModel):
    bezahlt_am: Optional[datetime] = None
    status: Optional[str] = None
    notiz: Optional[str] = None
    aktenzeichen: Optional[str] = None


class LeasingRueckgabePayload(BaseModel):
    rueckgabedatum: datetime
    km_stand_bei_rueckgabe: float = Field(..., ge=0)
    zustand_bemerkung: Optional[str] = None
    benutzer: Optional[str] = None


# ── Statushistorie ────────────────────────────────────────────────────────────

@router.post(
    "/fahrzeuge/{fahrzeug_id}/status",
    response_model=FuhrparkOut,
    status_code=201,
    summary="Fahrzeug-Status wechseln und in Historie schreiben",
)
async def change_fahrzeug_status(
    fahrzeug_id: str,
    payload: StatusWechselPayload,
    db: Session = Depends(get_db),
):
    gueltiger_status = {"verfuegbar", "unterwegs", "wartung", "ausgeschieden"}
    if payload.zu_status not in gueltiger_status:
        raise HTTPException(status_code=422, detail=f"Ungültiger Status: {payload.zu_status}")

    fz = _ensure_fahrzeug(fahrzeug_id, db)
    von_status = fz.status

    fz.status = payload.zu_status
    if payload.km_stand is not None:
        fz.kilometerstand = payload.km_stand

    eintrag_id = _new_id("SH")
    db.execute(
        text("""
            INSERT INTO domain_ops.ops_fahrzeug_status_historie
                (id, fahrzeug_id, von_status, zu_status, grund, benutzer, km_stand, timestamp)
            VALUES (:id, :fid, :von, :zu, :grund, :benutzer, :km, NOW())
        """),
        {
            "id": eintrag_id,
            "fid": fahrzeug_id,
            "von": von_status,
            "zu": payload.zu_status,
            "grund": payload.grund,
            "benutzer": payload.benutzer,
            "km": payload.km_stand,
        },
    )
    db.commit()
    db.refresh(fz)
    result = _to_dict(fz)
    result["historie_id"] = eintrag_id
    return result


@router.get(
    "/fahrzeuge/{fahrzeug_id}/status-historie",
    response_model=list[FuhrparkOut],
    summary="Statushistorie eines Fahrzeugs",
)
async def get_status_historie(
    fahrzeug_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    _ensure_fahrzeug(fahrzeug_id, db)
    rows = db.execute(
        text("""
            SELECT id, fahrzeug_id, von_status, zu_status, grund, benutzer, km_stand,
                   timestamp
            FROM domain_ops.ops_fahrzeug_status_historie
            WHERE fahrzeug_id = :fid
            ORDER BY timestamp DESC
            LIMIT :lim
        """),
        {"fid": fahrzeug_id, "lim": limit},
    ).fetchall()
    return [dict(r._mapping) for r in rows]


# ── Schadensfälle ─────────────────────────────────────────────────────────────

@router.get(
    "/fahrzeuge/{fahrzeug_id}/schaeden",
    response_model=list[FuhrparkOut],
    summary="Schadensfälle eines Fahrzeugs",
)
async def list_schaeden(
    fahrzeug_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    _ensure_fahrzeug(fahrzeug_id, db)
    q = "SELECT * FROM domain_ops.ops_fahrzeug_schaeden WHERE fahrzeug_id = :fid"
    params: dict = {"fid": fahrzeug_id}
    if status:
        q += " AND status = :status"
        params["status"] = status
    q += " ORDER BY datum DESC"
    rows = db.execute(text(q), params).fetchall()
    return [dict(r._mapping) for r in rows]


@router.post(
    "/fahrzeuge/{fahrzeug_id}/schaeden",
    response_model=FuhrparkOut,
    status_code=201,
    summary="Schadensfall anlegen",
)
async def create_schaden(
    fahrzeug_id: str,
    payload: SchadenPayload,
    db: Session = Depends(get_db),
):
    _ensure_fahrzeug(fahrzeug_id, db)
    schaden_id = _new_id("SCH")
    db.execute(
        text("""
            INSERT INTO domain_ops.ops_fahrzeug_schaeden
                (id, fahrzeug_id, datum, ort, beschreibung, schadenhoehe_eur,
                 versicherung_gemeldet, versicherungs_nr, gegner_kennzeichen,
                 polizei_aktenzeichen, status, erstellt_von, created_at, updated_at)
            VALUES
                (:id, :fid, :datum, :ort, :beschr, :hoehe, :vers_gem, :vers_nr,
                 :gegner, :polizei, :status, :von, NOW(), NOW())
        """),
        {
            "id": schaden_id,
            "fid": fahrzeug_id,
            "datum": payload.datum,
            "ort": payload.ort,
            "beschr": payload.beschreibung,
            "hoehe": payload.schadenhoehe_eur,
            "vers_gem": payload.versicherung_gemeldet,
            "vers_nr": payload.versicherungs_nr,
            "gegner": payload.gegner_kennzeichen,
            "polizei": payload.polizei_aktenzeichen,
            "status": payload.status,
            "von": payload.erstellt_von,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_ops.ops_fahrzeug_schaeden WHERE id = :id"),
        {"id": schaden_id},
    ).fetchone()
    return dict(row._mapping)


@router.patch(
    "/fahrzeuge/{fahrzeug_id}/schaeden/{schaden_id}",
    response_model=FuhrparkOut,
    summary="Schadensfall aktualisieren",
)
async def update_schaden(
    fahrzeug_id: str,
    schaden_id: str,
    payload: SchadenUpdatePayload,
    db: Session = Depends(get_db),
):
    _ensure_fahrzeug(fahrzeug_id, db)
    existing = db.execute(
        text("SELECT id FROM domain_ops.ops_fahrzeug_schaeden WHERE id = :id AND fahrzeug_id = :fid"),
        {"id": schaden_id, "fid": fahrzeug_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Schadensfall nicht gefunden")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=422, detail="Keine Felder zum Aktualisieren")

    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = schaden_id
    db.execute(
        # nosec S608 -- reviewed-safe: set_clause is built only from Pydantic model field names.
        text(f"UPDATE domain_ops.ops_fahrzeug_schaeden SET {set_clause}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_ops.ops_fahrzeug_schaeden WHERE id = :id"),
        {"id": schaden_id},
    ).fetchone()
    return dict(row._mapping)


# ── Bußgelder / Verwarnungen ──────────────────────────────────────────────────

@router.get(
    "/fahrzeuge/{fahrzeug_id}/bussgeld",
    response_model=list[FuhrparkOut],
    summary="Bußgelder/Verwarnungen eines Fahrzeugs",
)
async def list_bussgeld(
    fahrzeug_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    _ensure_fahrzeug(fahrzeug_id, db)
    q = "SELECT * FROM domain_ops.ops_fahrzeug_bussgeld WHERE fahrzeug_id = :fid"
    params: dict = {"fid": fahrzeug_id}
    if status:
        q += " AND status = :status"
        params["status"] = status
    q += " ORDER BY datum DESC"
    rows = db.execute(text(q), params).fetchall()
    return [dict(r._mapping) for r in rows]


@router.post(
    "/fahrzeuge/{fahrzeug_id}/bussgeld",
    response_model=FuhrparkOut,
    status_code=201,
    summary="Bußgeld/Verwarnung anlegen",
)
async def create_bussgeld(
    fahrzeug_id: str,
    payload: BussgeldPayload,
    db: Session = Depends(get_db),
):
    _ensure_fahrzeug(fahrzeug_id, db)
    bg_id = _new_id("BG")
    db.execute(
        text("""
            INSERT INTO domain_ops.ops_fahrzeug_bussgeld
                (id, fahrzeug_id, fahrer_id, datum, ort, tatbestand, betrag_eur,
                 faellig_am, aktenzeichen, notiz, status, created_at, updated_at)
            VALUES
                (:id, :fid, :fahrer, :datum, :ort, :tatbestand, :betrag,
                 :faellig, :aktenzeichen, :notiz, 'offen', NOW(), NOW())
        """),
        {
            "id": bg_id,
            "fid": fahrzeug_id,
            "fahrer": payload.fahrer_id,
            "datum": payload.datum,
            "ort": payload.ort,
            "tatbestand": payload.tatbestand,
            "betrag": payload.betrag_eur,
            "faellig": payload.faellig_am,
            "aktenzeichen": payload.aktenzeichen,
            "notiz": payload.notiz,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_ops.ops_fahrzeug_bussgeld WHERE id = :id"),
        {"id": bg_id},
    ).fetchone()
    return dict(row._mapping)


@router.patch(
    "/fahrzeuge/{fahrzeug_id}/bussgeld/{bg_id}",
    response_model=FuhrparkOut,
    summary="Bußgeld/Verwarnung aktualisieren (bezahlt, Einspruch, …)",
)
async def update_bussgeld(
    fahrzeug_id: str,
    bg_id: str,
    payload: BussgeldUpdatePayload,
    db: Session = Depends(get_db),
):
    _ensure_fahrzeug(fahrzeug_id, db)
    existing = db.execute(
        text("SELECT id FROM domain_ops.ops_fahrzeug_bussgeld WHERE id = :id AND fahrzeug_id = :fid"),
        {"id": bg_id, "fid": fahrzeug_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Bußgeld-Eintrag nicht gefunden")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=422, detail="Keine Felder zum Aktualisieren")

    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = bg_id
    db.execute(
        # nosec S608 -- reviewed-safe: set_clause is built only from Pydantic model field names.
        text(f"UPDATE domain_ops.ops_fahrzeug_bussgeld SET {set_clause}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_ops.ops_fahrzeug_bussgeld WHERE id = :id"),
        {"id": bg_id},
    ).fetchone()
    return dict(row._mapping)


# ── Predictive Maintenance ────────────────────────────────────────────────────

@router.get(
    "/fahrzeuge/{fahrzeug_id}/wartung-vorhersage",
    response_model=FuhrparkOut,
    summary="Wartungsvorhersage auf Basis KM-Stand und Terminarten",
)
async def get_wartung_vorhersage(
    fahrzeug_id: str,
    db: Session = Depends(get_db),
):
    fz = _ensure_fahrzeug(fahrzeug_id, db)
    km = float(fz.kilometerstand or 0)

    terminarten = db.execute(
        text("SELECT terminart, intervall_monate, intervall_km FROM domain_ops.ops_fuhrpark_terminarten ORDER BY intervall_km")
    ).fetchall()

    def _naechste_faelligkeit(intervall_km: int, aktuell_km: float) -> dict:
        if intervall_km <= 0:
            return {"faellig_in_km": None, "faellig_bei_km": None}
        bereits_abgearbeitet = int(aktuell_km // intervall_km)
        naechste_km = (bereits_abgearbeitet + 1) * intervall_km
        return {
            "faellig_in_km": round(naechste_km - aktuell_km, 1),
            "faellig_bei_km": naechste_km,
        }

    vorhersagen = []
    for ta in terminarten:
        pred = _naechste_faelligkeit(ta.intervall_km, km)
        dringend = pred["faellig_in_km"] is not None and pred["faellig_in_km"] <= 2000
        vorhersagen.append({
            "terminart": ta.terminart,
            "intervall_monate": ta.intervall_monate,
            "intervall_km": ta.intervall_km,
            **pred,
            "dringend": dringend,
        })

    tuev_days = None
    if fz.naechster_tuev_termin:
        delta = fz.naechster_tuev_termin.replace(tzinfo=None) - datetime.now()
        tuev_days = delta.days

    asu_days = None
    if fz.naechster_asu_termin:
        delta = fz.naechster_asu_termin.replace(tzinfo=None) - datetime.now()
        asu_days = delta.days

    inspektion_days = None
    if fz.naechste_inspektion:
        delta = fz.naechste_inspektion.replace(tzinfo=None) - datetime.now()
        inspektion_days = delta.days

    return {
        "fahrzeug_id": fahrzeug_id,
        "kennzeichen": fz.kennzeichen,
        "aktueller_km_stand": km,
        "tuev_faellig_in_tagen": tuev_days,
        "asu_faellig_in_tagen": asu_days,
        "inspektion_faellig_in_tagen": inspektion_days,
        "vorhersagen_nach_km": vorhersagen,
    }


# ── Leasing-Rückgabe ──────────────────────────────────────────────────────────

@router.post(
    "/fahrzeuge/{fahrzeug_id}/leasing-rueckgabe",
    response_model=FuhrparkOut,
    summary="Leasing-Rückgabe einleiten (Status → ausgeschieden + KM-Protokoll)",
)
async def leasing_rueckgabe(
    fahrzeug_id: str,
    payload: LeasingRueckgabePayload,
    db: Session = Depends(get_db),
):
    fz = _ensure_fahrzeug(fahrzeug_id, db)

    if not fz.leasinggesellschaft:
        raise HTTPException(status_code=422, detail="Fahrzeug ist kein Leasing-Fahrzeug (leasinggesellschaft fehlt)")

    von_status = fz.status
    fz.status = "ausgeschieden"
    fz.abmeldedatum = payload.rueckgabedatum
    fz.kilometerstand = payload.km_stand_bei_rueckgabe

    historie_id = _new_id("SH")
    grund = f"Leasing-Rückgabe an {fz.leasinggesellschaft}"
    if payload.zustand_bemerkung:
        grund += f" — {payload.zustand_bemerkung}"

    db.execute(
        text("""
            INSERT INTO domain_ops.ops_fahrzeug_status_historie
                (id, fahrzeug_id, von_status, zu_status, grund, benutzer, km_stand, timestamp)
            VALUES (:id, :fid, :von, 'ausgeschieden', :grund, :benutzer, :km, NOW())
        """),
        {
            "id": historie_id,
            "fid": fahrzeug_id,
            "von": von_status,
            "grund": grund,
            "benutzer": payload.benutzer,
            "km": payload.km_stand_bei_rueckgabe,
        },
    )
    db.commit()
    db.refresh(fz)
    result = _to_dict(fz)
    result["rueckgabe_protokoll"] = {
        "rueckgabedatum": payload.rueckgabedatum.isoformat(),
        "km_stand_bei_rueckgabe": payload.km_stand_bei_rueckgabe,
        "leasinggesellschaft": fz.leasinggesellschaft,
        "zustand_bemerkung": payload.zustand_bemerkung,
        "historie_id": historie_id,
    }
    return result
