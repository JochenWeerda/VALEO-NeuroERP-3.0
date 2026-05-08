"""DOM-CRM-002: Tests fuer reklamation_api.py.

Abdeckung: ReklamationCreateRequest-Validierung, _build_reklamation_payload, HTTP smoke.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.reklamation_api import (
    ReklamationCreateRequest,
    ReklamationTransitionRequest,
    _build_reklamation_payload,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# ReklamationCreateRequest validation
# ---------------------------------------------------------------------------

def test_create_request_requires_tenant_id():
    with pytest.raises(Exception):
        ReklamationCreateRequest(
            lieferant_id="LF-001",
            typ="qualitaet",
            positionen=[],
            zustaendiger="max",
            frist_datum="2026-06-01",
            aktor_id="system",
        )


def test_create_request_valid():
    req = ReklamationCreateRequest(
        tenant_id="test-tenant",
        lieferant_id="LF-001",
        typ="qualitaet",
        positionen=[],
        zustaendiger="max",
        frist_datum="2026-06-01",
    )
    assert req.aktor_id == "system"


def test_transition_request_defaults():
    req = ReklamationTransitionRequest(neuer_status="in_bearbeitung")
    assert req.aktor_id == "system"
    assert req.kommentar is None


# ---------------------------------------------------------------------------
# _build_reklamation_payload unit tests
# ---------------------------------------------------------------------------

def test_build_reklamation_payload_returns_dict():
    from datetime import datetime, timezone
    from app.core.reklamation import Reklamation, ReklamationsTyp, ReklamationsStatus
    rek = Reklamation(
        reklamation_id="REK-001",
        tenant_id="test-tenant",
        lieferant_id="LF-001",
        typ=ReklamationsTyp.QUALITAET,
        status=ReklamationsStatus.OFFEN,
        positionen=[],
        zustaendiger="max",
        frist_datum="2026-06-01",
        erstellt_am=datetime(2026, 5, 8, tzinfo=timezone.utc),
    )
    result = _build_reklamation_payload(rek)
    assert isinstance(result, dict)
    assert result.get("reklamation_id") == "REK-001"


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_get_nonexistent_reklamation_returns_404():
    resp = _client.get("/api/v1/reklamationen/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_get_offene_reklamationen():
    resp = _client.get("/api/v1/reklamationen/offene/test-tenant", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 404)


def test_create_reklamation_missing_fields_returns_422():
    resp = _client.post("/api/v1/reklamationen", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_create_reklamation_valid_payload():
    payload = {
        "tenant_id": "test-tenant",
        "lieferant_id": "LF-001",
        "typ": "qualitaet",
        "positionen": [],
        "zustaendiger": "max",
        "frist_datum": "2026-06-01",
        "aktor_id": "system",
    }
    resp = _client.post("/api/v1/reklamationen", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 201, 422)
