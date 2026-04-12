"""
Tests for Config Service API — Connectors, Reporting Units, Schedules.

Covers Pydantic schema validation (no DB needed) and endpoint structure tests.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.core.config import settings
from main import app
from app.api.v1.endpoints.config_service import (
    ConnectorCreateIn,
    ConnectorUpdateIn,
    ConnectorOut,
    ReportingUnitCreateIn,
    ReportingUnitUpdateIn,
    ScheduleCreateIn,
    ScheduleUpdateIn,
)

client = TestClient(app, raise_server_exceptions=False)
AUTH = {
    "Authorization": f"Bearer {settings.API_DEV_TOKEN or 'dev-token'}",
    "X-Tenant-ID": "test-tenant",
}


def _skip_if_unavailable(resp):
    if resp.status_code in (500, 503):
        body = resp.text
        if any(k in body for k in ("OperationalError", "Connection refused", "UndefinedTable", "does not exist")):
            pytest.skip("DB or tables not available")


# ── Schema Tests ──────────────────────────────────────────────────


class TestConnectorSchemas:
    """Pydantic schema validation for Connector models."""

    def test_connector_create_valid(self):
        c = ConnectorCreateIn(connector_key="sap-erp", connector_type="api")
        assert c.connector_key == "sap-erp"
        assert c.connector_type == "api"
        assert c.is_active is True
        assert c.display_name is None
        assert c.config_json is None

    def test_connector_create_with_all_fields(self):
        c = ConnectorCreateIn(
            connector_key="oauth-provider",
            connector_type="oauth2",
            display_name="OAuth Provider",
            config_json={"client_id": "abc"},
            is_active=False,
        )
        assert c.is_active is False
        assert c.config_json == {"client_id": "abc"}

    def test_connector_create_empty_key_rejected(self):
        with pytest.raises(ValidationError):
            ConnectorCreateIn(connector_key="", connector_type="api")

    def test_connector_create_key_too_long_rejected(self):
        with pytest.raises(ValidationError):
            ConnectorCreateIn(connector_key="x" * 81, connector_type="api")

    def test_connector_create_empty_type_rejected(self):
        with pytest.raises(ValidationError):
            ConnectorCreateIn(connector_key="key1", connector_type="")

    def test_connector_create_type_too_long_rejected(self):
        with pytest.raises(ValidationError):
            ConnectorCreateIn(connector_key="key1", connector_type="t" * 41)

    def test_connector_create_missing_required_fields(self):
        with pytest.raises(ValidationError):
            ConnectorCreateIn()

    def test_connector_update_all_optional(self):
        u = ConnectorUpdateIn()
        assert u.display_name is None
        assert u.config_json is None
        assert u.is_active is None

    def test_connector_update_partial(self):
        u = ConnectorUpdateIn(is_active=False, display_name="Updated")
        assert u.is_active is False
        assert u.display_name == "Updated"


class TestReportingUnitSchemas:
    """Pydantic schema validation for Reporting Unit models."""

    def test_reporting_unit_create_valid(self):
        r = ReportingUnitCreateIn(unit_key="BU-01", display_name="Hauptwerk")
        assert r.unit_key == "BU-01"
        assert r.display_name == "Hauptwerk"
        assert r.is_active is True

    def test_reporting_unit_create_empty_key_rejected(self):
        with pytest.raises(ValidationError):
            ReportingUnitCreateIn(unit_key="", display_name="Test")

    def test_reporting_unit_create_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            ReportingUnitCreateIn(unit_key="BU-01", display_name="")

    def test_reporting_unit_create_missing_fields(self):
        with pytest.raises(ValidationError):
            ReportingUnitCreateIn()


class TestScheduleSchemas:
    """Pydantic schema validation for Schedule models."""

    def test_schedule_create_valid(self):
        s = ScheduleCreateIn(schedule_key="monthly-report", display_name="Monatsbericht")
        assert s.schedule_key == "monthly-report"
        assert s.lead_days == 5
        assert s.use_workday_rule is False
        assert s.is_active is True

    def test_schedule_create_custom_lead_days(self):
        s = ScheduleCreateIn(schedule_key="weekly", display_name="Wochenbericht", lead_days=10)
        assert s.lead_days == 10

    def test_schedule_create_empty_key_rejected(self):
        with pytest.raises(ValidationError):
            ScheduleCreateIn(schedule_key="", display_name="Test")

    def test_schedule_update_all_optional(self):
        u = ScheduleUpdateIn()
        assert u.display_name is None
        assert u.lead_days is None


# ── Endpoint Tests ────────────────────────────────────────────────


class TestConnectorEndpoints:
    """HTTP endpoint tests for /api/v1/config/connectors."""

    def test_list_connectors(self):
        resp = client.get("/api/v1/config/connectors", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_connector_via_put(self):
        payload = {"connector_key": "test-conn-1", "connector_type": "api"}
        resp = client.put("/api/v1/config/connectors", headers=AUTH, json=payload)
        _skip_if_unavailable(resp)
        assert resp.status_code in (200, 201)

    def test_patch_connector_nonexistent(self):
        resp = client.patch(
            "/api/v1/config/connectors/00000000-0000-0000-0000-000000000000",
            headers=AUTH,
            json={"display_name": "Updated"},
        )
        _skip_if_unavailable(resp)
        assert resp.status_code == 404

    def test_delete_connector_nonexistent(self):
        resp = client.delete(
            "/api/v1/config/connectors/00000000-0000-0000-0000-000000000000",
            headers=AUTH,
        )
        _skip_if_unavailable(resp)
        assert resp.status_code == 404

    def test_create_connector_validation_error(self):
        payload = {"connector_key": "", "connector_type": "api"}
        resp = client.put("/api/v1/config/connectors", headers=AUTH, json=payload)
        assert resp.status_code == 422


class TestReportingUnitEndpoints:
    """HTTP endpoint tests for /api/v1/config/reporting-units."""

    def test_list_reporting_units(self):
        resp = client.get("/api/v1/config/reporting-units", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_reporting_unit_via_put(self):
        payload = {"unit_key": "test-unit-1", "display_name": "Testeinheit"}
        resp = client.put("/api/v1/config/reporting-units", headers=AUTH, json=payload)
        _skip_if_unavailable(resp)
        assert resp.status_code in (200, 201)

    def test_create_reporting_unit_validation_error(self):
        resp = client.put(
            "/api/v1/config/reporting-units",
            headers=AUTH,
            json={"unit_key": "x"},
        )
        assert resp.status_code == 422


class TestScheduleEndpoints:
    """HTTP endpoint tests for /api/v1/config/schedules."""

    def test_list_schedules(self):
        resp = client.get("/api/v1/config/schedules", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_schedule_via_put(self):
        payload = {"schedule_key": "test-sched-1", "display_name": "Testplan"}
        resp = client.put("/api/v1/config/schedules", headers=AUTH, json=payload)
        _skip_if_unavailable(resp)
        assert resp.status_code in (200, 201)

    def test_create_schedule_validation_error(self):
        resp = client.put(
            "/api/v1/config/schedules",
            headers=AUTH,
            json={"schedule_key": ""},
        )
        assert resp.status_code == 422
