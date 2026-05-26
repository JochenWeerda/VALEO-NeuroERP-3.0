"""
Finance Follow-up API — Wave 4 AP5

Explizite Backend-Contracts für Mahnwesen-Export und Lastschriften-Export.
"""
from __future__ import annotations

import csv
import io
import json
import logging
import os
import tempfile
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.finance_followup import (
    MahnwesenPreview,
    MahnwesenExportResult,
    MahnwesenExportFormat,
    LastschriftPreview,
    LastschriftExportResult,
    KassenfolgePreview,
    KassenfolgeExportResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/finance/followup", tags=["finance", "followup"])


def build_finance_followup_superglue_rollout(tenant_id: str) -> dict[str, object]:
    """Thin wrapper for finance/export-specific Superglue rollout metadata."""
    from app.integrations.services.superglue_domain_rollouts import build_superglue_domain_rollout_summary

    summary = build_superglue_domain_rollout_summary(tenant_id)
    domain = next((item for item in summary["domains"] if item["domain_key"] == "finance"), None)
    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "domain_key": "finance",
        "rollout": domain or {"domain_key": "finance", "connector_count": 0, "connectors": []},
        "schema_version": 1,
    }


def _insert_finance_export_stub(
    db: Session,
    *,
    export_id: str,
    tenant_id: str,
    kind: str,
    run_id: str | None,
    record_count: int,
    dms_document_id: int | None = None,
    dms_view_url: str | None = None,
    params_json: dict | None = None,
) -> None:
    db.execute(
        text(
            """
            INSERT INTO domain_shared.finance_followup_exports
                (id, tenant_id, kind, run_id, record_count, dms_document_id, dms_view_url, params_json)
            VALUES
                (CAST(:id AS uuid), :tid, :kind, :run_id, :cnt, :dms_id, :dms_url, CAST(:params AS jsonb))
            """
        ),
        {
            "id": export_id,
            "tid": tenant_id,
            "kind": kind,
            "run_id": run_id,
            "cnt": record_count,
            "dms_id": dms_document_id,
            "dms_url": dms_view_url,
            "params": json.dumps(params_json) if params_json else None,
        },
    )


def _get_export_stub(
    db: Session, export_id: str, tenant_id: str
):
    try:
        return db.execute(
            text(
                """
                SELECT kind, run_id, record_count, dms_document_id, dms_view_url, params_json
                FROM domain_shared.finance_followup_exports
                WHERE id = CAST(:id AS uuid) AND tenant_id = :tid
                """
            ),
            {"id": export_id, "tid": tenant_id},
        ).fetchone()
    except Exception:
        return None


def _maybe_redirect_dms(stub) -> RedirectResponse | None:
    if stub and stub.dms_view_url:
        return RedirectResponse(url=str(stub.dms_view_url), status_code=302)
    return None


def _stub_params_json(stub) -> dict | None:
    if stub is None or stub.params_json is None:
        return None
    p = stub.params_json
    if isinstance(p, dict):
        return p
    if isinstance(p, str):
        try:
            return json.loads(p)
        except json.JSONDecodeError:
            return None
    return None


def _stream_csv(filename: str, rows: list[list[object]]) -> StreamingResponse:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\r\n")
    for row in rows:
        w.writerow(row)
    data = buf.getvalue().encode("utf-8-sig")
    return StreamingResponse(
        iter([data]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _mahnwesen_csv_rows(
    db: Session, tenant_id: str, params: dict | None
) -> list[list[object]]:
    rows: list[list[object]] = [
        ["debitor_id", "balance", "overdue_days", "dunning_level"],
    ]
    dunning_level_filter = (params or {}).get("dunning_level_filter")
    try:
        level_clause = ""
        qparams: dict = {"tid": tenant_id}
        if dunning_level_filter is not None:
            level_clause = " AND dunning_level = :dlevel"
            qparams["dlevel"] = int(dunning_level_filter)
        result = db.execute(
            text(
                f"""
                SELECT debitor_id, balance, overdue_days, dunning_level
                FROM domain_shared.open_items
                WHERE tenant_id = :tid AND status = 'open' AND type = 'debitor'
                  AND overdue_days > 0{level_clause}
                LIMIT 10000
                """
            ),
            qparams,
        )
        for row in result:
            rows.append(
                [row.debitor_id, row.balance, row.overdue_days, row.dunning_level]
            )
    except Exception as exc:
        logger.debug("Mahnwesen CSV query skipped: %s", exc)
    return rows


def _lastschrift_csv_rows(db: Session, tenant_id: str, run_id: str) -> list[list[object]]:
    rows: list[list[object]] = [["debitor_id", "amount", "run_id"]]
    try:
        result = db.execute(
            text(
                """
                SELECT debitor_id, amount, run_id
                FROM domain_shared.direct_debit_items
                WHERE tenant_id = :tid AND run_id = :run_id
                LIMIT 50000
                """
            ),
            {"tid": tenant_id, "run_id": run_id},
        )
        for row in result:
            rows.append([row.debitor_id, row.amount, row.run_id])
    except Exception as exc:
        logger.debug("Lastschrift CSV query skipped: %s", exc)
    return rows


def _kasse_csv_rows(db: Session, tenant_id: str) -> list[list[object]]:
    rows: list[list[object]] = [
        ["id", "terminal_id", "tse_transaction_id", "transaction_ended_at"],
    ]
    try:
        result = db.execute(
            text(
                """
                SELECT id, terminal_id, tse_transaction_id, transaction_ended_at
                FROM domain_docflow.pos_receipt_compliance
                WHERE tenant_id = :tid
                LIMIT 50000
                """
            ),
            {"tid": tenant_id},
        )
        for row in result:
            rows.append(
                [
                    row.id,
                    row.terminal_id,
                    row.tse_transaction_id,
                    row.transaction_ended_at,
                ]
            )
    except Exception as exc:
        logger.debug("Kasse CSV query skipped: %s", exc)
    return rows


# ---------------------------------------------------------------------------
# Mahnwesen
# ---------------------------------------------------------------------------

@router.get("/mahnwesen/preview", response_model=dict)
async def get_mahnwesen_preview(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liefert eine Vorschau des aktuellen Mahnwesen-Stands."""
    try:
        result = db.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE overdue_days > 0) AS open_items_count,
                COALESCE(SUM(balance) FILTER (WHERE overdue_days > 0), 0) AS total_overdue,
                COUNT(*) FILTER (WHERE dunning_level = 1) AS level_1,
                COUNT(*) FILTER (WHERE dunning_level = 2) AS level_2,
                COUNT(*) FILTER (WHERE dunning_level = 3) AS level_3
            FROM domain_shared.open_items
            WHERE tenant_id = :tid AND status = 'open' AND type = 'debitor'
        """), {"tid": tenant_id})
        row = result.fetchone()
    except Exception:
        row = None

    if row:
        preview = MahnwesenPreview(
            tenant_id=tenant_id,
            open_items_count=row.open_items_count or 0,
            total_overdue_amount=float(row.total_overdue or 0),
            dunning_level_counts={
                "1": row.level_1 or 0,
                "2": row.level_2 or 0,
                "3": row.level_3 or 0,
            },
            export_ready=True,
        )
    else:
        preview = MahnwesenPreview(
            tenant_id=tenant_id,
            open_items_count=0,
            total_overdue_amount=0.0,
            dunning_level_counts={"1": 0, "2": 0, "3": 0},
            export_ready=True,
        )
    return preview.model_dump(mode="json")


@router.post("/mahnwesen/export", response_model=dict, status_code=202)
async def export_mahnwesen(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Startet den Mahnwesen-Export und gibt das Export-Ergebnis zurück (202 Accepted)."""
    fmt = body.get("format", MahnwesenExportFormat.PDF)
    dunning_level_filter = body.get("dunning_level_filter")
    export_id = str(uuid.uuid4())

    export_params: dict = {}
    if dunning_level_filter is not None:
        export_params["dunning_level_filter"] = int(dunning_level_filter)

    record_count = 0
    try:
        level_clause = ""
        params: dict = {"tid": tenant_id}
        if dunning_level_filter is not None:
            level_clause = " AND dunning_level = :dlevel"
            params["dlevel"] = int(dunning_level_filter)
        result = db.execute(
            text(
                f"""
            SELECT COUNT(*) AS cnt
            FROM domain_shared.open_items
            WHERE tenant_id = :tid AND status = 'open' AND type = 'debitor'
              AND overdue_days > 0{level_clause}
        """
            ),
            params,
        )
        row = result.fetchone()
        if row:
            record_count = row.cnt or 0
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass

    dms_meta: dict = {"dms_upload": None, "dms_url": None}
    try:
        _insert_finance_export_stub(
            db,
            export_id=export_id,
            tenant_id=tenant_id,
            kind="mahnwesen",
            run_id=None,
            record_count=record_count,
            params_json=export_params or None,
        )
        if record_count > 0 and (
            os.environ.get("DMS_DOCUMENT_TYPE_ID")
            or os.environ.get("FINANCE_EXPORT_S3_BUCKET")
        ):
            from app.integrations.finance_export_upload import upload_finance_export_csv

            rows = _mahnwesen_csv_rows(db, tenant_id, export_params or None)
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
            ) as tmp:
                w = csv.writer(tmp, delimiter=";")
                for r in rows:
                    w.writerow(r)
                tmp_path = tmp.name
            try:
                up = upload_finance_export_csv(
                    tmp_path,
                    label=f"mahnwesen-{export_id}.csv",
                    tenant_id=tenant_id,
                )
                if up.get("ok") and (up.get("document_id") or up.get("url")):
                    db.execute(
                        text(
                            """
                            UPDATE domain_shared.finance_followup_exports
                            SET dms_document_id = :did, dms_view_url = :url
                            WHERE id = CAST(:eid AS uuid)
                            """
                        ),
                        {
                            "did": up.get("document_id"),
                            "url": up.get("url"),
                            "eid": export_id,
                        },
                    )
                    dms_meta = {
                        "export_upload": "ok",
                        "export_backend": up.get("backend"),
                        "export_url": up.get("url"),
                        "dms_document_id": up.get("document_id"),
                    }
                else:
                    dms_meta = {"export_upload": "skipped", "detail": up.get("error")}
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        db.commit()
    except Exception as exc:
        logger.debug("finance_followup_exports (mahnwesen): %s", exc)
        db.rollback()

    download_url = (
        f"/api/v1/finance/followup/mahnwesen/export/{export_id}/download"
        if record_count > 0
        else None
    )

    result = MahnwesenExportResult(
        export_id=export_id,
        tenant_id=tenant_id,
        format=MahnwesenExportFormat(fmt) if isinstance(fmt, str) else fmt,
        record_count=record_count,
        download_url=download_url,
    )
    out = result.model_dump(mode="json")
    out.update(dms_meta)
    return out


@router.get("/mahnwesen/export/{export_id}/download")
async def download_mahnwesen_export(
    export_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """CSV-Download fuer Mahnwesen; optional Redirect auf DMS-Spiegel."""
    stub = _get_export_stub(db, export_id, tenant_id)
    if not stub or stub.kind != "mahnwesen":
        raise HTTPException(status_code=404, detail="Export nicht gefunden")
    redir = _maybe_redirect_dms(stub)
    if redir:
        return redir
    rows = _mahnwesen_csv_rows(db, tenant_id, _stub_params_json(stub))
    return _stream_csv(f"mahnwesen-{export_id}.csv", rows)


# ---------------------------------------------------------------------------
# Lastschriften
# ---------------------------------------------------------------------------

@router.get("/lastschriften/{run_id}/preview", response_model=dict)
async def get_lastschrift_preview(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liefert eine Vorschau eines Lastschriften-Runs."""
    total_amount = 0.0
    debitor_count = 0
    mandate_valid_count = 0
    mandate_expired_count = 0
    try:
        result = db.execute(text("""
            SELECT
                COALESCE(SUM(amount), 0) AS total_amount,
                COUNT(DISTINCT debitor_id) AS debitor_count
            FROM domain_shared.direct_debit_items
            WHERE tenant_id = :tid AND run_id = :run_id
        """), {"tid": tenant_id, "run_id": run_id})
        row = result.fetchone()
        if row:
            total_amount = float(row.total_amount or 0)
            debitor_count = row.debitor_count or 0
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass

    try:
        result = db.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE mandate_valid = true) AS valid_count,
                COUNT(*) FILTER (WHERE mandate_valid = false OR mandate_expired_at < NOW()) AS expired_count
            FROM domain_shared.sepa_mandates
            WHERE tenant_id = :tid AND debitor_id IN (
                SELECT DISTINCT debitor_id FROM domain_shared.direct_debit_items
                WHERE tenant_id = :tid AND run_id = :run_id
            )
        """), {"tid": tenant_id, "run_id": run_id})
        mrow = result.fetchone()
        if mrow:
            mandate_valid_count = mrow.valid_count or 0
            mandate_expired_count = mrow.expired_count or 0
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass

    preview = LastschriftPreview(
        tenant_id=tenant_id,
        direct_debit_run_id=run_id,
        total_amount=total_amount,
        debitor_count=debitor_count,
        mandate_valid_count=mandate_valid_count,
        mandate_expired_count=mandate_expired_count,
        sepa_ready=(mandate_expired_count == 0 and debitor_count > 0),
    )
    return preview.model_dump(mode="json")


@router.post("/lastschriften/{run_id}/export", response_model=dict, status_code=202)
async def export_lastschriften(
    run_id: str,
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Startet den SEPA-Export eines Lastschriften-Runs (202 Accepted)."""
    export_id = str(uuid.uuid4())
    record_count = 0
    try:
        result = db.execute(
            text(
                """
            SELECT COUNT(*) AS cnt
            FROM domain_shared.direct_debit_items
            WHERE tenant_id = :tid AND run_id = :run_id
        """
            ),
            {"tid": tenant_id, "run_id": run_id},
        )
        row = result.fetchone()
        if row:
            record_count = row.cnt or 0
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass

    dms_meta: dict = {}
    try:
        _insert_finance_export_stub(
            db,
            export_id=export_id,
            tenant_id=tenant_id,
            kind="lastschrift",
            run_id=run_id,
            record_count=record_count,
            params_json={"run_id": run_id},
        )
        if record_count > 0 and (
            os.environ.get("DMS_DOCUMENT_TYPE_ID")
            or os.environ.get("FINANCE_EXPORT_S3_BUCKET")
        ):
            from app.integrations.finance_export_upload import upload_finance_export_csv

            rows = _lastschrift_csv_rows(db, tenant_id, run_id)
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
            ) as tmp:
                w = csv.writer(tmp, delimiter=";")
                for r in rows:
                    w.writerow(r)
                tmp_path = tmp.name
            try:
                up = upload_finance_export_csv(
                    tmp_path,
                    label=f"lastschrift-{run_id}-{export_id}.csv",
                    tenant_id=tenant_id,
                )
                if up.get("ok") and (up.get("document_id") or up.get("url")):
                    db.execute(
                        text(
                            """
                            UPDATE domain_shared.finance_followup_exports
                            SET dms_document_id = :did, dms_view_url = :url
                            WHERE id = CAST(:eid AS uuid)
                            """
                        ),
                        {
                            "did": up.get("document_id"),
                            "url": up.get("url"),
                            "eid": export_id,
                        },
                    )
                    dms_meta = {
                        "export_upload": "ok",
                        "export_backend": up.get("backend"),
                        "export_url": up.get("url"),
                        "dms_document_id": up.get("document_id"),
                    }
                else:
                    dms_meta = {"export_upload": "skipped", "detail": up.get("error")}
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        db.commit()
    except Exception as exc:
        logger.debug("finance_followup_exports (lastschrift): %s", exc)
        db.rollback()

    download_url = (
        f"/api/v1/finance/followup/lastschriften/{run_id}/export/{export_id}/download"
        if record_count > 0
        else None
    )

    result = LastschriftExportResult(
        export_id=export_id,
        tenant_id=tenant_id,
        direct_debit_run_id=run_id,
        record_count=record_count,
        download_url=download_url,
    )
    out = result.model_dump(mode="json")
    out.update(dms_meta)
    return out


@router.get("/lastschriften/{run_id}/export/{export_id}/download")
async def download_lastschrift_export(
    run_id: str,
    export_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    stub = _get_export_stub(db, export_id, tenant_id)
    if not stub or stub.kind != "lastschrift" or (stub.run_id or "") != run_id:
        raise HTTPException(status_code=404, detail="Export nicht gefunden")
    redir = _maybe_redirect_dms(stub)
    if redir:
        return redir
    rows = _lastschrift_csv_rows(db, tenant_id, run_id)
    return _stream_csv(f"lastschrift-{run_id}-{export_id}.csv", rows)


# ---------------------------------------------------------------------------
# Kasse / POS-Folge (TSE-Compliance, Dokumentations-Export)
# ---------------------------------------------------------------------------


@router.get("/kasse/preview", response_model=dict)
async def get_kassenfolge_preview(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Vorschau offener POS-/Kassen-Folgethemen (Compliance-Eintraege pro Tenant)."""
    total = 0
    pending = 0
    try:
        row = db.execute(
            text(
                """
                SELECT COUNT(*) AS cnt
                FROM domain_docflow.pos_receipt_compliance
                WHERE tenant_id = :tid
                """
            ),
            {"tid": tenant_id},
        ).fetchone()
        if row:
            total = int(row.cnt or 0)
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass

    try:
        prow = db.execute(
            text(
                """
                SELECT COUNT(*) AS cnt
                FROM domain_docflow.pos_receipt_compliance
                WHERE tenant_id = :tid
                  AND dsfinvk_export_batch_id IS NULL
                """
            ),
            {"tid": tenant_id},
        ).fetchone()
        if prow:
            pending = int(prow.cnt or 0)
    except Exception:
        pending = 0

    preview = KassenfolgePreview(
        tenant_id=tenant_id,
        pos_compliance_records=total,
        pending_export_count=pending,
        export_ready=total > 0,
    )
    return preview.model_dump(mode="json")


@router.post("/kasse/export", response_model=dict, status_code=202)
async def export_kassenfolge(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Startet einen Export-Paketlauf fuer Kassen-/POS-TSE-Dokumentation (202 Accepted)."""
    export_id = str(uuid.uuid4())
    record_count = 0
    try:
        row = db.execute(
            text(
                """
                SELECT COUNT(*) AS cnt
                FROM domain_docflow.pos_receipt_compliance
                WHERE tenant_id = :tid
                """
            ),
            {"tid": tenant_id},
        ).fetchone()
        if row:
            record_count = int(row.cnt or 0)
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass

    fmt = str(body.get("format") or "zip")[:32]
    dms_meta: dict = {}
    try:
        _insert_finance_export_stub(
            db,
            export_id=export_id,
            tenant_id=tenant_id,
            kind="kasse",
            run_id=None,
            record_count=record_count,
            params_json={"format": fmt},
        )
        if record_count > 0 and (
            os.environ.get("DMS_DOCUMENT_TYPE_ID")
            or os.environ.get("FINANCE_EXPORT_S3_BUCKET")
        ):
            from app.integrations.finance_export_upload import upload_finance_export_csv

            rows = _kasse_csv_rows(db, tenant_id)
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
            ) as tmp:
                w = csv.writer(tmp, delimiter=";")
                for r in rows:
                    w.writerow(r)
                tmp_path = tmp.name
            try:
                up = upload_finance_export_csv(
                    tmp_path,
                    label=f"kasse-{export_id}.csv",
                    tenant_id=tenant_id,
                )
                if up.get("ok") and (up.get("document_id") or up.get("url")):
                    db.execute(
                        text(
                            """
                            UPDATE domain_shared.finance_followup_exports
                            SET dms_document_id = :did, dms_view_url = :url
                            WHERE id = CAST(:eid AS uuid)
                            """
                        ),
                        {
                            "did": up.get("document_id"),
                            "url": up.get("url"),
                            "eid": export_id,
                        },
                    )
                    dms_meta = {
                        "export_upload": "ok",
                        "export_backend": up.get("backend"),
                        "export_url": up.get("url"),
                        "dms_document_id": up.get("document_id"),
                    }
                else:
                    dms_meta = {"export_upload": "skipped", "detail": up.get("error")}
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        db.commit()
    except Exception as exc:
        logger.debug("finance_followup_exports (kasse): %s", exc)
        db.rollback()

    download_url = (
        f"/api/v1/finance/followup/kasse/export/{export_id}/download"
        if record_count > 0
        else None
    )
    result = KassenfolgeExportResult(
        export_id=export_id,
        tenant_id=tenant_id,
        format=fmt,
        record_count=record_count,
        download_url=download_url,
    )
    out = result.model_dump(mode="json")
    out.update(dms_meta)
    return out


@router.get("/kasse/export/{export_id}/download")
async def download_kasse_export(
    export_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    stub = _get_export_stub(db, export_id, tenant_id)
    if not stub or stub.kind != "kasse":
        raise HTTPException(status_code=404, detail="Export nicht gefunden")
    redir = _maybe_redirect_dms(stub)
    if redir:
        return redir
    rows = _kasse_csv_rows(db, tenant_id)
    return _stream_csv(f"kasse-{export_id}.csv", rows)
