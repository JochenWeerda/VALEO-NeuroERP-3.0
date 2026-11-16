"""Local public OIDC configuration; no identity, network or database mutation."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

class PreviewLoader(yaml.SafeLoader):
    pass

PreviewLoader.add_constructor('!reset', lambda loader, node: loader.construct_sequence(node) if isinstance(node, yaml.SequenceNode) else None)
PreviewLoader.add_constructor('!override', lambda loader, node: loader.construct_sequence(node))

def preview():
    return yaml.load((ROOT/'docker-compose.local-preview.yml').read_text(encoding='utf-8'), Loader=PreviewLoader)['services']

def test_public_identity_origin_is_shared_by_all_three_participants():
    services = preview()
    origin = 'http://localhost:${VALEO_LOCAL_IDENTITY_PORT:-8081}'
    assert services['keycloak']['ports'] == ['127.0.0.1:${VALEO_LOCAL_IDENTITY_PORT:-8081}:8080']
    assert services['keycloak']['environment']['KC_HOSTNAME'] is None
    assert services['keycloak']['environment']['KC_HOSTNAME_URL'] == origin
    issuer = origin+'/realms/valeo-neuro-erp'
    assert services['backend']['environment']['OIDC_ISSUER_URL'] == issuer
    assert services['frontend-web']['build']['args'] == {
        'VITE_OIDC_DISCOVERY_URL': issuer+'/.well-known/openid-configuration',
        'VITE_OIDC_CLIENT_ID': 'valeo-neuro-erp-frontend'}

def test_provider_settings_are_available_before_build_without_reinstalling_dependencies():
    dockerfile = (ROOT/'Dockerfile.frontend').read_text(encoding='utf-8')
    install = dockerfile.index('RUN pnpm install')
    build = dockerfile.index('RUN pnpm run routes:generate')
    for setting in ('VITE_OIDC_DISCOVERY_URL', 'VITE_OIDC_CLIENT_ID'):
        assert install < dockerfile.index('ARG '+setting) < build
        assert setting+'=${'+setting+'}' in dockerfile
    assert 'VITE_OIDC_REDIRECT_URI' not in preview()['frontend-web']['build']['args']

def test_profile_does_not_disable_authentication_or_change_provider_internal_port():
    services=preview()
    assert services['backend']['volumes']==[]
    assert '--workers' in services['backend']['command']
    assert services['keycloak']['ports'][0].endswith(':8080')
    assert set(services['backend']['environment'])=={'OIDC_ISSUER_URL'}
    assert not any('SECRET' in key or 'PASSWORD' in key or 'TOKEN' in key
                   for key in services['frontend-web']['build']['args'])
