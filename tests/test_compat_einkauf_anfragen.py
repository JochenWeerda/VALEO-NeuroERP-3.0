from app.api.v1.endpoints import compat
from app.core import security
from app.core.config import settings
from fastapi.testclient import TestClient
from main import app


client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
AUTH_HEADERS = {"Authorization": "Bearer jwt-token"}
TENANT_HEADER = {"X-Tenant-ID": "default"}


def _disable_dev_token(monkeypatch) -> None:
    monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
    monkeypatch.setattr(security, "_validate_jwt", lambda token: {"sub": "test-user"})


def test_get_einkauf_anfrage_returns_contract_payload(monkeypatch):
    _disable_dev_token(monkeypatch)
    monkeypatch.setattr(
        compat,
        "_load_einkauf_anfrage",
        lambda db, anfrage_id: {
            "id": anfrage_id,
            "anfrageNummer": "BANF-2026-001",
            "typ": "BANF",
            "anforderer": "Disposition Nord",
            "artikel": "Sommergerste",
            "menge": 24.0,
            "prioritaet": "hoch",
            "status": "FREIGEGEBEN",
            "faelligkeit": "2026-04-10",
            "createdAt": "2026-03-27T10:15:00",
        },
    )

    response = client.get(
        "/api/v1/einkauf/anfragen/req-1",
        headers={**AUTH_HEADERS, **TENANT_HEADER},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "req-1"
    assert payload["anfrageNummer"] == "BANF-2026-001"
    assert payload["artikel"] == "Sommergerste"
    assert payload["menge"] == 24.0


def test_get_einkauf_anfrage_returns_404_when_unknown(monkeypatch):
    _disable_dev_token(monkeypatch)
    monkeypatch.setattr(compat, "_load_einkauf_anfrage", lambda db, anfrage_id: None)

    response = client.get(
        "/api/v1/einkauf/anfragen/unbekannt",
        headers={**AUTH_HEADERS, **TENANT_HEADER},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Anfrage not found"


def test_get_contract_compat_delegates_to_contract_router(monkeypatch):
    _disable_dev_token(monkeypatch)

    async def _fake_get_contract(*, contract_id, db, tenant_id):
        assert contract_id == "kon-1"
        assert tenant_id == "default"
        return {
            "id": contract_id,
            "contractNo": "K-2026-004",
            "supplierId": "SUP-44",
            "commodity": "Rapsschrot",
        }

    monkeypatch.setattr(compat, "get_contract_via_router", _fake_get_contract)

    response = client.get(
        "/api/v1/contracts/kon-1",
        headers={**AUTH_HEADERS, **TENANT_HEADER},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "kon-1"
    assert payload["contractNo"] == "K-2026-004"
    assert payload["commodity"] == "Rapsschrot"
