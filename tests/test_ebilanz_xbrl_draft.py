"""Official concept provenance and real XML draft contracts, without DB/network."""
from datetime import date
import json
from xml.etree import ElementTree as ET

import pytest

from app.services import ebilanz_xbrl_service as xbrl
from scripts.build_ebilanz_taxonomy_catalog import build, render, SHA256


def facts():
    return dict(zip(xbrl.CORE_FIELDS, ['Test & <Betrieb>', 'Deutschland', '2026-01-01', '2026-12-31']))


def draft(values=None, **options):
    return xbrl.build_draft(values or facts(), options.get('start', date(2026, 1, 1)),
                            options.get('end', date(2026, 12, 31)), options.get('identifier', 'Test-Entity'),
                            options.get('scheme', 'https://example.invalid/entity'))


def test_official_catalog_provenance_names_labels_and_paging():
    data = json.loads(xbrl.CATALOG.read_text(encoding='utf-8'))
    assert data['source_sha256'] == SHA256 and data['version'] == '6.9'
    assert len(data['concepts']) == 3944
    assert len({row['element'] for row in data['concepts']}) == 3944
    assert all(row['namespace'] == xbrl.NS[row['element'].split(':')[0]] for row in data['concepts'])
    assert all(row['label'] for row in data['concepts'])
    assert set(xbrl.CORE_FIELDS) <= set(xbrl._catalog())
    assert 'de-gcd:genInfo.doc.id.companyId.companyName' not in xbrl._catalog()
    assert xbrl.catalog_page(2, 2) == data['concepts'][2:4]
    assert xbrl.catalog_page(100, 3944) == []
    first = xbrl.catalog_page(1, 0); first[0]['label'] = 'changed'
    assert xbrl.catalog_page(1, 0)[0]['label'] != 'changed'


def test_generator_rejects_unverified_package_before_parsing(tmp_path):
    package = tmp_path/'bad.zip'; package.write_bytes(b'unverified')
    with pytest.raises(ValueError, match='SHA256'):
        build(package)


def test_catalog_render_does_not_mutate_input_and_is_deterministic():
    data = json.loads(xbrl.CATALOG.read_text(encoding='utf-8'))
    assert render(data) == render(data) == xbrl.CATALOG.read_text(encoding='utf-8')


def test_xml_is_deterministic_qualified_escaped_and_period_bound():
    content = draft()
    assert content == draft(dict(reversed(list(facts().items()))))
    root = ET.fromstring(content)
    assert root.tag == '{'+xbrl.NS['xbrli']+'}xbrl'
    assert root.find('de-gcd:genInfo.company.id.name', xbrl.NS).text == 'Test & <Betrieb>'
    assert len(root.findall('link:schemaRef', xbrl.NS)) == 2
    assert len(root.findall('xbrli:context', xbrl.NS)) == 2
    assert root.find("xbrli:context[@id='duration']/xbrli:period/xbrli:startDate", xbrl.NS).text == '2026-01-01'
    assert root.find("xbrli:context[@id='instant']/xbrli:period/xbrli:instant", xbrl.NS).text == '2026-12-31'
    assert all(e.get('contextRef') == 'duration' for e in root if e.tag.startswith('{'+xbrl.NS['de-gcd']))


def test_numeric_and_nil_facts_use_appropriate_context_and_units():
    values = facts()
    name = next(n for n, c in xbrl._catalog().items() if c['typ'] == 'xbrli:monetaryItemType' and
                not c['abstract'] and c['periodType'] == 'instant' and c['substitutionGroup'] == 'xbrli:item')
    values[name] = '-1234.50'
    root = ET.fromstring(draft(values)); item = root.find(name, xbrl.NS)
    assert item.text == '-1234.50'
    assert item.attrib == {'contextRef': 'instant', 'unitRef': 'EUR', 'decimals': 'INF'}
    values[name] = None
    item = ET.fromstring(draft(values)).find(name, xbrl.NS)
    assert item.get('{'+xbrl.NS['xsi']+'}nil') == 'true' and item.text is None


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '1e100', '1,23', '<bad>', ''])
def test_numeric_lexical_errors_fail(value):
    name = next(n for n, c in xbrl._catalog().items() if c['typ'] == 'xbrli:monetaryItemType' and
                not c['abstract'] and c['substitutionGroup'] == 'xbrli:item')
    with pytest.raises(ValueError):
        xbrl.fact_text(name, value)


@pytest.mark.parametrize('value', ['2026-02-30', '20260101', ' 2026-01-01', '2026-01-01T12:00'])
def test_date_lexical_errors_fail(value):
    with pytest.raises(ValueError):
        xbrl.fact_text(xbrl.CORE_FIELDS[2], value)


@pytest.mark.parametrize('value', ['\x00', '\ud800', '\uffff'])
def test_invalid_xml_characters_are_rejected(value):
    with pytest.raises(ValueError):
        xbrl.fact_text(xbrl.CORE_FIELDS[0], value)


def test_unknown_abstract_and_tuple_concepts_are_rejected():
    for name in ['de-gcd:invented', 'de-gcd:genInfo.doc', 'de-gcd:genInfo.report.id.statementType']:
        with pytest.raises(ValueError):
            xbrl.fact_text(name, 'value')


def test_conflicting_period_and_unsupported_taxonomy_year_fail():
    with pytest.raises(ValueError, match='widersprechen'):
        draft(end=date(2026, 12, 30))
    with pytest.raises(ValueError, match='2025/2026'):
        draft(start=date(2024, 1, 1))
    with pytest.raises(ValueError):
        draft(scheme='file:///secret')
    with pytest.raises(ValueError):
        draft(identifier='invalid\x00identifier')


def test_missing_core_field_fails_without_inventing_data():
    values = facts(); del values[xbrl.CORE_FIELDS[0]]
    with pytest.raises(ValueError, match='Entwurfsvoraussetzung'):
        draft(values)


def test_integer_and_boolean_facts_have_valid_xml_lexical_values():
    name = 'de-gcd:genInfo.company.id.shareholder.currentnumber'
    assert xbrl.fact_text(name, '+01.0') == '1'
    flag = 'de-gcd:genInfo.report.id.statementType.restated'
    assert xbrl.fact_text(flag, '1') == 'true'
    assert xbrl.fact_text(flag, '0') == 'false'
    with pytest.raises(ValueError):
        xbrl.fact_text(flag, 'yes')


@pytest.mark.parametrize('value', ['0', '-1', '1.5'])
def test_positive_integer_facts_cannot_be_zero_negative_or_fractional(value):
    with pytest.raises(ValueError):
        xbrl.fact_text('de-gcd:genInfo.company.id.shareholder.currentnumber', value)


@pytest.mark.parametrize('character', ['\x01', '\ud800', '\uffff'])
def test_entity_scheme_cannot_inject_invalid_xml_characters(character):
    with pytest.raises(ValueError):
        draft(scheme='https://example.invalid/' + character)
