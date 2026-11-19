from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.customer_master_profile_service import validate_changes, version_of, scoped_pair


def test_version_is_exact_javascript_safe_microseconds():
    partner = SimpleNamespace(updated_at=datetime(2026, 11, 17, 12, 0, 0, 123456, tzinfo=timezone.utc), created_at=None)
    assert version_of(partner) == 1794916800123456
    assert version_of(partner) < 2**53


def test_partial_valid_fields_and_unsafe_or_malformed_fields():
    version, values = validate_changes({'expected_version': 123, 'partner_iban': 'DE123', 'partner_blocked_for_invoice': True})
    assert version == 123 and values == {'iban': 'DE123', 'blocked_for_invoice': True}
    for changes in ({'partner_tenant_id': 'other'}, {'partner_is_customer': False},
                    {'partner_email_opt_in': True}, {'partner_name_1': 'Drift'},
                    {'partner_blocked_for_invoice': 'false'}, {'partner_iban': 'x' * 35}):
        with pytest.raises(ValueError):
            validate_changes({'expected_version': 123, **changes})
    for invalid in (True, None, 0, 2**53):
        with pytest.raises(ValueError):
            validate_changes({'expected_version': invalid, 'partner_iban': 'DE'})


def test_missing_tenant_denied_before_query():
    class NoQuery:
        def execute(self, *_):
            raise AssertionError('must not query')
    with pytest.raises(HTTPException) as error:
        scoped_pair(NoQuery(), '', 'customer')
    assert error.value.status_code == 403


def test_recheck_prevents_stale_write_and_advances_timestamp(monkeypatch):
    from app.services import customer_master_profile_service as service
    stamp = datetime(2026, 11, 17, 12, 0, 0, 123456, tzinfo=timezone.utc)
    partner = SimpleNamespace(updated_at=stamp, created_at=stamp, iban='old')
    locks = []
    def pair(db, tenant, customer_id, *, lock=False):
        locks.append((tenant, customer_id, lock))
        return object(), partner
    monkeypatch.setattr(service, 'scoped_pair', pair)
    db = SimpleNamespace(flush=lambda: None)
    initial = version_of(partner)
    service.update_profile(db, {'expected_version': initial, 'partner_iban': 'new'}, 'customer', 'tenant')
    assert partner.iban == 'NEW' and version_of(partner) > initial
    with pytest.raises(ValueError, match='zwischenzeitlich'):
        service.update_profile(db, {'expected_version': initial, 'partner_iban': 'stale'}, 'customer', 'tenant')
    assert partner.iban == 'NEW'
    assert locks == [('tenant', 'customer', True), ('tenant', 'customer', True)]


def test_nonnullable_field_rejects_null_even_when_dto_optional():
    with pytest.raises(ValueError):
        validate_changes({'expected_version': 123, 'partner_bank_connection_active': None})


def test_bank_values_use_existing_canonical_normalization():
    _, values = validate_changes({'expected_version': 123, 'partner_iban': ' de 123\t', 'partner_bic': ' b ic\n'})
    assert values == {'iban': 'DE123', 'bic': 'BIC'}
    assert validate_changes({'expected_version': 123, 'partner_iban': None})[1]['iban'] is None


class _Result:
    def __init__(self, item):
        self.item = item
    def scalars(self):
        return self
    def all(self):
        return self.item if isinstance(self.item, list) else ([] if self.item is None else [self.item])


class _ScopedDb:
    def __init__(self, *items):
        self.items = list(items)
        self.statements = []
    def execute(self, statement):
        self.statements.append(statement)
        return _Result(self.items.pop(0))


def test_read_unlinked_customer_keeps_existing_projection_without_version(monkeypatch):
    from app.services import customer_master_profile_service as service
    customer = SimpleNamespace(id='customer-1', business_partner_id=None)
    db = _ScopedDb(customer, None)
    class Projection:
        def __init__(self, db, tenant):
            assert tenant == 'tenant-1'
        def get_from_db_any_key(self, key):
            assert key == 'customer-1'
            return {'id': key, 'tenant_id': 'tenant-1', 'business_partner_id': None, 'company_name': 'Kunde'}
        def merge_extensions(self, projection):
            return {**projection, 'version': 5}
    monkeypatch.setattr(service, 'CustomerService', Projection)
    result = service.read_profile(db, 'tenant-1', 'customer-1')
    assert result == {'id': 'customer-1', 'tenant_id': 'tenant-1', 'business_partner_id': None, 'company_name': 'Kunde'}
    assert len(db.statements) == 2
    statement = str(db.statements[0])
    assert 'customers.tenant_id' in statement and 'customers.deleted_at IS NULL' in statement
    assert db.statements[0].compile().params['tenant_id_1'] == 'tenant-1'


def test_read_linked_customer_exposes_partner_metadata(monkeypatch):
    from app.services import customer_master_profile_service as service
    customer = SimpleNamespace(id='customer-1', business_partner_id='partner-1')
    partner = SimpleNamespace(partner_id='partner-1', iban='DE123', created_at=datetime(2026, 1, 1, tzinfo=timezone.utc), updated_at=None)
    # Model-backed fake returns None for other scalar fields in the catalogue.
    class Partner:
        def __getattr__(self, key):
            return getattr(partner, key, None)
    db = _ScopedDb(customer, Partner(), None)
    class Projection:
        def __init__(self, db, tenant): pass
        def get_from_db_any_key(self, key):
            return {'id': key, 'tenant_id': 'tenant-1', 'business_partner_id': 'partner-1'}
        def merge_extensions(self, projection): return projection
    monkeypatch.setattr(service, 'CustomerService', Projection)
    result = service.read_profile(db, 'tenant-1', 'customer-1')
    assert result['partner_iban'] == 'DE123'
    assert result['version'] == version_of(partner)
    assert db.statements[1].compile().params['tenant_id_1'] == 'tenant-1'
    assert db.statements[1].compile().params['partner_id_1'] == 'partner-1'


def test_read_missing_or_foreign_link_fails_closed():
    from app.services.customer_master_profile_service import read_profile
    for db in (_ScopedDb(None, None), _ScopedDb(SimpleNamespace(id='c', business_partner_id='foreign'), None)):
        with pytest.raises(HTTPException) as error:
            read_profile(db, 'tenant-1', 'c')
        assert error.value.status_code == 404


def test_unlinked_customer_cannot_enter_write_path():
    db = _ScopedDb(SimpleNamespace(id='c', business_partner_id=None))
    with pytest.raises(HTTPException) as error:
        scoped_pair(db, 'tenant-1', 'c', lock=True)
    assert error.value.status_code == 404


def _partner():
    class Partner:
        partner_id = 'partner-1'
        partner_number = 'K-1'
        name_1 = 'Testkunde'
        is_customer = True
        created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        updated_at = None
        def __getattr__(self, key): return None
    return Partner()


@pytest.mark.parametrize('alias', ['customer-1', 'K-1', 'partner-1'])
def test_customer_aliases_resolve_tenant_customer(alias):
    from app.services.customer_master_profile_service import scoped_pair
    customer = SimpleNamespace(id='customer-1', business_partner_id='partner-1')
    partner = _partner()
    db = _ScopedDb(customer, partner, [])
    assert scoped_pair(db, 'tenant-1', alias, lock=True) == (customer, partner)
    query = str(db.statements[0])
    assert 'customers.customer_number' in query and 'customers.business_partner_id' in query
    assert 'FOR UPDATE' in query and 'FOR UPDATE' in str(db.statements[1])
    assert db.statements[0].compile().params['tenant_id_1'] == 'tenant-1'


@pytest.mark.parametrize('alias', ['partner-1', 'K-1'])
def test_bp_only_customer_read_validates_existing_customer_contract(alias):
    from app.services.customer_master_profile_service import read_profile
    from app.api.v1.schemas.crm import Customer as CustomerOut
    partner = _partner()
    db = _ScopedDb(None, partner, None, None, partner)
    result = read_profile(db, 'tenant-1', alias)
    assert CustomerOut.model_validate(result).customer_number == 'K-1'
    assert result['business_partner_id'] == 'partner-1'
    assert result['partner_partner_number'] == 'K-1'
    assert result['version'] == version_of(partner)
    assert 'business_partners.is_customer IS true' in str(db.statements[1])
    assert 'customers.deleted_at IS NULL' in str(db.statements[2])


def test_partner_number_resolves_linked_customer_and_locks_in_order():
    from app.services.customer_master_profile_service import scoped_pair
    partner = _partner()
    customer = SimpleNamespace(id='customer-1', business_partner_id='partner-1')
    db = _ScopedDb(None, partner, customer, partner, partner)
    assert scoped_pair(db, 'tenant-1', 'K-1', lock=True) == (customer, partner)
    assert 'FOR UPDATE' not in str(db.statements[1])
    assert 'FOR UPDATE' in str(db.statements[2]) and 'FOR UPDATE' in str(db.statements[3])


def test_ambiguous_customer_alias_and_partner_collision_are_rejected():
    from app.services.customer_master_profile_service import scoped_pair
    c1 = SimpleNamespace(id='c1', business_partner_id='partner-1')
    c2 = SimpleNamespace(id='c2', business_partner_id='partner-2')
    partner = _partner()
    foreign_alias = SimpleNamespace(partner_id='partner-2')
    for db in (_ScopedDb([c1, c2]), _ScopedDb(c1, partner, foreign_alias)):
        with pytest.raises(HTTPException) as error:
            scoped_pair(db, 'tenant-1', 'K-1')
        assert error.value.status_code == 409


def test_supplier_only_or_foreign_bp_alias_does_not_resolve():
    from app.services.customer_master_profile_service import scoped_pair
    # SQL query filters both tenant and customer role, so no matching result.
    db = _ScopedDb(None, None)
    with pytest.raises(HTTPException) as error:
        scoped_pair(db, 'tenant-1', 'supplier-or-foreign')
    assert error.value.status_code == 404
    assert 'business_partners.is_customer IS true' in str(db.statements[1])
    assert db.statements[1].compile().params['tenant_id_1'] == 'tenant-1'


def test_deleted_customer_cannot_reappear_as_partner_only():
    partner = _partner()
    db = _ScopedDb(None, partner, None, SimpleNamespace(id='deleted'))
    with pytest.raises(HTTPException) as error:
        scoped_pair(db, 'tenant-1', 'partner-1')
    assert error.value.status_code == 404
    assert 'customers.deleted_at IS NOT NULL' in str(db.statements[3])
