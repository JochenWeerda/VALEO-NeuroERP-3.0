"""Systemweit: gemeinsame 'system'-Zeilen nur mit Begruendung lesbar (rls_system_read_justified_20261027).

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).
"""

from __future__ import annotations

import importlib.util
import json
from types import SimpleNamespace

import pytest
import sqlalchemy as sa

import rls_domain_support as support
from app.core.tenant_context import cross_tenant_scope, tenant_scope
from rls_domain_support import A, ROOT

MIGRATIONS = ROOT / "alembic" / "versions"
EXCEPTIONS = json.loads((ROOT / "docs" / "admin" / "rls-exceptions.json").read_text(encoding="utf-8"))
FRISTEN = "domain_finance.aufbewahrungsfristen"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"_test_{name}", MIGRATIONS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MIGRATION = _load("rls_system_read_justified_20261027")


@pytest.mark.unit
def test_begruendete_tabellen_stimmen_mit_der_ausnahmeliste_ueberein():
    assert set(MIGRATION.KEEP_SYSTEM_READ) == set(EXCEPTIONS["system_lesbar"])
    assert EXCEPTIONS["altbestand_hoechstens"] == 0


@pytest.mark.unit
def test_umstellung_deckt_genau_die_bestandstabellen():
    expected = []
    for name, constant in MIGRATION.SOURCES:
        expected += list(getattr(_load(name), constant))
    covered = MIGRATION._covered_tables()
    assert covered == [t for t in dict.fromkeys(expected) if t not in MIGRATION.KEEP_SYSTEM_READ]
    assert len(covered) == 501


@pytest.fixture(scope="module")
def probe():
    with support.probe((FRISTEN,)) as conn:
        seeds = support.keys(conn, FRISTEN, "id", "tenant_id = 'system'")
        assert seeds, "frisches Schema ohne system-Seeds der Aufbewahrungsfristen"
        own = support.insert_row(conn, FRISTEN, A)
        support.as_app(conn)
        yield conn, seeds, own


@pytest.mark.integration
def test_system_seeds_sind_fuer_mandanten_unsichtbar_und_unberuehrbar(probe):
    conn, seeds, own = probe
    with tenant_scope(A, "test"):
        assert support.keys(conn, FRISTEN) == {own}
        for seed in seeds:
            assert support.affected(conn, f"UPDATE {FRISTEN} SET tenant_id = :a WHERE id = :i", {"a": A, "i": seed}) == 0
            assert support.affected(conn, f"DELETE FROM {FRISTEN} WHERE id = :i", {"i": seed}) == 0
    with cross_tenant_scope("test: Systemverbindung"):
        savepoint = conn.begin_nested()
        try:
            conn.execute(sa.text("SET LOCAL ROLE valeo_system"))
            assert seeds | {own} <= support.keys(conn, FRISTEN)
        finally:
            savepoint.rollback()


@pytest.mark.integration
def test_rueckweg_stellt_das_system_lesen_wieder_her(probe, monkeypatch):
    import rls_policy_shape

    conn, _seeds, _own = probe
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text("RESET ROLE"))
        monkeypatch.setattr(MIGRATION, "op", SimpleNamespace(
            execute=lambda sql: conn.execute(sa.text(sql)), get_bind=lambda: conn))
        covered = [t for t in MIGRATION._covered_tables() if support.exists(conn, t)]
        MIGRATION.downgrade()
        shapes = rls_policy_shape.shapes(conn)
        assert {shapes[t.removeprefix("public.")][0] for t in covered} == {"getrennt_system"}
        MIGRATION.upgrade()
        shapes = rls_policy_shape.shapes(conn)
        assert {shapes[t.removeprefix("public.")][0] for t in covered} == {"getrennt"}
    finally:
        savepoint.rollback()
