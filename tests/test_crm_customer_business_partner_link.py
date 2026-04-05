from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

from app.integrations.crm_core_client import CRMCoreCustomer
from app.services.customer_sales_eligibility import describe_sales_eligibility
from app.api.v1.schemas.crm import CustomerCreate, CustomerUpdate

customers_endpoint = importlib.import_module("app.api.v1.endpoints.customers")


class _FakeResult:
    def __init__(self, *, scalar_value=None, fetchone_value=None):
        self._scalar_value = scalar_value
        self._fetchone_value = fetchone_value

    def scalar(self):
        return self._scalar_value

    def fetchone(self):
        return self._fetchone_value


class _CapturingDb:
    def __init__(self, results=None):
        self.results = list(results or [])
        self.calls: list[tuple[str, dict]] = []
        self.commits = 0

    def execute(self, statement, params=None):
        self.calls.append((str(statement), dict(params or {})))
        if self.results:
            return self.results.pop(0)
        return _FakeResult()

    def commit(self):
        self.commits += 1


def _core_customer(customer_id: str = "12345678-1234-1234-1234-1234567890ab") -> CRMCoreCustomer:
    return CRMCoreCustomer(
        id=customer_id,
        display_name="Muster Agrar GmbH",
        type="company",
        status="active",
        email="info@example.com",
        phone="+49 123 456",
        industry="agrar",
        region="DE-NI",
        created_at="2026-04-05T12:00:00Z",
        updated_at="2026-04-05T12:00:00Z",
    )


@pytest.mark.asyncio
async def test_create_customer_persists_business_partner_link_for_request_tenant(monkeypatch):
    db = _CapturingDb(
        results=[
            _FakeResult(scalar_value=1),
            _FakeResult(),
            _FakeResult(fetchone_value=SimpleNamespace(chefanweisung=None, business_partner_id="bp-1")),
        ]
    )
    payload = CustomerCreate(
        tenant_id="11111111-1111-1111-1111-111111111111",
        customer_number="DEB-100",
        company_name="Muster Agrar GmbH",
        business_partner_id="bp-1",
        email="info@example.com",
    )
    monkeypatch.setattr(customers_endpoint, "crm_create_customer", lambda body: _async_value(_core_customer()))

    created = await customers_endpoint.create_customer(payload, db=db)

    ensure_statement, ensure_params = db.calls[0]
    insert_statement, insert_params = db.calls[1]
    fetch_statement, fetch_params = db.calls[2]
    assert "FROM domain_crm.business_partners" in ensure_statement
    assert ensure_params == {"pid": "bp-1", "tid": "11111111-1111-1111-1111-111111111111"}
    assert "INSERT INTO domain_crm.customers" in insert_statement
    assert insert_params["tid"] == "11111111-1111-1111-1111-111111111111"
    assert insert_params["bid"] == "bp-1"
    assert "tenant_id = :tid" in fetch_statement
    assert fetch_params == {"cid": "12345678-1234-1234-1234-1234567890ab", "tid": "11111111-1111-1111-1111-111111111111"}
    assert created.business_partner_id == "bp-1"
    assert db.commits == 1


@pytest.mark.asyncio
async def test_update_customer_persists_business_partner_link_for_request_tenant(monkeypatch):
    db = _CapturingDb(
        results=[
            _FakeResult(scalar_value=1),
            _FakeResult(),
            _FakeResult(fetchone_value=SimpleNamespace(chefanweisung=None, business_partner_id="bp-77")),
        ]
    )
    payload = CustomerUpdate(business_partner_id="bp-77", company_name="Muster Agrar GmbH")
    monkeypatch.setattr(
        customers_endpoint,
        "crm_update_customer",
        lambda customer_id, body: _async_value(_core_customer(customer_id)),
    )

    updated = await customers_endpoint.update_customer(
        customer_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        customer_data=payload,
        db=db,
        tenant_id="22222222-2222-2222-2222-222222222222",
    )

    ensure_statement, ensure_params = db.calls[0]
    insert_statement, insert_params = db.calls[1]
    fetch_statement, fetch_params = db.calls[2]
    assert "FROM domain_crm.business_partners" in ensure_statement
    assert ensure_params == {"pid": "bp-77", "tid": "22222222-2222-2222-2222-222222222222"}
    assert "INSERT INTO domain_crm.customers" in insert_statement
    assert insert_params["tid"] == "22222222-2222-2222-2222-222222222222"
    assert insert_params["bid"] == "bp-77"
    assert "tenant_id = :tid" in fetch_statement
    assert fetch_params == {"cid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "tid": "22222222-2222-2222-2222-222222222222"}
    assert updated.business_partner_id == "bp-77"
    assert db.commits == 1


def test_describe_sales_eligibility_reports_delivery_and_invoice_blocks():
    db = _CapturingDb(
        results=[
            _FakeResult(
                fetchone_value=SimpleNamespace(
                    customer_number="DEB-100",
                    business_partner_id="bp-1",
                    bp_id="bp-1",
                    bp_status="active",
                    blocked_for_delivery=True,
                    blocked_for_invoice=True,
                )
            )
        ]
    )

    summary = describe_sales_eligibility(db, "tenant-a", "cust-1")

    assert summary["linked"] is True
    assert summary["partner_id"] == "bp-1"
    assert summary["allowed_order"] is False
    assert summary["allowed_delivery"] is False
    assert summary["allowed_invoice"] is False
    assert "Lieferungen" in " ".join(summary["reasons"])
    assert "Rechnungsstellung" in " ".join(summary["reasons"])


async def _async_value(value):
    return value
