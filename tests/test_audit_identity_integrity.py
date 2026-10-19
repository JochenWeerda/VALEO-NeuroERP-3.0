"""Verified identities, tenant-local profile mapping, and real PostgreSQL errors."""
from uuid import uuid4
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.core.database import get_db
from app.core.tenant_binding import install_tenant_bindings
from app.core.akteur import gepruefter_akteur, bekannter_nutzer
from app.infrastructure.models import User, AuditLog
from app.api.v1.endpoints import sales_delivery_notes
from main import BearerAuthMiddleware
from test_gdpr_subject_boundary import keys, probe, subject_data  # noqa: F401


@pytest.fixture
def attestation_case(subject_data):
    _, db, provider, tenant, other_tenant, own, other, foreign = subject_data
    note, foreign_note = str(uuid4()), str(uuid4())
    for identity, tid in ((note, tenant), (foreign_note, other_tenant)):
        db.execute(text("INSERT INTO domain_sales.delivery_notes (id,tenant_id,delivery_note_number,delivery_date,status) VALUES (:id,:t,:nr,CURRENT_DATE,'posted')"), {'id': identity, 't': tid, 'nr': 'SYNTH-' + identity})
    db.commit()  # release only fixture savepoint, outer probe transaction still rolls back
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    app.include_router(sales_delivery_notes.router, prefix='/api/v1')
    def shared_db():
        try:
            yield db
        except Exception:
            db.rollback()
            raise
    app.dependency_overrides[get_db] = shared_db
    install_tenant_bindings(app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, db, provider, tenant, other_tenant, own, other, foreign, note, foreign_note


def headers(case, subject='human-a'):
    return {'Authorization': 'Bearer ' + case[2].token(case[3], changes={'sub': subject, 'roles': ['SALES_BEARBEITEN']})}


def print_note(case, **kwargs):
    return case[0].post(f'/api/v1/sales/delivery-notes/{case[8]}/print', params={'attestation': 'Synthetic verified reprint'}, headers=headers(case, **kwargs))


@pytest.mark.parametrize('long_subject', [False, True])
def test_attestation_keeps_provider_identity_and_local_fk(attestation_case, long_subject):
    case = attestation_case
    subject = 'human-a' + ('x' * 150 if long_subject else '')
    if long_subject:
        case[1].get(User, case[5]).keycloak_id = subject
        case[1].commit()
    assert gepruefter_akteur({'sub': subject}) == subject
    result = print_note(case, subject=subject)
    assert result.status_code == 200, result.text
    row = case[1].execute(text('SELECT created_by,changes FROM domain_audit.attestations WHERE tenant_id=:t AND entity_id=:e'), {'t': case[3], 'e': case[8]}).mappings().one()
    assert row['created_by'] == case[5]
    assert row['changes']['actor'] == {'subject': subject, 'tenant_id': case[3], 'issuer': 'https://tenant-identity.invalid/realm'}


@pytest.mark.parametrize('subject', ['missing-profile', 'synthetic-foreign'])
def test_missing_or_foreign_mapping_cannot_become_system(attestation_case, subject):
    case = attestation_case
    assert print_note(case, subject=subject).status_code == 403
    assert case[1].execute(text('SELECT COUNT(*) FROM domain_audit.attestations WHERE tenant_id=:t AND entity_id=:e'), {'t': case[3], 'e': case[8]}).scalar_one() == 0
    assert case[1].execute(text('SELECT status FROM domain_sales.delivery_notes WHERE id=:id'), {'id': case[8]}).scalar_one() == 'posted'
    assert case[0].post(f'/api/v1/sales/delivery-notes/{case[9]}/print', params={'attestation': 'Synthetic'}, headers=headers(case)).status_code == 404


def test_ambiguous_provider_mapping_is_denied(attestation_case):
    case = attestation_case
    db = case[1]
    subject = str(uuid4())
    db.get(User, case[5]).keycloak_id = subject
    db.add(User(id=subject, tenant_id=case[3], keycloak_id='synthetic-extra-'+str(uuid4()), username='synth-'+str(uuid4()), email=str(uuid4())+'@example.org', first_name='Synthetic', last_name='Ambiguous', roles=['user'], is_active=True))
    db.commit()
    assert print_note(case, subject=subject).status_code == 403


def test_sql_failure_is_not_converted_to_fallback_or_partial_print(attestation_case, monkeypatch):
    case = attestation_case
    db, execute = case[1], case[1].execute
    def fail_lookup(statement, *args, **kwargs):
        if 'SELECT id FROM domain_shared.users' in str(statement):
            return execute(text('SELECT * FROM synthetic_missing_actor_table'))
        return execute(statement, *args, **kwargs)
    monkeypatch.setattr(db, 'execute', fail_lookup)
    assert print_note(case).status_code == 500
    monkeypatch.setattr(db, 'execute', execute)
    assert db.execute(text('SELECT status FROM domain_sales.delivery_notes WHERE id=:id'), {'id': case[8]}).scalar_one() == 'posted'
    assert db.execute(text('SELECT COUNT(*) FROM domain_audit.attestations WHERE entity_id=:id'), {'id': case[8]}).scalar_one() == 0


def test_audit_metadata_agrees_with_migrated_schema():
    assert not AuditLog.__table__.c.user_id.foreign_keys
    assert not AuditLog.__table__.c.tenant_id.foreign_keys


def test_reason_and_verified_identity_are_required(attestation_case):
    case = attestation_case
    path = f'/api/v1/sales/delivery-notes/{case[8]}/print'
    assert case[0].post(path, headers=headers(case)).status_code == 400
    assert case[0].post(path, params={'attestation': 'Synthetic'}).status_code == 401
    assert case[1].execute(text('SELECT COUNT(*) FROM domain_audit.attestations WHERE entity_id=:id'), {'id': case[8]}).scalar_one() == 0
