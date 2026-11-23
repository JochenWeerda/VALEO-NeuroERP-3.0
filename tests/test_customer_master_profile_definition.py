"""Customer profile remains a single, versioned Studio surface and typed command."""
from app.core.customer_master_profile import master_fields, master_input_fields
from app.core.screen_definitions import build_crm_customer_360_screen_definition
from app.services.customer_master_profile_service import field_specs


def test_all_catalog_fields_are_visible_once_and_editable_fields_match_server():
    screen = build_crm_customer_360_screen_definition()
    fields = [f['key'] for tab in screen['tabs'] for f in tab.get('fields', [])
              if f['key'].startswith('partner_')]
    expected = {'partner_' + key for key in master_fields() if key not in {'tenant_id', 'partner_id'}}
    assert set(fields) == expected
    assert len(fields) == len(expected)
    inputs = master_input_fields()
    assert {f['key'][8:] for f in inputs} == set(field_specs())
    assert all(f.get('section') for f in inputs)
    assert all(f['type'] != 'currency' for f in inputs)
    assert any(f['key'] == 'partner_iban' for f in inputs)
    assert any(f['key'] == 'partner_blocked_for_invoice' for f in inputs)
    assert all(t['dataSourceKey'] == 'entity' for t in screen['tabs'] if t['key'].startswith('partner_'))


def test_profile_command_uses_existing_role_permission_and_concurrency_contract():
    screen = build_crm_customer_360_screen_definition()
    action = next(a for a in screen['actions'] if a['key'] == 'stammdaten_pflegen')
    assert action['permission'] == 'crm.customer.update'
    assert action['requiresIdempotencyKey'] and action['requiresExpectedVersion']
    assert action['auditReasonRequired']
    assert action['inputPrefill'] == 'entity'
    assert action['enabledWhen'] == {'path': 'business_partner_id', 'exists': True}
    source = next(s for s in screen['dataSources'] if s['key'] == 'entity')
    assert source['endpoint'].endswith('/{entity_id}/master-profile')
