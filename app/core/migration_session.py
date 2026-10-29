"""Session setup shared by Alembic and scripts/init_db.py (DB-Governance).

- ``migration_database_url``: the migrator login (MIGRATION_DATABASE_URL) for the database that
  DATABASE_URL names; DATABASE_URL always decides the target.
- ``prepare_migration_session``: marks the session for governance.ddl_events and, once the
  roles from scripts/provision_db_roles.py exist, switches to valeo_owner so new objects are
  owned by it instead of the login role (superuser in development).
"""
from __future__ import annotations

import os

from sqlalchemy import text

OWNER_ROLE = "valeo_owner"
_SET_OWNER_ROLE = text("SET ROLE valeo_owner")  # literal: OWNER_ROLE, no interpolation into SQL


def _same_target(left: str, right: str) -> bool:
    from sqlalchemy.engine import make_url

    a, b = make_url(left), make_url(right)
    return (a.host, a.port or 5432, a.database) == (b.host, b.port or 5432, b.database)


def migration_database_url(default: str | None = None) -> str | None:
    """DATABASE_URL decides the target; MIGRATION_DATABASE_URL only supplies the migrator
    login for that same database. A migrator URL for another database (e.g. the development
    database from .env while pruefstand_db.py migrates valeo_probe) is ignored."""
    target = os.getenv("DATABASE_URL")
    migrator = os.getenv("MIGRATION_DATABASE_URL")
    if migrator and (not target or _same_target(migrator, target)):
        return migrator
    return target or default


def owner_role_available(connection) -> bool:
    """valeo_owner exists, the login may act as it, and THIS database is provisioned for it.

    Roles are cluster-wide: a freshly created database (e.g. pruefstand_db.py) knows the role
    but grants it nothing yet; migrating it as valeo_owner would fail on schema public. Such a
    database is migrated by the login role and handed over later by provision_db_roles.py.
    """
    return bool(connection.execute(text(
        "SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :role "
        "AND pg_has_role(current_user, oid, 'MEMBER') "
        "AND has_database_privilege(oid, current_database(), 'CREATE'))"
    ), {"role": OWNER_ROLE}).scalar())


def prepare_migration_session(connection, application_name: str) -> bool:
    """Returns True when the session now acts as valeo_owner."""
    connection.execute(text("SELECT set_config('application_name', :name, false)"), {"name": application_name})
    can_own = owner_role_available(connection)
    if can_own:
        connection.execute(_SET_OWNER_ROLE)
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
