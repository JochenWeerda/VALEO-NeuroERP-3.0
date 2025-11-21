"""
CRM FastAPI Router
CRUD für Contacts, Leads, Activities, Betriebsprofile
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.database_pg import get_db
from . import models, schemas

router = APIRouter(prefix="/api/v1/crm", tags=["CRM"])


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
        id=str(uuid.uuid4()),
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


# --- LEADS ---

@router.post("/leads", response_model=schemas.Lead, status_code=201)
async def create_lead(
    lead: schemas.LeadCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new lead"""
    db_lead = models.Lead(
        id=str(uuid.uuid4()),
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


# --- ACTIVITIES ---

@router.post("/activities", response_model=schemas.Activity, status_code=201)
async def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new activity"""
    db_activity = models.Activity(
        id=str(uuid.uuid4()),
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
        id=str(uuid.uuid4()),
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

