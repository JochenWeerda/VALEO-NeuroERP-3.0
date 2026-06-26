"""Tests fuer Qualitaets-Cockpit API (INTEGRATION-EVIDENCE-BOARD-001)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def sample_release_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    payload = {
        "generated_at": "2026-06-26T12:00:00+00:00",
        "overall_status": "pass",
        "summary": {"pass": 5, "warn": 1, "fail": 0},
        "dimensions": [
            {"dimension": "drift", "status": "pass", "detail": "total_drift_items=0"},
            {"dimension": "openapi", "status": "pass", "detail": "openapi.json aktuell"},
        ],
    }
    (artifacts / "release_evidence.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )
    import app.api.v1.endpoints.quality_evidence as qe

    monkeypatch.setattr(qe, "ARTIFACTS", artifacts)
    return payload


@pytest.mark.unit
def test_get_quality_evidence_with_release_artifact(sample_release_evidence: dict) -> None:
    resp = _client.get("/api/v1/admin/quality-evidence/", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_status"] == "pass"
    assert len(body["dimensions"]) == 2
    assert body["source"] == "artifacts/release_evidence.json"
    assert body["summary"]["pass"] == 5


@pytest.mark.unit
def test_get_quality_evidence_missing_artifacts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import app.api.v1.endpoints.quality_evidence as qe

    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(qe, "ARTIFACTS", empty)

    resp = _client.get("/api/v1/admin/quality-evidence/", headers=_HEADERS)
    assert resp.status_code == 503


@pytest.mark.unit
def test_get_drift_status_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import app.api.v1.endpoints.quality_evidence as qe

    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    drift = {
        "generated_at": "2026-06-26T12:00:00+00:00",
        "summary": {"total_drift_items": 0},
    }
    (artifacts / "doc_drift_report.json").write_text(json.dumps(drift), encoding="utf-8")
    monkeypatch.setattr(qe, "ARTIFACTS", artifacts)

    resp = _client.get("/api/v1/admin/quality-evidence/drift", headers=_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["summary"]["total_drift_items"] == 0
