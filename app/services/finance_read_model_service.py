"""Service layer for Finance Read-Models (cockpit KPI projections).

Contains all projection, caching, persistence, and aggregation logic
that was previously inline in the finance_read_models endpoint file.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from typing import Any, Callable

from pydantic import BaseModel
from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.api.v1.schemas.finance_read_models_schemas import (
    APInvoiceBucket,
    APInvoiceCockpitReadModel,
    CashClosingAnalysisBucket,
    CashClosingAnalysisReadModel,
    CashClosingExceptionFlags,
    CashClosingImportContext,
    CashClosingPosting,
    CashClosingReadModel,
    CashClosingReferenceContext,
    CashClosingReportingBucket,
    CashClosingReportingReadModel,
    CashClosingSnapshot,
    CashClosingTotals,
    PaymentRunCockpitReadModel,
    ProcessObservationReadModel,
    ProjectionRebuildEntry,
    ProjectionRebuildResult,
    ProjectionStatusEntry,
    ProjectionStatusReadModel,
    WorkflowInstanceSummary,
    WorkflowSlaProfile,
    WorkflowStepSlaSummary,
)

# ── In-memory projection store ─────────────────────────────────────────────────

_PROJECTION_STORE: dict[str, dict[str, dict[str, Any]]] = {}
_PROJECTION_META: dict[str, dict[str, Any]] = {}
_DEFAULT_PROJECTION_CONSUMER_ID = "finance-projections-01"


# ── Store accessors (loaded from endpoint gateways) ────────────────────────────

def _get_ap_invoice_store() -> dict[str, Any] | None:
    from app.core.endpoint_gateways import get_ap_invoice_store_loader
    loader = get_ap_invoice_store_loader()
    return loader() if loader else None


def _get_payment_run_store() -> dict[str, Any] | None:
    from app.core.endpoint_gateways import get_payment_run_store_loader
    loader = get_payment_run_store_loader()
    return loader() if loader else None


# ── Pure value helpers ─────────────────────────────────────────────────────────

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


# ── Projection cache helpers ───────────────────────────────────────────────────

def _projection_bucket(tenant_id: str) -> dict[str, dict[str, Any]]:
    return _PROJECTION_STORE.setdefault(tenant_id, {})


def _projection_meta(tenant_id: str) -> dict[str, Any]:
    return _PROJECTION_META.setdefault(
        tenant_id,
        {"last_rebuilt_at": None, "cache_hits": 0, "cache_misses": 0},
    )


def cache_projection(tenant_id: str, projection_key: str, payload: BaseModel) -> BaseModel:
    _projection_bucket(tenant_id)[projection_key] = payload.model_dump(mode="json")
    return payload


def load_projection(tenant_id: str, projection_key: str, model_type: type[BaseModel]) -> BaseModel | None:
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


# ── DB table bootstrap helpers ─────────────────────────────────────────────────

def _ensure_projection_registry_table(db: Session) -> None:
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS domain_shared.process_projection_registry (
                tenant_id TEXT NOT NULL,
                projection_key TEXT NOT NULL,
                item_count INTEGER NOT NULL DEFAULT 0,
                last_rebuilt_at TEXT NULL,
                last_accessed_at TEXT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (tenant_id, projection_key)
            )
        """))
        db.commit()
    except Exception:
        db.rollback()
        raise


def _ensure_projection_snapshot_table(db: Session) -> None:
    try:
        db.execute(text("""
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
        """))
        db.commit()
    except Exception:
        db.rollback()
        raise


def _ensure_projection_cursor_table(db: Session) -> None:
    try:
        db.execute(text("""
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
        """))
        db.commit()
    except Exception:
        db.rollback()
        raise


# ── DB persistence helpers ─────────────────────────────────────────────────────

def persist_projection_registry_entry(
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
            text("""
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
            """),
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
        except Exception:  # noqa: BLE001
            pass


def persist_projection_snapshot(
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
            text("""
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
            """),
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
        except Exception:  # noqa: BLE001
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
            text("""
                INSERT INTO domain_shared.process_projection_cursors (
                    tenant_id, consumer_id, projection_key, schema_version,
                    cursor_token, last_event_id, source_rebuilt_at,
                    replay_from_event_id, replay_to_event_id, status, updated_at
                ) VALUES (
                    :tenant_id, :consumer_id, :projection_key, :schema_version,
                    :cursor_token, :last_event_id, :source_rebuilt_at,
                    :replay_from_event_id, :replay_to_event_id, :status, :updated_at
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
            """),
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
        except Exception:  # noqa: BLE001
            pass


# ── DB read helpers ────────────────────────────────────────────────────────────

def _load_persisted_projection_registry(
    db: Session | None,
    tenant_id: str,
) -> tuple[dict[str, ProjectionStatusEntry], str | None]:
    if db is None:
        return {}, None
    try:
        _ensure_projection_registry_table(db)
        rows = db.execute(
            text("""
                SELECT projection_key, item_count, last_rebuilt_at
                FROM domain_shared.process_projection_registry
                WHERE tenant_id = :tenant_id
                ORDER BY projection_key
            """),
            {"tenant_id": tenant_id},
        ).mappings().all()
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
        rows = db.execute(
            text("""
                SELECT projection_key, rebuilt_at
                FROM domain_shared.process_projection_snapshots
                WHERE tenant_id = :tenant_id
                ORDER BY projection_key
            """),
            {"tenant_id": tenant_id},
        ).mappings().all()
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
    if projection_key in ("ap-invoice-cockpit", "payment-run-cockpit"):
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
            SELECT consumer_id, projection_key, status, updated_at, last_event_id,
                   replay_from_event_id, replay_to_event_id
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


def _latest_workflow_event_id(db: Session | None) -> str | None:
    if db is None:
        return None
    try:
        # reviewed-safe: generated clauses contain only fixed parameter names; values are bound.
        row = db.execute(
            text("""
                SELECT domain, doc_number, ts
                FROM workflow_audit
                ORDER BY ts DESC
                LIMIT 1
            """)
        ).mappings().first()
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
        # reviewed-safe: clauses contain fixed parameter names only; event values are bound.
        row = db.execute(
            text(f"""
                SELECT id, event_type, timestamp
                FROM outbox_events
                WHERE tenant_id = :tenant_id
                  AND ({' OR '.join(conditions)})
                ORDER BY timestamp DESC
                LIMIT 1
            """),
            params,
        ).mappings().first()
    except Exception:
        return None
    if not row or not row.get("id"):
        return None
    return str(row.get("id"))


# ── Projection status ──────────────────────────────────────────────────────────

def get_projection_status(tenant_id: str, db: Session | None = None) -> ProjectionStatusReadModel:
    bucket = _projection_bucket(tenant_id)
    meta = _projection_meta(tenant_id)
    persisted_entries, persisted_last_rebuilt_at = _load_persisted_projection_registry(db=db, tenant_id=tenant_id)
    persisted_snapshot_count, persisted_last_snapshot_at = _load_persisted_projection_snapshot_meta(db=db, tenant_id=tenant_id)
    persisted_cursor_count, persisted_last_cursor_advanced_at, persisted_last_processed_event_id = (
        _load_persisted_projection_cursor_meta(db=db, tenant_id=tenant_id, consumer_id=_DEFAULT_PROJECTION_CONSUMER_ID)
    )
    persisted_cursor_entries = _load_persisted_projection_cursor_entries(
        db=db, tenant_id=tenant_id, consumer_id=_DEFAULT_PROJECTION_CONSUMER_ID
    )

    in_memory_entries = {
        k: ProjectionStatusEntry(
            projection_key=k,
            item_count=_count_projection_payload_items(v),
            cached=True,
        )
        for k, v in sorted(bucket.items())
    }
    merged = {**persisted_entries}
    for key, cursor_entry in persisted_cursor_entries.items():
        base = merged.get(key, ProjectionStatusEntry(projection_key=key, item_count=0, cached=False))
        merged[key] = ProjectionStatusEntry(
            projection_key=key,
            item_count=base.item_count,
            cached=cursor_entry.cached,
            cursor_status=cursor_entry.cursor_status,
            cursor_source=cursor_entry.cursor_source,
            cursor_updated_at=cursor_entry.cursor_updated_at,
            last_processed_event_id=cursor_entry.last_processed_event_id,
        )
    for key, mem_entry in in_memory_entries.items():
        base = merged.get(key, ProjectionStatusEntry(projection_key=key, item_count=0, cached=False))
        merged[key] = ProjectionStatusEntry(
            projection_key=key,
            item_count=mem_entry.item_count,
            cached=True,
            cursor_status=base.cursor_status,
            cursor_source=base.cursor_source,
            cursor_updated_at=base.cursor_updated_at,
            last_processed_event_id=base.last_processed_event_id,
        )

    projections = sorted(merged.values(), key=lambda e: e.projection_key)
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


# ── SLA profiles ───────────────────────────────────────────────────────────────

def build_sla_profiles(tenant_id: str, db: Session | None) -> list[WorkflowSlaProfile]:
    from app.core.process_config import DEFAULT_PROCESS_VARIANTS
    from app.core.workflow_definitions import merge_workflow_variants

    custom_variants: object = None
    if db is not None:
        try:
            settings_row = db.execute(
                text("SELECT settings FROM domain_shared.tenants WHERE id = :tenant_id"),
                {"tenant_id": tenant_id},
            ).first()
            if settings_row and settings_row[0]:
                raw = settings_row[0]
                if isinstance(raw, dict):
                    custom_variants = raw.get("process_variants")
                elif isinstance(raw, str):
                    parsed = json.loads(raw)
                    if isinstance(parsed, dict):
                        custom_variants = parsed.get("process_variants")
        except Exception:
            custom_variants = None

    merged_variants = merge_workflow_variants(DEFAULT_PROCESS_VARIANTS, custom_variants, tenant_id=tenant_id)

    profiles: list[WorkflowSlaProfile] = []
    for process_key, definition in sorted(merged_variants.items()):
        sla_defs = definition.get("step_sla") or {}
        step_sla = [
            WorkflowStepSlaSummary(
                step_key=step_key,
                timeout_hours=sla.get("timeout_hours") or 0,
                escalation_roles=list(sla.get("escalation_roles") or []),
            )
            for step_key, sla in sorted(sla_defs.items())
            if isinstance(sla, dict)
        ]
        profiles.append(WorkflowSlaProfile(
            process_key=process_key,
            escalatable_steps=sum(1 for s in step_sla if s.timeout_hours and s.timeout_hours > 0),
            step_sla=step_sla,
        ))
    return profiles


# ── AP-Invoice projection ──────────────────────────────────────────────────────

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
                    created_dt = datetime.fromisoformat(created_raw) if isinstance(created_raw, str) else created_raw
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
        total_count=sum(b.count for b in buckets),
        pending_approval_count=pending_approval_count,
        ready_to_post_count=ready_to_post_count,
        overdue_count=overdue_count,
        schema_version=1,
    )


# ── Payment-Run projection ─────────────────────────────────────────────────────

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


# ── Process Observation projection ─────────────────────────────────────────────

def default_process_observation_instances() -> list[WorkflowInstanceSummary]:
    return [
        WorkflowInstanceSummary(process_key=key, running_count=0, waiting_count=0)
        for key in ("ap_approval", "payment_run", "closing_checklist", "vat_return")
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
        total_running=sum(i.running_count for i in workflow_instances),
        total_waiting=sum(i.waiting_count for i in workflow_instances),
        overdue_instances=overdue_instances,
        schema_version=1,
    )


# ── Cash Closing projection ────────────────────────────────────────────────────

def _fetch_cash_closing_rows(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    try:
        return db.execute(
            text("""
                SELECT id, periode, status, verantwortlicher, abschluss_datum, items, created_at
                FROM abschluss_checklisten
                WHERE tenant_id = :tenant_id AND abschluss_art = 'kasse'
                ORDER BY abschluss_datum DESC NULLS LAST, created_at DESC NULLS LAST
            """),
            {"tenant_id": tenant_id},
        ).mappings().all()
    except Exception:
        return []


def _fetch_cash_movement_count(db: Session, tenant_id: str) -> int:
    try:
        return int(
            db.execute(
                text("SELECT COUNT(*) FROM domain_erp.cash_movements WHERE tenant_id = :tenant_id"),
                {"tenant_id": tenant_id},
            ).scalar() or 0
        )
    except Exception:
        return 0


def _cash_closing_row_belegnummer(row: dict[str, Any]) -> str | None:
    raw = _parse_items_blob(row.get("items")).get("belegnummer")
    if raw is None:
        return None
    s = str(raw).strip()
    return s or None


def _batch_fetch_journal_entries_for_closings(
    db: Session,
    tenant_id: str,
    closing_rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    belege = sorted({b for b in (_cash_closing_row_belegnummer(r) for r in closing_rows) if b})
    if not belege:
        return {}
    try:
        stmt = text("""
            SELECT id, entry_number, posting_date, status, reference, created_at
            FROM domain_erp.journal_entries
            WHERE tenant_id = :tenant_id
              AND (entry_number IN :belege OR reference IN :belege)
            ORDER BY created_at DESC NULLS LAST
        """).bindparams(bindparam("belege", expanding=True))
        rows = db.execute(stmt, {"tenant_id": tenant_id, "belege": belege}).mappings().all() or []
    except Exception:
        return {}
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        rowd = dict(row)
        en = rowd.get("entry_number")
        ref = rowd.get("reference")
        for key in belege:
            if key not in by_key and (en == key or ref == key):
                by_key[key] = rowd
    return by_key


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
        abs(v) >= 0.01
        for v in (totals.cash_difference, totals.card_difference, totals.paypal_difference)
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
        project_cash_closing_snapshot(row=row, tenant_cash_movement_count=tenant_cash_movement_count, journal_row=journal_resolver(row))
        for row in closing_rows
    ]
    return CashClosingReadModel(tenant_id=tenant_id, items=items, total_count=len(items), schema_version=1)


def project_cash_closing_analysis(snapshot: CashClosingReadModel) -> CashClosingAnalysisReadModel:
    items = snapshot.items
    exception_items = [i for i in items if i.exception_flags.has_difference or i.exception_flags.has_missing_posting or i.exception_flags.has_import_gap]
    operator_counts: dict[str, int] = {}
    date_counts: dict[str, int] = {}
    for item in exception_items:
        op = item.operator_name or "Unbekannt"
        operator_counts[op] = operator_counts.get(op, 0) + 1
        d = item.closing_date or "ohne-datum"
        date_counts[d] = date_counts.get(d, 0) + 1

    return CashClosingAnalysisReadModel(
        tenant_id=snapshot.tenant_id,
        total_count=snapshot.total_count,
        exception_count=sum(1 for i in items if i.workflow_status == "exception"),
        balanced_count=sum(1 for i in items if not i.exception_flags.has_difference),
        missing_posting_count=sum(1 for i in items if i.exception_flags.has_missing_posting),
        difference_count=sum(1 for i in items if i.exception_flags.has_difference),
        import_context_count=sum(1 for i in items if i.import_context.import_source_label is not None),
        top_exception_operators=[CashClosingAnalysisBucket(key=k, count=c) for k, c in sorted(operator_counts.items(), key=lambda p: (-p[1], p[0]))[:3]],
        top_exception_dates=[CashClosingAnalysisBucket(key=k, count=c) for k, c in sorted(date_counts.items(), key=lambda p: (-p[1], p[0]))[:3]],
        schema_version=1,
    )


def project_cash_closing_reporting(snapshot: CashClosingReadModel) -> CashClosingReportingReadModel:
    period_map: dict[str, CashClosingReportingBucket] = {}
    for item in snapshot.items:
        key = _reporting_period_key(item.closing_date)
        bucket = period_map.setdefault(key, CashClosingReportingBucket(period_key=key, closing_count=0))
        bucket.closing_count += 1
        bucket.gross_total += item.totals.gross_total
        bucket.difference_total += abs(item.totals.cash_difference) + abs(item.totals.card_difference) + abs(item.totals.paypal_difference)
        if item.exception_flags.has_difference or item.exception_flags.has_missing_posting or item.exception_flags.has_import_gap:
            bucket.exception_count += 1
        if item.exception_flags.has_missing_posting:
            bucket.missing_posting_count += 1

    periods = sorted(period_map.values(), key=lambda b: b.period_key, reverse=True)
    return CashClosingReportingReadModel(
        tenant_id=snapshot.tenant_id,
        periods=periods,
        total_count=snapshot.total_count,
        total_gross=sum(i.totals.gross_total for i in snapshot.items),
        total_difference=sum(abs(i.totals.cash_difference) + abs(i.totals.card_difference) + abs(i.totals.paypal_difference) for i in snapshot.items),
        schema_version=1,
    )


def project_cash_closing_detail(snapshot: CashClosingReadModel, closing_id: str) -> CashClosingSnapshot | None:
    for item in snapshot.items:
        if item.id == closing_id:
            return item
    return None


def build_cash_closing_read_model(db: Session | None, tenant_id: str) -> CashClosingReadModel:
    if db is None:
        return project_cash_closing_read_model(
            tenant_id=tenant_id, closing_rows=[], tenant_cash_movement_count=0,
            journal_resolver=lambda _: None,
        )
    closing_rows = _fetch_cash_closing_rows(db=db, tenant_id=tenant_id)
    movement_count = _fetch_cash_movement_count(db=db, tenant_id=tenant_id)
    journal_by = _batch_fetch_journal_entries_for_closings(db, tenant_id, closing_rows)

    def _resolve(row: dict[str, Any]) -> dict[str, Any] | None:
        k = _cash_closing_row_belegnummer(row)
        return journal_by.get(k) if k else None

    return project_cash_closing_read_model(
        tenant_id=tenant_id, closing_rows=closing_rows,
        tenant_cash_movement_count=movement_count, journal_resolver=_resolve,
    )


# ── Rebuild ────────────────────────────────────────────────────────────────────

def rebuild_finance_projection_store(tenant_id: str, db: Session | None) -> ProjectionRebuildResult:
    rebuilt_at = datetime.now(tz=timezone.utc).isoformat()

    latest_ap_event = _latest_outbox_event_id(db, tenant_id=tenant_id, event_types=[
        "APInvoiceApprovalRequested", "APInvoiceApprovalGranted", "APInvoiceApproved",
        "APInvoiceRejected", "APInvoicePosted",
    ])
    latest_payment_event = _latest_outbox_event_id(db, tenant_id=tenant_id, event_types=[
        "payment_run.created", "payment_run.approved", "payment_run.executed", "payment_run.returned",
    ])
    latest_cash_event = _latest_outbox_event_id(db, tenant_id=tenant_id, event_types=["cash_closing.posted"])
    latest_workflow_event = _latest_workflow_event_id(db)

    entries: list[ProjectionRebuildEntry] = []
    _projection_meta(tenant_id)["last_rebuilt_at"] = rebuilt_at

    def _rebuild_projection(key: str, payload: BaseModel, event_id: str | None) -> None:
        cached = cache_projection(tenant_id, key, payload)
        count = _count_projection_items(cached)
        persist_projection_registry_entry(db, tenant_id, key, count, rebuilt_at=rebuilt_at)
        persist_projection_snapshot(db, tenant_id, key, cached, rebuilt_at=rebuilt_at)
        persist_projection_cursor(
            db, tenant_id, _DEFAULT_PROJECTION_CONSUMER_ID, key,
            cursor_token=rebuilt_at, last_event_id=event_id,
            source_rebuilt_at=rebuilt_at, status="ready",
        )
        entries.append(ProjectionRebuildEntry(projection_key=key, item_count=count))

    ap_store = _get_ap_invoice_store()
    tenant_invoices = list(ap_store.get(tenant_id, {}).values()) if ap_store and tenant_id in ap_store else []
    _rebuild_projection("ap-invoice-cockpit", project_ap_invoice_cockpit(tenant_id, tenant_invoices), latest_ap_event)

    payment_store = _get_payment_run_store()
    tenant_runs = list(payment_store.get(tenant_id, {}).values()) if payment_store and tenant_id in payment_store else []
    _rebuild_projection("payment-run-cockpit", project_payment_run_cockpit(tenant_id, tenant_runs), latest_payment_event)

    _rebuild_projection("process-observation", project_process_observation(
        tenant_id=tenant_id,
        workflow_instances=default_process_observation_instances(),
        sla_profiles=build_sla_profiles(tenant_id=tenant_id, db=db),
        overdue_instances=0,
    ), latest_workflow_event)

    snapshot = cache_projection(tenant_id, "cash-closings", build_cash_closing_read_model(db, tenant_id))
    snap_count = _count_projection_items(snapshot)
    persist_projection_registry_entry(db, tenant_id, "cash-closings", snap_count, rebuilt_at=rebuilt_at)
    persist_projection_snapshot(db, tenant_id, "cash-closings", snapshot, rebuilt_at=rebuilt_at)
    persist_projection_cursor(db, tenant_id, _DEFAULT_PROJECTION_CONSUMER_ID, "cash-closings",
                              cursor_token=rebuilt_at, last_event_id=latest_cash_event,
                              source_rebuilt_at=rebuilt_at, status="ready")
    entries.append(ProjectionRebuildEntry(projection_key="cash-closings", item_count=snap_count))

    _rebuild_projection("cash-closings/analysis", project_cash_closing_analysis(snapshot), latest_cash_event)
    _rebuild_projection("cash-closings/reporting", project_cash_closing_reporting(snapshot), latest_cash_event)

    detail_count = 0
    for item in snapshot.items:
        cache_projection(tenant_id, f"cash-closings/detail/{item.id}", item)
        detail_count += 1
    persist_projection_registry_entry(db, tenant_id, "cash-closings/detail", detail_count, rebuilt_at=rebuilt_at)
    persist_projection_cursor(db, tenant_id, _DEFAULT_PROJECTION_CONSUMER_ID, "cash-closings/detail",
                              cursor_token=rebuilt_at, last_event_id=latest_cash_event,
                              source_rebuilt_at=rebuilt_at, status="ready")
    entries.append(ProjectionRebuildEntry(projection_key="cash-closings/detail", item_count=detail_count))

    return ProjectionRebuildResult(tenant_id=tenant_id, rebuilt_at=rebuilt_at, projections=entries, schema_version=1)
