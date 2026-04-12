"""
Zentrale Test-Fixtures für VALEO NeuroERP 3.0.

- Setzt API_DEV_TOKEN automatisch für alle Tests (kein Keycloak nötig).
- Stellt skip_if_db_unavailable() als Hilfsfunktion bereit.
- Marker needs_live_db: wird Tests zugewiesen, die die Fixture require_db nutzen
  (für CI: pytest -m needs_live_db mit PYTEST_REQUIRE_DB_STRICT=1).
"""

import os

import pytest

from app.core.config import settings
from app.core import security


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """Markiert alle Tests, die die Fixture require_db anfordern (-m needs_live_db)."""
    for item in items:
        fns = getattr(item, "fixturenames", None)
        if not fns:
            continue
        if "require_db" in fns:
            item.add_marker(pytest.mark.needs_live_db)


@pytest.fixture(autouse=True)
def _enable_dev_token(monkeypatch):
    """Aktiviert den Dev-Token-Bypass in allen Tests."""
    monkeypatch.setattr(settings, "API_DEV_TOKEN", "dev-token")
    monkeypatch.setattr(security.settings, "API_DEV_TOKEN", "dev-token")


def skip_if_db_unavailable(response):
    """Skipt den Test wenn PostgreSQL nicht erreichbar ist (500/503 mit Connection refused)."""
    if response.status_code in (500, 503):
        body = response.text
        if any(k in body for k in (
            "OperationalError", "Connection refused",
            "Identity provider unavailable", "UndefinedTable", "does not exist",
        )):
            pytest.skip("DB or identity provider not available")


def _is_db_reachable() -> bool:
    """Prüft ob PostgreSQL erreichbar ist."""
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        return True
    except Exception:
        return False


@pytest.fixture
def require_db():
    """Fixture: skipt den Test wenn die Datenbank nicht erreichbar ist."""
    if not _is_db_reachable():
        if os.environ.get("PYTEST_REQUIRE_DB_STRICT") == "1":
            pytest.fail(
                "PostgreSQL nicht erreichbar (PYTEST_REQUIRE_DB_STRICT=1). "
                "DATABASE_URL prüfen und Schema mit scripts/init_db.py migrieren."
            )
        pytest.skip("PostgreSQL nicht erreichbar — docker compose up erforderlich")
