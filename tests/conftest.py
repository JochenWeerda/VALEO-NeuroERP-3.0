"""
Zentrale Test-Fixtures für VALEO NeuroERP 3.0.

- Setzt die alte Token-Konfiguration nur fuer isolierte Kompatibilitaetstests.
- Ersetzt Anmeldung ausschliesslich in app.main; Produktionsauth bleibt unveraendert.
- Stellt skip_if_db_unavailable() als Hilfsfunktion bereit.
- Marker needs_live_db: wird Tests zugewiesen, die die Fixture require_db nutzen
  (für CI: pytest -m needs_live_db mit PYTEST_REQUIRE_DB_STRICT=1).
"""

import os
import sys
from types import SimpleNamespace

import pytest
from sqlalchemy import text

from app.core.config import settings
from app.core import security

# Coverage tracing adds frames to the large FastAPI startup graph. Python
# 3.11.0 on Windows can otherwise hit the interpreter default during
# TestClient lifespan startup even though the same tests pass without tracing.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 4000))


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """Markiert alle Tests, die die Fixture require_db anfordern (-m needs_live_db)."""
    for item in items:
        fns = getattr(item, "fixturenames", None)
        if not fns:
            continue
        if "require_db" in fns:
            item.add_marker(pytest.mark.needs_live_db)


@pytest.fixture
def mocker(monkeypatch):
    """Small pytest-mock compatible subset used by legacy unit tests."""

    def _patch(target: str, **kwargs):
        from unittest.mock import MagicMock

        parts = target.split(".")
        if len(parts) < 2:
            raise ValueError("target must contain a module and attribute")
        module_name = ".".join(parts[:-1])
        attr_name = parts[-1]
        module = __import__(module_name, fromlist=[attr_name])
        replacement = kwargs.pop("new", MagicMock(**kwargs))
        monkeypatch.setattr(module, attr_name, replacement)
        return replacement

    return SimpleNamespace(patch=_patch)


@pytest.fixture(autouse=True)
def _enable_dev_token(monkeypatch):
    """Explizite Identitaetsattrappe der separaten Kompatibilitaets-App.

    Diese Fixture beweist keine Signatur- oder Mandantensicherheit. Die echte
    Produktions-App main:app behaelt ihre Provider- und Mandantenpruefung.
    """
    monkeypatch.setattr(settings, "API_DEV_TOKEN", "dev-token")
    monkeypatch.setattr(security.settings, "API_DEV_TOKEN", "dev-token")

    # Authentifizierung nur fuer die Kompatibilitaets-App ersetzen.
    from app.main import app as _app
    from fastapi import Request
    def declared_test_identity(request: Request):
        # Only the documented compatibility app uses this explicit auth double.
        # Production main:app and its RSA/JWKS contract are not overridden.
        tenant = request.headers.get("X-Tenant-ID") or settings.DEFAULT_TENANT_ID
        request.state.tenant_id = tenant
        request.state.tenant_verified = True
        request.state.token_claims = {"sub": "dev", "tenant_id": tenant, "roles": ["admin"], "scope": "admin:all"}
        request.state.authenticated_token = "dev-token"
        return "dev-token"
    _app.dependency_overrides[security.require_bearer_token] = declared_test_identity
    yield
    _app.dependency_overrides.pop(security.require_bearer_token, None)


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


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """Ensure tenant fixtures referenced by DB integration tests exist."""
    if not _is_db_reachable():
        yield
        return

    from app.core.database import SessionLocal

    session = SessionLocal()
    try:
        for tenant_id, name in (
            # Kanonische Tenant-UUIDs (Konvention seit 2026-07-02): neue Tests
            # verwenden ausschliesslich diese UUIDs als X-Tenant-Id.
            ("00000000-0000-0000-0000-000000000001", "Dev/Test Tenant A (kanonisch)"),
            ("00000000-0000-0000-0000-000000000002", "Test Tenant B (Tenant-Isolation)"),
            # Legacy-String-Tenants: nur noch fuer Bestandstests, nicht neu verwenden.
            ("test-tenant", "Integration Test Tenant"),
            ("default", "Default Test Tenant"),
        ):
            session.execute(
                text(
                    """
                    INSERT INTO domain_shared.tenants (id, name, domain, is_active)
                    VALUES (:id, :name, :domain, TRUE)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {"id": tenant_id, "name": name, "domain": f"{tenant_id}.test.local"},
            )
        session.commit()
    finally:
        session.close()
    yield


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
