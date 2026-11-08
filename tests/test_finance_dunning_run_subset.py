"""Teilmengen-Mahnlauf über rechnungsnrn (FIN-MAHNLAUF-MUTATION-005).

Der Mahnlauf mahnt eine vom Bediener gewählte Teilmenge der fälligen
Posten. Der Endpoint iteriert je Rechnungsnummer über den bestehenden
Service-Vertrag run_dunning(rechnungsnr=...) und aggregiert das Ergebnis.

Wer den Lauf ausführt, sagt die Anmeldung (EIN-MAHNLAUF-20261011): Bis zum
11.10.2026 kam der Bediener aus dem Rumpf ("Portal"), sonst stand "KIM" im Vermerk.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import finance_dunning
from app.auth.deps import get_current_user
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
    # Wie Keycloak: die Kennung ist eine UUID, lesbar ist der Anmeldename.
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "5f0c2a9e-0b7d-4e55-9d0e-1c2a3b4c5d6e", "name": "t.de-vries", "roles": ["FINANCE_BEARBEITEN"]}
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
    # Im Rumpf steht "Portal" — im Vermerk steht, wer angemeldet ist.
    assert _SvcRecorder.calls == [("R-2026-001", "t.de-vries"), ("R-2026-002", "t.de-vries")]


def test_run_dunning_single_traegt_die_anmeldung(monkeypatch):
    _SvcRecorder.calls = []
    client = _client(monkeypatch)

    r = client.post("/api/v1/finance/mahnlauf/run", json={"rechnungsnr": "R-9"})

    assert r.status_code == 200
    assert _SvcRecorder.calls == [("R-9", "t.de-vries")]


def test_leere_auswahl_ist_kein_gesamtlauf(monkeypatch):
    """Eine leere Liste fiel auf den Gesamtlauf zurueck: Wer alles abwaehlte, mahnte alle."""
    _SvcRecorder.calls = []
    client = _client(monkeypatch)

    r = client.post("/api/v1/finance/mahnlauf/run", json={"rechnungsnrn": []})

    assert r.status_code == 200
    assert r.json() == {"ok": True, "erzeugt": 0, "mahnungen": []}
    assert _SvcRecorder.calls == []


def test_ohne_auswahl_laeuft_der_gesamtlauf(monkeypatch):
    _SvcRecorder.calls = []
    client = _client(monkeypatch)

    r = client.post("/api/v1/finance/mahnlauf/run", json={})

    assert r.status_code == 200
    assert _SvcRecorder.calls == [(None, "t.de-vries")]


def test_ohne_anmeldung_kein_mahnlauf(monkeypatch):
    _SvcRecorder.calls = []
    client = _client(monkeypatch)
    client.app.dependency_overrides.pop(get_current_user)

    r = client.post("/api/v1/finance/mahnlauf/run", json={})

    assert r.status_code in (401, 403)
    assert _SvcRecorder.calls == []
