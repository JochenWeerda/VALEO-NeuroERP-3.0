"""User-scoped ScreenDefinition overlays (UIX-071)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_user_id_from_request
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/ux/overlays", tags=["ux-overlays"])

OVERLAYABLE_KEYS = {"tables", "density", "tileOrder", "collapsedSections", "schemaVersion"}
OVERLAYABLE_TABLE_KEYS = {"visibleColumns", "columnWidths", "activeVariant", "customVariants"}
VALID_DENSITIES = {"comfortable", "compact", "expertDense"}


class OverlayPut(BaseModel):
    schema_version: int = Field(ge=1)
    overlay: dict[str, Any] = Field(default_factory=dict)

    @field_validator("overlay")
    @classmethod
    def overlay_must_be_object(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("overlay must be an object")
        return value


class OverlayOut(BaseModel):
    screen_id: str
    schema_version: int | None = None
    overlay: dict[str, Any]
    updated_at: datetime | None = None


def _overlay_user_id(request: Request) -> str:
    header_user = (request.headers.get("X-User-ID") or "").strip()
    if header_user:
        return header_user[:64]
    return get_user_id_from_request(request)[:64]


def _validate_string_list(value: Any, path: str, violations: list[str]) -> list[str] | None:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        violations.append(path)
        return None
    return [item.strip() for item in value]


def _validate_overlay(raw: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    violations: list[str] = []
    clean: dict[str, Any] = {}

    for key, value in raw.items():
        if key not in OVERLAYABLE_KEYS:
            violations.append(key)
            continue
        if key == "schemaVersion":
            if isinstance(value, int) and value >= 1:
                clean[key] = value
            else:
                violations.append(key)
        elif key == "density":
            if value in VALID_DENSITIES:
                clean[key] = value
            else:
                violations.append(key)
        elif key == "tileOrder":
            validated = _validate_string_list(value, key, violations)
            if validated is not None:
                clean[key] = validated
        elif key == "collapsedSections":
            validated = _validate_string_list(value, key, violations)
            if validated is not None:
                clean[key] = validated
        elif key == "tables":
            if not isinstance(value, dict):
                violations.append(key)
                continue
            clean_tables: dict[str, Any] = {}
            for table_key, table_overlay in value.items():
                if not isinstance(table_key, str) or not table_key.strip() or not isinstance(table_overlay, dict):
                    violations.append(f"tables.{table_key}")
                    continue
                clean_table: dict[str, Any] = {}
                for table_prop, table_value in table_overlay.items():
                    path = f"tables.{table_key}.{table_prop}"
                    if table_prop not in OVERLAYABLE_TABLE_KEYS:
                        violations.append(path)
                        continue
                    if table_prop == "visibleColumns":
                        validated = _validate_string_list(table_value, path, violations)
                        if validated is not None:
                            clean_table[table_prop] = validated
                    elif table_prop == "columnWidths":
                        if not isinstance(table_value, dict):
                            violations.append(path)
                            continue
                        widths: dict[str, int] = {}
                        for col_key, width in table_value.items():
                            if isinstance(col_key, str) and isinstance(width, int) and 40 <= width <= 640:
                                widths[col_key] = width
                            else:
                                violations.append(f"{path}.{col_key}")
                        if widths:
                            clean_table[table_prop] = widths
                    elif table_prop == "activeVariant":
                        if isinstance(table_value, str) and table_value.strip():
                            clean_table[table_prop] = table_value.strip()
                        else:
                            violations.append(path)
                    elif table_prop == "customVariants":
                        if not isinstance(table_value, list):
                            violations.append(path)
                            continue
                        variants: list[dict[str, Any]] = []
                        for index, variant in enumerate(table_value):
                            variant_path = f"{path}.{index}"
                            if not isinstance(variant, dict):
                                violations.append(variant_path)
                                continue
                            variant_key = variant.get("key")
                            label = variant.get("label")
                            filters = variant.get("filters")
                            if not isinstance(variant_key, str) or not variant_key.strip() or not isinstance(label, str) or not label.strip():
                                violations.append(variant_path)
                                continue
                            if filters is not None and not isinstance(filters, dict):
                                violations.append(f"{variant_path}.filters")
                                continue
                            clean_variant = {
                                "key": variant_key.strip(),
                                "label": label.strip(),
                            }
                            if isinstance(filters, dict):
                                clean_variant["filters"] = filters
                            variants.append(clean_variant)
                        if variants:
                            clean_table[table_prop] = variants
                if clean_table:
                    clean_tables[table_key.strip()] = clean_table
            if clean_tables:
                clean[key] = clean_tables

    return clean, violations


@router.get("/{screen_id:path}", response_model=OverlayOut, summary="User overlay fuer Maske lesen")
async def get_overlay(
    screen_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> OverlayOut:
    user_id = _overlay_user_id(request)
    result = db.execute(
        text(
            """
            SELECT screen_id, schema_version, overlay, updated_at
              FROM domain_shared.user_screen_overlays
             WHERE tenant_id = :tenant_id
               AND user_id = :user_id
               AND screen_id = :screen_id
            """
        ),
        {"tenant_id": tenant_id, "user_id": user_id, "screen_id": screen_id},
    )
    row = result.mappings().first()
    if row is None:
        return OverlayOut(screen_id=screen_id, overlay={})
    overlay = row["overlay"]
    if isinstance(overlay, str):
        overlay = json.loads(overlay)
    return OverlayOut(
        screen_id=str(row["screen_id"]),
        schema_version=row["schema_version"],
        overlay=overlay if isinstance(overlay, dict) else {},
        updated_at=row["updated_at"],
    )


@router.put("/{screen_id:path}", response_model=OverlayOut, summary="User overlay fuer Maske speichern")
async def put_overlay(
    screen_id: str,
    payload: OverlayPut,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> OverlayOut:
    clean_overlay, violations = _validate_overlay(payload.overlay)
    if violations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Overlay contains non-overlayable or invalid fields", "violations": violations},
        )
    user_id = _overlay_user_id(request)
    result = db.execute(
        text(
            """
            INSERT INTO domain_shared.user_screen_overlays
                (tenant_id, user_id, screen_id, schema_version, overlay, updated_at)
            VALUES
                (:tenant_id, :user_id, :screen_id, :schema_version, CAST(:overlay AS jsonb), now())
            ON CONFLICT (tenant_id, user_id, screen_id)
            DO UPDATE SET schema_version = EXCLUDED.schema_version,
                          overlay = EXCLUDED.overlay,
                          updated_at = now()
            RETURNING screen_id, schema_version, overlay, updated_at
            """
        ),
        {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "screen_id": screen_id,
            "schema_version": payload.schema_version,
            "overlay": json.dumps(clean_overlay),
        },
    )
    db.commit()
    row = result.mappings().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Overlay upsert failed")
    overlay = row["overlay"]
    if isinstance(overlay, str):
        overlay = json.loads(overlay)
    return OverlayOut(
        screen_id=str(row["screen_id"]),
        schema_version=row["schema_version"],
        overlay=overlay if isinstance(overlay, dict) else {},
        updated_at=row["updated_at"],
    )


@router.delete("/{screen_id:path}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, summary="User overlay zuruecksetzen")
async def delete_overlay(
    screen_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Response:
    user_id = _overlay_user_id(request)
    db.execute(
        text(
            """
            DELETE FROM domain_shared.user_screen_overlays
             WHERE tenant_id = :tenant_id
               AND user_id = :user_id
               AND screen_id = :screen_id
            """
        ),
        {"tenant_id": tenant_id, "user_id": user_id, "screen_id": screen_id},
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
