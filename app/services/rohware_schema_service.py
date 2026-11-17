"""Rohware settlement schema: one tenant-bound catalog and lifecycle."""
from datetime import date, datetime
from typing import Any
from uuid import uuid4

from app.core.business_time import business_today
from fastapi import HTTPException
from sqlalchemy import text

HEAD = "domain_shared.rohware_abrechnungsschemata"
GROUPS = "domain_shared.rohwarengruppen"
LINES = "domain_shared.rohware_schema_lines"



def validate_header(payload: dict[str, Any], *, create: bool = False, existing=None) -> None:
    """Validate known fields without echoing supplied values in errors."""
    limits = {"schema_code": 20, "name": 200, "gruppe_id": 128, "rohwaren_gruppe": 20}
    for field, maximum in limits.items():
        if field in payload:
            value = payload[field]
            if not isinstance(value, str) or not value.strip() or len(value) > maximum:
                raise HTTPException(422, detail=f"{field} ist ungültig")
    if create and "name" not in payload:
        raise HTTPException(422, detail="name ist erforderlich")
    if create and not ("gruppe_id" in payload or "rohwaren_gruppe" in payload):
        raise HTTPException(422, detail="Rohwarengruppe erforderlich")
    if "gruppe_id" in payload and "rohwaren_gruppe" in payload:
        raise HTTPException(422, detail="Rohwarengruppe nur einmal angeben")
    if "version" in payload:
        version = payload["version"]
        if type(version) is not int or not 1 <= version <= 2147483647:
            raise HTTPException(422, detail="version ist ungültig")
    dates = {}
    for field in ("gueltig_ab", "gueltig_bis"):
        value = payload.get(field) if field in payload else (existing.get(field) if existing else None)
        if value is None:
            dates[field] = None
        elif isinstance(value, date) and not isinstance(value, datetime):
            dates[field] = value
        elif isinstance(value, str):
            try:
                parsed = date.fromisoformat(value)
                if parsed.isoformat() != value:
                    raise ValueError
                dates[field] = parsed
            except ValueError:
                raise HTTPException(422, detail=f"{field} ist ungültig") from None
        else:
            raise HTTPException(422, detail=f"{field} ist ungültig")
    if dates["gueltig_ab"] and dates["gueltig_bis"] and dates["gueltig_bis"] < dates["gueltig_ab"]:
        raise HTTPException(422, detail="Gültigkeitszeitraum ist ungültig")

def group_id(db, tenant_id, *, group_id=None, group_code=None):
    if not group_id and not group_code:
        raise HTTPException(422, "Rohwarengruppe erforderlich")
    if group_id and group_code:
        raise HTTPException(422, "Rohwarengruppe nur einmal angeben")
    query = ("SELECT id FROM domain_shared.rohwarengruppen WHERE tenant_id = :tenant_id AND id = :value"
             if group_id else
             "SELECT id FROM domain_shared.rohwarengruppen WHERE tenant_id = :tenant_id AND gruppe_nr = :value")
    row = db.execute(text(query),
                     {"tenant_id": tenant_id, "value": group_id or group_code}).fetchone()
    if not row:
        raise HTTPException(404, "Rohwarengruppe nicht gefunden")
    return row[0]


def create(db, tenant_id, *, schema_code, name, group, valid_from=None,
           valid_until=None, version=1, article=None, activate=False):
    validate_header({"schema_code": schema_code, "name": name, "version": version,
                     "gueltig_ab": valid_from, "gueltig_bis": valid_until})
    identifier = str(uuid4())
    valid_from = valid_from or (business_today() if activate else None)
    if activate and not valid_from:
        raise HTTPException(422, "gueltig_ab erforderlich")
    db.execute(text("""INSERT INTO domain_shared.rohware_abrechnungsschemata
        (id, tenant_id, schema_nr, bezeichnung, gruppe_id, artikel_nr,
         gueltig_ab, gueltig_bis, version, status, aktiv)
        VALUES (:id, :tenant_id, :code, :name, :group_id, :article,
                :valid_from, :valid_until, :version, :status, :active)"""),
        {"id": identifier, "tenant_id": tenant_id, "code": schema_code, "name": name,
         "group_id": group, "article": article, "valid_from": valid_from,
         "valid_until": valid_until, "version": version,
         "status": "AKTIV" if activate else "ENTWURF", "active": activate})
    return identifier


def transition(db, tenant_id, schema_id, target):
    source = {"AKTIV": "ENTWURF", "ARCHIV": "AKTIV"}[target]
    row = db.execute(text("SELECT status, gueltig_ab FROM domain_shared.rohware_abrechnungsschemata WHERE id = :id AND tenant_id = :tenant_id FOR UPDATE"),
                     {"id": schema_id, "tenant_id": tenant_id}).mappings().fetchone()
    if not row:
        raise HTTPException(404, "Schema nicht gefunden")
    if row["status"] != source:
        raise HTTPException(422, "Statusübergang nicht zulässig")
    if target == "AKTIV" and not row["gueltig_ab"]:
        raise HTTPException(422, "gueltig_ab muss gesetzt sein")
    db.execute(text("UPDATE domain_shared.rohware_abrechnungsschemata SET status = :status, aktiv = :active, updated_at = NOW() WHERE id = :id AND tenant_id = :tenant_id"),
               {"status": target, "active": target == "AKTIV", "id": schema_id, "tenant_id": tenant_id})
