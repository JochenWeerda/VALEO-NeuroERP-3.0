from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from app.core.exceptions import ConflictError, ValidationFailedError
from app.services.business_partner_service import BusinessPartnerService


@pytest.fixture
def service():
    return BusinessPartnerService(MagicMock(), 'tenant-a')


def result(*, scalar=None, row=None):
    r = MagicMock()
    r.scalar.return_value = scalar
    r.mappings.return_value.first.return_value = row
    return r


def test_tenant_membership_is_checked_with_both_bound_identifiers(service):
    service.db.execute.return_value = result(scalar=None)
    with pytest.raises(ValidationFailedError):
        service.ensure_partner_belongs_to_tenant('foreign')
    sql, params = service.db.execute.call_args.args
    assert 'tenant_id = :tid' in str(sql)
    assert params == {'pid': 'foreign', 'tid': 'tenant-a'}


def test_role_fields_normalize_bank_identifiers_and_preserve_equal_values(service):
    service.db.execute.side_effect = [result(row={'iban': 'de12 345', 'cash_discount_percent': '2.00'}), result()]
    service._rollenfelder_setzen('bp', {'iban': ' DE12 345 ', 'cash_discount_percent': 2, 'ignored': 'x'})
    sql, params = service.db.execute.call_args.args
    assert 'ignored' not in str(sql)
    assert params == {'iban': 'DE12345', 'cash_discount_percent': 2, 'pid': 'bp', 'tid': 'tenant-a'}
    service.db.commit.assert_not_called()


def test_role_field_conflict_does_not_overwrite_existing_value(service):
    service.db.execute.return_value = result(row={'iban': 'DE111'})
    with pytest.raises(ConflictError):
        service._rollenfelder_setzen('bp', {'iban': 'DE222'})
    assert service.db.execute.call_count == 1
    service.db.commit.assert_not_called()


@pytest.mark.parametrize('active,free', [(False, 10000), (True, None)])
def test_blocked_or_exhausted_account_range_never_advances(service, active, free):
    locked = MagicMock()
    locked.one.return_value = SimpleNamespace(is_active=active, start_number=10000, prefix='', current_value=10000, digit_count=5)
    service.db.execute.side_effect = [result(), locked, result(scalar=free)]
    with pytest.raises(ConflictError):
        service.naechste_kontonummer('is_customer')
    assert service.db.execute.call_count == (3 if active else 2)
    service.db.commit.assert_not_called()


def test_account_allocation_skips_used_values_and_advances_range(service):
    locked = MagicMock()
    locked.one.return_value = SimpleNamespace(is_active=True, start_number=10000, prefix='', current_value=10000, digit_count=5)
    service.db.execute.side_effect = [result(), locked, result(scalar=10002), result()]
    assert service.naechste_kontonummer('is_customer') == '10002'
    assert service.db.execute.call_args.args[1] == {'n': 10003, 'tid': 'tenant-a', 'typ': 'debtor_account'}
    service.db.commit.assert_not_called()


def test_assigned_account_cannot_be_changed_or_cleared(service):
    row = SimpleNamespace(is_customer=True, is_supplier=False, debtor_account=None, creditor_account=None)
    with pytest.raises(ConflictError):
        service.assign_account_numbers(row, {'debtor_account': '10001'})
    service.db.execute.assert_not_called()


@pytest.mark.parametrize('method', ['persist_new_partner', 'persist_updated_partner'])
def test_integrity_error_rolls_back_and_reports_conflict(service, method):
    service.db.commit.side_effect = IntegrityError('insert', {}, Exception('duplicate'))
    row = object()
    with pytest.raises(ConflictError):
        getattr(service, method)(row)
    service.db.rollback.assert_called_once_with()
    service.db.refresh.assert_not_called()


def test_address_falls_back_after_missing_satellite_and_rolls_back(service):
    service.db.execute.side_effect = [OperationalError('select', {}, Exception('missing')), result(row={'plz': '12345'})]
    assert service.get_customer_address('K1') == {'plz': '12345'}
    service.db.rollback.assert_called_once_with()
    assert service.db.execute.call_args.args[1] == {'k': 'K1'}


def test_customer_party_uses_partner_address_and_customer_fallbacks(service):
    customer = {'company_name': 'Fallback', 'postal_code': '10000', 'city': 'Berlin', 'country': None,
                'tax_id': 'DE1', 'email': 'a@example.test', 'business_partner_id': 'BP1'}
    partner = {'name_1': 'Partner', 'street': 'Weg', 'house_number': '7', 'postal_code': None, 'city': None, 'vat_id': None}
    service.db.execute.side_effect = [result(row=customer), result(row=partner)]
    assert service.get_customer_party('C1') == {'name': 'Partner', 'street': 'Weg 7', 'postal_code': '10000',
        'city': 'Berlin', 'country_code': 'DE', 'vat_id': 'DE1', 'email': 'a@example.test'}
    assert service.db.execute.call_args.args[1] == {'pid': 'BP1', 'tid': 'tenant-a'}
