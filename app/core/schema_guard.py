"""Existence checks for tables that migrations own.

The application connects as valeo_app without CREATE rights (DB-Governance); code paths that
used to create their tables on demand now check that the migration ran and fail with a clear
message instead of an opaque permission error.
"""
from __future__ import annotations

from sqlalchemy import text


class MissingSchemaError(RuntimeError):
    """A table that a migration should have created is missing."""


def require_tables(db, tables: tuple[str, ...], migration: str) -> None:
    missing = [name for name in tables if db.execute(text("SELECT to_regclass(:name)"), {"name": name}).scalar() is None]
    if missing:
        raise MissingSchemaError(
            f"Tabellen fehlen: {', '.join(missing)}. Sie entstehen durch die Migration {migration}; "
            "bitte 'alembic upgrade head' bzw. scripts/init_db.py ausfuehren."
        )
