"""
Config Service API.
Connectors, Reporting Units, Schedules for Meldewesen/ERP-Belegkette.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import Response, APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter()


# ── Connectors ──────────────────────────────────────────────────────────────────

class ConnectorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    connector_key: str
    connector_type: str
    display_name: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConnectorCreateIn(BaseModel):
    connector_key: str = Field(..., min_length=1, max_length=80)
    connector_type: str = Field(..., min_length=1, max_length=40)  # api, oauth2, cert, basic, file-drop, https, sftp, email, provider
    display_name: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool = True


class ConnectorUpdateIn(BaseModel):
    display_name: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: Optional[bool] = None


@router.get("/connectors", response_model=list[ConnectorOut], summary="Connectors auflisten")
async def list_connectors(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List connectors (API-Keys, OAuth, Zertifikate)."""
    from sqlalchemy import text
    rows = db.execute(
        text(
            "SELECT id, tenant_id, connector_key, connector_type, display_name, config_json, is_active, created_at, updated_at "
            "FROM domain_shared.connectors WHERE tenant_id = :tid ORDER BY connector_key"
        ),
        {"tid": tenant_id}
    ).fetchall()
    return [
        ConnectorOut(
            id=str(r[0]),
            tenant_id=str(r[1]),
            connector_key=r[2],
            connector_type=r[3],
            display_name=r[4],
            config_json=r[5],
            is_active=r[6],
            created_at=r[7],
            updated_at=r[8],
        )
        for r in rows
    ]


@router.get("/connectors/{connector_id}", response_model=ConnectorOut, summary="Connector abrufen")
async def get_connector(
    connector_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get connector by ID."""
    from sqlalchemy import text
    row = db.execute(
        text(
            "SELECT id, tenant_id, connector_key, connector_type, display_name, config_json, is_active, created_at, updated_at "
            "FROM domain_shared.connectors WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": connector_id, "tid": tenant_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Connector not found")
    return ConnectorOut(
        id=str(row[0]),
        tenant_id=str(row[1]),
        connector_key=row[2],
        connector_type=row[3],
        display_name=row[4],
        config_json=row[5],
        is_active=row[6],
        created_at=row[7],
        updated_at=row[8],
    )


@router.put("/connectors", response_model=ConnectorOut, status_code=201, summary="Connector upsert")
async def upsert_connector(
    payload: ConnectorCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create or update connector."""
    from uuid import uuid4
    from sqlalchemy import text
    uid = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.connectors (id, tenant_id, connector_key, connector_type, display_name, config_json, is_active)
            VALUES (:id, :tid, :key, :type, :dn, :cfg, :active)
            ON CONFLICT DO NOTHING
            """
        ),
        {
            "id": uid,
            "tid": tenant_id,
            "key": payload.connector_key,
            "type": payload.connector_type,
            "dn": payload.display_name,
            "cfg": payload.config_json,
            "active": payload.is_active,
        }
    )
    db.commit()
    return await get_connector(uid, db, tenant_id)


@router.patch("/connectors/{connector_id}", response_model=ConnectorOut, summary="Connector aktualisieren")
async def update_connector(
    connector_id: str,
    payload: ConnectorUpdateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Update connector by ID."""
    from sqlalchemy import text
    row = db.execute(
        text("SELECT id FROM domain_shared.connectors WHERE id = :id AND tenant_id = :tid"),
        {"id": connector_id, "tid": tenant_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Connector not found")
    db.execute(
        text(
            "UPDATE domain_shared.connectors SET "
            "display_name = COALESCE(:dn, display_name), "
            "config_json = COALESCE(CAST(:cfg AS jsonb), config_json), "
            "is_active = COALESCE(:active, is_active), updated_at = now() "
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {
            "id": connector_id,
            "tid": tenant_id,
            "dn": payload.display_name,
            "cfg": payload.config_json,
            "active": payload.is_active,
        },
    )
    db.commit()
    return await get_connector(connector_id, db, tenant_id)


@router.delete("/connectors/{connector_id}", status_code=204, response_class=Response, response_model=None, summary="Connector löschen")
async def delete_connector(
    connector_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Delete connector by ID."""
    from sqlalchemy import text
    r = db.execute(
        text("DELETE FROM domain_shared.connectors WHERE id = :id AND tenant_id = :tid"),
        {"id": connector_id, "tid": tenant_id}
    )
    db.commit()
    if r.rowcount == 0:
        raise HTTPException(status_code=404, detail="Connector not found")


# ── Reporting Units ─────────────────────────────────────────────────────────────

class ReportingUnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    unit_key: str
    display_name: str
    connector_id: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReportingUnitCreateIn(BaseModel):
    unit_key: str = Field(..., min_length=1, max_length=80)
    display_name: str = Field(..., min_length=1, max_length=200)
    connector_id: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool = True


class ReportingUnitUpdateIn(BaseModel):
    display_name: Optional[str] = None
    connector_id: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: Optional[bool] = None


@router.get("/reporting-units", response_model=list[ReportingUnitOut], summary="Reporting units auflisten")
async def list_reporting_units(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List reporting units (Firmen/Meldeeinheiten)."""
    from sqlalchemy import text
    rows = db.execute(
        text(
            "SELECT id, tenant_id, unit_key, display_name, connector_id, config_json, is_active, created_at, updated_at "
            "FROM domain_shared.reporting_units WHERE tenant_id = :tid ORDER BY unit_key"
        ),
        {"tid": tenant_id}
    ).fetchall()
    return [
        ReportingUnitOut(
            id=str(r[0]),
            tenant_id=str(r[1]),
            unit_key=r[2],
            display_name=r[3],
            connector_id=str(r[4]) if r[4] else None,
            config_json=r[5],
            is_active=r[6],
            created_at=r[7],
            updated_at=r[8],
        )
        for r in rows
    ]


@router.put("/reporting-units", response_model=ReportingUnitOut, status_code=201, summary="Reporting unit upsert")
async def upsert_reporting_unit(
    payload: ReportingUnitCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create or update reporting unit."""
    from uuid import uuid4
    from sqlalchemy import text
    uid = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.reporting_units (id, tenant_id, unit_key, display_name, connector_id, config_json, is_active)
            VALUES (:id, :tid, :key, :dn, :conn_id, :cfg, :active)
            """
        ),
        {
            "id": uid,
            "tid": tenant_id,
            "key": payload.unit_key,
            "dn": payload.display_name,
            "conn_id": payload.connector_id,
            "cfg": payload.config_json,
            "active": payload.is_active,
        }
    )
    db.commit()
    row = db.execute(
        text(
            "SELECT id, tenant_id, unit_key, display_name, connector_id, config_json, is_active, created_at, updated_at "
            "FROM domain_shared.reporting_units WHERE id = :id"
        ),
        {"id": uid}
    ).fetchone()
    return ReportingUnitOut(
        id=str(row[0]),
        tenant_id=str(row[1]),
        unit_key=row[2],
        display_name=row[3],
        connector_id=str(row[4]) if row[4] else None,
        config_json=row[5],
        is_active=row[6],
        created_at=row[7],
        updated_at=row[8],
    )


@router.patch("/reporting-units/{unit_id}", response_model=ReportingUnitOut, summary="Reporting unit aktualisieren")
async def update_reporting_unit(
    unit_id: str,
    payload: ReportingUnitUpdateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Update reporting unit by ID."""
    from sqlalchemy import text
    row = db.execute(
        text("SELECT id FROM domain_shared.reporting_units WHERE id = :id AND tenant_id = :tid"),
        {"id": unit_id, "tid": tenant_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Reporting unit not found")
    db.execute(
        text(
            "UPDATE domain_shared.reporting_units SET "
            "display_name = COALESCE(:dn, display_name), "
            "connector_id = COALESCE(:conn_id, connector_id), "
            "config_json = COALESCE(CAST(:cfg AS jsonb), config_json), "
            "is_active = COALESCE(:active, is_active), updated_at = now() "
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {
            "id": unit_id,
            "tid": tenant_id,
            "dn": payload.display_name,
            "conn_id": payload.connector_id,
            "cfg": payload.config_json,
            "active": payload.is_active,
        },
    )
    db.commit()
    row2 = db.execute(
        text(
            "SELECT id, tenant_id, unit_key, display_name, connector_id, config_json, is_active, created_at, updated_at "
            "FROM domain_shared.reporting_units WHERE id = :id"
        ),
        {"id": unit_id}
    ).fetchone()
    return ReportingUnitOut(
        id=str(row2[0]),
        tenant_id=str(row2[1]),
        unit_key=row2[2],
        display_name=row2[3],
        connector_id=str(row2[4]) if row2[4] else None,
        config_json=row2[5],
        is_active=row2[6],
        created_at=row2[7],
        updated_at=row2[8],
    )


@router.delete("/reporting-units/{unit_id}", status_code=204, response_class=Response, response_model=None, summary="Reporting unit löschen")
async def delete_reporting_unit(
    unit_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Delete reporting unit by ID."""
    from sqlalchemy import text
    r = db.execute(
        text("DELETE FROM domain_shared.reporting_units WHERE id = :id AND tenant_id = :tid"),
        {"id": unit_id, "tid": tenant_id}
    )
    db.commit()
    if r.rowcount == 0:
        raise HTTPException(status_code=404, detail="Reporting unit not found")


# ── Schedules ───────────────────────────────────────────────────────────────────

class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    schedule_key: str
    display_name: str
    reporting_unit_id: Optional[str] = None
    cron_expr: Optional[str] = None
    lead_days: int
    use_workday_rule: bool
    output_format: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ScheduleCreateIn(BaseModel):
    schedule_key: str = Field(..., min_length=1, max_length=80)
    display_name: str = Field(..., min_length=1, max_length=200)
    reporting_unit_id: Optional[str] = None
    cron_expr: Optional[str] = None
    lead_days: int = 5
    use_workday_rule: bool = False
    output_format: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: bool = True


class ScheduleUpdateIn(BaseModel):
    display_name: Optional[str] = None
    reporting_unit_id: Optional[str] = None
    cron_expr: Optional[str] = None
    lead_days: Optional[int] = None
    use_workday_rule: Optional[bool] = None
    output_format: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: Optional[bool] = None


@router.get("/schedules", response_model=list[ScheduleOut], summary="Schedules auflisten")
async def list_schedules(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List schedules (Stichtag - leadDays, 10. Arbeitstag)."""
    from sqlalchemy import text
    rows = db.execute(
        text(
            "SELECT id, tenant_id, schedule_key, display_name, reporting_unit_id, cron_expr, lead_days, use_workday_rule, output_format, "
            "COALESCE(config_json, '{}'::jsonb) as config_json, is_active, created_at, updated_at "
            "FROM domain_shared.schedules WHERE tenant_id = :tid ORDER BY schedule_key"
        ),
        {"tid": tenant_id}
    ).fetchall()
    return [
        ScheduleOut(
            id=str(r[0]),
            tenant_id=str(r[1]),
            schedule_key=r[2],
            display_name=r[3],
            reporting_unit_id=str(r[4]) if r[4] else None,
            cron_expr=r[5],
            lead_days=r[6],
            use_workday_rule=r[7],
            output_format=r[8],
            config_json=r[9],
            is_active=r[10],
            created_at=r[11],
            updated_at=r[12],
        )
        for r in rows
    ]


@router.put("/schedules", response_model=ScheduleOut, status_code=201, summary="Schedule upsert")
async def upsert_schedule(
    payload: ScheduleCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create or update schedule."""
    from uuid import uuid4
    from sqlalchemy import text
    uid = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.schedules (id, tenant_id, schedule_key, display_name, reporting_unit_id, cron_expr, lead_days, use_workday_rule, output_format, config_json, is_active)
            VALUES (:id, :tid, :key, :dn, :ru_id, :cron, :lead, :workday, :fmt, CAST(:cfg AS jsonb), :active)
            """
        ),
        {
            "id": uid,
            "tid": tenant_id,
            "key": payload.schedule_key,
            "dn": payload.display_name,
            "ru_id": payload.reporting_unit_id,
            "cron": payload.cron_expr,
            "lead": payload.lead_days,
            "workday": payload.use_workday_rule,
            "fmt": payload.output_format,
            "cfg": payload.config_json,
            "active": payload.is_active,
        }
    )
    db.commit()
    row = db.execute(
        text(
            "SELECT id, tenant_id, schedule_key, display_name, reporting_unit_id, cron_expr, lead_days, use_workday_rule, output_format, "
            "COALESCE(config_json, '{}'::jsonb) as config_json, is_active, created_at, updated_at "
            "FROM domain_shared.schedules WHERE id = :id"
        ),
        {"id": uid}
    ).fetchone()
    return ScheduleOut(
        id=str(row[0]),
        tenant_id=str(row[1]),
        schedule_key=row[2],
        display_name=row[3],
        reporting_unit_id=str(row[4]) if row[4] else None,
        cron_expr=row[5],
        lead_days=row[6],
        use_workday_rule=row[7],
        output_format=row[8],
        config_json=row[9],
        is_active=row[10],
        created_at=row[11],
        updated_at=row[12],
    )


@router.patch("/schedules/{schedule_id}", response_model=ScheduleOut, summary="Schedule aktualisieren")
async def update_schedule(
    schedule_id: str,
    payload: ScheduleUpdateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Update schedule by ID."""
    from sqlalchemy import text
    row = db.execute(
        text("SELECT id FROM domain_shared.schedules WHERE id = :id AND tenant_id = :tid"),
        {"id": schedule_id, "tid": tenant_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.execute(
        text(
            "UPDATE domain_shared.schedules SET "
            "display_name = COALESCE(:dn, display_name), "
            "reporting_unit_id = COALESCE(:ru_id, reporting_unit_id), "
            "cron_expr = COALESCE(:cron, cron_expr), "
            "lead_days = COALESCE(:lead, lead_days), "
            "use_workday_rule = COALESCE(:workday, use_workday_rule), "
            "output_format = COALESCE(:fmt, output_format), "
            "config_json = COALESCE(CAST(:cfg AS jsonb), config_json), "
            "is_active = COALESCE(:active, is_active), updated_at = now() "
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {
            "id": schedule_id,
            "tid": tenant_id,
            "dn": payload.display_name,
            "ru_id": payload.reporting_unit_id,
            "cron": payload.cron_expr,
            "lead": payload.lead_days,
            "workday": payload.use_workday_rule,
            "fmt": payload.output_format,
            "cfg": payload.config_json,
            "active": payload.is_active,
        },
    )
    db.commit()
    row2 = db.execute(
        text(
            "SELECT id, tenant_id, schedule_key, display_name, reporting_unit_id, cron_expr, lead_days, use_workday_rule, output_format, "
            "COALESCE(config_json, '{}'::jsonb) as config_json, is_active, created_at, updated_at "
            "FROM domain_shared.schedules WHERE id = :id"
        ),
        {"id": schedule_id}
    ).fetchone()
    return ScheduleOut(
        id=str(row2[0]),
        tenant_id=str(row2[1]),
        schedule_key=row2[2],
        display_name=row2[3],
        reporting_unit_id=str(row2[4]) if row2[4] else None,
        cron_expr=row2[5],
        lead_days=row2[6],
        use_workday_rule=row2[7],
        output_format=row2[8],
        config_json=row2[9],
        is_active=row2[10],
        created_at=row2[11],
        updated_at=row2[12],
    )


@router.delete("/schedules/{schedule_id}", status_code=204, response_class=Response, response_model=None, summary="Schedule löschen")
async def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Delete schedule by ID."""
    from sqlalchemy import text
    r = db.execute(
        text("DELETE FROM domain_shared.schedules WHERE id = :id AND tenant_id = :tid"),
        {"id": schedule_id, "tid": tenant_id}
    )
    db.commit()
    if r.rowcount == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
