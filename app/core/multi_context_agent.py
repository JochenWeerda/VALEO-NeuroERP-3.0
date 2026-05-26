from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.core.tenant_isolation_guard import IsolationDecision, TenantIsolationGuard


class AgentContextStatus(str, Enum):
    AKTIV = "aktiv"
    ABGELAUFEN = "abgelaufen"
    WIDERRUFEN = "widerrufen"


class AgentContext(BaseModel):
    """Kurzlebiger delegierter Kontext fuer einen KI-Agenten."""

    context_id: str
    agent_id: str
    tenant_id: str
    delegated_roles: list[str]
    context_expires_at: datetime
    erstellt_am: datetime
    status: AgentContextStatus = AgentContextStatus.AKTIV
    schema_version: int = 1

    def ist_aktiv(self, jetzt: Optional[datetime] = None) -> bool:
        if self.status != AgentContextStatus.AKTIV:
            return False
        jetzt = jetzt or datetime.now(timezone.utc)
        return jetzt < self.context_expires_at

    def verbleibende_sekunden(self, jetzt: Optional[datetime] = None) -> float:
        jetzt = jetzt or datetime.now(timezone.utc)
        return max(0.0, (self.context_expires_at - jetzt).total_seconds())

    def widerrufen(self) -> "AgentContext":
        self.status = AgentContextStatus.WIDERRUFEN
        return self


class AgentContextStore(BaseModel):
    """TTL-basierter In-Memory Store fuer aktive Agenten-Kontexte."""

    kontexte: dict[str, AgentContext] = Field(default_factory=dict)
    schema_version: int = 1

    def add(self, context: AgentContext) -> AgentContext:
        self.kontexte[context.context_id] = context
        return context

    def get(self, context_id: str) -> Optional[AgentContext]:
        return self.kontexte.get(context_id)

    def get_active(self, context_id: str, jetzt: Optional[datetime] = None) -> Optional[AgentContext]:
        context = self.kontexte.get(context_id)
        if context is None or not context.ist_aktiv(jetzt):
            return None
        return context

    def widerrufen(self, context_id: str) -> bool:
        context = self.kontexte.get(context_id)
        if context is None:
            return False
        context.widerrufen()
        return True

    def aktive_kontexte(self, tenant_id: str, jetzt: Optional[datetime] = None) -> list[AgentContext]:
        jetzt = jetzt or datetime.now(timezone.utc)
        return [
            context
            for context in self.kontexte.values()
            if context.tenant_id == tenant_id and context.ist_aktiv(jetzt)
        ]

    def bereinige_abgelaufene(self, jetzt: Optional[datetime] = None) -> int:
        jetzt = jetzt or datetime.now(timezone.utc)
        count = 0
        for context in self.kontexte.values():
            if context.status == AgentContextStatus.AKTIV and jetzt >= context.context_expires_at:
                context.status = AgentContextStatus.ABGELAUFEN
                count += 1
        return count


class AgentDispatchResult(BaseModel):
    context_id: str
    command_name: str
    tenant_id: str
    entscheidung: str
    details: Optional[str] = None
    schema_version: int = 1


def tenantbewusst_dispatch(
    context: AgentContext,
    command_name: str,
    resource_tenant_id: str,
    resource_type: str = "agent_command",
    issuer_role: str = "agent",
    jetzt: Optional[datetime] = None,
    isolation_guard: TenantIsolationGuard | None = None,
) -> AgentDispatchResult:
    """Prueft Kontext, Isolation und delegierte Rolle fuer einen Agenten-Dispatch."""

    if not context.ist_aktiv(jetzt):
        return AgentDispatchResult(
            context_id=context.context_id,
            command_name=command_name,
            tenant_id=context.tenant_id,
            entscheidung="DENIED_KONTEXT_ABGELAUFEN",
            details=f"Kontext {context.context_id} ist abgelaufen",
        )

    decision = (
        isolation_guard.check(
            requesting_tenant=context.tenant_id,
            resource_tenant=resource_tenant_id,
            resource_type=resource_type,
        )
        if isolation_guard is not None
        else (
            IsolationDecision.ALLOWED
            if context.tenant_id == resource_tenant_id
            else IsolationDecision.DENIED
        )
    )
    if decision == IsolationDecision.DENIED:
        return AgentDispatchResult(
            context_id=context.context_id,
            command_name=command_name,
            tenant_id=context.tenant_id,
            entscheidung="DENIED_TENANT_ISOLATION",
            details=f"Agent-Tenant {context.tenant_id} darf Ressource {resource_type} von {resource_tenant_id} nicht nutzen",
        )

    if issuer_role not in context.delegated_roles:
        return AgentDispatchResult(
            context_id=context.context_id,
            command_name=command_name,
            tenant_id=context.tenant_id,
            entscheidung="REJECTED",
            details=f"Rolle {issuer_role} nicht in delegated_roles",
        )

    return AgentDispatchResult(
        context_id=context.context_id,
        command_name=command_name,
        tenant_id=context.tenant_id,
        entscheidung="ACCEPTED" if decision == IsolationDecision.ALLOWED else "ACCEPTED_VERBUND",
    )


class MultiContextAgentManifest(BaseModel):
    """Erweitert das Wave-5-AgentCommandManifest um Tenant-Kontext-Einschraenkungen."""

    manifest_id: str
    tenant_id: str
    max_context_ttl_sekunden: int = 3600
    max_aktive_kontexte: int = 5
    erlaubte_command_names: list[str]
    gesperrte_command_names: list[str]
    requires_human_approval_above_eur: float = 10000.0
    schema_version: int = 1
