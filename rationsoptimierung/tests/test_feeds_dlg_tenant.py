"""
DLG-merged tenant: optional dataset loaded from dlg_merged_feeds_lp.csv.

This is opt-in via env var so default tests remain stable.
"""

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_dlg_tenant(monkeypatch):
    monkeypatch.setenv("RATIONS_DLG_MERGED_ENABLE", "1")
    monkeypatch.setenv("RATIONS_DLG_MERGED_TENANT_ID", "dlg")

    # Import after env is set so FeedService picks it up.
    from app.main import app

    api_key = os.getenv("RATIONS_OPTIMIZATION_API_KEY", "dev-api-key-change-in-production")
    return TestClient(app, headers={"X-API-Key": api_key, "X-Tenant-Id": "dlg"})


def test_get_feeds_dlg_tenant_contains_weizen(client_dlg_tenant):
    r = client_dlg_tenant.get("/api/v1/feeds")
    assert r.status_code == 200
    ids = {x["id"] for x in r.json()}
    assert "weizen" in ids

