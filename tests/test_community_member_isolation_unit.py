"""Community membership isolation without connections or database mutations."""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.v1.endpoints.business_partners import router
from app.core.exceptions import EntityNotFoundError, PermissionDeniedError, ValidationFailedError
from app.services.business_partner_service import BusinessPartnerService


class QueryRecorder:
    def __init__(self, db, query):
        self.db, self.query = db, query
    def __getattr__(self, name):
        if name in {'join', 'filter', 'order_by', 'with_for_update'}:
            def chain(*args, **kwargs):
                self.query = getattr(self.query, name)(*args, **kwargs)
                return self
            return chain
        raise AttributeError(name)
    def first(self):
        self.db.statements.append(self.query.statement)
        return self.db.results.pop(0)
    def all(self):
        self.db.statements.append(self.query.statement)
        return self.db.results.pop(0)


class FakeDb:
    def __init__(self, *results):
        self.results, self.statements = list(results), []
        self.session = Session()
        self.added, self.deleted, self.commits = [], [], 0
    def query(self, *entities): return QueryRecorder(self, self.session.query(*entities))
    def add(self, row): self.added.append(row)
    def delete(self, row): self.deleted.append(row)
    def commit(self): self.commits += 1
    def refresh(self, row): pass
    def rollback(self): pass


def sql(statement):
    from sqlalchemy.dialects import postgresql
    compiled = statement.compile(dialect=postgresql.dialect())
    return str(compiled), compiled.params


def test_list_joins_partner_and_filters_tenant_and_community():
    db = FakeDb(('community',), [])
    assert BusinessPartnerService(db, 'tenant-A').list_community_members('community-A') == []
    query, values = sql(db.statements[1])
    assert 'JOIN domain_crm.business_partners' in query
    assert 'business_partners.partner_id = domain_crm.business_partner_community_members.partner_id' in query
    assert 'business_partners.tenant_id' in query and 'business_partner_community_members.community_id' in query
    assert 'tenant-A' in values.values() and 'community-A' in values.values()


def test_missing_tenant_denied_before_any_query():
    db = FakeDb()
    with pytest.raises(PermissionDeniedError):
        BusinessPartnerService(db, '').list_community_members('community-A')
    assert not db.statements


def test_create_checks_parent_and_exact_tenant_partner_before_insert():
    db = FakeDb(('community',), None)
    with pytest.raises(EntityNotFoundError):
        BusinessPartnerService(db, 'tenant-A').create_community_member('community-A', {'partner_id': 'foreign'})
    assert not db.added and db.commits == 0
    query, values = sql(db.statements[1])
    assert 'business_partners.tenant_id' in query and 'business_partners.partner_id' in query
    assert 'tenant-A' in values.values() and 'foreign' in values.values()
    missing_parent = FakeDb(None)
    with pytest.raises(EntityNotFoundError):
        BusinessPartnerService(missing_parent, 'tenant-A').create_community_member('missing', {'partner_id': 'p'})
    assert len(missing_parent.statements) == 1 and not missing_parent.added


@pytest.mark.parametrize('method', ['patch', 'delete'])
def test_member_write_requires_url_community_and_tenant(method):
    db = FakeDb(('community',), None)
    service = BusinessPartnerService(db, 'tenant-A')
    with pytest.raises(EntityNotFoundError):
        if method == 'patch': service.patch_community_member('wrong-community', 'member', {'share_percent': 5})
        else: service.delete_community_member('wrong-community', 'member')
    query, values = sql(db.statements[1])
    assert 'JOIN domain_crm.business_partners' in query
    assert 'business_partner_community_members.id' in query
    assert 'business_partner_community_members.community_id' in query
    assert 'business_partners.tenant_id' in query
    assert {'wrong-community', 'member', 'tenant-A'} <= set(values.values())
    assert 'FOR UPDATE' in query
    assert not db.deleted and db.commits == 0


def test_reassignment_requires_own_partner_and_null_is_rejected():
    member = SimpleNamespace(partner_id='own', share_percent=10)
    db = FakeDb(('community',), member, None)
    with pytest.raises(EntityNotFoundError):
        BusinessPartnerService(db, 'tenant-A').patch_community_member('community', 'member', {'partner_id': 'foreign'})
    assert member.partner_id == 'own' and db.commits == 0
    query, values = sql(db.statements[2])
    assert 'business_partners.tenant_id' in query and {'tenant-A', 'foreign'} <= set(values.values())
    db = FakeDb(('community',), member)
    with pytest.raises(ValidationFailedError):
        BusinessPartnerService(db, 'tenant-A').patch_community_member('community', 'member', {'partner_id': None})
    assert member.partner_id == 'own' and db.commits == 0


def _role_check(method, path, roles):
    route = next(r for r in router.routes if getattr(r, 'path', None) == path and method in r.methods)
    role_dependency = route.dependencies[0].dependency
    return role_dependency({'sub': 'actor', 'roles': roles})


def test_existing_read_and_admin_role_policy():
    read = '/catalog/communities/{community_id}/members'
    for role in ('CRM_LESEN', 'SALES_LESEN', 'FINANCE_LESEN', 'admin'):
        assert _role_check('GET', read, [role])['sub'] == 'actor'
    with pytest.raises(HTTPException) as error:
        _role_check('GET', read, ['customer_portal'])
    assert error.value.status_code == 403
    for method, path in [('POST', '/catalog/communities'), ('PATCH', '/catalog/communities/{community_id}'),
                         ('DELETE', '/catalog/communities/{community_id}')]:
        with pytest.raises(HTTPException) as error:
            _role_check(method, path, ['CRM_ADMIN'])
        assert error.value.status_code == 403
        assert _role_check(method, path, ['admin'])['sub'] == 'actor'


def test_own_member_create_reassign_and_delete_succeed():
    create_db = FakeDb(('community',), ('own-partner',))
    created = BusinessPartnerService(create_db, 'tenant-A').create_community_member(
        'community-A', {'partner_id': 'partner-A', 'share_percent': 12})
    assert created.community_id == 'community-A' and created.partner_id == 'partner-A'
    assert create_db.added == [created] and create_db.commits == 1
    member = SimpleNamespace(partner_id='partner-A', share_percent=12)
    patch_db = FakeDb(('community',), member, ('new-own-partner',))
    assert BusinessPartnerService(patch_db, 'tenant-A').patch_community_member(
        'community-A', 'member-A', {'partner_id': 'partner-B', 'share_percent': 25}) is member
    assert member.partner_id == 'partner-B' and member.share_percent == 25 and patch_db.commits == 1
    delete_db = FakeDb(('community',), member)
    BusinessPartnerService(delete_db, 'tenant-A').delete_community_member('community-A', 'member-A')
    assert delete_db.deleted == [member] and delete_db.commits == 1


def test_member_routes_require_trusted_tenant_and_crm_write_roles():
    from app.core.tenant import get_tenant_id
    for method, path in [('POST', '/catalog/communities/{community_id}/members'),
                         ('PATCH', '/catalog/communities/{community_id}/members/{member_id}'),
                         ('DELETE', '/catalog/communities/{community_id}/members/{member_id}')]:
        route = next(r for r in router.routes if getattr(r, 'path', None) == path and method in r.methods)
        assert any(dep.call is get_tenant_id for dep in route.dependant.dependencies)
        assert _role_check(method, path, ['CRM_ADMIN'])['sub'] == 'actor'
        with pytest.raises(HTTPException): _role_check(method, path, ['CRM_LESEN'])
        with pytest.raises(HTTPException): _role_check(method, path, ['customer_portal'])
