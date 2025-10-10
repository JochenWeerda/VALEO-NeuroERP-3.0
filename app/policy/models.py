"""
Policy Framework Models
Pydantic v2-kompatible Models für Policy-Management
"""

from __future__ import annotations
from typing import Literal, List, Dict, Optional
from pydantic import BaseModel, Field

# Type Aliases
Severity = Literal["ok", "warn", "crit"]
Role = Literal["admin", "manager", "operator"]


class Window(BaseModel):
    """Zeitfenster für Policy-Ausführung"""
    days: List[int] = Field(..., description="0=Sun ... 6=Sat")
    start: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end: str = Field(..., pattern=r"^\d{2}:\d{2}$")


class When(BaseModel):
    """When-Condition für Rule-Matching"""
    kpiId: str
    severity: List[Severity]


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
    params: Optional[Dict[str, object]] = None
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


class DecisionAllow(BaseModel):
    """Policy-Entscheidung: Allow"""
    type: Literal["allow"] = "allow"
    execute: bool
    needsApproval: bool
    approverRoles: Optional[List[Role]] = None
    ruleId: str
    resolvedParams: Dict[str, object]


class DecisionDeny(BaseModel):
    """Policy-Entscheidung: Deny"""
    type: Literal["deny"] = "deny"
    reason: str


# Union Type für Decision
Decision = DecisionAllow | DecisionDeny


class RulesEnvelope(BaseModel):
    """Envelope für Bulk-Import"""
    rules: List[Rule]

