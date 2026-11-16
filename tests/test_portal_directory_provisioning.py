"""Safety boundaries of narrowly scoped directory provisioning."""
import pytest
from scripts.provision_portal_directory_reads import TABLES, grant_plan, provision


class Result:
    def __init__(self, value):
        self.value = value

    def one_or_none(self):
        return self.value

    def scalar_one(self):
        return self.value


class Connection:
    def __init__(self, role=(False, True), exists=True):
        self.role, self.exists, self.grants = role, exists, []

    def execute(self, statement, params=None):
        sql = str(statement)
        if "FROM pg_roles" in sql:
            return Result(self.role)
        if "to_regclass" in sql:
            return Result("existing" if self.exists else None)
        if sql.startswith("GRANT"):
            self.grants.append(sql)
        return Result(True)


@pytest.mark.parametrize("role", [None, (True, True), (False, False)])
def test_untrusted_role_never_receives_grants(role):
    conn = Connection(role)
    with pytest.raises(RuntimeError):
        provision(conn, apply=True)
    assert conn.grants == []


def test_missing_source_stops_before_any_grant():
    conn = Connection(exists=False)
    with pytest.raises(RuntimeError):
        provision(conn, apply=True)
    assert conn.grants == []


def test_default_plan_never_applies_changes():
    conn = Connection()
    provision(conn, apply=False)
    assert conn.grants == []


def test_grants_are_reads_for_exact_existing_sources_only():
    conn = Connection()
    provision(conn, apply=True)
    assert set(conn.grants) == set(grant_plan())
    assert {sql.split()[4] for sql in conn.grants if sql.startswith("GRANT SELECT")} == set(TABLES)
    assert all(sql.startswith(("GRANT SELECT ON TABLE ", "GRANT USAGE ON SCHEMA "))
               and sql.endswith(" TO valeo_system") for sql in conn.grants)
