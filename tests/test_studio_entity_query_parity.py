"""Real signed collection queries: shared probe, existing transaction fixtures."""
import pytest
import sqlalchemy as sa
from app.services.studio_entity_commands import tables
from test_studio_entity_generation import entity, auth, command, values, path, subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


def create(entity, name, *, tenant=None):
    response = entity[0].post(path(entity) + '/actions/create', headers=auth(entity, tenant=tenant),
                              json=command({**values(), 'name': name}))
    assert response.status_code == 200, response.text
    return response.json()['result']


def test_runtime_page_and_cli_skip_address_the_same_rows(entity):
    for name in ['First', 'Second', 'Third']:
        create(entity, name)
    create(entity, 'Foreign only', tenant=entity[4])
    client, headers, url = entity[0], auth(entity), path(entity)
    all_rows = client.get(url, headers=headers).json()
    page = client.get(url, headers=headers, params={'limit': 1, 'page': 2})
    skip = client.get(url, headers=headers, params={'limit': 1, 'skip': 1})
    assert page.status_code == skip.status_code == 200
    assert page.json() == skip.json()
    assert page.json()['items'][0]['id'] == all_rows['items'][1]['id']
    assert page.json()['total'] == 3 and page.json()['skip'] == 1
    assert client.get(url, headers=headers, params={'limit': 1, 'page': 2, 'skip': 0}).status_code == 422
    assert client.get(url, headers=headers, params={'limit': 100, 'page': 1000001}).status_code == 422


def test_search_and_total_share_tenant_deactivation_and_literal_text_filters(entity):
    create(entity, 'Alpha%warehouse')
    create(entity, 'Alpha without percent')
    deleted = create(entity, 'Alpha%deleted')
    create(entity, 'Alpha%foreign', tenant=entity[4])
    client, headers, url = entity[0], auth(entity), path(entity)
    response = client.post(url + '/' + deleted['id'] + '/actions/delete', headers=headers,
                           json=command(version=1))
    assert response.status_code == 200, response.text
    result = client.get(url, headers=headers, params={'q': 'aLpHa%'}).json()
    assert result['total'] == 1
    assert [row['name'] for row in result['items']] == ['Alpha%warehouse']
    assert client.get(url, headers=headers, params={'q': "' OR 1=1 --"}).json()['total'] == 0
    assert client.get(url, headers=headers, params={'q': 'x' * 201}).status_code == 422


@pytest.mark.parametrize('kind', ['agent', 'service', None, 'unknown'])
def test_nonhuman_or_untyped_identity_cannot_bypass_disabled_agent_capability(entity, kind):
    token = entity[2].token(entity[3], changes={'roles': ['CRM_BEARBEITEN'], 'identity_type': kind})
    response = entity[0].post(path(entity) + '/actions/create', headers={'Authorization': 'Bearer ' + token},
                              json=command(values()))
    assert response.status_code == 403, response.text
    for table in tables(entity[5]):
        assert entity[1].scalar(sa.select(sa.func.count()).select_from(table)) == 0
