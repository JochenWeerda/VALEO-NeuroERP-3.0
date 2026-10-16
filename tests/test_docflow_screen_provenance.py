"""Screen provenance follows the verified tenant and immutable creation audit."""
from copy import deepcopy
import pytest
from app.core.studio_release import definition_hash
from app.core.exceptions import ConflictError, ValidationFailedError
from app.api.v1.schemas.docflow_screen_context import DocflowScreenContextIn
from app.services.docflow_screen_provenance import resolve_screen_context, read_screen_context
from app.services.docflow_service import DocflowService
from sqlalchemy.orm import Session
from app.core.database import engine
from test_docflow_create_guard import context, create, request
from test_docflow_update_guard import sql_doc, client

pytestmark=[pytest.mark.integration,pytest.mark.needs_live_db]

@pytest.fixture
def screen(monkeypatch):
    from app.core import screen_definitions
    definition={'id':'beleg/sales-offer','variant':{'belegart':'sales_offer'},
                'documentVariant':{'variantId':'sales_offer','variantVersion':'1.0.0','baseVersion':'1.0.0'}}
    calls=[]
    def lookup(screen_id,*,tenant_id):
        calls.append((screen_id,tenant_id))
        return deepcopy(definition) if screen_id==definition['id'] else None
    monkeypatch.setattr(screen_definitions,'get_screen_definition',lookup)
    return definition,calls


def binding(definition):
    return {'screen_id':definition['id'],'definition_hash':definition_hash(definition)}


def test_lookup_is_bound_to_verified_tenant(screen):
    definition,calls=screen
    result=resolve_screen_context(DocflowScreenContextIn(**binding(definition)),'sales_offer','verified-tenant')
    assert calls==[(definition['id'],'verified-tenant')]
    assert result['document_variant']==definition['documentVariant']
    result['document_variant']['baseVersion']='changed'
    assert definition['documentVariant']['baseVersion']=='1.0.0'


@pytest.mark.parametrize('case',['missing','hash','type'])
def test_unknown_changed_or_wrong_document_kind_rejected(screen,case):
    definition,_=screen;body=binding(definition)
    if case=='missing':body['screen_id']='tenant/unpublished'
    if case=='hash':body['definition_hash']='0'*64
    with pytest.raises(ConflictError if case=='hash' else ValidationFailedError):
        resolve_screen_context(DocflowScreenContextIn(**body),'purchase_order' if case=='type' else 'sales_offer','own')


def test_real_registry_does_not_grant_native_test_mask_to_other_tenant():
    context=DocflowScreenContextIn(screen_id='beleg/sales-offer',definition_hash='0'*64)
    with pytest.raises(ValidationFailedError):resolve_screen_context(context,'sales_offer','synthetic-unapproved-tenant')


def test_provenance_persists_and_replays_after_registry_changes(context,screen,client):
    definition,_=screen;body=request(screen_context=binding(definition)).model_dump(mode='json')
    first=client.post('/docflow/',json=body)
    assert first.status_code==200,first.text
    expected=first.json()['screen_context']
    assert expected['document_variant']['variantVersion']=='1.0.0'
    definition['documentVariant']['variantVersion']='2.0.0'
    assert client.post('/docflow/',json=body).json()==first.json()
    fetched=client.get('/docflow/'+first.json()['id'])
    assert fetched.status_code==200
    assert fetched.json()['screen_context']==expected
    with Session(engine) as db:
        assert read_screen_context(DocflowService(db,context.tenant),first.json()['id'])==expected
        assert read_screen_context(DocflowService(db,'synthetic-other'),first.json()['id']) is None


def test_legacy_documents_get_no_invented_provenance(context,client):
    response=client.get('/docflow/'+context.id)
    assert response.status_code==200
    assert response.json()['screen_context'] is None


def test_input_cannot_supply_its_own_release_proof(context,screen,client):
    definition,_=screen
    bad={**binding(definition),'studio_release':{'candidateRevision':'forged'}}
    response=client.post('/docflow/',json=request().model_dump(mode='json')|{'screen_context':bad})
    assert response.status_code==422


def test_actual_native_definition_resolves_exact_version():
    from app.core.screen_definitions import get_screen_definition
    tenant='00000000-0000-0000-0000-000000000051'
    definition=get_screen_definition('beleg/sales-offer',tenant_id=tenant)
    assert definition is not None
    result=resolve_screen_context(DocflowScreenContextIn(**binding(definition)),'sales_offer',tenant)
    assert result['document_variant']['variantVersion']=='1.0.0'


def test_pre_provenance_request_hash_remains_replayable(context):
    from uuid import uuid5,NAMESPACE_URL
    import json
    body=request()
    legacy=body.model_dump(mode='json',exclude={'idempotency_key','created_by','screen_context'})
    legacy['actor']='synthetic-editor'
    resource=str(uuid5(NAMESPACE_URL,json.dumps([context.tenant,body.idempotency_key])))
    with Session(engine) as db:
        svc=DocflowService(db,context.tenant,'synthetic-editor')
        snapshot=json.loads(json.dumps({'header':svc.fetch_header(context.id),'items':svc.fetch_items(context.id),
            'pos_compliance':None},default=str))
        svc.store_create_idempotency(body.idempotency_key,context.id)
        svc.store_idempotent_response('create',resource,body.idempotency_key,snapshot,legacy);db.commit()
    assert create(context)==snapshot
