"""The lead mask and qualification use the INTERESSENT-IST-LEAD register."""
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.services.interessent_service import STAENDE

FIELDS = {
    "company_name": "company", "contact_person": "contact_person", "email": "email",
    "phone": "phone", "source": "source", "status": "status", "priority": "priority",
    "estimated_value": "potential", "assigned_to": "assigned_to",
}


def get_row(db: Session, tenant_id: str, lead_id: str, *, lock: bool = False):
    query = "SELECT * FROM public.crm_leads WHERE id::text = :id AND tenant_id = :tid FOR UPDATE" if lock else "SELECT * FROM public.crm_leads WHERE id::text = :id AND tenant_id = :tid"
    row = db.execute(text(query), {"id": lead_id, "tid": tenant_id}).mappings().first()
    if not row:
        raise HTTPException(404, "Lead nicht gefunden")
    return dict(row)


def project(row: dict) -> dict:
    return {
        "id": str(row["id"]), "tenant_id": row["tenant_id"],
        **{key: row.get(column) for key, column in FIELDS.items()},
        "source": row.get("source") or "unknown", "priority": row.get("priority") or "medium",
        "created_at": row.get("created_at"), "updated_at": row.get("updated_at"),
        "qualified_opportunity_id": row.get("qualified_opportunity_id"),
    }


def validate_fields(data: dict) -> dict:
    data = {key: value for key, value in data.items() if key in FIELDS}
    if "status" in data:
        data["status"] = (data["status"] or "NEW").upper()
        if data["status"] not in STAENDE:
            raise HTTPException(422, "Unbekannter Lead-Status")
    return data


def list_rows(db: Session, tenant_id: str, status: str | None, search: str | None, skip: int, limit: int):
    status = validate_fields({"status": status})["status"] if status else None
    params = {"tid": tenant_id, "status": status, "search": f"%{search}%" if search else None, "skip": skip, "limit": limit}
    total = db.execute(text("SELECT COUNT(*) FROM public.crm_leads WHERE tenant_id = :tid AND (:status IS NULL OR status = :status) AND (:search IS NULL OR company ILIKE :search OR contact_person ILIKE :search)"), params).scalar_one()
    rows = db.execute(text("SELECT * FROM public.crm_leads WHERE tenant_id = :tid AND (:status IS NULL OR status = :status) AND (:search IS NULL OR company ILIKE :search OR contact_person ILIKE :search) ORDER BY created_at DESC NULLS LAST, id LIMIT :limit OFFSET :skip"), params).mappings().all()
    return [project(dict(row)) for row in rows], total


def create(db: Session, tenant_id: str, data: dict) -> dict:
    data = validate_fields(data)
    columns = [FIELDS[key] for key in data]
    values = [":" + key for key in data]
    row = db.execute(text(
        "INSERT INTO public.crm_leads (id, tenant_id, " + ", ".join(columns) + ") "
        "VALUES (:id, :tid, " + ", ".join(values) + ") RETURNING *"
    ), {**data, "id": str(uuid7()), "tid": tenant_id}).mappings().one()  # nosec B608  # Column names from closed FIELDS whitelist; all values bound.
    return project(dict(row))


def update(db: Session, tenant_id: str, lead_id: str, data: dict) -> dict:
    current = get_row(db, tenant_id, lead_id, lock=True)
    data = validate_fields(data)
    if current.get("qualified_opportunity_id") and data.get("status", current["status"]) != current["status"]:
        raise HTTPException(409, "Ein qualifizierter Lead hat bereits eine Opportunity; Status dort bearbeiten.")
    if data:
        assignments = ", ".join(FIELDS[key] + " = :" + key for key in data)
        db.execute(text("UPDATE public.crm_leads SET " + assignments + ", updated_at = NOW() WHERE id::text = :id AND tenant_id = :tid"), {**data, "id": lead_id, "tid": tenant_id})  # nosec B608  # Assignment columns from closed FIELDS whitelist; all values bound.
    return project(get_row(db, tenant_id, lead_id))


def qualification_inputs(db: Session, tenant_id: str, lead_id: str, customer_id: str, *, lock: bool = False):
    lead = get_row(db, tenant_id, lead_id, lock=lock)
    if lead.get("qualified_opportunity_id"):
        raise HTTPException(409, "Lead ist bereits als Opportunity qualifiziert.")
    if lead["status"] in ("CONVERTED", "LOST"):
        raise HTTPException(409, "Konvertierte oder verlorene Leads werden nicht qualifiziert.")
    customer = db.execute(text("SELECT id, company_name FROM domain_crm.customers WHERE id::text = :id AND tenant_id = :tid AND deleted_at IS NULL"), {"id": customer_id, "tid": tenant_id}).mappings().first()
    if not customer:
        raise HTTPException(422, "Einen vorhandenen Kunden des eigenen Mandanten auswaehlen.")
    return lead, customer


def qualify(db: Session, tenant_id: str, lead_id: str, customer_id: str) -> str:
    lead, customer = qualification_inputs(db, tenant_id, lead_id, customer_id, lock=True)
    opportunity_id = str(uuid7())
    db.execute(text("""
        INSERT INTO domain_crm.crm_opportunities
            (id, tenant_id, customer_id, title, estimated_value, stage, probability, assigned_to, source, status)
        VALUES (:id, :tid, :customer, :title, :value, 'QUALIFIZIERT', 25, :assigned, :source, 'aktiv')
    """), {"id": opportunity_id, "tid": tenant_id, "customer": customer["id"],
             "title": lead["company"][:200], "value": lead.get("potential") or Decimal(0),
             "assigned": lead.get("assigned_to") or "unassigned", "source": lead.get("source")})
    db.execute(text("UPDATE public.crm_leads SET status = 'QUALIFIED', qualified_opportunity_id = :opportunity, updated_at = NOW() WHERE id::text = :id AND tenant_id = :tid"), {"opportunity": opportunity_id, "id": lead_id, "tid": tenant_id})
    return opportunity_id
