"""
Portal Feldbuch — Endpoints für den Landwirt im Kundenportal

Gefiltert nach customer_id aus JWT.
Export (CSV / Ackerschlagkartei-CSV) und Import.
"""
from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from sqlalchemy.orm import selectinload

from app.core.data_quality_enforcement import evaluate_feldbuch_massnahme_datensatz
from app.core.database import get_db
from app.core.data_quality_enforcement import DQValidationException
from app.core.tenant import get_tenant_id
from app.core.security import get_user_id_from_request
from app.core.uuid7 import uuid7
from app.infrastructure.models.agrar_models import FeldbuchMassnahme, FeldbuchSchlag

logger = logging.getLogger(__name__)

try:
    from modules.agrar.services.feldbuch_service import import_csv
except ImportError as e:
    import_csv = None  # type: ignore[assignment]
    logger.warning("Portal Feldbuch: import_csv nicht verfügbar (%s)", e)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class PortalFeldbuchOut(BaseSchema):
    """Typed response schema for PortalFeldbuchOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


router = APIRouter(tags=["portal", "feldbuch"])


def _validate_portal_feldbuch_csv(content: bytes) -> None:
    text = content.decode("utf-8-sig", errors="replace")
    delimiter = ";" if ";" in text.split("\n")[0] else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    column_map = {
        "datum": "datum",
        "date": "datum",
        "schlag": "schlag_name",
        "field": "schlag_name",
        "schlag_name": "schlag_name",
        "typ": "typ",
        "type": "typ",
        "flaeche": "flaeche_ha",
        "fläche": "flaeche_ha",
        "area": "flaeche_ha",
        "menge": "menge",
        "quantity": "menge",
    }
    typ_map = {
        "psm": "psm",
        "pflanzenschutz": "psm",
        "pflanzenschutzmittel": "psm",
        "herbizid": "psm",
        "fungizid": "psm",
        "insektizid": "psm",
        "düngung": "duengung",
        "duengung": "duengung",
        "dünger": "duengung",
        "duenger": "duengung",
        "fertilizer": "duengung",
        "aussaat": "aussaat",
        "sowing": "aussaat",
        "seeding": "aussaat",
        "ernte": "ernte",
        "harvest": "ernte",
        "bodenbearbeitung": "bodenbearbeitung",
        "tillage": "bodenbearbeitung",
        "soil": "bodenbearbeitung",
    }
    for row_num, row in enumerate(reader, start=2):
        normalized: dict[str, str] = {}
        for key, value in row.items():
            if key is None:
                continue
            mapped = column_map.get(key.strip().lower().replace(" ", "_"))
            if mapped:
                normalized[mapped] = (value or "").strip()

        def _parse_float(value: Optional[str]) -> float | str | None:
            if value is None or value == "":
                return None
            try:
                return float(value.replace(",", "."))
            except ValueError:
                return value

        dq_result = evaluate_feldbuch_massnahme_datensatz(
            {
                "datum": normalized.get("datum"),
                "schlag_name": normalized.get("schlag_name"),
                "typ": typ_map.get(normalized.get("typ", "").lower(), "sonstiges"),
                "flaeche_ha": _parse_float(normalized.get("flaeche_ha")),
                "menge": _parse_float(normalized.get("menge")),
            }
        )
        if not dq_result.bestanden:
            detail = "; ".join(v.meldung for v in dq_result.verletzungen if v.severity == "FEHLER")
            raise HTTPException(status_code=422, detail=f"Zeile {row_num}: {detail}")


# ────────────────────────────────────────────────────────────────────────────
# Auth helper — customer_id aus JWT oder Query-Param (dev-mode)
# ────────────────────────────────────────────────────────────────────────────

def _get_customer_id(
    request: Request,
    customer_id: Optional[str] = Query(None),
) -> str:
    """
    Im Production-Betrieb kommt customer_id aus dem JWT-Sub-Claim (token_claims).
    Im Dev-Mode kann sie als Query-Parameter übergeben werden.
    Wenn weder JWT noch Query-Param vorhanden → Fallback 'dev-customer'.
    """
    if customer_id:
        return customer_id
    uid = get_user_id_from_request(request)
    if uid and uid not in ("system", "dev-user"):
        return uid
    return "dev-customer"


# ────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ────────────────────────────────────────────────────────────────────────────

class _SchlagDuevFields(BaseModel):
    # AS-W2 (DüV): N-Düngebedarf-Grundlagen
    n_sollwert_kg_ha: Optional[float] = None
    ertragsniveau_dt_ha: Optional[float] = None
    # AS-W5 (DüV): Nmin + Bodenuntersuchung
    nmin_fruehjahr_kg_ha: Optional[float] = None
    nmin_in_bedarf: Optional[bool] = None
    boden_p2o5_mg: Optional[float] = None
    boden_k2o_mg: Optional[float] = None
    boden_mgo_mg: Optional[float] = None
    boden_ph: Optional[float] = None
    boden_datum: Optional[datetime] = None
    versorgungsstufe: Optional[str] = None


class PortalSchlagCreate(_SchlagDuevFields):
    name: str
    flik: Optional[str] = None
    flaeche: float
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: str = "aktiv"


class PortalSchlagUpdate(_SchlagDuevFields):
    name: Optional[str] = None
    flik: Optional[str] = None
    flaeche: Optional[float] = None
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: Optional[str] = None


# Nicht-Spalten-Eingaben (nur zur Berechnung), werden vor dem Persistieren entfernt.
_NUTRIENT_INPUT_KEYS = ("n_gehalt", "p2o5_gehalt", "k2o_gehalt", "mgo_gehalt", "s_gehalt", "preis_je_einheit")


class PortalMassnahmeBase(BaseModel):
    # AS-W1: Düngung — Reinnährstoffe werden aus Gehalten (% des Produkts) berechnet
    n_gehalt: Optional[float] = None
    p2o5_gehalt: Optional[float] = None
    k2o_gehalt: Optional[float] = None
    mgo_gehalt: Optional[float] = None
    s_gehalt: Optional[float] = None
    preis_je_einheit: Optional[float] = None   # €/kg bzw. €/l Produkt → kosten_eur
    duenger_form: Optional[str] = None         # 'M' | 'O'
    # AS-W4: Pflanzenschutz
    wirkungsbereich: Optional[str] = None
    begruendung: Optional[str] = None
    # AS-W6: Ernte
    ertrag_dt_ha: Optional[float] = None
    qualitaet: Optional[str] = None
    erloes_eur: Optional[float] = None
    nebenleistung_eur: Optional[float] = None
    kosten_eur: Optional[float] = None


class PortalMassnahmeCreate(PortalMassnahmeBase):
    schlag_id: Optional[str] = None
    datum: datetime
    uhrzeit: Optional[str] = None
    typ: str
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    bemerkung: Optional[str] = None


class PortalMassnahmeUpdate(PortalMassnahmeBase):
    schlag_id: Optional[str] = None
    datum: Optional[datetime] = None
    uhrzeit: Optional[str] = None
    typ: Optional[str] = None
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    bemerkung: Optional[str] = None


def _apply_duengung_nutrients(payload: dict[str, Any]) -> dict[str, Any]:
    """AS-W1: Reinnährstoffe (N/P2O5/K2O/MgO/S) + Kosten aus Gehalten berechnen.

    Erwartet die Gehalt-Prozente und Produktmenge/ha (`menge`) + Fläche im Payload,
    entfernt die Nicht-Spalten-Eingaben und ergänzt die berechneten Spalten.
    """
    from app.agrar.feldbuch.naehrstoff import NaehrstoffGehalt, reinnaehrstoffe_kg

    gehalt = NaehrstoffGehalt(
        n=float(payload.get("n_gehalt") or 0.0),
        p2o5=float(payload.get("p2o5_gehalt") or 0.0),
        k2o=float(payload.get("k2o_gehalt") or 0.0),
        mgo=float(payload.get("mgo_gehalt") or 0.0),
        s=float(payload.get("s_gehalt") or 0.0),
        organisch=(payload.get("duenger_form") == "O"),
    )
    menge = float(payload.get("menge") or 0.0)
    flaeche = float(payload.get("flaeche") or 0.0)
    has_gehalt = any(getattr(gehalt, k) > 0 for k in ("n", "p2o5", "k2o", "mgo", "s"))
    if has_gehalt and menge > 0 and flaeche > 0:
        rn = reinnaehrstoffe_kg(menge, flaeche, gehalt)
        payload["n_kg"] = rn["n"]
        payload["p2o5_kg"] = rn["p2o5"]
        payload["k2o_kg"] = rn["k2o"]
        payload["mgo_kg"] = rn["mgo"]
        payload["s_kg"] = rn["s"]
    preis = payload.get("preis_je_einheit")
    if preis is not None and menge > 0 and flaeche > 0:
        payload["kosten_eur"] = round(float(preis) * menge * flaeche, 2)
    for key in _NUTRIENT_INPUT_KEYS:
        payload.pop(key, None)
    return payload


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _schlag_to_dict(s: FeldbuchSchlag) -> dict[str, Any]:
    return {
        "id": str(s.id) if s.id else None,
        "name": str(s.name) if s.name else "",
        "flik": str(s.flik) if s.flik else None,
        "flaeche": float(s.flaeche) if s.flaeche is not None else 0.0,
        "kultur": str(s.kultur) if s.kultur else "",
        "vorkultur": str(s.vorkultur) if s.vorkultur else None,
        "gemeinde": str(s.gemeinde) if s.gemeinde else "",
        "gemarkung": str(s.gemarkung) if s.gemarkung else None,
        "bodenart": str(s.bodenart) if s.bodenart else None,
        "ackerzahl": float(s.ackerzahl) if s.ackerzahl is not None else None,
        "status": str(s.status) if s.status else "aktiv",
        # AS-W2/W5 (DüV): Sollwert, Nmin, Bodenuntersuchung
        "nSollwertKgHa": float(s.n_sollwert_kg_ha) if s.n_sollwert_kg_ha is not None else None,
        "ertragsniveauDtHa": float(s.ertragsniveau_dt_ha) if s.ertragsniveau_dt_ha is not None else None,
        "nminFruehjahrKgHa": float(s.nmin_fruehjahr_kg_ha) if s.nmin_fruehjahr_kg_ha is not None else None,
        "nminInBedarf": bool(s.nmin_in_bedarf) if s.nmin_in_bedarf is not None else True,
        "bodenP2o5Mg": float(s.boden_p2o5_mg) if s.boden_p2o5_mg is not None else None,
        "bodenK2oMg": float(s.boden_k2o_mg) if s.boden_k2o_mg is not None else None,
        "bodenMgoMg": float(s.boden_mgo_mg) if s.boden_mgo_mg is not None else None,
        "bodenPh": float(s.boden_ph) if s.boden_ph is not None else None,
        "bodenDatum": s.boden_datum.date().isoformat() if s.boden_datum else None,
        "versorgungsstufe": str(s.versorgungsstufe) if s.versorgungsstufe else None,
    }


def _massnahme_to_dict(m: FeldbuchMassnahme) -> dict[str, Any]:
    schlag_name = str(m.schlag.name) if m.schlag and m.schlag.name else None
    # JSON-sicher: auflagen als Liste oder None (JSONB kann list/dict sein)
    auflagen = m.auflagen
    if auflagen is not None and not isinstance(auflagen, list):
        auflagen = list(auflagen) if hasattr(auflagen, "__iter__") and not isinstance(auflagen, str) else [str(auflagen)]
    return {
        "id": str(m.id) if m.id else None,
        "schlagId": str(m.schlag_id) if m.schlag_id else None,
        "schlagName": schlag_name,
        "datum": m.datum.date().isoformat() if m.datum else None,
        "typ": str(m.typ) if m.typ else "",
        "bezeichnung": str(m.bezeichnung) if m.bezeichnung else None,
        "mittel": str(m.mittel) if m.mittel else None,
        "menge": float(m.menge) if m.menge is not None else None,
        "einheit": str(m.einheit) if m.einheit else None,
        "flaeche": float(m.flaeche) if m.flaeche is not None else None,
        "anwender": str(m.anwender) if m.anwender else None,
        "quelle": str(m.quelle) if m.quelle else "portal",
        "auflagen": auflagen,
        "compliant": bool(m.compliant) if m.compliant is not None else True,
        "exportiert": bool(m.exportiert) if m.exportiert is not None else False,
        "bemerkung": str(m.bemerkung) if m.bemerkung else None,
        # AS-W1: Reinnährstoffe + Kosten
        "nKg": float(m.n_kg) if m.n_kg is not None else None,
        "p2o5Kg": float(m.p2o5_kg) if m.p2o5_kg is not None else None,
        "k2oKg": float(m.k2o_kg) if m.k2o_kg is not None else None,
        "mgoKg": float(m.mgo_kg) if m.mgo_kg is not None else None,
        "sKg": float(m.s_kg) if m.s_kg is not None else None,
        "duengerForm": str(m.duenger_form) if m.duenger_form else None,
        "kostenEur": float(m.kosten_eur) if m.kosten_eur is not None else None,
        # AS-W4: Pflanzenschutz
        "wirkungsbereich": str(m.wirkungsbereich) if m.wirkungsbereich else None,
        "begruendung": str(m.begruendung) if m.begruendung else None,
        "wartezeitTage": int(m.wartezeit_tage) if m.wartezeit_tage is not None else None,
        # AS-W6: Ernte
        "ertragDtHa": float(m.ertrag_dt_ha) if m.ertrag_dt_ha is not None else None,
        "qualitaet": str(m.qualitaet) if m.qualitaet else None,
        "erloesEur": float(m.erloes_eur) if m.erloes_eur is not None else None,
        "nebenleistungEur": float(m.nebenleistung_eur) if m.nebenleistung_eur is not None else None,
    }


def _require_portal_massnahme(
    massnahme_id: str,
    customer_id: str,
    tenant_id: str,
    db: Session,
) -> FeldbuchMassnahme:
    m = (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.id == massnahme_id,
            FeldbuchMassnahme.tenant_id == tenant_id,
            FeldbuchMassnahme.customer_id == customer_id,
        )
        .first()
    )
    if not m:
        raise HTTPException(status_code=404, detail="Maßnahme nicht gefunden")
    return m


# ────────────────────────────────────────────────────────────────────────────
# Schläge
# ────────────────────────────────────────────────────────────────────────────

@router.get("/feldbuch/schlaege", summary="List schlaege portal",
    response_model=list[PortalFeldbuchOut]
)
async def portal_list_schlaege(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> list[dict[str, Any]]:
    try:
        schlaege = (
            db.query(FeldbuchSchlag)
            .filter(
                FeldbuchSchlag.tenant_id == tenant_id,
                FeldbuchSchlag.customer_id == customer_id,
            )
            .order_by(FeldbuchSchlag.name)
            .offset(skip).limit(limit)
            .all()
        )
        data = [_schlag_to_dict(s) for s in schlaege]
        return JSONResponse(content=json.loads(json.dumps(data, default=str)))
    except (ProgrammingError, OperationalError) as e:
        logger.exception("Portal Feldbuch Schläge: Schema/Tabelle fehlt (%s)", e)
        raise HTTPException(
            status_code=503,
            detail="Feldbuch-Schema nicht initialisiert. Bitte Migrationen ausführen: alembic upgrade head",
        ) from e
    except Exception as e:
        logger.exception("Portal Feldbuch Schläge: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/feldbuch/schlaege", status_code=201, summary="Create schlag portal",
    response_model=PortalFeldbuchOut
)
async def portal_create_schlag(
    data: PortalSchlagCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    schlag = FeldbuchSchlag(
        id=uuid7(),
        tenant_id=tenant_id,
        customer_id=customer_id,
        created_by=f"portal:{customer_id}",
        **data.model_dump(),
    )
    db.add(schlag)
    db.commit()
    db.refresh(schlag)
    return _schlag_to_dict(schlag)


@router.put("/feldbuch/schlaege/{schlag_id}", summary="Update schlag portal",
    response_model=PortalFeldbuchOut
)
async def portal_update_schlag(
    schlag_id: str,
    data: PortalSchlagUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    schlag = (
        db.query(FeldbuchSchlag)
        .filter(
            FeldbuchSchlag.id == schlag_id,
            FeldbuchSchlag.tenant_id == tenant_id,
            FeldbuchSchlag.customer_id == customer_id,
        )
        .first()
    )
    if not schlag:
        raise HTTPException(status_code=404, detail="Schlag nicht gefunden")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(schlag, field, value)
    db.commit()
    db.refresh(schlag)
    return _schlag_to_dict(schlag)


# ────────────────────────────────────────────────────────────────────────────
# Maßnahmen
# ────────────────────────────────────────────────────────────────────────────

@router.get("/feldbuch/massnahmen", summary="List massnahmen portal",
    response_model=list[PortalFeldbuchOut]
)
async def portal_list_massnahmen(
    schlag_id: Optional[str] = Query(None),
    typ: Optional[str] = Query(None),
    von: Optional[str] = Query(None),
    bis: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> list[dict[str, Any]]:
    try:
        q = (
            db.query(FeldbuchMassnahme)
            .filter(
                FeldbuchMassnahme.tenant_id == tenant_id,
                FeldbuchMassnahme.customer_id == customer_id,
            )
        )
        if schlag_id:
            q = q.filter(FeldbuchMassnahme.schlag_id == schlag_id)
        if typ:
            q = q.filter(FeldbuchMassnahme.typ == typ)
        if von:
            q = q.filter(FeldbuchMassnahme.datum >= datetime.fromisoformat(von))
        if bis:
            q = q.filter(FeldbuchMassnahme.datum <= datetime.fromisoformat(bis))
        massnahmen = (
            q.options(selectinload(FeldbuchMassnahme.schlag))
            .order_by(FeldbuchMassnahme.datum.desc())
            .offset(skip).limit(limit)
            .all()
        )
        data = [_massnahme_to_dict(m) for m in massnahmen]
        return JSONResponse(content=json.loads(json.dumps(data, default=str)))
    except (ProgrammingError, OperationalError) as e:
        logger.exception("Portal Feldbuch Massnahmen: Schema/Tabelle fehlt (%s)", e)
        raise HTTPException(
            status_code=503,
            detail="Feldbuch-Schema nicht initialisiert. Bitte Migrationen ausführen: alembic upgrade head",
        ) from e
    except Exception as e:
        logger.exception("Portal Feldbuch Massnahmen: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/feldbuch/massnahmen", status_code=201, summary="Create massnahme portal",
    response_model=PortalFeldbuchOut
)
async def portal_create_massnahme(
    data: PortalMassnahmeCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    payload = _apply_duengung_nutrients(data.model_dump())
    massnahme = FeldbuchMassnahme(
        id=uuid7(),
        tenant_id=tenant_id,
        customer_id=customer_id,
        quelle="portal",
        **payload,
    )
    db.add(massnahme)
    db.commit()
    db.refresh(massnahme)
    return _massnahme_to_dict(massnahme)


@router.put("/feldbuch/massnahmen/{massnahme_id}", summary="Update massnahme portal",
    response_model=PortalFeldbuchOut
)
async def portal_update_massnahme(
    massnahme_id: str,
    data: PortalMassnahmeUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    massnahme = _require_portal_massnahme(massnahme_id, customer_id, tenant_id, db)
    # Nur eigene Einträge editierbar (nicht VALEO-Dienste)
    if massnahme.quelle in ("erp_service", "erp_lieferschein"):
        raise HTTPException(
            status_code=403,
            detail="VALEO-Dienstleistungen können nicht bearbeitet werden",
        )
    payload = _apply_duengung_nutrients(data.model_dump(exclude_none=True))
    for field, value in payload.items():
        setattr(massnahme, field, value)
    db.commit()
    db.refresh(massnahme)
    return _massnahme_to_dict(massnahme)


@router.get("/feldbuch/duengebilanz", summary="Duengebilanz portal (DueV)",
    response_model=PortalFeldbuchOut
)
async def portal_duengebilanz(
    jahr: int = Query(default=None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    """AS-W1 (DüV): Nährstoffbilanz je Schlag aus den erfassten Düngungsmaßnahmen.

    Aggregiert N/P2O5/K2O, trennt organisch/mineralisch und prüft die
    170-kg-N/ha-Obergrenze für organische Düngung.
    """
    from sqlalchemy import extract

    from app.agrar.feldbuch.naehrstoff import duev_n_org_check

    year = jahr or datetime.now().year
    q = (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.tenant_id == tenant_id,
            FeldbuchMassnahme.customer_id == customer_id,
            FeldbuchMassnahme.typ == "duengung",
            extract("year", FeldbuchMassnahme.datum) == year,
        )
    )
    per_schlag: dict[str, dict[str, Any]] = {}
    for m in q.all():
        sid = m.schlag_id or "ohne_schlag"
        row = per_schlag.setdefault(sid, {
            "schlagId": None if sid == "ohne_schlag" else sid,
            "schlagName": (m.schlag.name if m.schlag else None),
            "flaecheHa": float(m.schlag.flaeche) if (m.schlag and m.schlag.flaeche) else 0.0,
            "nKg": 0.0, "nOrganischKg": 0.0, "nMineralischKg": 0.0,
            "p2o5Kg": 0.0, "k2oKg": 0.0, "massnahmen": 0,
        })
        n = float(m.n_kg or 0.0)
        row["nKg"] += n
        row["p2o5Kg"] += float(m.p2o5_kg or 0.0)
        row["k2oKg"] += float(m.k2o_kg or 0.0)
        if m.duenger_form == "O":
            row["nOrganischKg"] += n
        else:
            row["nMineralischKg"] += n
        row["massnahmen"] += 1

    schlaege = []
    ueberschreitungen = 0
    for row in per_schlag.values():
        check = duev_n_org_check(row["nOrganischKg"], row["flaecheHa"] or 1.0)
        row["duevOrgCheck"] = {
            "nOrganischProHa": check["n_organisch_pro_ha"],
            "grenzwertKgHa": check["grenzwert_kg_ha"],
            "ueberschritten": check["ueberschritten"],
            "auslastungPct": check["auslastung_pct"],
        }
        for k in ("nKg", "nOrganischKg", "nMineralischKg", "p2o5Kg", "k2oKg"):
            row[k] = round(row[k], 2)
        if check["ueberschritten"]:
            ueberschreitungen += 1
        schlaege.append(row)

    return {
        "jahr": year,
        "schlaege": schlaege,
        "ueberschreitungenOrgN": ueberschreitungen,
        "grenzwertKgHa": 170.0,
    }


@router.get("/feldbuch/stoffstrombilanz", summary="Naehrstoffvergleich/Stoffstrombilanz portal (DueV/StoffBilV)",
    response_model=PortalFeldbuchOut
)
async def portal_stoffstrombilanz(
    jahr: int = Query(default=None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    """AS-W3 (DüV/StoffBilV): Nährstoffvergleich — Zufuhr (Düngung) vs. Abfuhr
    (Erntegut) je Schlag und für den Betrieb; N- und P2O5-Saldo.
    """
    from sqlalchemy import extract

    from app.agrar.feldbuch.stoffstrombilanz import SchlagStrom, naehrstoffabfuhr_kg, stoffstrombilanz

    year = jahr or datetime.now().year
    zufuhr: dict[str, dict[str, float]] = {}
    ernte: dict[str, dict[str, Any]] = {}
    for m in (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.tenant_id == tenant_id,
            FeldbuchMassnahme.customer_id == customer_id,
            extract("year", FeldbuchMassnahme.datum) == year,
        )
        .all()
    ):
        sid = m.schlag_id or "ohne_schlag"
        if m.typ == "duengung":
            z = zufuhr.setdefault(sid, {"n": 0.0, "p2o5": 0.0})
            z["n"] += float(m.n_kg or 0.0)
            z["p2o5"] += float(m.p2o5_kg or 0.0)
        elif m.typ == "ernte" and m.ertrag_dt_ha:
            e = ernte.setdefault(sid, {"kultur": None, "ertrag": 0.0, "flaeche": 0.0})
            e["kultur"] = (m.schlag.kultur if m.schlag else None)
            e["ertrag"] = float(m.ertrag_dt_ha)
            e["flaeche"] = float(m.flaeche or (m.schlag.flaeche if m.schlag else 0.0) or 0.0)

    stroeme = []
    schlaege_out = []
    all_sids = set(zufuhr) | set(ernte)
    for sid in all_sids:
        z = zufuhr.get(sid, {"n": 0.0, "p2o5": 0.0})
        e = ernte.get(sid, {"kultur": None, "ertrag": 0.0, "flaeche": 0.0})
        strom = SchlagStrom(
            n_zufuhr_kg=z["n"], p2o5_zufuhr_kg=z["p2o5"],
            kultur=e["kultur"], ertrag_dt_ha=e["ertrag"], flaeche_ha=e["flaeche"],
        )
        stroeme.append(strom)
        ab = naehrstoffabfuhr_kg(e["kultur"], e["ertrag"], e["flaeche"])
        schlaege_out.append({
            "schlagId": None if sid == "ohne_schlag" else sid,
            "kultur": e["kultur"],
            "nZufuhrKg": round(z["n"], 2), "nAbfuhrKg": ab["n"], "nSaldoKg": round(z["n"] - ab["n"], 2),
            "p2o5ZufuhrKg": round(z["p2o5"], 2), "p2o5AbfuhrKg": ab["p2o5"], "p2o5SaldoKg": round(z["p2o5"] - ab["p2o5"], 2),
        })
    betrieb = stoffstrombilanz(stroeme)
    return {"jahr": year, "betrieb": betrieb, "schlaege": schlaege_out}


@router.get("/feldbuch/ernte-auswertung", summary="Ernte + Direktkostenfreie Leistung portal",
    response_model=PortalFeldbuchOut
)
async def portal_ernte_auswertung(
    jahr: int = Query(default=None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    """AS-W6: Ernte-Auswertung je Schlag — Erlös, Nebenleistung und
    Direktkostenfreie Leistung (Erlös − Direktkosten aus Düngung/PSM/Saatgut).
    """
    from sqlalchemy import extract

    year = jahr or datetime.now().year
    per_schlag: dict[str, dict[str, Any]] = {}
    for m in (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.tenant_id == tenant_id,
            FeldbuchMassnahme.customer_id == customer_id,
            extract("year", FeldbuchMassnahme.datum) == year,
        )
        .all()
    ):
        sid = m.schlag_id or "ohne_schlag"
        row = per_schlag.setdefault(sid, {
            "schlagId": None if sid == "ohne_schlag" else sid,
            "schlagName": (m.schlag.name if m.schlag else None),
            "kultur": (m.schlag.kultur if m.schlag else None),
            "flaecheHa": float(m.schlag.flaeche) if (m.schlag and m.schlag.flaeche) else 0.0,
            "erloesEur": 0.0, "nebenleistungEur": 0.0, "direktkostenEur": 0.0,
            "ertragDtHa": None,
        })
        row["erloesEur"] += float(m.erloes_eur or 0.0)
        row["nebenleistungEur"] += float(m.nebenleistung_eur or 0.0)
        row["direktkostenEur"] += float(m.kosten_eur or 0.0)
        if m.typ == "ernte" and m.ertrag_dt_ha:
            row["ertragDtHa"] = float(m.ertrag_dt_ha)

    out = []
    for row in per_schlag.values():
        dfl = row["erloesEur"] + row["nebenleistungEur"] - row["direktkostenEur"]
        ha = row["flaecheHa"] or 0.0
        row["erloesEur"] = round(row["erloesEur"], 2)
        row["nebenleistungEur"] = round(row["nebenleistungEur"], 2)
        row["direktkostenEur"] = round(row["direktkostenEur"], 2)
        row["direktkostenfreieLeistungEur"] = round(dfl, 2)
        row["direktkostenfreieLeistungEurHa"] = round(dfl / ha, 2) if ha > 0 else None
        out.append(row)
    return {"jahr": year, "schlaege": out}


@router.get("/feldbuch/duengebedarf", summary="N-Duengebedarf portal (DueV)",
    response_model=PortalFeldbuchOut
)
async def portal_duengebedarf(
    jahr: int = Query(default=None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    """AS-W2 (DüV): N-Düngebedarfsermittlung je Schlag (Sollwert − Nmin) und
    Abgleich gegen die ausgebrachte N-Menge des Jahres.
    """
    from sqlalchemy import extract

    from app.agrar.feldbuch.naehrstoff import duengebedarf_n

    year = jahr or datetime.now().year
    schlaege = (
        db.query(FeldbuchSchlag)
        .filter(
            FeldbuchSchlag.tenant_id == tenant_id,
            FeldbuchSchlag.customer_id == customer_id,
            FeldbuchSchlag.status == "aktiv",
        )
        .all()
    )
    # ausgebrachte N je Schlag (kg gesamt)
    ausgebracht: dict[str, float] = {}
    for m in (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.tenant_id == tenant_id,
            FeldbuchMassnahme.customer_id == customer_id,
            FeldbuchMassnahme.typ == "duengung",
            extract("year", FeldbuchMassnahme.datum) == year,
        )
        .all()
    ):
        ausgebracht[m.schlag_id or ""] = ausgebracht.get(m.schlag_id or "", 0.0) + float(m.n_kg or 0.0)

    out = []
    for s in schlaege:
        sollwert = float(s.n_sollwert_kg_ha or 0.0)
        nmin = float(s.nmin_fruehjahr_kg_ha or 0.0) if (s.nmin_in_bedarf is None or s.nmin_in_bedarf) else 0.0
        bedarf_kg_ha = duengebedarf_n(sollwert, nmin) if sollwert > 0 else None
        ha = float(s.flaeche or 0.0)
        bedarf_kg = round(bedarf_kg_ha * ha, 1) if (bedarf_kg_ha is not None and ha > 0) else None
        ausg_kg = round(ausgebracht.get(str(s.id), 0.0), 1)
        ausg_kg_ha = round(ausg_kg / ha, 1) if ha > 0 else None
        rest = round(bedarf_kg - ausg_kg, 1) if bedarf_kg is not None else None
        out.append({
            "schlagId": str(s.id),
            "schlagName": str(s.name),
            "kultur": str(s.kultur) if s.kultur else None,
            "flaecheHa": ha,
            "nSollwertKgHa": sollwert or None,
            "nminFruehjahrKgHa": nmin or None,
            "nminBeruecksichtigt": bool(s.nmin_in_bedarf) if s.nmin_in_bedarf is not None else True,
            "nBedarfKgHa": bedarf_kg_ha,
            "nBedarfKg": bedarf_kg,
            "nAusgebrachtKg": ausg_kg,
            "nAusgebrachtKgHa": ausg_kg_ha,
            "nRestbedarfKg": rest,
            "ueberschritten": bool(rest is not None and rest < 0),
        })
    return {"jahr": year, "schlaege": out}


@router.get("/feldbuch/pflanzenschutz-uebersicht", summary="Pflanzenschutz-Uebersicht portal (PflSchG)",
    response_model=PortalFeldbuchOut
)
async def portal_pflanzenschutz_uebersicht(
    jahr: int = Query(default=None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    """AS-W4 (PflSchG/CC): Spritztagebuch-Uebersicht mit Kostensplit nach
    Wirkungsbereich und Pflichtangaben-Pruefung je Massnahme.
    """
    from sqlalchemy import extract

    from app.agrar.feldbuch.pflanzenschutz import (
        PsmMassnahme,
        kostensplit_nach_wirkungsbereich,
        psm_compliance,
    )

    year = jahr or datetime.now().year
    rows = (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.tenant_id == tenant_id,
            FeldbuchMassnahme.customer_id == customer_id,
            FeldbuchMassnahme.typ == "psm",
            extract("year", FeldbuchMassnahme.datum) == year,
        )
        .order_by(FeldbuchMassnahme.datum.desc())
        .all()
    )
    psm_objs = [
        PsmMassnahme(
            datum=m.datum.date() if m.datum else None,
            mittel=m.mittel,
            menge=float(m.menge) if m.menge is not None else None,
            flaeche=float(m.flaeche) if m.flaeche is not None else None,
            anwender=m.anwender,
            wirkungsbereich=m.wirkungsbereich,
            begruendung=m.begruendung,
            wartezeit_tage=int(m.wartezeit_tage) if m.wartezeit_tage is not None else None,
            kosten_eur=float(m.kosten_eur) if m.kosten_eur is not None else None,
        )
        for m in rows
    ]
    split = kostensplit_nach_wirkungsbereich(psm_objs)
    unvollstaendig = 0
    massnahmen_out = []
    for m, obj in zip(rows, psm_objs):
        comp = psm_compliance(obj)
        if not comp["compliant"]:
            unvollstaendig += 1
        massnahmen_out.append({
            "id": str(m.id),
            "datum": m.datum.date().isoformat() if m.datum else None,
            "schlagName": (m.schlag.name if m.schlag else None),
            "mittel": m.mittel,
            "wirkungsbereich": m.wirkungsbereich,
            "anwender": m.anwender,
            "begruendung": m.begruendung,
            "wartezeitTage": int(m.wartezeit_tage) if m.wartezeit_tage is not None else None,
            "kostenEur": float(m.kosten_eur) if m.kosten_eur is not None else None,
            "compliant": comp["compliant"],
            "fehlendePflichtangaben": comp["fehlende_pflichtangaben"],
        })
    return {
        "jahr": year,
        "anzahl": len(rows),
        "unvollstaendig": unvollstaendig,
        "kostensplit": {
            "herbizide": split["Herbizid"],
            "fungizide": split["Fungizid"],
            "insektizide": split["Insektizid"],
            "wachstumsregler": split["Wachstumsregler"],
            "sonstiges": split["Sonstiges"],
            "gesamt": round(sum(split.values()), 2),
        },
        "massnahmen": massnahmen_out,
    }


# ────────────────────────────────────────────────────────────────────────────
# Stats
# ────────────────────────────────────────────────────────────────────────────

@router.get("/feldbuch/stats", summary="Feldbuch stats portal",
    response_model=PortalFeldbuchOut
)
async def portal_feldbuch_stats(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    try:
        schlaege = (
            db.query(FeldbuchSchlag)
            .filter(
                FeldbuchSchlag.tenant_id == tenant_id,
                FeldbuchSchlag.customer_id == customer_id,
                FeldbuchSchlag.status == "aktiv",
            )
            .all()
        )
        massnahmen = (
            db.query(FeldbuchMassnahme)
            .filter(
                FeldbuchMassnahme.tenant_id == tenant_id,
                FeldbuchMassnahme.customer_id == customer_id,
            )
            .all()
        )
        valeo_dienste = sum(1 for m in massnahmen if m.quelle in ("erp_service", "erp_lieferschein"))
        gesamt_flaeche = sum(s.flaeche for s in schlaege if s.flaeche)
        data = {
            "schlaege": len(schlaege),
            "gesamtFlaeche": round(float(gesamt_flaeche), 2),
            "massnahmen": len(massnahmen),
            "valeoDienste": valeo_dienste,
        }
        return JSONResponse(content=json.loads(json.dumps(data, default=str)))
    except (ProgrammingError, OperationalError) as e:
        logger.exception("Portal Feldbuch Stats: Schema/Tabelle fehlt (%s)", e)
        raise HTTPException(
            status_code=503,
            detail="Feldbuch-Schema nicht initialisiert. Bitte Migrationen ausführen: alembic upgrade head",
        ) from e
    except Exception as e:
        logger.exception("Portal Feldbuch Stats: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ────────────────────────────────────────────────────────────────────────────
# Export
# ────────────────────────────────────────────────────────────────────────────

@router.get("/feldbuch/export", summary="Export portal",
    response_model=PortalFeldbuchOut
)
async def portal_export(
    format: str = Query("csv", description="'csv' oder 'ackerschlagkartei'"),
    schlag_id: Optional[str] = Query(None),
    von: Optional[str] = Query(None),
    bis: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> StreamingResponse:
    # Maßnahmen laden
    q = (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.tenant_id == tenant_id,
            FeldbuchMassnahme.customer_id == customer_id,
        )
    )
    if schlag_id:
        q = q.filter(FeldbuchMassnahme.schlag_id == schlag_id)
    if von:
        q = q.filter(FeldbuchMassnahme.datum >= datetime.fromisoformat(von))
    if bis:
        q = q.filter(FeldbuchMassnahme.datum <= datetime.fromisoformat(bis))
    massnahmen = (
        q.options(selectinload(FeldbuchMassnahme.schlag))
        .order_by(FeldbuchMassnahme.datum.desc())
        .all()
    )

    output = io.StringIO()
    today = datetime.now().strftime("%Y%m%d")

    if format == "ackerschlagkartei":
        # Ackerschlagkartei-kompatibles CSV (proPlant, 365FarmNet)
        fieldnames = [
            "Schlag", "FLIK", "Kultur", "Datum", "Maßnahme-Typ",
            "Mittel/Produkt", "Aufwandmenge", "Einheit", "Fläche_ha",
            "Anwender", "Auflagen", "Wartezeit_Tage", "PSM-Compliant",
            "Quelle", "Bemerkung",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=";", lineterminator="\n")
        writer.writeheader()
        for m in massnahmen:
            schlag_name = m.schlag.name if m.schlag else ""
            flik = m.schlag.flik if m.schlag else ""
            kultur = m.schlag.kultur if m.schlag else ""
            quelle_label = {
                "erp_service": "VALEO Dienst",
                "erp_lieferschein": "VALEO Lieferschein",
                "portal": "Portal",
            }.get(m.quelle, m.quelle)
            writer.writerow({
                "Schlag": schlag_name,
                "FLIK": flik or "",
                "Kultur": kultur or "",
                "Datum": m.datum.date().isoformat() if m.datum else "",
                "Maßnahme-Typ": m.typ,
                "Mittel/Produkt": m.mittel or "",
                "Aufwandmenge": m.menge or "",
                "Einheit": m.einheit or "",
                "Fläche_ha": m.flaeche or "",
                "Anwender": m.anwender or "",
                "Auflagen": ",".join(m.auflagen) if m.auflagen else "",
                "Wartezeit_Tage": m.wartezeit_tage or "",
                "PSM-Compliant": "ja" if m.compliant else "nein",
                "Quelle": quelle_label,
                "Bemerkung": m.bemerkung or "",
            })
        filename = f"ackerschlagkartei_{today}.csv"
    else:
        # Generisches CSV
        fieldnames = [
            "id", "schlag", "flik", "kultur", "datum", "typ", "bezeichnung",
            "mittel", "menge", "einheit", "flaeche_ha", "anwender",
            "auflagen", "wartezeit_tage", "compliant", "quelle", "bemerkung",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=";", lineterminator="\n")
        writer.writeheader()
        for m in massnahmen:
            schlag_name = m.schlag.name if m.schlag else ""
            flik = m.schlag.flik if m.schlag else ""
            kultur = m.schlag.kultur if m.schlag else ""
            writer.writerow({
                "id": m.id,
                "schlag": schlag_name,
                "flik": flik or "",
                "kultur": kultur or "",
                "datum": m.datum.date().isoformat() if m.datum else "",
                "typ": m.typ,
                "bezeichnung": m.bezeichnung or "",
                "mittel": m.mittel or "",
                "menge": m.menge or "",
                "einheit": m.einheit or "",
                "flaeche_ha": m.flaeche or "",
                "anwender": m.anwender or "",
                "auflagen": ",".join(m.auflagen) if m.auflagen else "",
                "wartezeit_tage": m.wartezeit_tage or "",
                "compliant": "ja" if m.compliant else "nein",
                "quelle": m.quelle,
                "bemerkung": m.bemerkung or "",
            })
        filename = f"feldbuch_export_{today}.csv"

    output.seek(0)
    content = output.getvalue().encode("utf-8-sig")  # BOM für Excel-Kompatibilität
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
        },
    )


# ────────────────────────────────────────────────────────────────────────────
# Import
# ────────────────────────────────────────────────────────────────────────────

@router.post("/feldbuch/import", summary="Import portal",
    response_model=PortalFeldbuchOut
)
async def portal_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    """
    CSV-Import aus externer Ackerschlagkartei.
    Erkennt bekannte Spaltenbezeichnungen (dt./engl.).
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Nur CSV-Dateien werden unterstützt")
    if import_csv is None:
        raise HTTPException(
            status_code=503,
            detail="Feldbuch-Import (modules.agrar) nicht verfügbar",
        )
    content = await file.read()
    _validate_portal_feldbuch_csv(content)
    try:
        result = import_csv(db, file_content=content, tenant_id=tenant_id, customer_id=customer_id)
    except DQValidationException as exc:
        raise HTTPException(status_code=422, detail=exc.detail) from exc
    db.commit()
    return result
