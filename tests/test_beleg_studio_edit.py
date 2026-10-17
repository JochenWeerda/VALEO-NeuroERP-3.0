"""One edit definition for nine variants; linked position replacement fails atomically."""
import pytest
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import engine
from app.core.screen_definitions_beleg import BELEGARTEN, build_beleg_screen_definition
from test_docflow_update_guard import sql_doc, client, state  # noqa: F401


@pytest.mark.parametrize('kind', sorted(BELEGARTEN))
def test_all_variants_use_the_same_registered_edit_command(kind):
    definition = build_beleg_screen_definition(kind)
    edit = next(action for action in definition['actions'] if action['key'] == 'bearbeiten')
    assert edit['method'] == 'PUT'
    assert edit['kommando'] == 'docflow.update'
    assert edit['permission'] == 'belege.bearbeiten'
    assert edit['forbiddenForAgents'] is True
    table = next(field for field in edit['inputFields'] if field['key'] == 'items')
    assert table['tableEditing'] == {'allowAdd': True, 'allowDelete': True, 'maxRows': 200}
    assert ('unit_price' in {field['key'] for field in table['rowFields']}) == BELEGARTEN[kind].mit_preisen


@pytest.mark.integration
@pytest.mark.needs_live_db
def test_source_linked_position_cannot_be_replaced_or_lose_its_reference(sql_doc, client):
    with Session(engine) as db:
        db.execute(text('UPDATE domain_docflow.document_items SET source_line_id=:source WHERE tenant_id=:t AND header_id=:id'),
                   {'source': sql_doc.id, 't': sql_doc.tenant, 'id': sql_doc.id})
        db.commit()
    before = state(sql_doc)
    response = client.put('/docflow/' + sql_doc.id, json={
        'expected_version': 1, 'idempotency_key': 'no-linked-replacement',
        'currency': 'USD', 'items': [{'article_number': 'REPLACED', 'quantity': 2}],
    })
    assert response.status_code == 409, response.text
    assert state(sql_doc) == before


@pytest.mark.integration
@pytest.mark.needs_live_db
def test_document_link_prevents_replacement_before_any_header_or_outbox_change(sql_doc, client):
    link_id = str(uuid4())
    with Session(engine) as db:
        item = db.execute(text('SELECT id FROM domain_docflow.document_items WHERE tenant_id=:t AND header_id=:id'),
                          {'t': sql_doc.tenant, 'id': sql_doc.id}).scalar_one()
        db.execute(text('''INSERT INTO domain_docflow.document_links
            (id, tenant_id, from_header_id, to_header_id, relation_type, from_item_id, to_item_id, quantity_linked)
            VALUES (:link, :t, :id, :id, 'conversion', :item, :item, 1)'''),
                   {'link': link_id, 't': sql_doc.tenant, 'id': sql_doc.id, 'item': item})
        db.commit()
    try:
        before = state(sql_doc)
        response = client.put('/docflow/' + sql_doc.id, json={
            'expected_version': 1, 'idempotency_key': 'no-chain-replacement', 'currency': 'USD', 'items': [],
        })
        assert response.status_code == 409, response.text
        assert state(sql_doc) == before
    finally:
        with Session(engine) as db:
            db.execute(text('DELETE FROM domain_docflow.document_links WHERE tenant_id=:t AND id=:link'),
                       {'t': sql_doc.tenant, 'link': link_id})
            db.commit()
