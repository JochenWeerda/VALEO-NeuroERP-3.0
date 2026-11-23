"""Verification validates the request before checking provider configuration."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import channels


app = FastAPI()
app.include_router(channels.router)
client = TestClient(app)
PATH = "/channels/whatsapp/webhook"
VALID = {"hub.mode": "subscribe", "hub.verify_token": "expected", "hub.challenge": "challenge"}


@pytest.mark.parametrize("params", [
    {},
    {**VALID, "hub.mode": "other"},
    {**VALID, "hub.verify_token": ""},
    {**VALID, "hub.challenge": ""},
])
def test_invalid_request_is_rejected_without_provider_configuration(monkeypatch, params):
    monkeypatch.setattr(channels.settings, "CHANNEL_WHATSAPP_VERIFY_TOKEN", "")
    assert client.get(PATH, params=params).status_code == 400


def test_valid_request_fails_closed_without_configuration(monkeypatch):
    monkeypatch.setattr(channels.settings, "CHANNEL_WHATSAPP_VERIFY_TOKEN", "")
    assert client.get(PATH, params=VALID).status_code == 503


def test_configured_verification_requires_matching_token(monkeypatch):
    monkeypatch.setattr(channels.settings, "CHANNEL_WHATSAPP_VERIFY_TOKEN", "expected")
    assert client.get(PATH, params={**VALID, "hub.verify_token": "wrong"}).status_code == 403
    response = client.get(PATH, params=VALID)
    assert response.status_code == 200
    assert response.text == "challenge"
    assert response.headers["content-type"].startswith("text/plain")
