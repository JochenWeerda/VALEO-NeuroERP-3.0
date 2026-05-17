"""eBilanz / ELSTER Direktschnittstelle Stub."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/ebilanz", tags=["finance", "ebilanz", "elster"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class EBilanzExportRequest(BaseModel):
    wirtschaftsjahr: int
    bilanzart: str  # HGB / IFRS / EStG
    berichtsperiode_von: str  # ISO date
    berichtsperiode_bis: str  # ISO date
    steuernummer: str
    finanzamt_nr: str


class EBilanzExportResult(BaseModel):
    export_id: str
    status: str  # ERSTELLT / VALIDIERT / UEBERTRAGEN / FEHLER
    xbrl_paketgroesse_kb: int = 42
    taxonomie_version: str = "6.7"
    validierungsfehler: list[str] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/export/erstellen", response_model=EBilanzExportResult, status_code=201)
def erstellen(
    payload: EBilanzExportRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    export_id = str(uuid.uuid4())

    # Persist best-effort
    try:
        db.execute(
            text(
                "INSERT INTO domain_finance.ebilanz_exports "
                "(id, tenant_id, wirtschaftsjahr, bilanzart, berichtsperiode_von, "
                "berichtsperiode_bis, steuernummer, finanzamt_nr, status, "
                "taxonomie_version, xbrl_paketgroesse_kb, erstellt_am) "
                "VALUES (:id, :tenant_id, :wj, :bilanzart, :von, :bis, :stnr, :fanr, "
                "'ERSTELLT', '6.7', 42, NOW())"
            ),
            {
                "id": export_id,
                "tenant_id": tenant_id,
                "wj": payload.wirtschaftsjahr,
                "bilanzart": payload.bilanzart,
                "von": payload.berichtsperiode_von,
                "bis": payload.berichtsperiode_bis,
                "stnr": payload.steuernummer,
                "fanr": payload.finanzamt_nr,
            },
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "export_id": export_id,
        "status": "ERSTELLT",
        "xbrl_paketgroesse_kb": 42,
        "taxonomie_version": "6.7",
        "validierungsfehler": [],
    }


@router.post("/export/{export_id}/validieren")
def validieren(
    export_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    # Check existence (best-effort)
    try:
        db.execute(
            text(
                "SELECT id FROM domain_finance.ebilanz_exports WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": export_id, "tenant_id": tenant_id},
        ).first()
        db.execute(
            text(
                "UPDATE domain_finance.ebilanz_exports SET status='VALIDIERT' "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": export_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "export_id": export_id,
        "status": "VALIDIERT",
        "validierungsfehler": [],
        "hinweise": [
            "Taxonomie-Version 6.7 gültig",
            "Pflichtfelder vollständig",
        ],
    }


@router.post("/export/{export_id}/uebertragen")
def uebertragen(
    export_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    ticket = uuid.uuid4().hex[:16].upper()

    try:
        db.execute(
            text(
                "UPDATE domain_finance.ebilanz_exports SET status='UEBERTRAGEN', "
                "elster_transfer_ticket=:ticket, uebertragen_am=NOW() "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"ticket": ticket, "id": export_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "export_id": export_id,
        "status": "UEBERTRAGEN",
        "elster_transfer_ticket": ticket,
        "uebertragen_am": date.today().isoformat(),
    }


@router.get("/exports")
def list_exports(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        rows = db.execute(
            text(
                "SELECT id AS export_id, status, taxonomie_version, xbrl_paketgroesse_kb, "
                "wirtschaftsjahr, bilanzart, erstellt_am "
                "FROM domain_finance.ebilanz_exports WHERE tenant_id=:tenant_id "
                "ORDER BY erstellt_am DESC"
            ),
            {"tenant_id": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []
