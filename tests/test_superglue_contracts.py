from datetime import UTC, datetime

from app.core.config import Settings
from app.integrations.contracts import ExternalResultEnvelope, ExternalResultError, SuperglueToolRecord


def test_superglue_settings_defaults_and_allowlists() -> None:
    settings = Settings(
        SUPERGLUE_ALLOWED_HOSTS="api.superglue.dev, superglue.internal",
        SUPERGLUE_ALLOWED_DOMAINS="superglue.dev,example.com",
    )

    assert settings.SUPERGLUE_ENABLED is False
    assert settings.SUPERGLUE_PROVIDER_KEY == "superglue"
    assert settings.SUPERGLUE_TIMEOUT_SECONDS == 10.0
    assert settings.SUPERGLUE_ALLOWED_HOSTS == ["api.superglue.dev", "superglue.internal"]
    assert settings.SUPERGLUE_ALLOWED_DOMAINS == ["superglue.dev", "example.com"]
    assert settings.SUPERGLUE_ALLOW_LOOPBACK_DEV_EGRESS is False


def test_superglue_tool_record_uses_central_contract_defaults() -> None:
    record = SuperglueToolRecord(
        external_tool_id="sg-tool-1",
        external_tool_version="2026.04",
        valeo_contract_id="partner_adapter.document.fetch",
        display_name="Document Fetch",
        execution_modes=["read", "suggest"],
        target_kind="document",
        auth_model="bearer",
    )

    assert record.provider_key == "superglue"
    assert record.schema_version == 1
    assert record.execution_modes == ["read", "suggest"]


def test_external_result_envelope_serializes_with_stable_fields() -> None:
    started_at = datetime(2026, 4, 3, 9, 30, tzinfo=UTC)
    finished_at = datetime(2026, 4, 3, 9, 31, tzinfo=UTC)
    envelope = ExternalResultEnvelope(
        tenant_id="tenant-a",
        correlation_id="corr-123",
        execution_mode="execute",
        target_kind="external_api",
        result_status="success",
        cost_cents=42,
        started_at=started_at,
        finished_at=finished_at,
        payload={"status": "ok"},
        errors=[ExternalResultError(code="WARN", message="minor warning", retryable=False)],
    )

    data = envelope.model_dump(mode="json")

    assert data["provider_key"] == "superglue"
    assert data["schema_version"] == 1
    assert data["execution_mode"] == "execute"
    assert data["target_kind"] == "external_api"
    assert data["cost_cents"] == 42
    assert data["payload"] == {"status": "ok"}
    assert data["errors"] == [
        {
            "code": "WARN",
            "message": "minor warning",
            "retryable": False,
            "details": {},
        }
    ]
