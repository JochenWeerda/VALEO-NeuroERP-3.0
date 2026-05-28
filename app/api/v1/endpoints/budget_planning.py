"""
Budgetierung / Forecast — thin-router pattern with sqlalchemy.text()
Tabellen: domain_finance.budget_plans, domain_finance.budget_lines
"""
from __future__ import annotations

import logging
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
from pydantic import ConfigDict as _ConfigDict


class BudgetPlanningOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/finance/budgets", tags=["finance", "budget-planning"])

_TABLE_PLANS = "domain_finance.budget_plans"
_TABLE_LINES = "domain_finance.budget_lines"

VALID_STATUSES = {"ENTWURF", "GENEHMIGT", "GESPERRT"}


def _503(hint: str = "alembic upgrade head") -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={"error": "Tabelle nicht vorhanden", "migration_hint": hint},
    )


def _check_tables(db: Session) -> None:
    try:
        db.execute(text("SELECT 1 FROM domain_finance.budget_plans LIMIT 0"))
        db.execute(text("SELECT 1 FROM domain_finance.budget_lines LIMIT 0"))
    except Exception:
        raise _503()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class BudgetPlanCreate(BaseModel):
    plan_year: int
    plan_name: str
    status: str = "ENTWURF"


class BudgetLineCreate(BaseModel):
    kostenstelle_id: Optional[str] = None
    account_id: str
    period_month: int = Field(..., ge=1, le=12)
    budgeted_amount: Decimal


class BudgetLineUpdate(BaseModel):
    budgeted_amount: Optional[Decimal] = None
    period_month: Optional[int] = Field(None, ge=1, le=12)


# ---------------------------------------------------------------------------
# GET /finance/budgets  (summary shortcut lives at /summary)
# ---------------------------------------------------------------------------

@router.get("", tags=["finance", "budget-planning"], summary="Budget plans auflisten",
    response_model=BudgetPlanningOut
)
def list_budget_plans(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        rows = db.execute(
            text("SELECT * FROM domain_finance.budget_plans WHERE tenant_id = :tid ORDER BY plan_year DESC, plan_name"),
            {"tid": tenant_id},
        ).mappings().all()
        return {"items": [dict(r) for r in rows], "total": len(rows)}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("list_budget_plans: %s", exc)
        raise _503()


@router.post("", status_code=201, tags=["finance", "budget-planning"], summary="Budget plan anlegen",
    response_model=BudgetPlanningOut
)
def create_budget_plan(
    body: BudgetPlanCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    if body.status.upper() not in VALID_STATUSES:
        raise HTTPException(422, f"status muss einer von {VALID_STATUSES} sein")
    try:
        from app.core.uuid7 import uuid7
        pid = str(uuid7())
        db.execute(
            text(
                f"""INSERT INTO {_TABLE_PLANS} (id, plan_year, plan_name, status, tenant_id)
                VALUES (:id, :yr, :name, :st, :tid)"""
            ),
            {"id": pid, "yr": body.plan_year, "name": body.plan_name, "st": body.status.upper(), "tid": tenant_id},
        )
        db.commit()
        return {"id": pid, "plan_name": body.plan_name, "status": body.status.upper()}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("create_budget_plan: %s", exc)
        raise _503()


# ---------------------------------------------------------------------------
# GET /finance/budgets/summary  — muss VOR /{id} stehen!
# ---------------------------------------------------------------------------

@router.get("/summary", tags=["finance", "budget-planning"], summary="Summary budget",
    response_model=BudgetPlanningOut
)
def budget_summary(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        # Find the current approved budget (latest plan_year, GENEHMIGT)
        plan = db.execute(
            text(
                f"""SELECT * FROM {_TABLE_PLANS}
                WHERE tenant_id = :tid AND status = 'GENEHMIGT'
                ORDER BY plan_year DESC LIMIT 1"""
            ),
            {"tid": tenant_id},
        ).mappings().first()
        if not plan:
            return {"message": "Kein genehmigtes Budget vorhanden", "total_budget_eur": 0, "pct_used": 0}

        total_budget = db.execute(
            text("SELECT COALESCE(SUM(budgeted_amount), 0) FROM domain_finance.budget_lines WHERE plan_id = :pid AND tenant_id = :tid"),
            {"pid": plan["id"], "tid": tenant_id},
        ).scalar() or 0

        # Actual spend from journal_entries if available
        actual = 0.0
        try:
            actual = db.execute(
                text(
                    """SELECT COALESCE(SUM(ABS(amount)), 0)
                    FROM domain_finance.journal_entries
                    WHERE tenant_id = :tid
                    AND EXTRACT(YEAR FROM posting_date) = :yr"""
                ),
                {"tid": tenant_id, "yr": plan["plan_year"]},
            ).scalar() or 0.0
        except Exception:
            actual = 0.0

        pct = round(float(actual) / float(total_budget) * 100, 1) if float(total_budget) > 0 else 0.0
        return {
            "plan_id": plan["id"],
            "plan_name": plan["plan_name"],
            "plan_year": plan["plan_year"],
            "total_budget_eur": float(total_budget),
            "total_actual_eur": float(actual),
            "pct_used": pct,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("budget_summary: %s", exc)
        raise _503()


# ---------------------------------------------------------------------------
# GET/POST /finance/budgets/{id}
# ---------------------------------------------------------------------------

@router.get("/{plan_id}", tags=["finance", "budget-planning"], summary="Budget plan abrufen",
    response_model=BudgetPlanningOut
)
def get_budget_plan(
    plan_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        plan = db.execute(
            text("SELECT * FROM domain_finance.budget_plans WHERE id = :id AND tenant_id = :tid"),
            {"id": plan_id, "tid": tenant_id},
        ).mappings().first()
        if not plan:
            raise HTTPException(404, "Budget-Plan nicht gefunden")

        lines = db.execute(
            text("SELECT * FROM domain_finance.budget_lines WHERE plan_id = :pid AND tenant_id = :tid ORDER BY period_month"),
            {"pid": plan_id, "tid": tenant_id},
        ).mappings().all()

        return {"plan": dict(plan), "lines": [dict(l) for l in lines]}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_budget_plan: %s", exc)
        raise _503()


@router.post("/{plan_id}/approve", tags=["finance", "budget-planning"], summary="Budget plan genehmigen",
    response_model=BudgetPlanningOut
)
def approve_budget_plan(
    plan_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        plan = db.execute(
            text("SELECT status FROM domain_finance.budget_plans WHERE id = :id AND tenant_id = :tid"),
            {"id": plan_id, "tid": tenant_id},
        ).first()
        if not plan:
            raise HTTPException(404, "Budget-Plan nicht gefunden")
        if plan[0] != "ENTWURF":
            raise HTTPException(409, f"Budget ist bereits im Status '{plan[0]}' — Genehmigung nur aus ENTWURF möglich")
        db.execute(
            text("UPDATE domain_finance.budget_plans SET status = 'GENEHMIGT' WHERE id = :id AND tenant_id = :tid"),
            {"id": plan_id, "tid": tenant_id},
        )
        db.commit()
        return {"approved": True, "plan_id": plan_id, "new_status": "GENEHMIGT"}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("approve_budget_plan: %s", exc)
        raise _503()


@router.get("/{plan_id}/vs-actual", tags=["finance", "budget-planning"], summary="Vs actual budget",
    response_model=BudgetPlanningOut
)
def budget_vs_actual(
    plan_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        plan = db.execute(
            text("SELECT plan_year FROM domain_finance.budget_plans WHERE id = :id AND tenant_id = :tid"),
            {"id": plan_id, "tid": tenant_id},
        ).first()
        if not plan:
            raise HTTPException(404, "Budget-Plan nicht gefunden")

        lines = db.execute(
            text(
                f"""SELECT kostenstelle_id, account_id, period_month,
                       SUM(budgeted_amount) AS budgeted_amount
                FROM {_TABLE_LINES}
                WHERE plan_id = :pid AND tenant_id = :tid
                GROUP BY kostenstelle_id, account_id, period_month"""
            ),
            {"pid": plan_id, "tid": tenant_id},
        ).mappings().all()

        result = []
        for line in lines:
            budgeted = float(line["budgeted_amount"])
            # Try to get actual from journal_entries
            actual = 0.0
            try:
                actual_row = db.execute(
                    text(
                        """SELECT COALESCE(SUM(ABS(amount)), 0)
                        FROM domain_finance.journal_entries
                        WHERE tenant_id = :tid
                        AND account_id = :aid
                        AND EXTRACT(YEAR FROM posting_date) = :yr
                        AND EXTRACT(MONTH FROM posting_date) = :mo"""
                    ),
                    {
                        "tid": tenant_id,
                        "aid": line["account_id"],
                        "yr": plan[0],
                        "mo": line["period_month"],
                    },
                ).scalar()
                actual = float(actual_row or 0)
            except Exception:
                actual = 0.0

            variance = round(budgeted - actual, 2)
            pct = round(variance / budgeted * 100, 1) if budgeted != 0 else 0.0
            result.append(
                {
                    "kostenstelle_id": line["kostenstelle_id"],
                    "account_id": line["account_id"],
                    "period_month": line["period_month"],
                    "budgeted_amount_eur": budgeted,
                    "actual_amount_eur": actual,
                    "variance_amount_eur": variance,
                    "variance_percent": pct,
                }
            )

        return {"plan_id": plan_id, "items": result}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("budget_vs_actual: %s", exc)
        raise _503()


@router.post("/{plan_id}/lines", status_code=201, tags=["finance", "budget-planning"], summary="Budget line hinzufügen",
    response_model=BudgetPlanningOut
)
def add_budget_line(
    plan_id: str,
    body: BudgetLineCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        plan = db.execute(
            text("SELECT status FROM domain_finance.budget_plans WHERE id = :id AND tenant_id = :tid"),
            {"id": plan_id, "tid": tenant_id},
        ).first()
        if not plan:
            raise HTTPException(404, "Budget-Plan nicht gefunden")
        if plan[0] == "GESPERRT":
            raise HTTPException(409, "Budget ist gesperrt — keine Änderungen möglich")

        from app.core.uuid7 import uuid7
        lid = str(uuid7())
        db.execute(
            text(
                f"""INSERT INTO {_TABLE_LINES}
                (id, plan_id, kostenstelle_id, account_id, period_month, budgeted_amount, tenant_id)
                VALUES (:id, :pid, :kst, :aid, :mo, :amt, :tid)"""
            ),
            {
                "id": lid,
                "pid": plan_id,
                "kst": body.kostenstelle_id,
                "aid": body.account_id,
                "mo": body.period_month,
                "amt": float(body.budgeted_amount),
                "tid": tenant_id,
            },
        )
        db.commit()
        return {"id": lid, "plan_id": plan_id}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("add_budget_line: %s", exc)
        raise _503()


@router.patch("/{plan_id}/lines/{line_id}", tags=["finance", "budget-planning"], summary="Budget line aktualisieren",
    response_model=BudgetPlanningOut
)
def update_budget_line(
    plan_id: str,
    line_id: str,
    body: BudgetLineUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _check_tables(db)
    try:
        plan = db.execute(
            text("SELECT status FROM domain_finance.budget_plans WHERE id = :id AND tenant_id = :tid"),
            {"id": plan_id, "tid": tenant_id},
        ).first()
        if not plan:
            raise HTTPException(404, "Budget-Plan nicht gefunden")
        if plan[0] == "GESPERRT":
            raise HTTPException(409, "Budget ist gesperrt")

        line = db.execute(
            text("SELECT id FROM domain_finance.budget_lines WHERE id = :id AND plan_id = :pid AND tenant_id = :tid"),
            {"id": line_id, "pid": plan_id, "tid": tenant_id},
        ).first()
        if not line:
            raise HTTPException(404, "Budget-Zeile nicht gefunden")

        fields = body.model_dump(exclude_none=True)
        if not fields:
            raise HTTPException(422, "Keine Felder angegeben")

        set_parts = [f"{k} = :{k}" for k in fields]
        params = {**fields, "id": line_id, "pid": plan_id, "tid": tenant_id}
        if "budgeted_amount" in fields:
            params["budgeted_amount"] = float(params["budgeted_amount"])
        db.execute(
            text(
                f"UPDATE {_TABLE_LINES} SET {', '.join(set_parts)} WHERE id = :id AND plan_id = :pid AND tenant_id = :tid"
            ),
            params,
        )
        db.commit()
        return {"updated": True, "line_id": line_id}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("update_budget_line: %s", exc)
        raise _503()
