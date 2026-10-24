"""
Quality Protocol API endpoints.
Handles quality protocol management for harvest acceptance.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
import base64

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from app.infrastructure.models import QualityProtocol

from app.core.data_quality_enforcement import build_dq_error_detail, evaluate_quality_protocol_datensatz
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.shared.events import IntegrationEvent, get_event_publisher
from app.infrastructure.eventbus.outbox import OutboxPublisher
from modules.agrar.services.quality_protocol_service import (
    create_quality_protocol,
    update_quality_protocol,
    finalize_quality_protocol,
    import_from_csv,
    import_from_json,
    get_latest_protocol,
    QualityProtocolCreate,
    QualityProtocolUpdate,
)
from modules.agrar.repositories.quality_protocol_repo import AcceptanceNotOwnedError, QualityProtocolRepositoryImpl

from app.api.v1.schemas.base import BaseSchema
from app.core.akteur import akteur_aus_request, gepruefter_akteur
from app.auth.deps import get_current_user
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

QUALITY_PROTOCOL_COMPLETED_EVENT = "agrar.quality_protocol.completed"


router = APIRouter()


def _build_quality_protocol_dq_datensatz(data: dict[str, object]) -> dict[str, object]:
    return {
        "ernteannahme_id": data.get("harvest_acceptance_id"),
        "quelle": data.get("source_type"),
        "feuchte_pct": data.get("moisture_pct"),
        "protein_pct": data.get("protein_pct"),
        "hl_gewicht": data.get("hl_weight_kg_per_hl"),
    }


# ── Pydantic Models ───────────────────────────────────────────────────────────────

class QualityProtocolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    """Output-Model für Qualitätsprotokoll."""
    id: str
    tenant_id: str
    harvest_acceptance_id: Optional[str] = None
    protocol_number: str
    version: int
    moisture_pct: Optional[float] = None
    impurities_pct: Optional[float] = None
    hl_weight_kg_per_hl: Optional[float] = None
    protein_pct: Optional[float] = None
    mycotoxin_ppb: Optional[float] = None
    other_values: Optional[dict] = None
    source_type: Optional[str] = None
    source_device_id: Optional[str] = None
    source_file_name: Optional[str] = None
    is_final: bool
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class QualityProtocolCreateIn(BaseModel):
    """Input-Model für Protokoll-Erstellung."""
    harvest_acceptance_id: Optional[str] = None
    protocol_number: Optional[str] = None
    moisture_pct: Optional[float] = None
    impurities_pct: Optional[float] = None
    hl_weight_kg_per_hl: Optional[float] = None
    protein_pct: Optional[float] = None
    mycotoxin_ppb: Optional[float] = None
    other_values: Optional[dict] = None
    source_type: str = "manual"
    source_device_id: Optional[str] = None


class QualityProtocolUpdateIn(BaseModel):
    """Input-Model für Protokoll-Update."""
    moisture_pct: Optional[float] = None
    impurities_pct: Optional[float] = None
    hl_weight_kg_per_hl: Optional[float] = None
    protein_pct: Optional[float] = None
    mycotoxin_ppb: Optional[float] = None
    other_values: Optional[dict] = None


# ── Helper Functions ────────────────────────────────────────────────────────────

def _get_user_id_from_request(request) -> Optional[str]:
    """Urheber aus dem geprueften Token (bis 19.10.2026 zuerst aus dem Client-Header ``X-User-ID``)."""
    return akteur_aus_request(request)


def _to_out(protocol) -> QualityProtocolOut:
    """Konvertiert Service-Model zu Output-Model."""
    return QualityProtocolOut(
        id=protocol.id,
        tenant_id=protocol.tenant_id,
        harvest_acceptance_id=protocol.harvest_acceptance_id,
        protocol_number=protocol.protocol_number,
        version=protocol.version,
        moisture_pct=float(protocol.moisture_pct) if protocol.moisture_pct is not None else None,
        impurities_pct=float(protocol.impurities_pct) if protocol.impurities_pct is not None else None,
        hl_weight_kg_per_hl=float(protocol.hl_weight_kg_per_hl) if protocol.hl_weight_kg_per_hl is not None else None,
        protein_pct=float(protocol.protein_pct) if protocol.protein_pct is not None else None,
        mycotoxin_ppb=float(protocol.mycotoxin_ppb) if protocol.mycotoxin_ppb is not None else None,
        other_values=protocol.other_values,
        source_type=protocol.source_type,
        source_device_id=protocol.source_device_id,
        source_file_name=protocol.source_file_name,
        is_final=protocol.is_final,
        approved_by=protocol.approved_by,
        approved_at=protocol.approved_at,
        created_at=protocol.created_at,
        created_by=protocol.created_by,
        updated_at=protocol.updated_at,
        updated_by=protocol.updated_by,
    )


# ── API Endpoints ───────────────────────────────────────────────────────────────

class QualityProtocolQueueOut(BaseModel):
    protocols: list[QualityProtocolOut]


@router.get("", response_model=QualityProtocolQueueOut, summary="Qualitaetsprotokolle auflisten")
async def list_protocols(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> QualityProtocolQueueOut:
    rows = db.query(QualityProtocol).filter(
        QualityProtocol.tenant_id == tenant_id,
    ).order_by(QualityProtocol.created_at.desc()).limit(200).all()
    repo = QualityProtocolRepositoryImpl(db, tenant_id)
    return QualityProtocolQueueOut(protocols=[_to_out(repo._to_service(row)) for row in rows])

@router.post("", response_model=QualityProtocolOut, status_code=201, summary="Protocol anlegen", dependencies=SCHREIBEN["AGRAR"])
async def create_protocol(
    payload: QualityProtocolCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Erstellt ein neues Qualitätsprotokoll."""
    user_id = _get_user_id_from_request(request)
    dq_result = evaluate_quality_protocol_datensatz(
        _build_quality_protocol_dq_datensatz(payload.model_dump(mode="python"))
    )
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("Qualitaetsprotokoll", dq_result))

    create_input = QualityProtocolCreate(
        tenant_id=tenant_id,
        harvest_acceptance_id=payload.harvest_acceptance_id,
        protocol_number=payload.protocol_number,
        moisture_pct=Decimal(str(payload.moisture_pct)) if payload.moisture_pct is not None else None,
        impurities_pct=Decimal(str(payload.impurities_pct)) if payload.impurities_pct is not None else None,
        hl_weight_kg_per_hl=Decimal(str(payload.hl_weight_kg_per_hl)) if payload.hl_weight_kg_per_hl is not None else None,
        protein_pct=Decimal(str(payload.protein_pct)) if payload.protein_pct is not None else None,
        mycotoxin_ppb=Decimal(str(payload.mycotoxin_ppb)) if payload.mycotoxin_ppb is not None else None,
        other_values=payload.other_values,
        source_type=payload.source_type,
        source_device_id=payload.source_device_id,
        created_by=user_id,
    )
    
    repo = QualityProtocolRepositoryImpl(db, tenant_id)
    try:
        protocol = create_quality_protocol(repo, create_input)
    except AcceptanceNotOwnedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    return _to_out(protocol)


@router.get("/{protocol_id}", response_model=QualityProtocolOut, summary="Protocol abrufen")
async def get_protocol(
    protocol_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft ein Qualitätsprotokoll ab."""
    repo = QualityProtocolRepositoryImpl(db, tenant_id)
    protocol = repo.get_by_id(protocol_id)
    
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Quality protocol {protocol_id} not found")
    
    if protocol.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return _to_out(protocol)


@router.get("/harvest-acceptance/{harvest_acceptance_id}", response_model=list[QualityProtocolOut], summary="Protocols by harvest acceptance abrufen")
async def get_protocols_by_harvest_acceptance(
    harvest_acceptance_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft alle Protokolle für eine Ernte-Annahme ab."""
    repo = QualityProtocolRepositoryImpl(db, tenant_id)
    try:
        protocols = repo.get_by_harvest_acceptance(harvest_acceptance_id)
    except AcceptanceNotOwnedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    # Filter nach tenant_id
    protocols = [p for p in protocols if p.tenant_id == tenant_id]
    
    return [_to_out(p) for p in protocols]


@router.get("/harvest-acceptance/{harvest_acceptance_id}/latest", response_model=QualityProtocolOut, summary="Latest protocol for harvest acceptance abrufen")
async def get_latest_protocol_for_harvest_acceptance(
    harvest_acceptance_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft das neueste Protokoll für eine Ernte-Annahme ab."""
    repo = QualityProtocolRepositoryImpl(db, tenant_id)
    try:
        protocol = get_latest_protocol(repo, harvest_acceptance_id)
    except AcceptanceNotOwnedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    if not protocol:
        raise HTTPException(status_code=404, detail=f"No quality protocol found for harvest acceptance {harvest_acceptance_id}")
    
    if protocol.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return _to_out(protocol)


@router.put("/{protocol_id}", response_model=QualityProtocolOut, summary="Protocol aktualisieren", dependencies=SCHREIBEN["AGRAR"])
async def update_protocol(
    protocol_id: str,
    payload: QualityProtocolUpdateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Aktualisiert ein Qualitätsprotokoll."""
    user_id = _get_user_id_from_request(request)
    
    repo = QualityProtocolRepositoryImpl(db, tenant_id)
    protocol = repo.get_by_id(protocol_id)
    
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Quality protocol {protocol_id} not found")
    
    if protocol.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_input = QualityProtocolUpdate(
        moisture_pct=Decimal(str(payload.moisture_pct)) if payload.moisture_pct is not None else None,
        impurities_pct=Decimal(str(payload.impurities_pct)) if payload.impurities_pct is not None else None,
        hl_weight_kg_per_hl=Decimal(str(payload.hl_weight_kg_per_hl)) if payload.hl_weight_kg_per_hl is not None else None,
        protein_pct=Decimal(str(payload.protein_pct)) if payload.protein_pct is not None else None,
        mycotoxin_ppb=Decimal(str(payload.mycotoxin_ppb)) if payload.mycotoxin_ppb is not None else None,
        other_values=payload.other_values,
        updated_by=user_id,
    )
    
    try:
        protocol = update_quality_protocol(repo, protocol_id, update_input)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_out(protocol)


@router.post("/{protocol_id}/approve", response_model=QualityProtocolOut, summary="Protocol finalize", dependencies=SCHREIBEN["QUALITAET"])
@router.post("/{protocol_id}/finalize", response_model=QualityProtocolOut, summary="Protocol finalize", dependencies=SCHREIBEN["AGRAR"])
async def finalize_protocol(
    protocol_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(get_current_user),
):
    """Finalisiert ein Qualitaetsprotokoll und schreibt Outbox fuer Workspace-SSE."""
    approved_by = gepruefter_akteur(user)
    repo = QualityProtocolRepositoryImpl(db, tenant_id)
    protocol = repo.get_by_id(protocol_id)
    
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Quality protocol {protocol_id} not found")
    
    if protocol.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if protocol.is_final:
        raise HTTPException(status_code=409, detail=f"Quality protocol {protocol_id} is already finalized")

    try:
        protocol = finalize_quality_protocol(repo, protocol_id, approved_by)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    now = datetime.utcnow()
    event_payload = {
        "protocol_id": protocol.id,
        "acceptance_id": protocol.harvest_acceptance_id,
        "approved_by": approved_by,
        "is_final": True,
    }
    outbox = OutboxPublisher(db, get_event_publisher())
    try:
        await outbox.store_event(
            IntegrationEvent(
                aggregate_id=protocol.id,
                timestamp=now,
                event_type=QUALITY_PROTOCOL_COMPLETED_EVENT,
                payload=event_payload,
            ),
            tenant_id=tenant_id,
            mirror_on_store=False,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return _to_out(protocol)


@router.post("/import/csv", response_model=QualityProtocolOut, status_code=201, summary="Protocol from csv importieren", dependencies=SCHREIBEN["AGRAR"])
async def import_protocol_from_csv(
    harvest_acceptance_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Importiert Laborwerte aus CSV."""
    user_id = _get_user_id_from_request(request)
    
    # Lese Dateiinhalt
    content = await file.read()
    csv_content = content.decode("utf-8")
    import csv
    from io import StringIO

    row = next(csv.DictReader(StringIO(csv_content)), None)
    if row is None:
        raise HTTPException(status_code=422, detail="CSV file is empty")

    def _parse_float(value: Optional[str]) -> float | None:
        if value is None or value.strip() == "":
            return None
        return float(value.replace(",", "."))

    dq_result = evaluate_quality_protocol_datensatz(
        _build_quality_protocol_dq_datensatz(
            {
                "harvest_acceptance_id": harvest_acceptance_id,
                "source_type": "import",
                "moisture_pct": _parse_float(row.get("moisture_pct")),
                "protein_pct": _parse_float(row.get("protein_pct")),
                "hl_weight_kg_per_hl": _parse_float(row.get("hl_weight_kg_per_hl")),
            }
        )
    )
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("Qualitaetsprotokoll", dq_result))

    repo = QualityProtocolRepositoryImpl(db, tenant_id)
    try:
        repo.ensure_acceptance_owned(harvest_acceptance_id)
    except AcceptanceNotOwnedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    protocol = import_from_csv(
        repo,
        tenant_id=tenant_id,
        harvest_acceptance_id=harvest_acceptance_id,
        csv_content=csv_content,
        file_name=file.filename or "import.csv",
        created_by=user_id,
    )
    
    return _to_out(protocol)


@router.post("/import/json", response_model=QualityProtocolOut, status_code=201, summary="Protocol from json importieren", dependencies=SCHREIBEN["AGRAR"])
async def import_protocol_from_json(
    harvest_acceptance_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Importiert Laborwerte aus JSON."""
    user_id = _get_user_id_from_request(request)
    
    # Lese Dateiinhalt
    content = await file.read()
    json_content = content.decode("utf-8")
    import json

    data = json.loads(json_content)
    dq_result = evaluate_quality_protocol_datensatz(
        _build_quality_protocol_dq_datensatz(
            {
                "harvest_acceptance_id": harvest_acceptance_id,
                "source_type": "import",
                "moisture_pct": data.get("moisture_pct"),
                "protein_pct": data.get("protein_pct"),
                "hl_weight_kg_per_hl": data.get("hl_weight_kg_per_hl"),
            }
        )
    )
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("Qualitaetsprotokoll", dq_result))

    repo = QualityProtocolRepositoryImpl(db, tenant_id)
    try:
        repo.ensure_acceptance_owned(harvest_acceptance_id)
    except AcceptanceNotOwnedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    protocol = import_from_json(
        repo,
        tenant_id=tenant_id,
        harvest_acceptance_id=harvest_acceptance_id,
        json_content=json_content,
        file_name=file.filename or "import.json",
        created_by=user_id,
    )
    
    return _to_out(protocol)

