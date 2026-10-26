"""Session setup shared by Alembic and scripts/init_db.py (DB-Governance).

- ``migration_database_url``: MIGRATION_DATABASE_URL (valeo_migrator) before DATABASE_URL, so
  application and migrations can use separate roles while existing setups keep working.
- ``prepare_migration_session``: marks the session for governance.ddl_events and, once the
  roles from scripts/provision_db_roles.py exist, switches to valeo_owner so new objects are
  owned by it instead of the login role (superuser in development).
"""
from __future__ import annotations

import os

from sqlalchemy import text

OWNER_ROLE = "valeo_owner"


def migration_database_url(default: str | None = None) -> str | None:
    return os.getenv("MIGRATION_DATABASE_URL") or os.getenv("DATABASE_URL") or default


def owner_role_available(connection) -> bool:
    return bool(connection.execute(text(
        "SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :role "
        "AND pg_has_role(current_user, oid, 'MEMBER'))"
    ), {"role": OWNER_ROLE}).scalar())


def prepare_migration_session(connection, application_name: str) -> bool:
    """Returns True when the session now acts as valeo_owner."""
    connection.execute(text("SELECT set_config('application_name', :name, false)"), {"name": application_name})
    can_own = owner_role_available(connection)
    if can_own:
        connection.execute(text(f"SET ROLE {OWNER_ROLE}"))
    return can_own


def migration_engine(url: str, application_name: str):
    """Engine whose every connection is marked and, once provisioned, acts as valeo_owner."""
    from sqlalchemy import create_engine

    probe = create_engine(url)
    try:
        with probe.connect() as connection:
            can_own = owner_role_available(connection)
    finally:
        probe.dispose()
    options = {"application_name": application_name}
    if can_own:
        options["options"] = f"-c role={OWNER_ROLE}"
    return create_engine(url, connect_args=options)
