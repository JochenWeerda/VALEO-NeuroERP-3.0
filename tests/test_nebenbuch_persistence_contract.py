"""Exercise the actual finance handlers against one in-memory transactional store."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.auth.deps import get_current_user, get_tenant_id
from app.core.database import get_db
from app.finance.models import NebenbuchAbstimmung
from app.finance.router import router


@pytest.fixture(scope="module")
def store():
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"check_same_thread": False})
    NebenbuchAbstimmung.__table__.create(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def api(store):
    application = FastAPI()
    application.include_router(router)
    with store.connect() as connection:
        transaction = connection.begin()
        # SQLite's legacy driver must begin before SAVEPOINT, or release commits it.
        connection.exec_driver_sql("BEGIN")
        with Session(connection, join_transaction_mode="create_savepoint") as session:
            assert session.execute(select(NebenbuchAbstimmung)).scalars().all() == []
            application.dependency_overrides[get_db] = lambda: session
            application.dependency_overrides[get_current_user] = lambda: {"id": "test-user"}
            application.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
            with TestClient(application) as client:
                yield client, session, application
        transaction.rollback()


@pytest.mark.parametrize("datum,periode", [("2026-01-01", "2026-01"),
                                          ("2026-12-31", "2026-12")])
def test_creation_is_persisted_and_readable_with_complete_response(api, datum, periode):
    client, session, _ = api
    response = client.post("/finance/abstimmung/nebenbuch", json={
        "abstimmungs_datum": datum, "buchungskreis": "DE01"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["periode"] == periode
    assert body["tenant_id"] == "tenant-a"
    assert body["status"] == "OFFEN"
    assert [body[k] for k in ("nebenbuch_saldo", "hauptbuch_saldo", "differenz")] == [0, 0, 0]
    assert body["nicht_abgestimmte"] == []
    session.expire_all()
    saved = session.execute(select(NebenbuchAbstimmung).where(
        NebenbuchAbstimmung.id == body["id"])).scalar_one()
    assert saved.periode == periode
    assert saved.tenant_id == "tenant-a"
    detail = client.get(f'/finance/abstimmung/nebenbuch/{body["id"]}')
    assert detail.status_code == 200
    assert detail.json() == body


def test_other_tenant_cannot_read_or_list_saved_reconciliation(api):
    client, _, application = api
    response = client.post("/finance/abstimmung/nebenbuch", json={
        "abstimmungs_datum": "2026-10-06", "buchungskreis": "DE01"})
    assert response.status_code == 200, response.text
    application.dependency_overrides[get_tenant_id] = lambda: "tenant-b"
    detail = client.get(f'/finance/abstimmung/nebenbuch/{response.json()["id"]}')
    assert detail.status_code == 404
    listed = client.get("/finance/abstimmung/nebenbuch")
    assert listed.status_code == 200
    assert listed.json() == []


def test_missing_record_returns_not_found(api):
    client, _, _ = api
    response = client.get("/finance/abstimmung/nebenbuch/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Abstimmung nicht gefunden"
