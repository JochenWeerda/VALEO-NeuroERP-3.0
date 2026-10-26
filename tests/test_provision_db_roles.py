"""Rollenplan von scripts/provision_db_roles.py (ohne Datenbank)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from provision_db_roles import (  # noqa: E402
    AGENT, APP, AUDIT, GOVERNANCE, MIGRATOR, OWNER, grant_statements, ownership_statements, role_statements,
)

pytestmark = pytest.mark.unit


def test_roles_are_created_idempotently_without_superpowers_or_passwords():
    statements = role_statements()
    for role in (OWNER, GOVERNANCE, MIGRATOR, APP, AGENT, AUDIT):
        assert any(f"rolname = '{role}'" in s and "CREATE ROLE" in s for s in statements)
        assert any(s.startswith(f"ALTER ROLE {role} ") and "NOSUPERUSER" in s and "NOBYPASSRLS" in s for s in statements)
    assert f"GRANT {OWNER} TO {MIGRATOR}" in statements
    assert f"ALTER ROLE {MIGRATOR} SET role = '{OWNER}'" in statements
    assert not any("PASSWORD" in s for s in statements)
    assert any(s.startswith(f"ALTER ROLE {OWNER} NOLOGIN") for s in statements)


def test_data_roles_get_dml_but_no_ddl():
    statements = grant_statements("valeo_probe", ["domain_crm"], ["valeo_owner", "valeo_dev"], governance=False)
    data = f"{APP}, {AGENT}"
    assert f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA "domain_crm" TO {data}' in statements
    assert f'GRANT USAGE ON SCHEMA "domain_crm" TO {data}' in statements
    assert f'GRANT USAGE, CREATE ON SCHEMA "domain_crm" TO {OWNER}' in statements
    assert not any("CREATE ON SCHEMA" in s and APP in s for s in statements)
    assert "REVOKE CREATE ON SCHEMA public FROM PUBLIC" in statements
    assert f'GRANT CONNECT, CREATE ON DATABASE "valeo_probe" TO {OWNER}' in statements
    # objects created later by the owner or the development superuser stay usable for the app
    assert any('FOR ROLE "valeo_dev" IN SCHEMA "domain_crm" GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES' in s
               for s in statements)


def test_governance_log_is_insert_only_for_migrators_and_read_only_for_audit():
    statements = grant_statements("valeo_probe", [], ["valeo_owner"], governance=True)
    assert f"ALTER TABLE governance.ddl_events OWNER TO {GOVERNANCE}" in statements
    assert f"GRANT INSERT ON governance.ddl_events TO {OWNER}" in statements
    assert f"GRANT SELECT ON governance.ddl_events TO {AUDIT}" in statements
    assert not any("governance.ddl_events" in s and ("UPDATE" in s or "DELETE" in s) for s in statements)


def test_ownership_moves_to_valeo_owner():
    assert ownership_statements([("TABLE", "domain_crm.customers"), ("SCHEMA", "domain_crm")]) == [
        f"ALTER TABLE domain_crm.customers OWNER TO {OWNER}",
        f"ALTER SCHEMA domain_crm OWNER TO {OWNER}",
    ]
