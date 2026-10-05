"""Booked single-entry CAMT profile: authoritative balances and safe details."""
from decimal import Decimal

import pytest

from app.api.v1.endpoints.bank_statement_import import parse_camt053
from test_bank_import_account_replay import import_case as replay_case, counts, upload

import_case = replay_case
NS = 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.02'


def balance(code, amount, direction='CRDT', currency='EUR'):
    return f'<Bal><Tp><CdOrPrtry><Cd>{code}</Cd></CdOrPrtry></Tp><Amt Ccy="{currency}">{amount}</Amt><CdtDbtInd>{direction}</CdtDbtInd><Dt><Dt>2026-09-28</Dt></Dt></Bal>'


ENTRY = '<Ntry><Amt Ccy="EUR">25.00</Amt><CdtDbtInd>CRDT</CdtDbtInd><Sts>BOOK</Sts><BookgDt><Dt>2026-09-28</Dt></BookgDt><ValDt><Dt>2026-09-29</Dt></ValDt><AcctSvcrRef>BANK-1</AcctSvcrRef>{details}</Ntry>'
DETAIL = '<NtryDtls><TxDtls><Refs><EndToEndId>REF-1</EndToEndId></Refs><AmtDtls><TxAmt><Amt Ccy="EUR">25.00</Amt></TxAmt></AmtDtls><RltdPties><Cdtr><Nm>Creditor</Nm></Cdtr><CdtrAcct><Id><IBAN>DE89370400440532013000</IBAN></Id></CdtrAcct></RltdPties><RmtInf><Ustrd>Invoice</Ustrd><Ustrd>REF-1</Ustrd><Strd><CdtrRefInf><Ref>REF-1</Ref></CdtrRefInf></Strd></RmtInf></TxDtls></NtryDtls>'


def statement(entry=None, balances=None):
    if entry is None:
        entry = ENTRY.format(details=DETAIL)
    if balances is None:
        balances = balance('OPBD', '0') + balance('CLBD', '25')
    return f'<Document xmlns="{NS}"><BkToCstmrStmt><Stmt><Acct><Id><IBAN>DE89370400440532013000</IBAN></Id><Ccy>EUR</Ccy></Acct>{balances}{entry}</Stmt></BkToCstmrStmt></Document>'


def test_balance_type_and_sign_not_xml_order():
    xml = statement(balances=balance('CLAV', '999') + balance('CLBD', '75', 'DBIT') + balance('OPBD', '100', 'DBIT'))
    parsed = parse_camt053(xml.encode())
    assert parsed['opening_balance'] == -100
    assert parsed['closing_balance'] == -75


def test_real_related_accounts_and_all_remittance_parts_preserved():
    parsed = parse_camt053(statement().encode())
    entry = parsed['entries'][0]
    assert entry['reference'] == 'BANK-1'
    assert entry['creditor_name'] == 'Creditor'
    assert entry['creditor_iban'] == 'DE89370400440532013000'
    assert entry['remittance_info'] == 'Invoice\nREF-1\nREF-1'
    assert entry['amount'] == Decimal('25')


@pytest.mark.parametrize('payload', [
    statement(balances=balance('OPBD', '0')),
    statement(balances=balance('OPBD', '0') + balance('OPBD', '0') + balance('CLBD', '25')),
    statement(balances=balance('OPBD', '0') + balance('CLBD', '24.99')),
    statement(balances=balance('OPBD', '0') + balance('CLBD', '25', currency='CHF')),
    statement().replace('<Sts>BOOK</Sts>', '<Sts>PDNG</Sts>'),
    statement().replace('<Sts>BOOK</Sts>', ''),
    statement().replace('<Sts>BOOK</Sts>', '<Sts>BOOK</Sts><RvslInd>true</RvslInd>'),
    statement().replace('<CdtDbtInd>CRDT</CdtDbtInd><Sts>', '<CdtDbtInd>UNKNOWN</CdtDbtInd><Sts>'),
    statement().replace('<BookgDt><Dt>2026-09-28</Dt></BookgDt>', ''),
    statement().replace('<ValDt><Dt>2026-09-29</Dt></ValDt>', ''),
    statement().replace('<TxAmt><Amt Ccy="EUR">25.00', '<TxAmt><Amt Ccy="EUR">24.99'),
    statement(entry=ENTRY.format(details=DETAIL.replace('</NtryDtls>', DETAIL.removeprefix('<NtryDtls>')))),
    statement().replace('<Amt Ccy="EUR">25.00</Amt><CdtDbtInd>', '<Amt Ccy="EUR">-25.00</Amt><CdtDbtInd>'),
    statement().replace('<Amt Ccy="EUR">25.00</Amt><CdtDbtInd>', '<Amt Ccy="EUR">25.00</Amt><Amt Ccy="EUR">25.00</Amt><CdtDbtInd>'),
    statement().replace('<BookgDt><Dt>2026-09-28</Dt></BookgDt>', '<BookgDt><Dt>2026-09-30</Dt></BookgDt>'),
    statement().replace('<Amt Ccy="EUR">25.00</Amt><CdtDbtInd>', '<CdtDbtInd>'),
    statement().replace('<CdtDbtInd>CRDT</CdtDbtInd><Sts>', '<Sts>'),
    statement().replace('<RltdPties>', '<RltdPties></RltdPties><RltdPties>'),
    statement().replace(NS, 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.08'),
    '<!DOCTYPE Document [<!ENTITY injected "25">]>' + statement(),
    statement().replace('</TxDtls>', '<RtrInf/></TxDtls>'),
    statement().replace('</TxDtls>', '<CcyXchg/></TxDtls>'),
    statement().replace('<NtryDtls>', '<NtryDtls><Btch><NbOfTxs>1</NbOfTxs></Btch>'),
    statement(balances=balance('OPBD', '0') + balance('CLBD', '10000000000000')).replace('25.00', '10000000000000.00'),
])
def test_unsafe_statement_is_rejected_as_whole(payload):
    with pytest.raises(ValueError):
        parse_camt053(payload.encode())


def test_datetime_date_choices_preserved_without_today_fallback():
    xml = statement().replace('<BookgDt><Dt>2026-09-28</Dt></BookgDt>', '<BookgDt><DtTm>2026-09-28T23:59:00+02:00</DtTm></BookgDt>')
    assert str(parse_camt053(xml.encode())['entries'][0]['booking_date']) == '2026-09-28'


def test_debit_entry_sign_matches_closing_balance():
    xml = statement(balances=balance('OPBD', '0') + balance('CLBD', '25', 'DBIT'))
    xml = xml.replace('<Amt Ccy="EUR">25.00</Amt><CdtDbtInd>CRDT', '<Amt Ccy="EUR">25.00</Amt><CdtDbtInd>DBIT')
    assert parse_camt053(xml.encode())['entries'][0]['amount'] == Decimal('-25.00')


def test_largest_storable_amount_keeps_exact_cents():
    xml = statement(balances=balance('OPBD', '0') + balance('CLBD', '9999999999999.99')).replace('25.00', '9999999999999.99')
    assert parse_camt053(xml.encode())['closing_balance'] == Decimal('9999999999999.99')


def test_import_and_replay_preserve_authoritative_balance(import_case):
    xml = statement()
    first = upload(import_case, xml, fmt='CAMT')
    assert first.status_code == 200, first.text
    second = upload(import_case, xml, fmt='camt')
    assert second.status_code == 200, second.text
    assert first.json() == second.json()
    assert float(first.json()['closing_balance']) == 25
    assert counts(import_case) == (1, 1)


def test_bad_balance_never_writes(import_case):
    response = upload(import_case, statement(balances=balance('OPBD', '0') + balance('CLBD', '24')), fmt='CAMT', auto=True)
    assert response.status_code == 400, response.text
    assert counts(import_case) == (0, 0)


def test_empty_statement_still_checks_account_currency(import_case):
    xml = statement(entry='', balances=balance('OPBD', '0') + balance('CLBD', '0')).replace('EUR', 'CHF')
    response = upload(import_case, xml, fmt='CAMT')
    assert response.status_code == 422, response.text
    assert counts(import_case) == (0, 0)
