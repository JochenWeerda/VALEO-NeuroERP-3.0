"""Creation replay uses the shared probe and only the fixture's own rows."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.v1.endpoints.docflow import DocflowCreateRequest, DocflowLineInput
from app.core.database import engine
from app.core.exceptions import ConflictError
from app.services.docflow_service import DocflowService
from test_docflow_update_guard import client, sql_doc  # noqa: F401 -- shared owned-row fixture

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

@pytest.fixture
def context(sql_doc):
    try:
        yield sql_doc
    finally:
        with Session(engine) as db:
            db.execute(text('DELETE FROM domain_docflow.create_request_idempotency WHERE tenant_id=:t'), {'t': sql_doc.tenant})
            db.commit()


def request(**changes):
    return DocflowCreateRequest(doc_type='sales_offer', doc_number='SYNTH-CREATE',
        idempotency_key='synthetic-create-key', items=[DocflowLineInput(article_number='SYNTH', quantity=2, unit_price=10)], **changes)


def create(context, payload=None, actor='synthetic-editor'):
    with Session(engine) as db:
        return DocflowService(db, context.tenant, actor).create_document_snapshot(payload or request())


def counts(context):
    with Session(engine) as db:
        return tuple(db.execute(text(sql), {'t': context.tenant}).scalar_one() for sql in [
            'SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id=:t',
            'SELECT count(*) FROM domain_docflow.document_command_log WHERE tenant_id=:t',
            "SELECT count(*) FROM outbox_events WHERE tenant_id=:t AND event_type='docflow.document.created'",
        ])


def test_replay_is_immutable_after_later_edit(context):
    first = create(context)
    with Session(engine) as db:
        svc=DocflowService(db,context.tenant,'synthetic-editor')
        from app.api.v1.endpoints.docflow import DocflowUpdateRequest
        svc.update_document(first['header']['id'], DocflowUpdateRequest(expected_version=1,
            idempotency_key='later-create-edit',currency='USD'))
    assert create(context)==first
    assert first['header']['version']==1
    assert counts(context)==(2,3,2)


@pytest.mark.parametrize('change', ['body','actor'])
def test_changed_content_or_actor_conflicts(context,change):
    create(context)
    with pytest.raises(ConflictError):
        create(context,request(currency='USD') if change=='body' else None,
               actor='other-synthetic' if change=='actor' else 'synthetic-editor')
    assert counts(context)==(2,2,2)


def test_concurrent_same_key_has_one_document(context):
    barrier=Barrier(2)
    def worker():
        barrier.wait(timeout=10)
        return create(context)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:worker(),range(2)))
    assert results[0]==results[1]
    assert counts(context)==(2,2,2)


@pytest.mark.parametrize('method',['upsert_outbox_event','store_idempotent_response'])
def test_failure_rolls_back_every_business_effect(context,monkeypatch,method):
    before=counts(context)
    def fail(*args,**kwargs):raise RuntimeError('synthetic-failure')
    monkeypatch.setattr(DocflowService,method,fail)
    with pytest.raises(RuntimeError):create(context)
    assert counts(context)==before


def test_old_key_without_content_proof_is_not_silently_replayed(context):
    with Session(engine) as db:
        svc=DocflowService(db,context.tenant,'synthetic-editor')
        svc.store_create_idempotency('synthetic-create-key',context.id);db.commit()
    with pytest.raises(ConflictError):create(context)


def test_body_actor_does_not_replace_verified_actor(context):
    result=create(context,request(created_by='forged-caller'))
    assert result['header']['created_by']=='synthetic-editor'
    assert create(context,request(created_by='another-forged-caller'))==result


def test_http_immutable_replay_and_conflict(context,client):
    body=request().model_dump(mode='json')
    first=client.post('/docflow/',json=body)
    assert first.status_code==200,first.text
    from app.api.v1.endpoints.docflow import DocflowUpdateRequest
    with Session(engine) as db:
        DocflowService(db,context.tenant,'synthetic-editor').update_document(first.json()['id'],
            DocflowUpdateRequest(expected_version=1,idempotency_key='http-create-update',currency='USD'))
    assert client.post('/docflow/',json=body).json()==first.json()
    assert client.post('/docflow/',json={**body,'currency':'USD'}).status_code==409


def test_http_error_redacts_and_rolls_back(context,client,monkeypatch):
    before=counts(context)
    def fail(*args,**kwargs):raise RuntimeError('synthetic-private-value')
    monkeypatch.setattr(DocflowService,'upsert_outbox_event',fail)
    response=client.post('/docflow/',json=request().model_dump(mode='json'))
    assert response.status_code==500
    assert response.json()['detail']=='Document create failed'
    assert 'synthetic-private-value' not in response.text
    assert counts(context)==before


def test_http_permissions_before_replay(context,client):
    from app.auth.deps import get_current_user
    create(context)
    client.app.dependency_overrides[get_current_user]=lambda:{'sub':'synthetic-editor','roles':[]}
    assert client.post('/docflow/',json=request().model_dump(mode='json')).status_code==403
