"""
Waage API Endpoints - SQLAlchemy Version
"""

import logging
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import Response, APIRouter, Depends, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect as sa_inspect

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.auth.tenant import get_verified_tenant_id
from app.auth.deps_oidc import get_current_user
from app.services import waage_import_service as scale_import
from app.core.business_time import business_today, business_timezone
from app.core.uuid7 import uuid7
from app.services.frachtbrief_service import finalize_menge_from_outbound_weighing

from app.domains.operations.repository import WaageRepository

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


class WaageOut(BaseSchema):
    """Typed response schema for WaageOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")



class WaageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)
    standort: str = Field(min_length=1, max_length=100)
    typ: str = Field(min_length=1, max_length=50)
    max_kapazitaet: float = Field(gt=0)
    letzte_eichung: Optional[datetime] = None
    naechste_eichung: Optional[datetime] = None
    status: Optional[str] = Field(default=None, max_length=20)
    hersteller: Optional[str] = Field(default=None, max_length=100)
    seriennummer: Optional[str] = Field(default=None, max_length=50)
    installiert_am: Optional[datetime] = None


class WaageUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)
    standort: Optional[str] = Field(default=None, min_length=1, max_length=100)
    typ: Optional[str] = Field(default=None, min_length=1, max_length=50)
    max_kapazitaet: Optional[float] = Field(default=None, gt=0)
    letzte_eichung: Optional[datetime] = None
    naechste_eichung: Optional[datetime] = None
    status: Optional[str] = Field(default=None, max_length=20)
    hersteller: Optional[str] = Field(default=None, max_length=100)
    seriennummer: Optional[str] = Field(default=None, max_length=50)
    installiert_am: Optional[datetime] = None


class WaageCalibrationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    letztes_eichdatum: Optional[date] = None
    naechste_eichfaelligkeit: Optional[date] = None
    eichamt: Optional[str] = Field(default=None, max_length=200)
    zertifikat_nr: Optional[str] = Field(default=None, max_length=200)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/waage", tags=["Waage"])

# ============================================================
# PARTIE-PFLICHT-001 â€” Partiepflicht-Konfiguration
# ============================================================

_PARTIEPFLICHTIGE_WIEGETYPEN = ["ROHWARE", "SAATGUT", "DUENGER"]
_PARTIEPFLICHTIGE_ARTIKEL_GRUPPEN = ["GE", "RA", "SG"]


class PartiepflichtCheckRequest(BaseModel):
    artikel_id: str
    wiegetyp: str
    partie_id: Optional[str] = None


@router.get("/waagen/partiepflicht-config", response_model=WaageOut, summary="Partiepflicht config abrufen")
async def get_partiepflicht_config(db: Session = Depends(get_db)) -> dict:
    """PARTIE-PFLICHT-001: Gibt zurÃ¼ck, welche Wiegetypen/Artikelgruppen Partiepflicht haben."""
    config_source = "default"
    try:
        rows = db.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'articles' AND column_name = 'artikel_gruppe'"
            )
        ).fetchall()
        if rows:
            config_source = "articles_table"
    except Exception:  # noqa: BLE001 â€” optionale DB-Abfrage; Fallback greift
        pass
    return {
        "partiepflichtige_wiegetypen": _PARTIEPFLICHTIGE_WIEGETYPEN,
        "partiepflichtige_artikel_gruppen": _PARTIEPFLICHTIGE_ARTIKEL_GRUPPEN,
        "config_source": config_source,
    }


@router.post("/waagen/partiepflicht-check", response_model=WaageOut, summary="Partiepflicht prÃ¼fen", dependencies=SCHREIBEN["LAGER"])
async def check_partiepflicht(
    payload: PartiepflichtCheckRequest,
    db: Session = Depends(get_db),
) -> dict:
    """PARTIE-PFLICHT-001: PrÃ¼ft ob fÃ¼r Artikel/Wiegetyp eine Partie Pflicht ist."""
    wiegetyp_upper = payload.wiegetyp.upper()
    pflicht = wiegetyp_upper in _PARTIEPFLICHTIGE_WIEGETYPEN

    if not pflicht:
        try:
            row = db.execute(
                text("SELECT artikel_gruppe FROM articles WHERE id = :id"),
                {"id": payload.artikel_id},
            ).fetchone()
            if row and row[0] in _PARTIEPFLICHTIGE_ARTIKEL_GRUPPEN:
                pflicht = True
        except Exception:  # noqa: BLE001 â€” Artikel-Gruppe nicht ermittelbar; Partiepflicht bleibt wie initialisiert
            pass

    if pflicht and not payload.partie_id:
        return {
            "valid": False,
            "reason": f"Partie erforderlich fÃ¼r Wiegetyp {payload.wiegetyp}",
        }
    return {"valid": True}


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _to_dict(model: Any) -> dict:
    if model is None:
        return {}
    mapper = sa_inspect(model.__class__)
    data = {}
    for column in mapper.columns:
        key = column.key
        data[key] = _serialize_value(getattr(model, key))
    return data


def _to_list(models: List[Any]) -> List[dict]:
    return [_to_dict(model) for model in models]


# === WAAGE ENDPOINTS ===

@router.get("/waagen", response_model=list[WaageOut], summary="Waagen auflisten")
async def list_waagen(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), status: Optional[str] = None, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id)):
    repo = WaageRepository(db, tenant_id)
    return _to_list(repo.get_by_status(status, skip=skip, limit=limit) if status else repo.get_all(skip=skip, limit=limit))


@router.get("/waagen/{waage_id}", response_model=WaageOut, summary="Waage abrufen")
async def get_waage(waage_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id)):
    waage = WaageRepository(db, tenant_id).get_by_id(waage_id)
    if waage is None:
        raise HTTPException(status_code=404, detail="Waage nicht gefunden")
    return _to_dict(waage)


@router.post("/waagen", response_model=WaageOut, status_code=201, summary="Waage anlegen", dependencies=SCHREIBEN["LAGER"])
async def create_waage(waage_data: WaageCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id)):
    return _to_dict(WaageRepository(db, tenant_id).create(waage_data.model_dump(exclude_none=True)))


@router.patch("/waagen/{waage_id}", response_model=WaageOut, summary="Waage aktualisieren", dependencies=SCHREIBEN["LAGER"])
async def update_waage(waage_id: str, waage_data: WaageUpdate, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id)):
    payload = waage_data.model_dump(exclude_unset=True)
    if any(k in payload and payload[k] is None for k in ("standort", "typ", "max_kapazitaet")):
        raise HTTPException(status_code=422, detail="Pflichtfelder duerfen nicht leer sein")
    waage = WaageRepository(db, tenant_id).update(waage_id, payload)
    if waage is None:
        raise HTTPException(status_code=404, detail="Waage nicht gefunden")
    return _to_dict(waage)


@router.delete("/waagen/{waage_id}", status_code=204, response_class=Response, response_model=None, summary="Waage loeschen", dependencies=SCHREIBEN["LAGER"])
async def delete_waage(waage_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id)):
    try:
        deleted = WaageRepository(db, tenant_id).delete(waage_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail="Waage hat bestehende Wiegungen") from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Waage nicht gefunden")


# Legacy ops_wiegungen has no tenant ownership. The active UI uses the canonical
# /weighing-tickets API; never expose or mutate the unscoped legacy aggregate.
@router.get("/wiegungen", response_model=None, status_code=410, summary="Legacy-Wiegungen abgeloest")
async def list_wiegungen():
    raise HTTPException(status_code=410, detail="Legacy-Wiegungen abgeloest; Wiegescheine verwenden")


@router.get("/wiegungen/{wiegung_id}", response_model=None, status_code=410, summary="Legacy-Wiegung abgeloest")
async def get_wiegung(wiegung_id: str):
    raise HTTPException(status_code=410, detail="Legacy-Wiegungen abgeloest; Wiegescheine verwenden")


@router.post("/wiegungen", response_model=None, status_code=410, summary="Legacy-Wiegung abgeloest", dependencies=SCHREIBEN["LAGER"])
async def create_wiegung(wiegung_data: dict):
    raise HTTPException(status_code=410, detail="Legacy-Wiegungen abgeloest; Wiegescheine verwenden")


@router.delete("/wiegungen/{wiegung_id}", response_model=None, status_code=410, summary="Legacy-Wiegung abgeloest", dependencies=SCHREIBEN["LAGER"])
async def delete_wiegung(wiegung_id: str):
    raise HTTPException(status_code=410, detail="Legacy-Wiegungen abgeloest; Wiegescheine verwenden")


# ===========================================================================
# WAAGE-LIVE-001 â€” ASCII-Import, Fehlerqueue, Kalibrierung
# ===========================================================================

# ---------------------------------------------------------------------------
# 1a. ASCII-Dateiimport
# ---------------------------------------------------------------------------

def _parse_w_line(parts: List[str]) -> Dict[str, Any]:
    """Parse a W-Satzart line into a dict. Raises ValueError on bad format."""
    if len(parts) < 17:
        raise ValueError(f"W-Satzart braucht 17 Felder, got {len(parts)}")
    return {
        "wiegung_nr": parts[1],
        "datum": parts[2],
        "uhrzeit": parts[3],
        "brutto_kg": float(parts[4]),
        "tara_kg": float(parts[5]),
        "netto_kg": float(parts[6]),
        "kfz_kennzeichen": parts[7],
        "lieferant_id": parts[8],
        "artikel_id": parts[9],
        "sorte": parts[10],
        "partie_id": parts[11],
        "silo_id": parts[12],
        "qualitaet_feuchtigkeit": float(parts[13]) if parts[13] else None,
        "qualitaet_hl": float(parts[14]) if parts[14] else None,
        "qualitaet_bruch": float(parts[15]) if parts[15] else None,
    }


def _parse_q_line(parts: List[str]) -> Dict[str, Any]:
    """Parse a Q-Satzart line into a dict. Raises ValueError on bad format."""
    if len(parts) < 5:
        raise ValueError(f"Q-Satzart braucht 5 Felder, got {len(parts)}")
    return {
        "wiegung_nr": parts[1],
        "parameter": parts[2],
        "wert": parts[3],
        "einheit": parts[4],
    }


@router.post("/waagen/import/ascii", response_model=None, summary="ASCII-Wiegescheine importieren", dependencies=SCHREIBEN["LAGER"])
async def import_ascii(file: UploadFile, waage_id: str = Form(...), fehler_toleranz: bool = Form(True),
                       db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id), user: dict = Depends(get_current_user)):
    if WaageRepository(db, tenant_id).get_by_id(waage_id) is None:
        raise HTTPException(status_code=404, detail="Waage nicht gefunden")
    data = await file.read(1048577)
    if len(data) > 1048576:
        raise HTTPException(413, "Datei ist groesser als 1 MB")
    try:
        content = data.decode('utf-8-sig', errors='strict')
    except UnicodeDecodeError as exc:
        raise HTTPException(422, "Datei muss UTF-8 sein") from exc
    try:
        result = scale_import.import_records(db, tenant_id, waage_id, content, fehler_toleranz, user['sub'])
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


@router.get("/waagen/import/fehlerqueue", response_model=None, summary="Importfehler auflisten")
async def list_fehlerqueue(db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id),
                          limit: int = Query(100, ge=1, le=1000)):
    entries = db.query(scale_import.WaageImportEntry).filter(
        scale_import.WaageImportEntry.tenant_id == tenant_id,
        scale_import.WaageImportEntry.status == 'error').order_by(scale_import.WaageImportEntry.created_at).limit(limit).all()
    return [scale_import.serialize_entry(item) for item in entries]


@router.post("/waagen/import/fehlerqueue/{entry_id}/retry", response_model=None, summary="Importfehler erneut pruefen", dependencies=SCHREIBEN["LAGER"])
async def retry_fehlerqueue_entry(entry_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id), user: dict = Depends(get_current_user)):
    try:
        result = scale_import.retry_entry(db, tenant_id, entry_id, user['sub'])
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


@router.delete("/waagen/import/fehlerqueue/{entry_id}", response_model=None, summary="Importfehler verwerfen", dependencies=SCHREIBEN["LAGER"])
async def delete_fehlerqueue_entry(entry_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id), user: dict = Depends(get_current_user)):
    try:
        item = scale_import.queue_entry(db, tenant_id, entry_id)
        if item.status != 'error':
            raise HTTPException(409, 'Eintrag wurde bereits verarbeitet')
        item.status = 'dismissed'
        scale_import._event(db, tenant_id, user['sub'], item, 'dismissed')
        db.commit()
        return {'deleted': True, 'id': entry_id}
    except Exception:
        db.rollback()
        raise


# ---------------------------------------------------------------------------
# 1c. Kalibrierungsstatus
# ---------------------------------------------------------------------------

def _kalibrierung_status(naechste_eichfaelligkeit: Optional[str]) -> str:
    if not naechste_eichfaelligkeit:
        return "faellig"
    try:
        faellig = date.fromisoformat(str(naechste_eichfaelligkeit)[:10])
        today = business_today()
        if faellig < today:
            delta = (today - faellig).days
            return "ueberfaellig" if delta > 30 else "faellig"
        return "ok"
    except (ValueError, TypeError):
        return "unbekannt"


def _calibration_response(scale):
    def day(value):
        return value.date().isoformat() if isinstance(value, datetime) else value.isoformat() if value else None
    return {'waage_id': scale.id, 'letztes_eichdatum': day(scale.letzte_eichung),
            'naechste_eichfaelligkeit': day(scale.naechste_eichung), 'eichamt': scale.eichamt,
            'zertifikat_nr': scale.zertifikat_nr, 'kalibrierungsstatus': _kalibrierung_status(day(scale.naechste_eichung))}


@router.get("/waagen/{waage_id}/kalibrierung", response_model=WaageOut, summary="Kalibrierung abrufen")
async def get_kalibrierung(waage_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id)):
    scale = WaageRepository(db, tenant_id).get_by_id(waage_id)
    if scale is None:
        raise HTTPException(status_code=404, detail="Waage nicht gefunden")
    return _calibration_response(scale)


@router.patch("/waagen/{waage_id}/kalibrierung", response_model=WaageOut, summary="Kalibrierung aktualisieren", dependencies=SCHREIBEN["LAGER"])
async def update_kalibrierung(waage_id: str, payload: WaageCalibrationUpdate, db: Session = Depends(get_db), tenant_id: str = Depends(get_verified_tenant_id), user: dict = Depends(get_current_user)):
    scale = scale_import.locked_scale(db, tenant_id, waage_id)
    values = payload.model_dump(exclude_unset=True)
    previous = _calibration_response(scale)
    last = values.get('letztes_eichdatum', scale.letzte_eichung.date() if scale.letzte_eichung else None)
    next_ = values.get('naechste_eichfaelligkeit', scale.naechste_eichung.date() if scale.naechste_eichung else None)
    if last and next_ and next_ < last:
        raise HTTPException(422, 'Naechste Eichung liegt vor der letzten Eichung')
    mapping = {'letztes_eichdatum': 'letzte_eichung', 'naechste_eichfaelligkeit': 'naechste_eichung', 'eichamt': 'eichamt', 'zertifikat_nr': 'zertifikat_nr'}
    try:
        for key, value in values.items():
            setattr(scale, mapping[key], datetime.combine(value, time(), business_timezone()) if isinstance(value, date) else value)
        scale.updated_by = user['sub']
        result = _calibration_response(scale)
        import json
        from app.infrastructure.eventbus.outbox import OutboxEvent
        from app.core.business_time import business_now
        from app.services.mask_action_runtime_service import _write_audit
        _write_audit(db, tenant_id=tenant_id, action_key='waage.calibration.update', entity_type='waage',
            entity_id=scale.id, audit_reason=None, idempotency_key=None, summary=json.dumps({'before':previous, 'after':result}), performed_by=user['sub'])
        db.add(OutboxEvent(id=str(uuid7()), event_type='waage.calibration.updated', aggregate_id=scale.id,
            tenant_id=tenant_id, timestamp=business_now().replace(tzinfo=None), payload=json.dumps({'tenant_id': tenant_id,
                'actor': user['sub'], 'before': previous, 'after': result})))
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


# ===========================================================================
# DUAL-WIEGUNG â€” Doppelwiegung (Brutto/Tara als zwei separate WiegevorgÃ¤nge)
# ===========================================================================

# ============================================================
# Doppelwiegung auf dem kanonischen Wiegeschein
# ============================================================
#
# Bis zum 05.10.2026 schrieb dieser Teil ``domain_agrar.wiegungen`` — eine
# Tabelle, die keine Migration anlegt und die in keiner Datenbank existiert.
# Daneben stehen drei weitere Wiegetabellen. Geschrieben wird jetzt
# ``domain_inventory.weighing_tickets``: das Rueckgrat, auf das die
# Rueckverfolgbarkeit zeigt und das alle Felder der Doppelwiegung schon hat.
#
# Drei Fehler sind damit weg:
#
# 1. ``netto = abs(wiegung1 - wiegung2)`` — der Absolutbetrag verdeckte den
#    Vorzeichenfehler und machte aus einer Verwechslung der Eingaben ein
#    plausibles Nettogewicht, auf dem die Rechnung aufbaute.
# 2. Der JSONB-Rueckfall — schlug der INSERT fehl, wurde die ganze Wiegung als
#    undurchsichtiger Klumpen gespeichert, ohne Gewicht, ohne Waage, und der Weg
#    antwortete ``201 created``. Ein Wiegeschein ohne Gewicht ist kein Beleg.
# 3. Kein ``tenant_id`` — weder beim Schreiben noch beim Lesen.
#
# Entscheidungen: ``docs/quality-assurance/wiegung-kanonisch-20261005.md``.

from app.api.v1.schemas.waage_schemas import (  # noqa: E402
    WiegescheinMitDoppelwiegung,
    WiegescheinOut,
    WiegungAngelegt,
    WiegungErweitert,
)
from app.services import wiegung_service as wiegung  # noqa: E402

__all__ = ["WiegungErweitert", "WiegescheinMitDoppelwiegung"]


@router.post(
    "/wiegungen/dual",
    response_model=WiegungAngelegt,
    status_code=201,
    summary="Doppelwiegung buchen (Brutto und Tara)", dependencies=SCHREIBEN["LAGER"])
async def create_dual_wiegung(
    payload: WiegescheinMitDoppelwiegung,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Nimmt Brutto- und Tarawiegung entgegen und rechnet das Netto.

    ``netto = brutto - tara`` — ohne Absolutbetrag. Ist die Tara nicht kleiner
    als das Brutto, ist das ein Messfehler oder eine Verwechslung der beiden
    Waegungen; dann entsteht kein Wiegeschein, sondern ein 422. Das
    Nettogewicht ist die abgerechnete Menge.
    """
    ext = payload.wiegung_erweitert or WiegungErweitert()
    brutto, tara, netto = wiegung.netto_aus_doppelwiegung(
        ext.brutto_kg, ext.tara_kg, ext.netto_kg
    )
    richtung = wiegung.richtung(ext.zielschein_typ)

    schein_id = str(uuid7())
    try:
        scheinnummer = wiegung.naechste_scheinnummer(db, tenant_id)
        wiegung.schreiben(
            db,
            tenant_id,
            schein_id,
            scheinnummer,
            scale_id=payload.waage_id or ext.waage_id,
            vehicle_plate=payload.kfz_kennzeichen,
            brutto=brutto,
            tara=tara,
            netto=netto,
            richtung_=richtung,
            gosse=ext.gosse,
            muster_nr=ext.muster_nr,
            handwiegung=ext.handwiegung,
            ident_nr=ext.ident_nr,
            disposition_nr=payload.disponr,
            charge_nr=payload.charge_nr,
            article_id=payload.artikel_id,
            reference_doc=payload.partie_id,
            notes=payload.bemerkung,
        )
        finalize_menge_from_outbound_weighing(
            db,
            tenant_id=tenant_id,
            kennzeichen=payload.kfz_kennzeichen,
            netto_kg=netto,
            zielschein_typ=ext.zielschein_typ,
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Doppelwiegung nicht buchbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Wiegung nicht gebucht",
                "grund": str(fehler),
                "migration_hint": wiegung.MIGRATIONS_HINWEIS["X-Migration-Hint"],
            },
            headers=wiegung.MIGRATIONS_HINWEIS,
        ) from fehler

    return {
        "id": schein_id,
        "ticket_number": scheinnummer,
        "brutto_kg": brutto,
        "tara_kg": tara,
        "netto_kg": netto,
        "richtung": richtung,
        "gosse": ext.gosse,
        "handwiegung": ext.handwiegung,
    }


@router.get(
    "/wiegungen/{wiegeschein_id}/extended",
    response_model=WiegescheinOut,
    summary="Wiegeschein abrufen",
)
async def get_wiegung_extended(
    wiegeschein_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Den Wiegeschein des Mandanten lesen.

    Vorher hatte dieser Weg nicht einmal die Mandantenabhaengigkeit: Jedes Haus
    konnte jeden Wiegeschein lesen, wenn es die Kennung kannte.
    """
    try:
        return wiegung.holen(db, tenant_id, wiegeschein_id)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise wiegung.nicht_lesbar(db, fehler, "Wiegeschein", tenant_id) from fehler
