"""Real lifecycle transactions on the existing shared probe, rolled back per test."""
import os
from types import SimpleNamespace
from uuid import uuid4
from datetime import datetime
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from app.infrastructure.models import Tenant
from app.infrastructure.models.journal import JournalEntry
from app.infrastructure.eventbus.outbox import OutboxEvent
from app.services import tenant_lifecycle_service as lifecycle
from test_identity_sessions import session


@pytest.fixture
def database():
    raw=os.getenv('TEST_DATABASE_URL')
    if not raw: pytest.skip('Existing shared test database required')
    url=make_url(raw)
    assert url.database=='valeo_probe' or 'test' in url.database.lower()
    engine=create_engine(url)
    with engine.connect() as connection:
        transaction=connection.begin()
        with Session(bind=connection,join_transaction_mode='create_savepoint') as db:
            yield db
        transaction.rollback()
    engine.dispose()


@pytest.fixture
def service(database,session,monkeypatch):
    target=str(uuid4())
    principal=SimpleNamespace(tenant_id=target,subject='synthetic-admin',
        claims={'identity_type':'human'},roles={'admin'},scopes=set())
    monkeypatch.setattr(lifecycle,'current_identity',lambda:principal)
    row=Tenant(id=target,name='Handbuch Prüfmandant',domain='manual.invalid',settings='{}',is_active=True)
    database.add(row);database.commit()
    return lifecycle.TenantLifecycleService(database),principal,row


def test_empty_tenant_is_deleted_with_actor_outbox(service):
    controller,actor,row=service
    controller.delete(row.id,'Abnahme abgeschlossen')
    assert controller.db.get(Tenant,row.id) is None
    event=controller.db.query(OutboxEvent).filter(OutboxEvent.aggregate_id==row.id).one()
    assert event.event_type=='identity.tenant.deleted'
    assert 'synthetic-admin' in event.payload


@pytest.mark.parametrize('status',['draft','posted','reversed'])
def test_any_journal_history_prevents_deletion_and_can_be_blocked(service,status):
    controller,actor,row=service
    entry=JournalEntry(id=str(uuid4()),tenant_id=row.id,entry_number=uuid4().hex[:18],
        entry_date=datetime(2026,10,12),posting_date=datetime(2026,10,12),
        description='Synthetic lifecycle contract',status=status)
    controller.db.add(entry);controller.db.commit()
    with pytest.raises(HTTPException) as error: controller.delete(row.id,'Test beenden')
    assert error.value.status_code==409
    assert controller.db.get(JournalEntry,entry.id) is not None
    assert controller.db.get(Tenant,row.id).is_active
    blocked=controller.block(row.id,'Testmandant sperren')
    assert not blocked.is_active
    assert controller.db.get(JournalEntry,entry.id) is not None


def test_admin_role_does_not_grant_foreign_tenant_access(service):
    controller,actor,row=service
    other=Tenant(id=str(uuid4()),name='Foreign fixture',domain='foreign.invalid',settings='{}',is_active=True)
    controller.db.add(other);controller.db.commit()
    with pytest.raises(HTTPException) as error:controller.get(other.id)
    assert error.value.status_code==403
    items,total=controller.list(0,100)
    assert total==1 and [item.id for item in items]==[row.id]
    actor.scopes.add('platform:tenants:manage')
    assert controller.get(other.id).id==other.id


def test_user_cannot_create_or_administer_tenant(service):
    controller,actor,row=service
    actor.roles.clear()
    with pytest.raises(HTTPException) as error:controller.block(row.id,'Nicht erlaubt')
    assert error.value.status_code==403
    with pytest.raises(HTTPException) as error:controller.create(dict(name='No',domain='no.invalid',settings='{}'))
    assert error.value.status_code==403
    assert controller.db.get(Tenant,row.id).is_active


def test_explicit_platform_grant_creates_new_stable_identity(service):
    controller,actor,row=service
    actor.scopes.add('platform:tenants:manage')
    created=controller.create(dict(name='Synthetic new tenant',domain='new.invalid',settings='{}'))
    assert created.id!=row.id and created.id!=created.name and created.is_active
    assert controller.db.query(OutboxEvent).filter(OutboxEvent.aggregate_id==created.id).count()==1


def test_tenant_settings_cannot_be_read_by_ordinary_or_service_identities(service):
    controller,actor,row=service
    actor.roles.clear()
    with pytest.raises(HTTPException) as error:controller.get(row.id)
    assert error.value.status_code==403
    actor.roles.add('admin');actor.claims['identity_type']='service'
    with pytest.raises(HTTPException) as error:controller.list(0,100)
    assert error.value.status_code==403
