"""Real shared-catalog membership ownership; only rollback-isolated synthetic rows."""
import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, PermissionDeniedError
from app.core.rls_session import install_tenant_setting
from app.core.tenant_context import tenant_scope
from app.infrastructure.models import BusinessPartner, BusinessPartnerCommunity, Tenant
from app.services.business_partner_service import BusinessPartnerService


def test_real_memberships_keep_tenant_and_url_parent_boundaries():
    raw = os.getenv('TEST_DATABASE_URL')
    if not raw:
        pytest.skip('Existing shared PostgreSQL probe required')
    url = make_url(raw)
    if url.database != 'valeo_probe':
        pytest.fail('Only the shared valeo_probe is allowed for this rollback contract')
    engine = install_tenant_setting(create_engine(url, connect_args={
        'application_name': 'agent:codex-community-isolation', 'connect_timeout': 5}))
    a, b, ax, ay, bx, group, other_group = (str(uuid4()) for _ in range(7))
    try:
        with engine.connect() as connection, connection.begin() as outer:
            if connection.execute(text('SELECT current_user')).scalar_one() != 'valeo_agent':
                connection.execute(text('SET LOCAL ROLE valeo_agent'))
            with Session(bind=connection, join_transaction_mode='create_savepoint') as db:
                assert db.execute(text('SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user')).one() == (False, False)
                with tenant_scope(a, 'synthetic community fixtures'):
                    db.add_all([Tenant(id=t, name='Synthetic community test', domain=t + '.invalid') for t in (a, b)])
                    db.add_all([BusinessPartnerCommunity(id=g, description='Synthetic community test') for g in (group, other_group)])
                    db.flush()
                    db.add_all([BusinessPartner(partner_id=p, tenant_id=a, partner_number=p, name_1='Synthetic own partner') for p in (ax, ay)])
                    db.commit()
                with tenant_scope(b, 'synthetic foreign community fixture'):
                    db.add(BusinessPartner(partner_id=bx, tenant_id=b, partner_number=bx, name_1='Synthetic other partner'))
                    db.commit()
                    foreign = BusinessPartnerService(db, b).create_community_member(group, {'partner_id': bx})
                    foreign_id = foreign.id
                    db.rollback()
                with tenant_scope(a, 'synthetic own membership checks'):
                    service = BusinessPartnerService(db, a)
                    own = service.create_community_member(group, {'partner_id': ax, 'share_percent': 25})
                    own_id = own.id
                    db.rollback()
                    assert [m.id for m in service.list_community_members(group)] == [own_id]
                    db.rollback()
                    with pytest.raises(EntityNotFoundError):
                        service.create_community_member(group, {'partner_id': bx})
                    db.rollback()
                    with pytest.raises(EntityNotFoundError):
                        service.patch_community_member(other_group, own_id, {'share_percent': 99})
                    db.rollback()
                    with pytest.raises(EntityNotFoundError):
                        service.patch_community_member(group, own_id, {'partner_id': bx})
                    db.rollback()
                    with pytest.raises(EntityNotFoundError):
                        service.delete_community_member(group, foreign_id)
                    db.rollback()
                    with pytest.raises(EntityNotFoundError):
                        service.delete_community_member(other_group, own_id)
                    db.rollback()
                    before = service.list_community_members(group)[0]
                    assert before.partner_id == ax and before.share_percent == 25
                    db.rollback()
                    changed = service.patch_community_member(group, own_id, {'partner_id': ay, 'share_percent': 40})
                    assert changed.partner_id == ay and changed.share_percent == 40
                    db.rollback()
                    service.delete_community_member(group, own_id)
                    assert service.list_community_members(group) == []
                    db.rollback()
                    with pytest.raises(PermissionDeniedError):
                        BusinessPartnerService(db, '').list_community_members(group)
                with tenant_scope(b, 'synthetic foreign membership remains unchanged'):
                    remaining = BusinessPartnerService(db, b).list_community_members(group)
                    assert [m.id for m in remaining] == [foreign_id]
                    assert remaining[0].partner_id == bx
            outer.rollback()
    finally:
        engine.dispose()
