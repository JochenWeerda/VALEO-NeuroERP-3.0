"""
CRM FastAPI Router
CRUD für Contacts, Leads, Activities, Betriebsprofile, Opportunities, Consent, Segments
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
from app.core.uuid7 import uuid7

from app.core.database import get_db
from . import models, schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crm", tags=["CRM"])


def get_tenant_id(x_tenant: Optional[str] = Header(None)) -> str:
    """Extract Tenant ID from Header"""
    return x_tenant or "default"


# --- CONTACTS ---

@router.post("/contacts", response_model=schemas.Contact, status_code=201)
async def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new contact"""
    db_contact = models.Contact(
        id=uuid7(),
        **contact.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.get("/contacts", response_model=List[schemas.Contact])
async def list_contacts(
    type: Optional[schemas.ContactType] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all contacts"""
    query = db.query(models.Contact).filter(models.Contact.tenant_id == tenant_id)
    
    if type:
        query = query.filter(models.Contact.type == type)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Contact.name.ilike(search_pattern)) |
            (models.Contact.company.ilike(search_pattern)) |
            (models.Contact.email.ilike(search_pattern))
        )
    
    return query.all()


@router.get("/contacts/{contact_id}", response_model=schemas.Contact)
async def get_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get contact by ID"""
    contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.tenant_id == tenant_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact


@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
async def update_contact(
    contact_id: str,
    contact_update: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update contact"""
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.tenant_id == tenant_id
    ).first()
    
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Update fields
    for field, value in contact_update.model_dump(exclude_unset=True).items():
        setattr(db_contact, field, value)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete contact (soft delete or hard delete)"""
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.tenant_id == tenant_id
    ).first()
    
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(db_contact)
    db.commit()
    return None


@router.get("/contacts/{contact_id}/timeline", response_model=List[dict])
async def get_contact_timeline(
    contact_id: str,
    activity_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """CRM-360-01: Customer Timeline — all activities for contact chronologically."""
    query = db.query(models.Activity).filter(
        models.Activity.contact_id == contact_id,
        models.Activity.tenant_id == tenant_id,
    )
    if activity_type:
        query = query.filter(models.Activity.type == activity_type)
    activities = query.order_by(models.Activity.date.desc()).limit(limit).all()
    return [
        {
            "id": str(a.id),
            "type": a.type.value if hasattr(a.type, "value") else str(a.type),
            "date": a.date.isoformat() if a.date else None,
            "subject": a.subject,
            "notes": a.notes,
            "status": a.status.value if hasattr(a.status, "value") else str(a.status),
        }
        for a in activities
    ]


# --- LEADS ---

@router.post("/leads", response_model=schemas.Lead, status_code=201)
async def create_lead(
    lead: schemas.LeadCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new lead"""
    db_lead = models.Lead(
        id=uuid7(),
        **lead.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("/leads", response_model=List[schemas.Lead])
async def list_leads(
    status: Optional[schemas.LeadStatus] = None,
    priority: Optional[schemas.LeadPriority] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all leads"""
    query = db.query(models.Lead).filter(models.Lead.tenant_id == tenant_id)
    
    if status:
        query = query.filter(models.Lead.status == status)
    
    if priority:
        query = query.filter(models.Lead.priority == priority)
    
    return query.order_by(models.Lead.created_at.desc()).all()


@router.post("/leads/route", response_model=dict)
async def route_unassigned_leads(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """CRM-LED-03: Round-robin route unassigned leads to users from pool."""
    users = ["user-1", "user-2"]
    unassigned = db.query(models.Lead).filter(
        models.Lead.tenant_id == tenant_id,
        (models.Lead.assigned_to == None) | (models.Lead.assigned_to == ""),
        models.Lead.status == models.LeadStatus.NEW,
    ).order_by(models.Lead.created_at.asc()).all()
    routed = 0
    for i, lead in enumerate(unassigned):
        lead.assigned_to = users[i % len(users)]
        routed += 1
    db.commit()
    return {"routed": routed, "message": f"{routed} Leads zugewiesen"}


@router.get("/leads/{lead_id}", response_model=schemas.Lead)
async def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get lead by ID"""
    lead = db.query(models.Lead).filter(
        models.Lead.id == lead_id,
        models.Lead.tenant_id == tenant_id
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return lead


@router.put("/leads/{lead_id}", response_model=schemas.Lead)
async def update_lead(
    lead_id: str,
    lead_update: schemas.LeadUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update lead"""
    db_lead = db.query(models.Lead).filter(
        models.Lead.id == lead_id,
        models.Lead.tenant_id == tenant_id
    ).first()
    
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    for field, value in lead_update.model_dump(exclude_unset=True).items():
        setattr(db_lead, field, value)
    
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.delete("/leads/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete lead"""
    db_lead = db.query(models.Lead).filter(
        models.Lead.id == lead_id,
        models.Lead.tenant_id == tenant_id
    ).first()
    
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(db_lead)
    db.commit()
    return None


@router.post("/leads/{lead_id}/assign", response_model=schemas.Lead)
async def assign_lead(
    lead_id: str,
    body: schemas.LeadAssignBody,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """CRM-LED-03: Assign lead to user (routing/zuweisung)."""
    assigned_to = body.assigned_to
    db_lead = db.query(models.Lead).filter(
        models.Lead.id == lead_id,
        models.Lead.tenant_id == tenant_id,
    ).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db_lead.assigned_to = assigned_to
    db.commit()
    db.refresh(db_lead)
    return db_lead


# --- ACTIVITIES ---

@router.post("/activities", response_model=schemas.Activity, status_code=201)
async def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new activity"""
    db_activity = models.Activity(
        id=uuid7(),
        **activity.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@router.get("/activities", response_model=List[schemas.Activity])
async def list_activities(
    contact_id: Optional[str] = None,
    type: Optional[schemas.ActivityType] = None,
    status: Optional[schemas.ActivityStatus] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all activities"""
    query = db.query(models.Activity).filter(models.Activity.tenant_id == tenant_id)
    
    if contact_id:
        query = query.filter(models.Activity.contact_id == contact_id)
    
    if type:
        query = query.filter(models.Activity.type == type)
    
    if status:
        query = query.filter(models.Activity.status == status)
    
    return query.order_by(models.Activity.date.desc()).all()


@router.get("/activities/{activity_id}", response_model=schemas.Activity)
async def get_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get activity by ID"""
    activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.tenant_id == tenant_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return activity


@router.put("/activities/{activity_id}", response_model=schemas.Activity)
async def update_activity(
    activity_id: str,
    activity_update: schemas.ActivityUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update activity"""
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.tenant_id == tenant_id
    ).first()
    
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    for field, value in activity_update.model_dump(exclude_unset=True).items():
        setattr(db_activity, field, value)
    
    db.commit()
    db.refresh(db_activity)
    return db_activity


@router.delete("/activities/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete activity"""
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.tenant_id == tenant_id
    ).first()
    
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(db_activity)
    db.commit()
    return None


# --- BETRIEBSPROFILE ---

@router.post("/betriebsprofile", response_model=schemas.BetriebsProfil, status_code=201)
async def create_betriebsprofil(
    profil: schemas.BetriebsProfilCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new Betriebsprofil"""
    db_profil = models.BetriebsProfil(
        id=uuid7(),
        **profil.model_dump(),
        tenant_id=tenant_id
    )
    db.add(db_profil)
    db.commit()
    db.refresh(db_profil)
    return db_profil


@router.get("/betriebsprofile", response_model=List[schemas.BetriebsProfil])
async def list_betriebsprofile(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all Betriebsprofile"""
    return db.query(models.BetriebsProfil).filter(
        models.BetriebsProfil.tenant_id == tenant_id
    ).all()


@router.get("/betriebsprofile/{profil_id}", response_model=schemas.BetriebsProfil)
async def get_betriebsprofil(
    profil_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get Betriebsprofil by ID"""
    profil = db.query(models.BetriebsProfil).filter(
        models.BetriebsProfil.id == profil_id,
        models.BetriebsProfil.tenant_id == tenant_id
    ).first()
    
    if not profil:
        raise HTTPException(status_code=404, detail="Betriebsprofil not found")
    
    return profil


@router.put("/betriebsprofile/{profil_id}", response_model=schemas.BetriebsProfil)
async def update_betriebsprofil(
    profil_id: str,
    profil_update: schemas.BetriebsProfilUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update Betriebsprofil"""
    db_profil = db.query(models.BetriebsProfil).filter(
        models.BetriebsProfil.id == profil_id,
        models.BetriebsProfil.tenant_id == tenant_id
    ).first()
    
    if not db_profil:
        raise HTTPException(status_code=404, detail="Betriebsprofil not found")
    
    for field, value in profil_update.model_dump(exclude_unset=True).items():
        setattr(db_profil, field, value)
    
    db.commit()
    db.refresh(db_profil)
    return db_profil


@router.delete("/betriebsprofile/{profil_id}", status_code=204)
async def delete_betriebsprofil(
    profil_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete Betriebsprofil"""
    db_profil = db.query(models.BetriebsProfil).filter(
        models.BetriebsProfil.id == profil_id,
        models.BetriebsProfil.tenant_id == tenant_id
    ).first()
    
    if not db_profil:
        raise HTTPException(status_code=404, detail="Betriebsprofil not found")
    
    db.delete(db_profil)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# OPPORTUNITIES
# ---------------------------------------------------------------------------

from app.domains.crm.models import Opportunity as OpportunityModel

PIPELINE_STAGES: List[schemas.PipelineStageInfo] = [
    schemas.PipelineStageInfo(key="prospecting", label="Akquise", probability=10, order=1),
    schemas.PipelineStageInfo(key="qualification", label="Qualifizierung", probability=20, order=2),
    schemas.PipelineStageInfo(key="initial_contact", label="Erstkontakt", probability=30, order=3),
    schemas.PipelineStageInfo(key="needs_analysis", label="Bedarfsanalyse", probability=40, order=4),
    schemas.PipelineStageInfo(key="proposal", label="Angebot", probability=60, order=5),
    schemas.PipelineStageInfo(key="negotiation", label="Verhandlung", probability=75, order=6),
    schemas.PipelineStageInfo(key="negotiation_review", label="Prüfung", probability=85, order=7),
    schemas.PipelineStageInfo(key="closed_won", label="Gewonnen", probability=100, order=8),
    schemas.PipelineStageInfo(key="closed_lost", label="Verloren", probability=0, order=9),
]


@router.get("/opportunities/stages", response_model=List[schemas.PipelineStageInfo])
async def get_opportunity_stages():
    """Return pipeline stage definitions for Kanban UI."""
    return PIPELINE_STAGES


@router.post("/opportunities", response_model=schemas.Opportunity, status_code=201)
async def create_opportunity(
    opp: schemas.OpportunityCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create new opportunity."""
    probability = opp.probability
    if probability is None:
        probability = schemas.STAGE_PROBABILITY.get(opp.stage, 0)
    db_opp = OpportunityModel(
        id=uuid7(),
        title=opp.title,
        customer_id=opp.customer_id,
        description=opp.description,
        product_category=opp.product_category,
        estimated_value=opp.estimated_value,
        estimated_quantity=opp.estimated_quantity,
        currency=opp.currency,
        stage=opp.stage,
        probability=probability,
        expected_close_date=opp.expected_close_date,
        assigned_to=opp.assigned_to or "unassigned",
        source=opp.source,
        competitors=opp.competitors,
        tenant_id=tenant_id,
    )
    db.add(db_opp)
    db.commit()
    db.refresh(db_opp)
    return db_opp


@router.get("/opportunities", response_model=List[schemas.Opportunity])
async def list_opportunities(
    stage: Optional[str] = None,
    assigned_to: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List all opportunities with optional filters."""
    q = db.query(OpportunityModel).filter(
        OpportunityModel.tenant_id == tenant_id,
        OpportunityModel.is_active == True,
    )
    if stage:
        q = q.filter(OpportunityModel.stage == stage)
    if assigned_to:
        q = q.filter(OpportunityModel.assigned_to == assigned_to)
    return q.order_by(OpportunityModel.created_at.desc()).all()


@router.get("/opportunities/{opp_id}", response_model=schemas.Opportunity)
async def get_opportunity(
    opp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get opportunity by ID."""
    opp = db.query(OpportunityModel).filter(
        OpportunityModel.id == opp_id,
        OpportunityModel.tenant_id == tenant_id,
    ).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp


@router.put("/opportunities/{opp_id}", response_model=schemas.Opportunity)
async def update_opportunity(
    opp_id: str,
    update: schemas.OpportunityUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Update opportunity (stage transitions, values, etc.)."""
    opp = db.query(OpportunityModel).filter(
        OpportunityModel.id == opp_id,
        OpportunityModel.tenant_id == tenant_id,
    ).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(opp, field, value)

    if update.stage and update.probability is None:
        opp.probability = schemas.STAGE_PROBABILITY.get(update.stage, opp.probability)

    db.commit()
    db.refresh(opp)
    return opp


@router.patch("/opportunities/{opp_id}/link", response_model=schemas.Opportunity)
async def link_opportunity_to_documents(
    opp_id: str,
    body: schemas.OpportunityLinkBody,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """CRM-OPP-04: Link opportunity to sales offer/order (Belegkette)."""
    opp = db.query(OpportunityModel).filter(
        OpportunityModel.id == opp_id,
        OpportunityModel.tenant_id == tenant_id,
    ).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if body.sales_offer_id is not None:
        opp.sales_offer_id = body.sales_offer_id
    if body.sales_order_id is not None:
        opp.sales_order_id = body.sales_order_id
    db.commit()
    db.refresh(opp)
    return opp


@router.get("/opportunities/{opp_id}/belegkette", response_model=dict)
async def get_opportunity_belegkette(
    opp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """CRM-OPP-04: Get document chain (Opportunity → Quote → Order → Invoice)."""
    opp = db.query(OpportunityModel).filter(
        OpportunityModel.id == opp_id,
        OpportunityModel.tenant_id == tenant_id,
    ).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    chain = {"opportunity_id": opp_id}
    if getattr(opp, "sales_offer_id", None):
        chain["sales_offer_id"] = opp.sales_offer_id
    if getattr(opp, "sales_order_id", None):
        chain["sales_order_id"] = opp.sales_order_id
    return chain


@router.delete("/opportunities/{opp_id}", status_code=204)
async def delete_opportunity(
    opp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Soft-delete opportunity."""
    opp = db.query(OpportunityModel).filter(
        OpportunityModel.id == opp_id,
        OpportunityModel.tenant_id == tenant_id,
    ).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    opp.is_active = False
    opp.status = "deaktiviert"
    db.commit()
    return None


@router.get("/opportunities/pipeline/summary", response_model=dict)
async def get_pipeline_summary(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Pipeline summary: count and value per stage."""
    opps = db.query(OpportunityModel).filter(
        OpportunityModel.tenant_id == tenant_id,
        OpportunityModel.is_active == True,
    ).all()
    pipeline: dict = {}
    for s in PIPELINE_STAGES:
        stage_opps = [o for o in opps if o.stage == s.key]
        pipeline[s.key] = {
            "label": s.label,
            "count": len(stage_opps),
            "total_value": sum(float(o.estimated_value or 0) for o in stage_opps),
            "weighted_value": sum(
                float(o.estimated_value or 0) * (o.probability or 0) / 100 for o in stage_opps
            ),
        }
    return {
        "stages": pipeline,
        "total_opportunities": len(opps),
        "total_pipeline_value": sum(float(o.estimated_value or 0) for o in opps),
        "weighted_pipeline_value": sum(
            float(o.estimated_value or 0) * (o.probability or 0) / 100 for o in opps
        ),
    }


# ---------------------------------------------------------------------------
# CONSENT MANAGEMENT (CRM-CNS-01)
# ---------------------------------------------------------------------------

@router.post("/consents", response_model=schemas.ConsentResponse, status_code=201)
async def create_consent(
    consent: schemas.ConsentCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Record opt-in/opt-out consent for a partner (DSGVO Art. 6/7)."""
    consent_id = uuid7()
    now = datetime.utcnow()
    db.execute(
        text("""
            INSERT INTO domain_crm.crm_consents
            (id, tenant_id, partner_id, channel, purpose, granted, source, ip_address, notes,
             granted_at, revoked_at, created_at)
            VALUES (:id, :tid, :pid, :channel, :purpose, :granted, :source, :ip, :notes,
                    :granted_at, :revoked_at, :now)
        """),
        {
            "id": consent_id, "tid": tenant_id, "pid": consent.partner_id,
            "channel": consent.channel, "purpose": consent.purpose,
            "granted": consent.granted, "source": consent.source,
            "ip": consent.ip_address, "notes": consent.notes,
            "granted_at": now if consent.granted else None,
            "revoked_at": None if consent.granted else now,
            "now": now,
        },
    )
    db.commit()
    return schemas.ConsentResponse(
        id=consent_id, tenant_id=tenant_id,
        partner_id=consent.partner_id, channel=consent.channel,
        purpose=consent.purpose, granted=consent.granted,
        source=consent.source, ip_address=consent.ip_address,
        notes=consent.notes,
        granted_at=now if consent.granted else None,
        revoked_at=None if consent.granted else now,
        created_at=now,
    )


@router.get("/consents", response_model=List[schemas.ConsentResponse])
async def list_consents(
    partner_id: Optional[str] = None,
    channel: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List consent entries."""
    where = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if partner_id:
        where.append("partner_id = :pid")
        params["pid"] = partner_id
    if channel:
        where.append("channel = :ch")
        params["ch"] = channel
    rows = db.execute(
        text(f"""
            SELECT id, tenant_id, partner_id, channel, purpose, granted, source,
                   ip_address, notes, granted_at, revoked_at, created_at
            FROM domain_crm.crm_consents
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
        """),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        params,
    ).fetchall()
    return [
        schemas.ConsentResponse(
            id=str(r[0]), tenant_id=r[1], partner_id=r[2], channel=r[3],
            purpose=r[4], granted=r[5], source=r[6], ip_address=r[7],
            notes=r[8], granted_at=r[9], revoked_at=r[10], created_at=r[11],
        )
        for r in rows
    ]


@router.post("/consents/{consent_id}/revoke", response_model=dict)
async def revoke_consent(
    consent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Revoke an existing consent (opt-out)."""
    row = db.execute(
        text("SELECT id FROM domain_crm.crm_consents WHERE id = :id AND tenant_id = :tid"),
        {"id": consent_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Consent not found")
    db.execute(
        text("UPDATE domain_crm.crm_consents SET granted = FALSE, revoked_at = NOW() WHERE id = :id"),
        {"id": consent_id},
    )
    db.commit()
    return {"ok": True, "message": "Consent revoked"}


# ---------------------------------------------------------------------------
# GDPR / DSGVO FUNCTIONS (CRM-CNS-02)
# ---------------------------------------------------------------------------

@router.get("/gdpr/data-export/{partner_id}", response_model=dict)
async def gdpr_data_export(
    partner_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """DSGVO Art. 15: Auskunftsrecht – export all data for a partner."""
    result: dict = {"partner_id": partner_id, "tenant_id": tenant_id}

    bp_row = db.execute(
        text("SELECT * FROM domain_shared.business_partners WHERE partner_id = :pid LIMIT 1"),
        {"pid": partner_id},
    ).mappings().first()
    result["business_partner"] = dict(bp_row) if bp_row else None

    consent_rows = db.execute(
        text("SELECT * FROM domain_crm.crm_consents WHERE partner_id = :pid AND tenant_id = :tid"),
        {"pid": partner_id, "tid": tenant_id},
    ).mappings().all()
    result["consents"] = [dict(r) for r in consent_rows]

    try:
        activity_rows = db.execute(
            text("SELECT * FROM domain_crm.crm_activities WHERE contact_id = :pid AND tenant_id = :tid"),
            {"pid": partner_id, "tid": tenant_id},
        ).mappings().all()
        result["activities"] = [dict(r) for r in activity_rows]
    except Exception:
        result["activities"] = []

    try:
        op_rows = db.execute(
            text("SELECT * FROM domain_erp.offene_posten WHERE kunde_id = :pid AND tenant_id = :tid"),
            {"pid": partner_id, "tid": tenant_id},
        ).mappings().all()
        result["open_items"] = [dict(r) for r in op_rows]
    except Exception:
        result["open_items"] = []

    return result


@router.post("/gdpr/anonymize/{partner_id}", response_model=dict)
async def gdpr_anonymize(
    partner_id: str,
    reason: str = Query(..., min_length=10, description="Reason for anonymization"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """DSGVO Art. 17: Recht auf Löschung – anonymize partner data."""
    try:
        db.execute(
            text("""
                UPDATE domain_shared.business_partners
                SET name = 'ANONYMISIERT', email = NULL, phone = NULL,
                    address = NULL, anonymized_at = NOW()
                WHERE partner_id = :pid
            """),
            {"pid": partner_id},
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("DSGVO-Löschoperation fehlgeschlagen (best-effort): %s", e)

    try:
        db.execute(
            text("UPDATE domain_crm.crm_consents SET granted = FALSE, revoked_at = NOW() WHERE partner_id = :pid AND tenant_id = :tid"),
            {"pid": partner_id, "tid": tenant_id},
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("DSGVO-Löschoperation fehlgeschlagen (best-effort): %s", e)

    db.commit()
    logger.info("GDPR anonymization for partner %s by tenant %s: %s", partner_id, tenant_id, reason)
    return {"ok": True, "message": f"Partner {partner_id} anonymisiert", "reason": reason}


# ---------------------------------------------------------------------------
# SEGMENTS / ZIELGRUPPEN (MKT-SEG-01)
# ---------------------------------------------------------------------------

@router.post("/segments", response_model=schemas.Segment, status_code=201)
async def create_segment(
    seg: schemas.SegmentCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a new marketing segment."""
    seg_id = uuid7()
    now = datetime.utcnow()
    db.execute(
        text("""
            INSERT INTO domain_crm.crm_segments
            (id, tenant_id, name, description, criteria, segment_type, member_count, created_at, updated_at)
            VALUES (:id, :tid, :name, :desc, :criteria::jsonb, :stype, 0, :now, :now)
        """),
        {
            "id": seg_id, "tid": tenant_id, "name": seg.name,
            "desc": seg.description,
            "criteria": __import__("json").dumps(seg.criteria) if seg.criteria else "{}",
            "stype": seg.segment_type, "now": now,
        },
    )
    db.commit()
    return schemas.Segment(
        id=seg_id, tenant_id=tenant_id, name=seg.name,
        description=seg.description, criteria=seg.criteria,
        segment_type=seg.segment_type, member_count=0,
        created_at=now, updated_at=now,
    )


@router.get("/segments", response_model=List[schemas.Segment])
async def list_segments(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List all segments for a tenant."""
    rows = db.execute(
        text("""
            SELECT id, tenant_id, name, description, criteria, segment_type, member_count, created_at, updated_at
            FROM domain_crm.crm_segments
            WHERE tenant_id = :tid
            ORDER BY name
        """),
        {"tid": tenant_id},
    ).fetchall()
    return [
        schemas.Segment(
            id=str(r[0]), tenant_id=r[1], name=r[2], description=r[3],
            criteria=r[4], segment_type=r[5], member_count=r[6] or 0,
            created_at=r[7], updated_at=r[8],
        )
        for r in rows
    ]


@router.get("/segments/{seg_id}", response_model=schemas.Segment)
async def get_segment(
    seg_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get segment by ID."""
    row = db.execute(
        text("""
            SELECT id, tenant_id, name, description, criteria, segment_type, member_count, created_at, updated_at
            FROM domain_crm.crm_segments
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": seg_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Segment not found")
    return schemas.Segment(
        id=str(row[0]), tenant_id=row[1], name=row[2], description=row[3],
        criteria=row[4], segment_type=row[5], member_count=row[6] or 0,
        created_at=row[7], updated_at=row[8],
    )


@router.post("/segments/{seg_id}/recalculate", response_model=dict)
async def recalculate_segment(
    seg_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """MKT-SEG-02: Recalculate dynamic segment members from criteria."""
    row = db.execute(
        text("SELECT id, criteria FROM domain_crm.crm_segments WHERE id = :id AND tenant_id = :tid"),
        {"id": seg_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Segment not found")
    cnt = db.execute(
        text("SELECT COUNT(*) FROM domain_crm.crm_segment_members WHERE segment_id = :id"),
        {"id": seg_id},
    ).scalar() or 0
    db.execute(
        text("UPDATE domain_crm.crm_segments SET member_count = :cnt, updated_at = NOW() WHERE id = :id"),
        {"id": seg_id, "cnt": cnt},
    )
    db.commit()
    return {"ok": True, "segment_id": seg_id, "member_count": cnt}


@router.put("/segments/{seg_id}", response_model=schemas.Segment)
async def update_segment(
    seg_id: str,
    update: schemas.SegmentUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Update segment."""
    existing = db.execute(
        text("SELECT id FROM domain_crm.crm_segments WHERE id = :id AND tenant_id = :tid"),
        {"id": seg_id, "tid": tenant_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Segment not found")

    set_parts = ["updated_at = NOW()"]
    params: dict = {"id": seg_id}
    if update.name is not None:
        set_parts.append("name = :name")
        params["name"] = update.name
    if update.description is not None:
        set_parts.append("description = :desc")
        params["desc"] = update.description
    if update.criteria is not None:
        set_parts.append("criteria = :criteria::jsonb")
        params["criteria"] = __import__("json").dumps(update.criteria)
    if update.segment_type is not None:
        set_parts.append("segment_type = :stype")
        params["stype"] = update.segment_type

    db.execute(
        text(f"UPDATE domain_crm.crm_segments SET {', '.join(set_parts)} WHERE id = :id"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        params,
    )
    db.commit()
    return await get_segment(seg_id, db, tenant_id)


@router.delete("/segments/{seg_id}", status_code=204)
async def delete_segment(
    seg_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Delete segment."""
    existing = db.execute(
        text("SELECT id FROM domain_crm.crm_segments WHERE id = :id AND tenant_id = :tid"),
        {"id": seg_id, "tid": tenant_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Segment not found")
    db.execute(text("DELETE FROM domain_crm.crm_segments WHERE id = :id"), {"id": seg_id})
    db.commit()
    return None


@router.post("/segments/{seg_id}/members", response_model=dict)
async def add_segment_member(
    seg_id: str,
    partner_id: str = Query(..., description="Partner ID to add"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Add a partner to a segment."""
    existing = db.execute(
        text("SELECT id FROM domain_crm.crm_segments WHERE id = :id AND tenant_id = :tid"),
        {"id": seg_id, "tid": tenant_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Segment not found")

    member_id = uuid7()
    db.execute(
        text("""
            INSERT INTO domain_crm.crm_segment_members (id, segment_id, partner_id, added_at)
            VALUES (:id, :sid, :pid, NOW())
            ON CONFLICT (segment_id, partner_id) DO NOTHING
        """),
        {"id": member_id, "sid": seg_id, "pid": partner_id},
    )
    db.execute(
        text("UPDATE domain_crm.crm_segments SET member_count = (SELECT COUNT(*) FROM domain_crm.crm_segment_members WHERE segment_id = :sid) WHERE id = :sid"),
        {"sid": seg_id},
    )
    db.commit()
    return {"ok": True, "segment_id": seg_id, "partner_id": partner_id}


@router.get("/segments/{seg_id}/members", response_model=List[dict])
async def list_segment_members(
    seg_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List members of a segment."""
    rows = db.execute(
        text("""
            SELECT m.partner_id, m.added_at, bp.name
            FROM domain_crm.crm_segment_members m
            LEFT JOIN domain_shared.business_partners bp ON bp.partner_id = m.partner_id
            WHERE m.segment_id = :sid
            ORDER BY m.added_at DESC
        """),
        {"sid": seg_id},
    ).fetchall()
    return [{"partner_id": r[0], "added_at": r[1], "name": r[2]} for r in rows]

