"""Entscheidungslogik von scripts/check_ddl_provenance.py (ohne Datenbank)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_ddl_provenance import TRIGGERS, bewerte  # noqa: E402

pytestmark = pytest.mark.unit

AKTIV = {name: "O" for name in TRIGGERS}


def _ereignis(source: str, tag: str = "CREATE TABLE") -> dict:
    return {
        "occurred_at": "2026-10-26T08:00:00+00:00", "source": source, "application_name": f"{source}:x",
        "session_role": "valeo_dev", "command_tag": tag, "object_identity": "s.t", "object_type": "table",
    }


def test_missing_log_table_is_exit_2():
    code, befunde = bewerte({"tabelle": False, "trigger": {}, "ereignisse": []}, {"alembic"})
    assert code == 2
    assert "governance_ddl_log_20261026" in befunde[0]


def test_missing_or_disabled_trigger_is_exit_2():
    code, befunde = bewerte({"tabelle": True, "trigger": {TRIGGERS[0]: "D"}, "ereignisse": []}, {"alembic"})
    assert code == 2
    assert any("fehlen" in b for b in befunde)
    assert any("deaktiviert" in b for b in befunde)


def test_only_allowed_sources_pass():
    zustand = {"tabelle": True, "trigger": AKTIV, "ereignisse": [_ereignis("alembic"), _ereignis("drizzle-kit")]}
    assert bewerte(zustand, {"alembic", "drizzle-kit"}) == (0, [])


def test_foreign_sources_are_listed_with_role_and_object():
    zustand = {"tabelle": True, "trigger": AKTIV,
               "ereignisse": [_ereignis("alembic"), _ereignis("unbekannt", "DROP TABLE"), _ereignis("agent")]}
    code, befunde = bewerte(zustand, {"alembic"})
    assert code == 1
    assert len(befunde) == 2
    assert "unbekannt" in befunde[0] and "DROP TABLE s.t" in befunde[0] and "Rolle valeo_dev" in befunde[0]
