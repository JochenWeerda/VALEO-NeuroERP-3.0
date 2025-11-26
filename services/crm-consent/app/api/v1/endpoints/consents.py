"""Consent management endpoints."""

from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Consent, ConsentHistory, ConsentChannel, ConsentType, ConsentStatus, ConsentSource, ConsentHistoryAction
from app.db.session import get_db
from app.schemas.consent import (
    ConsentCreate,
    ConsentUpdate,
    Consent as ConsentSchema,
    ConsentHistory as ConsentHistorySchema,
    ConsentCheckRequest,
    ConsentCheckResponse,
)
from app.config.settings import settings
from app.services.events import get_event_publisher

router = APIRouter()


@router.post("", response_model=ConsentSchema, status_code=201)
async def create_consent(
    consent_data: ConsentCreate,
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Create a new consent record with double opt-in token."""
    # Generate double opt-in token
    double_opt_in_token = uuid4()
    
    # Get IP address and user agent from request
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
    
    # Create consent record
    consent = Consent(
        tenant_id=consent_data.tenant_id,
        contact_id=consent_data.contact_id,
        channel=ConsentChannel(consent_data.channel),
        consent_type=ConsentType(consent_data.consent_type),
        status=ConsentStatus.PENDING,  # Pending until double opt-in confirmed
        source=ConsentSource(consent_data.source),
        double_opt_in_token=double_opt_in_token,
        ip_address=ip_address or consent_data.ip_address,
        user_agent=user_agent or consent_data.user_agent,
        expires_at=consent_data.expires_at,
        created_by=consent_data.tenant_id,  # TODO: Get from auth context
    )
    
    db.add(consent)
    await db.commit()
    await db.refresh(consent)
    
    # Create history entry
    history = ConsentHistory(
        consent_id=consent.id,
        action=ConsentHistoryAction.GRANTED,
        old_status=None,
        new_status=ConsentStatus.PENDING,
        changed_by=consent.created_by or "system",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(history)
    await db.commit()
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_consent_created(
        consent_id=consent.id,
        tenant_id=consent.tenant_id,
        contact_id=consent.contact_id,
        channel=consent.channel.value,
        consent_type=consent.consent_type.value,
    )
    
    # TODO: Send double opt-in email
    # await send_double_opt_in_email(consent.contact_id, double_opt_in_token)
    
    return consent


@router.get("", response_model=list[ConsentSchema])
async def list_consents(
    tenant_id: str = Query(..., description="Tenant ID"),
    contact_id: UUID | None = Query(None, description="Filter by contact ID"),
    channel: str | None = Query(None, description="Filter by channel"),
    status: str | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    """List consents with optional filters."""
    filters = [Consent.tenant_id == tenant_id]
    
    if contact_id:
        filters.append(Consent.contact_id == contact_id)
    if channel:
        filters.append(Consent.channel == ConsentChannel(channel))
    if status:
        filters.append(Consent.status == ConsentStatus(status))
    
    stmt = select(Consent).where(and_(*filters)).order_by(Consent.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{consent_id}", response_model=ConsentSchema)
async def get_consent(
    consent_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get consent details."""
    consent = await db.get(Consent, consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    return consent


@router.put("/{consent_id}", response_model=ConsentSchema)
async def update_consent(
    consent_id: UUID,
    consent_data: ConsentUpdate,
    db: AsyncSession = Depends(get_db),
    changed_by: str | None = Query(None, description="User ID making the change"),
):
    """Update a consent record."""
    consent = await db.get(Consent, consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    old_status = consent.status
    
    # Update fields
    if consent_data.status:
        consent.status = ConsentStatus(consent_data.status)
        # Update timestamps based on status
        now = datetime.utcnow()
        if consent.status == ConsentStatus.GRANTED:
            consent.granted_at = now
        elif consent.status == ConsentStatus.DENIED:
            consent.denied_at = now
        elif consent.status == ConsentStatus.REVOKED:
            consent.revoked_at = now
    
    if consent_data.expires_at is not None:
        consent.expires_at = consent_data.expires_at
    
    consent.updated_by = changed_by or "system"
    consent.updated_at = datetime.utcnow()
    
    # Create history entry if status changed
    if old_status != consent.status:
        history = ConsentHistory(
            consent_id=consent.id,
            action=ConsentHistoryAction.UPDATED if old_status else ConsentHistoryAction.GRANTED,
            old_status=old_status,
            new_status=consent.status,
            reason=consent_data.reason,
            changed_by=consent.updated_by,
        )
        db.add(history)
    
    await db.commit()
    await db.refresh(consent)
    
    # Publish event if status changed
    if old_status != consent.status:
        event_publisher = get_event_publisher()
        await event_publisher.publish_consent_updated(
            consent_id=consent.id,
            tenant_id=consent.tenant_id,
            contact_id=consent.contact_id,
            old_status=old_status.value,
            new_status=consent.status.value,
        )
    
    return consent


@router.delete("/{consent_id}", status_code=204)
async def delete_consent(
    consent_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a consent record."""
    consent = await db.get(Consent, consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    await db.delete(consent)
    await db.commit()
    
    return None


@router.post("/{consent_id}/confirm", response_model=ConsentSchema)
async def confirm_double_opt_in(
    consent_id: UUID,
    token: UUID = Query(..., description="Double opt-in token"),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Confirm double opt-in with token."""
    consent = await db.get(Consent, consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    if consent.double_opt_in_token != token:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Check if token is expired
    if consent.created_at:
        expiry_time = consent.created_at + timedelta(hours=settings.DOUBLE_OPT_IN_TOKEN_EXPIRY_HOURS)
        if datetime.utcnow() > expiry_time:
            raise HTTPException(status_code=400, detail="Token expired")
    
    # Update consent status
    old_status = consent.status
    consent.status = ConsentStatus.GRANTED
    consent.granted_at = datetime.utcnow()
    consent.double_opt_in_confirmed_at = datetime.utcnow()
    consent.double_opt_in_token = None  # Clear token after confirmation
    consent.updated_at = datetime.utcnow()
    
    # Get IP and user agent
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
    
    # Create history entry
    history = ConsentHistory(
        consent_id=consent.id,
        action=ConsentHistoryAction.GRANTED,
        old_status=old_status,
        new_status=ConsentStatus.GRANTED,
        changed_by="contact",  # User confirmed themselves
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(consent)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_consent_confirmed(
        consent_id=consent.id,
        tenant_id=consent.tenant_id,
        contact_id=consent.contact_id,
        channel=consent.channel.value,
    )
    
    return consent


@router.post("/{consent_id}/revoke", response_model=ConsentSchema)
async def revoke_consent(
    consent_id: UUID,
    reason: str | None = Query(None, description="Reason for revocation"),
    db: AsyncSession = Depends(get_db),
    changed_by: str | None = Query(None, description="User ID making the change"),
    request: Request = None,
):
    """Revoke a consent."""
    consent = await db.get(Consent, consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    if consent.status != ConsentStatus.GRANTED:
        raise HTTPException(status_code=400, detail="Consent is not granted")
    
    old_status = consent.status
    consent.status = ConsentStatus.REVOKED
    consent.revoked_at = datetime.utcnow()
    consent.updated_at = datetime.utcnow()
    consent.updated_by = changed_by or "contact"
    
    # Get IP and user agent
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
    
    # Create history entry
    history = ConsentHistory(
        consent_id=consent.id,
        action=ConsentHistoryAction.REVOKED,
        old_status=old_status,
        new_status=ConsentStatus.REVOKED,
        reason=reason,
        changed_by=consent.updated_by,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(consent)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_consent_revoked(
        consent_id=consent.id,
        tenant_id=consent.tenant_id,
        contact_id=consent.contact_id,
        channel=consent.channel.value,
        reason=reason,
    )
    
    return consent


@router.get("/contact/{contact_id}", response_model=list[ConsentSchema])
async def get_contact_consents(
    contact_id: UUID,
    tenant_id: str = Query(..., description="Tenant ID"),
    db: AsyncSession = Depends(get_db),
):
    """Get all consents for a contact."""
    stmt = select(Consent).where(
        and_(
            Consent.tenant_id == tenant_id,
            Consent.contact_id == contact_id
        )
    ).order_by(Consent.created_at.desc())
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{consent_id}/history", response_model=list[ConsentHistorySchema])
async def get_consent_history(
    consent_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get consent history."""
    consent = await db.get(Consent, consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    
    stmt = select(ConsentHistory).where(
        ConsentHistory.consent_id == consent_id
    ).order_by(ConsentHistory.changed_at.desc())
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/check", response_model=ConsentCheckResponse)
async def check_consent(
    check_request: ConsentCheckRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
    db: AsyncSession = Depends(get_db),
):
    """Check if a contact has active consent for a channel."""
    filters = [
        Consent.tenant_id == tenant_id,
        Consent.contact_id == check_request.contact_id,
        Consent.channel == ConsentChannel(check_request.channel),
        Consent.status == ConsentStatus.GRANTED,
    ]
    
    if check_request.consent_type:
        filters.append(Consent.consent_type == ConsentType(check_request.consent_type))
    
    stmt = select(Consent).where(and_(*filters)).order_by(Consent.granted_at.desc())
    result = await db.execute(stmt)
    consent = result.scalar_one_or_none()
    
    if not consent:
        return ConsentCheckResponse(
            has_consent=False,
            is_expired=False,
        )
    
    # Check if expired
    is_expired = False
    if consent.expires_at and consent.expires_at < datetime.utcnow():
        is_expired = True
    
    return ConsentCheckResponse(
        has_consent=not is_expired,
        consent_id=consent.id,
        status=consent.status.value,
        granted_at=consent.granted_at,
        expires_at=consent.expires_at,
        is_expired=is_expired,
    )

