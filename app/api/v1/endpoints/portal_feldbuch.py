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

class PortalSchlagCreate(BaseModel):
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


class PortalSchlagUpdate(BaseModel):
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


class PortalMassnahmeCreate(BaseModel):
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


class PortalMassnahmeUpdate(BaseModel):
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

@router.get("/feldbuch/schlaege")
async def portal_list_schlaege(
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


@router.post("/feldbuch/schlaege", status_code=201)
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


@router.put("/feldbuch/schlaege/{schlag_id}")
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

@router.get("/feldbuch/massnahmen")
async def portal_list_massnahmen(
    schlag_id: Optional[str] = Query(None),
    typ: Optional[str] = Query(None),
    von: Optional[str] = Query(None),
    bis: Optional[str] = Query(None),
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


@router.post("/feldbuch/massnahmen", status_code=201)
async def portal_create_massnahme(
    data: PortalMassnahmeCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    customer_id: str = Depends(_get_customer_id),
) -> dict[str, Any]:
    massnahme = FeldbuchMassnahme(
        id=uuid7(),
        tenant_id=tenant_id,
        customer_id=customer_id,
        quelle="portal",
        **data.model_dump(),
    )
    db.add(massnahme)
    db.commit()
    db.refresh(massnahme)
    return _massnahme_to_dict(massnahme)


@router.put("/feldbuch/massnahmen/{massnahme_id}")
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
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(massnahme, field, value)
    db.commit()
    db.refresh(massnahme)
    return _massnahme_to_dict(massnahme)


# ────────────────────────────────────────────────────────────────────────────
# Stats
# ────────────────────────────────────────────────────────────────────────────

@router.get("/feldbuch/stats")
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

@router.get("/feldbuch/export")
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

@router.post("/feldbuch/import")
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
