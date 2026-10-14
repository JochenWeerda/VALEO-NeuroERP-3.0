"""Studio drafts with tenant isolation, four-eyes publish, and optional Postgres."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from threading import RLock
from functools import wraps
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

_DRAFTS: dict[str, dict[str, Any]] = {}
_HISTORY: list[dict[str, Any]] = []
_memory_lock = RLock()
_prefer_memory = False
_table_ok: bool | None = None
_EDITABLE = frozenset({"draft", "review", "retired"})
_STATUSES = frozenset({"draft", "review", "published_temp", "retired"})


class StudioStorageUnavailable(RuntimeError):
    """Persistence failure; never substitute volatile state for durable drafts."""


def _durable_operation(operation):
    @wraps(operation)
    def guarded(*args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except SQLAlchemyError as error:
            raise StudioStorageUnavailable("studio_persistenz_nicht_verfuegbar") from error
    return guarded


def reset_studio_drafts() -> None:
    """Unit-Test-Reset: leert den Prozessspeicher und bleibt bewusst ohne Postgres."""
    global _prefer_memory
    _prefer_memory = True
    _DRAFTS.clear()
    _HISTORY.clear()


def use_sql_studio_drafts() -> None:
    """Schaltet Persistenz auf domain_shared.screen_definition_drafts."""
    global _prefer_memory, _table_ok
    _prefer_memory = False
    _table_ok = None
    _DRAFTS.clear()
    _HISTORY.clear()


def invalidate_studio_table_cache() -> None:
    global _table_ok
    _table_ok = None


def _with_revision(item: dict[str, Any]) -> dict[str, Any]:
    record = deepcopy(item)
    bound = {key: record.get(key) for key in (
        "id", "tenant_id", "definition", "updated_at", "updated_by", "status"
    )}
    record["revision"] = hashlib.sha256(json.dumps(
        bound, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()).hexdigest()
    return record


def _history_entry(record: dict[str, Any], actor: str, action: str, previous: str | None, key: str | None = None) -> dict[str, Any]:
    snapshot = _with_revision(record)
    return {"id": key or str(uuid4()), "tenant_id": record["tenant_id"], "draft_id": record["id"],
            "actor": actor, "action": action, "previous_revision": previous,
            "revision": snapshot["revision"], "snapshot": snapshot, "recorded_at": datetime.now(UTC)}


def _append_sql_history(session: Session, record: dict[str, Any], actor: str, action: str, previous: str | None, key: str | None = None) -> None:
    from app.infrastructure.models.studio_models import ScreenDefinitionHistory
    session.add(ScreenDefinitionHistory(**_history_entry(record, actor, action, previous, key)))


def _matching_replay(entry: dict[str, Any] | None, tenant: str, draft: str, actor: str, action: str, revision: str | None):
    if entry is None:
        return None
    if any(entry[field] != value for field, value in (
        ("tenant_id", tenant), ("draft_id", draft), ("actor", actor),
        ("action", action), ("previous_revision", revision),
    )):
        raise ValueError("idempotenzschluessel_anderer_auftrag")
    return deepcopy(entry["snapshot"])


def _sql_replay(session: Session, key: str, tenant: str, draft: str, actor: str, action: str, revision: str | None):
    from app.infrastructure.models.studio_models import ScreenDefinitionHistory
    row = session.get(ScreenDefinitionHistory, key)
    entry = {field: getattr(row, field) for field in (
        "tenant_id", "draft_id", "actor", "action", "previous_revision", "snapshot"
    )} if row is not None else None
    return _matching_replay(entry, tenant, draft, actor, action, revision)


def _matching_save_replay(entry, tenant, actor, draft, definition, revision):
    if entry is None:
        return None
    action = "update" if draft else "create"
    snapshot = _matching_replay(entry, tenant, draft or entry["draft_id"], actor, action, revision)
    encode = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if encode(snapshot["definition"]) != encode(definition):
        raise ValueError("idempotenzschluessel_anderer_inhalt")
    return snapshot


def _sql_save_replay(session, key, tenant, actor, draft, definition, revision):
    from app.infrastructure.models.studio_models import ScreenDefinitionHistory
    row = session.get(ScreenDefinitionHistory, key)
    entry = {field: getattr(row, field) for field in (
        "tenant_id", "draft_id", "actor", "action", "previous_revision", "snapshot"
    )} if row is not None else None
    return _matching_save_replay(entry, tenant, actor, draft, definition, revision)


@_durable_operation
def get_status_replay(tenant: str, draft: str, actor: str, action: str, revision: str, key: str):
    if _prefer_memory:
        with _memory_lock:
            entry = next((e for e in _HISTORY if e["id"] == key), None)
            return _matching_replay(entry, tenant, draft, actor, action, revision)
    session = _sql_session()
    try:
        return _sql_replay(session, key, tenant, draft, actor, action, revision)
    finally:
        session.close()


@_durable_operation
def list_history(tenant_id: str, draft_id: str, *, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    if _prefer_memory:
        with _memory_lock:
            return [deepcopy(entry) for entry in _HISTORY if entry["tenant_id"] == tenant_id and entry["draft_id"] == draft_id][skip:skip + limit]
    from app.infrastructure.models.studio_models import ScreenDefinitionHistory
    session = _sql_session()
    try:
        rows = session.query(ScreenDefinitionHistory).filter_by(tenant_id=tenant_id, draft_id=draft_id).order_by(
            ScreenDefinitionHistory.recorded_at, ScreenDefinitionHistory.id).offset(skip).limit(limit).all()
        return [{"id": row.id, "actor": row.actor, "action": row.action, "revision": row.revision,
                 "previous_revision": row.previous_revision, "snapshot": deepcopy(row.snapshot),
                 "recorded_at": row.recorded_at.isoformat()} for row in rows]
    finally:
        session.close()


@_durable_operation
def list_drafts(tenant_id: str) -> list[dict[str, Any]]:
    if _use_sql():
        return [_with_revision(item) for item in _sql_list(tenant_id)]
    return [_with_revision(item) for item in _DRAFTS.values() if item["tenant_id"] == tenant_id]


@_durable_operation
def get_draft(tenant_id: str, draft_id: str) -> dict[str, Any] | None:
    if _use_sql():
        item = _sql_get(tenant_id, draft_id)
        return _with_revision(item) if item is not None else None
    item = _DRAFTS.get(draft_id)
    if item is None or item["tenant_id"] != tenant_id:
        return None
    return _with_revision(item)


@_durable_operation
def save_draft(
    tenant_id: str,
    actor: str,
    definition: dict[str, Any],
    *,
    draft_id: str | None = None,
    readiness: dict[str, Any] | None = None,
    expected_revision: str | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    if _use_sql():
        return _with_revision(_sql_save(tenant_id, actor, definition, draft_id=draft_id, readiness=readiness, expected_revision=expected_revision, idempotency_key=idempotency_key))
    with _memory_lock:
        return _with_revision(_memory_save(tenant_id, actor, definition, draft_id=draft_id, readiness=readiness, expected_revision=expected_revision, idempotency_key=idempotency_key))


def _assert_snapshot(item: dict[str, Any], expected: dict[str, Any] | None) -> None:
    if expected is not None and any(
        item.get(key) != expected.get(key)
        for key in ("id", "tenant_id", "definition", "updated_at", "updated_by", "status")
    ):
        raise ValueError("entwurf_seit_pruefung_geaendert")


def _assert_transition(current: str, target: str) -> None:
    allowed = {"draft": {"review"}, "review": {"published_temp"}, "published_temp": {"retired"}, "retired": set()}
    if target not in allowed.get(current, set()):
        raise ValueError(f"statuswechsel_{current}_nach_{target}_unzulässig")


@_durable_operation
def set_status(
    tenant_id: str, draft_id: str, actor: str, status: str,
    *, expected_snapshot: dict[str, Any] | None = None,
    idempotency_key: str | None = None, request_revision: str | None = None,
) -> dict[str, Any]:
    if status not in _STATUSES:
        raise ValueError(f"status_{status}_unbekannt")
    if _use_sql():
        return _with_revision(_sql_set_status(tenant_id, draft_id, actor, status, expected_snapshot=expected_snapshot, idempotency_key=idempotency_key, request_revision=request_revision))
    with _memory_lock:
        item = _DRAFTS.get(draft_id)
        if item is None or item["tenant_id"] != tenant_id:
            raise KeyError(draft_id)
        if idempotency_key:
            replay = get_status_replay(tenant_id, draft_id, actor, status, request_revision, idempotency_key)
            if replay is not None:
                return replay
        _assert_snapshot(item, expected_snapshot)
        _assert_transition(item["status"], status)
        _assert_four_eyes(item["updated_by"], actor, status)
        previous = _with_revision(item)["revision"]
        item = deepcopy(item)
        item["status"] = status
        if status != "review":
            item["updated_by"] = actor
        item["updated_at"] = datetime.now(UTC).isoformat()
        _HISTORY.append(_history_entry(item, actor, status, previous, idempotency_key))
        _DRAFTS[draft_id] = item
        return _with_revision(item)


@_durable_operation
def get_published_definition(tenant_id: str, screen_id: str) -> dict[str, Any] | None:
    """Runtime-Lookup fuer published_temp. Native IDs werden nie aus Drafts geliefert."""
    if _is_native(screen_id):
        return None
    if _prefer_memory:
        return _memory_published(tenant_id, screen_id)
    return _sql_published(tenant_id, screen_id)


@_durable_operation
def list_published_definitions(tenant_id: str) -> list[dict[str, Any]]:
    if _prefer_memory:
        with _memory_lock:
            return [deepcopy(item["definition"]) for item in _DRAFTS.values()
                    if item["tenant_id"] == tenant_id and item["status"] == "published_temp"
                    and item.get("screen_id") and not _is_native(item["screen_id"])]
    return [definition for definition in _sql_list_published(tenant_id)
            if definition.get("id") and not _is_native(str(definition["id"]))]


def studio_run_route(screen_id: str) -> str:
    return f"/studio/run/{screen_id.replace('/', '__')}"


def _assert_four_eyes(updated_by: str, actor: str, status: str) -> None:
    if status == "published_temp" and updated_by == actor:
        raise PermissionError("vier_augen:publisher_gleich_letzter_editor")


def _is_native(screen_id: str) -> bool:
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS

    return screen_id in SCREEN_DEFINITION_BUILDERS


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _memory_published(tenant_id: str, screen_id: str) -> dict[str, Any] | None:
    for item in _DRAFTS.values():
        if (
            item["tenant_id"] == tenant_id
            and item["screen_id"] == screen_id
            and item["status"] == "published_temp"
        ):
            return deepcopy(item["definition"])
    return None


def _memory_save(
    tenant_id: str,
    actor: str,
    definition: dict[str, Any],
    *,
    draft_id: str | None,
    readiness: dict[str, Any] | None,
    expected_revision: str | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    if idempotency_key:
        entry = next((e for e in _HISTORY if e["id"] == idempotency_key), None)
        replay = _matching_save_replay(entry, tenant_id, actor, draft_id, definition, expected_revision)
        if replay is not None:
            return replay
    existing = _DRAFTS.get(draft_id) if draft_id else None
    if existing is None and draft_id is None:
        existing = _find_memory_by_screen(tenant_id, str(definition.get("id") or ""))
    if draft_id and existing is None:
        raise KeyError(draft_id)
    if not draft_id and existing is not None:
        raise ValueError("screen_id_bereits_vorhanden")
    if existing is not None and existing["tenant_id"] != tenant_id:
        raise KeyError(draft_id or existing["id"])
    if existing is not None and expected_revision is not None and _with_revision(existing)["revision"] != expected_revision:
        raise ValueError("entwurf_seit_anzeige_geaendert")
    if existing is not None and existing["status"] not in _EDITABLE:
        raise ValueError(f"status_{existing['status']}_nicht_editierbar")
    record = {
        "id": existing["id"] if existing else str(uuid4()),
        "tenant_id": tenant_id,
        "screen_id": definition.get("id"),
        "base_screen_id": definition.get("baseScreenId"),
        "definition": deepcopy(definition),
        "status": "draft",
        "readiness": deepcopy(readiness) if readiness is not None else (existing or {}).get("readiness"),
        "created_by": existing["created_by"] if existing else actor,
        "updated_by": actor,
        "updated_at": _now(),
    }
    _HISTORY.append(_history_entry(record, actor, "update" if existing else "create", _with_revision(existing)["revision"] if existing else None, idempotency_key))
    _DRAFTS[record["id"]] = record
    return deepcopy(record)


def _find_memory_by_screen(tenant_id: str, screen_id: str) -> dict[str, Any] | None:
    if not screen_id:
        return None
    for item in _DRAFTS.values():
        if item["tenant_id"] == tenant_id and item["screen_id"] == screen_id:
            return item
    return None


def _use_sql() -> bool:
    return not _prefer_memory


def _table_exists() -> bool:
    global _table_ok
    if _table_ok is not None:
        return _table_ok
    try:
        from app.core.database import SessionLocal

        session = SessionLocal()
        try:
            session.execute(text("SELECT 1 FROM domain_shared.screen_definition_drafts LIMIT 0"))
            _table_ok = True
        finally:
            session.close()
    except ProgrammingError:
        _table_ok = False
    except (OperationalError, Exception):
        return False
    return bool(_table_ok)


def _sql_session() -> Session:
    from app.core.database import SessionLocal

    return SessionLocal()


def _row_to_dict(row: Any) -> dict[str, Any]:
    updated = row.updated_at
    updated_s = updated.isoformat() if hasattr(updated, "isoformat") else str(updated)
    return {
        "id": row.id,
        "tenant_id": row.tenant_id,
        "screen_id": row.screen_id,
        "base_screen_id": row.base_screen_id,
        "definition": deepcopy(row.definition) if isinstance(row.definition, dict) else row.definition,
        "status": row.status,
        "readiness": deepcopy(row.readiness) if isinstance(row.readiness, dict) else row.readiness,
        "created_by": row.created_by,
        "updated_by": row.updated_by,
        "updated_at": updated_s,
    }


def _sql_list(tenant_id: str) -> list[dict[str, Any]]:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    session = _sql_session()
    try:
        rows = session.query(ScreenDefinitionDraft).filter_by(tenant_id=tenant_id).all()
        return [_row_to_dict(row) for row in rows]
    finally:
        session.close()


def _sql_get(tenant_id: str, draft_id: str) -> dict[str, Any] | None:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    session = _sql_session()
    try:
        row = session.get(ScreenDefinitionDraft, draft_id)
        if row is None or row.tenant_id != tenant_id:
            return None
        return _row_to_dict(row)
    finally:
        session.close()


def _sql_save(
    tenant_id: str,
    actor: str,
    definition: dict[str, Any],
    *,
    draft_id: str | None,
    readiness: dict[str, Any] | None,
    expected_revision: str | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    screen_id = str(definition.get("id") or "")
    session = _sql_session()
    try:
        if idempotency_key:
            # Same UUID is serialized even when two CREATEs have no row yet.
            session.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"), {"key": idempotency_key})
            replay = _sql_save_replay(session, idempotency_key, tenant_id, actor, draft_id, definition, expected_revision)
            if replay is not None:
                return replay
        row = (session.query(ScreenDefinitionDraft).filter_by(id=draft_id, tenant_id=tenant_id)
               .with_for_update().one_or_none()) if draft_id else None
        if draft_id and row is None:
            raise KeyError(draft_id)
        if row is None and not draft_id and screen_id:
            row = (
                session.query(ScreenDefinitionDraft)
                .filter_by(tenant_id=tenant_id, screen_id=screen_id)
                .with_for_update().one_or_none()
            )
        if not draft_id and row is not None:
            raise ValueError("screen_id_bereits_vorhanden")
        if row is not None and expected_revision is not None and _with_revision(_row_to_dict(row))["revision"] != expected_revision:
            raise ValueError("entwurf_seit_anzeige_geaendert")
        if row is not None and row.tenant_id != tenant_id:
            raise KeyError(draft_id or row.id)
        if row is not None and row.status not in _EDITABLE:
            raise ValueError(f"status_{row.status}_nicht_editierbar")
        previous = _with_revision(_row_to_dict(row))["revision"] if row is not None else None
        now = datetime.now(UTC)
        if row is None:
            row = ScreenDefinitionDraft(
                id=str(uuid4()),
                tenant_id=tenant_id,
                created_by=actor,
                status="draft",
            )
            session.add(row)
        row.screen_id = screen_id
        row.base_screen_id = definition.get("baseScreenId")
        row.status = "draft"
        row.definition = deepcopy(definition)
        row.readiness = deepcopy(readiness) if readiness is not None else row.readiness
        row.updated_by = actor
        row.updated_at = now
        session.flush()
        _append_sql_history(session, _row_to_dict(row), actor, "update" if previous else "create", previous, idempotency_key)
        session.commit()
        session.refresh(row)
        return _row_to_dict(row)
    except IntegrityError as error:
        session.rollback()
        raise ValueError("idempotenz_oder_screen_id_konflikt" if idempotency_key else "screen_id_bereits_vorhanden") from error
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _sql_set_status(
    tenant_id: str, draft_id: str, actor: str, status: str,
    *, expected_snapshot: dict[str, Any] | None = None,
    idempotency_key: str | None = None, request_revision: str | None = None,
) -> dict[str, Any]:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    session = _sql_session()
    try:
        row = (session.query(ScreenDefinitionDraft).filter_by(id=draft_id, tenant_id=tenant_id)
               .with_for_update().one_or_none())
        if row is None:
            raise KeyError(draft_id)
        if idempotency_key:
            replay = _sql_replay(session, idempotency_key, tenant_id, draft_id, actor, status, request_revision)
            if replay is not None:
                return replay
        _assert_snapshot(_row_to_dict(row), expected_snapshot)
        _assert_transition(row.status, status)
        _assert_four_eyes(row.updated_by, actor, status)
        previous = _with_revision(_row_to_dict(row))["revision"]
        row.status = status
        if status != "review":
            row.updated_by = actor
        row.updated_at = datetime.now(UTC)
        session.flush()
        _append_sql_history(session, _row_to_dict(row), actor, status, previous, idempotency_key)
        session.commit()
        session.refresh(row)
        return _row_to_dict(row)
    except IntegrityError as error:
        session.rollback()
        if idempotency_key:
            raise ValueError("idempotenzschluessel_anderer_auftrag") from error
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _sql_published(tenant_id: str, screen_id: str) -> dict[str, Any] | None:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    session = _sql_session()
    try:
        row = (
            session.query(ScreenDefinitionDraft)
            .filter_by(tenant_id=tenant_id, screen_id=screen_id, status="published_temp")
            .one_or_none()
        )
        if row is None or not isinstance(row.definition, dict):
            return None
        return deepcopy(row.definition)
    finally:
        session.close()


def _sql_list_published(tenant_id: str) -> list[dict[str, Any]]:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    session = _sql_session()
    try:
        rows = (
            session.query(ScreenDefinitionDraft)
            .filter_by(tenant_id=tenant_id, status="published_temp")
            .all()
        )
        return [deepcopy(row.definition) for row in rows if isinstance(row.definition, dict)]
    finally:
        session.close()


def clear_sql_studio_drafts() -> None:
    if not _table_exists():
        return
    session = _sql_session()
    try:
        session.execute(text("DELETE FROM domain_shared.screen_definition_drafts"))
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
