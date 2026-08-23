"""
CRM Campaign Management API
Full CRUD + State Machine + Templates + Recipients + Analytics

State Machine:
  draft â†’ active â†’ paused â†’ active â†’ completed â†’ archived
  draft â†’ archived (discard)
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CrmCampaignOut(BaseSchema):
    """Typed response schema for CrmCampaignOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/crm/campaigns", tags=["crm", "campaigns", "marketing"])

# â”€â”€â”€ Pydantic Schemas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: str = Field("email", pattern=r"^(email|sms|post|event|webinar|push)$")
    subject_line: Optional[str] = Field(None, max_length=500)
    message_body: Optional[str] = None
    is_active: bool = True
    meta: Optional[dict] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    subject_line: Optional[str] = None
    message_body: Optional[str] = None
    is_active: Optional[bool] = None
    meta: Optional[dict] = None


class TemplateResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    campaign_type: str
    subject_line: Optional[str]
    message_body: Optional[str]
    is_active: bool
    created_by: Optional[str]
    meta: Optional[dict]
    created_at: str
    updated_at: str


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: str = Field("email", pattern=r"^(email|sms|post|event|webinar|push)$")
    template_id: Optional[str] = None
    segment_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    owner_id: Optional[str] = None
    campaign_channel: Optional[str] = None
    target_customer_type: Optional[str] = None
    seasonal_context: Optional[str] = None
    meta: Optional[dict] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    template_id: Optional[str] = None
    segment_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    owner_id: Optional[str] = None
    campaign_channel: Optional[str] = None
    target_customer_type: Optional[str] = None
    seasonal_context: Optional[str] = None
    meta: Optional[dict] = None


class RecipientAdd(BaseModel):
    recipient_id: str
    recipient_type: str = "contact"
    meta: Optional[dict] = None


class RecipientStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(queued|sent|bounced|opened|clicked|converted|unsubscribed)$")
    bounce_reason: Optional[str] = None


# â”€â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _dt(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v)


def _row_to_template(row: Any) -> dict:
    return {
        "id": row.id,
        "tenant_id": row.tenant_id,
        "name": row.name,
        "description": row.description,
        "campaign_type": row.campaign_type,
        "subject_line": row.subject_line,
        "message_body": row.message_body,
        "is_active": row.is_active,
        "created_by": row.created_by,
        "meta": row.meta or {},
        "created_at": _dt(row.created_at),
        "updated_at": _dt(row.updated_at),
    }


def _row_to_campaign(row: Any) -> dict:
    sent = row.total_sent or 0
    delivered = row.total_delivered or 0
    opens = row.total_opens or 0
    clicks = row.total_clicks or 0
    conversions = row.total_conversions or 0
    return {
        "id": row.id,
        "tenant_id": row.tenant_id,
        "name": row.name,
        "description": row.description,
        "state": row.state,
        "campaign_type": row.campaign_type,
        "template_id": row.template_id,
        "segment_id": row.segment_id,
        "start_date": str(row.start_date.date()) if row.start_date else None,
        "end_date": str(row.end_date.date()) if row.end_date else None,
        "budget": float(row.budget) if row.budget is not None else None,
        "owner_id": row.owner_id,
        "kpis": {
            "total_sent": sent,
            "total_delivered": delivered,
            "total_bounced": row.total_bounced or 0,
            "total_opens": opens,
            "total_clicks": clicks,
            "total_conversions": conversions,
            "revenue_generated": float(row.revenue_generated or 0),
            "open_rate": round(opens / delivered * 100, 2) if delivered > 0 else 0.0,
            "click_rate": round(clicks / opens * 100, 2) if opens > 0 else 0.0,
            "conversion_rate": round(conversions / delivered * 100, 2) if delivered > 0 else 0.0,
        },
        "activated_at": _dt(row.activated_at),
        "paused_at": _dt(row.paused_at),
        "completed_at": _dt(row.completed_at),
        "campaign_channel": row.campaign_channel,
        "target_customer_type": row.target_customer_type,
        "seasonal_context": row.seasonal_context,
        "meta": row.meta or {},
        "created_at": _dt(row.created_at),
        "updated_at": _dt(row.updated_at),
    }


VALID_TRANSITIONS: dict[str, list[str]] = {
    "draft":     ["active", "archived"],
    "active":    ["paused", "completed", "archived"],
    "paused":    ["active", "archived"],
    "completed": ["archived"],
    "archived":  [],
}


def _assert_transition(current: str, target: str) -> None:
    allowed = VALID_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"StatusÃ¼bergang '{current}' â†’ '{target}' ist nicht erlaubt. Erlaubt: {allowed}",
        )


# â”€â”€â”€ Campaign Templates â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/templates", response_model=list[CrmCampaignOut], summary="Templates auflisten")
async def list_templates(
    tenant_id: str = Query("system"),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Kampagnen-Vorlagen auflisten"""
    filters = "WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if is_active is not None:
        filters += " AND is_active = :active"
        params["active"] = is_active
    rows = db.execute(
        text(f"SELECT * FROM domain_crm.crm_campaign_templates {filters} ORDER BY name"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    ).fetchall()
    return [_row_to_template(r) for r in rows]


@router.post("/templates", response_model=CrmCampaignOut, status_code=201, summary="Template anlegen")
async def create_template(
    payload: TemplateCreate,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    """Neue Kampagnen-Vorlage anlegen"""
    nid = uuid7()
    now = datetime.utcnow()
    db.execute(
        text("""
            INSERT INTO domain_crm.crm_campaign_templates
              (id, tenant_id, name, description, campaign_type, subject_line,
               message_body, is_active, meta, created_at, updated_at)
            VALUES
              (:id, :tid, :name, :desc, :ctype, :subject, :body, :active,
               :meta::jsonb, :now, :now)
        """),
        {
            "id": nid, "tid": tenant_id, "name": payload.name,
            "desc": payload.description, "ctype": payload.campaign_type,
            "subject": payload.subject_line, "body": payload.message_body,
            "active": payload.is_active, "meta": str(payload.meta or {}), "now": now,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaign_templates WHERE id = :id"),
        {"id": nid},
    ).fetchone()
    return _row_to_template(row)


@router.get("/templates/{template_id}", response_model=CrmCampaignOut, summary="Template abrufen")
async def get_template(
    template_id: str,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaign_templates WHERE id = :id AND tenant_id = :tid"),
        {"id": template_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")
    return _row_to_template(row)


@router.put("/templates/{template_id}", response_model=CrmCampaignOut, summary="Template aktualisieren")
async def update_template(
    template_id: str,
    payload: TemplateUpdate,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaign_templates WHERE id = :id AND tenant_id = :tid"),
        {"id": template_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")

    updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if not updates:
        return _row_to_template(row)

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = template_id
    updates["tid"] = tenant_id
    updates["now"] = datetime.utcnow()
    db.execute(
        text(f"UPDATE domain_crm.crm_campaign_templates SET {set_clauses}, updated_at = :now WHERE id = :id AND tenant_id = :tid"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        updates,
    )
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_crm.crm_campaign_templates WHERE id = :id"),
        {"id": template_id},
    ).fetchone()
    return _row_to_template(updated)


@router.post("/templates/{template_id}/duplicate", response_model=CrmCampaignOut, status_code=201, summary="Template duplicate")
async def duplicate_template(
    template_id: str,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    """Vorlage duplizieren"""
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaign_templates WHERE id = :id AND tenant_id = :tid"),
        {"id": template_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")

    nid = uuid7()
    now = datetime.utcnow()
    db.execute(
        text("""
            INSERT INTO domain_crm.crm_campaign_templates
              (id, tenant_id, name, description, campaign_type, subject_line,
               message_body, is_active, meta, created_at, updated_at)
            VALUES
              (:id, :tid, :name, :desc, :ctype, :subject, :body, :active,
               :meta::jsonb, :now, :now)
        """),
        {
            "id": nid, "tid": tenant_id,
            "name": f"{row.name} (Kopie)",
            "desc": row.description, "ctype": row.campaign_type,
            "subject": row.subject_line, "body": row.message_body,
            "active": False, "meta": str(row.meta or {}), "now": now,
        },
    )
    db.commit()
    copy = db.execute(
        text("SELECT * FROM domain_crm.crm_campaign_templates WHERE id = :id"),
        {"id": nid},
    ).fetchone()
    return _row_to_template(copy)


@router.post("/templates/{template_id}/activate", response_model=CrmCampaignOut, summary="Template aktivieren")
async def activate_template(
    template_id: str,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    db.execute(
        text("UPDATE domain_crm.crm_campaign_templates SET is_active = TRUE, updated_at = NOW() WHERE id = :id AND tenant_id = :tid"),
        {"id": template_id, "tid": tenant_id},
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaign_templates WHERE id = :id AND tenant_id = :tid"),
        {"id": template_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")
    return _row_to_template(row)


@router.post("/templates/{template_id}/deactivate", response_model=CrmCampaignOut, summary="Template deaktivieren")
async def deactivate_template(
    template_id: str,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    db.execute(
        text("UPDATE domain_crm.crm_campaign_templates SET is_active = FALSE, updated_at = NOW() WHERE id = :id AND tenant_id = :tid"),
        {"id": template_id, "tid": tenant_id},
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaign_templates WHERE id = :id AND tenant_id = :tid"),
        {"id": template_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")
    return _row_to_template(row)


@router.delete("/templates/{template_id}", status_code=204, response_class=Response, summary="Template lÃ¶schen")
async def delete_template(
    template_id: str,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> Response:
    result = db.execute(
        text("DELETE FROM domain_crm.crm_campaign_templates WHERE id = :id AND tenant_id = :tid"),
        {"id": template_id, "tid": tenant_id},
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")
    return Response(status_code=204)


# â”€â”€â”€ Campaigns CRUD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("", response_model=list[CrmCampaignOut], summary="Campaigns auflisten")
async def list_campaigns(
    tenant_id: str = Query("system"),
    state: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Kampagnen auflisten"""
    filters = "WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if state:
        filters += " AND state = :state"
        params["state"] = state
    if campaign_type:
        filters += " AND campaign_type = :ctype"
        params["ctype"] = campaign_type
    rows = db.execute(
        text(f"SELECT * FROM domain_crm.crm_campaigns {filters} ORDER BY created_at DESC"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    ).fetchall()
    return [_row_to_campaign(r) for r in rows]


@router.post("", response_model=CrmCampaignOut, status_code=201, summary="Campaign anlegen")
async def create_campaign(
    payload: CampaignCreate,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    """Neue Kampagne anlegen (Status: draft)"""
    if payload.template_id:
        tmpl = db.execute(
            text("SELECT id FROM domain_crm.crm_campaign_templates WHERE id = :id AND tenant_id = :tid"),
            {"id": payload.template_id, "tid": tenant_id},
        ).fetchone()
        if not tmpl:
            raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")

    nid = uuid7()
    now = datetime.utcnow()
    db.execute(
        text("""
            INSERT INTO domain_crm.crm_campaigns
              (id, tenant_id, name, description, state, campaign_type, template_id,
               segment_id, start_date, end_date, budget, owner_id,
               campaign_channel, target_customer_type, seasonal_context, meta,
               created_at, updated_at)
            VALUES
              (:id, :tid, :name, :desc, 'draft', :ctype, :tmpl, :seg,
               :start, :end, :budget, :owner, :channel, :cust_type, :season,
               :meta::jsonb, :now, :now)
        """),
        {
            "id": nid, "tid": tenant_id, "name": payload.name,
            "desc": payload.description, "ctype": payload.campaign_type,
            "tmpl": payload.template_id, "seg": payload.segment_id,
            "start": payload.start_date, "end": payload.end_date,
            "budget": payload.budget, "owner": payload.owner_id,
            "channel": payload.campaign_channel,
            "cust_type": payload.target_customer_type,
            "season": payload.seasonal_context,
            "meta": str(payload.meta or {}), "now": now,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaigns WHERE id = :id"),
        {"id": nid},
    ).fetchone()
    return _row_to_campaign(row)


@router.get("/{campaign_id}", response_model=CrmCampaignOut, summary="Campaign abrufen")
async def get_campaign(
    campaign_id: str,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaigns WHERE id = :id AND tenant_id = :tid"),
        {"id": campaign_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    return _row_to_campaign(row)


@router.put("/{campaign_id}", response_model=CrmCampaignOut, summary="Campaign aktualisieren")
async def update_campaign(
    campaign_id: str,
    payload: CampaignUpdate,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaigns WHERE id = :id AND tenant_id = :tid"),
        {"id": campaign_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    if row.state in ("completed", "archived"):
        raise HTTPException(status_code=422, detail=f"Kampagne im Status '{row.state}' kann nicht bearbeitet werden.")

    updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if not updates:
        return _row_to_campaign(row)

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = campaign_id
    updates["tid"] = tenant_id
    updates["now"] = datetime.utcnow()
    db.execute(
        text(f"UPDATE domain_crm.crm_campaigns SET {set_clauses}, updated_at = :now WHERE id = :id AND tenant_id = :tid"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        updates,
    )
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_crm.crm_campaigns WHERE id = :id"),
        {"id": campaign_id},
    ).fetchone()
    return _row_to_campaign(updated)


@router.delete("/{campaign_id}", status_code=204, response_class=Response, summary="Campaign lÃ¶schen")
async def delete_campaign(
    campaign_id: str,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> Response:
    row = db.execute(
        text("SELECT state FROM domain_crm.crm_campaigns WHERE id = :id AND tenant_id = :tid"),
        {"id": campaign_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    if row.state not in ("draft", "archived"):
        raise HTTPException(status_code=422, detail="Nur EntwÃ¼rfe und archivierte Kampagnen kÃ¶nnen gelÃ¶scht werden.")
    db.execute(
        text("DELETE FROM domain_crm.crm_campaigns WHERE id = :id AND tenant_id = :tid"),
        {"id": campaign_id, "tid": tenant_id},
    )
    db.commit()
    return Response(status_code=204)


# â”€â”€â”€ State Machine â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _transition(campaign_id: str, tenant_id: str, target: str, db: Session) -> dict:
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaigns WHERE id = :id AND tenant_id = :tid"),
        {"id": campaign_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    _assert_transition(row.state, target)

    ts_fields: dict[str, Any] = {"state": target, "updated_at": datetime.utcnow()}
    if target == "active" and row.activated_at is None:
        ts_fields["activated_at"] = datetime.utcnow()
    if target == "paused":
        ts_fields["paused_at"] = datetime.utcnow()
    if target == "completed":
        ts_fields["completed_at"] = datetime.utcnow()

    set_clauses = ", ".join(f"{k} = :{k}" for k in ts_fields)
    ts_fields["id"] = campaign_id
    ts_fields["tid"] = tenant_id
    db.execute(
        text(f"UPDATE domain_crm.crm_campaigns SET {set_clauses} WHERE id = :id AND tenant_id = :tid"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        ts_fields,
    )
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_crm.crm_campaigns WHERE id = :id"),
        {"id": campaign_id},
    ).fetchone()
    return _row_to_campaign(updated)


@router.post("/{campaign_id}/activate", response_model=CrmCampaignOut, summary="Campaign aktivieren")
async def activate_campaign(
    campaign_id: str, tenant_id: str = Query("system"), db: Session = Depends(get_db)
) -> dict:
    """Kampagne aktivieren (draft/paused â†’ active)"""
    return _transition(campaign_id, tenant_id, "active", db)


@router.post("/{campaign_id}/pause", response_model=CrmCampaignOut, summary="Campaign pausieren")
async def pause_campaign(
    campaign_id: str, tenant_id: str = Query("system"), db: Session = Depends(get_db)
) -> dict:
    """Kampagne pausieren (active â†’ paused)"""
    return _transition(campaign_id, tenant_id, "paused", db)


@router.post("/{campaign_id}/resume", response_model=CrmCampaignOut, summary="Campaign fortsetzen")
async def resume_campaign(
    campaign_id: str, tenant_id: str = Query("system"), db: Session = Depends(get_db)
) -> dict:
    """Pausierte Kampagne fortsetzen (paused â†’ active)"""
    return _transition(campaign_id, tenant_id, "active", db)


@router.post("/{campaign_id}/complete", response_model=CrmCampaignOut, summary="Campaign complete")
async def complete_campaign(
    campaign_id: str, tenant_id: str = Query("system"), db: Session = Depends(get_db)
) -> dict:
    """Kampagne abschlieÃŸen (active â†’ completed)"""
    return _transition(campaign_id, tenant_id, "completed", db)


@router.post("/{campaign_id}/archive", response_model=CrmCampaignOut, summary="Campaign archivieren")
async def archive_campaign(
    campaign_id: str, tenant_id: str = Query("system"), db: Session = Depends(get_db)
) -> dict:
    """Kampagne archivieren"""
    return _transition(campaign_id, tenant_id, "archived", db)


# â”€â”€â”€ Recipients â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/{campaign_id}/recipients", response_model=list[CrmCampaignOut], summary="Recipients auflisten")
async def list_recipients(
    campaign_id: str,
    tenant_id: str = Query("system"),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
) -> List[dict]:
    """EmpfÃ¤nger einer Kampagne auflisten"""
    sql = "SELECT * FROM domain_crm.crm_campaign_recipients WHERE campaign_id = :cid AND tenant_id = :tid"
    params: dict = {"cid": campaign_id, "tid": tenant_id}
    if status_filter:
        sql += " AND status = :status"
        params["status"] = status_filter
    rows = db.execute(text(sql + " ORDER BY created_at"), params).fetchall()
    return [
        {
            "id": r.id, "campaign_id": r.campaign_id, "recipient_id": r.recipient_id,
            "recipient_type": r.recipient_type, "status": r.status,
            "sent_at": _dt(r.sent_at), "opened_at": _dt(r.opened_at),
            "clicked_at": _dt(r.clicked_at), "converted_at": _dt(r.converted_at),
            "bounce_reason": r.bounce_reason, "meta": r.meta or {},
            "created_at": _dt(r.created_at),
        }
        for r in rows
    ]


@router.post("/{campaign_id}/recipients", response_model=CrmCampaignOut, status_code=201, summary="Recipient hinzufÃ¼gen")
async def add_recipient(
    campaign_id: str,
    payload: RecipientAdd,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    """EmpfÃ¤nger zu Kampagne hinzufÃ¼gen"""
    existing = db.execute(
        text("SELECT id FROM domain_crm.crm_campaign_recipients WHERE campaign_id = :cid AND recipient_id = :rid"),
        {"cid": campaign_id, "rid": payload.recipient_id},
    ).fetchone()
    if existing:
        raise HTTPException(status_code=409, detail="EmpfÃ¤nger bereits in dieser Kampagne vorhanden")

    nid = uuid7()
    db.execute(
        text("""
            INSERT INTO domain_crm.crm_campaign_recipients
              (id, tenant_id, campaign_id, recipient_id, recipient_type, status, meta, created_at)
            VALUES (:id, :tid, :cid, :rid, :rtype, 'queued', :meta::jsonb, NOW())
        """),
        {
            "id": nid, "tid": tenant_id, "cid": campaign_id,
            "rid": payload.recipient_id, "rtype": payload.recipient_type,
            "meta": str(payload.meta or {}),
        },
    )
    db.commit()
    return {"id": nid, "campaign_id": campaign_id, "recipient_id": payload.recipient_id, "status": "queued"}


@router.patch("/{campaign_id}/recipients/{recipient_id}", response_model=CrmCampaignOut, summary="Recipient status aktualisieren")
async def update_recipient_status(
    campaign_id: str,
    recipient_id: str,
    payload: RecipientStatusUpdate,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    """EmpfÃ¤nger-Status aktualisieren (z.B. sent, opened, clicked, converted)"""
    ts_field = {"sent": "sent_at", "opened": "opened_at", "clicked": "clicked_at", "converted": "converted_at"}.get(payload.status)
    extra = f", {ts_field} = NOW()" if ts_field else ""
    bounce = ", bounce_reason = :bounce" if payload.bounce_reason else ""
    params: dict = {
        "status": payload.status, "cid": campaign_id, "rid": recipient_id, "tid": tenant_id
    }
    if payload.bounce_reason:
        params["bounce"] = payload.bounce_reason
    result = db.execute(
        text(f"UPDATE domain_crm.crm_campaign_recipients SET status = :status{extra}{bounce} WHERE campaign_id = :cid AND recipient_id = :rid AND tenant_id = :tid"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="EmpfÃ¤nger nicht gefunden")
    db.commit()
    # Rebuild KPI aggregates
    _rebuild_kpis(campaign_id, tenant_id, db)
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaign_recipients WHERE campaign_id = :cid AND recipient_id = :rid AND tenant_id = :tid"),
        {"cid": campaign_id, "rid": recipient_id, "tid": tenant_id},
    ).fetchone()
    return {"id": row.id, "campaign_id": campaign_id, "recipient_id": recipient_id, "status": row.status}


# â”€â”€â”€ Analytics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _rebuild_kpis(campaign_id: str, tenant_id: str, db: Session) -> None:
    """KPI-Aggregation aus crm_campaign_recipients neu berechnen"""
    agg = db.execute(
        text("""
            SELECT
                COUNT(*) FILTER (WHERE status IN ('sent','bounced','opened','clicked','converted')) AS total_sent,
                COUNT(*) FILTER (WHERE status IN ('sent','opened','clicked','converted'))           AS total_delivered,
                COUNT(*) FILTER (WHERE status = 'bounced')                                         AS total_bounced,
                COUNT(*) FILTER (WHERE status IN ('opened','clicked','converted'))                 AS total_opens,
                COUNT(*) FILTER (WHERE status IN ('clicked','converted'))                          AS total_clicks,
                COUNT(*) FILTER (WHERE status = 'converted')                                       AS total_conversions
            FROM domain_crm.crm_campaign_recipients
            WHERE campaign_id = :cid AND tenant_id = :tid
        """),
        {"cid": campaign_id, "tid": tenant_id},
    ).fetchone()
    if agg:
        db.execute(
            text("""
                UPDATE domain_crm.crm_campaigns
                SET total_sent = :sent, total_delivered = :delivered,
                    total_bounced = :bounced, total_opens = :opens,
                    total_clicks = :clicks, total_conversions = :convs,
                    updated_at = NOW()
                WHERE id = :cid AND tenant_id = :tid
            """),
            {
                "sent": agg.total_sent or 0, "delivered": agg.total_delivered or 0,
                "bounced": agg.total_bounced or 0, "opens": agg.total_opens or 0,
                "clicks": agg.total_clicks or 0, "convs": agg.total_conversions or 0,
                "cid": campaign_id, "tid": tenant_id,
            },
        )
        db.commit()


@router.get("/{campaign_id}/analytics", response_model=CrmCampaignOut, summary="Analytics abrufen")
async def get_analytics(
    campaign_id: str,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
) -> dict:
    """Detaillierte Kampagnen-Analytik"""
    row = db.execute(
        text("SELECT * FROM domain_crm.crm_campaigns WHERE id = :id AND tenant_id = :tid"),
        {"id": campaign_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")

    # Zeitverlauf: tÃ¤glich aggregiert
    timeline = db.execute(
        text("""
            SELECT
                DATE(sent_at) AS day,
                COUNT(*) FILTER (WHERE status IN ('sent','opened','clicked','converted')) AS sent,
                COUNT(*) FILTER (WHERE status IN ('opened','clicked','converted'))         AS opens,
                COUNT(*) FILTER (WHERE status IN ('clicked','converted'))                 AS clicks,
                COUNT(*) FILTER (WHERE status = 'converted')                              AS conversions
            FROM domain_crm.crm_campaign_recipients
            WHERE campaign_id = :cid AND tenant_id = :tid AND sent_at IS NOT NULL
            GROUP BY DATE(sent_at)
            ORDER BY day
        """),
        {"cid": campaign_id, "tid": tenant_id},
    ).fetchall()

    campaign = _row_to_campaign(row)
    campaign["timeline"] = [
        {"day": str(t.day), "sent": t.sent, "opens": t.opens, "clicks": t.clicks, "conversions": t.conversions}
        for t in timeline
    ]
    return campaign

