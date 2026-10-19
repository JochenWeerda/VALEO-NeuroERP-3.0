"""Signed provider identities, real probe SQL and rollback-only synthetic records."""
from uuid import uuid4
from datetime import datetime, timezone
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from app.core.tenant_binding import install_tenant_bindings
from app.infrastructure.models import Tenant, User, AuditLog
from app.api.v1.endpoints import gdpr
from main import BearerAuthMiddleware
from test_system_tenant_binding import keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


@pytest.fixture
def subject_data(probe):
    tenant_a, tenant_b = str(uuid4()), str(uuid4())
    own, other, foreign = [str(uuid4()) for _ in range(3)]
    with engine.connect() as connection:
        transaction = connection.begin()
        db = Session(bind=connection, join_transaction_mode='create_savepoint')
        try:
            for tid in (tenant_a, tenant_b):
                db.add(Tenant(id=tid, name='Synthetic privacy probe', domain=tid+'.invalid', is_active=True))
            db.flush()
            for uid, tid, provider in [(own, tenant_a, 'human-a'), (other, tenant_a, 'synthetic-other'), (foreign, tenant_b, 'synthetic-foreign')]:
                db.add(User(id=uid, tenant_id=tid, keycloak_id=provider, username='synthetic-'+uid, email=uid+'@example.invalid', first_name='Synthetic', last_name='Privacy', roles=['user'], is_active=True))
            db.flush()
            for tid, action in [(tenant_a,'synthetic-own-event'),(tenant_b,'synthetic-foreign-event')]:
                db.add(AuditLog(id=str(uuid4()), timestamp=datetime.now(timezone.utc), tenant_id=tid, user_id=own, user_email='synthetic@example.invalid', action=action, entity_type='privacy-probe', entity_id=own, changes={}, ip_address='127.0.0.1', user_agent='Synthetic'))
            db.flush()
            app = FastAPI()
            app.add_middleware(BearerAuthMiddleware)
            app.include_router(gdpr.router, prefix='/api/v1/gdpr')
            app.dependency_overrides[get_db] = lambda: db
            install_tenant_bindings(app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
            with TestClient(app, raise_server_exceptions=False) as client:
                yield client, db, probe, tenant_a, tenant_b, own, other, foreign
        finally:
            db.close()
            transaction.rollback()


def headers(data, *, admin=False):
    _, _, provider, tenant, *_ = data
    return {'Authorization':'Bearer '+provider.token(tenant, changes={'roles':['admin'] if admin else ['user']})}


@pytest.mark.parametrize('operation',['data-export','export-portable'])
def test_self_export_uses_provider_mapping_and_only_own_tenant_audit(subject_data, operation):
    client, _, _, tenant, _, own, *_ = subject_data
    response=client.get(f'/api/v1/gdpr/{operation}/{own}',headers=headers(subject_data))
    assert response.status_code==200,response.text
    body=response.json()
    assert body['personal_data']['id']==own
    assert body['export_metadata']['tenant_id']==tenant
    assert [item['action'] for item in body['audit_logs']]==['synthetic-own-event']


@pytest.mark.parametrize('operation',['data-export','export-portable'])
def test_other_local_subject_is_denied_and_admin_is_still_tenant_bound(subject_data, operation):
    client, _, _, _, _, _, other, foreign=subject_data
    assert client.get(f'/api/v1/gdpr/{operation}/{other}',headers=headers(subject_data)).status_code==403
    assert client.get(f'/api/v1/gdpr/{operation}/{other}',headers=headers(subject_data,admin=True)).status_code==200
    assert client.get(f'/api/v1/gdpr/{operation}/{foreign}',headers=headers(subject_data,admin=True)).status_code==404


def test_anonymization_requires_admin_and_never_rewrites_retained_audit(subject_data):
    client, db, _, tenant, _, own, other, foreign=subject_data
    audit_before=[(row.id,row.user_email,row.ip_address,row.action) for row in db.query(AuditLog).filter(AuditLog.user_id==own).all()]
    original_email=db.get(User,own).email
    assert client.delete(f'/api/v1/gdpr/delete-user/{own}',headers=headers(subject_data)).status_code==403
    assert db.get(User,own).email==original_email
    assert client.delete(f'/api/v1/gdpr/delete-user/{foreign}',headers=headers(subject_data,admin=True)).status_code==404
    response=client.delete(f'/api/v1/gdpr/delete-user/{own}',headers=headers(subject_data,admin=True))
    assert response.status_code==204,response.text
    db.expire_all()
    assert db.get(User,own).is_active is False
    assert db.get(User,own).deleted_at is not None
    assert db.get(User,other).is_active and db.get(User,foreign).is_active
    assert [(row.id,row.user_email,row.ip_address,row.action) for row in db.query(AuditLog).filter(AuditLog.user_id==own).all()]==audit_before


def test_forged_tenant_or_user_headers_and_missing_identity_cannot_authorize(subject_data):
    client, db, _, _, foreign_tenant, own, other, _=subject_data
    path=f'/api/v1/gdpr/data-export/{other}'
    assert client.get(path,headers={**headers(subject_data),'X-User-ID':other}).status_code==403
    assert client.get(path,headers={**headers(subject_data),'X-Tenant-ID':foreign_tenant}).status_code==403
    assert client.get(path).status_code==401
    assert db.get(User,own).is_active and db.get(User,other).is_active
