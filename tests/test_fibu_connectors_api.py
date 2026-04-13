from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import fibu_connectors
from app.core.database import get_db
from app.core.tenant import get_tenant_id


class _FakeResult:
    def __init__(self, fetchone=None, fetchall=None, rowcount: int = 0):
        self._fetchone = fetchone
        self._fetchall = list(fetchall or [])
        self.rowcount = rowcount

    def fetchone(self):
        return self._fetchone

    def fetchall(self):
        return list(self._fetchall)


class FakeDb:
    def __init__(self):
        now = datetime(2026, 4, 13, 12, 0, tzinfo=timezone.utc)
        self.commit_count = 0
        self.profiles = {
            "prof-1": {
                "id": "prof-1",
                "tenant_id": "tenant-a",
                "connector_type": "PAYROLL",
                "name": "Payroll Default",
                "is_default": True,
                "settings": {"delimiter": ";"},
                "mapping": {"konto": "account"},
                "version": 1,
                "created_at": now,
                "updated_at": now,
                "created_by": None,
                "updated_by": None,
            }
        }
        self.runs = {
            "run-1": {
                "id": "run-1",
                "tenant_id": "tenant-a",
                "connector_type": "PAYROLL",
                "direction": "IMPORT",
                "profile_id": "prof-1",
                "idempotency_key": None,
                "status": "PARSED",
                "counts": {"lines_total": 2, "lines_ok": 2, "lines_err": 0},
                "totals": {"debit": "100.00", "credit": "100.00"},
                "error_summary": None,
                "started_at": now,
                "finished_at": now,
                "created_at": now,
                "created_by": "tester",
            }
        }
        self.run_items = {
            "run-1": [
                (
                    "item-1",
                    "run-1",
                    1,
                    "JOURNAL_ENTRY_LINE",
                    {"booking_date": "2026-04-13"},
                    None,
                    None,
                    "OK",
                ),
                (
                    "item-2",
                    "run-1",
                    2,
                    "JOURNAL_ENTRY_LINE",
                    {"booking_date": "2026-04-13"},
                    ["missing cost center"],
                    None,
                    "ERROR",
                ),
            ]
        }
        self.profile_has_references = False

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        params = params or {}

        if "FROM domain_erp.fibu_connector_profiles WHERE tenant_id = :tid AND connector_type = :ct" in sql:
            rows = []
            for profile in self.profiles.values():
                if profile["tenant_id"] == params["tid"] and profile["connector_type"] == params["ct"]:
                    rows.append(
                        (
                            profile["id"],
                            profile["tenant_id"],
                            profile["connector_type"],
                            profile["name"],
                            profile["is_default"],
                            profile["settings"],
                            profile["mapping"],
                            profile["version"],
                            profile["created_at"],
                            profile["updated_at"],
                            profile["created_by"],
                            profile["updated_by"],
                        )
                    )
            return _FakeResult(fetchall=rows)

        if "INSERT INTO domain_erp.fibu_connector_profiles" in sql:
            self.profiles[params["id"]] = {
                "id": params["id"],
                "tenant_id": params["tenant_id"],
                "connector_type": params["connector_type"],
                "name": params["name"],
                "is_default": params["is_default"],
                "settings": __import__("json").loads(params["settings"]),
                "mapping": __import__("json").loads(params["mapping"]),
                "version": 1,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "created_by": None,
                "updated_by": None,
            }
            return _FakeResult()

        if "UPDATE domain_erp.fibu_connector_profiles SET is_default = false" in sql:
            for profile in self.profiles.values():
                if (
                    profile["tenant_id"] == params["tid"]
                    and profile["connector_type"] == params["ct"]
                    and profile["id"] != params["id"]
                ):
                    profile["is_default"] = False
            return _FakeResult()

        if "FROM domain_erp.fibu_connector_profiles WHERE id = :id AND tenant_id = :tid" in sql and "SELECT id, version" in sql:
            profile = self.profiles.get(params["id"])
            row = None
            if profile and profile["tenant_id"] == params["tid"]:
                row = (profile["id"], profile["version"])
            return _FakeResult(fetchone=row)

        if "SELECT connector_type FROM domain_erp.fibu_connector_profiles WHERE id = :id" in sql:
            profile = self.profiles.get(params["id"])
            return _FakeResult(fetchone=(profile["connector_type"],) if profile else None)

        if "UPDATE domain_erp.fibu_connector_profiles SET" in sql and "version = :version" in sql:
            profile = self.profiles[params["id"]]
            if "name" in params:
                profile["name"] = params["name"]
            if "is_default" in params:
                profile["is_default"] = params["is_default"]
            if "settings" in params:
                profile["settings"] = __import__("json").loads(params["settings"])
            if "mapping" in params:
                profile["mapping"] = __import__("json").loads(params["mapping"])
            profile["version"] = params["version"]
            profile["updated_at"] = datetime.now(timezone.utc)
            return _FakeResult()

        if "SELECT id, tenant_id, connector_type, name, is_default, settings, mapping, version, created_at, updated_at, created_by, updated_by FROM domain_erp.fibu_connector_profiles WHERE id = :id" in sql:
            profile = self.profiles[params["id"]]
            return _FakeResult(
                fetchone=(
                    profile["id"],
                    profile["tenant_id"],
                    profile["connector_type"],
                    profile["name"],
                    profile["is_default"],
                    profile["settings"],
                    profile["mapping"],
                    profile["version"],
                    profile["created_at"],
                    profile["updated_at"],
                    profile["created_by"],
                    profile["updated_by"],
                )
            )

        if "FROM domain_erp.fibu_connector_profiles WHERE id = :id AND tenant_id = :tid" in sql:
            profile = self.profiles.get(params["id"])
            row = None
            if profile and profile["tenant_id"] == params["tid"]:
                row = (
                    profile["id"],
                    profile["tenant_id"],
                    profile["connector_type"],
                    profile["name"],
                    profile["is_default"],
                    profile["settings"],
                    profile["mapping"],
                    profile["version"],
                    profile["created_at"],
                    profile["updated_at"],
                    profile["created_by"],
                    profile["updated_by"],
                )
            return _FakeResult(fetchone=row)

        if "SELECT 1 FROM domain_erp.fibu_connector_runs WHERE profile_id = :id LIMIT 1" in sql:
            return _FakeResult(fetchone=(1,) if self.profile_has_references else None)

        if "DELETE FROM domain_erp.fibu_connector_profiles WHERE id = :id AND tenant_id = :tid" in sql:
            existed = params["id"] in self.profiles and self.profiles[params["id"]]["tenant_id"] == params["tid"]
            if existed:
                del self.profiles[params["id"]]
            return _FakeResult(rowcount=1 if existed else 0)

        if "FROM domain_erp.fibu_connector_runs WHERE id = :id AND tenant_id = :tid" in sql and "SELECT id, tenant_id, connector_type" in sql:
            run = self.runs.get(params["id"])
            row = None
            if run and run["tenant_id"] == params["tid"]:
                row = (
                    run["id"],
                    run["tenant_id"],
                    run["connector_type"],
                    run["direction"],
                    run["profile_id"],
                    run["idempotency_key"],
                    run["status"],
                    None,
                    None,
                    None,
                    None,
                    run["counts"],
                    run["totals"],
                    run["error_summary"],
                    run["started_at"],
                    run["finished_at"],
                    run["created_at"],
                    run["created_by"],
                )
            return _FakeResult(fetchone=row)

        if "SELECT 1 FROM domain_erp.fibu_connector_runs WHERE id = :id AND tenant_id = :tid" in sql:
            run = self.runs.get(params["id"])
            return _FakeResult(fetchone=(1,) if run and run["tenant_id"] == params["tid"] else None)

        if "FROM domain_erp.fibu_connector_run_items WHERE run_id = :run_id" in sql:
            rows = self.run_items.get(params["run_id"], [])
            if "AND status = 'ERROR'" in sql:
                rows = [row for row in rows if row[7] == "ERROR"]
            return _FakeResult(fetchall=rows[: params["limit"]])

        raise AssertionError(f"Unhandled SQL in fibu connector test double: {sql}")

    def commit(self):
        self.commit_count += 1


def _build_client(db: FakeDb) -> TestClient:
    app = FastAPI()
    app.include_router(fibu_connectors.router)
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


def test_profile_crud_and_default_switching():
    db = FakeDb()
    client = _build_client(db)

    listed = client.get("/connectors/profiles?type=PAYROLL")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    created = client.post(
        "/connectors/profiles",
        json={
            "connector_type": "PAYROLL",
            "name": "Payroll Alt",
            "is_default": True,
            "settings": {"encoding": "utf-8"},
            "mapping": {"betrag": "amount"},
        },
    )
    assert created.status_code == 201
    created_body = created.json()
    assert created_body["is_default"] is True
    assert db.commit_count >= 1
    assert db.profiles["prof-1"]["is_default"] is False

    fetched = client.get(f"/connectors/profiles/{created_body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Payroll Alt"

    updated = client.put(
        f"/connectors/profiles/{created_body['id']}",
        json={"name": "Payroll Updated", "version": 1},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Payroll Updated"


def test_update_profile_rejects_stale_version_and_delete_profile_handles_refs():
    db = FakeDb()
    client = _build_client(db)
    db.profiles["prof-delete"] = {
        **db.profiles["prof-1"],
        "id": "prof-delete",
        "name": "Delete me",
        "is_default": False,
    }

    conflict = client.put("/connectors/profiles/prof-1", json={"name": "X", "version": 99})
    assert conflict.status_code == 409

    db.profile_has_references = True
    blocked_delete = client.delete("/connectors/profiles/prof-delete")
    assert blocked_delete.status_code == 400

    db.profile_has_references = False
    missing = client.delete("/connectors/profiles/missing-profile")
    assert missing.status_code == 404


def test_import_run_endpoints_cover_upload_summary_items_and_workflow_actions(monkeypatch):
    db = FakeDb()
    client = _build_client(db)
    called: list[tuple[str, str]] = []

    def _create_run(db_arg, tenant_id, connector_type, profile_id, idempotency_key, created_by):
        assert tenant_id == "tenant-a"
        called.append(("create", connector_type))
        run_id = "run-new"
        db.runs[run_id] = {
            "id": run_id,
            "tenant_id": tenant_id,
            "connector_type": connector_type,
            "direction": "IMPORT",
            "profile_id": profile_id,
            "idempotency_key": idempotency_key,
            "status": "PARSED",
            "counts": {"lines_total": 1, "lines_ok": 1, "lines_err": 0},
            "totals": {"debit": "50.00", "credit": "50.00"},
            "error_summary": None,
            "started_at": datetime.now(timezone.utc),
            "finished_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "created_by": created_by,
        }
        db.run_items[run_id] = [
            ("item-new", run_id, 1, "JOURNAL_ENTRY_LINE", {"document_no": "A-1"}, None, "JE-1", "OK")
        ]
        return run_id

    monkeypatch.setattr(fibu_connectors.workflow, "create_run", _create_run)
    monkeypatch.setattr(fibu_connectors.workflow, "set_run_artifact", lambda *args, **kwargs: called.append(("artifact", "ok")))
    monkeypatch.setattr(fibu_connectors.workflow, "parse_run", lambda *args, **kwargs: called.append(("parse", "ok")))
    monkeypatch.setattr(fibu_connectors.workflow, "validate_run", lambda *args, **kwargs: db.runs.__setitem__("run-1", {**db.runs["run-1"], "status": "VALIDATED"}))
    monkeypatch.setattr(fibu_connectors.workflow, "post_run", lambda *args, **kwargs: db.runs.__setitem__("run-1", {**db.runs["run-1"], "status": "POSTED"}))
    monkeypatch.setattr(fibu_connectors.workflow, "cancel_run", lambda *args, **kwargs: db.runs.__setitem__("run-1", {**db.runs["run-1"], "status": "CANCELLED"}))
    monkeypatch.setattr(fibu_connectors.workflow, "reverse_run", lambda *args, **kwargs: db.runs.__setitem__("run-1", {**db.runs["run-1"], "status": "REVERSED"}))

    uploaded = client.post(
        "/connectors/PAYROLL/imports?profile_id=prof-1&idempotency_key=idem-1",
        files={"file": ("payroll.csv", b"a;b;c\n1;2;3\n", "text/csv")},
        headers={"X-User-ID": "tester"},
    )
    assert uploaded.status_code == 201
    assert uploaded.json()["run_id"] == "run-new"
    assert ("create", "PAYROLL") in called
    assert ("parse", "ok") in called

    summary = client.get("/connectors/imports/run-1")
    assert summary.status_code == 200
    assert summary.json()["status"] == "PARSED"

    items = client.get("/connectors/imports/run-1/items?only_errors=true")
    assert items.status_code == 200
    assert len(items.json()) == 1
    assert items.json()[0]["status"] == "ERROR"

    validated = client.post("/connectors/imports/run-1/validate")
    assert validated.status_code == 200
    assert validated.json()["status"] == "VALIDATED"

    posted = client.post("/connectors/imports/run-1/post")
    assert posted.status_code == 200
    assert posted.json()["status"] == "POSTED"

    cancelled = client.post("/connectors/imports/run-1/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"

    reversed_run = client.post("/connectors/imports/run-1/reverse")
    assert reversed_run.status_code == 200
    assert reversed_run.json()["status"] == "REVERSED"
