"""RBAC- und Freigabe-Policies für FiBu-Services."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Set

from pydantic import BaseModel, Field, field_validator

from .models import FiBuPermission, FiBuRole, RoleAssignment


class PermissionDeniedError(RuntimeError):
    """Wird ausgelöst, wenn eine Aktion nicht zulässig ist."""

    def __init__(self, permission: FiBuPermission, message: str | None = None) -> None:
        super().__init__(message or f"Missing permission: {permission.value}")
        self.permission = permission


@dataclass(frozen=True)
class ApprovalRule:
    """Definiert Schwellenwerte für Freigaben."""

    min_amount: Decimal
    currency: str
    required_role: FiBuRole = FiBuRole.FREIGEBER

    def matches(self, amount: Decimal, currency: str) -> bool:
        return amount >= self.min_amount and currency.upper() == self.currency.upper()


class ApprovalPolicyConfig(BaseModel):
    """Konfigurierbare Freigabeparameter aus Settings oder Datenbank."""

    rules: list[ApprovalRule] = Field(default_factory=list)
    default_currency: str = "EUR"

    @field_validator("default_currency")
    @classmethod
    def _upper_currency(cls, value: str) -> str:
        if not value:
            raise ValueError("default_currency darf nicht leer sein.")
        return value.upper()


class FiBuAccessPolicy:
    """Hält Rollen-/Berechtigungsinformation und führt Prüfungen durch."""

    def __init__(self, assignment: RoleAssignment, config: ApprovalPolicyConfig | None = None) -> None:
        self._assignment = assignment
        self._permissions: Set[FiBuPermission] = assignment.permissions()
        self._config = config or ApprovalPolicyConfig()

    @property
    def tenant_id(self) -> str:
        return self._assignment.tenant_id

    @property
    def user_id(self) -> str:
        return self._assignment.user_id

    def has_permission(self, permission: FiBuPermission) -> bool:
        return permission in self._permissions

    def ensure_permission(self, permission: FiBuPermission) -> None:
        if not self.has_permission(permission):
            raise PermissionDeniedError(permission)

    def roles(self) -> Iterable[FiBuRole]:
        return tuple(self._assignment.roles)

    def require_approval(self, amount: Decimal, currency: str | None = None) -> bool:
        """Prüft, ob eine Freigabe erforderlich ist."""
        normalized_currency = (currency or self._config.default_currency).upper()
        for rule in self._config.rules:
            if rule.matches(amount, normalized_currency):
                return not self._has_role(rule.required_role)
        # Keine spezifische Regel getroffen: Sachbearbeiter darf frei entscheiden?
        return FiBuPermission.JOURNAL_APPROVE not in self._permissions and amount > Decimal("0")

    def _has_role(self, role: FiBuRole) -> bool:
        return role in self._assignment.roles


