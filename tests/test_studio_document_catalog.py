"""Only the pinned, currently registered document variant supplies its command policy."""
from copy import deepcopy

import pytest

from app.core.screen_definitions_beleg import BELEGARTEN
from app.core.studio_release import profile_errors
from app.services.studio_validation import validate_studio_draft


def candidate(variant='sales_invoice'):
    from app.services.studio_native_import import source_definition
    from app.core.screen_definitions_beleg import NATIVE_BELEG_TENANTS, screen_id
    definition = source_definition(next(iter(NATIVE_BELEG_TENANTS)), screen_id(variant))
    definition.update(id=f'tenant/{variant}', adapter={
        'type': 'native', 'sourceId': f'tenant/{variant}', 'temporary': True})
    return definition


@pytest.mark.parametrize('variant', BELEGARTEN)
def test_all_registered_document_variants_are_understood_without_granting_release(variant):
    definition = candidate(variant)
    assert validate_studio_draft(definition, native_screen_ids=set()) == []
    assert profile_errors(definition)  # No new document process profile is being claimed.


@pytest.mark.parametrize('field', [
    'commandEndpoint', 'method', 'commandBinding', 'kommando', 'permission',
    'enabledWhen', 'inputFields', 'folgebelegart',
])
def test_a_document_action_cannot_change_its_transport_state_or_input_contract(field):
    definition = candidate('sales_order')
    action = next(item for item in definition['actions'] if item['key'].startswith('umwandeln:'))
    action[field] = 'unregistered'
    assert validate_studio_draft(definition, native_screen_ids=set())


@pytest.mark.parametrize('field', ['forbiddenForAgents', 'requiresConfirmation', 'auditReasonRequired'])
def test_document_action_protection_cannot_be_removed(field):
    definition = candidate()
    action = next(item for item in definition['actions'] if item['key'] == 'stornieren')
    assert action[field] is True
    action.pop(field)
    assert validate_studio_draft(definition, native_screen_ids=set())


def test_another_variants_sources_and_unregistered_queries_are_rejected():
    for endpoint in ['/api/v1/belege/purchase_invoice/{entity_id}/kopf',
                     '/api/v1/belege/sales_invoice/{entity_id}/kopf?tenant_id=foreign']:
        definition = candidate()
        definition['dataSources'][0]['endpoint'] = endpoint
        assert any('datenquelle_nicht_im_katalog' in value
                   for value in validate_studio_draft(definition, native_screen_ids=set()))


def test_document_sources_and_actions_do_not_become_a_global_free_allowlist():
    definition = candidate()
    definition.pop('documentVariant')
    violations = validate_studio_draft(definition, native_screen_ids=set())
    assert any('datenquelle_nicht_im_katalog' in value for value in violations)
    assert violations


@pytest.mark.parametrize('mutation', ['domain', 'variant', 'boolean_type', 'binding'])
def test_a_template_reference_cannot_be_used_for_another_business_case(mutation):
    definition = candidate()
    if mutation == 'domain':
        definition['domain'] = 'agrar'
    elif mutation == 'variant':
        definition['variant']['belegart'] = 'goods_receipt'
    elif mutation == 'boolean_type':
        definition['variant']['mitPreisen'] = 1
    else:
        definition['documentVariant']['baseHash'] = '0' * 64
    assert 'belegvariantenbindung_ungueltig' in validate_studio_draft(definition, native_screen_ids=set())


def test_cosmetic_changes_and_more_restrictive_actions_remain_possible():
    definition = candidate()
    definition['title'] = 'Rechnung mit neuer Beschriftung'
    definition['layout']['density'] = 'comfortable'
    definition['actions'][0]['disabled'] = True
    assert validate_studio_draft(definition, native_screen_ids=set()) == []


def test_a_pinned_old_template_cannot_hide_a_new_stricter_registered_command(monkeypatch):
    from app.core import screen_definitions_beleg as builder
    definition = candidate()
    real_builder = builder.build_beleg_screen_definition
    def changed(variant):
        result = deepcopy(real_builder(variant))
        result['actions'][0]['dangerLevel'] = 'critical'
        return result
    monkeypatch.setattr(builder, 'build_beleg_screen_definition', changed)
    assert 'belegvariantenbindung_ungueltig' in validate_studio_draft(definition, native_screen_ids=set())
