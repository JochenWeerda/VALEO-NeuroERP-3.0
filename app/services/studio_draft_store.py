"""Studio drafts with tenant isolation, four-eyes publish, and optional Postgres."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError
from sqlalchemy.orm import Session

_DRAFTS: dict[str, dict[str, Any]] = {}
_prefer_memory = False
_table_ok: bool | None = None
_EDITABLE = frozenset({"draft", "review"})
_STATUSES = frozenset({"draft", "review", "published_temp", "retired"})


def reset_studio_drafts() -> None:
    """Unit-Test-Reset: leert den Prozessspeicher und bleibt bewusst ohne Postgres."""
    global _prefer_memory
    _prefer_memory = True
    _DRAFTS.clear()


def use_sql_studio_drafts() -> None:
    """Schaltet Persistenz auf domain_shared.screen_definition_drafts."""
    global _prefer_memory, _table_ok
    _prefer_memory = False
    _table_ok = None
    _DRAFTS.clear()


def invalidate_studio_table_cache() -> None:
    global _table_ok
    _table_ok = None


def list_drafts(tenant_id: str) -> list[dict[str, Any]]:
    if _use_sql():
        return _sql_list(tenant_id)
    return [deepcopy(item) for item in _DRAFTS.values() if item["tenant_id"] == tenant_id]


def get_draft(tenant_id: str, draft_id: str) -> dict[str, Any] | None:
    if _use_sql():
        return _sql_get(tenant_id, draft_id)
    item = _DRAFTS.get(draft_id)
    if item is None or item["tenant_id"] != tenant_id:
        return None
    return deepcopy(item)


def save_draft(
    tenant_id: str,
    actor: str,
    definition: dict[str, Any],
    *,
    draft_id: str | None = None,
    readiness: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if _use_sql():
        return _sql_save(tenant_id, actor, definition, draft_id=draft_id, readiness=readiness)
    return _memory_save(tenant_id, actor, definition, draft_id=draft_id, readiness=readiness)


def set_status(tenant_id: str, draft_id: str, actor: str, status: str) -> dict[str, Any]:
    if status not in _STATUSES:
        raise ValueError(f"status_{status}_unbekannt")
    if _use_sql():
        return _sql_set_status(tenant_id, draft_id, actor, status)
    item = _DRAFTS.get(draft_id)
    if item is None or item["tenant_id"] != tenant_id:
        raise KeyError(draft_id)
    _assert_four_eyes(item["updated_by"], actor, status)
    item = deepcopy(item)
    item["status"] = status
    item["updated_by"] = actor
    item["updated_at"] = datetime.now(UTC).isoformat()
    _DRAFTS[draft_id] = item
    return deepcopy(item)


def get_published_definition(tenant_id: str, screen_id: str) -> dict[str, Any] | None:
    """Runtime-Lookup fuer published_temp. Native IDs werden nie aus Drafts geliefert."""
    if _is_native(screen_id):
        return None
    published = _memory_published(tenant_id, screen_id)
    if published is not None:
        return published
    if _prefer_memory:
        return None
    return _sql_published(tenant_id, screen_id)


def list_published_definitions(tenant_id: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in _DRAFTS.values():
        if item["tenant_id"] != tenant_id or item["status"] != "published_temp":
            continue
        screen_id = str(item.get("screen_id") or "")
        if not screen_id or _is_native(screen_id):
            continue
        items.append(deepcopy(item["definition"]))
        seen.add(screen_id)
    if _prefer_memory:
        return items
    for definition in _sql_list_published(tenant_id):
        screen_id = str(definition.get("id") or "")
        if not screen_id or screen_id in seen or _is_native(screen_id):
            continue
        items.append(definition)
        seen.add(screen_id)
    return items


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
) -> dict[str, Any]:
    existing = _DRAFTS.get(draft_id) if draft_id else None
    if existing is None and draft_id is None:
        existing = _find_memory_by_screen(tenant_id, str(definition.get("id") or ""))
    if existing is not None and existing["tenant_id"] != tenant_id:
        raise KeyError(draft_id or existing["id"])
    if existing is not None and existing["status"] not in _EDITABLE:
        raise ValueError(f"status_{existing['status']}_nicht_editierbar")
    record = {
        "id": existing["id"] if existing else str(uuid4()),
        "tenant_id": tenant_id,
        "screen_id": definition.get("id"),
        "base_screen_id": definition.get("baseScreenId"),
        "definition": deepcopy(definition),
        "status": existing["status"] if existing else "draft",
        "readiness": deepcopy(readiness) if readiness is not None else (existing or {}).get("readiness"),
        "created_by": existing["created_by"] if existing else actor,
        "updated_by": actor,
        "updated_at": _now(),
    }
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
    return not _prefer_memory and _table_exists()


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
) -> dict[str, Any]:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    screen_id = str(definition.get("id") or "")
    session = _sql_session()
    try:
        row = session.get(ScreenDefinitionDraft, draft_id) if draft_id else None
        if row is None and not draft_id and screen_id:
            row = (
                session.query(ScreenDefinitionDraft)
                .filter_by(tenant_id=tenant_id, screen_id=screen_id)
                .one_or_none()
            )
        if row is not None and row.tenant_id != tenant_id:
            raise KeyError(draft_id or row.id)
        if row is not None and row.status not in _EDITABLE:
            raise ValueError(f"status_{row.status}_nicht_editierbar")
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
        row.definition = deepcopy(definition)
        row.readiness = deepcopy(readiness) if readiness is not None else row.readiness
        row.updated_by = actor
        row.updated_at = now
        session.commit()
        session.refresh(row)
        return _row_to_dict(row)
    except IntegrityError as error:
        session.rollback()
        raise ValueError("screen_id_bereits_vorhanden") from error
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _sql_set_status(tenant_id: str, draft_id: str, actor: str, status: str) -> dict[str, Any]:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    session = _sql_session()
    try:
        row = session.get(ScreenDefinitionDraft, draft_id)
        if row is None or row.tenant_id != tenant_id:
            raise KeyError(draft_id)
        _assert_four_eyes(row.updated_by, actor, status)
        row.status = status
        row.updated_by = actor
        row.updated_at = datetime.now(UTC)
        session.commit()
        session.refresh(row)
        return _row_to_dict(row)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _sql_published(tenant_id: str, screen_id: str) -> dict[str, Any] | None:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    try:
        session = _sql_session()
    except Exception:
        return None
    try:
        row = (
            session.query(ScreenDefinitionDraft)
            .filter_by(tenant_id=tenant_id, screen_id=screen_id, status="published_temp")
            .one_or_none()
        )
        if row is None or not isinstance(row.definition, dict):
            return None
        return deepcopy(row.definition)
    except (ProgrammingError, OperationalError):
        return None
    finally:
        session.close()


def _sql_list_published(tenant_id: str) -> list[dict[str, Any]]:
    from app.infrastructure.models.studio_models import ScreenDefinitionDraft

    try:
        session = _sql_session()
    except Exception:
        return []
    try:
        rows = (
            session.query(ScreenDefinitionDraft)
            .filter_by(tenant_id=tenant_id, status="published_temp")
            .all()
        )
        return [deepcopy(row.definition) for row in rows if isinstance(row.definition, dict)]
    except (ProgrammingError, OperationalError):
        return []
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
