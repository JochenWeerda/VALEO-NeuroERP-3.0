"""PostgreSQL profile command isolation, using only an outer rollback transaction."""
import os
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session

from app.services import versandprofil_commands as service


@pytest.fixture
def probe():
    url = os.environ.get('TEST_DATABASE_URL')
    if not url or make_url(url).database != 'valeo_probe':
        pytest.skip('Explicit shared valeo_probe URL required')
    engine = create_engine(url)
    connection = engine.connect()
    outer = connection.begin()
    try:
        yield connection
    finally:
        outer.rollback()
        connection.close()
        engine.dispose()


def identity(tenant, actor='human-a'):
    return SimpleNamespace(tenant_id=tenant, roles={'LAGER_BEARBEITEN'}, subject=actor,
                           claims={'identity_type': 'human'})


def profile(conn, tenant):
    uid = str(uuid4())
    conn.execute(text('INSERT INTO domain_shared.versandprofile '
                      '(id,tenant_id,profil_nr,bezeichnung,versandart) '
                      "VALUES (:id,:tenant,:nr,'Test','email')"),
                 {'id': uid, 'tenant': tenant, 'nr': uid[:20]})
    return uid


def cmd(uid, key):
    return service.DeactivateProfileV1(profile_id=uid, expected_active=True,
                                       idempotency_key=key, reason='Rollback contract test')


def test_real_postgres_replay_and_tenant_isolation(probe):
    tenant, other, key = str(uuid4()), str(uuid4()), str(uuid4())
    own, foreign = profile(probe, tenant), profile(probe, other)
    with Session(bind=probe, join_transaction_mode='create_savepoint') as db:
        with patch.object(service, 'current_identity', return_value=identity(tenant)):
            first = service.deactivate_profile(db, tenant, cmd(own, key))
            db.commit()
            assert service.deactivate_profile(db, tenant, cmd(own, key)) == {**first, 'replayed': True}
            db.rollback()
            with pytest.raises(HTTPException) as conflict:
                service.deactivate_profile(db, tenant, cmd(foreign, str(uuid4())))
            assert conflict.value.status_code == 404
        with patch.object(service, 'current_identity', return_value=identity(tenant, 'human-b')):
            with pytest.raises(HTTPException) as conflict:
                service.deactivate_profile(db, tenant, cmd(own, key))
            assert conflict.value.status_code == 409
    assert probe.execute(text('SELECT aktiv FROM domain_shared.versandprofile WHERE id=:id'), {'id': own}).scalar_one() is False
    assert probe.execute(text('SELECT aktiv FROM domain_shared.versandprofile WHERE id=:id'), {'id': foreign}).scalar_one() is True
    assert probe.execute(text('SELECT COUNT(*) FROM public.mcp_tool_executions WHERE tenant_id=:tenant AND idempotency_key=:key'),
                         {'tenant': tenant, 'key': key}).scalar_one() == 1


def test_real_postgres_audit_failure_rolls_back_deactivation(probe):
    tenant, key = str(uuid4()), str(uuid4())
    uid = profile(probe, tenant)
    with Session(bind=probe, join_transaction_mode='create_savepoint') as db:
        with patch.object(service, 'current_identity', return_value=identity(tenant)), \
             patch.object(service, '_write_audit', side_effect=RuntimeError('synthetic failure')):
            with pytest.raises(HTTPException) as error:
                service.deactivate_profile(db, tenant, cmd(uid, key))
            assert error.value.status_code == 503
            db.rollback()
    assert probe.execute(text('SELECT aktiv FROM domain_shared.versandprofile WHERE id=:id'), {'id': uid}).scalar_one() is True
    assert probe.execute(text('SELECT COUNT(*) FROM public.mcp_tool_executions WHERE tenant_id=:tenant AND idempotency_key=:key'),
                         {'tenant': tenant, 'key': key}).scalar_one() == 0


def test_application_role_rls_restricts_cross_tenant_profile(probe):
    tenant, other = str(uuid4()), str(uuid4())
    own, foreign = profile(probe, tenant), profile(probe, other)
    probe.exec_driver_sql('SET LOCAL ROLE valeo_app')
    probe.execute(text("SELECT set_config('app.tenant_id', :tenant, true)"), {'tenant': tenant})
    assert probe.execute(text('SELECT count(*) FROM domain_shared.versandprofile WHERE id=:id'), {'id': own}).scalar_one() == 1
    assert probe.execute(text('SELECT count(*) FROM domain_shared.versandprofile WHERE id=:id'), {'id': foreign}).scalar_one() == 0
    with Session(bind=probe, join_transaction_mode='create_savepoint') as db:
        with patch.object(service, 'current_identity', return_value=identity(tenant)):
            result = service.deactivate_profile(db, tenant, cmd(own, str(uuid4())))
            assert result['success']
            db.commit()
    probe.exec_driver_sql('RESET ROLE')
    assert probe.execute(text('SELECT aktiv FROM domain_shared.versandprofile WHERE id=:id'), {'id': foreign}).scalar_one() is True


def test_concurrent_identical_requests_create_one_effect_and_one_replay():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    url = os.environ.get('TEST_DATABASE_URL')
    if not url or make_url(url).database != 'valeo_probe':
        pytest.skip('Explicit shared valeo_probe URL required')
    engine = create_engine(url, pool_size=3)
    tenant, uid, key = str(uuid4()), str(uuid4()), str(uuid4())
    try:
        with engine.begin() as conn:
            conn.execute(text('INSERT INTO domain_shared.versandprofile '
                              '(id,tenant_id,profil_nr,bezeichnung,versandart) '
                              "VALUES (:id,:tenant,:nr,'Concurrency test','email')"),
                         {'id': uid, 'tenant': tenant, 'nr': uid[:20]})
        barrier = Barrier(2, timeout=15)
        def invoke():
            with engine.connect() as conn:
                transaction = conn.begin()
                try:
                    conn.exec_driver_sql('SET LOCAL ROLE valeo_app')
                    conn.execute(text("SELECT set_config('app.tenant_id', :tenant, true)"), {'tenant': tenant})
                    with Session(bind=conn, join_transaction_mode='create_savepoint') as db:
                        barrier.wait()
                        result = service.deactivate_profile(db, tenant, cmd(uid, key))
                        db.commit()
                    transaction.commit()
                    return result
                except BaseException:
                    transaction.rollback()
                    raise
        with patch.object(service, 'current_identity', return_value=identity(tenant)):
            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(lambda _: invoke(), range(2)))
        assert sorted(result['replayed'] for result in results) == [False, True]
        with engine.connect() as conn:
            assert conn.execute(text('SELECT count(*) FROM domain_crm.crm_action_audit_log WHERE tenant_id=:t AND entity_id=:id'),
                                {'t': tenant, 'id': uid}).scalar_one() == 1
            assert conn.execute(text('SELECT count(*) FROM outbox_events WHERE tenant_id=:t AND aggregate_id=:id'),
                                {'t': tenant, 'id': uid}).scalar_one() == 1
            assert conn.execute(text('SELECT count(*) FROM public.mcp_tool_executions WHERE tenant_id=:t AND idempotency_key=:key'),
                                {'t': tenant, 'key': key}).scalar_one() == 1
    finally:
        with engine.begin() as conn:
            conn.execute(text('DELETE FROM outbox_events WHERE tenant_id=:t AND aggregate_id=:id'), {'t': tenant, 'id': uid})
            conn.execute(text('DELETE FROM domain_crm.crm_action_audit_log WHERE tenant_id=:t AND entity_id=:id'), {'t': tenant, 'id': uid})
            conn.execute(text('DELETE FROM public.mcp_tool_executions WHERE tenant_id=:t AND idempotency_key=:key'), {'t': tenant, 'key': key})
            conn.execute(text('DELETE FROM domain_shared.versandprofile WHERE tenant_id=:t AND id=:id'), {'t': tenant, 'id': uid})
        engine.dispose()
