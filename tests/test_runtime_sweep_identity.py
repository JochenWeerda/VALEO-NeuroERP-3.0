"""Runtime reports must prove authentication before classifying business paths."""
import json
import httpx
import pytest
from scripts import api_runtime_sweep as sweep


@pytest.mark.parametrize('status,payload', [(401, {}), (403, {}), (503, {}), (200, {}),
                                          (200, {'subject': 'synthetic', 'tenant_id': 'foreign'})])
def test_session_probe_rejects_missing_or_foreign_identity(status, payload):
    with httpx.Client(base_url='http://test', transport=httpx.MockTransport(lambda _: httpx.Response(status, json=payload))) as client:
        with pytest.raises((ValueError, httpx.HTTPError)):
            sweep.verify_session(client, 'own')


@pytest.mark.parametrize('code,expected', [(200, 0), (401, 1), (500, 1)])
def test_sweep_cannot_hide_authentication_failure(monkeypatch, tmp_path, code, expected):
    original = httpx.Client
    def respond(request):
        if request.url.path == '/api/v1/identity/session':
            return httpx.Response(200, json={'subject': 'synthetic', 'tenant_id': 'own'})
        if request.url.path == '/api/v1/openapi.json':
            return httpx.Response(200, json={'openapi': '3.1.0', 'paths': {'/business': {'get': {}}}})
        return httpx.Response(code, json={})
    monkeypatch.setattr(sweep.httpx, 'Client', lambda **kw: original(**kw, transport=httpx.MockTransport(respond)))
    monkeypatch.setattr(sweep, 'load_allowlist', lambda: ({}, set()))
    target = tmp_path / 'report.json'
    monkeypatch.setenv('SWEEP_ACCESS_TOKEN', 'synthetic-token-only')
    monkeypatch.setattr('sys.argv', ['sweep', '--base-url', 'http://test', '--tenant', 'own', '--output', str(target)])
    assert sweep.main() == expected
    report = json.loads(target.read_text())
    assert report['verified_session'] is True
    assert report['summary']['authentication_error'] == (1 if code == 401 else 0)
    assert 'synthetic-token-only' not in target.read_text()


@pytest.mark.parametrize('token', ['', 'dev-token'])
def test_no_legacy_identity(monkeypatch, token):
    monkeypatch.setenv('SWEEP_ACCESS_TOKEN', token)
    monkeypatch.setattr('sys.argv', ['sweep'])
    assert sweep.main() == 1


@pytest.mark.parametrize('case', ['not_ci', 'missing_configuration', 'denied', 'missing_token', 'success', 'sweep_failed'])
def test_ci_login_stays_in_memory_and_fails_closed(monkeypatch, capsys, case):
    from scripts.ci import runtime_sweep_authenticated as starter
    monkeypatch.delenv('SWEEP_ACCESS_TOKEN', raising=False)
    monkeypatch.setenv('CI', 'false' if case == 'not_ci' else 'true')
    monkeypatch.setenv('VALEO_USER_ADMIN', '' if case == 'missing_configuration' else 'synthetic@example.invalid')
    monkeypatch.setenv('VALEO_PASS_ADMIN', 'synthetic-password')
    calls = []
    def login(url, **kwargs):
        calls.append(url)
        assert url.startswith('http://localhost:8080/')
        assert kwargs['data']['password'] == 'synthetic-password'
        return httpx.Response(401 if case == 'denied' else 200,
                              request=httpx.Request('POST', url),
                              json={} if case == 'missing_token' else {'access_token': 'synthetic-private-token'})
    monkeypatch.setattr(starter.httpx, 'post', login)
    def run_sweep():
        import os
        assert os.environ['SWEEP_ACCESS_TOKEN'] == 'synthetic-private-token'
        return 1 if case == 'sweep_failed' else 0
    monkeypatch.setattr(starter, 'main', run_sweep)
    assert starter.run() == (0 if case == 'success' else 1)
    import os
    assert 'SWEEP_ACCESS_TOKEN' not in os.environ
    assert len(calls) == (0 if case in ('not_ci', 'missing_configuration') else 1)
    output = capsys.readouterr()
    assert 'synthetic-private-token' not in output.out + output.err
    assert 'synthetic-password' not in output.out + output.err
