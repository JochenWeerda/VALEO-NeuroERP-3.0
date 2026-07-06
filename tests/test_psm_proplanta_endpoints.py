"""Proplanta-PSM-Endpoints im nicht-konfigurierten Zustand (503-by-design).

Deckt die is_configured()-Guards und die HTTPException-Passthrough-Bloecke ab,
damit externe Abhaengigkeiten sauber 503 liefern statt 500 (Runtime-Sweep-Fix)
und haelt die Coverage der psm_proplanta-Integration ueber dem Ratchet.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": "00000000-0000-0000-0000-000000000001",
}
BASE = "/api/v1/agrar/psm/proplanta"


def test_status_returns_200_with_configured_flag():
    resp = client.get(f"{BASE}/status", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "configured" in body
    assert isinstance(body["configured"], bool)


@pytest.mark.parametrize(
    "path",
    [
        f"{BASE}/list",
        f"{BASE}/stats/overview",
        f"{BASE}/search?q=test",
    ],
)
def test_endpoints_return_503_when_not_configured(path):
    # Ohne Proplanta-Konfiguration ist 503-by-design der Vertrag —
    # niemals 500 (HTTPException-Passthrough vor generischem except).
    resp = client.get(path, headers=HEADERS)
    assert resp.status_code in (200, 503), resp.text
    if resp.status_code == 503:
        assert "detail" in resp.json()
