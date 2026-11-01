from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services import waage_import_service as imports
from app.api.v1.endpoints import waage
from asyncio import run as finish


ROW = 'W;PROBE-1;2026-10-30;08:00;1000;400;600;TEST-123;source-supplier;;WW;source-lot;source-silo;14.5;78;1.2;0'


@pytest.mark.parametrize('old,new', [('1000', 'NaN'), ('400', '-1'), ('600', '601'), ('2026-10-30', '2026-99-99'), ('14.5', '101'), ('1000', '1E9999')])
def test_invalid_record_never_becomes_a_ticket(old, new):
    with pytest.raises((ValueError, HTTPException)):
        imports.parse_record(ROW.replace(old, new))


def test_quality_records_remain_with_their_weighing():
    groups = imports.split_records(ROW + '\n' + ROW.replace('PROBE-1', 'PROBE-2') + '\nQ;PROBE-1;Protein;11.5;%')
    assert len(groups) == 2
    assert imports.parse_record(groups[0])['quality_data']['additional'][0]['parameter'] == 'Protein'
    assert imports.parse_record(groups[1])['quality_data']['additional'] == []


def test_duplicate_source_number_is_rejected_before_any_persistence():
    with pytest.raises(HTTPException) as duplicate:
        imports.split_records(ROW + '\n' + ROW)
    assert duplicate.value.status_code == 422


def test_strict_import_rolls_back_when_later_record_is_invalid(monkeypatch):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    monkeypatch.setattr(imports, 'locked_scale', lambda *args: object())
    with pytest.raises(HTTPException) as invalid:
        imports.import_records(db, 'tenant-a', 'scale-a', 'BROKEN', False, 'actor')
    assert invalid.value.status_code == 422
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_known_foreign_scale_blocks_dual_insert():
    from app.services.wiegung_service import schreiben
    db = MagicMock()
    db.execute.return_value.scalar_one.return_value = False
    with pytest.raises(HTTPException) as forbidden:
        schreiben(db, 'tenant-a', 'new', 'PROBE', scale_id='foreign', vehicle_plate='TEST',
            brutto=1000, tara=400, netto=600, richtung_='in', gosse=None, muster_nr=None,
            handwiegung=False, ident_nr=None, disposition_nr=None, charge_nr=None, article_id=None,
            reference_doc=None, notes=None)
    assert forbidden.value.status_code == 404
    assert len(db.execute.call_args_list) == 1
    assert 'INSERT' not in str(db.execute.call_args.args[0])
    db.commit.assert_not_called()


def test_known_foreign_scale_blocks_canonical_create(monkeypatch):
    from app.api.v1.endpoints import weighing_tickets as tickets
    db = MagicMock()
    db.execute.return_value.scalar_one.return_value = False
    monkeypatch.setattr(tickets, 'evaluate_weighing_ticket_datensatz', lambda _: SimpleNamespace(bestanden=True))
    with pytest.raises(HTTPException) as forbidden:
        finish(tickets.create_weighing_ticket(tickets.WeighingTicketCreate(ticket_number='PROBE', scale_id='foreign',
            gross_weight=1000, tare_weight=400, net_weight=600), tenant_id='tenant-a', db=db))
    assert forbidden.value.status_code == 404
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_calibration_date_order_preserves_stored_values(monkeypatch):
    scale = SimpleNamespace(id='own', letzte_eichung=datetime(2026, 10, 1, tzinfo=timezone.utc),
        naechste_eichung=None, eichamt=None, zertifikat_nr=None)
    monkeypatch.setattr(imports, 'locked_scale', lambda *args: scale)
    db = MagicMock()
    with pytest.raises(HTTPException) as invalid:
        finish(waage.update_kalibrierung('own', waage.WaageCalibrationUpdate(naechste_eichfaelligkeit='2020-01-01'),
            db=db, tenant_id='tenant-a', user={'sub':'actor'}))
    assert invalid.value.status_code == 422
    assert scale.naechste_eichung is None
    db.commit.assert_not_called()
