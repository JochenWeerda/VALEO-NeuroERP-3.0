from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.einkauf_compat_service import EinkaufCompatService


class Result:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def first(self):
        return self.rows[0] if self.rows else None

    def one(self):
        assert len(self.rows) == 1
        return self.rows[0]

    def all(self):
        return self.rows


class Session:
    def __init__(self, fail_commit=False):
        self.users = {'sub-a': ('user-a', 'a@example.org'), 'sub-b': ('user-b', 'b@example.org')}
        self.status = 'OFFEN'
        self.pending_status = self.status
        self.audit = []
        self.committed_audit = []
        self.fail_commit = fail_commit
        self.rollbacks = 0

    def execute(self, statement, params):
        sql = str(statement)
        if 'SELECT id, status FROM einkauf_rechnungseingaenge' in sql:
            return Result([{'id': 'invoice', 'status': self.status}])
        if 'SELECT id FROM domain_shared.users' in sql:
            user = self.users.get(params['actor']) if params['tenant_id'] == 'tenant-a' else None
            return Result([(user[0],)] if user else [])
        if 'SELECT email FROM domain_shared.users' in sql:
            return Result([{'email': next(v[1] for v in self.users.values() if v[0] == params['id'])}])
        if 'UPDATE einkauf_rechnungseingaenge' in sql:
            self.pending_status = params['ns']
            return Result([])
        raise AssertionError(sql)

    def add(self, obj):
        self.audit.append(obj)

    def commit(self):
        if self.fail_commit:
            raise RuntimeError('audit insert failed')
        self.status = self.pending_status
        self.committed_audit.extend(self.audit)
        self.audit.clear()

    def rollback(self):
        self.rollbacks += 1
        self.pending_status = self.status
        self.audit.clear()


@pytest.mark.parametrize(('subject', 'user_id', 'email'), [
    ('sub-a', 'user-a', 'a@example.org'), ('sub-b', 'user-b', 'b@example.org'),
])
def test_real_service_records_verified_actor(subject, user_id, email, monkeypatch):
    db = Session()
    service = EinkaufCompatService(db, 'tenant-a')
    monkeypatch.setattr(service, '_invalidate', lambda: None)
    assert service.pruefen_rechnung('invoice', subject)['status'] == 'GEPRUEFT'
    assert db.status == 'GEPRUEFT'
    assert len(db.committed_audit) == 1
    audit = db.committed_audit[0]
    assert (audit.user_id, audit.user_email, audit.tenant_id) == (user_id, email, 'tenant-a')
    assert audit.changes == {'old': {'status': 'OFFEN'}, 'new': {'status': 'GEPRUEFT'}}


@pytest.mark.parametrize('subject', ['', 'unknown'])
def test_missing_identity_cannot_change_status(subject, monkeypatch):
    db = Session()
    service = EinkaufCompatService(db, 'tenant-a')
    monkeypatch.setattr(service, '_invalidate', lambda: None)
    with pytest.raises(HTTPException) as exc:
        service.pruefen_rechnung('invoice', subject)
    assert exc.value.status_code == 403
    assert (db.status, db.committed_audit, db.rollbacks) == ('OFFEN', [], 1)


def test_audit_failure_rolls_back_status(monkeypatch):
    db = Session(fail_commit=True)
    service = EinkaufCompatService(db, 'tenant-a')
    monkeypatch.setattr(service, '_invalidate', lambda: None)
    with pytest.raises(RuntimeError, match='audit insert failed'):
        service.pruefen_rechnung('invoice', 'sub-a')
    assert (db.status, db.committed_audit, db.rollbacks) == ('OFFEN', [], 1)