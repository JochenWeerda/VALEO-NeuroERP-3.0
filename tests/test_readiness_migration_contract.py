"""Readiness uses Alembic's real version table and fails on unmigrated databases."""
import sqlite3
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from app.core import health


@pytest.mark.parametrize("revision,expected", [("test_revision", True), (None, False)])
def test_readiness_against_alembic_version_table(monkeypatch, revision, expected):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
    if revision:
        db.execute("INSERT INTO alembic_version VALUES (?)", (revision,))

    class Connection:
        def execute(self, statement):
            value = db.execute(str(statement)).fetchone()[0]
            return SimpleNamespace(scalar=lambda: value)

    @contextmanager
    def connect():
        yield Connection()

    monkeypatch.setattr(health, "engine", SimpleNamespace(connect=connect))
    try:
        ok, message = health._check_postgresql_sync()
        assert ok is expected
        assert (revision if revision else "No alembic migrations") in message
    finally:
        db.close()
