"""Wave 101 — Unit-Tests fuer secrets_vault, whatsapp_agent_service,
whatsapp_notify_service, docflow_followup_service (pure/in-memory domain functions)."""

from __future__ import annotations

import pytest
from datetime import date


# ---------------------------------------------------------------------------
# secrets_vault — in-memory vault lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_check_health_returns_dict() -> None:
    from app.services.secrets_vault import check_health
    result = check_health()
    assert isinstance(result, dict)
    assert "status" in result


@pytest.mark.unit
def test_check_health_status_healthy() -> None:
    from app.services.secrets_vault import check_health
    result = check_health()
    assert result["status"] == "healthy"


@pytest.mark.unit
def test_list_secrets_returns_list() -> None:
    from app.services.secrets_vault import list_secrets
    result = list_secrets()
    assert isinstance(result, list)


@pytest.mark.unit
def test_store_and_get_secret() -> None:
    from app.services.secrets_vault import store_secret, get_secret, SecretType
    store_secret("wave101_api_key", "my-secret-value", SecretType.API_KEY, "wave101 test")
    value = get_secret("wave101_api_key")
    assert value == "my-secret-value"


@pytest.mark.unit
def test_store_secret_returns_metadata() -> None:
    from app.services.secrets_vault import store_secret, SecretType
    meta = store_secret("wave101_db_key", "db-password", SecretType.DATABASE_CREDENTIAL, "db test")
    assert hasattr(meta, "secret_id")
    assert hasattr(meta, "key")
    assert meta.key == "wave101_db_key"


@pytest.mark.unit
def test_get_secret_unknown_key_returns_none() -> None:
    from app.services.secrets_vault import get_secret
    result = get_secret("nonexistent_wave101_key")
    assert result is None


@pytest.mark.unit
def test_get_access_log_returns_list() -> None:
    from app.services.secrets_vault import get_access_log
    result = get_access_log(10)
    assert isinstance(result, list)


@pytest.mark.unit
def test_list_secrets_after_store_has_entry() -> None:
    from app.services.secrets_vault import store_secret, list_secrets, SecretType
    store_secret("wave101_list_test", "value", SecretType.API_KEY, "list test")
    secrets = list_secrets()
    keys = [s.key for s in secrets]
    assert "wave101_list_test" in keys


# ---------------------------------------------------------------------------
# whatsapp_agent_service — conversation state, order log, message processing
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_conversation_state_unknown_returns_none() -> None:
    from app.services.whatsapp_agent_service import get_conversation_state
    result = get_conversation_state("T-UNKNOWN-WAVE101", "+49999000001")
    assert result is None


@pytest.mark.unit
def test_get_order_log_empty_tenant_returns_list() -> None:
    from app.services.whatsapp_agent_service import get_order_log
    result = get_order_log("T-UNKNOWN-WAVE101")
    assert isinstance(result, list)


@pytest.mark.unit
def test_process_whatsapp_message_returns_string() -> None:
    from app.services.whatsapp_agent_service import process_whatsapp_message
    result = process_whatsapp_message("T1", "+49170000001", "Hallo")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.unit
def test_process_whatsapp_message_unknown_phone_has_fallback() -> None:
    from app.services.whatsapp_agent_service import process_whatsapp_message
    result = process_whatsapp_message("T1", "+49000000000", "Ich brauche Hilfe")
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# whatsapp_notify_service — outbox, send_dokument_ready
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_outbox_returns_list() -> None:
    from app.services.whatsapp_notify_service import get_outbox
    result = get_outbox("T-WAVE101")
    assert isinstance(result, list)


@pytest.mark.unit
def test_send_dokument_ready_returns_dict() -> None:
    from app.services.whatsapp_notify_service import send_dokument_ready
    result = send_dokument_ready("T1", "+49170000001", "K-001", "Mustermann", "Rechnung", "INV-WAVE101")
    assert isinstance(result, dict)


@pytest.mark.unit
def test_send_dokument_ready_has_status() -> None:
    from app.services.whatsapp_notify_service import send_dokument_ready
    result = send_dokument_ready("T1", "+49170000001", None, None, "Lieferschein", "LS-001")
    assert "status" in result


@pytest.mark.unit
def test_send_dokument_ready_has_msg_id() -> None:
    from app.services.whatsapp_notify_service import send_dokument_ready
    result = send_dokument_ready("T1", "+49170000002", "K-002", "Bauer", "Kontrakt", "KON-001")
    assert "msg_id" in result


# ---------------------------------------------------------------------------
# docflow_followup_service — followup_overdue (pure date logic)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_followup_overdue_past_date_open_status() -> None:
    from app.services.docflow_followup_service import followup_overdue
    assert followup_overdue(date(2024, 1, 1), "offen", date(2024, 2, 1)) is True


@pytest.mark.unit
def test_followup_overdue_future_date_not_overdue() -> None:
    from app.services.docflow_followup_service import followup_overdue
    assert followup_overdue(date(2025, 1, 1), "offen", date(2024, 2, 1)) is False


@pytest.mark.unit
def test_followup_overdue_none_date_returns_false() -> None:
    from app.services.docflow_followup_service import followup_overdue
    assert followup_overdue(None, "offen", date(2024, 2, 1)) is False


@pytest.mark.unit
def test_followup_overdue_erledigt_status_not_overdue() -> None:
    from app.services.docflow_followup_service import followup_overdue
    assert followup_overdue(date(2024, 1, 1), "erledigt", date(2024, 2, 1)) is False
