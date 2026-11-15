"""Bounded inventory drift planning and transaction guards; no database access."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from scripts import repair_inventory_reference_drift as repair

pytestmark = pytest.mark.unit
FULL_PLAN = [statement for ref in repair.REFERENCES for statement in ref.additions()]
ADD_COLUMN, ADD_FK, ADD_INDEX = repair.REFERENCES[0].additions()


@pytest.fixture
def catalog():
    result = {"tables": {}, "columns": {}, "constraints": [], "indexes": [], "policies": []}
    for table in repair.TABLES:
        result["tables"][table] = {"relkind": "r", "owner": "valeo_owner", "rls": True, "force_rls": False}
        for name in ("id", "tenant_id", "zone_id", "warehouse_id"):
            result["columns"][table, name] = {
                "type": ("character varying" if table in (repair.QUEUE, repair.ARTICLES) else
                         "character varying(64)" if name == "tenant_id" else "character varying(36)"),
                "not_null": True, "generated": "", "default_value": None,
            }
        result["constraints"].append({"table_name": table, "name": table + "_pkey", "kind": "p", "columns": ["id"]})
    return result


def completed(catalog, *, evolved=False):
    result = deepcopy(catalog)
    for ref in repair.REFERENCES:
        result["columns"][ref.child, ref.column] = {
            "type": ref.catalog_type, "not_null": False, "generated": "", "default_value": None,
        }
        result["constraints"].append({
            "table_name": ref.child, "name": ref.tenant_fk if evolved else ref.fk, "kind": "f",
            "columns": [ref.column, "tenant_id"] if evolved else [ref.column],
            "parent_schema": repair.SCHEMA, "parent": ref.parent,
            "parent_columns": ["id", "tenant_id"] if evolved else ["id"],
            "validated": True, "deferrable": False, "on_delete": ref.delete_code, "on_update": "a", "match": "s",
            "delete_columns": [ref.column] if evolved and ref.delete_code == "n" else [],
        })
        result["indexes"].append({"name": ref.index, "table_name": ref.child, "method": "btree",
                                  "valid": True, "ready": True, "unique": False, "attributes": 1,
                                  "keys": 1, "predicate": None, "first_column": ref.column})
    return result


def test_missing_optional_column_produces_only_canonical_additions_and_does_not_mutate_input(catalog):
    original = deepcopy(catalog)
    assert repair.repair_plan(catalog, inventory_applied=False) == FULL_PLAN
    assert catalog == original


@pytest.mark.parametrize("evolved", [False, True])
def test_existing_contract_is_idempotent_including_evolved_tenant_fk(catalog, evolved):
    assert repair.repair_plan(completed(catalog, evolved=evolved), inventory_applied=evolved) == []


def test_partial_pre_rls_contract_adds_only_missing_original_objects(catalog):
    state = completed(catalog)
    state["constraints"] = [c for c in state["constraints"] if c["name"] != repair.FK]
    assert repair.repair_plan(state, inventory_applied=False) == [ADD_FK]
    state["indexes"] = [i for i in state["indexes"] if i["name"] != repair.INDEX]
    assert repair.repair_plan(state, inventory_applied=False) == [ADD_FK, ADD_INDEX]


@pytest.mark.parametrize("mutate", [
    lambda c: c["tables"].pop(repair.AISLES),
    lambda c: c["tables"][repair.BINS].update(owner="valeo_dev"),
    lambda c: c["tables"][repair.BINS].update(relkind="p"),
    lambda c: c["columns"][repair.AISLES, "id"].update(type="uuid"),
    lambda c: c["columns"][repair.BINS, "tenant_id"].update(not_null=False),
    lambda c: c["columns"].pop((repair.AISLES, "warehouse_id")),
    lambda c: c["constraints"].clear(),
    lambda c: c["indexes"].append({"name": repair.INDEX}),
    lambda c: c["constraints"].append({"table_name": repair.BINS, "name": repair.FK, "kind": "f", "columns": ["zone_id"]}),
])
def test_missing_column_rejects_incompatible_existing_state(catalog, mutate):
    mutate(catalog)
    with pytest.raises(repair.RepairError):
        repair.repair_plan(catalog, inventory_applied=False)


@pytest.mark.parametrize("mutate", [
    lambda c: c["columns"][repair.BINS, "aisle_id"].update(type="character varying(64)"),
    lambda c: c["columns"][repair.BINS, "aisle_id"].update(default_value="'guessed'"),
    lambda c: c["columns"][repair.BINS, "aisle_id"].update(not_null=True),
    lambda c: c["constraints"][-1].update(validated=False),
    lambda c: c["constraints"][-1].update(parent=repair.BINS),
    lambda c: c["constraints"][-1].update(on_delete="c"),
    lambda c: c["constraints"][-1].update(columns=["tenant_id", "aisle_id"]),
    lambda c: c["indexes"][0].update(valid=False),
    lambda c: c["indexes"][0].update(unique=True),
    lambda c: c["indexes"][0].update(attributes=2),
    lambda c: c["indexes"][0].update(predicate="is_active"),
    lambda c: c["indexes"][0].update(table_name=repair.AISLES),
])
def test_present_column_rejects_weakened_or_different_contracts(catalog, mutate):
    state = completed(catalog)
    mutate(state)
    with pytest.raises(repair.RepairError):
        repair.repair_plan(state, inventory_applied=False)


def test_post_inventory_state_never_recreates_a_weaker_single_column_fk(catalog):
    for state in (catalog, completed(catalog)):
        with pytest.raises(repair.RepairError):
            repair.repair_plan(state, inventory_applied=True)
    state = completed(catalog, evolved=True)
    state["constraints"] = catalog["constraints"]
    with pytest.raises(repair.RepairError):
        repair.repair_plan(state, inventory_applied=True)


def test_evolved_queue_set_null_must_preserve_tenant_column(catalog):
    state = completed(catalog, evolved=True)
    state["constraints"][-1]["delete_columns"] = []
    with pytest.raises(repair.RepairError):
        repair.repair_plan(state, inventory_applied=True)


@pytest.mark.parametrize("column", ["aisle_id", "article_id"])
def test_one_missing_reference_is_repaired_without_changing_the_existing_other(catalog, column):
    state = completed(catalog)
    ref = next(r for r in repair.REFERENCES if r.column == column)
    del state["columns"][ref.child, ref.column]
    state["constraints"] = [c for c in state["constraints"] if c["name"] != ref.fk]
    state["indexes"] = [i for i in state["indexes"] if i["name"] != ref.index]
    assert repair.repair_plan(state, inventory_applied=False) == list(ref.additions())


def test_second_reference_failure_prevents_any_first_reference_plan(catalog):
    catalog["columns"][repair.ARTICLES, "id"]["type"] = "uuid"
    with pytest.raises(repair.RepairError):
        repair.repair_plan(catalog, inventory_applied=False)


@pytest.mark.parametrize("superuser,bypass", [(True, False), (False, True), (True, True)])
def test_even_named_migrator_with_superpowers_is_rejected(superuser, bypass):
    conn = MagicMock()
    conn.execute.side_effect = [SimpleNamespace(one=lambda: ("valeo_probe", "valeo_migrator", "valeo_owner", superuser, bypass)),
                                SimpleNamespace(scalars=lambda: ["expected"])]
    with pytest.raises(repair.RepairError):
        repair.check_identity(conn, "valeo_probe", "expected", apply=True)


@pytest.mark.parametrize("actual_db,revisions,login,role,apply", [
    ("other", ["expected"], "valeo_agent", "valeo_agent", False),
    ("valeo_probe", ["different"], "valeo_agent", "valeo_agent", False),
    ("valeo_probe", ["expected", "other"], "valeo_agent", "valeo_agent", False),
    ("valeo_probe", ["expected"], "valeo_dev", "valeo_owner", True),
    ("valeo_probe", ["expected"], "valeo_migrator", "valeo_migrator", True),
])
def test_actual_database_revision_and_login_are_checked(actual_db, revisions, login, role, apply):
    conn = MagicMock()
    conn.execute.side_effect = [SimpleNamespace(one=lambda: (actual_db, login, role)),
                                SimpleNamespace(scalars=lambda: revisions)]
    with pytest.raises(repair.RepairError):
        repair.check_identity(conn, "valeo_probe", "expected", apply=apply)


def transaction_fixture(monkeypatch, catalog, *, after=None):
    conn = MagicMock()
    tx = conn.begin.return_value
    tx.is_active = True
    conn.execute.return_value.scalar_one.return_value = 7
    monkeypatch.setattr(repair, "revision_has_inventory", lambda _: False)
    monkeypatch.setattr(repair, "check_identity", MagicMock())
    inspector = MagicMock(side_effect=[catalog, after or completed(catalog)])
    monkeypatch.setattr(repair, "inspect_catalog", inspector)
    return conn, tx, inspector


def test_plan_transaction_is_read_only_rolls_back_and_never_executes_ddl(monkeypatch, catalog):
    conn, tx, inspector = transaction_fixture(monkeypatch, catalog)
    assert repair.execute_repair(conn, "valeo_probe", "expected") == FULL_PLAN
    sql = [str(c.args[0]) for c in conn.execute.call_args_list]
    assert sql[0] == "SET TRANSACTION READ ONLY"
    assert not any(s.startswith(("ALTER", "CREATE", "LOCK", "INSERT", "UPDATE", "DELETE")) for s in sql)
    tx.rollback.assert_called_once()
    tx.commit.assert_not_called()
    assert inspector.call_count == 1


@pytest.mark.parametrize("rollback", [False, True])
def test_apply_rechecks_under_bounded_locks_and_verifies_before_commit_or_rollback(monkeypatch, catalog, rollback):
    conn, tx, inspector = transaction_fixture(monkeypatch, catalog)
    repair.execute_repair(conn, "valeo_probe", "expected", apply=True, rollback=rollback)
    sql = [str(c.args[0]) for c in conn.execute.call_args_list]
    assert "SET LOCAL lock_timeout = '5s'" in sql
    assert "SET LOCAL statement_timeout = '30s'" in sql
    assert sql.index(next(s for s in sql if s.startswith("LOCK TABLE"))) < sql.index(ADD_COLUMN)
    assert [s for s in sql if s.startswith(("ALTER", "CREATE"))] == FULL_PLAN
    assert repair.check_identity.call_count == 2
    assert inspector.call_count == 2
    (tx.rollback if rollback else tx.commit).assert_called_once()
    (tx.commit if rollback else tx.rollback).assert_not_called()


@pytest.mark.parametrize("change", ["incomplete", "policies", "rows", "columns", "fk"])
def test_failed_postconditions_roll_back_all_work(monkeypatch, catalog, change):
    after = completed(catalog)
    if change == "incomplete":
        after["indexes"] = []
    elif change == "policies":
        after["policies"] = [{"policyname": "unexpected"}]
    elif change == "columns":
        after["columns"][repair.BINS, "zone_id"]["default_value"] = "'unexpected'"
    elif change == "fk":
        # An unrelated key must survive as well.
        catalog["constraints"].append({"table_name": repair.BINS, "name": "unrelated", "kind": "f", "columns": ["zone_id"]})
    conn, tx, _ = transaction_fixture(monkeypatch, catalog, after=after)
    if change == "rows":
        conn.execute.return_value.scalar_one.side_effect = [7, 7, 7, 7, 8]
    with pytest.raises(repair.RepairError):
        repair.execute_repair(conn, "valeo_probe", "expected", apply=True)
    tx.rollback.assert_called_once()
    tx.commit.assert_not_called()


def test_statement_failure_rolls_back(monkeypatch, catalog):
    conn, tx, _ = transaction_fixture(monkeypatch, catalog)
    normal = conn.execute.return_value
    def execute(sql):
        if str(sql) == ADD_FK:
            raise RuntimeError("simulated validation failure")
        return normal
    conn.execute.side_effect = execute
    with pytest.raises(RuntimeError):
        repair.execute_repair(conn, "valeo_probe", "expected", apply=True)
    tx.rollback.assert_called_once()
    tx.commit.assert_not_called()


def test_cli_redacts_connection_errors_and_refuses_non_migrator_writes(monkeypatch, capsys):
    monkeypatch.setenv("REPAIR_TEST_URL", "postgresql://valeo_dev:SECRET@localhost/valeo_probe")
    engine = MagicMock(side_effect=AssertionError("must not connect"))
    monkeypatch.setattr(repair, "create_engine", engine)
    args = ["--expected-database", "valeo_probe", "--expected-revision", "expected", "--url-env", "REPAIR_TEST_URL"]
    assert repair.main([*args, "--anwenden"]) == 1
    engine.assert_not_called()
    monkeypatch.setattr(repair, "create_engine", MagicMock(side_effect=RuntimeError("postgresql://SECRET")))
    assert repair.main(args) == 1
    assert "SECRET" not in capsys.readouterr().err


def test_real_repository_revision_dag_distinguishes_pre_and_post_inventory():
    assert repair.revision_has_inventory("runtime_ddl_to_migrations_20261026") is False
    assert repair.revision_has_inventory(repair.RLS_REV) is True
    with pytest.raises(repair.RepairError):
        repair.revision_has_inventory("001")


@pytest.mark.parametrize("url", [
    "postgresql://valeo_migrator:SECRET@production.example/valeo_probe",
    "postgresql://valeo_migrator:SECRET@localhost/valeo_probe?host=production.example",
    "postgresql://valeo_migrator:SECRET@localhost/valeo_probe?service=production",
    "postgresql://valeo_migrator:SECRET@localhost:5433/valeo_probe",
])
def test_cli_rejects_external_or_overridden_connection_targets_before_connecting(monkeypatch, capsys, url):
    monkeypatch.setenv("REPAIR_TEST_URL", url)
    engine = MagicMock(side_effect=AssertionError("must not connect"))
    monkeypatch.setattr(repair, "create_engine", engine)
    assert repair.main(["--expected-database", "valeo_probe", "--expected-revision", "expected",
                        "--url-env", "REPAIR_TEST_URL"]) == 1
    engine.assert_not_called()
    assert "SECRET" not in capsys.readouterr().err
