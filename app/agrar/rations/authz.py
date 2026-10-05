"""Gemeinsame serverseitige Rollenpruefung der Feed-Advice-/Rations-Router.

FEED-ADVICE-ROLES-013: Eine Quelle fuer die Rollen-Sets aller vier Router
(lifecycle, controlling, readiness, integrations). Die Pruefung ist bewusst
schnittstellenarm (User-TypedDict + Set), damit sie in Endpoints ohne
zusaetzliche Dependencies aufrufbar bleibt.
"""
from __future__ import annotations

from fastapi import HTTPException

from app.auth.deps import User

READ_ROLES = {"FUTTERMITTEL_LESEN", "FUTTERMITTEL_BEARBEITEN", "FUTTERMITTEL_ADMIN", "admin", "manager"}
WRITE_ROLES = {"FUTTERMITTEL_BEARBEITEN", "FUTTERMITTEL_ADMIN", "admin", "manager"}
APPROVE_ROLES = {"FUTTERMITTEL_ADMIN", "admin", "manager"}
# Connector-Verwaltung traegt Vertrags-/Consent-/Secret-Konfiguration -> Admin-Level.
CONNECTOR_ADMIN_ROLES = APPROVE_ROLES


def require_roles(user: User, allowed: set[str], detail: str = "Keine Berechtigung fuer diese Futtermittel-Aktion.") -> None:
    """403, wenn der Benutzer keine der erlaubten Rollen traegt."""
    if not set(user.get("roles") or []).intersection(allowed):
        raise HTTPException(status_code=403, detail=detail)
