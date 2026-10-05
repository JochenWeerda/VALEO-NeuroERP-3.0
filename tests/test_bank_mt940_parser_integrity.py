"""Strict supported MT940 profile: no dropped entries or invented balances."""
from decimal import Decimal

import pytest

from app.api.v1.endpoints.bank_statement_import import parse_mt940
from test_bank_import_account_replay import import_case as replay_case, counts, upload

import_case = replay_case


def statement(lines=':61:2609280928C25,00NTRFREF-1//BANK-1', opening='C260928EUR0,00', closing='C260928EUR25,00'):
    return f':20:REF\n:25:DE89370400440532013000\n:28C:1\n:60F:{opening}\n{lines}\n:62F:{closing}\n'


def test_entry_without_description_is_preserved():
    parsed = parse_mt940(statement().encode())
    assert len(parsed['entries']) == 1
    assert parsed['entries'][0]['amount'] == Decimal('25')
    assert str(parsed['entries'][0]['booking_date']) == '2026-09-28'
    assert parsed['entries'][0]['reference'] == 'BANK-1'


def test_optional_booking_date_and_two_entries_without_description():
    parsed = parse_mt940(statement(':61:260928C25,00NTRFREF-1\n:61:260928D10,00NTRFREF-2', closing='C260928EUR15,00').encode())
    assert [e['amount'] for e in parsed['entries']] == [Decimal('25'), Decimal('-10')]
    assert str(parsed['entries'][0]['booking_date']) == '2026-09-28'
    assert parsed['entries'][0]['reference'] == 'REF-1'


def test_signed_balance_and_multiline_description():
    parsed = parse_mt940(statement(':61:2609280928C25,00NTRFREF-1\n:86:Invoice\ncontinued', opening='D260928EUR100,00', closing='D260928EUR75,00').encode())
    assert parsed['opening_balance'] == -100
    assert parsed['closing_balance'] == -75
    assert parsed['entries'][0]['remittance_info'] == 'Invoice\ncontinued'


@pytest.mark.parametrize('payload', [
    statement(closing='C260928EUR24,99'),
    statement(closing='C260928CHF25,00'),
    statement().replace(':60F:C260928EUR0,00\n', ''),
    statement().replace(':62F:C260928EUR25,00\n', ''),
    statement() + statement(),
    statement(':61:2609280928RC25,00NTRFREF-1'),
    statement(':61:2609280928RD25,00NTRFREF-1'),
    statement(':61:bad'),
    statement(':61:2609280230C25,00NTRFREF-1'),
    statement(':61:2609280928C25,001NTRFREF-1'),
    statement(':61:2609280928C25,00'),
    statement(':86:orphan'),
    statement(':61:2407020101C25,00NTRFREF-1', opening='C240702EUR0,00', closing='C240702EUR25,00'),
])
def test_invalid_statement_rejected_as_whole(payload):
    with pytest.raises(ValueError):
        parse_mt940(payload.encode())


def test_invalid_encoding_not_silently_repaired():
    with pytest.raises(ValueError):
        parse_mt940(statement().encode() + b'\xff')


def test_year_boundary_and_currency_funds_code():
    parsed = parse_mt940(statement(':61:2612310101CF25,00NTRFREF-1', opening='C261231CHF0,00', closing='C270101CHF25,00').encode())
    assert str(parsed['entries'][0]['booking_date']) == '2027-01-01'
    assert parsed['entries'][0]['currency'] == 'CHF'


def test_mt940_import_without_description_persists_and_replays(import_case):
    first = upload(import_case, statement(), fmt='MT940')
    assert first.status_code == 200, first.text
    replay = upload(import_case, statement(), fmt='mt940')
    assert replay.status_code == 200, replay.text
    assert first.json() == replay.json()
    assert counts(import_case) == (1, 1)


def test_bad_closing_balance_leaves_no_header_or_line(import_case):
    response = upload(import_case, statement(closing='C260928EUR24,99'), fmt='MT940')
    assert response.status_code == 400, response.text
    assert counts(import_case) == (0, 0)
