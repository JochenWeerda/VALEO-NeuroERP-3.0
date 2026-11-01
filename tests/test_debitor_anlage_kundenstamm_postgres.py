"""Debitor-Anlage landet im fuehrenden Kundenstamm und erscheint in Liste und Detail; alles rollt zurueck."""
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text

from app.api.v1.endpoints import finance_stammdaten
from app.services import customer_service
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """Dedicated probe test owns only rollback-scoped rows."""
    yield


@pytest.fixture
def debitoren(require_db, subject_data, monkeypatch):
    client, db, provider, tenant, foreign, *_ = subject_data
    client.app.include_router(finance_stammdaten.router, prefix="/api/v1")

    async def offline(_payload):
        raise httpx.ConnectError("crm-core im Test nicht erreichbar")

    monkeypatch.setattr(customer_service, "_crm_create", offline)

    def send(method, path, *, selected=tenant, roles=None, **kwargs):
        token = provider.token(selected, changes={"roles": roles or ["FINANCE_BEARBEITEN"],
                                                 "identity_type": "human", "sub": "human-a"})
        return client.request(method, path, headers={"Authorization": "Bearer " + token}, **kwargs)

    return db, send, tenant, foreign


def body(number, **extra):
    return {"debtor_number": number, "company_name": "Synthetischer Hof", "street": "Weg 1",
            "postal_code": "12345", "city": "Ort", "country": "DE", "vat_id": "DE123456789",
            "payment_terms_days": 14, "credit_limit": 5000, **extra}


def test_created_debtor_is_listed_and_opens_in_detail(debitoren):
    db, send, tenant, foreign = debitoren
    number = "DEB-" + uuid4().hex[:12]
    created = send("POST", "/api/v1/finance/debitoren", json=body(number))
    assert created.status_code == 201, created.text
    debitor_id = created.json()["id"]

    listed = send("GET", "/api/v1/finance/debitoren")
    assert listed.status_code == 200, listed.text
    row = next(item for item in listed.json() if item["id"] == debitor_id)
    assert row["debitoren_nr"] == number
    assert row["kreditlimit"] == 5000
    assert row["zahlungsbedingungen"] == "14 Tage"
    assert row["ust_id"] == "DE123456789"

    detail = send("GET", f"/api/v1/finance/debitoren/{debitor_id}")
    assert detail.status_code == 200, detail.text
    assert detail.json()["debitoren_nr"] == number

    # Kein zweiter Stammsatz in der stillgelegten Tabelle.
    assert db.execute(text("SELECT count(*) FROM domain_erp.debitors WHERE debitor_number = :n"),
                      {"n": number}).scalar() == 0
    # Der fremde Mandant sieht den Debitor nicht.
    assert send("GET", f"/api/v1/finance/debitoren/{debitor_id}", selected=foreign).status_code == 404
    assert all(item["id"] != debitor_id for item in send("GET", "/api/v1/finance/debitoren", selected=foreign).json())


def test_legacy_route_uses_the_same_action_and_numbers_are_unique_per_tenant(debitoren):
    _, send, tenant, foreign = debitoren
    number = "DEB-" + uuid4().hex[:12]
    assert send("POST", "/api/v1/finance/debtors/", json=body(number)).status_code == 201
    assert send("POST", "/api/v1/finance/debitoren", json=body(number)).status_code == 409
    # Dieselbe Nummer im anderen Mandanten ist ein eigener Debitor.
    assert send("POST", "/api/v1/finance/debitoren", json=body(number), selected=foreign).status_code == 201


def test_creation_needs_finance_write_role(debitoren):
    _, send, *_ = debitoren
    response = send("POST", "/api/v1/finance/debitoren", json=body("DEB-" + uuid4().hex[:12]), roles=["user"])
    assert response.status_code == 403


def test_crm_core_path_keeps_finance_fields_on_the_local_entry(debitoren, monkeypatch):
    db, send, tenant, _ = debitoren
    core_id = str(uuid4())

    async def online(payload):
        return SimpleNamespace(id=core_id, display_name=payload["display_name"], email=None, phone=None,
                               region=None, industry=None, status="active", notes=None,
                               created_at=None, updated_at=None)

    monkeypatch.setattr(customer_service, "_crm_create", online)
    monkeypatch.setattr(customer_service, "_adapt_customer", lambda core, tid: {"id": core.id})
    monkeypatch.setattr(customer_service.CustomerService, "merge_extensions", lambda self, d: d)
    created = send("POST", "/api/v1/finance/debitoren", json=body("DEB-" + uuid4().hex[:12]))
    assert created.status_code == 201, created.text
    stored = db.execute(text("SELECT credit_limit, payment_terms, tax_id, city FROM domain_crm.customers "
                             "WHERE id = :id AND tenant_id = :t"), {"id": core_id, "t": tenant}).one()
    # payment_terms ist auf der frisch migrierten Datenbank VARCHAR, in der gewachsenen INTEGER.
    assert (float(stored.credit_limit), str(stored.payment_terms), stored.tax_id, stored.city) == \
        (5000.0, "14", "DE123456789", "Ort")
