"""Creation uses actual tenant-owned partners and the existing atomic command."""
from copy import deepcopy
from uuid import uuid4
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import engine
from app.core.exceptions import ValidationFailedError
from app.core.screen_definitions_beleg import BELEGARTEN, build_beleg_screen_definition
from app.services.docflow_creation_context import search_partners, validate_partner
from app.services.studio_validation import validate_studio_draft
from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest
from test_docflow_create_guard import context, create, request, counts  # noqa: F401
from test_docflow_update_guard import sql_doc  # noqa: F401


@pytest.fixture
def partners(context):
    customer, supplier = str(uuid4()), str(uuid4())
    with Session(engine) as db:
        db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) VALUES (:id,:t,:id,'SYNTHETIC Customer')"), {'id': customer, 't': context.tenant})
        db.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) VALUES (:id,:t,:id,'SYNTHETIC Supplier')"), {'id': supplier, 't': context.tenant})
        db.commit()
    try:
        yield customer, supplier
    finally:
        with Session(engine) as db:
            db.execute(text('DELETE FROM domain_crm.customers WHERE tenant_id=:t AND id=:id'), {'t': context.tenant, 'id': customer})
            db.execute(text('DELETE FROM domain_einkauf.lieferanten WHERE tenant_id=:t AND id=:id'), {'t': context.tenant, 'id': supplier})
            db.commit()


@pytest.mark.parametrize('kind', sorted(BELEGARTEN))
def test_every_variant_has_one_registered_creation_and_lookup(kind):
    definition = build_beleg_screen_definition(kind)
    creation = definition['creation']
    assert creation['adapter'] == 'docflow.create.v1'
    assert creation['endpoint'] == '/api/v1/docflow/'
    assert creation['permission'] == 'belege.bearbeiten'
    expected = 'supplier_id' if BELEGARTEN[kind].partnerrolle == 'lieferant' else 'customer_id'
    assert next(field for field in creation['fields'] if field['type'] == 'lookup')['key'] == expected
    assert creation['dataSources'][0]['endpoint'] == f'/api/v1/belege/{kind}/partner-auswahl'


@pytest.mark.parametrize('kind', ['sales_offer','purchase_order'])
@pytest.mark.integration
@pytest.mark.needs_live_db
def test_actual_partner_lookup_and_validation_are_tenant_bound(context, partners, kind):
    customer, supplier = partners
    field = 'customer_id' if kind == 'sales_offer' else 'supplier_id'
    identifier = customer if kind == 'sales_offer' else supplier
    payload = DocflowCreateRequest(doc_type=kind, doc_number='SYNTHETIC', **{field: identifier})
    with Session(engine) as db:
        result = search_partners(db, context.tenant, kind, 'SYNTHETIC', 25)
        assert result == [{'value': identifier, 'label': identifier + ' - SYNTHETIC ' + ('Customer' if kind == 'sales_offer' else 'Supplier')}]
        validate_partner(db, context.tenant, payload)
        assert search_partners(db, str(uuid4()), kind, 'SYNTHETIC', 25) == []
        with pytest.raises(ValidationFailedError):
            validate_partner(db, str(uuid4()), payload)


@pytest.mark.integration
@pytest.mark.needs_live_db
def test_bound_creation_checks_partner_before_any_business_effect(context, partners, monkeypatch):
    from app.core import screen_definitions
    from app.core.studio_release import definition_hash
    definition = build_beleg_screen_definition('sales_offer')
    monkeypatch.setattr(screen_definitions, 'get_screen_definition', lambda _id, **_kw: definition)
    binding = {'screen_id': definition['id'], 'definition_hash': definition_hash(definition)}
    before = counts(context)
    for change in ({}, {'customer_id': str(uuid4())}, {'supplier_id': partners[1]},
                   {'customer_id': partners[0], 'supplier_id': partners[1]}):
        with pytest.raises(ValidationFailedError):
            create(context, request(screen_context=binding, **change))
        assert counts(context) == before
    payload = request(screen_context=binding, customer_id=partners[0])
    first = create(context, payload)
    assert create(context, payload) == first
    assert counts(context) == tuple(number + 1 for number in before)


def test_creation_transport_cannot_be_changed_in_studio():
    from test_studio_document_catalog import candidate
    original = candidate('sales_offer')
    assert validate_studio_draft(original, native_screen_ids=set()) == []
    for path, value in [('endpoint','/api/v1/docflow/foreign'), ('permission',''), ('adapter','custom'), ('fields',[])]:
        changed = deepcopy(original)
        changed['creation'][path] = value
        assert validate_studio_draft(changed, native_screen_ids=set())


@pytest.mark.asyncio
async def test_definition_response_provides_server_proof_without_changing_definition(monkeypatch):
    from app.api.v1.endpoints import mask_screen_definition as endpoint
    from app.core.studio_release import definition_hash
    definition = build_beleg_screen_definition('sales_offer')
    original = deepcopy(definition)
    calls = []
    def lookup(mask_id, *, tenant_id):
        calls.append((mask_id, tenant_id))
        return definition
    monkeypatch.setattr(endpoint, 'get_screen_definition', lookup)
    response = await endpoint.get_mask_screen_definition('beleg__sales-offer', tenant_id='verified-tenant')
    assert calls == [('beleg/sales-offer', 'verified-tenant')]
    assert response['creationContext'] == {'screen_id': definition['id'], 'definition_hash': definition_hash(original)}
    assert definition == original and 'creationContext' not in definition


@pytest.mark.integration
@pytest.mark.needs_live_db
def test_partner_http_uses_verified_context_existing_roles_and_bounded_search(context, partners):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints import belege
    from app.core.database import get_db
    from app.core.tenant import get_tenant_id
    from app.auth.deps import get_current_user
    app = FastAPI()
    app.include_router(belege.router, prefix='/belege')
    app.dependency_overrides[get_tenant_id] = lambda: context.tenant
    actor = {'sub': 'synthetic', 'roles': ['SALES_BEARBEITEN']}
    app.dependency_overrides[get_current_user] = lambda: actor
    def database():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = database
    with TestClient(app) as http:
        result = http.get('/belege/sales_offer/partner-auswahl', params={'q':'SYNTHETIC','tenant_id':str(uuid4())})
        assert result.status_code == 200
        assert result.json()['items'][0]['value'] == partners[0]
        assert http.get('/belege/sales_offer/partner-auswahl?limit=51').status_code == 422
        actor['roles'] = ['LAGER_LESEN']
        assert http.get('/belege/sales_offer/partner-auswahl').status_code == 403
