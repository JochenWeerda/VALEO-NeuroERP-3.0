"""
Policy Store Adapter
Bridging legacy policy router to the shared PostgreSQL-backed policy service.
"""

from __future__ import annotations

from typing import List, Optional

from app.services.policy_service import PolicyStore as ServicePolicyStore, Rule as ServiceRule

from .models import Rule

DEFAULT_DB = None  # Retained for backwards compatibility


class PolicyStore:
    """Compatibility wrapper delegating to the shared PolicyService."""

    def __init__(self, _db_path: str | None = None) -> None:  # pragma: no cover - legacy signature
        self._delegate = ServicePolicyStore()

    def list(self) -> List[Rule]:
        return [Rule.model_validate(rule.model_dump()) for rule in self._delegate.list()]

    def get(self, rule_id: str) -> Optional[Rule]:
        rule = self._delegate.get(rule_id)
        return Rule.model_validate(rule.model_dump()) if rule else None

    def upsert(self, rule: Rule) -> None:
        self._delegate.upsert(ServiceRule.model_validate(rule.model_dump()))

    def bulk_upsert(self, rules: List[Rule]) -> None:
        service_rules = [ServiceRule.model_validate(rule.model_dump()) for rule in rules]
        self._delegate.bulk_upsert(service_rules)

    def delete(self, rule_id: str) -> None:
        self._delegate.delete(rule_id)

    def export_json(self) -> str:
        return self._delegate.export_json()

    def restore_json(self, json_str: str) -> None:
        self._delegate.restore_json(json_str)
