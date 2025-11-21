"""Rollen- und Berechtigungsmodelle für die FiBu-Domain."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Set

from pydantic import BaseModel, Field, field_validator


class FiBuRole(str, Enum):
    """Offiziell abgestimmte FiBu-Rollen."""

    SACHBEARBEITER = "sachbearbeiter"
    FREIGEBER = "freigeber"
    STEUERBERATER = "steuerberater"
    ADMIN = "admin"


class FiBuPermission(str, Enum):
    """Atomare Finanzberechtigungen."""

    JOURNAL_CREATE = "journal:create"
    JOURNAL_APPROVE = "journal:approve"
    JOURNAL_READ = "journal:read"
    MASTER_DATA_MANAGE = "master-data:manage"
    MASTER_DATA_READ = "master-data:read"
    OP_MANAGE = "op:manage"
    OP_READ = "op:read"
    EXPORT_FINANCIALS = "export:financials"
    AUDIT_READ = "audit:read"
    SYSTEM_CONFIGURE = "system:configure"


ROLE_PERMISSIONS: Dict[FiBuRole, Set[FiBuPermission]] = {
    FiBuRole.SACHBEARBEITER: {
        FiBuPermission.JOURNAL_CREATE,
        FiBuPermission.JOURNAL_READ,
        FiBuPermission.MASTER_DATA_READ,
        FiBuPermission.OP_READ,
    },
    FiBuRole.FREIGEBER: {
        FiBuPermission.JOURNAL_CREATE,
        FiBuPermission.JOURNAL_APPROVE,
        FiBuPermission.JOURNAL_READ,
        FiBuPermission.MASTER_DATA_READ,
        FiBuPermission.OP_MANAGE,
        FiBuPermission.OP_READ,
    },
    FiBuRole.STEUERBERATER: {
        FiBuPermission.JOURNAL_READ,
        FiBuPermission.MASTER_DATA_READ,
        FiBuPermission.OP_READ,
        FiBuPermission.EXPORT_FINANCIALS,
        FiBuPermission.AUDIT_READ,
    },
    FiBuRole.ADMIN: {
        FiBuPermission.JOURNAL_CREATE,
        FiBuPermission.JOURNAL_APPROVE,
        FiBuPermission.JOURNAL_READ,
        FiBuPermission.MASTER_DATA_MANAGE,
        FiBuPermission.MASTER_DATA_READ,
        FiBuPermission.OP_MANAGE,
        FiBuPermission.OP_READ,
        FiBuPermission.EXPORT_FINANCIALS,
        FiBuPermission.AUDIT_READ,
        FiBuPermission.SYSTEM_CONFIGURE,
    },
}


class RoleAssignment(BaseModel):
    """Verknüpft einen Nutzer mit Rollen und optional delegierten Rechten."""

    tenant_id: str
    user_id: str
    roles: List[FiBuRole] = Field(default_factory=list)
    delegated_permissions: List[FiBuPermission] = Field(default_factory=list)

    @field_validator("tenant_id", "user_id")
    @classmethod
    def _ensure_non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("tenant_id und user_id dürfen nicht leer sein.")
        return value

    def permissions(self) -> Set[FiBuPermission]:
        """Aggregiert alle Berechtigungen aus Rollen & Delegationen."""
        merged: Set[FiBuPermission] = set(self.delegated_permissions)
        for role in self.roles:
            merged.update(ROLE_PERMISSIONS.get(role, set()))
        return merged


class AuthorizationContext(BaseModel):
    """Kontextobjekt, das in FastAPI-Dependencies oder Worker-Jobs genutzt werden kann."""

    tenant_id: str
    user_id: str
    roles: List[FiBuRole]
    permissions: List[FiBuPermission]
    correlation_id: str | None = None

    @classmethod
    def from_assignment(cls, assignment: RoleAssignment, correlation_id: str | None = None) -> "AuthorizationContext":
        perms = sorted(assignment.permissions(), key=lambda perm: perm.value)
        return cls(
            tenant_id=assignment.tenant_id,
            user_id=assignment.user_id,
            roles=list(assignment.roles),
            permissions=perms,
            correlation_id=correlation_id,
        )


