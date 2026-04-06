"""Unit: Finance-Export Upload-Orchestrierung (DMS -> S3)."""

from __future__ import annotations

from pathlib import Path

from app.integrations.finance_export_upload import upload_finance_export_csv


def test_upload_prefers_dms_when_ok(monkeypatch, tmp_path: Path) -> None:
    p = tmp_path / "t.csv"
    p.write_text("a;b\n", encoding="utf-8")

    def fake_dms(path: str, *, label: str):
        return {"ok": True, "document_id": 42, "url": "http://dms/42", "error": None}

    monkeypatch.setattr(
        "app.integrations.finance_export_upload.try_upload_finance_csv_to_dms",
        fake_dms,
    )

    out = upload_finance_export_csv(str(p), label="x.csv", tenant_id="t1")
    assert out["ok"] is True
    assert out.get("backend") == "dms"


def test_upload_falls_back_to_s3(monkeypatch, tmp_path: Path) -> None:
    p = tmp_path / "t.csv"
    p.write_text("a;b\n", encoding="utf-8")

    monkeypatch.setattr(
        "app.integrations.finance_export_upload.try_upload_finance_csv_to_dms",
        lambda path, *, label: {"ok": False, "error": "no dms"},
    )

    def fake_s3(path: str, *, label: str, tenant_id: str | None = None):
        return {"ok": True, "document_id": None, "url": "s3://b/k", "error": None}

    monkeypatch.setattr(
        "app.integrations.finance_export_upload.try_upload_finance_csv_to_s3",
        fake_s3,
    )

    out = upload_finance_export_csv(str(p), label="x.csv", tenant_id="t1")
    assert out["ok"] is True
    assert out.get("backend") == "s3"
