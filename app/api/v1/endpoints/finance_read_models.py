"""
Finance Read-Models — Wave 2 AP2
Server-side pre-aggregated cockpit KPIs for stable query contracts.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.endpoint_gateways import (
    get_ap_invoice_store_loader,
    get_payment_run_store_loader,
    register_projection_status_loader,
)
from ....core.process_config import DEFAULT_PROCESS_VARIANTS
from ....core.tenant import get_tenant_id
from ....core.workflow_definitions import merge_workflow_variants

router = APIRouter(prefix="/finance/read-models", tags=["finance", "read-models"])


# ---------------------------------------------------------------------------
# Pydantic schemas — versioned stable contracts
# ---------------------------------------------------------------------------

class APInvoiceBucket(BaseModel):
    status: str
    count: int
    total_amount: float = 0.0


class APInvoiceCockpitReadModel(BaseModel):
    tenant_id: str
    buckets: list[APInvoiceBucket]  # one per semantic_status
    total_count: int
    pending_approval_count: int     # ZUR_FREIGABE + TEILWEISE_FREIGEGEBEN
    ready_to_post_count: int        # approval_can_post == True
    overdue_count: int              # ENTWURF older than 30 days
    schema_version: int = 1


class PaymentRunCockpitReadModel(BaseModel):
    tenant_id: str
    draft_count: int
    approved_count: int             # approval_can_execute == True
    executed_count: int
    total_pending_amount: float = 0.0
    schema_version: int = 1


class WorkflowInstanceSummary(BaseModel):
    process_key: str
    running_count: int
    waiting_count: int
    completed_today: int = 0
    failed_count: int = 0


class WorkflowStepSlaSummary(BaseModel):
    step_key: str
    timeout_hours: int | None = None
    escalation_roles: list[str] = Field(default_factory=list)


class WorkflowSlaProfile(BaseModel):
    process_key: str
    escalatable_steps: int = 0
    step_sla: list[WorkflowStepSlaSummary] = Field(default_factory=list)


class ProcessObservationReadModel(BaseModel):
    tenant_id: str
    workflow_instances: list[WorkflowInstanceSummary]
    sla_profiles: list[WorkflowSlaProfile] = Field(default_factory=list)
    total_running: int
    total_waiting: int
    overdue_instances: int = 0
    schema_version: int = 1


class CashClosingTotals(BaseModel):
    cash_expected: float = 0.0
    cash_counted: float = 0.0
    cash_difference: float = 0.0
    card_expected: float = 0.0
    card_counted: float = 0.0
    card_difference: float = 0.0
    paypal_expected: float = 0.0
    paypal_counted: float = 0.0
    paypal_difference: float = 0.0
    b2b_expected: float = 0.0
    gross_total: float = 0.0


class CashClosingPosting(BaseModel):
    journal_entry_id: str | None = None
    journal_entry_number: str | None = None
    posted_at: str | None = None
    posting_status: str | None = None


class CashClosingImportContext(BaseModel):
    import_batch_id: str | None = None
    import_source_label: str | None = None
    imported_at: str | None = None


class CashClosingReferenceContext(BaseModel):
    tse_transaction_count: int = 0
    source_document_refs: list[str] = Field(default_factory=list)


class CashClosingExceptionFlags(BaseModel):
    has_difference: bool = False
    has_import_gap: bool = False
    has_missing_posting: bool = False


class CashClosingSnapshot(BaseModel):
    id: str
    closing_date: str | None = None
    location_id: str | None = None
    location_name: str | None = None
    cash_register_id: str | None = None
    cash_register_name: str | None = None
    operator_name: str | None = None
    source: str = "POS"
    workflow_status: str = "draft"
    currency: str = "EUR"
    totals: CashClosingTotals
    posting: CashClosingPosting
    import_context: CashClosingImportContext
    reference_context: CashClosingReferenceContext
    exception_flags: CashClosingExceptionFlags


class CashClosingReadModel(BaseModel):
    tenant_id: str
    items: list[CashClosingSnapshot] = Field(default_factory=list)
    total_count: int
    schema_version: int = 1


class CashClosingAnalysisBucket(BaseModel):
    key: str
    count: int


class CashClosingAnalysisReadModel(BaseModel):
    tenant_id: str
    total_count: int
    exception_count: int
    balanced_count: int
    missing_posting_count: int
    difference_count: int
    import_context_count: int
    top_exception_operators: list[CashClosingAnalysisBucket]
    top_exception_dates: list[CashClosingAnalysisBucket]
    schema_version: int = 1


class CashClosingReportingBucket(BaseModel):
    period_key: str
    closing_count: int
    gross_total: float = 0.0
    exception_count: int = 0
    difference_total: float = 0.0
    missing_posting_count: int = 0


class CashClosingReportingReadModel(BaseModel):
    tenant_id: str
    periods: list[CashClosingReportingBucket]
    total_count: int
    total_gross: float = 0.0
    total_difference: float = 0.0
    schema_version: int = 1


class ProjectionRebuildEntry(BaseModel):
    projection_key: str
    item_count: int = 0


class ProjectionRebuildResult(BaseModel):
    tenant_id: str
    rebuilt_at: str
    projections: list[ProjectionRebuildEntry] = Field(default_factory=list)
    schema_version: int = 1


class ProjectionStatusEntry(BaseModel):
    projection_key: str
    item_count: int = 0
    cached: bool = True
    cursor_status: str | None = None
    cursor_source: str | None = None
    cursor_updated_at: str | None = None
    last_processed_event_id: str | None = None


class ProjectionStatusReadModel(BaseModel):
    tenant_id: str
    projection_count: int = 0
    persisted_snapshot_count: int = 0
    persisted_cursor_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_rebuilt_at: str | None = None
    last_snapshot_at: str | None = None
    last_cursor_advanced_at: str | None = None
    last_processed_event_id: str | None = None
    projections: list[ProjectionStatusEntry] = Field(default_factory=list)
    schema_version: int = 1


# ---------------------------------------------------------------------------
# Helpers — query from in-memory stores used by existing endpoints
# ---------------------------------------------------------------------------

_PROJECTION_STORE: dict[str, dict[str, dict[str, Any]]] = {}
_PROJECTION_META: dict[str, dict[str, Any]] = {}
_DEFAULT_PROJECTION_CONSUMER_ID = "finance-projections-01"
_REPLAY_PROJECTION_CONSUMER_ID = "finance-projections-01/replay"

def _get_ap_invoice_store() -> dict[str, Any] | None:
    loader = get_ap_invoice_store_loader()
    return loader() if loader else None


def _get_payment_run_store() -> dict[str, Any] | None:
    loader = get_payment_run_store_loader()
    return loader() if loader else None


def _as_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _parse_items_blob(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _iso_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value)


def _iso_datetime(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _reporting_period_key(value: str | None) -> str:
    if not value:
        return "ohne-periode"
    return value[:7] if len(value) >= 7 else value


def _map_cash_workflow_status(raw_status: str | None, has_posting: bool, has_missing_posting: bool) -> str:
    status = (raw_status or "").lower()
    if has_missing_posting:
        return "exception"
    if status in {"gebucht", "posted"}:
        return "posted" if has_posting else "booked"
    if status in {"reconciled", "abgeglichen"}:
        return "reconciled"
    if status in {"draft", "offen", "open"}:
        return "draft"
    return "posted" if has_posting else "draft"


def _projection_bucket(tenant_id: str) -> dict[str, dict[str, Any]]:
    return _PROJECTION_STORE.setdefault(tenant_id, {})


def _projection_meta(tenant_id: str) -> dict[str, Any]:
    return _PROJECTION_META.setdefault(
        tenant_id,
        {
            "last_rebuilt_at": None,
            "cache_hits": 0,
            "cache_misses": 0,
        },
    )


def _ensure_projection_registry_table(db: Session) -> None:
    try:
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS domain_shared.process_projection_registry (
                    tenant_id TEXT NOT NULL,
                    projection_key TEXT NOT NULL,
                    item_count INTEGER NOT NULL DEFAULT 0,
                    last_rebuilt_at TEXT NULL,
                    last_accessed_at TEXT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, projection_key)
                )
                """
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise


def _ensure_projection_snapshot_table(db: Session) -> None:
    try:
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS domain_shared.process_projection_snapshots (
                    tenant_id TEXT NOT NULL,
                    projection_key TEXT NOT NULL,
                    schema_version INTEGER NOT NULL DEFAULT 1,
                    item_count INTEGER NOT NULL DEFAULT 0,
                    payload TEXT NOT NULL,
                    rebuilt_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, projection_key)
                )
                """
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise


def _ensure_projection_cursor_table(db: Session) -> None:
    try:
        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS domain_shared.process_projection_cursors (
                    tenant_id TEXT NOT NULL,
                    consumer_id TEXT NOT NULL,
                    projection_key TEXT NOT NULL,
                    schema_version INTEGER NOT NULL DEFAULT 1,
                    cursor_token TEXT NULL,
                    last_event_id TEXT NULL,
                    source_rebuilt_at TEXT NULL,
                    replay_from_event_id TEXT NULL,
                    replay_to_event_id TEXT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, consumer_id, projection_key)
                )
                """
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise


def _persist_projection_registry_entry(
    db: Session | None,
    tenant_id: str,
    projection_key: str,
    item_count: int,
    *,
    rebuilt_at: str | None = None,
    accessed_at: str | None = None,
) -> None:
    if db is None:
        return
    now = datetime.now(tz=timezone.utc).isoformat()
    try:
        _ensure_projection_registry_table(db)
        db.execute(
            text(
                """
                INSERT INTO domain_shared.process_projection_registry (
                    tenant_id, projection_key, item_count, last_rebuilt_at, last_accessed_at, updated_at
                ) VALUES (
                    :tenant_id, :projection_key, :item_count, :last_rebuilt_at, :last_accessed_at, :updated_at
                )
                ON CONFLICT (tenant_id, projection_key) DO UPDATE SET
                    item_count = EXCLUDED.item_count,
                    last_rebuilt_at = COALESCE(EXCLUDED.last_rebuilt_at, domain_shared.process_projection_registry.last_rebuilt_at),
                    last_accessed_at = COALESCE(EXCLUDED.last_accessed_at, domain_shared.process_projection_registry.last_accessed_at),
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "tenant_id": tenant_id,
                "projection_key": projection_key,
                "item_count": item_count,
                "last_rebuilt_at": rebuilt_at,
                "last_accessed_at": accessed_at,
                "updated_at": now,
            },
        )
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass


def _persist_projection_snapshot(
    db: Session | None,
    tenant_id: str,
    projection_key: str,
    payload: BaseModel,
    *,
    rebuilt_at: str,
) -> None:
    if db is None:
        return
    item_count = _count_projection_items(payload)
    now = datetime.now(tz=timezone.utc).isoformat()
    try:
        _ensure_projection_snapshot_table(db)
        db.execute(
            text(
                """
                INSERT INTO domain_shared.process_projection_snapshots (
                    tenant_id, projection_key, schema_version, item_count, payload, rebuilt_at, updated_at
                ) VALUES (
                    :tenant_id, :projection_key, :schema_version, :item_count, :payload, :rebuilt_at, :updated_at
                )
                ON CONFLICT (tenant_id, projection_key) DO UPDATE SET
                    schema_version = EXCLUDED.schema_version,
                    item_count = EXCLUDED.item_count,
                    payload = EXCLUDED.payload,
                    rebuilt_at = EXCLUDED.rebuilt_at,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "tenant_id": tenant_id,
                "projection_key": projection_key,
                "schema_version": int(getattr(payload, "schema_version", 1) or 1),
                "item_count": item_count,
                "payload": json.dumps(payload.model_dump(mode="json")),
                "rebuilt_at": rebuilt_at,
                "updated_at": now,
            },
        )
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass


def persist_projection_cursor(
    db: Session | None,
    tenant_id: str,
    consumer_id: str,
    projection_key: str,
    *,
    cursor_token: str | None = None,
    last_event_id: str | None = None,
    source_rebuilt_at: str | None = None,
    replay_from_event_id: str | None = None,
    replay_to_event_id: str | None = None,
    status: str = "active",
) -> None:
    if db is None:
        return
    now = datetime.now(tz=timezone.utc).isoformat()
    try:
        _ensure_projection_cursor_table(db)
        db.execute(
            text(
                """
                INSERT INTO domain_shared.process_projection_cursors (
                    tenant_id,
                    consumer_id,
                    projection_key,
                    schema_version,
                    cursor_token,
                    last_event_id,
                    source_rebuilt_at,
                    replay_from_event_id,
                    replay_to_event_id,
                    status,
                    updated_at
                ) VALUES (
                    :tenant_id,
                    :consumer_id,
                    :projection_key,
                    :schema_version,
                    :cursor_token,
                    :last_event_id,
                    :source_rebuilt_at,
                    :replay_from_event_id,
                    :replay_to_event_id,
                    :status,
                    :updated_at
                )
                ON CONFLICT (tenant_id, consumer_id, projection_key) DO UPDATE SET
                    schema_version = EXCLUDED.schema_version,
                    cursor_token = EXCLUDED.cursor_token,
                    last_event_id = EXCLUDED.last_event_id,
                    source_rebuilt_at = EXCLUDED.source_rebuilt_at,
                    replay_from_event_id = EXCLUDED.replay_from_event_id,
                    replay_to_event_id = EXCLUDED.replay_to_event_id,
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "tenant_id": tenant_id,
                "consumer_id": consumer_id,
                "projection_key": projection_key,
                "schema_version": 1,
                "cursor_token": cursor_token,
                "last_event_id": last_event_id,
                "source_rebuilt_at": source_rebuilt_at,
                "replay_from_event_id": replay_from_event_id,
                "replay_to_event_id": replay_to_event_id,
                "status": status,
                "updated_at": now,
            },
        )
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass


def _load_persisted_projection_registry(
    db: Session | None,
    tenant_id: str,
) -> tuple[dict[str, ProjectionStatusEntry], str | None]:
    if db is None:
        return {}, None
    try:
        _ensure_projection_registry_table(db)
        rows = (
            db.execute(
                text(
                    """
                    SELECT projection_key, item_count, last_rebuilt_at
                    FROM domain_shared.process_projection_registry
                    WHERE tenant_id = :tenant_id
                    ORDER BY projection_key
                    """
                ),
                {"tenant_id": tenant_id},
            )
            .mappings()
            .all()
        )
    except Exception:
        return {}, None

    entries: dict[str, ProjectionStatusEntry] = {}
    last_rebuilt_at: str | None = None
    for row in rows:
        projection_key = str(row.get("projection_key") or "")
        rebuilt_at = row.get("last_rebuilt_at")
        if projection_key:
            entries[projection_key] = ProjectionStatusEntry(
                projection_key=projection_key,
                item_count=int(row.get("item_count") or 0),
                cached=projection_key in _projection_bucket(tenant_id),
            )
        if rebuilt_at and (last_rebuilt_at is None or str(rebuilt_at) > last_rebuilt_at):
            last_rebuilt_at = str(rebuilt_at)
    return entries, last_rebuilt_at


def _load_persisted_projection_snapshot_meta(
    db: Session | None,
    tenant_id: str,
) -> tuple[int, str | None]:
    if db is None:
        return 0, None
    try:
        _ensure_projection_snapshot_table(db)
        rows = (
            db.execute(
                text(
                    """
                    SELECT projection_key, rebuilt_at
                    FROM domain_shared.process_projection_snapshots
                    WHERE tenant_id = :tenant_id
                    ORDER BY projection_key
                    """
                ),
                {"tenant_id": tenant_id},
            )
            .mappings()
            .all()
        )
    except Exception:
        return 0, None

    last_snapshot_at: str | None = None
    for row in rows:
        rebuilt_at = row.get("rebuilt_at")
        if rebuilt_at and (last_snapshot_at is None or str(rebuilt_at) > last_snapshot_at):
            last_snapshot_at = str(rebuilt_at)
    return len(rows), last_snapshot_at


def _load_persisted_projection_cursor_meta(
    db: Session | None,
    tenant_id: str,
    *,
    consumer_id: str | None = None,
) -> tuple[int, str | None, str | None]:
    if db is None:
        return 0, None, None
    try:
        _ensure_projection_cursor_table(db)
        statement = """
            SELECT consumer_id, projection_key, updated_at, last_event_id
            FROM domain_shared.process_projection_cursors
            WHERE tenant_id = :tenant_id
        """
        params: dict[str, Any] = {"tenant_id": tenant_id}
        if consumer_id:
            statement += " AND consumer_id = :consumer_id"
            params["consumer_id"] = consumer_id
        statement += " ORDER BY consumer_id, projection_key"
        rows = db.execute(text(statement), params).mappings().all()
    except Exception:
        return 0, None, None

    last_cursor_advanced_at: str | None = None
    last_processed_event_id: str | None = None
    for row in rows:
        updated_at = row.get("updated_at")
        if updated_at and (last_cursor_advanced_at is None or str(updated_at) > last_cursor_advanced_at):
            last_cursor_advanced_at = str(updated_at)
            last_processed_event_id = str(row.get("last_event_id")) if row.get("last_event_id") else None
    return len(rows), last_cursor_advanced_at, last_processed_event_id


def _infer_cursor_source(
    projection_key: str,
    last_event_id: str | None,
    replay_from_event_id: str | None,
    replay_to_event_id: str | None,
) -> str | None:
    if replay_from_event_id or replay_to_event_id:
        return "runtime_replay"
    if last_event_id and last_event_id.startswith("replay-"):
        return "workflow_audit"
    if projection_key == "ap-invoice-cockpit":
        return "outbox_events"
    if projection_key == "payment-run-cockpit":
        return "outbox_events"
    if projection_key.startswith("cash-closings"):
        return "outbox_events"
    return None


def _load_persisted_projection_cursor_entries(
    db: Session | None,
    tenant_id: str,
    *,
    consumer_id: str | None = None,
) -> dict[str, ProjectionStatusEntry]:
    if db is None:
        return {}
    try:
        _ensure_projection_cursor_table(db)
        statement = """
            SELECT consumer_id, projection_key, status, updated_at, last_event_id, replay_from_event_id, replay_to_event_id
            FROM domain_shared.process_projection_cursors
            WHERE tenant_id = :tenant_id
        """
        params: dict[str, Any] = {"tenant_id": tenant_id}
        if consumer_id:
            statement += " AND consumer_id = :consumer_id"
            params["consumer_id"] = consumer_id
        statement += " ORDER BY consumer_id, projection_key"
        rows = db.execute(text(statement), params).mappings().all()
    except Exception:
        return {}

    entries: dict[str, ProjectionStatusEntry] = {}
    for row in rows:
        projection_key = str(row.get("projection_key") or "")
        if not projection_key:
            continue
        last_event_id = str(row.get("last_event_id")) if row.get("last_event_id") else None
        entries[projection_key] = ProjectionStatusEntry(
            projection_key=projection_key,
            item_count=0,
            cached=projection_key in _projection_bucket(tenant_id),
            cursor_status=str(row.get("status")) if row.get("status") else None,
            cursor_source=_infer_cursor_source(
                projection_key,
                last_event_id,
                str(row.get("replay_from_event_id")) if row.get("replay_from_event_id") else None,
                str(row.get("replay_to_event_id")) if row.get("replay_to_event_id") else None,
            ),
            cursor_updated_at=str(row.get("updated_at")) if row.get("updated_at") else None,
            last_processed_event_id=last_event_id,
        )
    return entries


def _cache_projection(tenant_id: str, projection_key: str, payload: BaseModel) -> BaseModel:
    _projection_bucket(tenant_id)[projection_key] = payload.model_dump(mode="json")
    return payload


def _load_projection(tenant_id: str, projection_key: str, model_type: type[BaseModel]) -> BaseModel | None:
    payload = _projection_bucket(tenant_id).get(projection_key)
    if payload is None:
        _projection_meta(tenant_id)["cache_misses"] += 1
        return None
    _projection_meta(tenant_id)["cache_hits"] += 1
    return model_type.model_validate(payload)


def _count_projection_items(payload: BaseModel) -> int:
    dumped = payload.model_dump()
    for key in ("items", "periods", "workflow_instances", "buckets", "step_sla", "projections"):
        value = dumped.get(key)
        if isinstance(value, list):
            return len(value)
    if "total_count" in dumped:
        return int(dumped["total_count"] or 0)
    return 1


def _count_projection_payload_items(payload: dict[str, Any]) -> int:
    for key in ("items", "periods", "workflow_instances", "buckets", "step_sla", "projections"):
        value = payload.get(key)
        if isinstance(value, list):
            return len(value)
    if "total_count" in payload:
        return int(payload["total_count"] or 0)
    return 1


def _latest_workflow_event_id(db: Session | None) -> str | None:
    if db is None:
        return None
    try:
        row = (
            db.execute(
                text(
                    """
                    SELECT domain, doc_number, ts
                    FROM workflow_audit
                    ORDER BY ts DESC
                    LIMIT 1
                    """
                )
            )
            .mappings()
            .first()
        )
    except Exception:
        return None
    if not row:
        return None
    domain = row.get("domain")
    doc_number = row.get("doc_number")
    ts = row.get("ts")
    if not domain or not doc_number or ts is None:
        return None
    return f"replay-{domain}-{doc_number}-{ts}"


def _latest_outbox_event_id(
    db: Session | None,
    *,
    tenant_id: str,
    event_types: list[str],
) -> str | None:
    if db is None or not event_types:
        return None
    conditions = []
    params: dict[str, Any] = {"tenant_id": tenant_id}
    for index, event_type in enumerate(event_types):
        key = f"event_type_{index}"
        conditions.append(f"event_type = :{key}")
        params[key] = event_type
    try:
        row = (
            db.execute(
                text(
                    f"""
                    SELECT id, event_type, timestamp
                    FROM outbox_events
                    WHERE tenant_id = :tenant_id
                      AND ({' OR '.join(conditions)})
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """
                ),
                params,
            )
            .mappings()
            .first()
        )
    except Exception:
        return None
    if not row or not row.get("id"):
        return None
    return str(row.get("id"))


def get_projection_status(tenant_id: str, db: Session | None = None) -> ProjectionStatusReadModel:
    bucket = _projection_bucket(tenant_id)
    meta = _projection_meta(tenant_id)
    persisted_entries, persisted_last_rebuilt_at = _load_persisted_projection_registry(db=db, tenant_id=tenant_id)
    persisted_snapshot_count, persisted_last_snapshot_at = _load_persisted_projection_snapshot_meta(db=db, tenant_id=tenant_id)
    persisted_cursor_count, persisted_last_cursor_advanced_at, persisted_last_processed_event_id = _load_persisted_projection_cursor_meta(
        db=db,
        tenant_id=tenant_id,
        consumer_id=_DEFAULT_PROJECTION_CONSUMER_ID,
    )
    persisted_cursor_entries = _load_persisted_projection_cursor_entries(
        db=db,
        tenant_id=tenant_id,
        consumer_id=_DEFAULT_PROJECTION_CONSUMER_ID,
    )
    in_memory_entries = {
        projection_key: ProjectionStatusEntry(
            projection_key=projection_key,
            item_count=_count_projection_payload_items(payload),
            cached=True,
        )
        for projection_key, payload in sorted(bucket.items())
    }
    merged_entries = {**persisted_entries}
    for projection_key, cursor_entry in persisted_cursor_entries.items():
        base_entry = merged_entries.get(
            projection_key,
            ProjectionStatusEntry(projection_key=projection_key, item_count=0, cached=False),
        )
        merged_entries[projection_key] = ProjectionStatusEntry(
            projection_key=projection_key,
            item_count=base_entry.item_count,
            cached=cursor_entry.cached,
            cursor_status=cursor_entry.cursor_status,
            cursor_source=cursor_entry.cursor_source,
            cursor_updated_at=cursor_entry.cursor_updated_at,
            last_processed_event_id=cursor_entry.last_processed_event_id,
        )
    for projection_key, in_memory_entry in in_memory_entries.items():
        base_entry = merged_entries.get(
            projection_key,
            ProjectionStatusEntry(projection_key=projection_key, item_count=0, cached=False),
        )
        merged_entries[projection_key] = ProjectionStatusEntry(
            projection_key=projection_key,
            item_count=in_memory_entry.item_count,
            cached=True,
            cursor_status=base_entry.cursor_status,
            cursor_source=base_entry.cursor_source,
            cursor_updated_at=base_entry.cursor_updated_at,
            last_processed_event_id=base_entry.last_processed_event_id,
        )
    projections = [
        ProjectionStatusEntry(
            projection_key=entry.projection_key,
            item_count=entry.item_count,
            cached=entry.cached,
            cursor_status=entry.cursor_status,
            cursor_source=entry.cursor_source,
            cursor_updated_at=entry.cursor_updated_at,
            last_processed_event_id=entry.last_processed_event_id,
        )
        for entry in sorted(merged_entries.values(), key=lambda entry: entry.projection_key)
    ]
    return ProjectionStatusReadModel(
        tenant_id=tenant_id,
        projection_count=len(projections),
        persisted_snapshot_count=persisted_snapshot_count,
        persisted_cursor_count=persisted_cursor_count,
        cache_hits=int(meta.get("cache_hits") or 0),
        cache_misses=int(meta.get("cache_misses") or 0),
        last_rebuilt_at=meta.get("last_rebuilt_at") or persisted_last_rebuilt_at,
        last_snapshot_at=persisted_last_snapshot_at,
        last_cursor_advanced_at=persisted_last_cursor_advanced_at,
        last_processed_event_id=persisted_last_processed_event_id,
        projections=projections,
        schema_version=1,
    )


register_projection_status_loader(get_projection_status)


def _build_sla_profiles(tenant_id: str, db: Session | None) -> list[WorkflowSlaProfile]:
    custom_variants: object = None
    if db is not None:
        try:
            settings_row = db.execute(
                text("SELECT settings FROM domain_shared.tenants WHERE id = :tenant_id"),
                {"tenant_id": tenant_id},
            ).first()
            if settings_row and settings_row[0]:
                raw_settings = settings_row[0]
                if isinstance(raw_settings, dict):
                    custom_variants = raw_settings.get("process_variants")
                elif isinstance(raw_settings, str):
                    parsed = json.loads(raw_settings)
                    if isinstance(parsed, dict):
                        custom_variants = parsed.get("process_variants")
        except Exception:
            custom_variants = None

    merged_variants = merge_workflow_variants(
        DEFAULT_PROCESS_VARIANTS,
        custom_variants,
        tenant_id=tenant_id,
    )

    profiles: list[WorkflowSlaProfile] = []
    for process_key, definition in sorted(merged_variants.items()):
        sla_defs = definition.get("step_sla") or {}
        step_sla = [
            WorkflowStepSlaSummary(
                step_key=step_key,
                timeout_hours=(sla.get("timeout_hours") or 0),
                escalation_roles=list(sla.get("escalation_roles") or []),
            )
            for step_key, sla in sorted(sla_defs.items())
            if isinstance(sla, dict)
        ]
        profiles.append(
            WorkflowSlaProfile(
                process_key=process_key,
                escalatable_steps=sum(1 for step in step_sla if step.timeout_hours and step.timeout_hours > 0),
                step_sla=step_sla,
            )
        )
    return profiles


def project_ap_invoice_cockpit(
    tenant_id: str,
    tenant_invoices: list[dict[str, Any]],
) -> APInvoiceCockpitReadModel:
    bucket_map: dict[str, APInvoiceBucket] = {}
    pending_approval_count = 0
    ready_to_post_count = 0
    overdue_count = 0
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=30)

    for inv in tenant_invoices:
        semantic = inv.get("semantic_status") or inv.get("status", "ENTWURF")
        amount = float(inv.get("amount", inv.get("netAmount", 0.0)) or 0.0)

        if semantic not in bucket_map:
            bucket_map[semantic] = APInvoiceBucket(status=semantic, count=0, total_amount=0.0)
        bucket_map[semantic].count += 1
        bucket_map[semantic].total_amount += amount

        if semantic in ("ZUR_FREIGABE", "TEILWEISE_FREIGEGEBEN"):
            pending_approval_count += 1

        if inv.get("approval_can_post") is True:
            ready_to_post_count += 1

        if semantic == "ENTWURF":
            created_raw = inv.get("created_at") or inv.get("createdAt")
            if created_raw:
                try:
                    if isinstance(created_raw, str):
                        created_dt = datetime.fromisoformat(created_raw)
                    else:
                        created_dt = created_raw
                    if created_dt.tzinfo is None:
                        created_dt = created_dt.replace(tzinfo=timezone.utc)
                    if created_dt < cutoff:
                        overdue_count += 1
                except (ValueError, TypeError):
                    pass

    buckets = list(bucket_map.values())
    return APInvoiceCockpitReadModel(
        tenant_id=tenant_id,
        buckets=buckets,
        total_count=sum(bucket.count for bucket in buckets),
        pending_approval_count=pending_approval_count,
        ready_to_post_count=ready_to_post_count,
        overdue_count=overdue_count,
        schema_version=1,
    )


def project_payment_run_cockpit(
    tenant_id: str,
    tenant_runs: list[dict[str, Any]],
) -> PaymentRunCockpitReadModel:
    draft_count = 0
    approved_count = 0
    executed_count = 0
    total_pending_amount = 0.0

    for run in tenant_runs:
        status = run.get("status", "draft")
        amount = float(run.get("total_amount", 0.0) or 0.0)

        if status == "draft":
            draft_count += 1
            total_pending_amount += amount
        elif run.get("approval_can_execute") is True or status == "approved":
            approved_count += 1
            total_pending_amount += amount
        elif status in ("executed", "posted"):
            executed_count += 1

    return PaymentRunCockpitReadModel(
        tenant_id=tenant_id,
        draft_count=draft_count,
        approved_count=approved_count,
        executed_count=executed_count,
        total_pending_amount=total_pending_amount,
        schema_version=1,
    )


def default_process_observation_instances() -> list[WorkflowInstanceSummary]:
    return [
        WorkflowInstanceSummary(
            process_key=process_key,
            running_count=0,
            waiting_count=0,
            completed_today=0,
            failed_count=0,
        )
        for process_key in ("ap_approval", "payment_run", "closing_checklist", "vat_return")
    ]


def project_process_observation(
    tenant_id: str,
    workflow_instances: list[WorkflowInstanceSummary],
    sla_profiles: list[WorkflowSlaProfile],
    overdue_instances: int = 0,
) -> ProcessObservationReadModel:
    return ProcessObservationReadModel(
        tenant_id=tenant_id,
        workflow_instances=workflow_instances,
        sla_profiles=sla_profiles,
        total_running=sum(instance.running_count for instance in workflow_instances),
        total_waiting=sum(instance.waiting_count for instance in workflow_instances),
        overdue_instances=overdue_instances,
        schema_version=1,
    )


def _fetch_cash_closing_rows(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    try:
        return (
            db.execute(
                text(
                    """
                    SELECT id, periode, status, verantwortlicher, abschluss_datum, items, created_at
                    FROM abschluss_checklisten
                    WHERE tenant_id = :tenant_id AND abschluss_art = 'kasse'
                    ORDER BY abschluss_datum DESC NULLS LAST, created_at DESC NULLS LAST
                    """
                ),
                {"tenant_id": tenant_id},
            )
            .mappings()
            .all()
        )
    except Exception:
        return []


def _fetch_cash_movement_count(db: Session, tenant_id: str) -> int:
    try:
        return int(
            db.execute(
                text("SELECT COUNT(*) FROM domain_erp.cash_movements WHERE tenant_id = :tenant_id"),
                {"tenant_id": tenant_id},
            ).scalar()
            or 0
        )
    except Exception:
        return 0


def _fetch_journal_entry_for_closing(db: Session, tenant_id: str, belegnummer: str | None) -> dict[str, Any] | None:
    if not belegnummer:
        return None
    try:
        return (
            db.execute(
                text(
                    """
                    SELECT id, entry_number, posting_date, status
                    FROM domain_erp.journal_entries
                    WHERE tenant_id = :tenant_id
                      AND (entry_number = :belegnummer OR reference = :belegnummer)
                    ORDER BY created_at DESC NULLS LAST
                    LIMIT 1
                    """
                ),
                {"tenant_id": tenant_id, "belegnummer": belegnummer},
            )
            .mappings()
            .fetchone()
        )
    except Exception:
        return None


def project_cash_closing_snapshot(
    row: dict[str, Any],
    tenant_cash_movement_count: int,
    journal_row: dict[str, Any] | None,
) -> CashClosingSnapshot:
    raw_items = _parse_items_blob(row.get("items"))
    closing_date = _iso_date(row.get("abschluss_datum") or row.get("periode"))

    totals = CashClosingTotals(
        cash_expected=_as_float(raw_items.get("umsatz_bar")),
        cash_counted=_as_float(raw_items.get("bargeld_gezaehlt")),
        cash_difference=_as_float(raw_items.get("differenz_bar")),
        card_expected=_as_float(raw_items.get("umsatz_ec")),
        card_counted=_as_float(raw_items.get("ec_abrechnung")),
        card_difference=_as_float(raw_items.get("ec_abrechnung")) - _as_float(raw_items.get("umsatz_ec")),
        paypal_expected=_as_float(raw_items.get("umsatz_paypal")),
        paypal_counted=_as_float(raw_items.get("paypal_abrechnung")),
        paypal_difference=_as_float(raw_items.get("paypal_abrechnung")) - _as_float(raw_items.get("umsatz_paypal")),
        b2b_expected=_as_float(raw_items.get("umsatz_b2b")),
        gross_total=_as_float(raw_items.get("umsatz_gesamt")),
    )

    has_missing_posting = totals.gross_total > 0 and journal_row is None
    has_difference = any(
        abs(value) >= 0.01
        for value in (totals.cash_difference, totals.card_difference, totals.paypal_difference)
    )
    workflow_status = _map_cash_workflow_status(
        str(row.get("status") or ""),
        has_posting=journal_row is not None,
        has_missing_posting=has_missing_posting,
    )

    source_document_refs = [f"abschluss_checklisten:{row['id']}"]
    if closing_date:
        source_document_refs.append(f"tse-journal:{closing_date}")
    if journal_row and journal_row.get("id"):
        source_document_refs.append(f"journal_entries:{journal_row['id']}")

    return CashClosingSnapshot(
        id=str(row["id"]),
        closing_date=closing_date,
        operator_name=row.get("verantwortlicher"),
        source="POS",
        workflow_status=workflow_status,
        totals=totals,
        posting=CashClosingPosting(
            journal_entry_id=str(journal_row["id"]) if journal_row and journal_row.get("id") is not None else None,
            journal_entry_number=journal_row.get("entry_number") if journal_row else None,
            posted_at=_iso_datetime(journal_row.get("posting_date")) if journal_row else None,
            posting_status=journal_row.get("status") if journal_row else None,
        ),
        import_context=CashClosingImportContext(
            import_batch_id=None,
            import_source_label="cash_movements" if tenant_cash_movement_count > 0 else None,
            imported_at=None,
        ),
        reference_context=CashClosingReferenceContext(
            tse_transaction_count=int(raw_items.get("tse_transaktionen") or 0),
            source_document_refs=source_document_refs,
        ),
        exception_flags=CashClosingExceptionFlags(
            has_difference=has_difference,
            has_import_gap=False,
            has_missing_posting=has_missing_posting,
        ),
    )


def project_cash_closing_read_model(
    tenant_id: str,
    closing_rows: list[dict[str, Any]],
    tenant_cash_movement_count: int,
    journal_resolver: Callable[[dict[str, Any]], dict[str, Any] | None],
) -> CashClosingReadModel:
    items = [
        project_cash_closing_snapshot(
            row=row,
            tenant_cash_movement_count=tenant_cash_movement_count,
            journal_row=journal_resolver(row),
        )
        for row in closing_rows
    ]
    return CashClosingReadModel(
        tenant_id=tenant_id,
        items=items,
        total_count=len(items),
        schema_version=1,
    )


def project_cash_closing_analysis(snapshot: CashClosingReadModel) -> CashClosingAnalysisReadModel:
    items = snapshot.items
    exception_items = [
        item for item in items
        if item.exception_flags.has_difference
        or item.exception_flags.has_missing_posting
        or item.exception_flags.has_import_gap
    ]

    operator_counts: dict[str, int] = {}
    date_counts: dict[str, int] = {}
    for item in exception_items:
        operator_key = item.operator_name or "Unbekannt"
        operator_counts[operator_key] = operator_counts.get(operator_key, 0) + 1

        date_key = item.closing_date or "ohne-datum"
        date_counts[date_key] = date_counts.get(date_key, 0) + 1

    top_exception_operators = [
        CashClosingAnalysisBucket(key=key, count=count)
        for key, count in sorted(operator_counts.items(), key=lambda pair: (-pair[1], pair[0]))[:3]
    ]
    top_exception_dates = [
        CashClosingAnalysisBucket(key=key, count=count)
        for key, count in sorted(date_counts.items(), key=lambda pair: (-pair[1], pair[0]))[:3]
    ]

    return CashClosingAnalysisReadModel(
        tenant_id=snapshot.tenant_id,
        total_count=snapshot.total_count,
        exception_count=sum(1 for item in items if item.workflow_status == "exception"),
        balanced_count=sum(1 for item in items if not item.exception_flags.has_difference),
        missing_posting_count=sum(1 for item in items if item.exception_flags.has_missing_posting),
        difference_count=sum(1 for item in items if item.exception_flags.has_difference),
        import_context_count=sum(1 for item in items if item.import_context.import_source_label is not None),
        top_exception_operators=top_exception_operators,
        top_exception_dates=top_exception_dates,
        schema_version=1,
    )


def project_cash_closing_reporting(snapshot: CashClosingReadModel) -> CashClosingReportingReadModel:
    period_map: dict[str, CashClosingReportingBucket] = {}

    for item in snapshot.items:
        period_key = _reporting_period_key(item.closing_date)
        bucket = period_map.setdefault(
            period_key,
            CashClosingReportingBucket(period_key=period_key, closing_count=0),
        )
        bucket.closing_count += 1
        bucket.gross_total += item.totals.gross_total
        bucket.difference_total += abs(item.totals.cash_difference) + abs(item.totals.card_difference) + abs(item.totals.paypal_difference)
        if (
            item.exception_flags.has_difference
            or item.exception_flags.has_missing_posting
            or item.exception_flags.has_import_gap
        ):
            bucket.exception_count += 1
        if item.exception_flags.has_missing_posting:
            bucket.missing_posting_count += 1

    periods = sorted(period_map.values(), key=lambda bucket: bucket.period_key, reverse=True)
    return CashClosingReportingReadModel(
        tenant_id=snapshot.tenant_id,
        periods=periods,
        total_count=snapshot.total_count,
        total_gross=sum(item.totals.gross_total for item in snapshot.items),
        total_difference=sum(
            abs(item.totals.cash_difference) + abs(item.totals.card_difference) + abs(item.totals.paypal_difference)
            for item in snapshot.items
        ),
        schema_version=1,
    )


def project_cash_closing_detail(snapshot: CashClosingReadModel, closing_id: str) -> CashClosingSnapshot | None:
    for item in snapshot.items:
        if item.id == closing_id:
            return item
    return None


def rebuild_finance_projection_store(tenant_id: str, db: Session | None) -> ProjectionRebuildResult:
    rebuilt_at = datetime.now(tz=timezone.utc).isoformat()
    latest_ap_invoice_event_id = _latest_outbox_event_id(
        db,
        tenant_id=tenant_id,
        event_types=[
            "APInvoiceApprovalRequested",
            "APInvoiceApprovalGranted",
            "APInvoiceApproved",
            "APInvoiceRejected",
            "APInvoicePosted",
        ],
    )
    latest_payment_run_event_id = _latest_outbox_event_id(
        db,
        tenant_id=tenant_id,
        event_types=[
            "payment_run.created",
            "payment_run.approved",
            "payment_run.executed",
            "payment_run.returned",
        ],
    )
    latest_cash_closing_event_id = _latest_outbox_event_id(
        db,
        tenant_id=tenant_id,
        event_types=[
            "cash_closing.posted",
        ],
    )
    latest_workflow_event_id = _latest_workflow_event_id(db)
    entries: list[ProjectionRebuildEntry] = []
    _projection_meta(tenant_id)["last_rebuilt_at"] = rebuilt_at

    ap_store = _get_ap_invoice_store()
    tenant_invoices = list(ap_store.get(tenant_id, {}).values()) if ap_store and tenant_id in ap_store else []
    ap_projection = _cache_projection(
        tenant_id,
        "ap-invoice-cockpit",
        project_ap_invoice_cockpit(tenant_id=tenant_id, tenant_invoices=tenant_invoices),
    )
    ap_count = _count_projection_items(ap_projection)
    _persist_projection_registry_entry(db, tenant_id, "ap-invoice-cockpit", ap_count, rebuilt_at=rebuilt_at)
    _persist_projection_snapshot(db, tenant_id, "ap-invoice-cockpit", ap_projection, rebuilt_at=rebuilt_at)
    persist_projection_cursor(
        db,
        tenant_id,
        _DEFAULT_PROJECTION_CONSUMER_ID,
        "ap-invoice-cockpit",
        cursor_token=rebuilt_at,
        last_event_id=latest_ap_invoice_event_id,
        source_rebuilt_at=rebuilt_at,
        status="ready",
    )
    entries.append(ProjectionRebuildEntry(projection_key="ap-invoice-cockpit", item_count=ap_count))

    payment_store = _get_payment_run_store()
    tenant_runs = list(payment_store.get(tenant_id, {}).values()) if payment_store and tenant_id in payment_store else []
    payment_projection = _cache_projection(
        tenant_id,
        "payment-run-cockpit",
        project_payment_run_cockpit(tenant_id=tenant_id, tenant_runs=tenant_runs),
    )
    payment_count = _count_projection_items(payment_projection)
    _persist_projection_registry_entry(db, tenant_id, "payment-run-cockpit", payment_count, rebuilt_at=rebuilt_at)
    _persist_projection_snapshot(db, tenant_id, "payment-run-cockpit", payment_projection, rebuilt_at=rebuilt_at)
    persist_projection_cursor(
        db,
        tenant_id,
        _DEFAULT_PROJECTION_CONSUMER_ID,
        "payment-run-cockpit",
        cursor_token=rebuilt_at,
        last_event_id=latest_payment_run_event_id,
        source_rebuilt_at=rebuilt_at,
        status="ready",
    )
    entries.append(ProjectionRebuildEntry(projection_key="payment-run-cockpit", item_count=payment_count))

    process_projection = _cache_projection(
        tenant_id,
        "process-observation",
        project_process_observation(
            tenant_id=tenant_id,
            workflow_instances=default_process_observation_instances(),
            sla_profiles=_build_sla_profiles(tenant_id=tenant_id, db=db),
            overdue_instances=0,
        ),
    )
    process_count = _count_projection_items(process_projection)
    _persist_projection_registry_entry(db, tenant_id, "process-observation", process_count, rebuilt_at=rebuilt_at)
    _persist_projection_snapshot(db, tenant_id, "process-observation", process_projection, rebuilt_at=rebuilt_at)
    persist_projection_cursor(
        db,
        tenant_id,
        _DEFAULT_PROJECTION_CONSUMER_ID,
        "process-observation",
        cursor_token=rebuilt_at,
        last_event_id=latest_workflow_event_id,
        source_rebuilt_at=rebuilt_at,
        status="ready",
    )
    entries.append(ProjectionRebuildEntry(projection_key="process-observation", item_count=process_count))

    closing_rows = _fetch_cash_closing_rows(db=db, tenant_id=tenant_id) if db is not None else []
    tenant_cash_movement_count = _fetch_cash_movement_count(db=db, tenant_id=tenant_id) if db is not None else 0
    snapshot = _cache_projection(
        tenant_id,
        "cash-closings",
        project_cash_closing_read_model(
            tenant_id=tenant_id,
            closing_rows=closing_rows,
            tenant_cash_movement_count=tenant_cash_movement_count,
            journal_resolver=lambda row: _fetch_journal_entry_for_closing(
                db=db,
                tenant_id=tenant_id,
                belegnummer=_parse_items_blob(row.get("items")).get("belegnummer"),
            ) if db is not None else None,
        ),
    )
    snapshot_count = _count_projection_items(snapshot)
    _persist_projection_registry_entry(db, tenant_id, "cash-closings", snapshot_count, rebuilt_at=rebuilt_at)
    _persist_projection_snapshot(db, tenant_id, "cash-closings", snapshot, rebuilt_at=rebuilt_at)
    persist_projection_cursor(
        db,
        tenant_id,
        _DEFAULT_PROJECTION_CONSUMER_ID,
        "cash-closings",
        cursor_token=rebuilt_at,
        last_event_id=latest_cash_closing_event_id,
        source_rebuilt_at=rebuilt_at,
        status="ready",
    )
    entries.append(ProjectionRebuildEntry(projection_key="cash-closings", item_count=snapshot_count))

    analysis = _cache_projection(
        tenant_id,
        "cash-closings/analysis",
        project_cash_closing_analysis(snapshot),
    )
    analysis_count = _count_projection_items(analysis)
    _persist_projection_registry_entry(db, tenant_id, "cash-closings/analysis", analysis_count, rebuilt_at=rebuilt_at)
    _persist_projection_snapshot(db, tenant_id, "cash-closings/analysis", analysis, rebuilt_at=rebuilt_at)
    persist_projection_cursor(
        db,
        tenant_id,
        _DEFAULT_PROJECTION_CONSUMER_ID,
        "cash-closings/analysis",
        cursor_token=rebuilt_at,
        last_event_id=latest_cash_closing_event_id,
        source_rebuilt_at=rebuilt_at,
        status="ready",
    )
    entries.append(ProjectionRebuildEntry(projection_key="cash-closings/analysis", item_count=analysis_count))

    reporting = _cache_projection(
        tenant_id,
        "cash-closings/reporting",
        project_cash_closing_reporting(snapshot),
    )
    reporting_count = _count_projection_items(reporting)
    _persist_projection_registry_entry(db, tenant_id, "cash-closings/reporting", reporting_count, rebuilt_at=rebuilt_at)
    _persist_projection_snapshot(db, tenant_id, "cash-closings/reporting", reporting, rebuilt_at=rebuilt_at)
    persist_projection_cursor(
        db,
        tenant_id,
        _DEFAULT_PROJECTION_CONSUMER_ID,
        "cash-closings/reporting",
        cursor_token=rebuilt_at,
        last_event_id=latest_cash_closing_event_id,
        source_rebuilt_at=rebuilt_at,
        status="ready",
    )
    entries.append(ProjectionRebuildEntry(projection_key="cash-closings/reporting", item_count=reporting_count))

    detail_count = 0
    for item in snapshot.items:
        _cache_projection(tenant_id, f"cash-closings/detail/{item.id}", item)
        detail_count += 1
    _persist_projection_registry_entry(db, tenant_id, "cash-closings/detail", detail_count, rebuilt_at=rebuilt_at)
    persist_projection_cursor(
        db,
        tenant_id,
        _DEFAULT_PROJECTION_CONSUMER_ID,
        "cash-closings/detail",
        cursor_token=rebuilt_at,
        last_event_id=latest_cash_closing_event_id,
        source_rebuilt_at=rebuilt_at,
        status="ready",
    )
    entries.append(ProjectionRebuildEntry(projection_key="cash-closings/detail", item_count=detail_count))

    return ProjectionRebuildResult(
        tenant_id=tenant_id,
        rebuilt_at=rebuilt_at,
        projections=entries,
        schema_version=1,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/ap-invoice-cockpit", response_model=APInvoiceCockpitReadModel)
async def get_ap_invoice_cockpit(
    tenant_id: str = Depends(get_tenant_id),
) -> APInvoiceCockpitReadModel:
    """
    Pre-aggregated AP-invoice cockpit KPIs for the finance dashboard.
    Schema v1 — stable contract.
    """
    # Attempt to read from the existing in-memory AP-invoice store
    store = _get_ap_invoice_store()
    tenant_invoices: list[dict[str, Any]] = []
    if store is not None and tenant_id in store:
        tenant_invoices = list(store[tenant_id].values())

    return _cache_projection(
        tenant_id,
        "ap-invoice-cockpit",
        project_ap_invoice_cockpit(tenant_id=tenant_id, tenant_invoices=tenant_invoices),
    )


@router.get("/payment-run-cockpit", response_model=PaymentRunCockpitReadModel)
async def get_payment_run_cockpit(
    tenant_id: str = Depends(get_tenant_id),
) -> PaymentRunCockpitReadModel:
    """
    Pre-aggregated payment-run cockpit KPIs for the finance dashboard.
    Schema v1 — stable contract.
    """
    store = _get_payment_run_store()
    tenant_runs: list[dict[str, Any]] = []
    if store is not None and tenant_id in store:
        tenant_runs = list(store[tenant_id].values())

    return _cache_projection(
        tenant_id,
        "payment-run-cockpit",
        project_payment_run_cockpit(tenant_id=tenant_id, tenant_runs=tenant_runs),
    )


@router.get("/process-observation", response_model=ProcessObservationReadModel)
async def get_process_observation(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> ProcessObservationReadModel:
    """
    Cross-domain observation of active workflow instances.
    Schema v1 — stable contract.
    No DB model backing yet; returns the canonical default shape for the
    known process keys so consumers can rely on the schema contract.
    """
    return _cache_projection(
        tenant_id,
        "process-observation",
        project_process_observation(
            tenant_id=tenant_id,
            workflow_instances=default_process_observation_instances(),
            sla_profiles=_build_sla_profiles(tenant_id=tenant_id, db=db),
            overdue_instances=0,
        ),
    )


@router.get("/cash-closings", response_model=CashClosingReadModel)
async def get_cash_closings(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CashClosingReadModel:
    """
    Finance-facing read model over productive POS cash closings.
    Schema v1 — read-only snapshot for reconciliation and reporting.
    """
    closing_rows = _fetch_cash_closing_rows(db=db, tenant_id=tenant_id)
    tenant_cash_movement_count = _fetch_cash_movement_count(db=db, tenant_id=tenant_id)
    return _cache_projection(
        tenant_id,
        "cash-closings",
        project_cash_closing_read_model(
            tenant_id=tenant_id,
            closing_rows=closing_rows,
            tenant_cash_movement_count=tenant_cash_movement_count,
            journal_resolver=lambda row: _fetch_journal_entry_for_closing(
                db=db,
                tenant_id=tenant_id,
                belegnummer=_parse_items_blob(row.get("items")).get("belegnummer"),
            ),
        ),
    )


@router.get("/cash-closings/analysis", response_model=CashClosingAnalysisReadModel)
async def get_cash_closing_analysis(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CashClosingAnalysisReadModel:
    snapshot = await get_cash_closings(tenant_id=tenant_id, db=db)
    return _cache_projection(
        tenant_id,
        "cash-closings/analysis",
        project_cash_closing_analysis(snapshot),
    )


@router.get("/cash-closings/reporting", response_model=CashClosingReportingReadModel)
async def get_cash_closing_reporting(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CashClosingReportingReadModel:
    snapshot = await get_cash_closings(tenant_id=tenant_id, db=db)
    return _cache_projection(
        tenant_id,
        "cash-closings/reporting",
        project_cash_closing_reporting(snapshot),
    )


@router.post("/_rebuild", response_model=ProjectionRebuildResult)
async def rebuild_finance_read_model_projections(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> ProjectionRebuildResult:
    return rebuild_finance_projection_store(tenant_id=tenant_id, db=db)


@router.get("/_status", response_model=ProjectionStatusReadModel)
async def get_finance_read_model_projection_status(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> ProjectionStatusReadModel:
    return get_projection_status(tenant_id=tenant_id, db=db)


@router.get("/cash-closings/{closing_id}", response_model=CashClosingSnapshot)
async def get_cash_closing_detail(
    closing_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CashClosingSnapshot:
    cached = _load_projection(tenant_id, f"cash-closings/detail/{closing_id}", CashClosingSnapshot)
    if cached is not None:
        _persist_projection_registry_entry(
            db,
            tenant_id,
            f"cash-closings/detail/{closing_id}",
            1,
            accessed_at=datetime.now(tz=timezone.utc).isoformat(),
        )
        return cached
    snapshot = await get_cash_closings(tenant_id=tenant_id, db=db)
    item = project_cash_closing_detail(snapshot=snapshot, closing_id=closing_id)
    if item is not None:
        _persist_projection_registry_entry(
            db,
            tenant_id,
            f"cash-closings/detail/{closing_id}",
            1,
            accessed_at=datetime.now(tz=timezone.utc).isoformat(),
        )
        return _cache_projection(tenant_id, f"cash-closings/detail/{closing_id}", item)
    raise HTTPException(status_code=404, detail="Cash closing not found")


# ---------------------------------------------------------------------------
# Wave 19 AP2: Settlement-Cockpit + Position-Exposure Read-Models
# ---------------------------------------------------------------------------

from ....core.finance_read_model_contracts import (  # noqa: E402
    PositionExposureSnapshot,
    SettlementCockpitSnapshot,
)


@router.get("/settlement-cockpit", response_model=dict)
async def get_settlement_cockpit(
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """
    Settlement-Cockpit Read-Model (schema_version=1).

    Liefert Abrechnungsstatus-Übersicht aller offenen Abrechnungen eines Mandanten.
    Stabiler Contract: schema_version wird nie ohne Wave-Beschluss geaendert.
    """
    snapshot = SettlementCockpitSnapshot(tenant_id=tenant_id)
    return snapshot.as_dict()


@router.get("/position-exposure", response_model=dict)
async def get_position_exposure(
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """
    Position-Exposure Read-Model (schema_version=1).

    Liefert Risikoexposure aller offenen Positionen (Kontrakt, Lager, Rechnung, Abrechnung)
    eines Mandanten. Stabiler Contract: schema_version wird nie ohne Wave-Beschluss geaendert.
    """
    snapshot = PositionExposureSnapshot(tenant_id=tenant_id)
    return snapshot.as_dict()
