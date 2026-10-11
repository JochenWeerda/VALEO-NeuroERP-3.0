"""Real preparation functions: no legacy network send, honest state, isolated drafts."""

import httpx
import pytest


@pytest.fixture
def service(monkeypatch):
    from app.services import whatsapp_notify_service
    service = whatsapp_notify_service
    from whatsapp_test_support import attach_unit_store
    attach_unit_store(monkeypatch, service)
    monkeypatch.delenv("WHATSAPP_PHONE_NUMBER_ID", raising=False)
    monkeypatch.delenv("WHATSAPP_ACCESS_TOKEN", raising=False)

    def forbidden(*args, **kwargs):
        pytest.fail("Preparing a browser message must not invoke an HTTP transport")

    monkeypatch.setattr(httpx, "post", forbidden)
    monkeypatch.setattr(httpx.Client, "request", forbidden)
    return service


@pytest.mark.parametrize("kind", ["delivery", "document"])
def test_legacy_credentials_never_trigger_network(service, kind, monkeypatch):
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "obsolete-test-id")
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "obsolete-test-token")
    if kind == "delivery":
        result = service.send_lieferankuendigung("tenant-a", "+491700000001", None, None, "Weizen", 2, "t")
    else:
        result = service.send_dokument_ready("tenant-a", "+491700000001", None, None, "Rechnung", "RE-1")
    assert result["status"] == "pending_browser"
    saved = service.get_outbox("tenant-a")
    assert len(saved) == 1
    assert saved[0]["status"] == "pending_browser"
    assert saved[0]["meta_msg_id"] is None


def test_returned_outbox_cannot_mutate_saved_recipient_or_state(service):
    service.send_dokument_ready("tenant-a", "+491700000001", None, None, "Rechnung", "RE-1")
    returned = service.get_outbox("tenant-a")
    returned[0]["status"] = "sent"
    returned[0]["phone"] = "+491700000002"
    returned.clear()
    actual = service.get_outbox("tenant-a")
    assert len(actual) == 1
    assert actual[0]["phone"] == "+491700000001"
    assert actual[0]["status"] == "pending_browser"


@pytest.mark.parametrize("tenant", [None, "", " ", "\t\n"])
@pytest.mark.parametrize("operation", ["read", "delivery", "document"])
def test_missing_tenant_never_creates_or_reads_global_outbox(service, tenant, operation):
    with pytest.raises(ValueError, match="Mandant"):
        if operation == "read":
            service.get_outbox(tenant)
        elif operation == "delivery":
            service.send_lieferankuendigung(tenant, "+491700000001", None, None, "Weizen", 2, "t")
        else:
            service.send_dokument_ready(tenant, "+491700000001", None, None, "Rechnung", "RE-1")
    assert service._OUTBOX == {}


def test_prepare_logs_do_not_contain_recipient_or_text(service, caplog):
    with caplog.at_level("INFO", logger="whatsapp.notify"):
        result = service.send_dokument_ready("tenant-a", "+491700000001", None, "Privater Kundenname", "Rechnung", "RE-PRIVAT")
    assert result["status"] == "pending_browser"
    assert "+491700000001" not in caplog.text
    assert "Privater Kundenname" not in caplog.text
    assert "RE-PRIVAT" not in caplog.text
