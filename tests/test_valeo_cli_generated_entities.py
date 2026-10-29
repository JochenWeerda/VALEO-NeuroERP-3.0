"""CLI envelope parity for generated domain commands; no authentication proof here."""
import json
from uuid import UUID
import httpx
import pytest
from test_valeo_cli import run, HUMAN


class GeneratedServer:
    def __init__(self, operation='create', uncertain=False):
        self.operation, self.uncertain, self.calls = operation, uncertain, []

    def __call__(self, request):
        if request.url.path.endswith('/screen-definition'):
            part = '{entity_id}/' if self.operation != 'create' else ''
            return httpx.Response(200, json={'actions': [{
                'key': self.operation, 'commandEndpoint': '/api/v1/studio/entities/studio_fixture/' + part + 'actions/' + self.operation,
            }]})
        self.calls.append(request)
        if self.uncertain:
            raise httpx.ReadTimeout('Synthetic lost response', request=request)
        return httpx.Response(200, json={'success': True})


def execute(server, monkeypatch, *extra):
    monkeypatch.setenv('VALEO_API_URL', 'https://api.invalid')
    return run(['ausfuehren', 'tenant/studio_fixture', server.operation, '--id', 'row-1', '--ja', '--json', *extra],
               server, token=HUMAN, monkeypatch=monkeypatch)


def test_missing_cli_key_is_generated_and_returned_for_replay(monkeypatch):
    server = GeneratedServer()
    code, output = execute(server, monkeypatch)
    assert code == 0
    key = json.loads(output)['idempotenz']
    assert str(UUID(key)) == key
    assert json.loads(server.calls[0].content)['_idempotencyKey'] == key


def test_uncertain_result_exposes_exact_retry_key(monkeypatch):
    server = GeneratedServer(uncertain=True)
    code, output = execute(server, monkeypatch)
    assert code == 4
    key = json.loads(server.calls[0].content)['_idempotencyKey']
    assert '--idempotenz ' + key in output
    assert len(server.calls) == 1


@pytest.mark.parametrize('operation', ['update', 'delete'])
def test_displayed_version_required_and_forwarded(monkeypatch, operation):
    server = GeneratedServer(operation)
    code, _ = execute(server, monkeypatch)
    assert code == 2 and not server.calls
    code, _ = execute(server, monkeypatch, '--version', '7')
    assert code == 0
    assert json.loads(server.calls[0].content)['expected_version'] == 7


def test_explicit_key_preserved_instead_of_silently_replaced(monkeypatch):
    server = GeneratedServer()
    key = '00000000-0000-0000-0000-000000000007'
    code, _ = execute(server, monkeypatch, '--idempotenz', key)
    assert code == 0
    assert json.loads(server.calls[0].content)['_idempotencyKey'] == key
