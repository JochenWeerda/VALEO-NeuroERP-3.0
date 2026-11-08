"""RLS-Plan P0: das Inventar in docs/admin/rls-inventory.json ist aktuell.

Eine neue Tabelle oder ein neuer Weg an der Mandantenbindung vorbei (Sitzung ausserhalb eines
Requests, direkte Verbindung, eigene Engine, Treiberverbindung, Standardmandant) macht das
Inventar ungueltig, bis es mit ``python scripts/rls_inventory.py`` neu erzeugt ist. So wird
jede Aenderung sichtbar und im Review klassifiziert (docs/architecture/rls-mandantenkernel-plan.md).
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rls_inventory  # noqa: E402

INVENTORY = json.loads(rls_inventory.OUTPUT.read_text(encoding="utf-8"))


# --- Selbsttest -------------------------------------------------------------------------


@pytest.mark.unit
def test_klassen():
    assert rls_inventory.classify("character varying(64)", True, []) == "A"
    assert rls_inventory.classify("text", False, []) == "B"
    assert rls_inventory.classify(None, None, ["domain_x.kopf"]) == "C"
    assert rls_inventory.classify(None, None, []) == "D"


@pytest.mark.unit
def test_codemuster_erkennen_umgehungswege(monkeypatch):
    synthetic = (
        "db = SessionLocal()\n"
        "with engine.connect() as c: pass\n"
        "e = create_async_engine(url)\n"
        "c = psycopg2.connect(dsn)\n"
        "t = settings.DEFAULT_TENANT_ID\n"
        "q = 'WHERE tenant_id = :t'\n"
    )
    monkeypatch.setattr(rls_inventory, "_code_files", lambda: iter([("app/x.py", synthetic)]))
    paths, filters = rls_inventory.scan_code()
    assert {name: files.get("app/x.py") for name, files in paths.items()} == {
        "session_local": 1, "engine_direct": 1, "new_engine": 1, "driver_connect": 1, "default_tenant": 1,
    }
    assert filters["sql_tenant_filter"] == 1


# --- Vertrag ohne Datenbank ---------------------------------------------------------------


@pytest.mark.unit
def test_codepfade_sind_im_inventar_erfasst():
    current, _ = rls_inventory.scan_code()
    recorded = INVENTORY["code_paths"]
    for name in rls_inventory.CODE_PATTERNS:
        new = {f: n for f, n in current[name].items() if recorded.get(name, {}).get(f) != n}
        gone = {f: n for f, n in recorded.get(name, {}).items() if f not in current[name]}
        assert not new and not gone, (
            f"{name}: Inventar veraltet (neu/geaendert {new}, entfallen {gone}); "
            "python scripts/rls_inventory.py --code-only ausfuehren und im Review klassifizieren"
        )


@pytest.mark.unit
def test_inventar_ist_in_sich_stimmig():
    tables = INVENTORY["tables"]
    assert INVENTORY["summary"] == rls_inventory.summary(tables)
    assert len({t["table"] for t in tables}) == len(tables)
    for t in tables:
        assert t["class"] == rls_inventory.classify(
            t["tenant_type"], t["class"] == "A", t.get("tenant_parents", [])
        ), t["table"]


# --- Vertrag gegen die frische Datenbank --------------------------------------------------


@pytest.mark.integration
def test_tabellen_entsprechen_dem_frischen_schema():
    if not os.environ.get("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    tables, _ = rls_inventory.scan_tables(rls_inventory._probe_url())
    recorded = {t["table"]: t for t in INVENTORY["tables"]}
    current = {t["table"]: t for t in tables}
    added = sorted(set(current) - set(recorded))
    removed = sorted(set(recorded) - set(current))
    changed = sorted(k for k in set(current) & set(recorded) if current[k] != recorded[k])
    assert not (added or removed or changed), (
        f"neu {added[:10]}, entfallen {removed[:10]}, geaendert {changed[:10]}; "
        "python scripts/rls_inventory.py ausfuehren und Klassen im Review pruefen"
    )
    assert Counter(t["class"] for t in tables) == Counter(t["class"] for t in INVENTORY["tables"])
