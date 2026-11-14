"""Vertrag der Sortenobjektmaske mit dem bestehenden Agrar-CRUD."""
import json
from pathlib import Path

from app.api.v1.endpoints.agrar_varieties import VarietyIn
from app.core.screen_definitions_sorte import build_agrar_sorte_stamm
from app.core.screen_definitions import get_screen_definition


def test_sorte_registry_fixture_and_put_contract():
    definition = build_agrar_sorte_stamm()
    fixture = Path(__file__).resolve().parents[1] / 'packages/frontend-web/src/__tests__/fixtures/agrar-sorte-studio.json'
    registered = get_screen_definition(definition['id'])
    assert registered is not None
    assert json.loads(fixture.read_text(encoding='utf8')) == registered
    assert registered['dataSources'] == definition['dataSources']
    assert registered['actions'] == definition['actions']
    action = definition['actions'][0]
    assert action['commandEndpoint'] == '/api/v1/agrar/varieties/{entity_id}'
    assert action['method'] == 'PUT' and action['forbiddenForAgents'] is True
    assert {f['key'] for f in action['inputFields']} == set(VarietyIn.model_fields)
    assert {f['key'] for f in action['inputFields'] if f.get('required')} == {'variety_number', 'name'}
    assert next(f for f in definition['tabs'][0]['fields'] if f['key'] == 'aktiv')['readOnly'] is True
