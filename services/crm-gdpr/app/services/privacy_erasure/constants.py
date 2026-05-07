"""Konstanten für Übergangsaktionen (keine eigenen Decision-Werte)."""

from uuid import UUID

# Übergang: ruft services/deletion_flow.orchestrate_erasure auf
ACTION_LEGACY_HTTP_CRM_ERASURE = "legacy_http_crm_erasure_orchestration"


def erasure_idempotency_key(
    tenant_id: str,
    request_id: UUID,
    decision_id: UUID,
    action: str,
) -> str:
    return f"{tenant_id}:{request_id}:{decision_id}:{action}"
