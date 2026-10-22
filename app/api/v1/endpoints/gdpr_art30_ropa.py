"""
DSGVO Art. 30 — Verzeichnis von Verarbeitungstätigkeiten (Records of Processing Activities, RoPA).

Pflichtinhalt nach Art. 30 Abs. 1 DSGVO:
  a) Name und Kontakt des Verantwortlichen
  b) Zwecke der Verarbeitung
  c) Kategorien betroffener Personen
  d) Kategorien personenbezogener Daten
  e) Kategorien von Empfängern
  f) Übermittlungen an Drittländer + geeignete Garantien
  g) Vorgesehene Fristen für Löschung
  h) Technisch-organisatorische Maßnahmen (Art. 32 DSGVO)

Endpoints:
  GET    /gdpr/art30/activities           — alle Aktivitäten des Mandanten
  POST   /gdpr/art30/activities           — neue Aktivität anlegen
  GET    /gdpr/art30/activities/{id}      — Einzelansicht
  PUT    /gdpr/art30/activities/{id}      — aktualisieren
  DELETE /gdpr/art30/activities/{id}      — löschen (keine GoBD-Relevanz bei reinen Prozessbeschreibungen)
  GET    /gdpr/art30/activities/export/json — maschinenlesbarer Export für Datenschutzbehörde
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.gdpr_art30_ropa_schemas import GdprArt30RopaOut


router = APIRouter(prefix="/gdpr/art30", tags=["gdpr", "compliance", "art30"])

# ---------------------------------------------------------------------------
# Schemas (Art. 30 Abs. 1 Pflichtfelder a–h)
# ---------------------------------------------------------------------------

class ProcessingActivityIn(BaseModel):
    """Eingabe-Schema für eine Verarbeitungstätigkeit (Art. 30 Abs. 1 DSGVO)."""

    # a) Verantwortlicher
    controller_name: str = Field(..., max_length=200, description="Name des Verantwortlichen (Art. 30 Abs. 1 lit. a)")
    controller_contact: str = Field(..., max_length=500, description="Kontaktdaten / Datenschutzbeauftragter")

    # b) Zweck
    purpose: str = Field(..., max_length=1000, description="Zwecke der Verarbeitung (Art. 30 Abs. 1 lit. b)")

    # c) Kategorien betroffener Personen
    subject_categories: list[str] = Field(
        default_factory=list,
        description="Kategorien betroffener Personen, z. B. Kunden, Mitarbeiter, Lieferanten",
    )

    # d) Kategorien personenbezogener Daten
    data_categories: list[str] = Field(
        default_factory=list,
        description="Kategorien personenbezogener Daten, z. B. Name, Adresse, Bankverbindung",
    )

    # e) Empfänger
    recipients: list[str] = Field(
        default_factory=list,
        description="Kategorien von Empfängern (Art. 30 Abs. 1 lit. e)",
    )

    # f) Drittlandtransfers
    third_country_transfers: list[dict[str, str]] = Field(
        default_factory=list,
        description="Drittlandtransfers mit Land und Garantiemechanismus (Art. 30 Abs. 1 lit. f)",
    )

    # g) Löschfristen
    retention_period: str = Field(
        default="",
        max_length=500,
        description="Vorgesehene Löschfristen (Art. 30 Abs. 1 lit. g)",
    )

    # h) TOMs
    toms: str = Field(
        default="",
        max_length=2000,
        description="Technisch-organisatorische Maßnahmen (Art. 32 DSGVO / Art. 30 Abs. 1 lit. h)",
    )

    # Zusatzfelder
    legal_basis: str = Field(
        default="",
        max_length=200,
        description="Rechtsgrundlage (Art. 6 Abs. 1 DSGVO), z. B. Einwilligung, Vertragserfüllung",
    )
    system_or_tool: str = Field(default="", max_length=200, description="Eingesetztes System / Tool")
    status: str = Field(
        default="AKTIV",
        pattern="^(AKTIV|INAKTIV|ENTWURF)$",
        description="Status der Verarbeitungstätigkeit",
    )


class ProcessingActivityOut(ProcessingActivityIn):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# In-Memory Store (konsistent mit gdpr_requests.py Muster)
# Für produktive Deployments: Migration domain_compliance.processing_activities
# ---------------------------------------------------------------------------

_store: dict[str, dict[str, Any]] = {}


def _store_key(tenant_id: str, activity_id: str) -> str:
    return f"{tenant_id}::{activity_id}"


def _get_all(tenant_id: str) -> list[dict[str, Any]]:
    prefix = f"{tenant_id}::"
    return [v for k, v in _store.items() if k.startswith(prefix)]


def _try_db_list(db: Session, tenant_id: str) -> list[dict[str, Any]] | None:
    """Liest aus domain_compliance.processing_activities wenn Tabelle existiert."""
    try:
        rows = db.execute(
            text(
                "SELECT id, tenant_id, controller_name, controller_contact, purpose,"
                " subject_categories, data_categories, recipients, third_country_transfers,"
                " retention_period, toms, legal_basis, system_or_tool, status,"
                " created_at, updated_at"
                " FROM domain_compliance.processing_activities"
                " WHERE tenant_id = :tenant_id ORDER BY created_at DESC"
            ),
            {"tenant_id": tenant_id},
        ).mappings().all()
        result = []
        for row in rows:
            d = dict(row)
            for json_col in ("subject_categories", "data_categories", "recipients", "third_country_transfers"):
                if isinstance(d.get(json_col), str):
                    try:
                        d[json_col] = json.loads(d[json_col])
                    except Exception:  # noqa: BLE001
                        d[json_col] = []
            result.append(d)
        return result
    except Exception:  # noqa: BLE001 — Tabelle noch nicht migriert → Fallback auf In-Memory
        return None


def _try_db_get(db: Session, tenant_id: str, activity_id: str) -> dict[str, Any] | None:
    try:
        row = db.execute(
            text(
                "SELECT * FROM domain_compliance.processing_activities"
                " WHERE tenant_id = :tenant_id AND id = :id"
            ),
            {"tenant_id": tenant_id, "id": activity_id},
        ).mappings().fetchone()
        if row is None:
            return None
        d = dict(row)
        for json_col in ("subject_categories", "data_categories", "recipients", "third_country_transfers"):
            if isinstance(d.get(json_col), str):
                try:
                    d[json_col] = json.loads(d[json_col])
                except Exception:  # noqa: BLE001
                    d[json_col] = []
        return d
    except Exception:  # noqa: BLE001
        return None


def _try_db_upsert(db: Session, tenant_id: str, data: dict[str, Any], *, update: bool = False) -> bool:
    try:
        if update:
            db.execute(
                text(
                    "UPDATE domain_compliance.processing_activities"
                    " SET controller_name=:controller_name, controller_contact=:controller_contact,"
                    "     purpose=:purpose, subject_categories=:subject_categories,"
                    "     data_categories=:data_categories, recipients=:recipients,"
                    "     third_country_transfers=:third_country_transfers,"
                    "     retention_period=:retention_period, toms=:toms,"
                    "     legal_basis=:legal_basis, system_or_tool=:system_or_tool,"
                    "     status=:status, updated_at=:updated_at"
                    " WHERE id=:id AND tenant_id=:tenant_id"
                ),
                {**data, "tenant_id": tenant_id},
            )
        else:
            db.execute(
                text(
                    "INSERT INTO domain_compliance.processing_activities"
                    " (id, tenant_id, controller_name, controller_contact, purpose,"
                    "  subject_categories, data_categories, recipients, third_country_transfers,"
                    "  retention_period, toms, legal_basis, system_or_tool, status, created_at, updated_at)"
                    " VALUES (:id, :tenant_id, :controller_name, :controller_contact, :purpose,"
                    "  :subject_categories, :data_categories, :recipients, :third_country_transfers,"
                    "  :retention_period, :toms, :legal_basis, :system_or_tool, :status, :created_at, :updated_at)"
                ),
                {**data, "tenant_id": tenant_id},
            )
        db.commit()
        return True
    except Exception:  # noqa: BLE001
        db.rollback()
        return False


def _try_db_delete(db: Session, tenant_id: str, activity_id: str) -> bool:
    try:
        db.execute(
            text(
                "DELETE FROM domain_compliance.processing_activities"
                " WHERE id = :id AND tenant_id = :tenant_id"
            ),
            {"id": activity_id, "tenant_id": tenant_id},
        )
        db.commit()
        return True
    except Exception:  # noqa: BLE001
        db.rollback()
        return False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

def _serialize(obj: Any) -> Any:
    """Rekursive Datetime-Serialisierung für JSON-Export."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(i) for i in obj]
    return obj


@router.get(
    "/activities/export/json",
    response_model=GdprArt30RopaOut,
    summary="RoPA-Export als JSON (Datenschutzbehörde)",
)
def export_activities_json(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> JSONResponse:
    """
    Maschinenlesbarer Export aller Verarbeitungstätigkeiten nach Art. 30 DSGVO.
    Geeignet für Vorlage bei Datenschutzbehörde oder DSB-Audit.
    """
    rows = _try_db_list(db, tenant_id) or _get_all(tenant_id)
    payload = {
        "art30_verarbeitungsverzeichnis": {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id,
            "total_activities": len(rows),
            "activities": _serialize(rows),
        }
    }
    return JSONResponse(
        content=payload,
        headers={
            "Content-Disposition": 'attachment; filename="art30-verarbeitungsverzeichnis.json"',
        },
    )


@router.get("/activities", response_model=list[ProcessingActivityOut], summary="Alle Verarbeitungstätigkeiten auflisten")
def list_activities(
    status: Optional[str] = Query(None, description="Filter: AKTIV / INAKTIV / ENTWURF"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    rows = _try_db_list(db, tenant_id)
    if rows is None:
        rows = _get_all(tenant_id)
    if status:
        rows = [r for r in rows if r.get("status") == status.upper()]
    return rows


@router.post("/activities", response_model=ProcessingActivityOut, status_code=201, summary="Verarbeitungstätigkeit anlegen")
def create_activity(
    payload: ProcessingActivityIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Neue Verarbeitungstätigkeit nach Art. 30 DSGVO anlegen."""
    now = datetime.now(timezone.utc)
    activity_id = str(uuid4())
    data: dict[str, Any] = {
        "id": activity_id,
        **payload.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    # JSON-Serialisierung für DB-Persistenz
    db_data = {
        **data,
        "subject_categories": json.dumps(data["subject_categories"]),
        "data_categories": json.dumps(data["data_categories"]),
        "recipients": json.dumps(data["recipients"]),
        "third_country_transfers": json.dumps(data["third_country_transfers"]),
    }
    persisted = _try_db_upsert(db, tenant_id, db_data)
    if not persisted:
        _store[_store_key(tenant_id, activity_id)] = {**data, "tenant_id": tenant_id}
    return {**data, "tenant_id": tenant_id}


@router.get("/activities/{activity_id}", response_model=ProcessingActivityOut, summary="Einzelne Verarbeitungstätigkeit abrufen")
def get_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    row = _try_db_get(db, tenant_id, activity_id)
    if row is None:
        row = _store.get(_store_key(tenant_id, activity_id))
    if row is None:
        raise HTTPException(status_code=404, detail=f"Verarbeitungstätigkeit {activity_id} nicht gefunden")
    return row


@router.put("/activities/{activity_id}", response_model=ProcessingActivityOut, summary="Verarbeitungstätigkeit aktualisieren")
def update_activity(
    activity_id: str,
    payload: ProcessingActivityIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    existing = _try_db_get(db, tenant_id, activity_id) or _store.get(_store_key(tenant_id, activity_id))
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Verarbeitungstätigkeit {activity_id} nicht gefunden")
    now = datetime.now(timezone.utc)
    updated: dict[str, Any] = {
        **existing,
        **payload.model_dump(),
        "id": activity_id,
        "updated_at": now,
    }
    db_data = {
        **updated,
        "subject_categories": json.dumps(updated["subject_categories"]),
        "data_categories": json.dumps(updated["data_categories"]),
        "recipients": json.dumps(updated["recipients"]),
        "third_country_transfers": json.dumps(updated["third_country_transfers"]),
    }
    persisted = _try_db_upsert(db, tenant_id, db_data, update=True)
    if not persisted:
        _store[_store_key(tenant_id, activity_id)] = {**updated, "tenant_id": tenant_id}
    return {**updated, "tenant_id": tenant_id}


@router.delete("/activities/{activity_id}", status_code=204, summary="Verarbeitungstätigkeit löschen",
    response_class=Response, response_model=None
)
def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    existing = _try_db_get(db, tenant_id, activity_id) or _store.get(_store_key(tenant_id, activity_id))
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Verarbeitungstätigkeit {activity_id} nicht gefunden")
    db_deleted = _try_db_delete(db, tenant_id, activity_id)
    if not db_deleted:
        _store.pop(_store_key(tenant_id, activity_id), None)
    return Response(status_code=204)
