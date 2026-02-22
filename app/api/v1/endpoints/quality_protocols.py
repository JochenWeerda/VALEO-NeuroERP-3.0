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
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.inventory.api.inventory_auth import require_inventory_admin
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
from modules.agrar.repositories.quality_protocol_repo import QualityProtocolRepositoryImpl

router = APIRouter()


# ── Pydantic Models ───────────────────────────────────────────────────────────────

class QualityProtocolOut(BaseModel):
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

    class Config:
        from_attributes = True


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


class QualityProtocolFinalizeIn(BaseModel):
    """Input-Model für Protokoll-Finalisierung."""
    approved_by: str = Field(..., min_length=1)


# ── Helper Functions ────────────────────────────────────────────────────────────

def _get_user_id_from_request(request) -> Optional[str]:
    """Holt User-ID aus Request (Placeholder)."""
    # TODO: Aus Request-Header oder JWT-Token extrahieren
    return None


def _to_out(protocol) -> QualityProtocolOut:
    """Konvertiert Service-Model zu Output-Model."""
    return QualityProtocolOut(
        id=protocol.id,
        tenant_id=protocol.tenant_id,
        harvest_acceptance_id=protocol.harvest_acceptance_id,
        protocol_number=protocol.protocol_number,
        version=protocol.version,
        moisture_pct=float(protocol.moisture_pct) if protocol.moisture_pct else None,
        impurities_pct=float(protocol.impurities_pct) if protocol.impurities_pct else None,
        hl_weight_kg_per_hl=float(protocol.hl_weight_kg_per_hl) if protocol.hl_weight_kg_per_hl else None,
        protein_pct=float(protocol.protein_pct) if protocol.protein_pct else None,
        mycotoxin_ppb=float(protocol.mycotoxin_ppb) if protocol.mycotoxin_ppb else None,
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

@router.post("", response_model=QualityProtocolOut, status_code=201)
async def create_protocol(
    payload: QualityProtocolCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Erstellt ein neues Qualitätsprotokoll."""
    user_id = _get_user_id_from_request(request)
    
    create_input = QualityProtocolCreate(
        tenant_id=tenant_id,
        harvest_acceptance_id=payload.harvest_acceptance_id,
        protocol_number=payload.protocol_number,
        moisture_pct=Decimal(str(payload.moisture_pct)) if payload.moisture_pct else None,
        impurities_pct=Decimal(str(payload.impurities_pct)) if payload.impurities_pct else None,
        hl_weight_kg_per_hl=Decimal(str(payload.hl_weight_kg_per_hl)) if payload.hl_weight_kg_per_hl else None,
        protein_pct=Decimal(str(payload.protein_pct)) if payload.protein_pct else None,
        mycotoxin_ppb=Decimal(str(payload.mycotoxin_ppb)) if payload.mycotoxin_ppb else None,
        other_values=payload.other_values,
        source_type=payload.source_type,
        source_device_id=payload.source_device_id,
        created_by=user_id,
    )
    
    repo = QualityProtocolRepositoryImpl(db)
    protocol = create_quality_protocol(repo, create_input)
    
    return _to_out(protocol)


@router.get("/{protocol_id}", response_model=QualityProtocolOut)
async def get_protocol(
    protocol_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft ein Qualitätsprotokoll ab."""
    repo = QualityProtocolRepositoryImpl(db)
    protocol = repo.get_by_id(protocol_id)
    
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Quality protocol {protocol_id} not found")
    
    if protocol.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return _to_out(protocol)


@router.get("/harvest-acceptance/{harvest_acceptance_id}", response_model=list[QualityProtocolOut])
async def get_protocols_by_harvest_acceptance(
    harvest_acceptance_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft alle Protokolle für eine Ernte-Annahme ab."""
    repo = QualityProtocolRepositoryImpl(db)
    protocols = repo.get_by_harvest_acceptance(harvest_acceptance_id)
    
    # Filter nach tenant_id
    protocols = [p for p in protocols if p.tenant_id == tenant_id]
    
    return [_to_out(p) for p in protocols]


@router.get("/harvest-acceptance/{harvest_acceptance_id}/latest", response_model=QualityProtocolOut)
async def get_latest_protocol_for_harvest_acceptance(
    harvest_acceptance_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Ruft das neueste Protokoll für eine Ernte-Annahme ab."""
    repo = QualityProtocolRepositoryImpl(db)
    protocol = get_latest_protocol(repo, harvest_acceptance_id)
    
    if not protocol:
        raise HTTPException(status_code=404, detail=f"No quality protocol found for harvest acceptance {harvest_acceptance_id}")
    
    if protocol.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return _to_out(protocol)


@router.put("/{protocol_id}", response_model=QualityProtocolOut)
async def update_protocol(
    protocol_id: str,
    payload: QualityProtocolUpdateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    request: Request = None,
):
    """Aktualisiert ein Qualitätsprotokoll."""
    user_id = _get_user_id_from_request(request)
    
    repo = QualityProtocolRepositoryImpl(db)
    protocol = repo.get_by_id(protocol_id)
    
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Quality protocol {protocol_id} not found")
    
    if protocol.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_input = QualityProtocolUpdate(
        moisture_pct=Decimal(str(payload.moisture_pct)) if payload.moisture_pct else None,
        impurities_pct=Decimal(str(payload.impurities_pct)) if payload.impurities_pct else None,
        hl_weight_kg_per_hl=Decimal(str(payload.hl_weight_kg_per_hl)) if payload.hl_weight_kg_per_hl else None,
        protein_pct=Decimal(str(payload.protein_pct)) if payload.protein_pct else None,
        mycotoxin_ppb=Decimal(str(payload.mycotoxin_ppb)) if payload.mycotoxin_ppb else None,
        other_values=payload.other_values,
        updated_by=user_id,
    )
    
    protocol = update_quality_protocol(repo, protocol_id, update_input)
    return _to_out(protocol)


@router.post("/{protocol_id}/approve", response_model=QualityProtocolOut)
@router.post("/{protocol_id}/finalize", response_model=QualityProtocolOut)
async def finalize_protocol(
    protocol_id: str,
    payload: QualityProtocolFinalizeIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Finalisiert ein Qualitätsprotokoll."""
    repo = QualityProtocolRepositoryImpl(db)
    protocol = repo.get_by_id(protocol_id)
    
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Quality protocol {protocol_id} not found")
    
    if protocol.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    protocol = finalize_quality_protocol(repo, protocol_id, payload.approved_by)
    return _to_out(protocol)


@router.post("/import/csv", response_model=QualityProtocolOut, status_code=201)
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
    
    repo = QualityProtocolRepositoryImpl(db)
    protocol = import_from_csv(
        repo,
        tenant_id=tenant_id,
        harvest_acceptance_id=harvest_acceptance_id,
        csv_content=csv_content,
        file_name=file.filename or "import.csv",
        created_by=user_id,
    )
    
    return _to_out(protocol)


@router.post("/import/json", response_model=QualityProtocolOut, status_code=201)
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
    
    repo = QualityProtocolRepositoryImpl(db)
    protocol = import_from_json(
        repo,
        tenant_id=tenant_id,
        harvest_acceptance_id=harvest_acceptance_id,
        json_content=json_content,
        file_name=file.filename or "import.json",
        created_by=user_id,
    )
    
    return _to_out(protocol)

