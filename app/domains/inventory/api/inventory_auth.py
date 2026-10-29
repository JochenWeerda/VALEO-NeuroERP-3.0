"""
Inventory-specific authentication and authorization.

Seit 14.10.2026 (CI-GRUEN): Rollen kommen aus der geprueften Anmeldung — den Fachrollen des Hauses
(``LAGER_LESEN``/``LAGER_BEARBEITEN``/``LAGER_ADMIN``, ``admin``) — und nur ergaenzend aus der lokalen
Benutzertabelle (Altbestand ``inventory_manager``/``inventory_user``). Bis dahin liess ein Token mit dem Claim
``token_type == "dev"`` jede Pruefung aus; Dev-Tokens gibt es seit 12.10.2026 nicht mehr, ein solcher Claim haette nur
noch ueber einen fehlkonfigurierten Provider kommen koennen und dann alles geoeffnet. Wer weder eine Fachrolle traegt
noch als aktiver lokaler Benutzer mit Lagerrolle gefuehrt ist, bekommt 403.
"""

import json

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ....auth.oidc import extract_roles
from ....core.config import settings
from ....core.database import get_db
from ....core.security import require_bearer_token
from ....infrastructure.models import User as UserModel

LESEN = frozenset({"admin", "LAGER_LESEN", "LAGER_BEARBEITEN", "LAGER_ADMIN",
                   "inventory_manager", "inventory_user"})
VERWALTEN = frozenset({"admin", "LAGER_ADMIN", "inventory_manager"})


def _rollen(request: Request, db: Session) -> set[str]:
    claims = getattr(request.state, "token_claims", None) or {}
    rollen = set(extract_roles(claims))
    user_id = claims.get("sub") or claims.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")
    if rollen & LESEN:
        return rollen
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User not found or inactive")
    try:
        lokal = json.loads(user.roles or "[]") if isinstance(user.roles or "[]", str) else (user.roles or [])
    except (json.JSONDecodeError, TypeError) as exc:
        raise HTTPException(status_code=403, detail="Invalid user roles configuration") from exc
    return rollen | {str(r) for r in lokal}


def require_inventory_access(
    request: Request,
    token: str = Depends(require_bearer_token),
    db: Session = Depends(get_db)
) -> str:
    """Lagerzugriff: eine Lese-, Bearbeitungs- oder Verwaltungsrolle."""
    if not _rollen(request, db) & LESEN:
        raise HTTPException(status_code=403, detail="Insufficient permissions for inventory access")
    return token


def require_inventory_admin(
    request: Request,
    token: str = Depends(require_inventory_access),
    db: Session = Depends(get_db)
) -> str:
    """Lagerverwaltung: ``LAGER_ADMIN``, ``admin`` oder lokal ``inventory_manager``."""
    if not _rollen(request, db) & VERWALTEN:
        raise HTTPException(status_code=403, detail="Admin permissions required for this operation")
    return token


def get_current_tenant_id(
    request: Request,
    token: str = Depends(require_inventory_access)
) -> str:
    """Der Mandant dieses Requests: der von der Middleware gepruefte ``X-Tenant-ID``.

    Bis 07.10.2026 lieferte diese Funktion beim Dev-Token immer den
    Standardmandanten und ignorierte den Header; jeder Inventar-Weg nahm zudem einen
    ``tenant_id``-Query-Parameter, der den Mandanten ueberschrieb. Wer eine fremde
    Kennung in die URL schrieb, las und buchte im fremden Lager.

    Traegt das Token einen Mandanten, muss er mit dem Kontext uebereinstimmen.
    """
    tenant_id = (
        getattr(request.state, "tenant_id", None)
        or request.headers.get("X-Tenant-ID")
        or ""
    ).strip() or settings.DEFAULT_TENANT_ID

    claims = getattr(request.state, 'token_claims', {}) or {}
    token_tenant = claims.get('tenant_id')
    if token_tenant and token_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied: tenant mismatch")

    return tenant_id


def require_tenant_access(
    tenant_id: str,
    request: Request,
    db: Session = Depends(get_db)
) -> str:
    """Der genannte Mandant muss der des Tokens sein."""
    claims = getattr(request.state, 'token_claims', {}) or {}
    if claims.get('tenant_id') != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied: tenant mismatch")
    return tenant_id
