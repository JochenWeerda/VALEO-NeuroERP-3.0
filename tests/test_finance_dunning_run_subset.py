"""Teilmengen-Mahnlauf über rechnungsnrn (FIN-MAHNLAUF-MUTATION-005).

Der Portal-Mahnlauf mahnt eine vom Bediener gewählte Teilmenge der fälligen
Posten. Der Endpoint iteriert je Rechnungsnummer über den bestehenden
Service-Vertrag run_dunning(rechnungsnr=...) und aggregiert das Ergebnis.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import finance_dunning
from app.core.database import get_db
from app.core.tenant import get_tenant_id


class _SvcRecorder:
    calls: list[tuple[str | None, str]] = []

    def __init__(self, db, tenant_id):
        pass

    def run_dunning(self, rechnungsnr=None, bediener="KIM"):
        _SvcRecorder.calls.append((rechnungsnr, bediener))
        return {
            "ok": True,
            "erzeugt": 1,
            "mahnungen": [{"rechnungsnr": rechnungsnr, "stufe": 1}],
        }


def _client(monkeypatch) -> TestClient:
    monkeypatch.setattr(finance_dunning, "FinanceDunningService", _SvcRecorder)
    app = FastAPI()
    app.include_router(finance_dunning.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: None
    app.dependency_overrides[get_tenant_id] = lambda: "system"
    return TestClient(app)


def test_run_dunning_subset_iterates_service_per_rechnungsnr(monkeypatch):
    _SvcRecorder.calls = []
    client = _client(monkeypatch)

    r = client.post(
        "/api/v1/finance/mahnlauf/run",
        json={"rechnungsnrn": ["R-2026-001", "R-2026-002"], "bediener": "Portal"},
    )

    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["erzeugt"] == 2
    assert [m["rechnungsnr"] for m in body["mahnungen"]] == ["R-2026-001", "R-2026-002"]
    assert _SvcRecorder.calls == [("R-2026-001", "Portal"), ("R-2026-002", "Portal")]


def test_run_dunning_single_and_default_bediener_unchanged(monkeypatch):
    _SvcRecorder.calls = []
    client = _client(monkeypatch)

    r = client.post("/api/v1/finance/mahnlauf/run", json={"rechnungsnr": "R-9"})

    assert r.status_code == 200
    assert _SvcRecorder.calls == [("R-9", "KIM")]
