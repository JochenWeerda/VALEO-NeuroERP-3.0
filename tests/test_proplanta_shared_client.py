"""The API must use the integration's configured transport and synchronized cache."""
import asyncio

from app.domains.agrar.api import psm_proplanta as api
from app.integrations import proplanta_psm_client as integration


def test_api_uses_configured_integration_client(monkeypatch):
    assert api.psm_client is integration.psm_client
    monkeypatch.setattr(integration, 'PROPLANTA_PSM_URL', 'https://example.invalid/psm')
    monkeypatch.setattr(api.psm_client, 'mcp_server_name', 'test-provider')
    monkeypatch.setattr(api.psm_client, '_tool_caller', lambda *_: {})
    monkeypatch.setattr(api.psm_client, '_cache', {
        'synthetic': integration.PSMData({'id': 'synthetic', 'name': 'Synthetic item'})
    })
    result = asyncio.run(api.list_proplanta_psm(status=None, manufacturer=None, hazard_class=None, limit=50))
    assert [item['id'] for item in result] == ['synthetic']
    assert asyncio.run(api.get_proplanta_psm_status())['configured'] is True


def test_api_remains_unconfigured_without_real_transport(monkeypatch):
    monkeypatch.setattr(api.psm_client, '_tool_caller', None)
    assert asyncio.run(api.get_proplanta_psm_status())['configured'] is False
