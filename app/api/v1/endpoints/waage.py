"""
Waage API Endpoints - SQLAlchemy Version
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect as sa_inspect

from app.core.database import get_db

from app.domains.operations.repository import WaageRepository, WiegungRepository

router = APIRouter(prefix="/waage", tags=["Waage"])

# ============================================================
# PARTIE-PFLICHT-001 — Partiepflicht-Konfiguration
# ============================================================

_PARTIEPFLICHTIGE_WIEGETYPEN = ["ROHWARE", "SAATGUT", "DUENGER"]
_PARTIEPFLICHTIGE_ARTIKEL_GRUPPEN = ["GE", "RA", "SG"]


class PartiepflichtCheckRequest(BaseModel):
    artikel_id: str
    wiegetyp: str
    partie_id: Optional[str] = None


@router.get("/waagen/partiepflicht-config", response_model=dict)
async def get_partiepflicht_config(db: Session = Depends(get_db)) -> dict:
    """PARTIE-PFLICHT-001: Gibt zurück, welche Wiegetypen/Artikelgruppen Partiepflicht haben."""
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
    except Exception:
        pass
    return {
        "partiepflichtige_wiegetypen": _PARTIEPFLICHTIGE_WIEGETYPEN,
        "partiepflichtige_artikel_gruppen": _PARTIEPFLICHTIGE_ARTIKEL_GRUPPEN,
        "config_source": config_source,
    }


@router.post("/waagen/partiepflicht-check", response_model=dict)
async def check_partiepflicht(
    payload: PartiepflichtCheckRequest,
    db: Session = Depends(get_db),
) -> dict:
    """PARTIE-PFLICHT-001: Prüft ob für Artikel/Wiegetyp eine Partie Pflicht ist."""
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
        except Exception:
            pass

    if pflicht and not payload.partie_id:
        return {
            "valid": False,
            "reason": f"Partie erforderlich für Wiegetyp {payload.wiegetyp}",
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

@router.get("/waagen", response_model=List[dict])
async def list_waagen(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all Waagen with optional filtering"""
    repo = WaageRepository(db)
    if status:
        return _to_list(repo.get_by_status(status))
    return _to_list(repo.get_all(skip=skip, limit=limit))


@router.get("/waagen/{waage_id}", response_model=dict)
async def get_waage(waage_id: str, db: Session = Depends(get_db)):
    """Get a single Waage by ID"""
    repo = WaageRepository(db)
    waage = repo.get_by_id(waage_id)
    if not waage:
        raise HTTPException(status_code=404, detail=f"Waage {waage_id} not found")
    return _to_dict(waage)


@router.post("/waagen", response_model=dict, status_code=201)
async def create_waage(
    waage_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new Waage"""
    repo = WaageRepository(db)
    try:
        waage = repo.create(waage_data)
        return _to_dict(waage)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/waagen/{waage_id}", response_model=dict)
async def update_waage(
    waage_id: str,
    waage_data: dict,
    db: Session = Depends(get_db)
):
    """Update a Waage"""
    repo = WaageRepository(db)
    waage = repo.update(waage_id, waage_data)
    if not waage:
        raise HTTPException(status_code=404, detail=f"Waage {waage_id} not found")
    return _to_dict(waage)


@router.delete("/waagen/{waage_id}", status_code=204)
async def delete_waage(waage_id: str, db: Session = Depends(get_db)):
    """Delete a Waage"""
    repo = WaageRepository(db)
    if not repo.delete(waage_id):
        raise HTTPException(status_code=404, detail=f"Waage {waage_id} not found")


# === WIEGUNG ENDPOINTS ===

@router.get("/wiegungen", response_model=List[dict])
async def list_wiegungen(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    waage_id: Optional[str] = None,
    kennzeichen: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all Wiegungen with optional filtering"""
    repo = WiegungRepository(db)
    
    if waage_id:
        return _to_list(repo.get_by_waage(waage_id))
    if kennzeichen:
        return _to_list(repo.get_by_kennzeichen(kennzeichen))
    return _to_list(repo.get_all(skip=skip, limit=limit))


@router.get("/wiegungen/{wiegung_id}", response_model=dict)
async def get_wiegung(wiegung_id: str, db: Session = Depends(get_db)):
    """Get a single Wiegung by ID"""
    repo = WiegungRepository(db)
    wiegung = repo.get_by_id(wiegung_id)
    if not wiegung:
        raise HTTPException(status_code=404, detail=f"Wiegung {wiegung_id} not found")
    return _to_dict(wiegung)


@router.post("/wiegungen", response_model=dict, status_code=201)
async def create_wiegung(
    wiegung_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new Wiegung"""
    repo = WiegungRepository(db)

    # PARTIE-PFLICHT-001: Partiepflicht-Validierung
    wiegetyp = wiegung_data.get("wiegetyp") or wiegung_data.get("typ")
    if wiegetyp and wiegetyp.upper() in _PARTIEPFLICHTIGE_WIEGETYPEN:
        partie = (
            wiegung_data.get("partie_id")
            or wiegung_data.get("charge_id")
            or wiegung_data.get("lot_id")
        )
        if not partie:
            raise HTTPException(
                status_code=422,
                detail=f"Partie/Charge Pflichtfeld für Wiegetyp {wiegetyp}",
            )

    # Auto-calculate netto if not provided
    if "brutto" in wiegung_data and "tara" in wiegung_data and "netto" not in wiegung_data:
        wiegung_data["netto"] = wiegung_data["brutto"] - wiegung_data["tara"]

    try:
        wiegung = repo.create(wiegung_data)
        return _to_dict(wiegung)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/wiegungen/{wiegung_id}", status_code=204)
async def delete_wiegung(wiegung_id: str, db: Session = Depends(get_db)):
    """Delete a Wiegung"""
    repo = WiegungRepository(db)
    if not repo.delete(wiegung_id):
        raise HTTPException(status_code=404, detail=f"Wiegung {wiegung_id} not found")


# ===========================================================================
# WAAGE-LIVE-001 — ASCII-Import, Fehlerqueue, Kalibrierung
# ===========================================================================

# Module-level in-memory Fehlerqueue
_fehlerqueue: List[Dict[str, Any]] = []


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


@router.post("/waagen/import/ascii", response_model=dict, status_code=200)
async def import_ascii(
    file: UploadFile,
    waage_id: str = Form(...),
    fehler_toleranz: bool = Form(True),
    db: Session = Depends(get_db),
):
    """Importiert eine AMIC ASCII-Waagendatei (Satzarten W und Q)."""
    content = (await file.read()).decode("utf-8", errors="replace")
    lines = content.splitlines()

    imported: int = 0
    skipped: int = 0
    errors: List[str] = []
    wiegung_ids: List[str] = []
    last_wiegung_id: Optional[str] = None
    last_wiegung_nr: Optional[str] = None

    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(";")
        satzart = parts[0].upper()

        try:
            if satzart == "W":
                data = _parse_w_line(parts)
                new_id = str(uuid.uuid4())
                try:
                    db.execute(
                        text(
                            """
                            INSERT INTO agrar_wiegungen (
                                id, waage_id, wiegung_nr, datum, uhrzeit,
                                brutto_kg, tara_kg, netto_kg, kfz_kennzeichen,
                                lieferant_id, artikel_id, sorte, partie_id, silo_id,
                                qualitaet_feuchtigkeit, qualitaet_hl, qualitaet_bruch,
                                created_at
                            ) VALUES (
                                :id, :waage_id, :wiegung_nr, :datum, :uhrzeit,
                                :brutto_kg, :tara_kg, :netto_kg, :kfz_kennzeichen,
                                :lieferant_id, :artikel_id, :sorte, :partie_id, :silo_id,
                                :qualitaet_feuchtigkeit, :qualitaet_hl, :qualitaet_bruch,
                                now()
                            )
                            """
                        ),
                        {**data, "id": new_id, "waage_id": waage_id},
                    )
                    db.commit()
                    last_wiegung_id = new_id
                    last_wiegung_nr = data["wiegung_nr"]
                    wiegung_ids.append(new_id)
                    imported += 1
                except Exception as db_err:
                    db.rollback()
                    # Tabelle nicht vorhanden oder anderer DB-Fehler → queue entry
                    entry_id = str(uuid.uuid4())
                    _fehlerqueue.append(
                        {
                            "id": entry_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            "waage_id": waage_id,
                            "rohdaten": line,
                            "fehler_beschreibung": str(db_err),
                            "retry_count": 0,
                        }
                    )
                    err_msg = f"Zeile {lineno} DB-Fehler: {db_err}"
                    if not fehler_toleranz:
                        return {
                            "imported": imported,
                            "skipped": skipped,
                            "errors": [err_msg],
                            "wiegung_ids": wiegung_ids,
                        }
                    errors.append(err_msg)
                    skipped += 1

            elif satzart == "Q":
                q_data = _parse_q_line(parts)
                if last_wiegung_id and q_data["wiegung_nr"] == last_wiegung_nr:
                    try:
                        db.execute(
                            text(
                                """
                                INSERT INTO agrar_wiegung_qualitaet (
                                    id, wiegung_id, parameter, wert, einheit, created_at
                                ) VALUES (
                                    :id, :wiegung_id, :parameter, :wert, :einheit, now()
                                )
                                """
                            ),
                            {
                                "id": str(uuid.uuid4()),
                                "wiegung_id": last_wiegung_id,
                                "parameter": q_data["parameter"],
                                "wert": q_data["wert"],
                                "einheit": q_data["einheit"],
                            },
                        )
                        db.commit()
                    except Exception:
                        db.rollback()
                        # Qualitätstabelle fehlt → ignorieren (non-critical)
                        pass
                else:
                    skipped += 1
            else:
                skipped += 1

        except ValueError as parse_err:
            err_msg = f"Zeile {lineno} Parse-Fehler: {parse_err}"
            if not fehler_toleranz:
                return {
                    "imported": imported,
                    "skipped": skipped,
                    "errors": [err_msg],
                    "wiegung_ids": wiegung_ids,
                }
            errors.append(err_msg)
            skipped += 1

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "wiegung_ids": wiegung_ids,
    }


# ---------------------------------------------------------------------------
# 1b. Fehlerqueue
# ---------------------------------------------------------------------------

@router.get("/waagen/import/fehlerqueue", response_model=List[dict])
async def list_fehlerqueue():
    """Gibt alle Einträge der Import-Fehlerqueue zurück."""
    return _fehlerqueue


@router.post("/waagen/import/fehlerqueue/{entry_id}/retry", response_model=dict)
async def retry_fehlerqueue_entry(entry_id: str):
    """Erhöht retry_count für einen Fehlerqueue-Eintrag (Simulation)."""
    for entry in _fehlerqueue:
        if entry["id"] == entry_id:
            entry["retry_count"] += 1
            return {"status": "retry_scheduled", "entry": entry}
    raise HTTPException(status_code=404, detail=f"Fehlerqueue-Eintrag {entry_id} nicht gefunden")


@router.delete("/waagen/import/fehlerqueue/{entry_id}", status_code=204)
async def delete_fehlerqueue_entry(entry_id: str):
    """Löscht einen Eintrag aus der Import-Fehlerqueue."""
    global _fehlerqueue
    before = len(_fehlerqueue)
    _fehlerqueue = [e for e in _fehlerqueue if e["id"] != entry_id]
    if len(_fehlerqueue) == before:
        raise HTTPException(status_code=404, detail=f"Fehlerqueue-Eintrag {entry_id} nicht gefunden")


# ---------------------------------------------------------------------------
# 1c. Kalibrierungsstatus
# ---------------------------------------------------------------------------

def _kalibrierung_status(naechste_eichfaelligkeit: Optional[str]) -> str:
    if not naechste_eichfaelligkeit:
        return "faellig"
    try:
        faellig = date.fromisoformat(str(naechste_eichfaelligkeit)[:10])
        today = date.today()
        if faellig < today:
            delta = (today - faellig).days
            return "ueberfaellig" if delta > 30 else "faellig"
        return "ok"
    except (ValueError, TypeError):
        return "unbekannt"


@router.get("/waagen/{waage_id}/kalibrierung", response_model=dict)
async def get_kalibrierung(waage_id: str, db: Session = Depends(get_db)):
    """Gibt den Kalibrierungsstatus einer Waage zurück."""
    # Versuche kalibrierung_meta aus agrar_waagen zu lesen
    meta: Dict[str, Any] = {}
    try:
        row = db.execute(
            text("SELECT kalibrierung_meta FROM agrar_waagen WHERE id = :id"),
            {"id": waage_id},
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Waage {waage_id} nicht gefunden")
        meta = row[0] or {}
    except HTTPException:
        raise
    except Exception:
        # Tabelle/Spalte fehlt noch → leere Meta
        meta = {}

    letztes_eichdatum = meta.get("letztes_eichdatum")
    naechste = meta.get("naechste_eichfaelligkeit")

    return {
        "waage_id": waage_id,
        "letztes_eichdatum": letztes_eichdatum,
        "naechste_eichfaelligkeit": naechste,
        "kalibrierungsstatus": _kalibrierung_status(naechste),
        "eichamt": meta.get("eichamt"),
        "zertifikat_nr": meta.get("zertifikat_nr"),
    }


@router.patch("/waagen/{waage_id}/kalibrierung", response_model=dict)
async def update_kalibrierung(
    waage_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Aktualisiert Kalibrierungsdaten einer Waage (kalibrierung_meta JSONB)."""
    allowed_keys = {"letztes_eichdatum", "naechste_eichfaelligkeit", "eichamt", "zertifikat_nr"}
    update_data = {k: v for k, v in payload.items() if k in allowed_keys}

    try:
        # Lese bisherige Meta, merge, schreibe zurück
        row = db.execute(
            text("SELECT kalibrierung_meta FROM agrar_waagen WHERE id = :id"),
            {"id": waage_id},
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Waage {waage_id} nicht gefunden")
        current: Dict[str, Any] = row[0] or {}
        current.update(update_data)
        import json
        db.execute(
            text(
                "UPDATE agrar_waagen SET kalibrierung_meta = :meta::jsonb WHERE id = :id"
            ),
            {"meta": json.dumps(current), "id": waage_id},
        )
        db.commit()
        naechste = current.get("naechste_eichfaelligkeit")
        return {
            "waage_id": waage_id,
            "letztes_eichdatum": current.get("letztes_eichdatum"),
            "naechste_eichfaelligkeit": naechste,
            "kalibrierungsstatus": _kalibrierung_status(naechste),
            "eichamt": current.get("eichamt"),
            "zertifikat_nr": current.get("zertifikat_nr"),
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


# ===========================================================================
# DUAL-WIEGUNG — Doppelwiegung (Brutto/Tara als zwei separate Wiegevorgänge)
# ===========================================================================

import json as _json


class WiegungErweitert(BaseModel):
    waage_id: str
    ident_nr: Optional[str] = None
    wiegung1: Optional[float] = None
    wiegung2: Optional[float] = None
    netto: Optional[float] = None
    gosse: Optional[int] = None
    muster_nr: Optional[str] = None
    handwiegung: bool = False
    export_flag: bool = False
    zielschein_typ: Optional[str] = None  # VL=Verkaufslieferschein, EL=Eingangslieferschein


class WiegescheinMitDoppelwiegung(BaseModel):
    # Core Wiegevorgang fields (flexible dict-based submission)
    waage_id: Optional[str] = None
    lieferant_id: Optional[str] = None
    artikel_id: Optional[str] = None
    partie_id: Optional[str] = None
    # Extended dual-weighing block
    wiegung_erweitert: Optional[WiegungErweitert] = None
    zielscheinfestgelegt: bool = False
    disponr: Optional[str] = None
    charge_nr: Optional[str] = None
    kfz_kennzeichen: Optional[str] = None


@router.post("/wiegungen/dual", response_model=dict, status_code=201)
async def create_dual_wiegung(
    payload: WiegescheinMitDoppelwiegung,
    db: Session = Depends(get_db),
):
    """Doppelwiegung: Nimmt Brutto- und Tara-Wiegung entgegen und berechnet Netto automatisch."""
    ext = payload.wiegung_erweitert
    netto: Optional[float] = None
    gosse: Optional[int] = None
    zielschein_typ: Optional[str] = None

    if ext:
        # Compute netto from the two weighings if both provided
        if ext.wiegung1 is not None and ext.wiegung2 is not None:
            netto = abs(ext.wiegung1 - ext.wiegung2)
            # Propagate back into model (for storage)
            ext.netto = netto
        elif ext.netto is not None:
            netto = ext.netto
        gosse = ext.gosse
        zielschein_typ = ext.zielschein_typ

    new_id = str(uuid.uuid4())
    extended_data = ext.model_dump() if ext else {}
    extended_data["zielscheinfestgelegt"] = payload.zielscheinfestgelegt
    extended_data["disponr"] = payload.disponr
    extended_data["charge_nr"] = payload.charge_nr
    extended_data["kfz_kennzeichen"] = payload.kfz_kennzeichen

    # Try inserting with native columns first; fall back to JSONB extended_data column
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_agrar.wiegungen (
                    id, waage_id, lieferant_id, artikel_id, partie_id,
                    netto_kg, gosse, zielschein_typ, kfz_kennzeichen,
                    extended_data, created_at
                ) VALUES (
                    :id, :waage_id, :lieferant_id, :artikel_id, :partie_id,
                    :netto_kg, :gosse, :zielschein_typ, :kfz_kennzeichen,
                    :extended_data::jsonb, now()
                )
                """
            ),
            {
                "id": new_id,
                "waage_id": payload.waage_id or (ext.waage_id if ext else None),
                "lieferant_id": payload.lieferant_id,
                "artikel_id": payload.artikel_id,
                "partie_id": payload.partie_id,
                "netto_kg": netto,
                "gosse": gosse,
                "zielschein_typ": zielschein_typ,
                "kfz_kennzeichen": payload.kfz_kennzeichen,
                "extended_data": _json.dumps(extended_data),
            },
        )
        db.commit()
    except Exception as e:
        db.rollback()
        err_str = str(e).lower()
        # Column missing → fallback: store everything as JSONB in extended_data column
        if "column" in err_str or "does not exist" in err_str or "relation" in err_str:
            try:
                db.execute(
                    text(
                        """
                        INSERT INTO domain_agrar.wiegungen (id, extended_data, created_at)
                        VALUES (:id, :extended_data::jsonb, now())
                        """
                    ),
                    {"id": new_id, "extended_data": _json.dumps(extended_data)},
                )
                db.commit()
            except Exception as e2:
                db.rollback()
                raise HTTPException(
                    status_code=503,
                    detail=f"DB-Fehler (JSONB-Fallback): {e2}",
                    headers={"X-Migration-Hint": "Run: alembic upgrade head (domain_agrar.wiegungen fehlt)"},
                )
        else:
            raise HTTPException(
                status_code=503,
                detail=f"DB-Fehler: {e}",
                headers={"X-Migration-Hint": "Run: alembic upgrade head"},
            )

    return {
        "id": new_id,
        "netto": netto,
        "gosse": gosse,
        "zielschein_typ": zielschein_typ,
        "status": "created",
    }


@router.get("/wiegungen/{wiegeschein_id}/extended", response_model=dict)
async def get_wiegung_extended(wiegeschein_id: str, db: Session = Depends(get_db)):
    """Gibt erweiterte Daten einer Wiegung zurück inkl. Doppelwiegungsinformationen."""
    try:
        row = db.execute(
            text(
                "SELECT id, waage_id, netto_kg, gosse, zielschein_typ, "
                "kfz_kennzeichen, extended_data, created_at "
                "FROM domain_agrar.wiegungen WHERE id = :id"
            ),
            {"id": wiegeschein_id},
        ).fetchone()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"DB-Fehler: {e}",
            headers={"X-Migration-Hint": "Run: alembic upgrade head"},
        )

    if row is None:
        raise HTTPException(status_code=404, detail=f"Wiegung {wiegeschein_id} nicht gefunden")

    return {
        "id": row[0],
        "waage_id": row[1],
        "netto_kg": float(row[2]) if row[2] is not None else None,
        "gosse": row[3],
        "zielschein_typ": row[4],
        "kfz_kennzeichen": row[5],
        "extended_data": row[6] or {},
        "created_at": row[7].isoformat() if row[7] else None,
    }
