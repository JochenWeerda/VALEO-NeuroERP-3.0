from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.core.exceptions import ValidationFailedError
from app.services.docflow_service import DocflowService


class _Mappings:
    def __init__(self, row):
        self.row = row

    def first(self):
        return self.row


class _Result:
    def __init__(self, row=None):
        self.row = row

    def mappings(self):
        return _Mappings(self.row)

    def first(self):
        return self.row


class _Db:
    def __init__(self, header, posting=None):
        self.results = [_Result(header), _Result(posting), _Result(), _Result()]
        self.calls: list[tuple[str, dict]] = []
        self.committed = False

    def execute(self, statement, params=None):
        self.calls.append((str(statement), dict(params or {})))
        return self.results.pop(0) if self.results else _Result()

    def commit(self):
        self.committed = True


def test_delete_draft_document_is_tenant_scoped_and_soft_deletes():
    db = _Db({"id": "doc-1", "tenant_id": "tenant-a", "status": "open"})
    service = DocflowService(db, "tenant-a")
    service.best_effort_audit = lambda *args, **kwargs: None

    service.delete_draft_document("doc-1")

    update_sql, update_params = db.calls[2]
    assert "SET deleted_at = NOW()" in update_sql
    assert "tenant_id = :tenant_id" in update_sql
    assert update_params == {"tenant_id": "tenant-a", "id": "doc-1"}
    assert db.committed is True


def test_delete_draft_document_rejects_posted_status():
    db = _Db({"id": "doc-1", "tenant_id": "tenant-a", "status": "posted"})
    service = DocflowService(db, "tenant-a")

    with pytest.raises(ValidationFailedError):
        service.delete_draft_document("doc-1")
