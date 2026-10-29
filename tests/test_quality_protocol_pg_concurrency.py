"""Real two-transaction checks on the shared valeo_probe stand.

Each case inserts and removes only its own synthetic quality protocol.
"""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import os
from threading import Event
from time import sleep
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.infrastructure.models import QualityProtocol
from modules.agrar.repositories.quality_protocol_repo import AcceptanceNotOwnedError, QualityProtocolRepositoryImpl
from modules.agrar.services.quality_protocol_service import QualityProtocol as ServiceQualityProtocol, QualityProtocolUpdate


pytestmark = pytest.mark.integration

@pytest.fixture(autouse=True)
def declared_test_database_only():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        if os.environ.get("PYTEST_REQUIRE_DB_STRICT") == "1":
            pytest.fail("Explicit TEST_DATABASE_URL required")
        pytest.skip("PostgreSQL integration requires an explicitly declared test database")
    selected = make_url(url)
    effective = os.environ.get("DATABASE_URL")
    assert effective and make_url(effective) == selected, "Test connection must match application connection"
    if os.environ.get("CI", "").lower() != "true":
        assert selected.database == "valeo_probe", "Local tests reuse the shared probe only"

@contextmanager
def own_protocol():
    url = os.environ.get("TEST_DATABASE_URL")
    assert url
    engine = create_engine(url, pool_pre_ping=True)
    protocol_id = f"qp_aw05_{uuid4().hex}"
    with Session(engine) as db:
        tenant_id = db.execute(text("SELECT id FROM domain_shared.tenants ORDER BY id LIMIT 1")).scalar_one()
        db.execute(text("""
            INSERT INTO domain_inventory.quality_protocols
                (id, tenant_id, protocol_number, version, is_final)
            VALUES (:id, :tenant, :number, 1, false)
        """), {"id": protocol_id, "tenant": tenant_id, "number": f"AW05-{uuid4().hex[:12]}"})
        db.commit()
    try:
        yield engine, tenant_id, protocol_id
    finally:
        with Session(engine) as db:
            db.execute(text("""
                DELETE FROM domain_inventory.quality_protocols
                WHERE id = :id AND tenant_id = :tenant
            """), {"id": protocol_id, "tenant": tenant_id})
            db.commit()
        engine.dispose()


@pytest.mark.parametrize("second_action", ["finalize", "update"])
def test_second_transaction_cannot_change_protocol_after_finalization(second_action):
    with own_protocol() as (engine, tenant_id, protocol_id):
        preloaded = Event()

        def second_transaction():
            with Session(engine) as db:
                # Load stale state into this session before the first transaction commits.
                row = db.query(QualityProtocol).filter_by(id=protocol_id, tenant_id=tenant_id).one()
                assert row.is_final is False
                preloaded.set()
                repo = QualityProtocolRepositoryImpl(db, tenant_id)
                try:
                    if second_action == "finalize":
                        repo.finalize(protocol_id, "second-actor")
                    else:
                        repo.update(protocol_id, QualityProtocolUpdate(moisture_pct=12))
                except ValueError as exc:
                    db.rollback()
                    return str(exc)
                raise AssertionError("Second transaction changed a finalized protocol")

        with Session(engine) as first_db, ThreadPoolExecutor(max_workers=1) as pool:
            first_repo = QualityProtocolRepositoryImpl(first_db, tenant_id)
            first_repo.finalize(protocol_id, "first-actor")
            future = pool.submit(second_transaction)
            assert preloaded.wait(timeout=5)
            sleep(0.2)
            first_db.commit()
            outcome = future.result(timeout=10)

        assert "finalized" in outcome
        with Session(engine) as db:
            row = db.query(QualityProtocol).filter_by(id=protocol_id, tenant_id=tenant_id).one()
            assert row.is_final is True
            assert row.approved_by == "first-actor"
            assert row.moisture_pct is None


def test_foreign_tenant_cannot_read_or_finalize_protocol():
    with own_protocol() as (engine, tenant_id, protocol_id):
        with Session(engine) as db:
            repo = QualityProtocolRepositoryImpl(db, f"{tenant_id}-foreign")
            assert repo.get_by_id(protocol_id) is None
            with pytest.raises(ValueError, match="not found"):
                repo.finalize(protocol_id, "foreign-actor")
            db.rollback()
        with Session(engine) as db:
            row = db.query(QualityProtocol).filter_by(id=protocol_id, tenant_id=tenant_id).one()
            assert row.is_final is False


def test_create_rejects_foreign_acceptance_before_insert():
    url = os.environ.get("TEST_DATABASE_URL")
    assert url
    engine = create_engine(url, pool_pre_ping=True)
    acceptance_id = f"aw02_{uuid4().hex}"
    protocol_id = f"qp_aw02_{uuid4().hex}"
    with Session(engine) as db:
        own_tenant, customer_id = db.execute(text("""
            SELECT c.tenant_id, c.id FROM domain_crm.customers c
            JOIN domain_shared.tenants t ON t.id = c.tenant_id
            ORDER BY c.id LIMIT 1
        """)).one()
        db.execute(text("""
            INSERT INTO domain_inventory.harvest_acceptances
                (id, acceptance_number, tenant_id, delivery_date, operator_id, customer_id,
                 is_sustainable_biomass, release_status, pricing_mode,
                 print_remarks_on_acceptance_note, print_remarks_on_settlement)
            VALUES (:id, :number, :tenant, CURRENT_DATE, 'aw02-probe', :customer,
                    false, 'draft', 'spot_daily', false, false)
        """), {"id": acceptance_id, "number": f"AW02-{uuid4().hex[:12]}",
               "tenant": own_tenant, "customer": customer_id})
        db.commit()
    try:
        foreign_tenant = f"{own_tenant}-foreign"
        with Session(engine) as db:
            repo = QualityProtocolRepositoryImpl(db, foreign_tenant)
            with pytest.raises(AcceptanceNotOwnedError):
                repo.ensure_acceptance_owned(acceptance_id, lock=True)
            with pytest.raises(AcceptanceNotOwnedError):
                repo.create(ServiceQualityProtocol(
                    id=protocol_id, tenant_id=foreign_tenant,
                    harvest_acceptance_id=acceptance_id, protocol_number="AW02-FOREIGN", version=1,
                ))
            db.rollback()
        with Session(engine) as db:
            assert db.execute(text("SELECT COUNT(*) FROM domain_inventory.quality_protocols WHERE id=:id"),
                              {"id": protocol_id}).scalar_one() == 0
    finally:
        with Session(engine) as db:
            db.execute(text("""
                DELETE FROM domain_inventory.harvest_acceptances
                WHERE id=:id AND tenant_id=:tenant
            """), {"id": acceptance_id, "tenant": own_tenant})
            db.commit()
        engine.dispose()


def test_finalization_and_completion_event_roll_back_together():
    import asyncio
    from datetime import datetime
    from app.domains.shared.events import IntegrationEvent
    from app.infrastructure.eventbus.outbox import OutboxEvent, OutboxPublisher
    with own_protocol() as (engine, tenant_id, protocol_id):
        event_id = f"aw03-{uuid4().hex}"
        with Session(engine) as db:
            repo = QualityProtocolRepositoryImpl(db, tenant_id)
            repo.finalize(protocol_id, "synthetic-actor")
            asyncio.run(OutboxPublisher(db, None).store_event(IntegrationEvent(
                aggregate_id=protocol_id, timestamp=datetime.utcnow(), event_id=event_id,
                event_type="agrar.quality_protocol.completed", tenant_id=tenant_id,
                payload={"protocol_id":protocol_id}), tenant_id=tenant_id))
            db.flush()
            assert db.get(OutboxEvent, event_id) is not None
            db.rollback()
        with Session(engine) as verify:
            assert verify.get(QualityProtocol, protocol_id).is_final is False
            assert verify.get(OutboxEvent, event_id) is None
