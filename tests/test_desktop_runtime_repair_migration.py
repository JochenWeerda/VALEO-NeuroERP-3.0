"""The additive repair preserves the original table contract and existing tables."""
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

from alembic.config import Config
from alembic.script import ScriptDirectory
import pytest
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "alembic/versions" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def table_contract(call):
    name, *parts = call.args
    columns = [(p.name, str(p.type.compile(dialect=postgresql.dialect())), p.nullable,
                str(p.server_default.arg) if p.server_default else None)
               for p in parts if isinstance(p, sa.Column)]
    constraints = [(type(p).__name__, p.name,
                    tuple(element.target_fullname for element in p.elements)
                    if isinstance(p, sa.ForeignKeyConstraint) else tuple(p._pending_colargs))
                   for p in parts if isinstance(p, (sa.ForeignKeyConstraint, sa.UniqueConstraint, sa.PrimaryKeyConstraint))]
    return name, columns, constraints, call.kwargs


def test_report_permissions_matches_historical_contract(monkeypatch):
    original = load("admin_report_permissions_20260215")
    repair = load("desktop_runtime_repair_20260909")
    original.op = MagicMock()
    repair.op = MagicMock()
    inspector = MagicMock()
    inspector.has_table.return_value = False
    inspector.get_indexes.return_value = []
    monkeypatch.setattr(repair.sa, "inspect", lambda _: inspector)
    original.upgrade()
    repair._admin_report_permissions_20260215()
    assert table_contract(repair.op.create_table.call_args) == table_contract(original.op.create_table.call_args)
    assert repair.op.create_index.call_args_list == original.op.create_index.call_args_list


def test_existing_report_permissions_and_indexes_are_untouched(monkeypatch):
    repair = load("desktop_runtime_repair_20260909")
    repair.op = MagicMock()
    inspector = MagicMock()
    inspector.has_table.return_value = True
    inspector.get_indexes.return_value = [
        {"name": "ix_admin_report_permissions_tenant_role"},
        {"name": "ix_admin_report_permissions_tenant_report"},
    ]
    monkeypatch.setattr(repair.sa, "inspect", lambda _: inspector)
    repair._admin_report_permissions_20260215()
    repair.op.create_table.assert_not_called()
    repair.op.create_index.assert_not_called()
    repair.op.execute.assert_not_called()


def test_repair_is_single_resolvable_head():
    config = Config()
    config.set_main_option("script_location", str(ROOT / "alembic"))
    script = ScriptDirectory.from_config(config)
    assert script.get_heads() == ["desktop_runtime_repair_20260909"]
    assert script.get_revision("desktop_runtime_repair_20260909").down_revision == "inv_movement_type_register_20260825"


def test_downgrade_refuses_to_delete_existing_business_tables():
    with pytest.raises(RuntimeError, match="pre-existing business tables"):
        load("desktop_runtime_repair_20260909").downgrade()
