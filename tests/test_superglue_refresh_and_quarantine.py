from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import external_agent_integrations
from app.integrations.adapters.superglue.tool_sync import build_superglue_sync_history, refresh_superglue_sync_snapshot
from app.integrations.services.superglue_execution_journal import append_execution_journal_entry, build_execution_journal_summary
from app.integrations.services.superglue_quarantine import (
    append_quarantine_entry,
    build_quarantine_summary,
    resolve_quarantine_entry,
    retry_quarantine_entry,
)
from app.integrations.services.superglue_tool_provisioning import provision_superglue_pilot_tools


def test_refresh_superglue_sync_snapshot_persists_file(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_SYNC_STATE_PATH", str(tmp_path / "sync.json"))
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_SYNC_HISTORY_PATH", str(tmp_path / "sync-history.jsonl"))

    result = refresh_superglue_sync_snapshot()

    assert result["provider_key"] == "superglue"
    assert Path(result["storage_path"]).exists()
    history = build_superglue_sync_history()
    assert history["entry_count"] == 1


def test_superglue_quarantine_summary_surfaces_latest(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("app.integrations.services.superglue_quarantine.settings.SUPERGLUE_QUARANTINE_LOG_PATH", str(tmp_path / "quarantine.jsonl"))

    entry = append_quarantine_entry(
        tenant_id="tenant-a",
        tool_id="sg.document.search",
        execution_mode="read",
        outcome="degraded",
        reason="temporary outage",
    )
    summary = build_quarantine_summary()

    assert summary["entry_count"] == 1
    assert summary["latest"]["tool_id"] == "sg.document.search"
    retried = retry_quarantine_entry(entry_id=entry.entry_id, retried_by="tester", note="retry once")
    assert retried["retry_count"] == 1
    resolve_quarantine_entry(entry_id=entry.entry_id, resolved_by="tester", note="reviewed")
    resolved = build_quarantine_summary()
    assert resolved["open_count"] == 0
    assert resolved["resolved_count"] == 1


def test_superglue_execution_journal_summary(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "app.integrations.services.superglue_execution_journal.settings.SUPERGLUE_EXECUTION_JOURNAL_PATH",
        str(tmp_path / "execution-journal.jsonl"),
    )

    append_execution_journal_entry(
        tenant_id="tenant-a",
        correlation_id="corr-1",
        tool_id="sg.document.search",
        execution_mode="read",
        target_kind="document",
        result_status="success",
        started_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
        detail={"provider_key": "superglue"},
    )
    summary = build_execution_journal_summary()
    assert summary["entry_count"] == 1
    assert summary["success_count"] == 1
    assert "average_latency_ms" in summary


def test_external_agent_integrations_surface_refresh_config_and_quarantine(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_SYNC_STATE_PATH", str(tmp_path / "sync.json"))
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_SYNC_HISTORY_PATH", str(tmp_path / "sync-history.jsonl"))
    monkeypatch.setattr("app.integrations.services.superglue_quarantine.settings.SUPERGLUE_QUARANTINE_LOG_PATH", str(tmp_path / "quarantine.jsonl"))
    monkeypatch.setattr(
        "app.integrations.services.superglue_execution_journal.settings.SUPERGLUE_EXECUTION_JOURNAL_PATH",
        str(tmp_path / "execution-journal.jsonl"),
    )
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
    history = client.get("/agent/integrations/providers/superglue/sync-history")
    config = client.get("/agent/integrations/providers/superglue/config-summary")
    quarantine = client.get("/agent/integrations/providers/superglue/quarantine")
    entry_id = quarantine.json()["open_entries"][0]["entry_id"]
    resolve = client.post(f"/agent/integrations/providers/superglue/quarantine/{entry_id}/resolve?resolved_by=tester")
    retry = client.post(f"/agent/integrations/providers/superglue/quarantine/{entry_id}/retry?retried_by=tester")
    journal = client.get("/agent/integrations/providers/superglue/execution-journal")
    monitoring = client.get("/agent/integrations/providers/superglue/monitoring")
    admin_overview = client.get("/agent/integrations/providers/superglue/admin-overview?tenant_id=tenant-a")

    assert refresh.status_code == 200
    assert refresh.json()["provider_key"] == "superglue"
    assert history.status_code == 200
    assert history.json()["entry_count"] == 1
    assert config.status_code == 200
    assert config.json()["provider_key"] == "superglue"
    assert quarantine.status_code == 200
    assert quarantine.json()["entry_count"] == 1
    assert resolve.status_code == 200
    assert resolve.json()["status"] == "resolved"
    assert retry.status_code == 200
    assert journal.status_code == 200
    assert monitoring.status_code == 200
    assert monitoring.json()["provider_key"] == "superglue"
    assert admin_overview.status_code == 200
    assert admin_overview.json()["tenant_id"] == "tenant-a"


def test_provision_superglue_pilot_tools_route(monkeypatch):
    monkeypatch.setattr(
        "app.api.v1.endpoints.external_agent_integrations.provision_superglue_pilot_tools",
        lambda: {"provider_key": "superglue", "tool_count": 3, "tool_ids": ["sg.document.search"]},
    )

    app = FastAPI()
    app.include_router(external_agent_integrations.router)
    client = TestClient(app)

    response = client.post("/agent/integrations/providers/superglue/pilot-tools/provision")

    assert response.status_code == 200
    assert response.json()["provider_key"] == "superglue"


def test_superglue_pilot_smoke_route(monkeypatch):
    monkeypatch.setattr(
        "app.api.v1.endpoints.external_agent_integrations.run_superglue_pilot_smoke",
        lambda: {"provider_key": "superglue", "run_id": "run-smoke", "status": "success"},
    )

    app = FastAPI()
    app.include_router(external_agent_integrations.router)
    client = TestClient(app)

    response = client.post("/agent/integrations/providers/superglue/pilot-tools/smoke-run")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
