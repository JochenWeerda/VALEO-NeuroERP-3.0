"""Admin device mapping and output/form settings."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter()


class AdminDeviceIn(BaseModel):
    device_type: str = Field(..., pattern="^(printer|scanner)$")
    name: str = Field(..., min_length=1, max_length=120)
    vendor: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    station_code: str | None = Field(default=None, max_length=80)
    connection_uri: str | None = Field(default=None, max_length=255)
    capabilities: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class AdminDeviceOut(AdminDeviceIn):
    id: str
    created_at: datetime
    updated_at: datetime


class AdminDeviceMappingIn(BaseModel):
    device_id: str
    document_type: str = Field(..., min_length=1, max_length=60)
    process_code: str = Field(..., min_length=1, max_length=60)
    output_format: str = Field(default="pdf", pattern="^(pdf|zpl|epl|raw)$")
    copies: int = Field(default=1, ge=1, le=20)
    is_default: bool = False
    settings: dict[str, Any] = Field(default_factory=dict)


class AdminDeviceMappingOut(AdminDeviceMappingIn):
    id: str
    created_at: datetime
    updated_at: datetime


class AdminOutputTemplateCreate(BaseModel):
    template_code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=120)
    document_type: str = Field(..., min_length=1, max_length=60)
    output_format: str = Field(default="pdf", pattern="^(pdf|zpl|epl|html|txt)$")
    language: str | None = Field(default=None, max_length=10)
    content: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    change_note: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class AdminOutputTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    language: str | None = Field(default=None, max_length=10)
    content: str | None = None
    metadata: dict[str, Any] | None = None
    change_note: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class AdminOutputTemplateOut(BaseModel):
    id: str
    template_code: str
    name: str
    document_type: str
    output_format: str
    language: str | None
    is_active: bool
    current_version: int
    created_at: datetime
    updated_at: datetime


class AdminOutputTemplateVersionOut(BaseModel):
    id: str
    template_id: str
    version_no: int
    content: str
    metadata: dict[str, Any]
    change_note: str | None
    created_by: str | None
    created_at: datetime


class AdminOutputProfileIn(BaseModel):
    profile_code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=120)
    document_type: str = Field(..., min_length=1, max_length=60)
    process_code: str = Field(..., min_length=1, max_length=60)
    template_id: str | None = None
    device_id: str | None = None
    output_channel: str = Field(default="print", pattern="^(print|email|dms|pdf)$")
    archive_mode: str = Field(default="dms", pattern="^(none|dms|worm)$")
    archive_retention_days: int | None = Field(default=None, ge=0)
    is_active: bool = True
    settings: dict[str, Any] = Field(default_factory=dict)


class AdminOutputProfileOut(AdminOutputProfileIn):
    id: str
    created_at: datetime
    updated_at: datetime


def _row_to_model(row: Any, model_cls: type[BaseModel]) -> BaseModel:
    payload = dict(row)
    for key, value in list(payload.items()):
        if isinstance(value, UUID):
            payload[key] = str(value)
    for key in ("capabilities", "settings", "metadata"):
        if key in payload and payload[key] is None:
            payload[key] = {}
    return model_cls(**payload)


@router.get("/devices", response_model=list[AdminDeviceOut], summary="Devices auflisten")
async def list_devices(
    device_type: Optional[str] = Query(default=None),
    include_inactive: bool = Query(default=False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if device_type:
        where.append("device_type = :device_type")
        params["device_type"] = device_type
    if not include_inactive:
        where.append("is_active = TRUE")
    rows = db.execute(
        text(
            f"""
            SELECT *
            FROM domain_shared.admin_devices
            WHERE {' AND '.join(where)}
            ORDER BY device_type ASC, name ASC
            """
        ),
        params,
    ).mappings().all()
    return [_row_to_model(row, AdminDeviceOut) for row in rows]


@router.post("/devices", response_model=AdminDeviceOut, status_code=201, summary="Device anlegen")
async def create_device(
    payload: AdminDeviceIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.admin_devices
              (id, tenant_id, device_type, name, vendor, model, station_code, connection_uri, capabilities, is_active, created_at, updated_at)
            VALUES
              (:id, :tenant_id, :device_type, :name, :vendor, :model, :station_code, :connection_uri, CAST(:capabilities AS jsonb), :is_active, NOW(), NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "device_type": payload.device_type,
            "name": payload.name,
            "vendor": payload.vendor,
            "model": payload.model,
            "station_code": payload.station_code,
            "connection_uri": payload.connection_uri,
            "capabilities": json.dumps(payload.capabilities),
            "is_active": payload.is_active,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_devices WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _row_to_model(row, AdminDeviceOut)


@router.put("/devices/{device_id}", response_model=AdminDeviceOut, summary="Device aktualisieren")
async def update_device(
    device_id: str,
    payload: AdminDeviceIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_devices
            SET device_type = :device_type,
                name = :name,
                vendor = :vendor,
                model = :model,
                station_code = :station_code,
                connection_uri = :connection_uri,
                capabilities = CAST(:capabilities AS jsonb),
                is_active = :is_active,
                updated_at = NOW()
            WHERE tenant_id = :tenant_id AND id = :id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": device_id,
            "device_type": payload.device_type,
            "name": payload.name,
            "vendor": payload.vendor,
            "model": payload.model,
            "station_code": payload.station_code,
            "connection_uri": payload.connection_uri,
            "capabilities": json.dumps(payload.capabilities),
            "is_active": payload.is_active,
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Device not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_devices WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": device_id},
    ).mappings().first()
    return _row_to_model(row, AdminDeviceOut)


@router.delete("/devices/{device_id}", status_code=204, response_class=Response, response_model=None, summary="Device löschen")
async def delete_device(
    device_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_devices WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": device_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Device not found")
    db.commit()
    return None


@router.get("/device-mappings", response_model=list[AdminDeviceMappingOut], summary="Device mappings auflisten")
async def list_device_mappings(
    document_type: Optional[str] = Query(default=None),
    process_code: Optional[str] = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if document_type:
        where.append("document_type = :document_type")
        params["document_type"] = document_type
    if process_code:
        where.append("process_code = :process_code")
        params["process_code"] = process_code
    rows = db.execute(
        text(
            f"""
            SELECT *
            FROM domain_shared.admin_device_mappings
            WHERE {' AND '.join(where)}
            ORDER BY document_type ASC, process_code ASC, created_at DESC
            """
        ),
        params,
    ).mappings().all()
    return [_row_to_model(row, AdminDeviceMappingOut) for row in rows]


@router.post("/device-mappings", response_model=AdminDeviceMappingOut, status_code=201, summary="Device mapping anlegen")
async def create_device_mapping(
    payload: AdminDeviceMappingIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    device_exists = db.execute(
        text("SELECT id FROM domain_shared.admin_devices WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": payload.device_id},
    ).first()
    if not device_exists:
        raise HTTPException(status_code=400, detail="device_id does not exist")

    if payload.is_default:
        db.execute(
            text(
                """
                UPDATE domain_shared.admin_device_mappings
                SET is_default = FALSE, updated_at = NOW()
                WHERE tenant_id = :tenant_id
                  AND document_type = :document_type
                  AND process_code = :process_code
                  AND output_format = :output_format
                """
            ),
            {
                "tenant_id": tenant_id,
                "document_type": payload.document_type,
                "process_code": payload.process_code,
                "output_format": payload.output_format,
            },
        )

    item_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_shared.admin_device_mappings
                  (id, tenant_id, device_id, document_type, process_code, output_format, copies, is_default, settings, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :device_id, :document_type, :process_code, :output_format, :copies, :is_default, CAST(:settings AS jsonb), NOW(), NOW())
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "device_id": payload.device_id,
                "document_type": payload.document_type,
                "process_code": payload.process_code,
                "output_format": payload.output_format,
                "copies": payload.copies,
                "is_default": payload.is_default,
                "settings": json.dumps(payload.settings),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Mapping conflict: {exc}") from exc
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_device_mappings WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _row_to_model(row, AdminDeviceMappingOut)


@router.put("/device-mappings/{mapping_id}", response_model=AdminDeviceMappingOut, summary="Device mapping aktualisieren")
async def update_device_mapping(
    mapping_id: str,
    payload: AdminDeviceMappingIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    current = db.execute(
        text("SELECT id FROM domain_shared.admin_device_mappings WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": mapping_id},
    ).first()
    if not current:
        raise HTTPException(status_code=404, detail="Device mapping not found")

    if payload.is_default:
        db.execute(
            text(
                """
                UPDATE domain_shared.admin_device_mappings
                SET is_default = FALSE, updated_at = NOW()
                WHERE tenant_id = :tenant_id
                  AND id <> :id
                  AND document_type = :document_type
                  AND process_code = :process_code
                  AND output_format = :output_format
                """
            ),
            {
                "tenant_id": tenant_id,
                "id": mapping_id,
                "document_type": payload.document_type,
                "process_code": payload.process_code,
                "output_format": payload.output_format,
            },
        )

    db.execute(
        text(
            """
            UPDATE domain_shared.admin_device_mappings
            SET device_id = :device_id,
                document_type = :document_type,
                process_code = :process_code,
                output_format = :output_format,
                copies = :copies,
                is_default = :is_default,
                settings = CAST(:settings AS jsonb),
                updated_at = NOW()
            WHERE tenant_id = :tenant_id AND id = :id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": mapping_id,
            "device_id": payload.device_id,
            "document_type": payload.document_type,
            "process_code": payload.process_code,
            "output_format": payload.output_format,
            "copies": payload.copies,
            "is_default": payload.is_default,
            "settings": json.dumps(payload.settings),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_device_mappings WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": mapping_id},
    ).mappings().first()
    return _row_to_model(row, AdminDeviceMappingOut)


@router.delete("/device-mappings/{mapping_id}", status_code=204, response_class=Response, response_model=None, summary="Device mapping löschen")
async def delete_device_mapping(
    mapping_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_device_mappings WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": mapping_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Device mapping not found")
    db.commit()
    return None


@router.get("/output-templates", response_model=list[AdminOutputTemplateOut], summary="Output templates auflisten")
async def list_output_templates(
    document_type: Optional[str] = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if document_type:
        where.append("document_type = :document_type")
        params["document_type"] = document_type
    rows = db.execute(
        text(
            f"""
            SELECT *
            FROM domain_shared.admin_output_templates
            WHERE {' AND '.join(where)}
            ORDER BY document_type ASC, template_code ASC
            """
        ),
        params,
    ).mappings().all()
    return [_row_to_model(row, AdminOutputTemplateOut) for row in rows]


@router.post("/output-templates", response_model=AdminOutputTemplateOut, status_code=201, summary="Output template anlegen")
async def create_output_template(
    payload: AdminOutputTemplateCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    template_id = str(uuid4())
    version_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_shared.admin_output_templates
                  (id, tenant_id, template_code, name, document_type, output_format, language, is_active, current_version, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :template_code, :name, :document_type, :output_format, :language, :is_active, 1, NOW(), NOW())
                """
            ),
            {
                "id": template_id,
                "tenant_id": tenant_id,
                "template_code": payload.template_code,
                "name": payload.name,
                "document_type": payload.document_type,
                "output_format": payload.output_format,
                "language": payload.language,
                "is_active": payload.is_active,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Template conflict: {exc}") from exc

    db.execute(
        text(
            """
            INSERT INTO domain_shared.admin_output_template_versions
              (id, tenant_id, template_id, version_no, content, metadata, change_note, created_at)
            VALUES
              (:id, :tenant_id, :template_id, 1, :content, CAST(:metadata AS jsonb), :change_note, NOW())
            """
        ),
        {
            "id": version_id,
            "tenant_id": tenant_id,
            "template_id": template_id,
            "content": payload.content,
            "metadata": json.dumps(payload.metadata),
            "change_note": payload.change_note,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_output_templates WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": template_id},
    ).mappings().first()
    return _row_to_model(row, AdminOutputTemplateOut)


@router.put("/output-templates/{template_id}", response_model=AdminOutputTemplateOut, summary="Output template aktualisieren")
async def update_output_template(
    template_id: str,
    payload: AdminOutputTemplateUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    current = db.execute(
        text("SELECT * FROM domain_shared.admin_output_templates WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": template_id},
    ).mappings().first()
    if not current:
        raise HTTPException(status_code=404, detail="Template not found")

    next_version = int(current["current_version"])
    if payload.content is not None:
        next_version += 1
        db.execute(
            text(
                """
                INSERT INTO domain_shared.admin_output_template_versions
                  (id, tenant_id, template_id, version_no, content, metadata, change_note, created_at)
                VALUES
                  (:id, :tenant_id, :template_id, :version_no, :content, CAST(:metadata AS jsonb), :change_note, NOW())
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "template_id": template_id,
                "version_no": next_version,
                "content": payload.content,
                "metadata": json.dumps(payload.metadata or {}),
                "change_note": payload.change_note,
            },
        )

    db.execute(
        text(
            """
            UPDATE domain_shared.admin_output_templates
            SET name = :name,
                language = :language,
                is_active = :is_active,
                current_version = :current_version,
                updated_at = NOW()
            WHERE tenant_id = :tenant_id AND id = :id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": template_id,
            "name": payload.name if payload.name is not None else current["name"],
            "language": payload.language if payload.language is not None else current["language"],
            "is_active": payload.is_active if payload.is_active is not None else current["is_active"],
            "current_version": next_version,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_output_templates WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": template_id},
    ).mappings().first()
    return _row_to_model(row, AdminOutputTemplateOut)


@router.get("/output-templates/{template_id}/versions", response_model=list[AdminOutputTemplateVersionOut], summary="Output template versions auflisten")
async def list_output_template_versions(
    template_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text(
            """
            SELECT id, template_id, version_no, content, metadata, change_note, created_by, created_at
            FROM domain_shared.admin_output_template_versions
            WHERE tenant_id = :tenant_id AND template_id = :template_id
            ORDER BY version_no DESC
            """
        ),
        {"tenant_id": tenant_id, "template_id": template_id},
    ).mappings().all()
    return [_row_to_model(row, AdminOutputTemplateVersionOut) for row in rows]


@router.delete("/output-templates/{template_id}", status_code=204, response_class=Response, response_model=None, summary="Output template löschen")
async def delete_output_template(
    template_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_output_templates
            SET is_active = FALSE, updated_at = NOW()
            WHERE tenant_id = :tenant_id AND id = :id
            """
        ),
        {"tenant_id": tenant_id, "id": template_id},
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Template not found")
    db.commit()
    return None


@router.get("/output-profiles", response_model=list[AdminOutputProfileOut], summary="Output profiles auflisten")
async def list_output_profiles(
    document_type: Optional[str] = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if document_type:
        where.append("document_type = :document_type")
        params["document_type"] = document_type
    rows = db.execute(
        text(
            f"""
            SELECT *
            FROM domain_shared.admin_output_profiles
            WHERE {' AND '.join(where)}
            ORDER BY document_type ASC, process_code ASC, profile_code ASC
            """
        ),
        params,
    ).mappings().all()
    return [_row_to_model(row, AdminOutputProfileOut) for row in rows]


@router.post("/output-profiles", response_model=AdminOutputProfileOut, status_code=201, summary="Output profile anlegen")
async def create_output_profile(
    payload: AdminOutputProfileIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_shared.admin_output_profiles
                  (id, tenant_id, profile_code, name, document_type, process_code, template_id, device_id, output_channel,
                   archive_mode, archive_retention_days, is_active, settings, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :profile_code, :name, :document_type, :process_code, :template_id, :device_id, :output_channel,
                   :archive_mode, :archive_retention_days, :is_active, CAST(:settings AS jsonb), NOW(), NOW())
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "profile_code": payload.profile_code,
                "name": payload.name,
                "document_type": payload.document_type,
                "process_code": payload.process_code,
                "template_id": payload.template_id,
                "device_id": payload.device_id,
                "output_channel": payload.output_channel,
                "archive_mode": payload.archive_mode,
                "archive_retention_days": payload.archive_retention_days,
                "is_active": payload.is_active,
                "settings": json.dumps(payload.settings),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Output profile conflict: {exc}") from exc
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_output_profiles WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _row_to_model(row, AdminOutputProfileOut)


@router.put("/output-profiles/{profile_id}", response_model=AdminOutputProfileOut, summary="Output profile aktualisieren")
async def update_output_profile(
    profile_id: str,
    payload: AdminOutputProfileIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_output_profiles
            SET profile_code = :profile_code,
                name = :name,
                document_type = :document_type,
                process_code = :process_code,
                template_id = :template_id,
                device_id = :device_id,
                output_channel = :output_channel,
                archive_mode = :archive_mode,
                archive_retention_days = :archive_retention_days,
                is_active = :is_active,
                settings = CAST(:settings AS jsonb),
                updated_at = NOW()
            WHERE tenant_id = :tenant_id AND id = :id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": profile_id,
            "profile_code": payload.profile_code,
            "name": payload.name,
            "document_type": payload.document_type,
            "process_code": payload.process_code,
            "template_id": payload.template_id,
            "device_id": payload.device_id,
            "output_channel": payload.output_channel,
            "archive_mode": payload.archive_mode,
            "archive_retention_days": payload.archive_retention_days,
            "is_active": payload.is_active,
            "settings": json.dumps(payload.settings),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Output profile not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_output_profiles WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": profile_id},
    ).mappings().first()
    return _row_to_model(row, AdminOutputProfileOut)


@router.delete("/output-profiles/{profile_id}", status_code=204, response_class=Response, response_model=None, summary="Output profile löschen")
async def delete_output_profile(
    profile_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_output_profiles WHERE tenant_id = :tenant_id AND id = :id"),
        {"tenant_id": tenant_id, "id": profile_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Output profile not found")
    db.commit()
    return None
