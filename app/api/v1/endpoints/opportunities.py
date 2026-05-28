"""CRM Sales Opportunities API endpoints proxied through crm-sales."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from math import ceil
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....integrations.crm_core_client import (
    create_opportunity as crm_create_opportunity,
    delete_opportunity as crm_delete_opportunity,
    get_opportunity as crm_get_opportunity,
    list_opportunities as crm_list_opportunities,
    update_opportunity as crm_update_opportunity,
)
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Opportunity, OpportunityCreate, OpportunityUpdate

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter()

# ---------------------------------------------------------------------------
# Stage definitions
# ---------------------------------------------------------------------------

OPPORTUNITY_STAGES = ["LEAD", "QUALIFIZIERT", "ANGEBOT", "VERHANDLUNG", "GEWONNEN", "VERLOREN"]


@router.post("/", response_model=Opportunity, status_code=status.HTTP_201_CREATED, summary="Opportunity anlegen")
async def create_opportunity(opportunity_data: OpportunityCreate):
    """Create a new sales opportunity via crm-sales."""
    try:
        created = await crm_create_opportunity(opportunity_data.model_dump())
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create opportunity: {exc}") from exc
    return Opportunity.model_validate(created)


@router.get("/", response_model=PaginatedResponse[Opportunity], summary="Opportunities auflisten")
async def list_opportunities(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return"),
):
    """List sales opportunities from crm-sales with pagination."""
    try:
        opportunities, total = await crm_list_opportunities(
            tenant_id=tenant_id,
            status=status,
            assigned_to=assigned_to,
            skip=skip,
            limit=limit
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list opportunities: {exc}") from exc

    pages = ceil(total / limit) if total else 1
    return PaginatedResponse[Opportunity](
        items=[Opportunity.model_validate(opportunity) for opportunity in opportunities],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


OPPORTUNITY_STAGES_LIST = [
    {"id": "LEAD", "name": "Lead", "order": 1, "probability": 10, "color": "#94a3b8"},
    {"id": "QUALIFIZIERT", "name": "Qualifiziert", "order": 2, "probability": 25, "color": "#60a5fa"},
    {"id": "ANGEBOT", "name": "Angebot", "order": 3, "probability": 50, "color": "#f59e0b"},
    {"id": "VERHANDLUNG", "name": "Verhandlung", "order": 4, "probability": 75, "color": "#f97316"},
    {"id": "GEWONNEN", "name": "Gewonnen", "order": 5, "probability": 100, "color": "#22c55e"},
    {"id": "VERLOREN", "name": "Verloren", "order": 6, "probability": 0, "color": "#ef4444"},
]

_STAGE_DEFAULT_PROB = {s["id"]: s["probability"] for s in OPPORTUNITY_STAGES_LIST}


def _ensure_opp_columns(db: Session) -> None:
    """Add missing columns to opportunities table (idempotent)."""
    cols_sql = text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='opportunities' AND table_schema='public'"
    )
    try:
        existing = {r[0] for r in db.execute(cols_sql)}
    except Exception:
        return
    migrations = [
        ("stage", "ALTER TABLE opportunities ADD COLUMN stage TEXT DEFAULT 'LEAD'"),
        ("probability", "ALTER TABLE opportunities ADD COLUMN probability FLOAT DEFAULT 25"),
        ("expected_close_date", "ALTER TABLE opportunities ADD COLUMN expected_close_date DATE"),
        ("amount", "ALTER TABLE opportunities ADD COLUMN amount NUMERIC"),
        ("stage_history", "ALTER TABLE opportunities ADD COLUMN stage_history JSONB DEFAULT '[]'::jsonb"),
    ]
    for col, ddl in migrations:
        if col not in existing:
            try:
                db.execute(text(ddl))
                db.commit()
            except Exception:
                db.rollback()


@router.get("/stages", response_model=list[CompatFlexOut], summary="Stages auflisten")
async def list_stages():
    """Pipeline-Stages fuer Kanban-Board."""
    return OPPORTUNITY_STAGES_LIST


# ---------------------------------------------------------------------------
# GET /pipeline — Kanban view grouped by stage
# ---------------------------------------------------------------------------

@router.get("/pipeline", response_model=CompatFlexOut, tags=["crm", "opportunities"], summary="Pipeline abrufen")
async def get_pipeline(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Kanban-View: Opportunities gruppiert nach Stage."""
    _ensure_opp_columns(db)

    try:
        sql = text(
            """
            SELECT
                COALESCE(stage, 'LEAD') AS stage,
                COUNT(*)::int AS cnt,
                COALESCE(SUM(COALESCE(amount,0)),0) AS total_value
            FROM opportunities
            WHERE (:tid IS NULL OR tenant_id = :tid)
            GROUP BY COALESCE(stage, 'LEAD')
            """
        )
        rows = db.execute(sql, {"tid": tenant_id}).fetchall()
        agg: dict[str, dict[str, Any]] = {s: {"count": 0, "total_value": 0.0, "items": []} for s in OPPORTUNITY_STAGES}
        for row in rows:
            stage = row[0].upper() if row[0] else "LEAD"
            if stage in agg:
                agg[stage]["count"] = row[1]
                agg[stage]["total_value"] = float(row[2])

        # Fetch items per stage (max 50 each)
        items_sql = text(
            """
            SELECT id, title, COALESCE(stage,'LEAD') AS stage,
                   COALESCE(amount,0) AS amount,
                   COALESCE(probability,0) AS probability,
                   expected_close_date,
                   customer_id, assigned_to
            FROM opportunities
            WHERE (:tid IS NULL OR tenant_id = :tid)
            ORDER BY COALESCE(amount,0) DESC
            LIMIT 300
            """
        )
        item_rows = db.execute(items_sql, {"tid": tenant_id}).fetchall()
        for r in item_rows:
            stage = (r[2] or "LEAD").upper()
            if stage in agg and len(agg[stage]["items"]) < 50:
                agg[stage]["items"].append({
                    "id": str(r[0]),
                    "title": r[1],
                    "stage": stage,
                    "amount": float(r[3]),
                    "probability": float(r[4]),
                    "expected_close_date": str(r[5]) if r[5] else None,
                    "customer_id": str(r[6]) if r[6] else None,
                    "assigned_to": str(r[7]) if r[7] else None,
                })
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline query failed: {exc}") from exc

    return {"stages": [
        {
            "stage": s,
            "label": next(x["name"] for x in OPPORTUNITY_STAGES_LIST if x["id"] == s),
            "count": agg[s]["count"],
            "total_value": agg[s]["total_value"],
            "items": agg[s]["items"],
        }
        for s in OPPORTUNITY_STAGES
    ]}


# ---------------------------------------------------------------------------
# GET /forecast — weighted monthly forecast
# ---------------------------------------------------------------------------

@router.get("/forecast", response_model=CompatFlexOut, summary="Forecast abrufen")
async def get_forecast(
    tenant_id: Optional[str] = Query(None),
    period: Optional[str] = Query(None, description="YYYY-MM"),
    db: Session = Depends(get_db),
):
    """Umsatz-Prognose: probability * amount, gruppiert nach Monat."""
    _ensure_opp_columns(db)

    # Try DB-based forecast first
    try:
        sql = text(
            """
            SELECT
                TO_CHAR(COALESCE(expected_close_date, NOW()::date), 'YYYY-MM') AS month,
                COALESCE(stage, 'LEAD') AS stage,
                COALESCE(amount, 0) AS amount,
                COALESCE(probability, 25) AS probability
            FROM opportunities
            WHERE (:tid IS NULL OR tenant_id = :tid)
              AND COALESCE(stage,'LEAD') NOT IN ('GEWONNEN','VERLOREN')
              AND (:period IS NULL OR TO_CHAR(COALESCE(expected_close_date, NOW()::date), 'YYYY-MM') = :period)
            """
        )
        rows = db.execute(sql, {"tid": tenant_id, "period": period}).fetchall()

        by_month: dict[str, dict[str, float]] = {}
        pipeline_value = 0.0
        weighted_value = 0.0

        for row in rows:
            month, stage, amount, prob = row[0], row[1], float(row[2]), float(row[3])
            pipeline_value += amount
            w = amount * prob / 100
            weighted_value += w
            if month not in by_month:
                by_month[month] = {"pipeline": 0.0, "weighted": 0.0}
            by_month[month]["pipeline"] += amount
            by_month[month]["weighted"] += w

        return {
            "total_opportunities": len(rows),
            "pipeline_value": pipeline_value,
            "weighted_forecast": weighted_value,
            "by_month": [
                {"month": m, "pipeline_value": v["pipeline"], "weighted_value": v["weighted"]}
                for m, v in sorted(by_month.items())
            ],
            "by_stage": [
                {"stage": s["name"], "stage_id": s["id"], "default_probability": s["probability"]}
                for s in OPPORTUNITY_STAGES_LIST
            ],
        }
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass

    # Fallback: CRM integration
    try:
        opps, total = await crm_list_opportunities(tenant_id=tenant_id, skip=0, limit=500)
    except Exception:
        opps, total = [], 0

    pipeline_value = 0.0
    weighted_value = 0.0
    by_stage: dict[str, float] = {}
    stage_map = {s["id"]: s["probability"] for s in OPPORTUNITY_STAGES_LIST}

    for opp in opps:
        value = float(opp.get("value", 0) or opp.get("amount", 0) or 0)
        stage = opp.get("stage", opp.get("status", "LEAD")).upper()
        pipeline_value += value
        prob = stage_map.get(stage, 25) / 100
        weighted_value += value * prob
        by_stage[stage] = by_stage.get(stage, 0) + value

    return {
        "total_opportunities": total,
        "pipeline_value": pipeline_value,
        "weighted_forecast": weighted_value,
        "by_month": [],
        "by_stage": [
            {"stage": s["name"], "stage_id": s["id"], "value": by_stage.get(s["id"], 0)}
            for s in OPPORTUNITY_STAGES_LIST
        ],
    }


# ---------------------------------------------------------------------------
# PATCH /{id}/stage — Stage-Wechsel mit History-Log
# ---------------------------------------------------------------------------

@router.patch("/{opportunity_id}/stage", response_model=CompatFlexOut, tags=["crm", "opportunities"], summary="Opportunity stage aktualisieren")
async def patch_opportunity_stage(
    opportunity_id: str,
    new_stage: str = Query(..., description="Target stage (LEAD/QUALIFIZIERT/ANGEBOT/VERHANDLUNG/GEWONNEN/VERLOREN)"),
    db: Session = Depends(get_db),
):
    """Stage-Wechsel mit Timestamp-Log in stage_history."""
    new_stage = new_stage.upper()
    if new_stage not in OPPORTUNITY_STAGES:
        raise HTTPException(status_code=422, detail=f"Ungueltige Stage. Erlaubt: {OPPORTUNITY_STAGES}")

    _ensure_opp_columns(db)

    try:
        # Check exists
        row = db.execute(
            text("SELECT id, stage, stage_history FROM opportunities WHERE id = :oid"),
            {"oid": opportunity_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Opportunity nicht gefunden")

        old_stage = row[1] or "LEAD"
        history = row[2] or []
        if isinstance(history, str):
            history = json.loads(history)

        history.append({"stage": old_stage, "changed_at": datetime.now(timezone.utc).isoformat()})
        prob = _STAGE_DEFAULT_PROB.get(new_stage, 25)

        db.execute(
            text(
                """
                UPDATE opportunities
                SET stage = :stage,
                    probability = :prob,
                    stage_history = :hist::jsonb,
                    updated_at = NOW()
                WHERE id = :oid
                """
            ),
            {"stage": new_stage, "prob": prob, "hist": json.dumps(history), "oid": opportunity_id},
        )
        db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Stage-Wechsel fehlgeschlagen: {exc}") from exc

    return {
        "id": opportunity_id,
        "old_stage": old_stage,
        "new_stage": new_stage,
        "probability": prob,
        "changed_at": datetime.now(timezone.utc).isoformat(),
        "stage_history": history,
    }


# ---------------------------------------------------------------------------
# POST /{id}/activities — Aktivität zur Opportunity
# ---------------------------------------------------------------------------

@router.post("/{opportunity_id}/activities", response_model=CompatFlexOut, status_code=status.HTTP_201_CREATED,
             tags=["crm", "opportunities"], summary="Opportunity activity hinzufügen")
async def add_opportunity_activity(
    opportunity_id: str,
    activity_type: str = Query("NOTE", description="Aktivitätstyp (NOTE/CALL/EMAIL/MEETING)"),
    subject: str = Query(..., description="Betreff"),
    notes: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Aktivität zur Opportunity hinzufügen."""
    try:
        # Verify opportunity exists
        row = db.execute(
            text("SELECT id FROM opportunities WHERE id = :oid"),
            {"oid": opportunity_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Opportunity nicht gefunden")

        # Try to insert into activities table
        sql = text(
            """
            INSERT INTO activities (id, opportunity_id, activity_type, subject, notes, assigned_to, created_at)
            VALUES (gen_random_uuid(), :oid, :atype, :subject, :notes, :assigned_to, NOW())
            RETURNING id, created_at
            """
        )
        result = db.execute(sql, {
            "oid": opportunity_id,
            "atype": activity_type.upper(),
            "subject": subject,
            "notes": notes,
            "assigned_to": assigned_to,
        }).fetchone()
        db.commit()
        return {
            "id": str(result[0]),
            "opportunity_id": opportunity_id,
            "activity_type": activity_type.upper(),
            "subject": subject,
            "created_at": str(result[1]),
        }
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Aktivitaet konnte nicht erstellt werden: {exc}") from exc


@router.get("/{opportunity_id}", response_model=Opportunity, summary="Opportunity abrufen")
async def get_opportunity(opportunity_id: str):
    """Get a specific sales opportunity by ID."""
    try:
        opportunity = await crm_get_opportunity(opportunity_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Opportunity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve opportunity: {exc}") from exc
    return Opportunity.model_validate(opportunity)


@router.put("/{opportunity_id}", response_model=Opportunity, summary="Opportunity aktualisieren")
async def update_opportunity(opportunity_id: str, opportunity_data: OpportunityUpdate):
    """Update a sales opportunity via crm-sales."""
    try:
        updated = await crm_update_opportunity(opportunity_id, opportunity_data.model_dump(exclude_unset=True))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Opportunity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update opportunity: {exc}") from exc
    return Opportunity.model_validate(updated)


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Opportunity löschen",
    response_model=None
)
async def delete_opportunity(opportunity_id: str):
    """Delete a sales opportunity via crm-sales."""
    try:
        await crm_delete_opportunity(opportunity_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Opportunity not found") from exc
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete opportunity: {exc}") from exc

