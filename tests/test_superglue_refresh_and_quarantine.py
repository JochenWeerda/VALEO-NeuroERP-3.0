from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import external_agent_integrations
from app.integrations.adapters.superglue.tool_sync import refresh_superglue_sync_snapshot
from app.integrations.services.superglue_quarantine import append_quarantine_entry, build_quarantine_summary


def test_refresh_superglue_sync_snapshot_persists_file(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_SYNC_STATE_PATH", str(tmp_path / "sync.json"))

    result = refresh_superglue_sync_snapshot()

    assert result["provider_key"] == "superglue"
    assert Path(result["storage_path"]).exists()


def test_superglue_quarantine_summary_surfaces_latest(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("app.integrations.services.superglue_quarantine.settings.SUPERGLUE_QUARANTINE_LOG_PATH", str(tmp_path / "quarantine.jsonl"))

    append_quarantine_entry(
        tenant_id="tenant-a",
        tool_id="sg.document.search",
        execution_mode="read",
        outcome="degraded",
        reason="temporary outage",
    )
    summary = build_quarantine_summary()

    assert summary["entry_count"] == 1
    assert summary["latest"]["tool_id"] == "sg.document.search"


def test_external_agent_integrations_surface_refresh_config_and_quarantine(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_SYNC_STATE_PATH", str(tmp_path / "sync.json"))
    monkeypatch.setattr("app.integrations.services.superglue_quarantine.settings.SUPERGLUE_QUARANTINE_LOG_PATH", str(tmp_path / "quarantine.jsonl"))
    append_quarantine_entry(
        tenant_id="tenant-a",
        tool_id="sg.partner.adapter.preview",
        execution_mode="simulate",
        outcome="degraded",
        reason="upstream unavailable",
    )

    app = FastAPI()
    app.include_router(external_agent_integrations.router)
    client = TestClient(app)

    refresh = client.post("/agent/integrations/providers/superglue/sync-status/refresh")
    config = client.get("/agent/integrations/providers/superglue/config-summary")
    quarantine = client.get("/agent/integrations/providers/superglue/quarantine")

    assert refresh.status_code == 200
    assert refresh.json()["provider_key"] == "superglue"
    assert config.status_code == 200
    assert config.json()["provider_key"] == "superglue"
    assert quarantine.status_code == 200
    assert quarantine.json()["entry_count"] == 1
