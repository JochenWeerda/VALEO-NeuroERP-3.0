"""RLS-Domains: Entscheidungsmatrix und eingefrorene Ausnahmeliste.

Jede Mandantentabelle ohne RLS (Klasse A/B ohne Policy, Klasse C) steht mit Ursache in
docs/admin/rls-exceptions.json. Eine neue ungeschuetzte Tabelle fehlt dort und macht den
Test rot; eine abgesicherte muss aus der Liste. Anders als ``pending`` in rls-rollout.json
waechst die Liste nicht von selbst mit, wenn neuer Code einen Rueckfall mitbringt.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rls_domain_matrix as matrix  # noqa: E402

pytestmark = pytest.mark.unit

EXCEPTIONS = json.loads((ROOT / "docs" / "admin" / "rls-exceptions.json").read_text(encoding="utf-8"))
INVENTORY = json.loads(matrix.INVENTORY.read_text(encoding="utf-8"))
# Obergrenze im Test selbst: die Liste zu verlaengern braucht zwei bewusste Aenderungen.
HOECHSTENS_ZURUECKGESTELLT = 76


def test_matrix_ist_aktuell():
    text, markdown = matrix._render_all()
    assert matrix.OUTPUT.read_text(encoding="utf-8") == text, "python scripts/rls_domain_matrix.py ausfuehren"
    assert matrix.MARKDOWN.read_text(encoding="utf-8") == markdown, "python scripts/rls_domain_matrix.py ausfuehren"


def test_jede_ungeschuetzte_mandantentabelle_ist_ausdruecklich_zurueckgestellt():
    unprotected = {t["table"] for t in matrix.scope_tables(INVENTORY)}
    listed = set(EXCEPTIONS["zurueckgestellt"])
    assert not unprotected - listed, f"neu und ungeschuetzt: {sorted(unprotected - listed)[:10]}"
    assert not listed - unprotected, f"abgesichert oder entfernt, bitte austragen: {sorted(listed - unprotected)[:10]}"
    assert len(listed) <= HOECHSTENS_ZURUECKGESTELLT


def test_ausnahmen_nennen_eine_bekannte_ursache():
    assert set(EXCEPTIONS["zurueckgestellt"].values()) <= set(matrix.URSACHEN)
    assert all(reason.strip() for reason in EXCEPTIONS["system_lesbar"].values())


def test_matrix_deckt_genau_die_ausnahmen():
    rows = json.loads(matrix.OUTPUT.read_text(encoding="utf-8"))["tables"]
    assert {r["table"] for r in rows} == set(EXCEPTIONS["zurueckgestellt"])


def test_analyse_selbsttest():
    inventory = {"tables": [
        {"table": "domain_x.kopf", "class": "A", "rls": False, "tenant_type": "character varying"},
        {"table": "domain_x.position", "class": "C", "rls": False, "tenant_type": None,
         "tenant_parents": ["domain_x.kopf"]},
        {"table": "domain_x.stamm", "class": "B", "rls": False, "tenant_type": "text"},
        {"table": "domain_x.fertig", "class": "A", "rls": True, "tenant_type": "text"},
        {"table": "public.svc_items", "class": "A", "rls": False, "tenant_type": "text"},
    ]}
    rollout = {"pending": {"domain_x.kopf": ["standardmandant"], "public.svc_items": ["dienst"]}}
    files = [
        ("app/api/kopf.py", "tid = settings.DEFAULT_TENANT_ID\ndb.execute('INSERT INTO domain_x.kopf VALUES (1)')"),
        ("app/workers/sync_worker.py", "q = 'SELECT * FROM domain_x.position'"),
        ("app/services/stamm.py",
         "from app.core.tenant import get_tenant_id\n"
         "q = 'SELECT * FROM domain_x.stamm WHERE tenant_id IS NULL OR tenant_id = :t'"),
        ("services/svc/models.py", "class Item(Base):\n    __tablename__ = 'svc_items'"),
    ]
    data = {"tables": {"domain_x.stamm": {"zeilen": 3, "null": 2, "default": 0, "system": 0, "mandanten": 1}}}
    rows = {r["table"]: r for r in matrix.analyse(inventory, rollout, data, files)["tables"]}
    assert set(rows) == {"domain_x.kopf", "domain_x.position", "domain_x.stamm", "public.svc_items"}
    assert rows["domain_x.kopf"]["ursache"] == "standardmandant"
    assert rows["domain_x.kopf"]["schreiber"] == ["app/api/kopf.py"]
    assert rows["domain_x.kopf"]["standardmandant_stellen"] == ["app/api/kopf.py:1"]
    assert rows["domain_x.position"]["ursache"] == "position"
    assert rows["domain_x.position"]["worker"] == ["app/workers/sync_worker.py"]
    assert "tenant_id aus domain_x.kopf" in rows["domain_x.position"]["policy"]
    assert rows["domain_x.stamm"]["ursache"] == "referenzdaten"
    assert rows["domain_x.stamm"]["identitaet"] == {"token": 1}
    assert any("2 Zeilen ohne Mandant" in s for s in rows["domain_x.stamm"]["bereinigung"])
    assert rows["public.svc_items"]["ursache"] == "dienst"
    assert rows["public.svc_items"]["policy"].startswith("keine")
