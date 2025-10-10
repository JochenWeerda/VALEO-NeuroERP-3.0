"""
Policy Service - Policy-Framework für Alert-Actions
Verwaltung von Policy-Regeln mit SQLite-Persistenz
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field


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
    """SQLite-basierte Policy-Persistenz"""

    def __init__(self, db_path: str = "data/policies.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialisiert Datenbank-Schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS policies (
                    id TEXT PRIMARY KEY,
                    when_kpiId TEXT NOT NULL,
                    when_severity TEXT NOT NULL,
                    action TEXT NOT NULL,
                    params TEXT,
                    limits TEXT,
                    window TEXT,
                    approval TEXT,
                    autoExecute INTEGER,
                    autoSuggest INTEGER
                )
            """)
            conn.commit()

    def list(self) -> List[Rule]:
        """Listet alle Policies auf"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM policies ORDER BY id")
            rows = cursor.fetchall()

            rules = []
            for row in rows:
                rule_dict = {
                    "id": row["id"],
                    "when": {
                        "kpiId": row["when_kpiId"],
                        "severity": json.loads(row["when_severity"])
                    },
                    "action": row["action"],
                    "params": json.loads(row["params"]) if row["params"] else None,
                    "limits": json.loads(row["limits"]) if row["limits"] else None,
                    "window": json.loads(row["window"]) if row["window"] else None,
                    "approval": json.loads(row["approval"]) if row["approval"] else None,
                    "autoExecute": bool(row["autoExecute"]),
                    "autoSuggest": bool(row["autoSuggest"]),
                }
                rules.append(Rule(**rule_dict))

            return rules

    def get(self, rule_id: str) -> Optional[Rule]:
        """Holt einzelne Policy"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM policies WHERE id = ?", (rule_id,))
            row = cursor.fetchone()

            if not row:
                return None

            rule_dict = {
                "id": row["id"],
                "when": {
                    "kpiId": row["when_kpiId"],
                    "severity": json.loads(row["when_severity"])
                },
                "action": row["action"],
                "params": json.loads(row["params"]) if row["params"] else None,
                "limits": json.loads(row["limits"]) if row["limits"] else None,
                "window": json.loads(row["window"]) if row["window"] else None,
                "approval": json.loads(row["approval"]) if row["approval"] else None,
                "autoExecute": bool(row["autoExecute"]),
                "autoSuggest": bool(row["autoSuggest"]),
            }
            return Rule(**rule_dict)

    def upsert(self, rule: Rule):
        """Erstellt oder aktualisiert Policy"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO policies (id, when_kpiId, when_severity, action, params, limits, window, approval, autoExecute, autoSuggest)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    when_kpiId=excluded.when_kpiId,
                    when_severity=excluded.when_severity,
                    action=excluded.action,
                    params=excluded.params,
                    limits=excluded.limits,
                    window=excluded.window,
                    approval=excluded.approval,
                    autoExecute=excluded.autoExecute,
                    autoSuggest=excluded.autoSuggest
            """, (
                rule.id,
                rule.when.kpiId,
                json.dumps(rule.when.severity),
                rule.action,
                json.dumps(rule.params) if rule.params else None,
                json.dumps(rule.limits) if rule.limits else None,
                json.dumps(rule.window.dict()) if rule.window else None,
                json.dumps(rule.approval.dict()) if rule.approval else None,
                1 if rule.autoExecute else 0,
                1 if rule.autoSuggest else 0,
            ))
            conn.commit()

    def bulk_upsert(self, rules: List[Rule]):
        """Bulk-Upsert (transaktional)"""
        with sqlite3.connect(self.db_path) as conn:
            for rule in rules:
                conn.execute("""
                    INSERT INTO policies (id, when_kpiId, when_severity, action, params, limits, window, approval, autoExecute, autoSuggest)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        when_kpiId=excluded.when_kpiId,
                        when_severity=excluded.when_severity,
                        action=excluded.action,
                        params=excluded.params,
                        limits=excluded.limits,
                        window=excluded.window,
                        approval=excluded.approval,
                        autoExecute=excluded.autoExecute,
                        autoSuggest=excluded.autoSuggest
                """, (
                    rule.id,
                    rule.when.kpiId,
                    json.dumps(rule.when.severity),
                    rule.action,
                    json.dumps(rule.params) if rule.params else None,
                    json.dumps(rule.limits) if rule.limits else None,
                    json.dumps(rule.window.dict()) if rule.window else None,
                    json.dumps(rule.approval.dict()) if rule.approval else None,
                    1 if rule.autoExecute else 0,
                    1 if rule.autoSuggest else 0,
                ))
            conn.commit()

    def delete(self, rule_id: str):
        """Löscht Policy"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM policies WHERE id = ?", (rule_id,))
            conn.commit()

    def export_json(self) -> str:
        """Exportiert alle Policies als JSON"""
        rules = self.list()
        return json.dumps({"rules": [r.dict() for r in rules]}, indent=2)

    def restore_json(self, json_str: str):
        """Importiert Policies aus JSON (ersetzt alle!)"""
        data = json.loads(json_str)
        rules = [Rule(**r) for r in data["rules"]]

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM policies")
            conn.commit()

        self.bulk_upsert(rules)


class PolicyEngine:
    """Policy-Entscheidungs-Engine"""

    @staticmethod
    def within_window(window: Optional[Window], now: Optional[datetime] = None) -> bool:
        """Prüft ob aktuelle Zeit im Zeitfenster liegt"""
        if not window:
            return True

        if now is None:
            now = datetime.now()

        # Wochentag prüfen (0=Mo..6=So in datetime vs 0=So..6=Sa in Policy)
        day = now.weekday()  # 0=Mo..6=So
        day_policy = (day + 1) % 7  # Convert zu 0=So..6=Sa
        if day_policy not in window.days:
            return False

        # Zeitfenster prüfen
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
        resolved = {}

        for key, value in params.items():
            if isinstance(value, dict) and "warn" in value and "crit" in value:
                # Severity-abhängige Werte
                resolved[key] = value.get(severity, value.get("warn"))
            elif isinstance(value, str) and alert and alert.delta is not None and "{delta}" in value:
                # Delta-Platzhalter
                resolved[key] = value.replace("{delta}", str(alert.delta))
            else:
                resolved[key] = value

        return resolved

    @staticmethod
    def decide(user_roles: List[str], alert: Alert, rules: List[Rule]) -> Decision:
        """Policy-Entscheidung treffen"""
        # Matching rule finden
        rule = next(
            (r for r in rules if r.when.kpiId == alert.kpiId and alert.severity in r.when.severity),
            None
        )

        if not rule:
            return Decision(type="deny", reason="No matching rule")

        # Zeitfenster prüfen
        if not PolicyEngine.within_window(rule.window):
            return Decision(type="deny", reason="Outside window")

        # Parameter auflösen
        params = PolicyEngine.resolve_params(rule, alert.severity, alert)

        # Approval prüfen
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

