"""RLS-Domains: Ratsche gegen abweichende Policy-Strukturen.

Jede Tabelle mit RLS traegt genau eine der Formen aus scripts/rls_policy_shape.py: die
getrennten Policies je Befehl (neu) oder die ALL-Policy ``tenant_isolation`` (alt, Zahl darf
nur sinken). ``system``-Lesen nur fuer Tabellen mit Begruendung in rls-exceptions.json.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import pytest
import sqlalchemy as sa

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rls_policy_shape as shape  # noqa: E402

EXCEPTIONS = json.loads((ROOT / "docs" / "admin" / "rls-exceptions.json").read_text(encoding="utf-8"))
URL = os.environ.get("TEST_DATABASE_URL")

OWN_V = "((tenant_id)::text = rls_current_tenant())"
SHARED_V = ("(((tenant_id)::text = rls_current_tenant()) OR (((tenant_id)::text = 'system'::text) "
            "AND (rls_current_tenant() IS NOT NULL)))")


def _split(select_qual=OWN_V, **override):
    rows = {
        "tenant_select": ("tenant_select", "r", True, "{0}", select_qual, None),
        "tenant_insert": ("tenant_insert", "a", True, "{0}", None, OWN_V),
        "tenant_update": ("tenant_update", "w", True, "{0}", OWN_V, OWN_V),
        "tenant_delete": ("tenant_delete", "d", True, "{0}", OWN_V, None),
    }
    rows.update(override)
    return [r for r in rows.values() if r is not None]


@pytest.mark.unit
def test_formen_selbsttest():
    assert shape.classify(False, _split()) == ("getrennt", "")
    assert shape.classify(False, _split(SHARED_V)) == ("getrennt_system", "")
    legacy = [("tenant_isolation", "*", True, "{0}", SHARED_V, OWN_V)]
    assert shape.classify(False, legacy) == ("alt", "")


@pytest.mark.unit
@pytest.mark.parametrize("policies, force", [
    # breite ALL-Policy neben den getrennten: PostgreSQL verknuepft permissive Policies mit OR
    (_split() + [("tenant_isolation", "*", True, "{0}", SHARED_V, OWN_V)], False),
    (_split(tenant_delete=None), False),
    # DELETE oder UPDATE auf system-Zeilen
    (_split(tenant_delete=("tenant_delete", "d", True, "{0}", SHARED_V, None)), False),
    (_split(tenant_update=("tenant_update", "w", True, "{0}", SHARED_V, OWN_V)), False),
    # Schreiben ohne Pruefung des Ergebnisses
    (_split(tenant_update=("tenant_update", "w", True, "{0}", OWN_V, None)), False),
    (_split(tenant_insert=("tenant_insert", "a", True, "{0}", None, SHARED_V)), False),
    (_split(tenant_select=("tenant_select", "r", False, "{0}", OWN_V, None)), False),
    (_split(tenant_select=("tenant_select", "r", True, "{16384}", OWN_V, None)), False),
    (_split(tenant_select=("tenant_select", "*", True, "{0}", OWN_V, None)), False),
    (_split(), True),
    ([(None, None, None, None, None, None)], False),
])
def test_abweichungen_werden_erkannt(policies, force):
    assert shape.classify(force, policies)[0] == "abweichend"


@pytest.mark.integration
def test_alle_rls_tabellen_tragen_eine_zulaessige_form():
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    import rls_inventory

    engine = sa.create_engine(URL)
    with engine.connect() as conn:
        tx = conn.begin()
        try:
            rls_inventory._pending_upgrade(conn)
            result = shape.shapes(conn)
        finally:
            tx.rollback()
    engine.dispose()
    bad = {t: d for t, (s, d) in result.items() if s == "abweichend"}
    assert not bad, list(bad.items())[:5]
    shared = {t for t, (s, _) in result.items() if s == "getrennt_system"}
    assert shared <= set(EXCEPTIONS["system_lesbar"]), f"system-Lesen ohne Begruendung: {sorted(shared - set(EXCEPTIONS['system_lesbar']))}"
    counts = Counter(s for s, _ in result.values())
    assert counts["alt"] <= EXCEPTIONS["altform_hoechstens"], counts
