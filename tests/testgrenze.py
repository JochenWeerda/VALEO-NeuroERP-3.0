"""Ausdrueckliche Testgrenze fuer Mini-Anwendungen: wer angemeldet ist und fuer welchen Mandanten.

Seit 12.10.2026 kommt der Mandant nur noch aus der geprueften Anmeldung (``get_tenant_id`` haengt am
Bearer-Token), und die Finanzwege pruefen eine Rolle. Ein Test, der einen einzelnen Router in eine
leere FastAPI-Anwendung haengt, hat weder das eine noch das andere — er muss beides ausdruecklich
ersetzen. Das gehoert in den Pruefstand und nirgends sonst hin.

Diese Ersetzung beweist nichts ueber Anmeldung oder Mandantentrennung. Die prueft
``tests/test_mandant_token_bindung.py`` und die Identitaetsvertraege.
"""

from __future__ import annotations

from fastapi import FastAPI, Request

from app.auth.deps import get_current_user
from app.core.config import settings
from app.core.tenant import get_tenant_id


def mandant_aus_kopf(request: Request) -> str:
    """Der Mandant, den der Test im Kopf nennt — fuer Tests, die zwei Mandanten gegeneinander pruefen."""
    return (request.headers.get("X-Tenant-ID") or "").strip() or settings.DEFAULT_TENANT_ID


def ersetze_mandant(app: FastAPI, mandant: str | None = None) -> None:
    """Fester Mandant, oder ohne Angabe der aus dem Kopf der Testanfrage."""
    app.dependency_overrides[get_tenant_id] = (lambda: mandant) if mandant else mandant_aus_kopf


def ersetze_nutzer(app: FastAPI, *rollen: str) -> None:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "5f0c2a9e", "name": "t.de-vries", "roles": list(rollen)}


def ersetze_bearer(app: FastAPI, *rollen: str) -> None:
    """Fuer Mini-Apps, die ``require_bearer_token`` selbst an einen Router haengen: die Pruefung ausdruecklich
    ersetzen und Mandant/Rolle so in den Request-Zustand legen, wie es die echte Pruefung taete."""
    from app.core.security import require_bearer_token

    def identitaet(request: Request) -> str:
        tenant = mandant_aus_kopf(request)
        request.state.tenant_id = tenant
        request.state.tenant_verified = True
        request.state.token_claims = {"sub": "5f0c2a9e", "tenant_id": tenant, "roles": list(rollen)}
        return "testgrenze"

    app.dependency_overrides[require_bearer_token] = identitaet
    # Rollen-Abhaengigkeiten (require_roles) lesen den Nutzer; er traegt dieselbe Identitaet und dieselben Rollen.
    app.dependency_overrides[get_current_user] = lambda: {"sub": "5f0c2a9e", "name": "t.de-vries", "roles": list(rollen)}


def _alle_fachrollen() -> tuple[str, ...]:
    """Alle Fachrollen, die der Code prueft (config/keycloak/fachrollen.json), plus admin/manager/user.

    Ersatz fuer das mit dem Dev-Token entfernte ``app.auth.deps._DEV_ROLES``: ein Testnutzer, der jede Fachrolle hat.
    """
    import json
    from pathlib import Path

    datei = Path(__file__).resolve().parents[1] / "config" / "keycloak" / "fachrollen.json"
    rollen = [r["name"] for r in json.loads(datei.read_text(encoding="utf-8"))["rollen"]]
    return ("admin", "manager", "user", *rollen)


ALLE_FACHROLLEN = _alle_fachrollen()


def pruefstand_erlaubt(url) -> bool:
    """Schreibende Datenbanktests nur gegen den Pruefstand ``valeo_probe``, eine Test-Datenbank oder — in CI — die
    erklaerte Job-Datenbank (``TEST_DATABASE_URL``/``DATABASE_URL``). Nie gegen die Entwicklungsdatenbank.

    Bis 14.10.2026 stand in elf Tests ein fester Name; in CI heisst die eigens angelegte Job-Datenbank anders, die
    Tests brachen dort im Setup ab.
    """
    import os

    from sqlalchemy.engine import make_url

    ziel = url if hasattr(url, "database") else make_url(str(url))
    name = (ziel.database or "").lower()
    if name == "valeo_probe" or "test" in name:
        return True
    if os.environ.get("CI", "").lower() == "true":
        erklaert = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
        return bool(erklaert) and make_url(erklaert).database == ziel.database
    return False


def setze_identitaet(app: FastAPI, sub: str = "5f0c2a9e", *rollen: str) -> None:
    """Fuer Mini-Apps ohne Bearer-Pruefung: die geprueften Claims so in den Request legen, wie es
    ``require_bearer_token`` taete. Ersetzt den frueheren Kopf ``X-User-ID`` (kein Weg liest ihn mehr)."""

    @app.middleware("http")
    async def _identitaet(request: Request, call_next):  # noqa: ANN001, ANN202
        request.state.token_claims = {"sub": sub, "roles": list(rollen)}
        return await call_next(request)
