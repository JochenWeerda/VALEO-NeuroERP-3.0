"""Bank closing date survives import and replay; CSV uses its booking cutoff."""
from datetime import date

import pytest
from sqlalchemy import text

from app.api.v1.endpoints.bank_statement_import import parse_camt053, parse_mt940, parse_csv
from test_bank_import_account_replay import import_case as replay_case, upload, counts, camt
from test_bank_mt940_parser_integrity import statement

import_case = replay_case
CSV = 'date,value_date,amount,currency,reference\n2026-09-29,2026-10-02,5,EUR,A\n2026-09-27,2026-10-03,10,EUR,B\n'


@pytest.mark.parametrize('parser,content', [
    (parse_camt053, camt()), (parse_mt940, statement()), (parse_csv, CSV),
])
def test_parser_exposes_authoritative_cutoff(parser, content):
    parsed = parser(content.encode())
    assert parsed['statement_date'] == date(2026, 9, 29 if parser == parse_csv else 28)


@pytest.mark.parametrize('content,fmt,route,expected', [
    (camt(), 'CAMT', 'bank', date(2026, 9, 28)),
    (statement(), 'MT940', 'bank', date(2026, 9, 28)),
    (CSV, 'CSV', 'bank', date(2026, 9, 29)),
    (CSV, 'CSV', 'payments', date(2026, 9, 29)),
])
def test_import_and_replay_keep_file_cutoff(import_case, content, fmt, route, expected):
    db, _, tenant = import_case
    first = upload(import_case, content, fmt=fmt, route=route)
    assert first.status_code == 200, first.text
    assert db.execute(text('SELECT statement_date FROM domain_erp.bank_statements WHERE tenant_id=:t'),
                      {'t': tenant}).scalar_one() == expected
    second = upload(import_case, content, fmt=fmt, route=route)
    assert second.status_code == 200, second.text
    assert counts(import_case) == (1, 2 if fmt == 'CSV' else 1)
    assert db.execute(text('SELECT statement_date FROM domain_erp.bank_statements WHERE tenant_id=:t'),
                      {'t': tenant}).scalar_one() == expected


def test_two_csv_entry_points_share_date_and_identity(import_case):
    assert upload(import_case, CSV, route='payments').status_code == 200
    assert upload(import_case, CSV).status_code == 200
    assert counts(import_case) == (1, 2)


@pytest.mark.parametrize('booking', ['0927','0929'])
def test_mt940_booking_outside_balance_interval_rejected(booking):
    with pytest.raises(ValueError, match='outside statement balances'):
        parse_mt940(statement(lines=f':61:260928{booking}C25,00NTRFREF-1').encode())


def test_empty_mt940_keeps_balance_date_and_currency():
    parsed = parse_mt940(statement(lines='',closing='C260928EUR0,00').encode())
    assert parsed['statement_date'] == date(2026,9,28)
    assert parsed['currency'] == 'EUR'


def test_empty_mt940_foreign_currency_cannot_create_header(import_case):
    content = statement(lines='',opening='C260928USD0,00',closing='C260928USD0,00')
    response = upload(import_case,content,fmt='MT940')
    assert response.status_code == 422, response.text
    assert counts(import_case) == (0,0)


def test_empty_bank_csv_has_no_date_and_cannot_create_header(import_case):
    response = upload(import_case,'date,amount,currency,reference\n')
    assert response.status_code == 422, response.text
    assert counts(import_case) == (0,0)


@pytest.mark.parametrize('route',['bank','payments'])
def test_replay_detects_inconsistent_stored_date(import_case,route):
    db, _, tenant=import_case
    assert upload(import_case,CSV,route=route).status_code==200
    db.execute(text("UPDATE domain_erp.bank_statements SET statement_date='2026-01-01' WHERE tenant_id=:t"),{'t':tenant})
    db.commit()
    response=upload(import_case,CSV,route=route)
    assert response.status_code==409,response.text
    assert counts(import_case)==(1,2)
    assert db.execute(text('SELECT statement_date FROM domain_erp.bank_statements WHERE tenant_id=:t'),
                      {'t':tenant}).scalar_one()==date(2026,1,1)
