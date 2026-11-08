"""Is row-level security effective for this connection? (RLS plan P7)

Policies bind nobody who connects as superuser, with BYPASSRLS, or as (a member of) the table
owner valeo_owner. docker-compose falls back to the superuser when
VALEO_APP_CONTAINER_DATABASE_URL is missing, which silently switches RLS off. The check runs at
startup: production refuses to start, development logs an error and sets a metric.
"""

from __future__ import annotations

import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)

OWNER_ROLE = "valeo_owner"

def rls_problems(conn) -> list[str]:
    name, superuser, bypass = conn.execute(
        text("SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")
    ).one()
    owner = conn.execute(
        text("SELECT pg_has_role(current_user, :o, 'MEMBER') "
             "WHERE EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :o)"),
        {"o": OWNER_ROLE},
    ).scalar()
    problems = []
    if superuser:
        problems.append(f"{name} ist Superuser")
    if bypass:
        problems.append(f"{name} hat BYPASSRLS")
    if owner:
        problems.append(f"{name} ist Mitglied von {OWNER_ROLE} (Tabelleneigentuemer)")
    return problems


def enforce_rls_effective(engine, app_env: str) -> list[str]:
    from app.core.metrics import rls_ineffective_connection

    with engine.connect() as conn:
        problems = rls_problems(conn)
    rls_ineffective_connection.set(1 if problems else 0)
    if not problems:
        logger.info("RLS wirksam: Anwendungsrolle ohne Superuser/BYPASSRLS/Eigentuemerrechte")
        return problems
    message = "RLS UNWIRKSAM: " + "; ".join(problems) + " (VALEO_APP_CONTAINER_DATABASE_URL pruefen)"
    if app_env == "production":
        raise RuntimeError(message)
    logger.error(message)
    return problems
