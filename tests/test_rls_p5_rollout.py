"""RLS-Plan P5: Ausrollen per Ratsche.

Jede Klasse-A-Tabelle hat RLS oder steht mit Grund in ``pending`` von
docs/admin/rls-rollout.json. Eine neue Mandantentabelle landet in ``ready`` und macht den Test
rot, bis eine Migration sie absichert oder die Analyse einen Grund nennt.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
import sqlalchemy as sa

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rls_rollout  # noqa: E402

ROLLOUT = json.loads(rls_rollout.OUTPUT.read_text(encoding="utf-8"))
INVENTORY = json.loads(rls_rollout.INVENTORY.read_text(encoding="utf-8"))
URL = os.environ.get("TEST_DATABASE_URL")
@pytest.mark.unit
def test_analyse_ist_aktuell():
    assert rls_rollout.analyse(INVENTORY) == ROLLOUT, "python scripts/rls_rollout.py ausfuehren"


@pytest.mark.unit
def test_keine_klasse_a_tabelle_ohne_rls_und_ohne_grund():
    assert ROLLOUT["ready"] == [], f"ohne RLS und ohne Grund: {ROLLOUT['ready'][:10]}"
    assert all(ROLLOUT["pending"].values())
    unprotected = {t["table"] for t in INVENTORY["tables"] if t["class"] == "A" and not t["rls"]}
    assert unprotected == set(ROLLOUT["pending"])


@pytest.mark.unit
def test_analyse_haelt_riskante_tabellen_zurueck(monkeypatch):
    inventory = {"tables": [
        {"table": "domain_x.sicher", "class": "A", "rls": False},
        {"table": "domain_x.standard", "class": "A", "rls": False},
        {"table": "domain_x.nullig", "class": "A", "rls": False},
        {"table": "domain_x.api_tokens", "class": "A", "rls": False},
        {"table": "domain_x.quer", "class": "A", "rls": False},
    ]}
    files = [
        ("app/a.py", "db.execute('SELECT * FROM domain_x.sicher WHERE id = :i')"),
        ("app/b.py", "t = settings.DEFAULT_TENANT_ID\nq = 'SELECT 1 FROM domain_x.standard'"),
        ("app/c.py", "q = 'SELECT 1 FROM domain_x.nullig WHERE tenant_id IS NULL'"),
        ("app/d.py", "q = 'SELECT tenant_id FROM domain_x.api_tokens WHERE token = :t'"),
        ("app/e.py", "with cross_tenant_scope('x'):\n    q = 'SELECT 1 FROM domain_x.quer'"),
    ]
    monkeypatch.setattr(rls_rollout, "_code_files", lambda: iter(files))
    result = rls_rollout.analyse(inventory)
    assert result["ready"] == ["domain_x.sicher"]
    assert result["pending"] == {
        "domain_x.api_tokens": ["identitaet", "mandant_ermitteln"],
        "domain_x.nullig": ["mandant_null"],
        "domain_x.quer": ["uebergreifend"],
        "domain_x.standard": ["standardmandant"],
    }


@pytest.mark.integration
def test_alle_rls_tabellen_tragen_genau_die_mandantenpolicy():
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    import rls_inventory
    engine = sa.create_engine(URL)
    with engine.connect() as conn:
        tx = conn.begin()
        try:
            rls_inventory._pending_upgrade(conn)
            rows = conn.execute(sa.text("""
                SELECT c.oid::regclass::text, c.relforcerowsecurity,
                       array_agg(p.polname ORDER BY p.polname),
                       array_agg(pg_get_expr(p.polqual, p.polrelid) ORDER BY p.polname),
                       array_agg(pg_get_expr(p.polwithcheck, p.polrelid) ORDER BY p.polname)
                  FROM pg_class c LEFT JOIN pg_policy p ON p.polrelid = c.oid
                 WHERE c.relrowsecurity GROUP BY 1, 2""")).all()
            assert len(rows) == INVENTORY["summary"]["rls_enabled"]
            # Form je Tabelle: eine gemeinsame Definition (scripts/rls_policy_shape.py, uebernommen
            # von Codex' Fassung am 27.10.2026). SELECT liest eigene Zeilen; gemeinsame
            # 'system'-Zeilen nur, wo docs/admin/rls-exceptions.json (system_lesbar) es begruendet.
            import rls_policy_shape
            exceptions = json.loads((ROOT / "docs" / "admin" / "rls-exceptions.json").read_text(encoding="utf-8"))
            shapes = rls_policy_shape.shapes(conn)
            assert set(shapes) == {table for table, *_ in rows}
            bad = [(t, s, d) for t, (s, d) in shapes.items()
                   if s not in ("getrennt", "getrennt_system")
                   or (s == "getrennt_system" and t not in exceptions["system_lesbar"])]
            assert not bad, bad[:5]
            # Jede Policy wird als valeo_app wirklich ausgewertet: Typvergleich, Funktionsrechte.
            schemas = {table.split(".")[0] for table, *_ in rows if "." in table} | {"public"}
            for schema in schemas:
                conn.execute(sa.text(f'GRANT USAGE ON SCHEMA "{schema}" TO valeo_app'))
                conn.execute(sa.text(f'GRANT SELECT ON ALL TABLES IN SCHEMA "{schema}" TO valeo_app'))
            conn.execute(sa.text("SET LOCAL ROLE valeo_app"))
            failures = []
            for tenant in ("rls-probe", ""):
                conn.execute(sa.text("SELECT set_config('app.tenant_id', :t, true)"), {"t": tenant})
                for table, *_ in rows:
                    nested = conn.begin_nested()
                    try:
                        conn.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar()
                        nested.commit()
                    except sa.exc.DBAPIError as exc:
                        nested.rollback()
                        failures.append((table, tenant, str(exc.orig).splitlines()[0]))
            assert not failures, failures[:5]
        finally:
            tx.rollback()
    engine.dispose()
