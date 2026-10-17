"""Complete item reads must support lossless editing and immutable replay."""
import pytest
from app.api.v1.schemas.docflow_schemas import DocflowLineInput
from test_docflow_update_guard import sql_doc, client  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


def test_item_metadata_survives_full_read_edit_and_replay(sql_doc, client):
    line = {
        'article_number': 'SYNTHETIC', 'description': 'Synthetic metadata test',
        'quantity': 12.5, 'unit': 't', 'unit_price': 220,
        'discount_percent': 2.5, 'tax_rate': 7,
        'batch_id': 'synthetic-batch', 'charge': 'synthetic-charge',
        'expense_account': 'synthetic-account',
    }
    first = client.put('/docflow/' + sql_doc.id, json={
        'expected_version': 1, 'idempotency_key': 'metadata-first-update', 'items': [line],
    })
    assert first.status_code == 200, first.text
    read = client.get('/docflow/' + sql_doc.id)
    assert read.status_code == 200, read.text
    for response in (first, read):
        item = response.json()['items'][0]
        for key, value in line.items():
            assert item[key] == value, key

    # Use the same canonical input projection a client uses after a complete read.
    item = DocflowLineInput.model_validate(read.json()['items'][0]).model_dump()
    item['quantity'] = 13
    payload = {'expected_version': 2, 'idempotency_key': 'metadata-second-update', 'items': [item]}
    second = client.put('/docflow/' + sql_doc.id, json=payload)
    assert second.status_code == 200, second.text
    assert second.json()['items'][0]['batch_id'] == line['batch_id']
    assert second.json()['items'][0]['charge'] == line['charge']

    changed = {**item, 'batch_id': 'another-batch', 'charge': 'another-charge'}
    later = client.put('/docflow/' + sql_doc.id, json={
        'expected_version': 3, 'idempotency_key': 'metadata-third-update', 'items': [changed],
    })
    assert later.status_code == 200, later.text
    assert client.put('/docflow/' + sql_doc.id, json=payload).json() == second.json()
    assert client.get('/docflow/' + sql_doc.id).json()['items'][0]['charge'] == 'another-charge'


def test_old_items_without_metadata_remain_readable(sql_doc, client):
    response = client.get('/docflow/' + sql_doc.id)
    assert response.status_code == 200, response.text
    assert response.json()['items'][0]['batch_id'] is None
    assert response.json()['items'][0]['charge'] is None
