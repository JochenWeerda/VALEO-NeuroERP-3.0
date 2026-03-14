from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime
import uuid

class IsolationDecision(str, Enum):
    ALLOWED = "allowed"
    VERBUND_ALLOWED = "verbund_allowed"
    DENIED = "denied"

class RessourcentypSharingPolicy(str, Enum):
    """Welche Ressourcentypen duerfen Verbundmitglieder sehen?"""
    FELDBUCH_SCHLAG = "feldbuch_schlag"         # readonly erlaubt
    QUALITAETSPROTOKOLL = "qualitaetsprotokoll"  # readonly erlaubt
    AP_INVOICE = "ap_invoice"                    # niemals
    PAYMENT_RUN = "payment_run"                  # niemals
    JOURNAL_ENTRY = "journal_entry"              # niemals

# Ressourcentypen die Verbundmitglieder (readonly) sehen duerfen
VERBUND_SHARING_ALLOWED: set[str] = {
    RessourcentypSharingPolicy.FELDBUCH_SCHLAG.value,
    RessourcentypSharingPolicy.QUALITAETSPROTOKOLL.value,
}

class CrossTenantAccessAttempt(BaseModel):
    attempt_id: str
    requesting_tenant: str
    resource_tenant: str
    resource_type: str
    decision: IsolationDecision
    timestamp: datetime
    schema_version: int = 1

class IsolationAuditLog(BaseModel):
    """Append-only Log aller Cross-Tenant-Zugriffe."""
    entries: list[CrossTenantAccessAttempt] = []
    schema_version: int = 1

    def append(self, entry: CrossTenantAccessAttempt) -> None:
        self.entries.append(entry)

    def denied_entries(self) -> list[CrossTenantAccessAttempt]:
        return [e for e in self.entries if e.decision == IsolationDecision.DENIED]

    def denied_count(self) -> int:
        return sum(1 for e in self.entries if e.decision == IsolationDecision.DENIED)

class VerbundSharingPolicy(BaseModel):
    """Policy: welche Tenant-IDs bilden einen Verbund und duerfen geteilte Ressourcen sehen."""
    verbund_id: str
    mitglieder_tenant_ids: list[str]
    erlaubte_ressourcentypen: list[str] = list(VERBUND_SHARING_ALLOWED)
    schema_version: int = 1

    def ist_mitglied(self, tenant_id: str) -> bool:
        return tenant_id in self.mitglieder_tenant_ids

    def ressourcentyp_erlaubt(self, ressourcentyp: str) -> bool:
        return ressourcentyp in self.erlaubte_ressourcentypen

class TenantIsolationGuard(BaseModel):
    """Prueft und protokolliert Cross-Tenant-Datenzugriffe."""
    verbund_policies: list[VerbundSharingPolicy] = []
    audit_log: IsolationAuditLog = IsolationAuditLog()
    schema_version: int = 1

    def check(
        self,
        requesting_tenant: str,
        resource_tenant: str,
        resource_type: str,
    ) -> IsolationDecision:
        """Gibt ALLOWED (gleicher Tenant), VERBUND_ALLOWED oder DENIED zurueck."""
        if requesting_tenant == resource_tenant:
            return IsolationDecision.ALLOWED

        # Verbund-Check
        for policy in self.verbund_policies:
            if (policy.ist_mitglied(requesting_tenant)
                    and policy.ist_mitglied(resource_tenant)
                    and policy.ressourcentyp_erlaubt(resource_type)):
                attempt = CrossTenantAccessAttempt(
                    attempt_id=str(uuid.uuid4()),
                    requesting_tenant=requesting_tenant,
                    resource_tenant=resource_tenant,
                    resource_type=resource_type,
                    decision=IsolationDecision.VERBUND_ALLOWED,
                    timestamp=datetime.utcnow(),
                )
                self.audit_log.append(attempt)
                return IsolationDecision.VERBUND_ALLOWED

        # Zugriff verweigert - protokollieren
        attempt = CrossTenantAccessAttempt(
            attempt_id=str(uuid.uuid4()),
            requesting_tenant=requesting_tenant,
            resource_tenant=resource_tenant,
            resource_type=resource_type,
            decision=IsolationDecision.DENIED,
            timestamp=datetime.utcnow(),
        )
        self.audit_log.append(attempt)
        return IsolationDecision.DENIED
