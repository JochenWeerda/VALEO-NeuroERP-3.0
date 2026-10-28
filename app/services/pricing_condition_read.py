"""Tenant-bound read shared by the existing pricing and POS adapters."""
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session


_QUERY = """SELECT k.* FROM domain_shared.zu_abschlag_konditionen k
JOIN domain_shared.zu_abschlaggruppen g ON g.id = k.gruppe_id
WHERE g.tenant_id = :t ORDER BY k.id LIMIT :limit"""


def read_pricing_conditions(db: Session, tenant_id: str, *, limit: int) -> list:
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise HTTPException(status_code=403, detail="Gepruefter Mandant fehlt.")
    if type(limit) is not int or not 1 <= limit <= 200:
        raise ValueError("Condition read limit must be between 1 and 200")
    try:
        return list(db.execute(text(_QUERY), {"t": tenant_id, "limit": limit}).mappings().all())
    except (OperationalError, ProgrammingError) as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Preiskonditionen konnten nicht geladen werden.") from exc
