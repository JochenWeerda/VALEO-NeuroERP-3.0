"""Reine Logik-Tests der KIM-Connectoren (ohne DB/Netz).

Deckt E-Mail-Parsing/Richtungserkennung und die STT-Client-Konfiguration ab.
"""

from __future__ import annotations

import pytest

from app.api.v1.endpoints.crm_mail_capture import _parse_raw, _resolve_direction
from app.services.connector_config import (
    ImapConfig,
    SttConfig,
    _split_addresses,
    load_imap_config,
    load_stt_config,
)
from app.services.stt_client import SttClient

pytestmark = pytest.mark.unit


RAW_MAIL = (
    "From: Kunde Mueller <mueller@hof-mueller.de>\r\n"
    "To: crm@valeo.de\r\n"
    "Subject: Futterbestellung KW 24\r\n"
    "Message-ID: <abc-123@hof-mueller.de>\r\n"
    "Content-Type: text/plain; charset=utf-8\r\n"
    "\r\n"
    "Bitte 5t Schweinemastfutter liefern.\r\n"
)


def test_parse_raw_extracts_fields():
    p = _parse_raw(RAW_MAIL)
    assert p["from"] == "mueller@hof-mueller.de"
    assert p["to"] == ["crm@valeo.de"]
    assert p["subject"] == "Futterbestellung KW 24"
    assert "Schweinemastfutter" in p["text"]
    assert p["message_id"] == "abc-123@hof-mueller.de"


def test_resolve_direction_incoming_default():
    direction, peer = _resolve_direction(None, "mueller@hof-mueller.de", ["crm@valeo.de"])
    assert direction == "incoming"
    assert peer == "mueller@hof-mueller.de"


def test_resolve_direction_outgoing_when_own_is_sender():
    direction, _ = _resolve_direction(None, "crm@valeo.de", ["crm@valeo.de"])
    assert direction == "outgoing"


def test_resolve_direction_declared_wins():
    direction, _ = _resolve_direction("outgoing", "mueller@hof-mueller.de", [])
    assert direction == "outgoing"


def test_stt_unconfigured_returns_none(monkeypatch):
    monkeypatch.delenv("STT_BASE_URL", raising=False)
    stt = SttClient(base_url="")
    assert stt.configured is False
    assert stt.transcribe(b"\x00\x01") is None


# ── Connector-Config (per Tenant, ENV-Fallback) ─────────────────────────────
def test_split_addresses_handles_list_and_string():
    assert _split_addresses("a@x.de, b@x.de") == ["a@x.de", "b@x.de"]
    assert _split_addresses(["a@x.de", " ", "b@x.de"]) == ["a@x.de", "b@x.de"]
    assert _split_addresses(None) == []


def test_stt_config_env_fallback(monkeypatch):
    monkeypatch.setenv("STT_BASE_URL", "http://whisper:8000/v1/")
    cfg = SttConfig()
    assert cfg.resolved_base_url() == "http://whisper:8000/v1"  # trailing slash entfernt
    assert cfg.configured is True


def test_stt_config_disabled_not_configured(monkeypatch):
    monkeypatch.setenv("STT_BASE_URL", "http://whisper:8000/v1")
    cfg = SttConfig(enabled=False)
    assert cfg.configured is False


def test_imap_config_requires_host_user():
    assert ImapConfig(enabled=True).configured is False
    assert ImapConfig(enabled=True, host="imap.x.de", user="a@x.de").configured is True
    assert ImapConfig(enabled=False, host="imap.x.de", user="a@x.de").configured is False


def test_imap_config_rejects_command_control_chars():
    cfg = ImapConfig(
        enabled=True,
        host="imap.x.de",
        user="a@x.de",
        password="secret",
        inbox="INBOX\r\nNOOP",
    )

    with pytest.raises(ValueError, match="Steuerzeichen"):
        cfg.validate_command_values()


def test_load_config_without_db_returns_defaults(monkeypatch):
    monkeypatch.delenv("STT_BASE_URL", raising=False)
    monkeypatch.delenv("IMAP_HOST", raising=False)
    assert load_stt_config(None, None).configured is False
    assert load_imap_config(None, None).configured is False
