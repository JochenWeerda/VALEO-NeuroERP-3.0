"""
Liquiditätsplanung — 13-Wochen-Rolling-Forecast, thin-router pattern
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.liquidity_planning_schemas import LiquidityPlanningOut


router = APIRouter(prefix="/finance/liquidity", tags=["finance", "liquidity"])

_TABLE_SCENARIOS = "domain_finance.liquidity_scenarios"


def _503(hint: str = "alembic upgrade head") -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={"error": "Tabelle nicht vorhanden", "migration_hint": hint},
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _week_start(ref: date, offset_weeks: int) -> date:
    """Monday of the week that is offset_weeks from ref's week."""
    monday = ref - timedelta(days=ref.weekday())
    return monday + timedelta(weeks=offset_weeks)


def _query_open_items_for_week(
    db: Session,
    tenant_id: str,
    week_start: date,
    week_end: date,
    item_type: str,  # "debitor" | "kreditor"
) -> float:
    """
    Sum open items due within [week_start, week_end].
    Falls back to 0.0 if table not available.
    """
    try:
        row = db.execute(
            text(
                """SELECT COALESCE(SUM(open_amount), 0)
                FROM domain_finance.open_items
                WHERE tenant_id = :tid
                AND type = :typ
                AND due_date BETWEEN :ws AND :we
                AND status = 'OPEN'"""
            ),
            {"tid": tenant_id, "typ": item_type, "ws": week_start, "we": week_end},
        ).scalar()
        return float(row or 0)
    except Exception:
        return 0.0


def _get_cash_at_bank(db: Session, tenant_id: str) -> float:
    try:
        row = db.execute(
            text(
                """SELECT COALESCE(SUM(current_balance), 0)
                FROM domain_finance.bank_accounts
                WHERE tenant_id = :tid AND is_active = true"""
            ),
            {"tid": tenant_id},
        ).scalar()
        return float(row or 0)
    except Exception:
        return 0.0


def _get_open_receivables(db: Session, tenant_id: str) -> float:
    try:
        row = db.execute(
            text(
                """SELECT COALESCE(SUM(open_amount), 0)
                FROM domain_finance.open_items
                WHERE tenant_id = :tid AND type = 'debitor' AND status = 'OPEN'"""
            ),
            {"tid": tenant_id},
        ).scalar()
        return float(row or 0)
    except Exception:
        return 0.0


def _get_open_payables(db: Session, tenant_id: str) -> float:
    try:
        row = db.execute(
            text(
                """SELECT COALESCE(SUM(open_amount), 0)
                FROM domain_finance.open_items
                WHERE tenant_id = :tid AND type = 'kreditor' AND status = 'OPEN'"""
            ),
            {"tid": tenant_id},
        ).scalar()
        return float(row or 0)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ScenarioAdjustment(BaseModel):
    week: int = Field(..., ge=1, le=52, description="Wochennummer (1=aktuelle Woche)")
    receipts_delta: float = 0.0
    payments_delta: float = 0.0


class ScenarioCreate(BaseModel):
    name: str
    adjustments: List[ScenarioAdjustment] = []


# ---------------------------------------------------------------------------
# GET /finance/liquidity/forecast
# ---------------------------------------------------------------------------

@router.get("/forecast", tags=["finance", "liquidity"], summary="Forecast liquidity",
    response_model=LiquidityPlanningOut
)
def liquidity_forecast(
    weeks: int = Query(13, ge=1, le=52),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    today = date.today()
    cash_start = _get_cash_at_bank(db, tenant_id)
    cumulative = cash_start

    bounded_weeks = max(1, min(weeks, 52))
    result = []
    for i in range(bounded_weeks):
        ws = _week_start(today, i)
        we = ws + timedelta(days=6)

        receipts = _query_open_items_for_week(db, tenant_id, ws, we, "debitor")
        payments = _query_open_items_for_week(db, tenant_id, ws, we, "kreditor")
        # Payroll estimate: 0 when no data available
        payroll = 0.0

        net = receipts - payments - payroll
        cumulative = round(cumulative + net, 2)

        result.append(
            {
                "week_number": i + 1,
                "week_start": ws.isoformat(),
                "week_end": we.isoformat(),
                "receipts_eur": round(receipts, 2),
                "payments_eur": round(payments + payroll, 2),
                "payroll_estimate_eur": payroll,
                "balance_eur": round(net, 2),
                "cumulative_balance_eur": cumulative,
            }
        )

    return {
        "as_of": today.isoformat(),
        "opening_cash_eur": round(cash_start, 2),
        "weeks": result,
    }


# ---------------------------------------------------------------------------
# GET /finance/liquidity/cash-position
# ---------------------------------------------------------------------------

@router.get("/cash-position", tags=["finance", "liquidity"], summary="Position cash",
    response_model=LiquidityPlanningOut
)
def cash_position(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    cash = _get_cash_at_bank(db, tenant_id)
    recv = _get_open_receivables(db, tenant_id)
    pay = _get_open_payables(db, tenant_id)
    net = round(cash + recv - pay, 2)

    return {
        "as_of": datetime.now(tz=timezone.utc).isoformat(),
        "cash_at_bank_eur": round(cash, 2),
        "open_receivables_eur": round(recv, 2),
        "open_payables_eur": round(pay, 2),
        "net_liquidity_eur": net,
    }


# ---------------------------------------------------------------------------
# POST /finance/liquidity/scenarios
# ---------------------------------------------------------------------------

@router.post("/scenarios", status_code=201, tags=["finance", "liquidity"], summary="Liquidity scenario anlegen",
    response_model=LiquidityPlanningOut
)
def create_liquidity_scenario(
    body: ScenarioCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    # Ensure scenario table exists; create inline if missing (graceful fallback)
    try:
        db.execute(text(f"SELECT 1 FROM {_TABLE_SCENARIOS} LIMIT 0"))  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
    except Exception:
        # Table doesn't exist — return forecast with adjustments applied without persisting
        logger.warning("liquidity_scenarios table missing; returning computed scenario without persistence")
        return _compute_scenario(body, tenant_id, db, persisted=False)

    try:
        import json
        from app.core.uuid7 import uuid7
        sid = str(uuid7())
        db.execute(
            text(
                f"""INSERT INTO {_TABLE_SCENARIOS} (id, name, adjustments, tenant_id, created_at)
                VALUES (:id, :name, :adj::jsonb, :tid, now())"""
            ),
            {
                "id": sid,
                "name": body.name,
                "adj": json.dumps([a.model_dump() for a in body.adjustments]),
                "tid": tenant_id,
            },
        )
        db.commit()
        result = _compute_scenario(body, tenant_id, db, persisted=True)
        result["scenario_id"] = sid
        return result
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("create_liquidity_scenario: %s", exc)
        # Fallback: return result without persistence
        return _compute_scenario(body, tenant_id, db, persisted=False)


def _compute_scenario(
    body: ScenarioCreate,
    tenant_id: str,
    db: Session,
    persisted: bool,
) -> dict:
    """Calculate adjusted 13-week forecast based on scenario adjustments."""
    today = date.today()
    adj_map = {a.week: a for a in body.adjustments}
    cash_start = _get_cash_at_bank(db, tenant_id)
    cumulative = cash_start
    weeks_out = []
    scenario_weeks = 13
    for i in range(scenario_weeks):
        ws = _week_start(today, i)
        we = ws + timedelta(days=6)
        week_num = i + 1
        receipts = _query_open_items_for_week(db, tenant_id, ws, we, "debitor")
        payments = _query_open_items_for_week(db, tenant_id, ws, we, "kreditor")
        adj = adj_map.get(week_num)
        if adj:
            receipts += adj.receipts_delta
            payments += adj.payments_delta
        net = receipts - payments
        cumulative = round(cumulative + net, 2)
        weeks_out.append(
            {
                "week_number": week_num,
                "week_start": ws.isoformat(),
                "week_end": we.isoformat(),
                "receipts_eur": round(receipts, 2),
                "payments_eur": round(payments, 2),
                "balance_eur": round(net, 2),
                "cumulative_balance_eur": cumulative,
            }
        )
    return {
        "scenario_name": body.name,
        "persisted": persisted,
        "opening_cash_eur": round(cash_start, 2),
        "weeks": weeks_out,
    }
