from __future__ import annotations

import pytest

from app.api.v1.endpoints.webhooks import WebhookCreate
from app.core import vies


class _FakeResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text


def test_webhook_create_rejects_private_ip_targets():
    with pytest.raises(ValueError):
        WebhookCreate(url="http://10.0.0.5/hook", event_area="auftrag")


def test_webhook_create_rejects_localhost_targets():
    with pytest.raises(ValueError):
        WebhookCreate(url="http://localhost:8080/hook", event_area="auftrag")


def test_check_vat_vies_escapes_country_and_number(monkeypatch):
    captured: dict[str, str] = {}

    def fake_post(url, data, headers, timeout):
        captured["body"] = data.decode("utf-8")
        return _FakeResponse(
            status_code=200,
            text="""
                <soap:Envelope>
                  <valid>true</valid>
                  <name>Company</name>
                  <address>Main Street</address>
                </soap:Envelope>
            """,
        )

    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setattr(vies, "normalize_vat_number", lambda _vat_id: ("DE", '12<34&56"78'))
    monkeypatch.setattr(vies, "check_vat_format", lambda _vat_id: None)

    result = vies.check_vat_vies("DE123")

    assert result.valid is True
    assert "<urn:vatNumber>12&lt;34&amp;56\"78</urn:vatNumber>" in captured["body"]
