from contextlib import contextmanager

from app.services.docflow_service import DocflowService


class FailingAuditSession:
    def __init__(self) -> None:
        self.savepoint_entered = False

    @contextmanager
    def begin_nested(self):
        self.savepoint_entered = True
        yield

    def execute(self, *_args, **_kwargs):
        raise RuntimeError("audit table unavailable")


def test_best_effort_audit_isolates_failure_in_savepoint() -> None:
    db = FailingAuditSession()
    service = DocflowService(db, "tenant-1")  # type: ignore[arg-type]

    service.best_effort_audit("convert", "docflow_document", "doc-1", {"status": "ok"})

    assert db.savepoint_entered is True
