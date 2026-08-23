"""
Neuro Decision Protocol — NC-D3
Protokolliert den vollstaendigen Entscheidungspfad jeder AI-gesteuerten Aktion.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def record_decision(
    db: Session,
    tenant_id: str,
    intent: str,
    plan_steps: list[dict],
    verification_result: dict,
    confidence_score: float,
    risk_class: str = "low",
    human_approval: Optional[str] = None,
    execution_result: Optional[dict] = None,
    explanation: str = "",
    actor: str = "neuro-core",
) -> dict:
    decision_id = str(uuid4())
    now = datetime.now(timezone.utc)

    try:
        db.execute(text("""
            INSERT INTO domain_shared.neuro_decision_protocol
                (id, tenant_id, intent, plan_steps, verification_result,
                 confidence_score, risk_class, human_approval,
                 execution_result, explanation, actor, created_at)
            VALUES
                (:id, :tid, :intent, :steps, :vresult,
                 :conf, :risk, :approval,
                 :exec_result, :explanation, :actor, :created_at)
        """), {
            "id": decision_id, "tid": tenant_id, "intent": intent,
            "steps": json.dumps(plan_steps), "vresult": json.dumps(verification_result),
            "conf": confidence_score, "risk": risk_class,
            "approval": human_approval,
            "exec_result": json.dumps(execution_result) if execution_result else None,
            "explanation": explanation, "actor": actor, "created_at": now,
        })
        db.commit()
    except Exception as exc:
        logger.warning("Decision protocol write failed (table may not exist): %s", exc)
        db.rollback()
        return {
            "decision_id": decision_id,
            "status": "fallback",
            "error": str(exc),
        }

    return {
        "decision_id": decision_id,
        "intent": intent,
        "confidence_score": confidence_score,
        "risk_class": risk_class,
        "verification_status": verification_result.get("status", "unknown"),
        "created_at": now.isoformat(),
    }


def get_decision(db: Session, decision_id: str, tenant_id: str) -> Optional[dict]:
    try:
        row = db.execute(text("""
            SELECT id, tenant_id, intent, plan_steps, verification_result,
                   confidence_score, risk_class, human_approval,
                   execution_result, explanation, actor, created_at
            FROM domain_shared.neuro_decision_protocol
            WHERE id = :id AND tenant_id = :tid
        """), {"id": decision_id, "tid": tenant_id}).fetchone()

        if not row:
            return None

        return {
            "decision_id": row.id,
            "tenant_id": row.tenant_id,
            "intent": row.intent,
            "plan_steps": json.loads(row.plan_steps) if isinstance(row.plan_steps, str) else row.plan_steps,
            "verification_result": json.loads(row.verification_result) if isinstance(row.verification_result, str) else row.verification_result,
            "confidence_score": float(row.confidence_score) if row.confidence_score else 0.0,
            "risk_class": row.risk_class,
            "human_approval": row.human_approval,
            "execution_result": json.loads(row.execution_result) if isinstance(row.execution_result, str) and row.execution_result else row.execution_result,
            "explanation": row.explanation,
            "actor": row.actor,
            "created_at": str(row.created_at),
        }
    except Exception:
        return None


def list_decisions(
    db: Session, tenant_id: str,
    limit: int = 50,
    risk_class: Optional[str] = None,
) -> list[dict]:
    where = "WHERE tenant_id = :tid"
    params: dict[str, Any] = {"tid": tenant_id, "lim": limit}
    if risk_class:
        where += " AND risk_class = :risk"
        params["risk"] = risk_class

    try:
        rows = db.execute(text(f"""
            SELECT id, intent, confidence_score, risk_class,
                   human_approval, actor, created_at
            FROM domain_shared.neuro_decision_protocol
            {where}
            ORDER BY created_at DESC LIMIT :lim
        """), params).fetchall()  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        return [
            {
                "decision_id": r.id, "intent": r.intent,
                "confidence_score": float(r.confidence_score) if r.confidence_score else 0.0,
                "risk_class": r.risk_class, "human_approval": r.human_approval,
                "actor": r.actor, "created_at": str(r.created_at),
            }
            for r in rows
        ]
    except Exception:
        return []
