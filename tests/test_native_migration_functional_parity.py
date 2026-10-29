"""Retain the real, previously delivered business transports through parent migration."""
import json
from pathlib import Path

import pytest

from app.core.screen_definitions import get_screen_definition
from app.api.v1.schemas.mask_data_contracts import MaskDataReadIn
from app.services.mask_data_read import resolve_source

FIXTURE = json.loads((Path(__file__).parent / 'fixtures/native_migration_transports.json').read_text(encoding='utf-8'))
TRANSPORT_FIELDS = ('commandEndpoint', 'commandBinding', 'inputFlow', 'inputFields', 'method', 'permission',
                    'forbiddenForAgents', 'auditReasonRequired', 'humanApprovalRequired', 'requiresConfirmation')


@pytest.mark.parametrize('case', FIXTURE['screens'], ids=lambda item: item['screen_id'])
def test_domain_actions_and_creation_survive_parent_shell(case):
    definition = get_screen_definition(case['screen_id'])
    assert definition is not None
    actual = {action['key']: action for action in definition.get('actions', [])}
    for old in case['actions']:
        if not (old.get('commandEndpoint') or old.get('inputFlow')):
            continue
        assert old['key'] in actual, f"Lost business action {case['screen_id']}:{old['key']}"
        for field in TRANSPORT_FIELDS:
            if field in {'forbiddenForAgents', 'auditReasonRequired', 'humanApprovalRequired', 'requiresConfirmation'} and old.get(field) is not True:
                continue  # Current central governance may require stronger safeguards.
            assert actual[old['key']].get(field) == old.get(field), (case['screen_id'], old['key'], field)
    if case['creation_changed']:
        assert definition.get('creation') == case['creation']


def test_datev_uses_real_export_not_unrelated_reconciliation():
    definition = get_screen_definition('finance/datev-export')
    action, = definition['actions']
    assert action['download']['endpoint'] == '/api/v1/finance/datev-export'
    assert action['download']['contentField'] == 'csv'
    assert action['download']['filenameField'] == 'filename'
    assert action['permission'] == 'finance.datev.export'
    assert [option['value'] for option in action['inputFields'][0]['options']] == ['alle', 'debitor', 'kreditor']
    assert 'EXTF' in definition['subtitle']
    assert not definition['tables']  # Never display a made-up id/name/status table over reconciliation.


@pytest.mark.parametrize('typ', ['alle', 'debitor', 'kreditor'])
def test_datev_cli_mcp_read_sources_use_identical_guarded_api(typ):
    resolved = resolve_source(MaskDataReadIn(screen_id='finance/datev-export', source_key='export-' + typ), 'synthetic-tenant')
    assert resolved.startswith('/api/v1/finance/datev-export?')
    assert 'typ=' + typ in resolved
    assert 'tenant_id' not in resolved
