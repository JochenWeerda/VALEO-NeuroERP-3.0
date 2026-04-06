"""
Zentrale Test-Fixtures für VALEO NeuroERP 3.0.

- Setzt API_DEV_TOKEN automatisch für alle Tests (kein Keycloak nötig).
- Stellt skip_if_db_unavailable() als Hilfsfunktion bereit.
"""

import pytest

from app.core.config import settings
from app.core import security


@pytest.fixture(autouse=True)
def _enable_dev_token(monkeypatch):
    """Aktiviert den Dev-Token-Bypass in allen Tests."""
    monkeypatch.setattr(settings, "API_DEV_TOKEN", "dev-token")
    monkeypatch.setattr(security.settings, "API_DEV_TOKEN", "dev-token")


def skip_if_db_unavailable(response):
    """Skipt den Test wenn PostgreSQL nicht erreichbar ist (500/503 mit Connection refused)."""
    if response.status_code in (500, 503):
        body = response.text
        if "OperationalError" in body or "Connection refused" in body:
            pytest.skip("PostgreSQL nicht erreichbar — docker compose up erforderlich")


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
        pytest.skip("PostgreSQL nicht erreichbar — docker compose up erforderlich")
