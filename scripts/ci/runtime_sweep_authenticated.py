"""CI-only provider login; pass the token to the sweep solely in process memory."""
import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.api_runtime_sweep import main


def run() -> int:
    if os.environ.get('CI') != 'true':
        print('CI-Anmeldung ist ausschliesslich im isolierten CI-Job erlaubt.', file=sys.stderr)
        return 1
    username, password = os.getenv('VALEO_USER_ADMIN'), os.getenv('VALEO_PASS_ADMIN')
    if not username or not password:
        print('Synthetische CI-Anmeldekonfiguration fehlt.', file=sys.stderr)
        return 1
    try:
        response = httpx.post('http://localhost:8080/realms/valeo-neuro-erp/protocol/openid-connect/token',
                              data={'grant_type': 'password', 'client_id': 'valeo-neuro-erp-frontend',
                                    'username': username, 'password': password, 'scope': 'openid'}, timeout=30)
        response.raise_for_status()
        token = response.json().get('access_token')
        if not isinstance(token, str) or not token:
            raise ValueError('missing access token')
        os.environ['SWEEP_ACCESS_TOKEN'] = token
        return main()
    except (httpx.HTTPError, ValueError):
        print('Provider-Anmeldung fehlgeschlagen; kein Runtime-Nachweis.', file=sys.stderr)
        return 1
    finally:
        os.environ.pop('SWEEP_ACCESS_TOKEN', None)


if __name__ == '__main__':
    sys.exit(run())
