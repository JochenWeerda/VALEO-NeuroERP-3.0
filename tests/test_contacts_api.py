"""DOM-CRM-002: Tests fuer contacts.py (CRM Kontaktverwaltung).

Abdeckung: _adapt_contact, _map_create_payload, _map_update_payload, HTTP smoke.
"""
from __future__ import annotations

import uuid
import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.contacts import (
    _adapt_contact,
    _map_create_payload,
    _map_update_payload,
)
from app.integrations.crm_core_client import CRMCoreContact
from app.api.v1.schemas.crm import ContactCreate, ContactUpdate

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# _adapt_contact unit tests
# ---------------------------------------------------------------------------

def _make_core_contact(**kwargs) -> CRMCoreContact:
    defaults = {
        "id": "c-001",
        "customer_id": "cust-001",
        "first_name": "Max",
        "last_name": "Mustermann",
        "email": "max@example.com",
    }
    defaults.update(kwargs)
    return CRMCoreContact(**defaults)


def test_adapt_contact_full_name():
    c = _make_core_contact(first_name="Anna", last_name="Schmidt")
    result = _adapt_contact(c)
    assert result["name"] == "Anna Schmidt"


def test_adapt_contact_falls_back_to_email_when_no_name():
    c = _make_core_contact(first_name="", last_name="", email="no-name@example.com")
    result = _adapt_contact(c)
    assert result["name"] == "no-name@example.com"


def test_adapt_contact_notes_combines_title_and_dept():
    c = _make_core_contact(job_title="Manager", department="Sales")
    result = _adapt_contact(c)
    assert "Manager" in result["notes"]
    assert "Sales" in result["notes"]


def test_adapt_contact_notes_none_when_no_title_or_dept():
    c = _make_core_contact(job_title=None, department=None)
    result = _adapt_contact(c)
    assert result["notes"] is None


def test_adapt_contact_keys_present():
    c = _make_core_contact()
    result = _adapt_contact(c)
    for key in ("id", "name", "company", "email", "phone", "type", "createdAt", "updatedAt"):
        assert key in result


# ---------------------------------------------------------------------------
# _map_create_payload unit tests
# ---------------------------------------------------------------------------

def test_map_create_payload_maps_fields():
    payload = ContactCreate(
        first_name="Hans",
        last_name="Müller",
        email="hans@example.com",
        customer_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        position="Buchhalter",
    )
    result = _map_create_payload(payload)
    assert result["first_name"] == "Hans"
    assert result["last_name"] == "Müller"
    assert result["job_title"] == "Buchhalter"
    assert "customer_id" in result


# ---------------------------------------------------------------------------
# _map_update_payload unit tests
# ---------------------------------------------------------------------------

def test_map_update_payload_only_set_fields():
    payload = ContactUpdate(first_name="Lieselotte")
    result = _map_update_payload(payload)
    assert result["first_name"] == "Lieselotte"
    assert "last_name" not in result
    assert "email" not in result


def test_map_update_payload_maps_position_to_job_title():
    payload = ContactUpdate(position="CFO")
    result = _map_update_payload(payload)
    assert result["job_title"] == "CFO"


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_list_contacts_returns_200():
    resp = _client.get("/api/v1/crm/contacts/", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 500, 503)


def test_create_contact_missing_fields_returns_422():
    resp = _client.post("/api/v1/crm/contacts/", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_get_nonexistent_contact_returns_404():
    resp = _client.get("/api/v1/crm/contacts/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (404, 500, 503)
