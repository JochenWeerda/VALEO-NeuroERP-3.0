"""Loading status, audit and outbox use a single real SQL transaction.

SQLite memory only: no PostgreSQL database/container is created. This does not
claim PostgreSQL acceptance. Parent-scoped tenant isolation is tested below.
"""
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Column, MetaData, String, Table, create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints import tours
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.operations.models import Fahrer, Fahrzeug  # register actual ORM relationships
from app.domains.verladung.models import Tour, TourEvent, TourStop, TourDeliveryNote
from app.infrastructure.eventbus.outbox import OutboxEvent, OutboxPublisher


@pytest.fixture(params=["sqlite", "postgres"])
def db(request):
    if request.param == "postgres":
        import os
        from sqlalchemy.engine import make_url
        raw = os.environ.get("TEST_DATABASE_URL")
        if not raw:
            pytest.skip("Existing shared probe URL required; never create a database")
        url = make_url(raw)
        if "probe" not in (url.database or "") and os.environ.get("CI") != "true":
            pytest.fail("Refusing writes outside configured shared probe")
        engine = create_engine(url)
        with engine.connect() as connection:
            outer = connection.begin()
            with Session(connection, join_transaction_mode="create_savepoint") as session:
                session.add(Tour(id="loading-probe", tour_no="SYNTH-LOADING", date=datetime(2026, 10, 23), status="planned", tenant_id="verified-tenant"))
                session.commit()
                yield session
            outer.rollback()
        engine.dispose()
        return
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False},
                           execution_options={"schema_translate_map": {"domain_log": None, "domain_ops": None}})
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys=ON")
    metadata = MetaData()
    for name in ("ops_fahrer", "ops_fahrzeuge"):
        Table(name, metadata, Column("id", String, primary_key=True), schema="domain_ops")
    for model in (Tour, TourStop, TourDeliveryNote, TourEvent, OutboxEvent):
        model.__table__.to_metadata(metadata)
    metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Tour(id="loading-probe", tour_no="SYNTH-LOADING", date=datetime(2026, 10, 23), status="planned", tenant_id="verified-tenant"))
        session.commit()
        yield session
    engine.dispose()


@pytest.mark.parametrize("operation,event_type,status", [
    ("start_loading", "LOADING_STARTED", "loading"),
    ("finish_loading", "LOADING_FINISHED", "in_transit"),
])
def test_loading_commits_status_actor_log_and_outbox_together(db, monkeypatch, operation, event_type, status):
    mirror = AsyncMock()
    monkeypatch.setattr("app.infrastructure.eventbus.outbox._mirror_workspace_sse", mirror)
    commits = []
    from sqlalchemy import event
    event.listen(db, "after_commit", lambda session: commits.append(True))
    asyncio.run(getattr(tours, operation)("loading-probe", db=db,
                current_user={"sub": "verified-subject", "name": "Synthetic Operator"}, tenant_id="verified-tenant"))
    assert len(commits) == 1
    db.expire_all()
    assert db.get(Tour, "loading-probe").status == status
    log = db.scalars(select(TourEvent)).one()
    outbox = db.scalars(select(OutboxEvent).where(OutboxEvent.aggregate_id.in_(["loading-probe", "other-tour"]))).one()
    assert (log.type, log.user_id, log.user_name) == (event_type, "verified-subject", "Synthetic Operator")
    assert outbox.event_type == event_type and outbox.tenant_id == "verified-tenant"
    assert json.loads(outbox.payload)["payload"]["user_id"] == "verified-subject"
    assert outbox.published is False
    mirror.assert_not_awaited()


@pytest.mark.parametrize("operation", ["start_loading", "finish_loading"])
def test_outbox_failure_rolls_back_status_and_log(db, monkeypatch, operation):
    async def fail(*args, **kwargs):
        raise RuntimeError("synthetic outbox failure")
    monkeypatch.setattr(OutboxPublisher, "store_event", fail)
    with pytest.raises(RuntimeError, match="synthetic outbox failure"):
        asyncio.run(getattr(tours, operation)("loading-probe", db=db,
                    current_user={"sub": "verified-subject"}, tenant_id="verified-tenant"))
    db.expire_all()
    assert db.get(Tour, "loading-probe").status == "planned"
    assert not db.scalars(select(TourEvent)).all()
    assert not db.scalars(select(OutboxEvent).where(OutboxEvent.aggregate_id.in_(["loading-probe", "other-tour"]))).all()


def test_loading_http_ignores_forged_query_actor(db, monkeypatch):
    # Overrides form only the explicit HTTP test boundary, not production auth.
    app = FastAPI()
    for route in tours.router.routes:
        if route.path.endswith("/start-loading"):
            app.add_api_route(route.path, route.endpoint, methods=["POST"])
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: {"sub": "verified-subject", "name": "Synthetic Operator"}
    app.dependency_overrides[get_tenant_id] = lambda: "verified-tenant"
    monkeypatch.setattr("app.infrastructure.eventbus.outbox._mirror_workspace_sse", AsyncMock())
    with TestClient(app) as client:
        response = client.post("/tours/loading-probe/start-loading?user_id=forged&user_name=forged")
    assert response.status_code == 200
    log = db.scalars(select(TourEvent)).one()
    assert log.user_id == "verified-subject" and log.user_name == "Synthetic Operator"


def test_missing_actor_rejected_before_sql(db):
    with pytest.raises(Exception) as caught:
        asyncio.run(tours.start_loading("loading-probe", db=db, current_user={}, tenant_id="verified-tenant"))
    assert caught.value.status_code == 401
    assert db.get(Tour, "loading-probe").status == "planned"
    assert not db.scalars(select(TourEvent)).all()


def seed_other_tenant(db):
    db.add_all([
        Tour(id="other-tour", tour_no="SYNTH-LOADING", date=datetime(2026, 10, 23), status="planned", tenant_id="other-tenant"),
        Tour(id="unassigned-tour", tour_no="UNASSIGNED", date=datetime(2026, 10, 23), status="planned", tenant_id="legacy-unassigned"),
        TourStop(id="own-stop", tour_id="loading-probe", sequence=1),
        TourStop(id="other-stop", tour_id="other-tour", sequence=1),
        TourDeliveryNote(id="own-note", tour_id="loading-probe", stop_id="own-stop", dn_no="DN-OWN"),
        TourDeliveryNote(id="other-note", tour_id="other-tour", stop_id="other-stop", dn_no="DN-OTHER"),
        TourEvent(id="other-event", tour_id="other-tour", type="LOADING_STARTED"),
    ])
    db.commit()


def test_tour_and_child_reads_are_tenant_scoped(db):
    from app.domains.verladung.repository import TourRepository, TourStopRepository, TourDeliveryNoteRepository, TourEventRepository
    seed_other_tenant(db)
    repo = TourRepository(db, "verified-tenant")
    assert [row.id for row in repo.get_all()] == ["loading-probe"]
    assert repo.get_by_id("other-tour") is None
    assert repo.get_by_id("unassigned-tour") is None
    assert repo.get_by_tour_no("SYNTH-LOADING").id == "loading-probe"
    assert TourStopRepository(db, "verified-tenant").get_by_id("other-stop") is None
    assert TourDeliveryNoteRepository(db, "verified-tenant").get_by_dn_no("DN-OTHER") is None
    assert TourEventRepository(db, "verified-tenant").get_all("other-tour") == []
    assert TourEventRepository(db, "verified-tenant").get_by_id("other-event") is None


@pytest.mark.parametrize("operation", ["start_loading", "finish_loading"])
def test_foreign_loading_cannot_mutate_or_emit(db, operation):
    seed_other_tenant(db)
    with pytest.raises(Exception) as error:
        asyncio.run(getattr(tours, operation)("other-tour", db=db,
                    current_user={"sub": "verified-subject"}, tenant_id="verified-tenant"))
    assert error.value.status_code == 404
    assert db.get(Tour, "other-tour").status == "planned"
    assert not db.scalars(select(OutboxEvent).where(OutboxEvent.aggregate_id.in_(["loading-probe", "other-tour"]))).all()


def test_foreign_updates_delete_and_bulk_assignment_are_denied_without_partial_writes(db):
    from app.domains.verladung.repository import TourRepository, TourStopRepository, TourDeliveryNoteRepository
    seed_other_tenant(db)
    assert TourRepository(db, "verified-tenant").update("other-tour", {"notes": "bad"}) is None
    assert not TourRepository(db, "verified-tenant").delete("other-tour")
    assert TourStopRepository(db, "verified-tenant").update("other-stop", {"notes": "bad"}) is None
    assert not TourStopRepository(db, "verified-tenant").delete("other-stop")
    repo = TourDeliveryNoteRepository(db, "verified-tenant")
    for tour_id, stop_id, notes in [
        ("loading-probe", "other-stop", ["own-note"]),
        ("loading-probe", "own-stop", ["own-note", "other-note"]),
    ]:
        with pytest.raises(Exception) as error:
            repo.assign_to_stop(tour_id, stop_id, notes)
        assert error.value.status_code == 404
    db.expire_all()
    assert db.get(TourDeliveryNote, "own-note").status == "ready"
    assert db.get(TourDeliveryNote, "other-note").tour_id == "other-tour"


def test_payload_cannot_override_owner_or_reparent_children(db):
    from app.domains.verladung.repository import TourRepository, TourStopRepository, TourDeliveryNoteRepository
    seed_other_tenant(db)
    for action in [
        lambda: TourRepository(db, "verified-tenant").update("loading-probe", {"tenant_id": "other-tenant"}),
        lambda: TourStopRepository(db, "verified-tenant").update("own-stop", {"tour_id": "other-tour"}),
        lambda: TourStopRepository(db, "verified-tenant").create({"tour_id": "other-tour", "sequence": 2}),
        lambda: TourDeliveryNoteRepository(db, "verified-tenant").create({"tour_id": "loading-probe", "stop_id": "other-stop", "dn_no": "BAD"}),
    ]:
        with pytest.raises(Exception) as error:
            action()
        assert error.value.status_code in (403, 404, 422)
    for tenant in [None, "", " ", "legacy-unassigned"]:
        with pytest.raises(Exception) as error:
            TourRepository(db, tenant)
        assert error.value.status_code == 403


def test_managed_collections_and_audit_cannot_be_overwritten(db):
    from app.domains.verladung.repository import TourRepository
    for payload in [{"events": []}, {"stops": []}, {"created_by": "forged"}, {"updated_by": "forged"}, {"__dict__": {}}]:
        with pytest.raises(Exception) as error:
            TourRepository(db, "verified-tenant").update("loading-probe", payload)
        assert error.value.status_code == 422
    assert db.get(Tour, "loading-probe").tenant_id == "verified-tenant"


def test_same_tour_stop_guaranteed_by_database(db):
    from sqlalchemy.exc import DBAPIError
    seed_other_tenant(db)
    with pytest.raises(DBAPIError, match="FOREIGN KEY constraint failed|violates foreign key constraint"):
        with db.begin_nested():
            db.add(TourDeliveryNote(id="bad-cross-tour", tour_id="other-tour", stop_id="own-stop", dn_no="BAD"))
            db.flush()
    assert db.get(TourDeliveryNote, "bad-cross-tour") is None
    assert db.get(TourDeliveryNote, "other-note").stop_id == "other-stop"


def test_get_tour_builds_dtos_without_mutating_collections(db):
    seed_other_tenant(db)
    result = asyncio.run(tours.get_tour("loading-probe", db=db, tenant_id="verified-tenant"))
    assert result["id"] == "loading-probe"
    assert result["stops"][0]["id"] == "own-stop"
    assert [note.id for note in result["stops"][0]["delivery_notes"]] == ["own-note"]
    assert not db.dirty and not db.deleted


def test_deliver_binds_all_path_ids_before_mutation(db):
    seed_other_tenant(db)
    for tour_id, stop_id, note_id in [
        ("other-tour", "other-stop", "own-note"),
        ("loading-probe", "other-stop", "own-note"),
        ("loading-probe", "own-stop", "other-note"),
    ]:
        with pytest.raises(Exception) as error:
            asyncio.run(tours.mark_delivered(tour_id, stop_id, note_id, db=db, tenant_id="verified-tenant"))
        assert error.value.status_code == 404
    assert db.get(TourDeliveryNote, "own-note").status == "ready"
    assert db.get(TourDeliveryNote, "other-note").status == "ready"
