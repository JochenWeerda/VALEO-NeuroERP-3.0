"""DOM-CONTROLLING-004.2 — Budget Lifecycle Service (Statusmaschine)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_BUDGET_TRANSITIONS = {
    ("ENTWURF", "FREIGEGEBEN"),
    ("ENTWURF", "STORNIERT"),
    ("FREIGEGEBEN", "AKTIV"),
    ("FREIGEGEBEN", "STORNIERT"),
    ("AKTIV", "ABGESCHLOSSEN"),
}


class BudgetLifecycleError(Exception):
    """Raised when Budget lifecycle constraints are violated."""


def _fetch_budget(db: Session, budget_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT * FROM domain_controlling.controlling_budgets WHERE id = :id"),
        {"id": budget_id},
    ).mappings().first()
    return dict(row) if row else None


def _log_budget_transition(
    db: Session,
    budget_id: str,
    old_status: str,
    new_status: str,
    tenant_id: str,
    operator: str,
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_controlling.controlling_budget_status_log
                (id, budget_id, tenant_id, old_status, new_status, operator, created_at)
            VALUES (:id, :budget_id, :tenant_id, :old_status, :new_status, :operator, NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "budget_id": budget_id,
            "tenant_id": tenant_id,
            "old_status": old_status,
            "new_status": new_status,
            "operator": operator,
        },
    )


def create_budget(
    db: Session,
    tenant_id: str,
    kostenstelle_id: str,
    periode: str,
    plan_eur: float,
    bezeichnung: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Legt ein neues Budget im Status ENTWURF an."""
    budget_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_controlling.controlling_budgets
                (id, tenant_id, kostenstelle_id, periode, plan_eur, bezeichnung, status, created_at)
            VALUES (:id, :tid, :kst, :periode, :plan_eur, :bez, 'ENTWURF', NOW())
        """),
        {
            "id": budget_id, "tid": tenant_id, "kst": kostenstelle_id,
            "periode": periode, "plan_eur": plan_eur, "bez": bezeichnung,
        },
    )
    _log_budget_transition(db, budget_id, "—", "ENTWURF", tenant_id, operator)
    db.commit()
    logger.info("budget created: %s KST=%s Periode=%s Plan=%.2f EUR", budget_id, kostenstelle_id, periode, plan_eur)
    return {
        "id": budget_id, "kostenstelle_id": kostenstelle_id, "periode": periode,
        "plan_eur": plan_eur, "bezeichnung": bezeichnung, "status": "ENTWURF",
    }


def transition_budget_status(
    db: Session,
    budget_id: str,
    tenant_id: str,
    new_status: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Wechselt Budget-Status (fail-closed Statusmaschine)."""
    budget = _fetch_budget(db, budget_id)
    if not budget:
        raise BudgetLifecycleError(f"Budget {budget_id} nicht gefunden")
    if budget.get("tenant_id") and budget["tenant_id"] != tenant_id:
        raise BudgetLifecycleError(f"Budget {budget_id} gehört nicht zu Tenant {tenant_id}")

    current = (budget.get("status") or "ENTWURF").upper()
    target = new_status.upper()

    # idempotent if already target
    if current == target:
        return {**budget, "idempotent": True}

    if (current, target) not in VALID_BUDGET_TRANSITIONS:
        raise BudgetLifecycleError(
            f"Ungültiger Budget-Übergang {current} → {target}. "
            f"Erlaubt: {sorted(VALID_BUDGET_TRANSITIONS)}"
        )

    if target == "FREIGEGEBEN" and not operator:
        raise BudgetLifecycleError("Freigabe-Operator ist Pflicht")

    extras: Dict[str, Any] = {}
    if target == "FREIGEGEBEN":
        extras["freigabe_operator"] = operator

    set_clauses = "status = :status"
    params: Dict[str, Any] = {"status": target, "id": budget_id}
    if "freigabe_operator" in extras:
        set_clauses += ", freigabe_operator = :freigabe_operator"
        params["freigabe_operator"] = operator

    db.execute(
        # nosec S608 — set_clauses is assembled only from fixed code-controlled fragments; values are parameterized.
        text(f"UPDATE domain_controlling.controlling_budgets SET {set_clauses} WHERE id = :id"),
        params,
    )
    _log_budget_transition(db, budget_id, current, target, tenant_id, operator)
    db.commit()
    logger.info("budget %s: %s → %s von %s", budget_id, current, target, operator)
    return {**budget, "status": target, "previous_status": current, "idempotent": False, **extras}
