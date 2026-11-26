"""Demo-Mandant: Unit (Mock) + Integration gegen valeo_probe (M7)."""
from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import scripts.demo_mandant as demo


def test_url_bevorzugt_test_database_url(monkeypatch):
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql://u:p@localhost:5432/valeo_probe")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/valeo_neuro_erp")
    assert "valeo_probe" in demo._url()


def test_url_lehnt_nicht_probe_ab(monkeypatch):
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/valeo_neuro_erp")
    monkeypatch.delenv("ALLOW_DEMO_MANDANT_ANY_DB", raising=False)
    with pytest.raises(SystemExit):
        demo._url()


def test_anlegen_und_loeschen_mit_mock_session():
    """Logik ohne echte DB: Mandant fehlt → Insert; Löschen → Delete."""
    db = MagicMock()

    # vorhanden? erst False (anlegen), dann True (nach Insert), für loeschen True dann False-Pfad
    calls = {"n": 0}

    def execute(stmt, params=None):
        sql = str(stmt)
        calls["n"] += 1
        if "information_schema.columns" in sql and "domain" in sql:
            return SimpleNamespace(first=lambda: True)  # hat domain-Spalte
        if "information_schema.tables" in sql and "chart_of_accounts" in sql:
            return SimpleNamespace(first=lambda: False)  # kein Kontenrahmen → überspringen
        if "FROM domain_shared.tenants WHERE id" in sql:
            # erste Prüfung in anlegen: fehlt; in loeschen: vorhanden
            if calls["n"] <= 3:
                return SimpleNamespace(first=lambda: None)
            return SimpleNamespace(first=lambda: (1,))
        return SimpleNamespace(first=lambda: None, rowcount=0)

    db.execute.side_effect = execute

    bericht = demo.anlegen(db)
    assert bericht["mandant"] is True
    assert bericht["konto_8000"] is False
    assert any("INSERT INTO domain_shared.tenants" in str(c.args[0]) for c in db.execute.call_args_list)

    db2 = MagicMock()

    def execute_del(stmt, params=None):
        sql = str(stmt)
        if "information_schema.tables" in sql:
            return SimpleNamespace(first=lambda: False)
        if "FROM domain_shared.tenants WHERE id" in sql:
            return SimpleNamespace(first=lambda: (1,))
        return SimpleNamespace(first=lambda: None, rowcount=0)

    db2.execute.side_effect = execute_del
    geloescht = demo.loeschen(db2)
    assert geloescht["mandant"] is True
    assert any("DELETE FROM domain_shared.tenants" in str(c.args[0]) for c in db2.execute.call_args_list)


@pytest.mark.integration
def test_demo_mandant_anlegen_und_loeschen_gegen_probe(monkeypatch):
    url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL/DATABASE_URL fehlt — Demo-Mandant braucht valeo_probe")
    if "valeo_probe" not in url and os.environ.get("ALLOW_DEMO_MANDANT_ANY_DB") != "1":
        pytest.skip("Demo-Mandant-Test nur gegen valeo_probe (oder ALLOW_DEMO_MANDANT_ANY_DB=1)")

    monkeypatch.setenv("TEST_DATABASE_URL", url if "valeo_probe" in url else url)
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("PGAPPNAME", "agent:test-demo-mandant")

    assert demo.main(["--loeschen"]) == 0
    assert demo.main(["--anlegen"]) == 0
    assert demo.main(["--status"]) == 0
    with demo._session() as db:
        assert demo.vorhanden(db) is True
    assert demo.main(["--loeschen"]) == 0
    with demo._session() as db:
        assert demo.vorhanden(db) is False
