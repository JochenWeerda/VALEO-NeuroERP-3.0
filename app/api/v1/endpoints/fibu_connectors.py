"""
FIBU Connectors API – einheitliches Framework für PAYROLL und VALEO Suite Anlagen (ASSET_LEDGER).
Profile CRUD, Import-Runs: Upload → Parse → Validate → Post → Cancel/Reverse.
"""

from __future__ import annotations

import json
from typing import List, Optional
from uuid import uuid4

from fastapi import Response, APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.connectors import workflow
from app.core.data_quality_enforcement import DQValidationException
from app.api.v1.schemas.fibu_connectors import (
    ConnectorProfile,
    ConnectorProfileCreate,
    ConnectorProfileUpdate,
    ConnectorRunSummary,
    ConnectorRunItem,
    ImportUploadResponse,
)

router = APIRouter(prefix="/connectors", tags=["finance", "fibu-connectors"])


def _user_from_request(request: Optional[Request]) -> Optional[str]:
    if not request:
        return None
    return request.headers.get("X-User-ID") or request.headers.get("X-User-Email")


# ---------- Profiles ----------

@router.get("/profiles", response_model=List[ConnectorProfile])
async def list_profiles(
    type: str = Query(..., pattern="^(PAYROLL|ASSET_LEDGER)$"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Profile pro Mandant und Connector-Typ."""
    rows = db.execute(
        text("""
            SELECT id, tenant_id, connector_type, name, is_default, settings, mapping, version, created_at, updated_at, created_by, updated_by
            FROM domain_erp.fibu_connector_profiles
            WHERE tenant_id = :tid AND connector_type = :ct
            ORDER BY is_default DESC, name
        """),
        {"tid": tenant_id, "ct": type},
    ).fetchall()
    return [
        ConnectorProfile(
            id=r[0],
            tenant_id=r[1],
            connector_type=r[2],
            name=r[3],
            is_default=r[4] is True,
            settings=r[5] or {},
            mapping=r[6] or {},
            version=r[7] or 1,
            created_at=r[8],
            updated_at=r[9],
            created_by=r[10],
            updated_by=r[11],
        )
        for r in rows
    ]


@router.post("/profiles", response_model=ConnectorProfile, status_code=201)
async def create_profile(
    payload: ConnectorProfileCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    profile_id = str(uuid4())
    db.execute(
        text("""
            INSERT INTO domain_erp.fibu_connector_profiles
            (id, tenant_id, connector_type, name, is_default, settings, mapping, version, created_at, updated_at)
            VALUES (:id, :tenant_id, :connector_type, :name, :is_default, :settings::jsonb, :mapping::jsonb, 1, NOW(), NOW())
        """),
        {
            "id": profile_id,
            "tenant_id": tenant_id,
            "connector_type": payload.connector_type,
            "name": payload.name,
            "is_default": payload.is_default,
            "settings": json.dumps(payload.settings),
            "mapping": json.dumps(payload.mapping),
        },
    )
    if payload.is_default:
        db.execute(
            text("""
                UPDATE domain_erp.fibu_connector_profiles SET is_default = false
                WHERE tenant_id = :tid AND connector_type = :ct AND id != :id
            """),
            {"tid": tenant_id, "ct": payload.connector_type, "id": profile_id},
        )
    db.commit()
    row = db.execute(
        text("SELECT id, tenant_id, connector_type, name, is_default, settings, mapping, version, created_at, updated_at, created_by, updated_by FROM domain_erp.fibu_connector_profiles WHERE id = :id"),
        {"id": profile_id},
    ).fetchone()
    return ConnectorProfile(
        id=row[0], tenant_id=row[1], connector_type=row[2], name=row[3], is_default=row[4] is True,
        settings=row[5] or {}, mapping=row[6] or {}, version=row[7] or 1,
        created_at=row[8], updated_at=row[9], created_by=row[10], updated_by=row[11],
    )


@router.get("/profiles/{profile_id}", response_model=ConnectorProfile)
async def get_profile(
    profile_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT id, tenant_id, connector_type, name, is_default, settings, mapping, version, created_at, updated_at, created_by, updated_by
            FROM domain_erp.fibu_connector_profiles WHERE id = :id AND tenant_id = :tid
        """),
        {"id": profile_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Profil nicht gefunden")
    return ConnectorProfile(
        id=row[0], tenant_id=row[1], connector_type=row[2], name=row[3], is_default=row[4] is True,
        settings=row[5] or {}, mapping=row[6] or {}, version=row[7] or 1,
        created_at=row[8], updated_at=row[9], created_by=row[10], updated_by=row[11],
    )


@router.put("/profiles/{profile_id}", response_model=ConnectorProfile)
async def update_profile(
  profile_id: str,
  payload: ConnectorProfileUpdate,
  tenant_id: str = Depends(get_tenant_id),
  db: Session = Depends(get_db),
):
    row = db.execute(
        text("SELECT id, version FROM domain_erp.fibu_connector_profiles WHERE id = :id AND tenant_id = :tid"),
        {"id": profile_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Profil nicht gefunden")
    current_version = row[1] or 1
    if payload.version is not None and payload.version != current_version:
        raise HTTPException(status_code=409, detail="Profil wurde zwischenzeitlich geändert (Version)")
    updates = ["updated_at = NOW()", "version = :version"]
    params: dict = {"id": profile_id, "tenant_id": tenant_id, "version": current_version + 1}
    if payload.name is not None:
        updates.append("name = :name")
        params["name"] = payload.name
    if payload.is_default is not None:
        updates.append("is_default = :is_default")
        params["is_default"] = payload.is_default
    if payload.settings is not None:
        updates.append("settings = :settings::jsonb")
        params["settings"] = json.dumps(payload.settings)
    if payload.mapping is not None:
        updates.append("mapping = :mapping::jsonb")
        params["mapping"] = json.dumps(payload.mapping)
    db.execute(text(f"UPDATE domain_erp.fibu_connector_profiles SET {', '.join(updates)} WHERE id = :id AND tenant_id = :tenant_id"), params)
    if payload.is_default is True:
        prof = db.execute(text("SELECT connector_type FROM domain_erp.fibu_connector_profiles WHERE id = :id"), {"id": profile_id}).fetchone()
        if prof:
            db.execute(
                text("UPDATE domain_erp.fibu_connector_profiles SET is_default = false WHERE tenant_id = :tid AND connector_type = :ct AND id != :id"),
                {"tid": tenant_id, "ct": prof[0], "id": profile_id},
            )
    db.commit()
    return await get_profile(profile_id, tenant_id, db)


@router.delete("/profiles/{profile_id}", status_code=204, response_class=Response)
async def delete_profile(
  profile_id: str,
  tenant_id: str = Depends(get_tenant_id),
  db: Session = Depends(get_db),
):
    ref = db.execute(
        text("SELECT 1 FROM domain_erp.fibu_connector_runs WHERE profile_id = :id LIMIT 1"),
        {"id": profile_id},
    ).fetchone()
    if ref:
        raise HTTPException(status_code=400, detail="Profil wird noch von Läufen referenziert; löschen nicht möglich.")
    r = db.execute(
        text("DELETE FROM domain_erp.fibu_connector_profiles WHERE id = :id AND tenant_id = :tid"),
        {"id": profile_id, "tid": tenant_id},
    )
    db.commit()
    if r.rowcount == 0:
        raise HTTPException(status_code=404, detail="Profil nicht gefunden")


# ---------- Imports (Runs) ----------

@router.post("/{connector_type}/imports", response_model=ImportUploadResponse, status_code=201)
async def create_import_run(
    connector_type: str,
    request: Request,
    file: UploadFile = File(...),
    profile_id: Optional[str] = Query(None),
    idempotency_key: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    if connector_type not in ("PAYROLL", "ASSET_LEDGER"):
        raise HTTPException(status_code=400, detail="connector_type muss PAYROLL oder ASSET_LEDGER sein")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Datei ist leer")
    created_by = _user_from_request(request)
    run_id = workflow.create_run(db, tenant_id, connector_type, profile_id, idempotency_key, created_by)
    storage_key = f"fibu/connectors/{connector_type.lower()}/{run_id}"
    workflow.set_run_artifact(db, run_id, tenant_id, content, file.filename, storage_key)
    try:
        workflow.parse_run(db, run_id, tenant_id, content)
    except DQValidationException as exc:
        raise HTTPException(status_code=422, detail=exc.detail) from exc
    return ImportUploadResponse(run_id=run_id, status="PARSED", message="Upload und Parse erfolgreich.")


@router.get("/imports/{run_id}", response_model=ConnectorRunSummary)
async def get_import_run(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("""
            SELECT id, tenant_id, connector_type, direction, profile_id, idempotency_key, status,
                   source_artifact_storage_key, source_artifact_sha256, source_artifact_file_name,
                   protocol_artifact_storage_key, protocol_artifact_sha256, counts, totals, error_summary,
                   started_at, finished_at, created_at, created_by
            FROM domain_erp.fibu_connector_runs WHERE id = :id AND tenant_id = :tid
        """),
        {"id": run_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Import-Lauf nicht gefunden")
    return ConnectorRunSummary(
        id=row[0], tenant_id=row[1], connector_type=row[2], direction=row[3] or "IMPORT",
        profile_id=row[4], idempotency_key=row[5], status=row[6],
        counts=row[11], totals=row[12], error_summary=row[13],
        started_at=row[14], finished_at=row[15], created_at=row[16], created_by=row[17],
    )


@router.get("/imports/{run_id}/items", response_model=List[ConnectorRunItem])
async def list_run_items(
    run_id: str,
    only_errors: bool = Query(False),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    ex = db.execute(
        text("SELECT 1 FROM domain_erp.fibu_connector_runs WHERE id = :id AND tenant_id = :tid"),
        {"id": run_id, "tid": tenant_id},
    ).fetchone()
    if not ex:
        raise HTTPException(status_code=404, detail="Import-Lauf nicht gefunden")
    q = """
        SELECT id, run_id, line_no, item_type, payload, validation_errors, posted_entity_id, status
        FROM domain_erp.fibu_connector_run_items WHERE run_id = :run_id
    """
    params: dict = {"run_id": run_id}
    if only_errors:
        q += " AND status = 'ERROR'"
    q += " ORDER BY line_no LIMIT :limit"
    params["limit"] = limit
    rows = db.execute(text(q), params).fetchall()
    return [
        ConnectorRunItem(
            id=r[0], run_id=r[1], line_no=r[2], item_type=r[3] or "JOURNAL_ENTRY_LINE",
            payload=r[4], validation_errors=r[5], posted_entity_id=r[6], status=r[7],
        )
        for r in rows
    ]


@router.post("/imports/{run_id}/validate", response_model=ConnectorRunSummary)
async def validate_import_run(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        workflow.validate_run(db, run_id, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return await get_import_run(run_id, tenant_id, db)


@router.post("/imports/{run_id}/post", response_model=ConnectorRunSummary)
async def post_import_run(
    run_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        workflow.post_run(db, run_id, tenant_id, request=request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return await get_import_run(run_id, tenant_id, db)


@router.post("/imports/{run_id}/cancel", response_model=ConnectorRunSummary)
async def cancel_import_run(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        workflow.cancel_run(db, run_id, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return await get_import_run(run_id, tenant_id, db)


@router.post("/imports/{run_id}/reverse", response_model=ConnectorRunSummary)
async def reverse_import_run(
    run_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        workflow.reverse_run(db, run_id, tenant_id, request=request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return await get_import_run(run_id, tenant_id, db)
