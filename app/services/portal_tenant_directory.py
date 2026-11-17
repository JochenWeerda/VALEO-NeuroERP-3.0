"""Read-only directory of the authenticated person's own portal trade partners.

The directory does not switch the request tenant or grant access to its data.
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import bindparam, text

from app.auth.portal_kunde import NUR_DURCH_DAS_HAUS, PORTAL_RECHTE, UEBERSICHT
from app.auth.tenant import tenant_from_claims
from app.core.config import settings
from app.core.database import system_session
from app.core.tenant_context import cross_tenant_scope

MAX_TENANTS = 100
_DIRECTORY_ROLES = tuple(sorted(
    rolle for rolle, rechte in PORTAL_RECHTE.items()
    if UEBERSICHT in rechte and rolle not in NUR_DURCH_DAS_HAUS
))
_QUERY = text("""
    SELECT t.id, t.name, count(DISTINCT c.id) AS customer_count
    FROM domain_portal.kundenzugaenge z
    JOIN domain_crm.customers c ON c.id = z.customer_id AND c.tenant_id = z.tenant_id
    JOIN domain_shared.tenants t ON t.id = z.tenant_id
    WHERE z.subject = :subject AND z.widerrufen_am IS NULL
      AND (z.gueltig_bis IS NULL OR z.gueltig_bis > now())
      AND c.deleted_at IS NULL AND t.is_active IS TRUE AND z.rolle IN :roles
    GROUP BY t.id, t.name
    ORDER BY t.name, t.id
    LIMIT :limit
""").bindparams(bindparam("roles", expanding=True))


def eigene_handelspartner(user: dict) -> list[dict]:
    """List own eligible tenants; ``user`` must come from verified get_current_user."""
    subject = user.get("sub") if isinstance(user, dict) else None
    raw = user.get("raw") if isinstance(user, dict) else None
    if (not isinstance(subject, str) or not subject.strip() or not isinstance(raw, dict)
            or raw.get("sub") != subject or not tenant_from_claims(raw)):
        raise HTTPException(status_code=403, detail="Gepruefte Anmeldung erforderlich")
    if not settings.SYSTEM_DATABASE_URL:
        raise HTTPException(status_code=503, detail="Handelspartnerverzeichnis nicht verfuegbar")

    try:
        with cross_tenant_scope("portal: eigene Handelspartner auflisten"):
            db = system_session()
            try:
                db.execute(text("SET TRANSACTION READ ONLY"))
                role = db.execute(text(
                    "SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user"
                )).one()
                if role[0] != "valeo_system" or role[1] is not False or role[2] is not True:
                    raise RuntimeError("Unexpected system role")
                rows = db.execute(_QUERY, {"subject": subject, "roles": _DIRECTORY_ROLES,
                                           "limit": MAX_TENANTS + 1}).all()
                if len(rows) > MAX_TENANTS:
                    raise RuntimeError("Directory limit exceeded")
                tenant = tenant_from_claims(raw)
                return [{"id": row[0], "name": row[1], "customer_count": row[2], "active": row[0] == tenant}
                        for row in rows]
            finally:
                try:
                    db.rollback()
                finally:
                    db.close()
    except Exception:
        raise HTTPException(status_code=503, detail="Handelspartnerverzeichnis nicht verfuegbar") from None
