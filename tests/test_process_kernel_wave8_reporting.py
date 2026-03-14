from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints import reporting_api
from app.core.database import get_db
from app.core.read_model_persistence import ReadModelSnapshot, ReadModelSnapshotStore
from app.core.reporting_layer import (
    build_default_data_products,
    run_report,
    ReportDefinition,
)
from app.infrastructure.models.read_model_snapshots import ReadModelSnapshotRecord


@pytest.fixture()
def sqlite_snapshot_db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ReadModelSnapshotRecord.__table__.create(bind=engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        ReadModelSnapshotRecord.__table__.drop(bind=engine)
        engine.dispose()


@pytest.fixture()
def store(sqlite_snapshot_db: Session) -> ReadModelSnapshotStore:
    return ReadModelSnapshotStore(db_session=sqlite_snapshot_db)


@pytest.fixture()
def client(sqlite_snapshot_db: Session):
    app = FastAPI()
    app.include_router(reporting_api.router, prefix="/api/v1")

    def _override_get_db():
        try:
            yield sqlite_snapshot_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_build_default_data_products_liefert_tenant_scope(store: ReadModelSnapshotStore):
    store.save(ReadModelSnapshot.build("ap-invoice-cockpit", "tenant-a", {"open": 4}))
    store.save(ReadModelSnapshot.build("ap-invoice-cockpit", "tenant-b", {"open": 9}))

    catalog = build_default_data_products(store=store, tenant_id="tenant-a", wirtschaftsjahr="2026")
    products = catalog.get_by_tenant("tenant-a")

    assert len(products) == 3
    assert all(product.tenant_id == "tenant-a" for product in products)
    assert products[0].wirtschaftsjahr == "2026"


def test_build_default_data_products_verknuepft_snapshot_ids(store: ReadModelSnapshotStore):
    snapshot = store.save(ReadModelSnapshot.build("payment-run-cockpit", "tenant-a", {"items": [{"amount": 5}]}))

    catalog = build_default_data_products(store=store, tenant_id="tenant-a")
    product = catalog.get("finance-payment-run-cockpit", "tenant-a")

    assert product is not None
    assert product.snapshot_ids == [snapshot.snapshot_id]


def test_run_report_nutzt_items_liste(store: ReadModelSnapshotStore):
    snapshot = store.save(
        ReadModelSnapshot.build(
            "ap-invoice-cockpit",
            "tenant-a",
            {"items": [{"status": "open", "amount": 10}, {"status": "posted", "amount": 5}]},
        )
    )
    product = build_default_data_products(store, "tenant-a").get("finance-ap-invoice-cockpit", "tenant-a")
    assert product is not None
    assert product.snapshot_ids == [snapshot.snapshot_id]

    result = run_report(
        ReportDefinition(
            report_id="report-open",
            titel="Open invoices",
            datenprodukt_id=product.product_id,
            filter_spec={"status": "open"},
        ),
        product,
        store,
    )

    assert result.total_rows == 1
    assert result.rows[0]["amount"] == 10


def test_run_report_kann_aggregieren(store: ReadModelSnapshotStore):
    store.save(
        ReadModelSnapshot.build(
            "payment-run-cockpit",
            "tenant-a",
            {"items": [{"amount": 10}, {"amount": 15}, {"amount": 1}]},
        )
    )
    product = build_default_data_products(store, "tenant-a").get("finance-payment-run-cockpit", "tenant-a")
    assert product is not None

    result = run_report(
        ReportDefinition(
            report_id="payment-sum",
            titel="Payment sum",
            datenprodukt_id=product.product_id,
            aggregationen=["count", "sum:amount"],
        ),
        product,
        store,
    )

    assert result.total_rows == 1
    assert result.rows[0] == {"count": 3, "sum_amount": 26}


def test_run_report_mit_dict_payload(store: ReadModelSnapshotStore):
    store.save(ReadModelSnapshot.build("process-observation", "tenant-a", {"status": "healthy", "count": 2}))
    product = build_default_data_products(store, "tenant-a").get("finance-process-observation", "tenant-a")
    assert product is not None

    result = run_report(
        ReportDefinition(
            report_id="process-health",
            titel="Process health",
            datenprodukt_id=product.product_id,
        ),
        product,
        store,
    )

    assert result.total_rows == 1
    assert result.rows[0]["status"] == "healthy"


def test_api_data_products_listet_catalog(client: TestClient, store: ReadModelSnapshotStore):
    store.save(ReadModelSnapshot.build("ap-invoice-cockpit", "tenant-a", {"open": 4}))

    response = client.get(
        "/api/v1/reporting/data-products",
        params={"tenant_id": "tenant-a", "requesting_tenant": "tenant-a"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert all(item["tenant_id"] == "tenant-a" for item in data["items"])


def test_api_run_report_filtert_rows(client: TestClient, store: ReadModelSnapshotStore):
    store.save(
        ReadModelSnapshot.build(
            "ap-invoice-cockpit",
            "tenant-a",
            {"items": [{"status": "open", "amount": 10}, {"status": "posted", "amount": 5}]},
        )
    )

    response = client.post(
        "/api/v1/reporting/run",
        json={
            "requesting_tenant": "tenant-a",
            "tenant_id": "tenant-a",
            "report_id": "r1",
            "titel": "Open invoices",
            "datenprodukt_id": "finance-ap-invoice-cockpit",
            "filter_spec": {"status": "open"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 1
    assert data["rows"][0]["amount"] == 10


def test_api_run_report_aggregiert_rows(client: TestClient, store: ReadModelSnapshotStore):
    store.save(
        ReadModelSnapshot.build(
            "payment-run-cockpit",
            "tenant-a",
            {"items": [{"amount": 10}, {"amount": 15}]},
        )
    )

    response = client.post(
        "/api/v1/reporting/run",
        json={
            "requesting_tenant": "tenant-a",
            "tenant_id": "tenant-a",
            "report_id": "r2",
            "titel": "Payment sum",
            "datenprodukt_id": "finance-payment-run-cockpit",
            "aggregationen": ["count", "sum:amount"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["rows"][0] == {"count": 2, "sum_amount": 25}


def test_api_run_report_fuer_unbekanntes_datenprodukt_404(client: TestClient):
    response = client.post(
        "/api/v1/reporting/run",
        json={
            "requesting_tenant": "tenant-a",
            "tenant_id": "tenant-a",
            "report_id": "r3",
            "titel": "Missing",
            "datenprodukt_id": "unknown-product",
        },
    )

    assert response.status_code == 404


def test_catalog_ohne_snapshots_bleibt_stabil(store: ReadModelSnapshotStore):
    catalog = build_default_data_products(store=store, tenant_id="tenant-a")
    product = catalog.get("finance-ap-invoice-cockpit", "tenant-a")

    assert product is not None
    assert product.snapshot_ids == []


def test_api_data_products_cross_tenant_denied(client: TestClient):
    response = client.get(
        "/api/v1/reporting/data-products",
        params={"tenant_id": "tenant-b", "requesting_tenant": "tenant-a"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Tenant isolation denied"


def test_api_run_report_cross_tenant_denied(client: TestClient, store: ReadModelSnapshotStore):
    store.save(
        ReadModelSnapshot.build(
            "ap-invoice-cockpit",
            "tenant-b",
            {"items": [{"status": "open", "amount": 10}]},
        )
    )

    response = client.post(
        "/api/v1/reporting/run",
        json={
            "requesting_tenant": "tenant-a",
            "tenant_id": "tenant-b",
            "report_id": "r4",
            "titel": "Denied",
            "datenprodukt_id": "finance-ap-invoice-cockpit",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Tenant isolation denied"


def test_api_isolation_check_endpoint(client: TestClient):
    response = client.get(
        "/api/v1/reporting/isolation/check",
        params={
            "requesting_tenant": "tenant-a",
            "resource_tenant": "tenant-b",
            "resource_type": "ap_invoice",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "denied"
    assert data["schema_version"] == 1
