"""Verified identities, tenant-local profile mapping, and real PostgreSQL errors.

Seit BELEG-052 (10.11.2026) ueber den Belegdruck mit Druckvermerk (DocFlow-Lieferschein, Nachdruck mit Begruendung)
statt ueber den entfernten Altweg /sales/delivery-notes/{id}/print.
"""
from uuid import uuid4
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.core.database import get_db
from app.core.tenant_binding import install_tenant_bindings
from app.core.akteur import gepruefter_akteur, bekannter_nutzer
from app.infrastructure.models import User, AuditLog
from app.api.v1.endpoints import belege
from main import BearerAuthMiddleware
from test_gdpr_subject_boundary import keys, probe, subject_data  # noqa: F401


@pytest.fixture
def attestation_case(subject_data):
    _, db, provider, tenant, other_tenant, own, other, foreign = subject_data
    note, foreign_note = str(uuid4()), str(uuid4())
    for identity, tid in ((note, tenant), (foreign_note, other_tenant)):
        # Schon einmal gedruckt: Jeder weitere Druck ist ein Nachdruck und braucht Begruendung und Identitaet.
        db.execute(text("INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number, status, "
                        "source_system, currency, total_net, total_tax, total_gross, document_date, version, print_count, "
                        "created_at, updated_at) VALUES (:id, :t, 'sales_delivery', :nr, 'open', 'test', 'EUR', 0, 0, 0, "
                        "NOW(), 1, 1, NOW(), NOW())"), {'id': identity, 't': tid, 'nr': 'SYNTH-' + identity})
    db.commit()  # release only fixture savepoint, outer probe transaction still rolls back
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    app.include_router(belege.router, prefix='/api/v1/belege')
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


def drucken(case, note=None, grund='Synthetic verified reprint', **kwargs):
    return case[0].post(f'/api/v1/belege/sales_delivery/{note or case[8]}/actions/drucken',
                        json={'grund': grund} if grund is not None else {}, headers=headers(case, **kwargs))


def print_note(case, **kwargs):
    """Erfolg nur, wenn der Druckvermerk geschrieben ist; jede Ablehnung mit ihrem Status."""
    antwort = drucken(case, **kwargs)
    if antwort.status_code == 200 and not antwort.json().get('success'):
        return type('Abgelehnt', (), {'status_code': 403 if 'Nutzerzuordnung' in antwort.text else 400, 'text': antwort.text})()
    return antwort


def gedruckt(case, note=None):
    return case[1].execute(text('SELECT print_count FROM domain_docflow.document_headers WHERE id=:id'), {'id': note or case[8]}).scalar_one()


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
    assert gedruckt(case) == 1  # kein Vermerk ohne eindeutige Zuordnung
    fremd = drucken(case, note=case[9], grund='Synthetic')
    assert fremd.status_code == 404 or fremd.json().get('success') is False
    assert gedruckt(case, case[9]) == 1


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
    from sqlalchemy.orm import Session as _Session
    db, execute = case[1], _Session.execute
    # Klassenweit: Die Maskenaktion schreibt ueber eine eigene Sitzung auf derselben Verbindung.
    def fail_lookup(self, statement, *args, **kwargs):
        if 'SELECT id FROM domain_shared.users' in str(statement):
            return execute(self, text('SELECT * FROM synthetic_missing_actor_table'))
        return execute(self, statement, *args, **kwargs)
    monkeypatch.setattr(_Session, 'execute', fail_lookup)
    assert print_note(case).status_code in (400, 403, 500, 503)
    monkeypatch.setattr(_Session, 'execute', execute)
    assert gedruckt(case) == 1
    assert db.execute(text('SELECT COUNT(*) FROM domain_audit.attestations WHERE entity_id=:id'), {'id': case[8]}).scalar_one() == 0


def test_audit_metadata_agrees_with_migrated_schema():
    assert not AuditLog.__table__.c.user_id.foreign_keys
    assert not AuditLog.__table__.c.tenant_id.foreign_keys


def test_reason_and_verified_identity_are_required(attestation_case):
    case = attestation_case
    assert print_note(case, grund=None).status_code == 400  # Nachdruck ohne Begruendung
    path = f'/api/v1/belege/sales_delivery/{case[8]}/actions/drucken'
    assert case[0].post(path, json={'grund': 'Synthetic'}).status_code == 401
    assert case[1].execute(text('SELECT COUNT(*) FROM domain_audit.attestations WHERE entity_id=:id'), {'id': case[8]}).scalar_one() == 0
