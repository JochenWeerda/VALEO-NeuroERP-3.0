"""UIX-082 ESG charge footprint API."""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services.esg_footprint_service import EsgInput, compute_footprint, current_factor_version

router = APIRouter(prefix="/esg", tags=["esg", "footprint"])


class FootprintComponentOut(BaseModel):
    key: str
    input: dict[str, float]
    factor_version: str
    co2e_kg: float
    source_ref: str
    source: str


class FootprintOut(BaseModel):
    charge_id: str
    tenant_id: str
    factor_version: str
    co2e_kg: float
    components: list[FootprintComponentOut] = Field(default_factory=list)
    inputs: list[dict[str, Any]] = Field(default_factory=list)
    persisted: bool


def _json_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return [item for item in parsed if isinstance(item, dict)] if isinstance(parsed, list) else []
        except ValueError:
            return []
    return []


def _row_out(row: dict[str, Any], *, persisted: bool) -> FootprintOut:
    return FootprintOut(
        charge_id=str(row["charge_id"]),
        tenant_id=str(row["tenant_id"]),
        factor_version=str(row["factor_version"]),
        co2e_kg=float(row["co2e_kg"] or 0),
        components=_json_list(row.get("components")),
        inputs=_json_list(row.get("inputs")),
        persisted=persisted,
    )


def _query_inputs(
    charge_id: str,
    *,
    drying_kwh: float | None,
    electricity_kwh: float | None,
    transport_tkm: float | None,
) -> list[EsgInput]:
    inputs: list[EsgInput] = []
    if drying_kwh is not None:
        inputs.append(EsgInput("trocknung_gas_kwh", drying_kwh, f"trocknung:{charge_id}"))
    if electricity_kwh is not None:
        inputs.append(EsgInput("strom_kwh", electricity_kwh, f"strom:{charge_id}"))
    if transport_tkm is not None:
        inputs.append(EsgInput("transport_tkm", transport_tkm, f"transport:{charge_id}"))
    return inputs


def _load_existing(db: Session, tenant_id: str, charge_id: str, factor_version: str) -> dict[str, Any] | None:
    row = db.execute(text("""
        SELECT tenant_id, charge_id, factor_version, co2e_kg, components, inputs
        FROM domain_agrar.esg_charge_footprint
        WHERE tenant_id = :tenant_id
          AND charge_id = :charge_id
          AND factor_version = :factor_version
    """), {
        "tenant_id": tenant_id,
        "charge_id": charge_id,
        "factor_version": factor_version,
    }).mappings().first()
    return dict(row) if row else None


def _upsert_footprint(db: Session, tenant_id: str, charge_id: str, inputs: list[EsgInput]) -> dict[str, Any]:
    footprint = compute_footprint(charge_id, inputs, tenant_id=tenant_id)
    input_payload = [
        {"factor_key": item.factor_key, "value": item.value, "source_ref": item.source_ref}
        for item in sorted(inputs, key=lambda item: item.factor_key)
    ]
    row = db.execute(text("""
        INSERT INTO domain_agrar.esg_charge_footprint
          (id, tenant_id, charge_id, factor_version, co2e_kg, components, inputs, updated_at)
        VALUES (:id, :tenant_id, :charge_id, :factor_version, :co2e_kg,
                CAST(:components AS jsonb), CAST(:inputs AS jsonb), now())
        ON CONFLICT (tenant_id, charge_id, factor_version) DO UPDATE
          SET co2e_kg = EXCLUDED.co2e_kg,
              components = EXCLUDED.components,
              inputs = EXCLUDED.inputs,
              updated_at = now()
        RETURNING tenant_id, charge_id, factor_version, co2e_kg, components, inputs
    """), {
        "id": uuid7(),
        "tenant_id": tenant_id,
        "charge_id": charge_id,
        "factor_version": footprint.factor_version,
        "co2e_kg": footprint.co2e_kg,
        "components": json.dumps(footprint.to_dict()["components"], ensure_ascii=False),
        "inputs": json.dumps(input_payload, ensure_ascii=False),
    }).mappings().first()
    db.commit()
    return dict(row)


@router.get("/charges/{charge_id}/footprint", response_model=FootprintOut, summary="ESG-Footprint je Charge")
async def get_charge_footprint(
    charge_id: str,
    recompute: bool = Query(default=False),
    drying_kwh: float | None = Query(default=None, ge=0),
    electricity_kwh: float | None = Query(default=None, ge=0),
    transport_tkm: float | None = Query(default=None, ge=0),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> FootprintOut:
    version = current_factor_version()
    inputs = _query_inputs(
        charge_id,
        drying_kwh=drying_kwh,
        electricity_kwh=electricity_kwh,
        transport_tkm=transport_tkm,
    )
    if not recompute and not inputs:
        existing = _load_existing(db, tenant_id, charge_id, version)
        if existing:
            return _row_out(existing, persisted=True)
    row = _upsert_footprint(db, tenant_id, charge_id, inputs)
    return _row_out(row, persisted=True)
