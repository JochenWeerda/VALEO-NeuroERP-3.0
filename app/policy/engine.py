"""
Policy Engine - Decision Logic
"""

from __future__ import annotations
from typing import List, Dict
from datetime import datetime
from .models import Alert, Decision, DecisionAllow, DecisionDeny, Rule, Role, Severity


def _within_window(window: dict | None, now: datetime | None = None) -> bool:
    """Prüft ob aktuelle Zeit im Zeitfenster liegt"""
    if not window:
        return True
    if now is None:
        now = datetime.now()

    day = now.weekday()  # 0=Mon .. 6=Sun
    days: List[int] = window.get("days", [])

    # Support für beide Konventionen: 0=Mon oder 0=Sun
    if day not in days and (day + 1) % 7 not in days:
        return False

    start = window.get("start", "00:00")
    end = window.get("end", "23:59")
    sh, sm = [int(x) for x in start.split(":")]
    eh, em = [int(x) for x in end.split(":")]
    t = now.hour * 60 + now.minute
    return (sh * 60 + sm) <= t <= (eh * 60 + em)


def _resolve_params(
    rule: Rule, sev: Severity, alert: Alert | None
) -> Dict[str, object]:
    """Löst Parameter-Platzhalter auf"""
    out: Dict[str, object] = {}
    for k, v in (rule.params or {}).items():
        if isinstance(v, dict) and "warn" in v and "crit" in v:
            # Severity-abhängige Werte
            out[k] = v.get(sev, v.get("warn"))
        elif (
            isinstance(v, str)
            and alert
            and ("{delta}" in v)
            and alert.delta is not None
        ):
            # Delta-Platzhalter
            out[k] = v.replace("{delta}", str(alert.delta))
        else:
            out[k] = v
    return out


def decide(user_roles: List[Role], alert: Alert, rules: List[Rule]) -> Decision:
    """
    Policy-Entscheidung treffen

    Args:
        user_roles: Rollen des aktuellen Users
        alert: Alert-Objekt
        rules: Liste aller Policies

    Returns:
        Decision (Allow oder Deny)
    """
    # Matching rule finden
    rule = next(
        (
            r
            for r in rules
            if r.when.kpiId == alert.kpiId and alert.severity in r.when.severity
        ),
        None,
    )

    if not rule:
        return DecisionDeny(type="deny", reason="No matching rule")

    # Zeitfenster prüfen
    if not _within_window(rule.window.model_dump() if rule.window else None):
        return DecisionDeny(type="deny", reason="Outside window")

    # Parameter auflösen
    params = _resolve_params(rule, alert.severity, alert)

    # Approval prüfen
    appr = rule.approval
    needs_approval = bool(
        appr
        and appr.required
        and not (appr.bypassIfSeverity and alert.severity == appr.bypassIfSeverity)
    )
    approver_roles = appr.roles if appr and appr.roles else None

    # Rollen-Check
    role_ok = (not needs_approval) or any(
        r in (approver_roles or []) for r in user_roles
    )
    execute = bool(rule.autoExecute and (not needs_approval or role_ok))

    return DecisionAllow(
        execute=execute,
        needsApproval=needs_approval,
        approverRoles=approver_roles,
        ruleId=rule.id,
        resolvedParams=params,
    )

