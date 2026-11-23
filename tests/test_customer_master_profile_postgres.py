"""Real PostgreSQL aggregate roundtrip; all synthetic rows roll back together."""
import asyncio
import os
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.tenant_context import tenant_scope
from app.core.rls_session import install_tenant_setting
from app.infrastructure.models import BusinessPartner, Customer, Tenant
from app.services.customer_master_profile_service import read_profile, update_profile
from app.services.mask_action_runtime_service import run_delegated_mask_action


def test_postgres_roundtrip_version_replay_actor_and_tenant_isolation():
    raw = os.getenv('TEST_DATABASE_URL')
    if not raw:
        pytest.skip('Existing shared PostgreSQL probe required')
    url = make_url(raw)
    if url.database != 'valeo_probe':
        pytest.fail('This contract only writes rollback-isolated records on valeo_probe')
    engine = install_tenant_setting(create_engine(url, connect_args={
        'application_name': 'agent:codex-customer-profile', 'connect_timeout': 5}))
    tenant, other, partner_id, customer_id = (str(uuid4()) for _ in range(4))
    try:
        with engine.connect() as connection, connection.begin() as outer:
            if connection.execute(text('SELECT current_user')).scalar_one() != 'valeo_agent':
                # CI supplies the database owner; run the business contract as the
                # already-provisioned restricted agent role, never as that owner.
                connection.execute(text('SET LOCAL ROLE valeo_agent'))
            with tenant_scope(tenant, 'synthetic master profile contract'):
                with Session(bind=connection, join_transaction_mode='create_savepoint') as db:
                    role = db.execute(text('SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user')).one()
                    assert role == (False, False)
                    db.add(Tenant(id=tenant, name='Synthetic profile test', domain=tenant + '.invalid'))
                    db.flush()
                    db.add(BusinessPartner(partner_id=partner_id, tenant_id=tenant,
                                           partner_number=partner_id, name_1='Synthetic profile test', is_customer=True))
                    db.flush()
                    db.add(Customer(id=customer_id, tenant_id=tenant, business_partner_id=partner_id,
                                    customer_number=customer_id, company_name='Synthetic profile test'))
                    db.commit()  # releases only this test's savepoint
                    profile = read_profile(db, tenant, customer_id)
                    version = profile['version']
                    db.rollback()
                    body = {'partner_iban': 'de 123', 'expected_version': version,
                            '_idempotencyKey': 'synthetic-' + customer_id, '_auditReason': 'Synthetic regression'}

                    def check(*_):
                        return []

                    def update(session, payload, eid, tid):
                        return update_profile(session, payload, eid, tid, actor='synthetic-actor')

                    def execute(fingerprint):
                        return asyncio.run(run_delegated_mask_action(
                            db, action_key='stammdaten_pflegen', entity_type='customer_master_profile',
                            entity_id=customer_id, tenant_id=tenant, body=body,
                            check_fn=check, delegate_fn=update,
                            outbox_event_type='crm.customer.master_profile.updated', require_audit_reason=True,
                            performed_by='synthetic-actor', request_fingerprint=fingerprint))

                    first = execute('synthetic-request')
                    assert first.success, first.error
                    result = read_profile(db, tenant, customer_id)
                    assert result['partner_iban'] == 'DE123'
                    assert result['partner_updated_by'] == 'synthetic-actor'
                    assert result['version'] > version
                    db.rollback()
                    assert execute('synthetic-request').success  # replay accepts the original version
                    assert not execute('different-request').success
                    assert db.execute(text('SELECT count(*) FROM domain_crm.crm_action_audit_log '
                                           'WHERE tenant_id=:t AND entity_id=:e'), {'t': tenant, 'e': customer_id}).scalar_one() == 1
                    db.rollback()
                    with pytest.raises(ValueError, match='zwischenzeitlich'):
                        update_profile(db, {'partner_iban': 'DE456', 'expected_version': version}, customer_id, tenant)
                    db.rollback()
                with tenant_scope(other, 'synthetic foreign tenant denial'):
                    with Session(bind=connection, join_transaction_mode='create_savepoint') as db:
                        with pytest.raises(HTTPException) as error:
                            read_profile(db, other, customer_id)
                        assert error.value.status_code == 404
            outer.rollback()
    finally:
        engine.dispose()
