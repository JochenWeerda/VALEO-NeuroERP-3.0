from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.infrastructure.models import Customer
from app.main import app


client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer dev-token"}
TENANT_ID = "00000000-0000-0000-0000-000000000001"


def _require_customer_table(db) -> None:
    try:
        db.query(Customer).limit(1).all()
    except SQLAlchemyError:
        pytest.skip("DB nicht erreichbar oder domain_crm.customers fehlt.")


PICKER_TEST_IDS = {"cust-picker-api-001", "cust-picker-api-002", "cust-picker-api-003"}


@pytest.fixture
def db():
    session = SessionLocal()
    # Clean up any leftover test rows from previous failed runs
    try:
        session.query(Customer).filter(Customer.id.in_(PICKER_TEST_IDS)).delete(synchronize_session=False)
        session.commit()
    except Exception:
        session.rollback()
    try:
        yield session
    finally:
        try:
            session.query(Customer).filter(Customer.id.in_(PICKER_TEST_IDS)).delete(synchronize_session=False)
            session.commit()
        except Exception:
            session.rollback()
        session.close()


def test_customer_quick_search_returns_picker_payload(db):
    _require_customer_table(db)

    customer = Customer(
        id="cust-picker-api-001",
        tenant_id=TENANT_ID,
        customer_number="CUST-PICK-001",
        company_name="Picker Agrar GmbH",
        address=json.dumps({"postal_code": "26121", "city": "Oldenburg"}),
        is_active=True,
    )
    db.add(customer)
    db.commit()

    response = client.get(
        "/api/v1/crm/customers/quick-search",
        params={"q": "Picker", "limit": 5},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert any(item["id"] == customer.id for item in body)
    match = next(item for item in body if item["id"] == customer.id)
    assert match == {
        "id": customer.id,
        "customer_number": "CUST-PICK-001",
        "company_name": "Picker Agrar GmbH",
        "city": "Oldenburg",
        "postal_code": "26121",
        "is_active": True,
    }
    # Cleanup handled by db fixture teardown


def test_customer_recent_returns_most_recent_active_customers(db):
    _require_customer_table(db)

    old_customer = Customer(
        id="cust-picker-api-002",
        tenant_id=TENANT_ID,
        customer_number="CUST-OLD-002",
        company_name="Alter Kunde",
        address=json.dumps({"postal_code": "20095", "city": "Hamburg"}),
        is_active=True,
    )
    new_customer = Customer(
        id="cust-picker-api-003",
        tenant_id=TENANT_ID,
        customer_number="CUST-NEW-003",
        company_name="Neuer Kunde",
        address=json.dumps({"postal_code": "28195", "city": "Bremen"}),
        is_active=True,
    )
    db.add(old_customer)
    db.add(new_customer)
    db.commit()

    db.execute(
        text(
            """
            UPDATE domain_crm.customers
            SET updated_at = CASE id
                WHEN :old_id THEN :old_updated_at
                WHEN :new_id THEN :new_updated_at
            END
            WHERE id IN (:old_id, :new_id)
            """
        ),
        {
            "old_id": old_customer.id,
            "new_id": new_customer.id,
            "old_updated_at": datetime(2026, 4, 14, 8, 0, tzinfo=UTC),
            "new_updated_at": datetime(2026, 4, 15, 9, 30, tzinfo=UTC),
        },
    )
    db.commit()

    response = client.get(
        "/api/v1/crm/customers/recent",
        params={"limit": 5},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    ids = [item["id"] for item in body]
    assert new_customer.id in ids
    assert old_customer.id in ids
    assert ids.index(new_customer.id) < ids.index(old_customer.id)
    # Cleanup handled by db fixture teardown
