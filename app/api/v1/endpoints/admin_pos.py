"""Admin POS/TSE settings and DSFinV-K exports."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter()


class PosTerminalIn(BaseModel):
    terminal_code: str = Field(..., min_length=1, max_length=60)
    name: str = Field(..., min_length=1, max_length=120)
    location_name: Optional[str] = Field(default=None, max_length=120)
    branch_code: Optional[str] = Field(default=None, max_length=60)
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class PosTerminalOut(PosTerminalIn):
    id: str
    registered_at: Optional[datetime] = None
    unregistered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PosTseDeviceIn(BaseModel):
    terminal_id: str
    serial_number: str = Field(..., min_length=1, max_length=120)
    provider: Optional[str] = Field(default=None, max_length=120)
    api_endpoint: Optional[str] = Field(default=None, max_length=255)
    certificate_fingerprint: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(default="active", pattern="^(active|inactive|retired)$")
    activation_date: Optional[date] = None
    deactivation_date: Optional[date] = None
    last_heartbeat_at: Optional[datetime] = None
    settings: dict[str, Any] = Field(default_factory=dict)


class PosTseDeviceOut(PosTseDeviceIn):
    id: str
    created_at: datetime
    updated_at: datetime


class PosNoticeIn(BaseModel):
    terminal_id: Optional[str] = None
    tse_device_id: Optional[str] = None
    notice_type: str = Field(..., pattern="^(install|change|decommission)$")
    notice_status: str = Field(default="draft", pattern="^(draft|submitted|accepted|rejected)$")
    effective_date: date
    submitted_at: Optional[datetime] = None
    reference_number: Optional[str] = Field(default=None, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)


class PosNoticeOut(PosNoticeIn):
    id: str
    created_at: datetime
    updated_at: datetime


class DsfinvkExportRequest(BaseModel):
    period_from: date
    period_to: date
    generated_by: Optional[str] = Field(default=None, max_length=100)


class DsfinvkExportOut(BaseModel):
    id: str
    tenant_id: str
    period_from: date
    period_to: date
    status: str
    file_path: Optional[str] = None
    checksum_sha256: Optional[str] = None
    row_count: int
    generated_by: Optional[str] = None
    generated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


def _map_row_to_model(row: Any, model_cls: type[BaseModel]) -> BaseModel:
    payload = dict(row)
    for key in ("metadata", "settings", "payload"):
        if key in payload and payload[key] is None:
            payload[key] = {}
    return model_cls(**payload)


@router.get("/pos/terminals", response_model=list[PosTerminalOut])
async def list_pos_terminals(
    include_inactive: bool = Query(default=False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    sql = """
        SELECT *
        FROM domain_docflow.pos_terminals
        WHERE tenant_id = :tenant_id
    """
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if not include_inactive:
        sql += " AND is_active = TRUE"
    sql += " ORDER BY terminal_code ASC"
    rows = db.execute(text(sql), params).mappings().all()
    return [_map_row_to_model(row, PosTerminalOut) for row in rows]


@router.post("/pos/terminals", response_model=PosTerminalOut, status_code=201)
async def create_pos_terminal(
    payload: PosTerminalIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_docflow.pos_terminals
            (id, tenant_id, terminal_code, name, location_name, branch_code, is_active, metadata, registered_at, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :terminal_code, :name, :location_name, :branch_code, :is_active, CAST(:metadata AS jsonb), NOW(), NOW(), NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "terminal_code": payload.terminal_code,
            "name": payload.name,
            "location_name": payload.location_name,
            "branch_code": payload.branch_code,
            "is_active": payload.is_active,
            "metadata": json.dumps(payload.metadata),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_docflow.pos_terminals WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _map_row_to_model(row, PosTerminalOut)


@router.put("/pos/terminals/{terminal_id}", response_model=PosTerminalOut)
async def update_pos_terminal(
    terminal_id: str,
    payload: PosTerminalIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    exists = db.execute(
        text("SELECT id FROM domain_docflow.pos_terminals WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": terminal_id},
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Terminal not found")

    db.execute(
        text(
            """
            UPDATE domain_docflow.pos_terminals
            SET terminal_code = :terminal_code,
                name = :name,
                location_name = :location_name,
                branch_code = :branch_code,
                is_active = :is_active,
                metadata = CAST(:metadata AS jsonb),
                updated_at = NOW(),
                unregistered_at = CASE WHEN :is_active = FALSE THEN COALESCE(unregistered_at, NOW()) ELSE NULL END
            WHERE tenant_id = :tenant_id AND id = :id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": terminal_id,
            "terminal_code": payload.terminal_code,
            "name": payload.name,
            "location_name": payload.location_name,
            "branch_code": payload.branch_code,
            "is_active": payload.is_active,
            "metadata": json.dumps(payload.metadata),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_docflow.pos_terminals WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": terminal_id},
    ).mappings().first()
    return _map_row_to_model(row, PosTerminalOut)


@router.delete("/pos/terminals/{terminal_id}", status_code=204)
async def delete_pos_terminal(
    terminal_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    updated = db.execute(
        text(
            """
            UPDATE domain_docflow.pos_terminals
            SET is_active = FALSE, unregistered_at = NOW(), updated_at = NOW()
            WHERE tenant_id = :tenant_id AND id = :id
            """
        ),
        {"tenant_id": tenant_id, "id": terminal_id},
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Terminal not found")
    db.commit()
    return None


@router.get("/pos/tse-devices", response_model=list[PosTseDeviceOut])
async def list_tse_devices(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text(
            """
            SELECT *
            FROM domain_docflow.pos_tse_devices
            WHERE tenant_id = :tenant_id
            ORDER BY created_at DESC
            """
        ),
        {"tenant_id": tenant_id},
    ).mappings().all()
    return [_map_row_to_model(row, PosTseDeviceOut) for row in rows]


@router.post("/pos/tse-devices", response_model=PosTseDeviceOut, status_code=201)
async def create_tse_device(
    payload: PosTseDeviceIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    terminal_exists = db.execute(
        text("SELECT id FROM domain_docflow.pos_terminals WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": payload.terminal_id},
    ).first()
    if not terminal_exists:
        raise HTTPException(status_code=400, detail="terminal_id does not exist")
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_docflow.pos_tse_devices
            (id, tenant_id, terminal_id, serial_number, provider, api_endpoint, certificate_fingerprint, status,
             activation_date, deactivation_date, last_heartbeat_at, settings, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :terminal_id, :serial_number, :provider, :api_endpoint, :certificate_fingerprint, :status,
             :activation_date, :deactivation_date, :last_heartbeat_at, CAST(:settings AS jsonb), NOW(), NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "terminal_id": payload.terminal_id,
            "serial_number": payload.serial_number,
            "provider": payload.provider,
            "api_endpoint": payload.api_endpoint,
            "certificate_fingerprint": payload.certificate_fingerprint,
            "status": payload.status,
            "activation_date": payload.activation_date,
            "deactivation_date": payload.deactivation_date,
            "last_heartbeat_at": payload.last_heartbeat_at,
            "settings": json.dumps(payload.settings),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_docflow.pos_tse_devices WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _map_row_to_model(row, PosTseDeviceOut)


@router.put("/pos/tse-devices/{device_id}", response_model=PosTseDeviceOut)
async def update_tse_device(
    device_id: str,
    payload: PosTseDeviceIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    db.execute(
        text(
            """
            UPDATE domain_docflow.pos_tse_devices
            SET terminal_id = :terminal_id,
                serial_number = :serial_number,
                provider = :provider,
                api_endpoint = :api_endpoint,
                certificate_fingerprint = :certificate_fingerprint,
                status = :status,
                activation_date = :activation_date,
                deactivation_date = :deactivation_date,
                last_heartbeat_at = :last_heartbeat_at,
                settings = CAST(:settings AS jsonb),
                updated_at = NOW()
            WHERE tenant_id = :tenant_id AND id = :id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": device_id,
            "terminal_id": payload.terminal_id,
            "serial_number": payload.serial_number,
            "provider": payload.provider,
            "api_endpoint": payload.api_endpoint,
            "certificate_fingerprint": payload.certificate_fingerprint,
            "status": payload.status,
            "activation_date": payload.activation_date,
            "deactivation_date": payload.deactivation_date,
            "last_heartbeat_at": payload.last_heartbeat_at,
            "settings": json.dumps(payload.settings),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_docflow.pos_tse_devices WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": device_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="TSE device not found")
    return _map_row_to_model(row, PosTseDeviceOut)


@router.get("/pos/notices", response_model=list[PosNoticeOut])
async def list_pos_notices(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text(
            """
            SELECT *
            FROM domain_docflow.pos_regulatory_notices
            WHERE tenant_id = :tenant_id
            ORDER BY effective_date DESC, created_at DESC
            """
        ),
        {"tenant_id": tenant_id},
    ).mappings().all()
    return [_map_row_to_model(row, PosNoticeOut) for row in rows]


@router.post("/pos/notices", response_model=PosNoticeOut, status_code=201)
async def create_pos_notice(
    payload: PosNoticeIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_docflow.pos_regulatory_notices
            (id, tenant_id, terminal_id, tse_device_id, notice_type, notice_status, effective_date, submitted_at, reference_number, payload, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :terminal_id, :tse_device_id, :notice_type, :notice_status, :effective_date, :submitted_at, :reference_number, CAST(:payload AS jsonb), NOW(), NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "terminal_id": payload.terminal_id,
            "tse_device_id": payload.tse_device_id,
            "notice_type": payload.notice_type,
            "notice_status": payload.notice_status,
            "effective_date": payload.effective_date,
            "submitted_at": payload.submitted_at,
            "reference_number": payload.reference_number,
            "payload": json.dumps(payload.payload),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_docflow.pos_regulatory_notices WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _map_row_to_model(row, PosNoticeOut)


@router.post("/pos/dsfinvk-exports", response_model=DsfinvkExportOut, status_code=201)
async def run_dsfinvk_export(
    payload: DsfinvkExportRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    export_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_docflow.dsfinvk_exports
            (id, tenant_id, period_from, period_to, status, generated_by, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :period_from, :period_to, 'running', :generated_by, NOW(), NOW())
            """
        ),
        {
            "id": export_id,
            "tenant_id": tenant_id,
            "period_from": payload.period_from,
            "period_to": payload.period_to,
            "generated_by": payload.generated_by,
        },
    )

    try:
        rows = db.execute(
            text(
                """
                SELECT
                    h.id AS header_id,
                    h.doc_type,
                    h.doc_number,
                    h.document_date,
                    h.total_net,
                    h.total_tax,
                    h.total_gross,
                    p.terminal_id,
                    p.cash_register_id,
                    p.transaction_type,
                    p.tse_transaction_id,
                    p.tse_signature,
                    p.tse_signature_counter,
                    p.transaction_started_at,
                    p.transaction_ended_at,
                    p.receipt_issued_at,
                    p.payment_breakdown
                FROM domain_docflow.document_headers h
                JOIN domain_docflow.pos_receipt_compliance p
                  ON p.header_id = h.id AND p.tenant_id = h.tenant_id
                WHERE h.tenant_id = :tenant_id
                  AND h.document_date::date >= :period_from
                  AND h.document_date::date <= :period_to
                ORDER BY h.document_date ASC, h.doc_number ASC
                """
            ),
            {"tenant_id": tenant_id, "period_from": payload.period_from, "period_to": payload.period_to},
        ).mappings().all()

        export_dir = Path("data") / "exports" / "dsfinvk" / tenant_id
        export_dir.mkdir(parents=True, exist_ok=True)
        filename = f"dsfinvk_{payload.period_from.isoformat()}_{payload.period_to.isoformat()}_{export_id}.csv"
        file_path = export_dir / filename

        fieldnames = [
            "header_id",
            "doc_type",
            "doc_number",
            "document_date",
            "terminal_id",
            "cash_register_id",
            "transaction_type",
            "tse_transaction_id",
            "tse_signature_counter",
            "transaction_started_at",
            "transaction_ended_at",
            "receipt_issued_at",
            "total_net",
            "total_tax",
            "total_gross",
            "payment_breakdown_json",
        ]
        with file_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "header_id": row["header_id"],
                        "doc_type": row["doc_type"],
                        "doc_number": row["doc_number"],
                        "document_date": row["document_date"].isoformat() if row["document_date"] else "",
                        "terminal_id": row["terminal_id"],
                        "cash_register_id": row["cash_register_id"] or "",
                        "transaction_type": row["transaction_type"],
                        "tse_transaction_id": row["tse_transaction_id"],
                        "tse_signature_counter": row["tse_signature_counter"] or "",
                        "transaction_started_at": row["transaction_started_at"].isoformat() if row["transaction_started_at"] else "",
                        "transaction_ended_at": row["transaction_ended_at"].isoformat() if row["transaction_ended_at"] else "",
                        "receipt_issued_at": row["receipt_issued_at"].isoformat() if row["receipt_issued_at"] else "",
                        "total_net": row["total_net"],
                        "total_tax": row["total_tax"],
                        "total_gross": row["total_gross"],
                        "payment_breakdown_json": json.dumps(row["payment_breakdown"] or {}),
                    }
                )

        checksum = hashlib.sha256(file_path.read_bytes()).hexdigest()
        db.execute(
            text(
                """
                UPDATE domain_docflow.dsfinvk_exports
                SET status = 'completed',
                    file_path = :file_path,
                    checksum_sha256 = :checksum,
                    row_count = :row_count,
                    generated_at = NOW(),
                    updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {
                "id": export_id,
                "tenant_id": tenant_id,
                "file_path": str(file_path),
                "checksum": checksum,
                "row_count": len(rows),
            },
        )
        db.commit()
    except Exception as exc:
        db.execute(
            text(
                """
                UPDATE domain_docflow.dsfinvk_exports
                SET status = 'failed', error_message = :error_message, updated_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {"id": export_id, "tenant_id": tenant_id, "error_message": str(exc)},
        )
        db.commit()
        raise HTTPException(status_code=500, detail=f"DSFinV-K export failed: {exc}") from exc

    row = db.execute(
        text("SELECT * FROM domain_docflow.dsfinvk_exports WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": export_id, "tenant_id": tenant_id},
    ).mappings().first()
    return _map_row_to_model(row, DsfinvkExportOut)


@router.get("/pos/dsfinvk-exports", response_model=list[DsfinvkExportOut])
async def list_dsfinvk_exports(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text(
            """
            SELECT *
            FROM domain_docflow.dsfinvk_exports
            WHERE tenant_id = :tenant_id
            ORDER BY created_at DESC
            """
        ),
        {"tenant_id": tenant_id},
    ).mappings().all()
    return [_map_row_to_model(row, DsfinvkExportOut) for row in rows]


@router.get("/pos/dsfinvk-exports/{export_id}/download")
async def download_dsfinvk_export(
    export_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            """
            SELECT *
            FROM domain_docflow.dsfinvk_exports
            WHERE id = :id AND tenant_id = :tenant_id
            """
        ),
        {"id": export_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Export not found")
    if row["status"] != "completed":
        raise HTTPException(status_code=409, detail="Export not completed")
    if not row["file_path"]:
        raise HTTPException(status_code=404, detail="Export file missing")
    file_path = Path(str(row["file_path"]))
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found on disk")
    return FileResponse(path=file_path, filename=file_path.name, media_type="text/csv")
