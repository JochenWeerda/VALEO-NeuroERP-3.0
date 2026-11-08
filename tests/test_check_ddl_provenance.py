"""Entscheidungslogik von scripts/check_ddl_provenance.py (ohne Datenbank)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_ddl_provenance import TRIGGERS, bewerte  # noqa: E402

pytestmark = pytest.mark.unit

AKTIV = {name: "O" for name in TRIGGERS}


def _ereignis(source: str, tag: str = "CREATE TABLE", session: str = "valeo_dev",
              current: str | None = None, superuser: bool = True) -> dict:
    return {
        "occurred_at": "2026-10-26T08:00:00+00:00", "source": source, "application_name": f"{source}:x",
        "session_role": session, "current_role_name": current or session, "session_super": superuser,
        "command_tag": tag, "object_identity": "s.t", "object_type": "table",
    }


def test_missing_log_table_is_exit_2():
    code, befunde, _ = bewerte({"tabelle": False, "trigger": {}, "ereignisse": []}, {"alembic"})
    assert code == 2
    assert "governance_ddl_log_20261026" in befunde[0]


def test_missing_or_disabled_trigger_is_exit_2():
    code, befunde, _ = bewerte({"tabelle": True, "trigger": {TRIGGERS[0]: "D"}, "ereignisse": []}, {"alembic"})
    assert code == 2
    assert any("fehlen" in b for b in befunde)
    assert any("deaktiviert" in b for b in befunde)


def test_only_allowed_sources_pass():
    zustand = {"tabelle": True, "trigger": AKTIV, "ereignisse": [_ereignis("alembic"), _ereignis("drizzle-kit")]}
    assert bewerte(zustand, {"alembic", "drizzle-kit"}) == (0, [], [])


def test_foreign_sources_are_listed_with_role_and_object():
    zustand = {"tabelle": True, "trigger": AKTIV,
               "ereignisse": [_ereignis("alembic"), _ereignis("unbekannt", "DROP TABLE"), _ereignis("agent")]}
    code, befunde, _ = bewerte(zustand, {"alembic"})
    assert code == 1
    assert len(befunde) == 2
    assert "unbekannt" in befunde[0] and "DROP TABLE s.t" in befunde[0] and "Rolle valeo_dev" in befunde[0]


def _mit_rollen(*ereignisse: dict) -> dict:
    return {"tabelle": True, "trigger": AKTIV, "ereignisse": list(ereignisse), "rollen_eingerichtet": True}


def test_with_roles_the_acting_role_decides_not_the_declared_source():
    # superuser acting as valeo_owner (SET ROLE) and a migrator login are fine, even as 'unbekannt'
    zustand = _mit_rollen(
        _ereignis("alembic", current="valeo_owner"),
        _ereignis("unbekannt", session="valeo_migrator", superuser=False),
    )
    assert bewerte(zustand, {"alembic"}) == (0, [], [])


def test_with_roles_direct_superuser_ddl_is_a_hint_or_with_flag_a_finding():
    zustand = _mit_rollen(_ereignis("agent"))
    code, befunde, hinweise = bewerte(zustand, {"alembic"})
    assert (code, befunde) == (0, []) and "superuser/agent" in hinweise[0]
    code, befunde, _ = bewerte(zustand, {"alembic"}, superuser_erlaubt=False)
    assert code == 1 and "superuser/agent" in befunde[0]


def test_with_roles_a_tool_source_without_migrator_role_is_spoofed():
    zustand = _mit_rollen(
        _ereignis("alembic", session="valeo_app", superuser=False),
        _ereignis("agent", session="valeo_agent", superuser=False),
    )
    code, befunde, _ = bewerte(zustand, {"alembic", "agent"})
    assert code == 1
    assert "vorgetaeuscht alembic" in befunde[0]
    assert "DDL ohne Migratorrolle (agent)" in befunde[1]
