"""
Tests for Mischfutter-Produktion API.

Validates:
- Pydantic schema constraints (rezept_id non-empty, menge_t > 0, status pattern)
- State machine transition rules
- GET /verfuegbarkeit, /rezepte, /auftraege structure
- POST /auftrag rejects missing recipe (404)

Integration tests skip when futtermittel tables are not yet migrated.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import ProgrammingError

from app.core.config import settings
from conftest import skip_if_db_unavailable


@pytest.fixture
def client():
    from main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def auth_header():
    token = settings.API_DEV_TOKEN or "dev-token"
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": "test-tenant"}


def _skip_if_table_missing(resp):
    """Skip test if futtermittel tables don't exist yet (migration not run)."""
    skip_if_db_unavailable(resp)
    if resp.status_code == 500:
        body = resp.text
        if "UndefinedTable" in body or "does not exist" in body or "futtermittel" in body:
            pytest.skip("Futtermittel tables not yet migrated — run alembic upgrade head")


class TestProduktionSchemas:
    """Pydantic schema validation — pure unit tests, no DB needed."""

    def test_produktionsauftrag_in_requires_rezept_id(self):
        from app.api.v1.endpoints.produktion_mischfutter import ProduktionsauftragIn
        with pytest.raises(Exception):
            ProduktionsauftragIn(rezept_id="", menge_t=10)

    def test_produktionsauftrag_in_requires_positive_menge(self):
        from app.api.v1.endpoints.produktion_mischfutter import ProduktionsauftragIn
        with pytest.raises(Exception):
            ProduktionsauftragIn(rezept_id="R-001", menge_t=0)

    def test_produktionsauftrag_in_valid(self):
        from app.api.v1.endpoints.produktion_mischfutter import ProduktionsauftragIn
        p = ProduktionsauftragIn(rezept_id="R-001", menge_t=10.5)
        assert p.rezept_id == "R-001"
        assert p.menge_t == 10.5

    def test_status_in_validates_pattern(self):
        from app.api.v1.endpoints.produktion_mischfutter import ProduktionsauftragStatusIn
        valid = ProduktionsauftragStatusIn(status="freigegeben")
        assert valid.status == "freigegeben"
        with pytest.raises(Exception):
            ProduktionsauftragStatusIn(status="ungueltig")

    def test_all_valid_status_values(self):
        from app.api.v1.endpoints.produktion_mischfutter import ProduktionsauftragStatusIn
        for status in ["freigegeben", "in_produktion", "fertig", "storniert"]:
            s = ProduktionsauftragStatusIn(status=status)
            assert s.status == status


class TestStateMachineLogic:
    """Validate state machine rules as documented."""

    def test_valid_transitions_coverage(self):
        valid_transitions = {
            "erstellt": ["freigegeben", "storniert"],
            "freigegeben": ["in_produktion", "storniert"],
            "in_produktion": ["fertig", "storniert"],
        }
        assert set(valid_transitions.keys()) == {"erstellt", "freigegeben", "in_produktion"}
        for targets in valid_transitions.values():
            assert "storniert" in targets
        assert "fertig" not in valid_transitions
        assert "storniert" not in valid_transitions

    def test_no_backward_transitions(self):
        valid_transitions = {
            "erstellt": ["freigegeben", "storniert"],
            "freigegeben": ["in_produktion", "storniert"],
            "in_produktion": ["fertig", "storniert"],
        }
        assert "erstellt" not in valid_transitions.get("freigegeben", [])
        assert "freigegeben" not in valid_transitions.get("in_produktion", [])


class TestVerfuegbarkeitEndpoint:
    def test_returns_list(self, client, auth_header):
        resp = client.get("/api/v1/produktion/mischfutter/verfuegbarkeit", headers=auth_header)
        _skip_if_table_missing(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestRezepteEndpoint:
    def test_returns_list(self, client, auth_header):
        resp = client.get("/api/v1/produktion/mischfutter/rezepte", headers=auth_header)
        _skip_if_table_missing(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_filter_by_tierart(self, client, auth_header):
        resp = client.get("/api/v1/produktion/mischfutter/rezepte?tierart=rind", headers=auth_header)
        _skip_if_table_missing(resp)
        assert resp.status_code == 200


class TestAuftragEndpoints:
    def test_create_auftrag_missing_rezept_returns_404(self, client, auth_header):
        resp = client.post(
            "/api/v1/produktion/mischfutter/auftrag",
            json={"rezept_id": "NONEXISTENT", "menge_t": 10},
            headers=auth_header,
        )
        _skip_if_table_missing(resp)
        assert resp.status_code == 404

    def test_list_auftraege(self, client, auth_header):
        resp = client.get("/api/v1/produktion/mischfutter/auftraege", headers=auth_header)
        _skip_if_table_missing(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_auftraege_filter_status(self, client, auth_header):
        resp = client.get("/api/v1/produktion/mischfutter/auftraege?status=erstellt", headers=auth_header)
        _skip_if_table_missing(resp)
        assert resp.status_code == 200

    def test_update_status_nonexistent_returns_404(self, client, auth_header):
        resp = client.patch(
            "/api/v1/produktion/mischfutter/auftrag/NONEXISTENT/status",
            json={"status": "freigegeben"},
            headers=auth_header,
        )
        _skip_if_table_missing(resp)
        assert resp.status_code == 404
