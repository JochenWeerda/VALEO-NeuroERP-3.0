from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest
from app.core.exceptions import ValidationFailedError
from app.services.docflow_service import DocflowService


def request(mengen=None, **extra):
    return DocflowConvertRequest(target_doc_type='sales_delivery', idempotency_key='test-key-001',
                                 quantities_by_source_item_id=mengen or {}, **extra)


def service():
    db = MagicMock()
    svc = DocflowService(db, 'tenant-a')
    svc.bootstrap_doc = MagicMock(return_value={'doc_type': 'sales_order', 'version': 1})
    svc._sperre = MagicMock()
    svc._pruefe_rechnungsweg = MagicMock()
    svc.umgewandelte_mengen = MagicMock(return_value={})
    svc.fetch_pos_compliance = MagicMock(return_value=None)
    svc.fetch_items = MagicMock(return_value=[{'id': 'owned', 'line_number': 1, 'quantity': 10, 'unit_price': 2, 'tax_rate': 0}])
    return svc, db


@pytest.mark.parametrize('value', [float('nan'), float('inf'), float('-inf'), -1])
def test_mengenmodell_lehnt_ungueltige_werte_ab(value):
    with pytest.raises(ValidationError):
        request({'owned': value})


def test_fremde_position_mit_gueltiger_wird_vor_schreiben_abgelehnt():
    svc, db = service()
    with pytest.raises(ValidationFailedError):
        svc.convert('auftrag', request({'owned': 2, 'foreign': 1}, dry_run=True))
    db.execute.assert_not_called()

@pytest.mark.parametrize('mengen, count, total', [({}, 1, 20.0), ({'owned': 3}, 1, 6.0)])
def test_gueltige_mengen_und_leere_legacy_auswahl(mengen, count, total):
    svc, db = service()
    result = svc.convert('auftrag', request(mengen, dry_run=True))
    assert result['payload']['item_count'] == count
    assert result['payload']['total_net'] == total
    db.execute.assert_not_called()


def test_null_menge_fuehrt_nicht_zur_uebernahme():
    svc, db = service()
    with pytest.raises(ValidationFailedError, match='No convertible'):
        svc.convert('auftrag', request({'owned': 0}, dry_run=True))
    db.execute.assert_not_called()


def test_ueber_restmenge_wird_abgelehnt():
    svc, db = service()
    with pytest.raises(ValidationFailedError, match='Restmenge'):
        svc.convert('auftrag', request({'owned': 11}, dry_run=True))
    db.execute.assert_not_called()


def test_options_zeigen_menge_und_rest_ohne_preise_oder_schreibzugriffe():
    from decimal import Decimal
    svc, db = service()
    svc.fetch_header = MagicMock(return_value={'doc_type': 'sales_order', 'version': 7, 'customer_id': 'secret'})
    svc.umgewandelte_mengen.return_value = {'owned': Decimal('3.5')}
    svc.fetch_items.return_value = [{'id': 'owned', 'line_number': 1, 'article_number': 'A1', 'description': 'Weizen',
                                     'unit': 'kg', 'quantity': 10, 'unit_price': 123, 'tax_code': 'secret'}]
    result = svc.conversion_options('auftrag', 'sales_delivery')
    assert result == {'source_doc_id': 'auftrag', 'source_doc_type': 'sales_order', 'target_doc_type': 'sales_delivery',
                      'version': 7, 'items': [{'source_item_id': 'owned', 'line_number': 1, 'article_number': 'A1',
                                              'description': 'Weizen', 'unit': 'kg', 'quantity': 10.0, 'remaining_quantity': 6.5}]}
    svc.bootstrap_doc.assert_not_called()
    svc._sperre.assert_not_called()
    db.execute.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_options_unbekannt_oder_ungueltige_relation():
    from app.core.exceptions import EntityNotFoundError
    svc, db = service()
    svc.fetch_header = MagicMock(return_value=None)
    with pytest.raises(EntityNotFoundError):
        svc.conversion_options('foreign', 'sales_delivery')
    svc.fetch_header.return_value = {'doc_type': 'sales_order', 'version': 1}
    with pytest.raises(ValidationFailedError, match='Transition not allowed'):
        svc.conversion_options('auftrag', 'purchase_order')
    svc.fetch_items.assert_not_called()
    db.execute.assert_not_called()
