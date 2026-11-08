"""Zielwahl von app.core.migration_session (ohne Datenbank)."""
from __future__ import annotations

import pytest

from app.core.migration_session import migration_database_url

pytestmark = pytest.mark.unit

DEV = "postgresql://valeo_dev:x@127.0.0.1:5432/valeo_neuro_erp"
MIGRATOR_DEV = "postgresql://valeo_migrator:y@127.0.0.1:5432/valeo_neuro_erp"
PROBE = "postgresql://valeo_dev:x@127.0.0.1:5432/valeo_probe"


def test_migrator_login_is_used_for_the_same_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", DEV)
    monkeypatch.setenv("MIGRATION_DATABASE_URL", MIGRATOR_DEV)
    assert migration_database_url() == MIGRATOR_DEV


def test_database_url_decides_the_target(monkeypatch):
    # pruefstand_db.py sets DATABASE_URL to valeo_probe while .env names the development migrator
    monkeypatch.setenv("DATABASE_URL", PROBE)
    monkeypatch.setenv("MIGRATION_DATABASE_URL", MIGRATOR_DEV)
    assert migration_database_url() == PROBE


def test_fallbacks(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MIGRATION_DATABASE_URL", MIGRATOR_DEV)
    assert migration_database_url() == MIGRATOR_DEV
    monkeypatch.delenv("MIGRATION_DATABASE_URL")
    assert migration_database_url("postgresql://d/x") == "postgresql://d/x"
