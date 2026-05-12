"""
FIBU Connector Workflow – Upload → Parse → Validate → Post → (optional) Reverse.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.connectors.base import NormalizedItem, NormalizedLine, validate_item_balance
from app.core.connectors.payroll_parser import PayrollParser
from app.core.connectors.asset_ledger_parser import AssetLedgerParser
from app.core.data_quality_enforcement import DQValidationException
from app.core.gobd_artifact import sha256_hex
from app.core.fibu_audit import log_fibu_audit

logger = logging.getLogger(__name__)

CONNECTOR_TYPES = ("PAYROLL", "ASSET_LEDGER")
RUN_STATUSES = ("DRAFT", "PARSED", "VALIDATED", "POSTED", "FAILED", "CANCELLED", "REVERSED")
ITEM_STATUSES = ("OK", "ERROR", "POSTED")


def get_parser(connector_type: str):
    if connector_type == "PAYROLL":
        return PayrollParser()
    if connector_type == "ASSET_LEDGER":
        return AssetLedgerParser()
    raise ValueError(f"Unknown connector_type: {connector_type}")


def _item_to_payload(item: NormalizedItem) -> dict:
    return {
        "booking_date": item.booking_date,
        "document_no": item.document_no,
        "text": item.text,
        "lines": [
            {"account": line_item.account, "dc": line_item.dc, "amount": str(line_item.amount), "tax_code": line_item.tax_code, "cost_center": line_item.cost_center}
            for line_item in item.lines
        ],
        "asset_no": item.asset_no,
        "asset_name": item.asset_name,
        "posting_type": item.posting_type,
    }


def create_run(
    db: Session,
    tenant_id: str,
    connector_type: str,
    profile_id: Optional[str],
    idempotency_key: Optional[str],
    created_by: Optional[str],
) -> str:
    if idempotency_key:
        existing = db.execute(
            text("""
                SELECT id FROM domain_erp.fibu_connector_runs
                WHERE tenant_id = :tid AND connector_type = :ct AND idempotency_key = :key
            """),
            {"tid": tenant_id, "ct": connector_type, "key": idempotency_key},
        ).fetchone()
        if existing:
            return existing[0]

    run_id = str(uuid4())
    db.execute(
        text("""
            INSERT INTO domain_erp.fibu_connector_runs
            (id, tenant_id, connector_type, direction, profile_id, idempotency_key, status, started_at, created_by)
            VALUES (:id, :tenant_id, :connector_type, 'IMPORT', :profile_id, :idempotency_key, 'DRAFT', NOW(), :created_by)
        """),
        {
            "id": run_id,
            "tenant_id": tenant_id,
            "connector_type": connector_type,
            "profile_id": profile_id,
            "idempotency_key": idempotency_key,
            "created_by": created_by,
        },
    )
    db.commit()
    return run_id


def set_run_artifact(
    db: Session,
    run_id: str,
    tenant_id: str,
    file_content: bytes,
    file_name: Optional[str],
    storage_key: str,
) -> None:
    h = sha256_hex(file_content)
    db.execute(
        text("""
            UPDATE domain_erp.fibu_connector_runs
            SET source_artifact_storage_key = :sk, source_artifact_sha256 = :sha, source_artifact_file_name = :fn
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"sk": storage_key, "sha": h, "fn": file_name, "id": run_id, "tenant_id": tenant_id},
    )
    db.commit()


def parse_run(db: Session, run_id: str, tenant_id: str, file_content: bytes) -> None:
    row = db.execute(
        text("""
            SELECT connector_type, profile_id FROM domain_erp.fibu_connector_runs
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {"id": run_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise ValueError("Run not found")
    connector_type, profile_id = row[0], row[1]
    settings, mapping = {}, {}
    if profile_id:
        pr = db.execute(
            text("SELECT settings, mapping FROM domain_erp.fibu_connector_profiles WHERE id = :id"),
            {"id": profile_id},
        ).fetchone()
        if pr:
            settings = pr[0] or {}
            mapping = pr[1] or {}

    parser = get_parser(connector_type)
    try:
        items = parser.parse(file_content, settings, mapping)
    except DQValidationException as exc:
        db.execute(
            text("""
                UPDATE domain_erp.fibu_connector_runs
                SET status = 'FAILED', error_summary = :err, finished_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {
                "id": run_id,
                "tenant_id": tenant_id,
                "err": json.dumps(exc.detail),
            },
        )
        db.commit()
        raise
    except Exception as exc:
        db.execute(
            text("""
                UPDATE domain_erp.fibu_connector_runs
                SET status = 'FAILED', error_summary = :err, finished_at = NOW()
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {
                "id": run_id,
                "tenant_id": tenant_id,
                "err": str(exc),
            },
        )
        db.commit()
        raise

    # Run-Items anlegen
    for i, item in enumerate(items, start=1):
        item_id = str(uuid4())
        payload = _item_to_payload(item)
        err = validate_item_balance(item)
        status = "ERROR" if err else "OK"
        val_errors = [err] if err else None
        db.execute(
            text("""
                INSERT INTO domain_erp.fibu_connector_run_items
                (id, run_id, line_no, item_type, payload, validation_errors, status)
                VALUES (:id, :run_id, :line_no, 'JOURNAL_ENTRY_LINE', :payload::jsonb, :validation_errors::jsonb, :status)
            """),
            {
                "id": item_id,
                "run_id": run_id,
                "line_no": i,
                "payload": json.dumps(payload),
                "validation_errors": json.dumps(val_errors) if val_errors else None,
                "status": status,
            },
        )

    total_d = sum(sum(line_item.amount for line_item in it.lines if line_item.dc == "D") for it in items)
    total_c = sum(sum(line_item.amount for line_item in it.lines if line_item.dc == "C") for it in items)
    err_count = sum(1 for it in items if validate_item_balance(it))
    db.execute(
        text("""
            UPDATE domain_erp.fibu_connector_runs
            SET status = 'PARSED', counts = :counts::jsonb, totals = :totals::jsonb, finished_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
        """),
        {
            "id": run_id,
            "tenant_id": tenant_id,
            "counts": json.dumps({"lines_total": len(items), "lines_ok": len(items) - err_count, "lines_err": err_count}),
            "totals": json.dumps({"debit": str(total_d), "credit": str(total_c)}),
        },
    )
    db.commit()
    log_fibu_audit(db, tenant_id, "parse", "connector_run", run_id, {"connector_type": connector_type, "items": len(items)}, request=None)


def validate_run(db: Session, run_id: str, tenant_id: str) -> None:
    """Setzt Status auf VALIDATED; Fehler bleiben in run_items."""
    run = db.execute(
        text("SELECT status, counts FROM domain_erp.fibu_connector_runs WHERE id = :id AND tenant_id = :tid"),
        {"id": run_id, "tenant_id": tenant_id},
    ).fetchone()
    if not run:
        raise ValueError("Run not found")
    if run[0] not in ("DRAFT", "PARSED"):
        raise ValueError(f"Run status must be DRAFT or PARSED, got {run[0]}")
    counts = run[1] or {}
    lines_err = counts.get("lines_err", 0)
    if lines_err and lines_err > 0:
        db.execute(
            text("""
                UPDATE domain_erp.fibu_connector_runs
                SET status = 'VALIDATED', error_summary = :err WHERE id = :id AND tenant_id = :tid
            """),
            {"err": f"{lines_err} Zeilen mit Fehlern", "id": run_id, "tenant_id": tenant_id},
        )
    else:
        db.execute(
            text("""
                UPDATE domain_erp.fibu_connector_runs SET status = 'VALIDATED' WHERE id = :id AND tenant_id = :tid
            """),
            {"id": run_id, "tenant_id": tenant_id},
        )
    db.commit()
    log_fibu_audit(db, tenant_id, "validate", "connector_run", run_id, {}, request=None)


def post_run(db: Session, run_id: str, tenant_id: str, request: Any = None) -> None:
    """Bucht alle OK-Items als Journal Entries; setzt source = connector_type, reference = run_id."""
    run = db.execute(
        text("""
            SELECT connector_type, status, profile_id FROM domain_erp.fibu_connector_runs
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": run_id, "tenant_id": tenant_id},
    ).fetchone()
    if not run:
        raise ValueError("Run not found")
    if run[1] != "VALIDATED":
        raise ValueError(f"Run must be VALIDATED, got {run[1]}")

    connector_type = run[0]
    source_system = connector_type  # PAYROLL or ASSET_LEDGER
    items = db.execute(
        text("""
            SELECT id, line_no, payload, status FROM domain_erp.fibu_connector_run_items
            WHERE run_id = :run_id AND status = 'OK' ORDER BY line_no
        """),
        {"run_id": run_id},
    ).fetchall()

    # Gruppieren nach document_no + booking_date (ein Beleg = mehrere Zeilen)
    from collections import defaultdict
    by_doc: Dict[str, List[tuple]] = defaultdict(list)
    for item_id, line_no, payload, status in items:
        if status != "OK" or not payload:
            continue
        key = f"{payload.get('booking_date')}_{payload.get('document_no')}"
        by_doc[key].append((item_id, payload))

    journal_entry_ids: List[str] = []
    for key, group in by_doc.items():
        if not group:
            continue
        first_payload = group[0][1]
        booking_date = first_payload.get("booking_date")
        document_no = first_payload.get("document_no") or f"IMP-{run_id[:8]}"
        text_desc = first_payload.get("text", "")

        all_lines: List[Dict] = []
        for _, pl in group:
            for ln in pl.get("lines", []):
                all_lines.append(ln)

        if not all_lines:
            continue

        total_debit = sum(Decimal(line_item.get("amount", 0)) for line_item in all_lines if line_item.get("dc") == "D")
        total_credit = sum(Decimal(line_item.get("amount", 0)) for line_item in all_lines if line_item.get("dc") == "C")
        if abs(total_debit - total_credit) > Decimal("0.01"):
            continue

        entry_id = str(uuid4())
        db.execute(
            text("""
                INSERT INTO domain_erp.journal_entries
                (id, tenant_id, entry_number, entry_date, posting_date, description, reference, source, total_debit, total_credit, status, created_at, updated_at)
                VALUES (:id, :tenant_id, :entry_number, :entry_date, :posting_date, :description, :reference, 'connector', :total_debit, :total_credit, 'posted', NOW(), NOW())
            """),
            {
                "id": entry_id,
                "tenant_id": tenant_id,
                "entry_number": document_no,
                "entry_date": booking_date,
                "posting_date": booking_date,
                "description": text_desc[:255] if text_desc else "Connector Import",
                "reference": run_id,
                "total_debit": total_debit,
                "total_credit": total_credit,
            },
        )

        # Kontonummer → account_id (chart_of_accounts)
        for line_no, ln in enumerate(all_lines, start=1):
            acc_num = ln.get("account", "")
            acc_row = db.execute(
                text("SELECT id FROM domain_erp.chart_of_accounts WHERE tenant_id = :tid AND account_number = :num LIMIT 1"),
                {"tid": tenant_id, "num": acc_num},
            ).fetchone()
            if not acc_row:
                continue
            line_id = f"{entry_id}-L{line_no}"
            debit = Decimal(ln.get("amount", 0)) if ln.get("dc") == "D" else Decimal("0")
            credit = Decimal(ln.get("amount", 0)) if ln.get("dc") == "C" else Decimal("0")
            db.execute(
                text("""
                    INSERT INTO domain_erp.journal_entry_lines
                    (id, tenant_id, journal_entry_id, account_id, debit, credit, line_number, description, created_at)
                    VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :debit, :credit, :line_number, :description, NOW())
                """),
                {
                    "id": line_id,
                    "tenant_id": tenant_id,
                    "journal_entry_id": entry_id,
                    "account_id": acc_row[0],
                    "debit": debit,
                    "credit": credit,
                    "line_number": line_no,
                    "description": text_desc[:200] if text_desc else None,
                },
            )

        journal_entry_ids.append(entry_id)
        log_fibu_audit(
            db, tenant_id, "create", "journal_entry", entry_id,
            {"source": "connector", "reference": run_id, "entry_number": document_no},
            request=request,
        )
        for item_id, _ in group:
            db.execute(
                text("UPDATE domain_erp.fibu_connector_run_items SET posted_entity_id = :eid, status = 'POSTED' WHERE id = :id"),
                {"eid": entry_id, "id": item_id},
            )

    db.execute(
        text("""
            UPDATE domain_erp.fibu_connector_runs
            SET status = 'POSTED', counts = jsonb_set(COALESCE(counts, '{}'), '{journal_entries_created}', to_jsonb(:cnt::int)), finished_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": run_id, "tenant_id": tenant_id, "cnt": len(journal_entry_ids)},
    )
    db.commit()
    log_fibu_audit(db, tenant_id, "post", "connector_run", run_id, {"journal_entries": len(journal_entry_ids), "source_system": source_system}, request=request)


def cancel_run(db: Session, run_id: str, tenant_id: str) -> None:
    run = db.execute(
        text("SELECT status FROM domain_erp.fibu_connector_runs WHERE id = :id AND tenant_id = :tid"),
        {"id": run_id, "tenant_id": tenant_id},
    ).fetchone()
    if not run:
        raise ValueError("Run not found")
    if run[0] not in ("DRAFT", "PARSED", "VALIDATED"):
        raise ValueError(f"Cannot cancel run in status {run[0]}")
    db.execute(
        text("UPDATE domain_erp.fibu_connector_runs SET status = 'CANCELLED' WHERE id = :id AND tenant_id = :tid"),
        {"id": run_id, "tenant_id": tenant_id},
    )
    db.commit()
    log_fibu_audit(db, tenant_id, "cancel", "connector_run", run_id, {}, request=None)


def reverse_run(db: Session, run_id: str, tenant_id: str, request: Any = None) -> None:
    """Erzeugt Gegenbuchungen für alle aus diesem Run erstellten Journal Entries (GoBD: kein Delete)."""
    run = db.execute(
        text("SELECT status FROM domain_erp.fibu_connector_runs WHERE id = :id AND tenant_id = :tid"),
        {"id": run_id, "tenant_id": tenant_id},
    ).fetchone()
    if not run:
        raise ValueError("Run not found")
    if run[0] != "POSTED":
        raise ValueError(f"Only POSTED runs can be reversed, got {run[0]}")

    items = db.execute(
        text("SELECT posted_entity_id FROM domain_erp.fibu_connector_run_items WHERE run_id = :run_id AND posted_entity_id IS NOT NULL"),
        {"run_id": run_id},
    ).fetchall()
    entry_ids = list({r[0] for r in items if r[0]})

    for entry_id in entry_ids:
        # Gegenbuchung: gleiche Zeilen, Soll/Haben getauscht (Spalten: debit, credit wie journal_entry_lines)
        lines = db.execute(
            text("""
                SELECT account_id, debit, credit, description FROM domain_erp.journal_entry_lines
                WHERE journal_entry_id = :eid
            """),
            {"eid": entry_id},
        ).fetchall()
        if not lines:
            continue
        rev_id = str(uuid4())
        _total_d = sum(Decimal(str(line_item[1])) for line_item in lines)  # noqa: F841
        _total_c = sum(Decimal(str(line_item[2])) for line_item in lines)  # noqa: F841
        db.execute(
            text("""
                INSERT INTO domain_erp.journal_entries
                (id, tenant_id, entry_number, entry_date, posting_date, description, reference, source, total_debit, total_credit, status, created_at, updated_at)
                SELECT :rev_id, tenant_id, 'STorno-' || entry_number, entry_date, posting_date, 'Storno: ' || description, :run_id, 'connector', total_credit, total_debit, 'posted', NOW(), NOW()
                FROM domain_erp.journal_entries WHERE id = :eid
            """),
            {"rev_id": rev_id, "run_id": run_id, "eid": entry_id},
        )
        for line_no, (acc_id, deb, cred, desc) in enumerate(lines, start=1):
            db.execute(
                text("""
                    INSERT INTO domain_erp.journal_entry_lines
                    (id, tenant_id, journal_entry_id, account_id, debit, credit, line_number, description, created_at)
                    VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :debit, :credit, :line_number, :description, NOW())
                """),
                {
                    "id": f"{rev_id}-L{line_no}",
                    "tenant_id": tenant_id,
                    "journal_entry_id": rev_id,
                    "account_id": acc_id,
                    "debit": cred,
                    "credit": deb,
                    "line_number": line_no,
                    "description": desc,
                },
            )
        log_fibu_audit(
            db, tenant_id, "create", "journal_entry", rev_id,
            {"source": "connector", "reference": run_id, "reversed_entry_id": entry_id},
            request=request,
        )

    db.execute(
        text("UPDATE domain_erp.fibu_connector_runs SET status = 'REVERSED' WHERE id = :id AND tenant_id = :tid"),
        {"id": run_id, "tenant_id": tenant_id},
    )
    db.commit()
    log_fibu_audit(db, tenant_id, "reverse", "connector_run", run_id, {"reversed_entries": len(entry_ids)}, request=request)
