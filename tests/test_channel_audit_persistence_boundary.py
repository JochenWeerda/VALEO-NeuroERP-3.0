from types import SimpleNamespace
import pytest
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import EntityNotFoundError
from app.core.channel_process_actions import ChannelProcessThread, ChannelThreadAuditItem
from app.repositories.channel_thread_repository import PersistentChannelProcessThreadStore


def thread():
    return ChannelProcessThread('thread-a', 'TEAMS', 'tenant-a', 'ordinary', 'Prepare', 'object', 'object-a', 'reader', 'employee', 'actor-a', None, {}, 'accepted', {}, audit_trail=[ChannelThreadAuditItem('prepared', {'actor': 'actor-a'})])


class Database:
    def __init__(self, existing=None, fail=False):
        self.existing = existing
        self.fail = fail
        self.added = []
        self.rollbacks = 0
        self.commits = 0
    def get(self, model, key): return self.existing
    def add(self, record): self.added.append(record)
    def commit(self):
        self.commits += 1
        if self.fail: raise IntegrityError('insert audit', {}, RuntimeError('constraint failure'))
    def refresh(self, record): pass
    def rollback(self): self.rollbacks += 1


def test_audit_child_tenant_is_copied_from_its_thread():
    db = Database()
    value = thread()
    assert PersistentChannelProcessThreadStore(db).save(value).thread_id == value.thread_id
    assert db.added[0].tenant_id == 'tenant-a'
    assert db.added[0].audit_items[0].tenant_id == 'tenant-a'
    assert db.commits == 1


def test_failed_persistence_does_not_report_memory_success():
    db = Database(fail=True)
    with pytest.raises(IntegrityError): PersistentChannelProcessThreadStore(db).save(thread())
    assert db.rollbacks == 1


def test_foreign_thread_cannot_be_reassigned():
    existing = SimpleNamespace(process_definition_key='ordinary', tenant_id='tenant-b')
    db = Database(existing=existing)
    with pytest.raises(EntityNotFoundError): PersistentChannelProcessThreadStore(db).save(thread())
    assert existing.tenant_id == 'tenant-b'
    assert db.added == [] and db.commits == 0


def test_persistent_audit_cannot_be_cleared_globally():
    db = Database()
    with pytest.raises(RuntimeError, match='cannot be globally cleared'): PersistentChannelProcessThreadStore(db).clear()
    assert db.commits == 0
