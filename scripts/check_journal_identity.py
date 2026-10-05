"""Read-only runtime gate for tenant-scoped journal identity.

Use the configured existing DATABASE_URL or TEST_DATABASE_URL. No migrations,
row scans, test databases, containers or repair operations are performed.
"""
import os
import sys

from sqlalchemy import create_engine, inspect


def violations(conn, schema="domain_erp"):
    inspector = inspect(conn)
    columns = {c["name"]: c for c in inspector.get_columns("journal_entries", schema=schema)}
    problems = []
    if "tenant_id" not in columns or columns["tenant_id"]["nullable"]:
        problems.append("Journal tenant_id must exist and be NOT NULL")
    if "entry_number" not in columns or columns["entry_number"]["nullable"]:
        problems.append("Journal entry_number must exist and be NOT NULL")
    keys = [c["column_names"] for c in inspector.get_unique_constraints("journal_entries", schema=schema)]
    keys += [i["column_names"] for i in inspector.get_indexes("journal_entries", schema=schema) if i["unique"]]
    if ["entry_number"] in keys:
        problems.append("Global journal entry_number uniqueness is still active")
    if not any(len(key) == 2 and set(key) == {"tenant_id", "entry_number"} for key in keys):
        problems.append("Tenant-scoped journal number uniqueness is missing")
    return problems


def main():
    raw = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not raw:
        print("FAIL: existing database URL required", file=sys.stderr)
        return 1
    engine = None
    try:
        engine = create_engine(raw, connect_args={"options": "-c statement_timeout=5000"})
        with engine.connect() as conn:
            problems = violations(conn)
        for problem in problems:
            print("FAIL:", problem)
        if not problems:
            print("PASS: required tenant and tenant-scoped journal identity")
        return int(bool(problems))
    except Exception:
        # Do not print a connection URL, SQL, or credentials from driver errors.
        print("FAIL: journal identity could not be verified", file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
