from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import finance_followup
from app.core.database import get_db
from app.core.tenant import get_tenant_id


class _FakeResult:
    def __init__(self, rows=None, fetchone=None):
        self._rows = list(rows or [])
        self._fetchone = fetchone

    def fetchone(self):
        return self._fetchone

    def __iter__(self):
        return iter(self._rows)


class FakeDb:
    def __init__(self):
        self.export_stubs: dict[str, dict] = {}
        self.commit_count = 0
        self.rollback_count = 0

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        params = params or {}

        if "INSERT INTO domain_shared.finance_followup_exports" in sql:
            self.export_stubs[params["id"]] = {
                "kind": params["kind"],
                "run_id": params["run_id"],
                "record_count": params["cnt"],
                "dms_document_id": params["dms_id"],
                "dms_view_url": params["dms_url"],
                "params_json": params["params"],
            }
            return _FakeResult()

        if "UPDATE domain_shared.finance_followup_exports" in sql:
            stub = self.export_stubs[params["eid"]]
            stub["dms_document_id"] = params["did"]
            stub["dms_view_url"] = params["url"]
            return _FakeResult()

        if "FROM domain_shared.finance_followup_exports" in sql:
            stub = self.export_stubs.get(params["id"])
            row = None
            if stub is not None:
                row = SimpleNamespace(**stub)
            return _FakeResult(fetchone=row)

        if "FROM domain_shared.open_items" in sql and "COUNT(*) FILTER" in sql:
            return _FakeResult(
                fetchone=SimpleNamespace(
                    open_items_count=3,
                    total_overdue=4200.5,
                    level_1=2,
                    level_2=1,
                    level_3=0,
                )
            )

        if "SELECT COUNT(*) AS cnt FROM domain_shared.open_items" in sql:
            dlevel = params.get("dlevel")
            return _FakeResult(fetchone=SimpleNamespace(cnt=1 if dlevel == 2 else 3))

        if "SELECT debitor_id, balance, overdue_days, dunning_level" in sql:
            rows = [
                SimpleNamespace(
                    debitor_id="DEB-1",
                    balance=1200.0,
                    overdue_days=12,
                    dunning_level=params.get("dlevel", 1),
                )
            ]
            return _FakeResult(rows=rows)

        if "COALESCE(SUM(amount), 0) AS total_amount" in sql:
            return _FakeResult(fetchone=SimpleNamespace(total_amount=980.0, debitor_count=2))

        if "COUNT(*) FILTER (WHERE mandate_valid = true)" in sql:
            return _FakeResult(fetchone=SimpleNamespace(valid_count=2, expired_count=0))

        if "SELECT COUNT(*) AS cnt FROM domain_shared.direct_debit_items" in sql:
            return _FakeResult(fetchone=SimpleNamespace(cnt=2))

        if "SELECT debitor_id, amount, run_id FROM domain_shared.direct_debit_items" in sql:
            return _FakeResult(
                rows=[
                    SimpleNamespace(debitor_id="DEB-1", amount=500.0, run_id=params["run_id"]),
                    SimpleNamespace(debitor_id="DEB-2", amount=480.0, run_id=params["run_id"]),
                ]
            )

        if "SELECT COUNT(*) AS cnt FROM domain_docflow.pos_receipt_compliance" in sql and "dsfinvk_export_batch_id IS NULL" not in sql:
            return _FakeResult(fetchone=SimpleNamespace(cnt=4))

        if "dsfinvk_export_batch_id IS NULL" in sql:
            return _FakeResult(fetchone=SimpleNamespace(cnt=1))

        if "SELECT id, terminal_id, tse_transaction_id, transaction_ended_at" in sql:
            return _FakeResult(
                rows=[
                    SimpleNamespace(
                        id="POS-1",
                        terminal_id="TERM-1",
                        tse_transaction_id="TSE-1",
                        transaction_ended_at="2026-04-13T10:15:00+00:00",
                    )
                ]
            )

        raise AssertionError(f"Unhandled SQL in test FakeDb: {sql}")

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(finance_followup.router)
    db = FakeDb()
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client, db


def test_build_finance_followup_superglue_rollout_filters_finance_domain(monkeypatch):
    monkeypatch.setattr(
        "app.integrations.services.superglue_domain_rollouts.build_superglue_domain_rollout_summary",
        lambda tenant_id: {
            "tenant_id": tenant_id,
            "domains": [
                {"domain_key": "sales", "connector_count": 1, "connectors": []},
                {"domain_key": "finance", "connector_count": 2, "connectors": ["datev", "elster"]},
            ],
        },
    )

    result = finance_followup.build_finance_followup_superglue_rollout("tenant-a")

    assert result["provider_key"] == "superglue"
    assert result["domain_key"] == "finance"
    assert result["rollout"]["connector_count"] == 2


def test_mahnwesen_preview_returns_aggregated_numbers(client):
    test_client, _db = client

    response = test_client.get("/finance/followup/mahnwesen/preview")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-a"
    assert body["open_items_count"] == 3
    assert body["total_overdue_amount"] == 4200.5
    assert body["dunning_level_counts"] == {"1": 2, "2": 1, "3": 0}


def test_mahnwesen_export_persists_stub_and_downloads_csv_without_dms(client):
    test_client, db = client

    response = test_client.post(
        "/finance/followup/mahnwesen/export",
        json={"format": "pdf", "dunning_level_filter": 2},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["record_count"] == 1
    assert body["download_url"].endswith("/download")
    assert db.commit_count == 1

    export_id = body["export_id"]
    download = test_client.get(f"/finance/followup/mahnwesen/export/{export_id}/download")
    assert download.status_code == 200
    assert "debitor_id;balance;overdue_days;dunning_level" in download.text
    assert "DEB-1;1200.0;12;2" in download.text


def test_mahnwesen_download_redirects_to_dms_view_url(client):
    test_client, db = client
    db.export_stubs["exp-redirect"] = {
        "kind": "mahnwesen",
        "run_id": None,
        "record_count": 2,
        "dms_document_id": 77,
        "dms_view_url": "https://dms.example/doc/77",
        "params_json": None,
    }

    response = test_client.get(
        "/finance/followup/mahnwesen/export/exp-redirect/download",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == "https://dms.example/doc/77"


def test_lastschrift_preview_export_and_download_work(client):
    test_client, db = client

    preview = test_client.get("/finance/followup/lastschriften/run-1/preview")
    assert preview.status_code == 200
    assert preview.json()["sepa_ready"] is True

    export = test_client.post("/finance/followup/lastschriften/run-1/export", json={})
    assert export.status_code == 202
    body = export.json()
    assert body["record_count"] == 2
    assert db.commit_count == 1

    download = test_client.get(
        f"/finance/followup/lastschriften/run-1/export/{body['export_id']}/download"
    )
    assert download.status_code == 200
    assert "debitor_id;amount;run_id" in download.text
    assert "DEB-1;500.0;run-1" in download.text


def test_lastschrift_download_404_for_mismatched_run(client):
    test_client, db = client
    db.export_stubs["exp-mismatch"] = {
        "kind": "lastschrift",
        "run_id": "run-x",
        "record_count": 2,
        "dms_document_id": None,
        "dms_view_url": None,
        "params_json": None,
    }

    response = test_client.get("/finance/followup/lastschriften/run-y/export/exp-mismatch/download")

    assert response.status_code == 404


def test_kasse_preview_export_and_download_use_existing_context(client):
    test_client, db = client

    preview = test_client.get("/finance/followup/kasse/preview")
    assert preview.status_code == 200
    assert preview.json()["pending_export_count"] == 1

    export = test_client.post("/finance/followup/kasse/export", json={"format": "zip"})
    assert export.status_code == 202
    body = export.json()
    assert body["record_count"] == 4
    assert body["format"] == "zip"
    assert db.commit_count == 1

    download = test_client.get(f"/finance/followup/kasse/export/{body['export_id']}/download")
    assert download.status_code == 200
    assert "terminal_id" in download.text
    assert "TERM-1" in download.text


def test_export_paths_attach_upload_metadata_when_export_storage_is_enabled(client, monkeypatch):
    test_client, db = client
    monkeypatch.setenv("FINANCE_EXPORT_S3_BUCKET", "exports-test")
    monkeypatch.setattr(
        "app.integrations.finance_export_upload.upload_finance_export_csv",
        lambda path, label, tenant_id: {
            "ok": True,
            "backend": "s3",
            "url": "https://files.example/export.csv",
            "document_id": 123,
        },
    )

    response = test_client.post("/finance/followup/kasse/export", json={"format": "zip"})

    assert response.status_code == 202
    body = response.json()
    assert body["export_upload"] == "ok"
    assert body["export_backend"] == "s3"
    assert body["dms_document_id"] == 123
    stub = db.export_stubs[body["export_id"]]
    assert stub["dms_view_url"] == "https://files.example/export.csv"

