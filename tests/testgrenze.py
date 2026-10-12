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
