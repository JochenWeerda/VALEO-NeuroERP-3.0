"""
CRM Reports and Analytics endpoints.
CRM-REP-01: Standard-CRM-Reports, Pipeline Funnel, Win/Loss-Analyse
"""

from __future__ import annotations

import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/crm/reports", tags=["crm", "reports"])

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class PipelineFunnelStage(BaseModel):
    stage_key: str
    stage_label: str
    count: int
    total_value: float
    weighted_value: float
    conversion_from_prev: Optional[float] = None


class PipelineFunnelReport(BaseModel):
    stages: List[PipelineFunnelStage]
    total_opportunities: int
    total_pipeline_value: float
    weighted_pipeline_value: float
    overall_conversion_rate: Optional[float] = None


class WinLossSummary(BaseModel):
    won_count: int
    won_value: float
    lost_count: int
    lost_value: float
    win_rate: float
    loss_reasons: List[dict]


class LeadSourceSummary(BaseModel):
    source: str
    count: int
    converted_count: int
    conversion_rate: float


@router.get("/pipeline-funnel", response_model=PipelineFunnelReport, summary="Pipeline funnel report abrufen")
async def get_pipeline_funnel_report(
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Pipeline funnel with stage distribution and conversion rates."""
    try:
        rows = db.execute(
            text("""
                SELECT stage, COUNT(*), COALESCE(SUM(estimated_value), 0),
                       SUM(COALESCE(estimated_value, 0) * COALESCE(probability, 0) / 100)
                FROM domain_crm.crm_opportunities
                WHERE tenant_id = :tid AND is_active = TRUE
                GROUP BY stage
                ORDER BY stage
            """),
            {"tid": tenant_id},
        ).fetchall()

        stages_order = [
            "prospecting", "qualification", "initial_contact", "needs_analysis",
            "proposal", "negotiation", "negotiation_review", "closed_won", "closed_lost",
        ]
        stage_labels = {
            "prospecting": "Akquise", "qualification": "Qualifizierung",
            "initial_contact": "Erstkontakt", "needs_analysis": "Bedarfsanalyse",
            "proposal": "Angebot", "negotiation": "Verhandlung",
            "negotiation_review": "Prüfung", "closed_won": "Gewonnen",
            "closed_lost": "Verloren",
        }

        by_stage = {r[0]: {"count": r[1], "value": float(r[2]), "weighted": float(r[3])} for r in rows}
        stages_out: List[PipelineFunnelStage] = []
        prev_count = None
        for sk in stages_order:
            data = by_stage.get(sk, {"count": 0, "value": 0, "weighted": 0})
            conv = None
            if prev_count is not None and prev_count > 0 and data["count"] > 0:
                conv = round(data["count"] / prev_count * 100, 1)
            stages_out.append(
                PipelineFunnelStage(
                    stage_key=sk,
                    stage_label=stage_labels.get(sk, sk),
                    count=data["count"],
                    total_value=data["value"],
                    weighted_value=data["weighted"],
                    conversion_from_prev=conv,
                )
            )
            if data["count"] > 0:
                prev_count = data["count"]

        total_opps = sum(s.count for s in stages_out)
        total_val = sum(s.total_value for s in stages_out)
        weighted_val = sum(s.weighted_value for s in stages_out)
        won = by_stage.get("closed_won", {"count": 0})["count"]
        overall_conv = round(won / total_opps * 100, 1) if total_opps > 0 else None

        return PipelineFunnelReport(
            stages=stages_out,
            total_opportunities=total_opps,
            total_pipeline_value=total_val,
            weighted_pipeline_value=weighted_val,
            overall_conversion_rate=overall_conv,
        )
    except Exception as e:
        logger.warning("Pipeline funnel query failed: %s", e)
        return PipelineFunnelReport(
            stages=[], total_opportunities=0,
            total_pipeline_value=0, weighted_pipeline_value=0,
        )


@router.get("/win-loss", response_model=WinLossSummary, summary="Win loss report abrufen")
async def get_win_loss_report(
    period_from: Optional[date] = None,
    period_to: Optional[date] = None,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Win/Loss analysis with loss reasons."""
    try:
        where = ["tenant_id = :tid", "is_active = TRUE"]
        params: dict = {"tid": tenant_id}
        if period_from:
            where.append("updated_at >= :from")
            params["from"] = period_from
        if period_to:
            where.append("updated_at <= :to")
            params["to"] = period_to

        won = db.execute(
            # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            text(f"""
                SELECT COUNT(*), COALESCE(SUM(estimated_value), 0)
                FROM domain_crm.crm_opportunities
                WHERE {' AND '.join(where)} AND stage = 'closed_won'
            """),
            params,
        ).fetchone()
        lost = db.execute(
            # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            text(f"""
                SELECT COUNT(*), COALESCE(SUM(estimated_value), 0)
                FROM domain_crm.crm_opportunities
                WHERE {' AND '.join(where)} AND stage = 'closed_lost'
            """),
            params,
        ).fetchone()

        loss_reasons_raw = db.execute(
            text("""
                SELECT COALESCE(competitors->>'loss_reason', 'nicht angegeben') AS reason, COUNT(*)
                FROM domain_crm.crm_opportunities
                WHERE tenant_id = :tid AND stage = 'closed_lost' AND is_active = TRUE
                GROUP BY reason
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """),
            {"tid": tenant_id},
        ).fetchall()

        won_c, won_v = (won[0] or 0, float(won[1] or 0)) if won else (0, 0.0)
        lost_c, lost_v = (lost[0] or 0, float(lost[1] or 0)) if lost else (0, 0.0)
        total = won_c + lost_c
        win_rate = round(won_c / total * 100, 1) if total > 0 else 0.0

        return WinLossSummary(
            won_count=won_c, won_value=won_v,
            lost_count=lost_c, lost_value=lost_v,
            win_rate=win_rate,
            loss_reasons=[{"reason": r[0], "count": r[1]} for r in loss_reasons_raw],
        )
    except Exception as e:
        logger.warning("Win-loss report failed: %s", e)
        return WinLossSummary(
            won_count=0, won_value=0, lost_count=0, lost_value=0,
            win_rate=0, loss_reasons=[],
        )


@router.get("/lead-sources", response_model=List[LeadSourceSummary], summary="Lead sources report abrufen")
async def get_lead_sources_report(
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Lead source analysis with conversion rates."""
    try:
        rows = db.execute(
            text("""
                SELECT COALESCE(source, 'unknown') AS src,
                       COUNT(*) AS cnt,
                       SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) AS conv
                FROM crm_leads
                WHERE tenant_id = :tid
                GROUP BY src
                ORDER BY cnt DESC
            """),
            {"tid": tenant_id},
        ).fetchall()
        return [
            LeadSourceSummary(
                source=r[0],
                count=r[1],
                converted_count=r[2],
                conversion_rate=round(r[2] / r[1] * 100, 1) if r[1] > 0 else 0,
            )
            for r in rows
        ]
    except Exception:
        return []
