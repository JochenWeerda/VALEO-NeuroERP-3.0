"""Wave 51 — Tests fuer modules, crm_contacts_ext, crm_capture_inbox."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# modules  /api/v1/modules
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_list_modules_returns_200() -> None:
    resp = _client.get("/api/v1/meta/modules", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body


@pytest.mark.unit
def test_list_modules_with_tenant_filter() -> None:
    resp = _client.get("/api/v1/meta/modules", params={"tenant_id": "T001"}, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_get_known_module_agrar() -> None:
    resp = _client.get("/api/v1/meta/modules/agrar", headers=_HEADERS)
    # If agrar is registered → 200 with name; if not → 404
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        assert "name" in resp.json()


@pytest.mark.unit
def test_get_unknown_module_returns_404() -> None:
    resp = _client.get("/api/v1/meta/modules/does_not_exist_xyz", headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_get_agrar_contracts_returns_200() -> None:
    resp = _client.get("/api/v1/meta/modules/agrar/contracts", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "event_contracts" in body or "hook_contracts" in body


# ---------------------------------------------------------------------------
# crm_contacts_ext  /api/v1/crm/kim/contacts/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_list_marketing_prefs(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_contacts_ext as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def list_marketing(self, cid): return {"items": [], "contact_id": cid}  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "CrmContactExtService", _FakeSvc)
    resp = _client.get("/api/v1/crm/kim/contacts/CTT-001/marketing-prefs", headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_set_marketing_pref(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_contacts_ext as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def set_marketing(self, cid, cat, pref, **kw):  # noqa: ANN001
            return {"status": "ok", "preference": pref}

    monkeypatch.setattr(ep_mod, "CrmContactExtService", _FakeSvc)
    payload = {"categoryCode": "newsletter", "preference": "company"}
    resp = _client.put("/api/v1/crm/kim/contacts/CTT-001/marketing-prefs", json=payload, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_pseudonymize_contact(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_contacts_ext as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def pseudonymize(self, cid): return {"pseudonymized": True}  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "CrmContactExtService", _FakeSvc)
    resp = _client.post("/api/v1/crm/kim/contacts/CTT-001/pseudonymize", headers=_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["pseudonymized"] is True


# ---------------------------------------------------------------------------
# crm_capture_inbox  /api/v1/crm/kim/capture-inbox
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_list_inbox_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_capture_inbox as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def list(self, status, limit): return []  # noqa: ANN001
        def count_open(self): return 0  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "CrmCaptureInboxService", _FakeSvc)
    resp = _client.get("/api/v1/crm/kim/capture-inbox", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert body["open"] == 0


@pytest.mark.unit
def test_list_inbox_with_status_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_capture_inbox as ep_mod

    received = {}

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def list(self, status, limit):  # noqa: ANN001
            received["status"] = status
            return []
        def count_open(self): return 0  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "CrmCaptureInboxService", _FakeSvc)
    _client.get("/api/v1/crm/kim/capture-inbox", params={"status": "zugeordnet"}, headers=_HEADERS)
    assert received.get("status") == "zugeordnet"


@pytest.mark.unit
def test_assign_inbox_item(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_capture_inbox as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def assign(self, inbox_id, kunden_nr, resolved_by=None):  # noqa: ANN001
            return {"assigned": True, "kunden_nr": kunden_nr}

    monkeypatch.setattr(ep_mod, "CrmCaptureInboxService", _FakeSvc)
    resp = _client.post(
        "/api/v1/crm/kim/capture-inbox/INB-001/assign",
        json={"kundenNr": "KN-123"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["assigned"] is True


@pytest.mark.unit
def test_dismiss_inbox_item(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_capture_inbox as ep_mod

    class _FakeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def dismiss(self, inbox_id, resolved_by=None):  # noqa: ANN001
            return {"dismissed": True}

    monkeypatch.setattr(ep_mod, "CrmCaptureInboxService", _FakeSvc)
    resp = _client.post(
        "/api/v1/crm/kim/capture-inbox/INB-001/dismiss",
        json={},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["dismissed"] is True
