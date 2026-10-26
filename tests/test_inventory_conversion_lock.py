"""Inventory replacement must not race with writers after an empty-table check."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import pytest


def migration(monkeypatch, *, rows=False, all_uuid=False, missing=False, converted_after_lock=False):
    path = Path(__file__).resolve().parents[1] / "alembic/versions/inventory_service_shape_20261026.py"
    spec = importlib.util.spec_from_file_location("inventory_conversion_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    events = []
    names = [name for name, _ in module._TABLES]
    locked = set()
    checks = 0

    def id_type(_bind, name):
        nonlocal checks
        checks += 1
        if missing: return None
        return "uuid" if all_uuid or (converted_after_lock and checks > len(names)) else "text"

    def execute(statement):
        sql = str(statement)
        if sql.startswith("LOCK TABLE"):
            assert sql.endswith(" IN ACCESS EXCLUSIVE MODE"), "Lock must exclude concurrent writers"
            name = sql.split('"')[1]
            locked.add(name)
            events.append(("lock", name))
        elif "SELECT EXISTS" in sql:
            assert locked == set(names), "A writer can enter before all candidate tables are locked"
            events.append(("check", sql))
        else:
            events.append(("index", sql))
        return SimpleNamespace(scalar=lambda: rows)

    bind = SimpleNamespace(execute=execute)
    fake_op = SimpleNamespace(get_bind=lambda: bind, execute=execute, drop_table=lambda name: events.append(("drop", name)))
    monkeypatch.setattr(module, "op", fake_op)
    monkeypatch.setattr(module, "_id_type", id_type)
    monkeypatch.setattr(module, "_TABLES", tuple((name, lambda name=name: events.append(("create", name))) for name in names))
    return module, events


def test_empty_compatibility_replacement_holds_all_locks_before_measuring(monkeypatch):
    module, events = migration(monkeypatch)
    module.upgrade()
    kinds = [kind for kind, _ in events]
    assert kinds[:4] == ["lock"] * 4
    assert kinds.count("check") == 4
    assert kinds.count("drop") == kinds.count("create") == 4
    assert max(i for i, kind in enumerate(kinds) if kind == "check") < kinds.index("drop")


def test_existing_rows_abort_without_dropping_any_table(monkeypatch):
    module, events = migration(monkeypatch, rows=True)
    with pytest.raises(RuntimeError, match="hold rows"):
        module.upgrade()
    assert not any(kind in {"drop", "create"} for kind, _ in events)


def test_live_uuid_shape_remains_a_lock_free_noop(monkeypatch):
    module, events = migration(monkeypatch, all_uuid=True)
    module.upgrade()
    assert events == []


def test_absent_tables_are_created_without_attempting_to_lock_them(monkeypatch):
    module, events = migration(monkeypatch, missing=True)
    module.upgrade()
    assert len([event for event in events if event[0] == "create"]) == 4
    assert not any(kind in {"lock", "check", "drop"} for kind, _ in events)


def test_shape_is_reread_after_waiting_for_locks(monkeypatch):
    module, events = migration(monkeypatch, converted_after_lock=True)
    module.upgrade()
    assert len(events) == 4
    assert all(kind == "lock" for kind, _ in events)
