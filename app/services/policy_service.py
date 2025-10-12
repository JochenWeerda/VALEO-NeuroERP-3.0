"""
Policy Service - Policy-Framework für Alert-Actions
Verwaltung von Policy-Regeln mit PostgreSQL-Persistenz
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Literal

from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.infrastructure.models import PolicyRule

# Types
Severity = Literal["ok", "warn", "crit"]
Role = Literal["admin", "manager", "operator"]


class When(BaseModel):
    """When-Condition für Rule-Matching"""
    kpiId: str
    severity: List[Severity]


class Window(BaseModel):
    """Zeitfenster für Policy-Ausführung"""
    days: List[int] = Field(..., description="Wochentage 0=So..6=Sa")
    start: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end: str = Field(..., pattern=r"^\d{2}:\d{2}$")


class Approval(BaseModel):
    """Approval-Konfiguration (Vier-Augen-Prinzip)"""
    required: bool
    roles: Optional[List[Role]] = None
    bypassIfSeverity: Optional[Severity] = None


class Rule(BaseModel):
    """Policy-Regel"""
    id: str
    when: When
    action: Literal["pricing.adjust", "inventory.reorder", "sales.notify"]
    params: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, float]] = None
    window: Optional[Window] = None
    approval: Optional[Approval] = None
    autoExecute: Optional[bool] = False
    autoSuggest: Optional[bool] = True


class Alert(BaseModel):
    """Alert für Policy-Matching"""
    id: str
    kpiId: str
    title: str
    message: str
    severity: Severity
    delta: Optional[float] = None


class Decision(BaseModel):
    """Policy-Entscheidung"""
    type: Literal["allow", "deny"]
    reason: Optional[str] = None
    execute: Optional[bool] = None
    needsApproval: Optional[bool] = None
    approverRoles: Optional[List[str]] = None
    ruleId: Optional[str] = None
    resolvedParams: Optional[Dict[str, Any]] = None


class PolicyStore:
    """PostgreSQL-basierte Policy-Persistenz."""

    def __init__(self, session_factory: Callable[[], Session] = SessionLocal):
        self._session_factory = session_factory

    # Query operations --------------------------------------------------
    def list(self) -> List[Rule]:
        """Listet alle Policies auf."""
        with self._session_factory() as session:
            rows = session.execute(
                select(PolicyRule).order_by(PolicyRule.id)
            ).scalars().all()
            return [self._to_rule(row) for row in rows]

    def get(self, rule_id: str) -> Optional[Rule]:
        """Holt einzelne Policy."""
        with self._session_factory() as session:
            entity = session.get(PolicyRule, rule_id)
            return self._to_rule(entity) if entity else None

    # Mutation operations -----------------------------------------------
    def upsert(self, rule: Rule) -> None:
        """Erstellt oder aktualisiert eine Policy."""
        with self._session_factory() as session:
            entity = session.get(PolicyRule, rule.id)
            if entity is None:
                entity = PolicyRule(id=rule.id)

            entity.when_kpi_id = rule.when.kpiId
            entity.when_severity = rule.when.severity
            entity.action = rule.action
            entity.params = rule.params
            entity.limits = rule.limits
            entity.window = rule.window.dict() if rule.window else None
            entity.approval = rule.approval.dict() if rule.approval else None
            entity.auto_execute = bool(rule.autoExecute)
            entity.auto_suggest = bool(rule.autoSuggest)

            session.add(entity)
            session.commit()

    def bulk_upsert(self, rules: List[Rule]) -> None:
        """Upsert für mehrere Policies."""
        with self._session_factory() as session:
            for rule in rules:
                entity = session.get(PolicyRule, rule.id) or PolicyRule(id=rule.id)
                entity.when_kpi_id = rule.when.kpiId
                entity.when_severity = rule.when.severity
                entity.action = rule.action
                entity.params = rule.params
                entity.limits = rule.limits
                entity.window = rule.window.dict() if rule.window else None
                entity.approval = rule.approval.dict() if rule.approval else None
                entity.auto_execute = bool(rule.autoExecute)
                entity.auto_suggest = bool(rule.autoSuggest)
                session.add(entity)
            session.commit()

    def delete(self, rule_id: str) -> None:
        """Löscht eine Policy."""
        with self._session_factory() as session:
            session.execute(delete(PolicyRule).where(PolicyRule.id == rule_id))
            session.commit()

    # Import / Export ---------------------------------------------------
    def export_json(self) -> str:
        """Exportiert alle Policies als JSON."""
        rules = self.list()
        return json.dumps({"rules": [r.dict() for r in rules]}, indent=2)

    def restore_json(self, json_str: str) -> None:
        """Importiert Policies aus JSON (ersetzt alle vorhandenen Einträge)."""
        data = json.loads(json_str)
        rules = [Rule(**r) for r in data.get("rules", [])]

        with self._session_factory() as session:
            session.execute(delete(PolicyRule))
            session.commit()

        if rules:
            self.bulk_upsert(rules)

    # Utilities ---------------------------------------------------------
    @staticmethod
    def _to_rule(entity: PolicyRule | None) -> Rule | None:
        if entity is None:
            return None

        return Rule(
            id=entity.id,
            when={"kpiId": entity.when_kpi_id, "severity": entity.when_severity or []},
            action=entity.action,
            params=entity.params,
            limits=entity.limits,
            window=Window(**entity.window) if entity.window else None,
            approval=Approval(**entity.approval) if entity.approval else None,
            autoExecute=entity.auto_execute,
            autoSuggest=entity.auto_suggest,
        )


class PolicyEngine:
    """Policy-Entscheidungs-Engine"""

    @staticmethod
    def within_window(window: Optional[Window], now: Optional[datetime] = None) -> bool:
        """Prüft ob aktuelle Zeit im Zeitfenster liegt"""
        if not window:
            return True

        if now is None:
            now = datetime.now()

        day = now.weekday()  # 0=Mo..6=So
        day_policy = (day + 1) % 7  # Convert zu 0=So..6=Sa
        if day_policy not in window.days:
            return False

        start_h, start_m = map(int, window.start.split(":"))
        end_h, end_m = map(int, window.end.split(":"))
        current_minutes = now.hour * 60 + now.minute
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m

        return start_minutes <= current_minutes <= end_minutes

    @staticmethod
    def resolve_params(rule: Rule, severity: Severity, alert: Optional[Alert] = None) -> Dict[str, Any]:
        """Löst Parameter-Platzhalter auf"""
        params = rule.params or {}
        resolved: Dict[str, Any] = {}

        for key, value in params.items():
            if isinstance(value, dict) and "warn" in value and "crit" in value:
                resolved[key] = value.get(severity, value.get("warn"))
            elif isinstance(value, str) and alert and alert.delta is not None and "{delta}" in value:
                resolved[key] = value.replace("{delta}", str(alert.delta))
            else:
                resolved[key] = value

        return resolved

    @staticmethod
    def decide(user_roles: List[str], alert: Alert, rules: List[Rule]) -> Decision:
        """Policy-Entscheidung treffen"""
        rule = next(
            (r for r in rules if r.when.kpiId == alert.kpiId and alert.severity in r.when.severity),
            None
        )

        if not rule:
            return Decision(type="deny", reason="No matching rule")

        if not PolicyEngine.within_window(rule.window):
            return Decision(type="deny", reason="Outside window")

        params = PolicyEngine.resolve_params(rule, alert.severity, alert)

        needs_approval = False
        if rule.approval and rule.approval.required:
            if not (rule.approval.bypassIfSeverity and alert.severity == rule.approval.bypassIfSeverity):
                needs_approval = True

        approver_roles = rule.approval.roles if rule.approval else None
        role_ok = not needs_approval or any(r in (approver_roles or []) for r in user_roles)
        execute = rule.autoExecute and (not needs_approval or role_ok)

        return Decision(
            type="allow",
            execute=execute,
            needsApproval=needs_approval,
            approverRoles=approver_roles,
            ruleId=rule.id,
            resolvedParams=params
        )
