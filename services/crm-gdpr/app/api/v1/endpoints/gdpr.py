"""GDPR request management endpoints."""

from datetime import datetime
from uuid import UUID, uuid4
from pathlib import Path
import json
import csv
import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    GDPRRequest,
    GDPRRequestHistory,
    GDPRRequestType,
    GDPRRequestStatus,
    VerificationMethod,
    GDPRRequestHistoryAction,
)
from app.db.session import get_db
from app.schemas.gdpr import (
    GDPRRequestCreate,
    GDPRRequestUpdate,
    GDPRRequest as GDPRRequestSchema,
    GDPRRequestHistory as GDPRRequestHistorySchema,
    GDPRRequestVerify,
    GDPRRequestExport,
    GDPRRequestDelete,
    GDPRRequestReject,
    GDPRCheckRequest,
    GDPRCheckResponse,
)
from app.config.settings import settings
from app.services.events import get_event_publisher

router = APIRouter()


@router.post("/requests", response_model=GDPRRequestSchema, status_code=201)
async def create_gdpr_request(
    request_data: GDPRRequestCreate,
    db: AsyncSession = Depends(get_db),
    request: Request = None,
):
    """Create a new GDPR request."""
    # Create request record
    gdpr_request = GDPRRequest(
        tenant_id=request_data.tenant_id,
        request_type=GDPRRequestType(request_data.request_type),
        contact_id=request_data.contact_id,
        status=GDPRRequestStatus.PENDING,
        requested_by=request_data.requested_by,
        is_self_request=request_data.is_self_request,
        notes=request_data.notes,
        created_by=request_data.requested_by,  # TODO: Get from auth context
    )
    
    db.add(gdpr_request)
    await db.commit()
    await db.refresh(gdpr_request)
    
    # Create history entry
    history = GDPRRequestHistory(
        request_id=gdpr_request.id,
        action=GDPRRequestHistoryAction.CREATED,
        old_status=None,
        new_status=GDPRRequestStatus.PENDING,
        changed_by=gdpr_request.created_by or "system",
    )
    db.add(history)
    await db.commit()
    
    # Generate verification token if email verification
    if request_data.is_self_request:
        verification_token = uuid4()
        gdpr_request.verification_token = verification_token
        await db.commit()
        # TODO: Send verification email
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_gdpr_request_created(
        request_id=gdpr_request.id,
        tenant_id=gdpr_request.tenant_id,
        contact_id=gdpr_request.contact_id,
        request_type=gdpr_request.request_type.value,
    )
    
    return gdpr_request


@router.get("/requests", response_model=list[GDPRRequestSchema])
async def list_gdpr_requests(
    tenant_id: str = Query(..., description="Tenant ID"),
    contact_id: UUID | None = Query(None, description="Filter by contact ID"),
    request_type: str | None = Query(None, description="Filter by request type"),
    status: str | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    """List GDPR requests with optional filters."""
    filters = [GDPRRequest.tenant_id == tenant_id]
    
    if contact_id:
        filters.append(GDPRRequest.contact_id == contact_id)
    if request_type:
        filters.append(GDPRRequest.request_type == GDPRRequestType(request_type))
    if status:
        filters.append(GDPRRequest.status == GDPRRequestStatus(status))
    
    stmt = select(GDPRRequest).where(and_(*filters)).order_by(GDPRRequest.requested_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/requests/{request_id}", response_model=GDPRRequestSchema)
async def get_gdpr_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get GDPR request details."""
    gdpr_request = await db.get(GDPRRequest, request_id)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")
    return gdpr_request


@router.put("/requests/{request_id}", response_model=GDPRRequestSchema)
async def update_gdpr_request(
    request_id: UUID,
    request_data: GDPRRequestUpdate,
    db: AsyncSession = Depends(get_db),
    changed_by: str | None = Query(None, description="User ID making the change"),
):
    """Update a GDPR request."""
    gdpr_request = await db.get(GDPRRequest, request_id)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")
    
    old_status = gdpr_request.status
    
    # Update fields
    if request_data.status:
        gdpr_request.status = GDPRRequestStatus(request_data.status)
        now = datetime.utcnow()
        if gdpr_request.status == GDPRRequestStatus.COMPLETED:
            gdpr_request.completed_at = now
        elif gdpr_request.status == GDPRRequestStatus.REJECTED:
            gdpr_request.rejected_at = now
    
    if request_data.notes is not None:
        gdpr_request.notes = request_data.notes
    
    gdpr_request.updated_by = changed_by or "system"
    gdpr_request.updated_at = datetime.utcnow()
    
    # Create history entry if status changed
    if old_status != gdpr_request.status:
        history = GDPRRequestHistory(
            request_id=gdpr_request.id,
            action=GDPRRequestHistoryAction.STATUS_CHANGED,
            old_status=old_status,
            new_status=gdpr_request.status,
            changed_by=gdpr_request.updated_by,
        )
        db.add(history)
    
    await db.commit()
    await db.refresh(gdpr_request)
    
    return gdpr_request


@router.post("/requests/{request_id}/verify", response_model=GDPRRequestSchema)
async def verify_gdpr_request(
    request_id: UUID,
    verify_data: GDPRRequestVerify,
    db: AsyncSession = Depends(get_db),
    changed_by: str | None = Query(None, description="User ID making the change"),
):
    """Verify identity for a GDPR request."""
    gdpr_request = await db.get(GDPRRequest, request_id)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")
    
    # Check verification token if email verification
    if verify_data.verification_method == "email" and verify_data.verification_token:
        if gdpr_request.verification_token != verify_data.verification_token:
            raise HTTPException(status_code=400, detail="Invalid verification token")
    
    # Update verification
    gdpr_request.verified_at = datetime.utcnow()
    gdpr_request.verification_method = VerificationMethod(verify_data.verification_method)
    gdpr_request.status = GDPRRequestStatus.IN_PROGRESS
    gdpr_request.updated_by = changed_by or "system"
    gdpr_request.updated_at = datetime.utcnow()
    
    # Create history entry
    history = GDPRRequestHistory(
        request_id=gdpr_request.id,
        action=GDPRRequestHistoryAction.VERIFIED,
        old_status=GDPRRequestStatus.PENDING,
        new_status=GDPRRequestStatus.IN_PROGRESS,
        changed_by=gdpr_request.updated_by,
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(gdpr_request)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_gdpr_request_verified(
        request_id=gdpr_request.id,
        tenant_id=gdpr_request.tenant_id,
        contact_id=gdpr_request.contact_id,
    )
    
    return gdpr_request


@router.post("/requests/{request_id}/export", response_model=GDPRRequestSchema)
async def export_gdpr_data(
    request_id: UUID,
    export_data: GDPRRequestExport,
    db: AsyncSession = Depends(get_db),
    changed_by: str | None = Query(None, description="User ID making the change"),
):
    """Generate data export for a GDPR request."""
    gdpr_request = await db.get(GDPRRequest, request_id)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")
    
    if gdpr_request.status != GDPRRequestStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Request must be verified and in progress")
    
    # TODO: Collect data from all CRM modules
    # This is a placeholder - actual implementation would query all services
    export_data_dict = {
        "contact_id": str(gdpr_request.contact_id),
        "exported_at": datetime.utcnow().isoformat(),
        "data_areas": export_data.data_areas,
        "contacts": [],  # TODO: Fetch from crm-core
        "opportunities": [],  # TODO: Fetch from crm-sales
        "activities": [],  # TODO: Fetch from crm-sales
        "consents": [],  # TODO: Fetch from crm-consent
        "campaigns": [],  # TODO: Fetch from crm-marketing
    }
    
    # Generate export file
    export_dir = Path(settings.EXPORT_STORAGE_PATH)
    export_dir.mkdir(parents=True, exist_ok=True)
    
    file_name = f"gdpr_export_{gdpr_request.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    if export_data.format == "json":
        file_path = export_dir / f"{file_name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data_dict, f, indent=2, ensure_ascii=False)
    elif export_data.format == "csv":
        file_path = export_dir / f"{file_name}.csv"
        # TODO: Convert to CSV format
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Contact ID", "Exported At", "Data Areas"])
            writer.writerow([str(gdpr_request.contact_id), datetime.utcnow().isoformat(), ", ".join(export_data.data_areas)])
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {export_data.format}")
    
    # Update request
    gdpr_request.response_data = export_data_dict
    gdpr_request.response_file_path = str(file_path)
    gdpr_request.response_file_format = export_data.format
    gdpr_request.status = GDPRRequestStatus.COMPLETED
    gdpr_request.completed_at = datetime.utcnow()
    gdpr_request.updated_by = changed_by or "system"
    gdpr_request.updated_at = datetime.utcnow()
    
    # Create history entry
    history = GDPRRequestHistory(
        request_id=gdpr_request.id,
        action=GDPRRequestHistoryAction.DATA_EXPORTED,
        old_status=GDPRRequestStatus.IN_PROGRESS,
        new_status=GDPRRequestStatus.COMPLETED,
        changed_by=gdpr_request.updated_by,
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(gdpr_request)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_gdpr_request_exported(
        request_id=gdpr_request.id,
        tenant_id=gdpr_request.tenant_id,
        contact_id=gdpr_request.contact_id,
    )
    
    return gdpr_request


@router.post("/requests/{request_id}/delete", response_model=GDPRRequestSchema)
async def delete_gdpr_data(
    request_id: UUID,
    delete_data: GDPRRequestDelete,
    db: AsyncSession = Depends(get_db),
    changed_by: str | None = Query(None, description="User ID making the change"),
):
    """Delete/anonymize data for a GDPR request."""
    gdpr_request = await db.get(GDPRRequest, request_id)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")
    
    if gdpr_request.request_type != GDPRRequestType.DELETION:
        raise HTTPException(status_code=400, detail="Request type must be deletion")
    
    if gdpr_request.status != GDPRRequestStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Request must be verified and in progress")
    
    # TODO: Implement actual deletion/anonymization logic
    # This would call anonymization services for all modules
    # For now, we just mark as completed
    
    gdpr_request.status = GDPRRequestStatus.COMPLETED
    gdpr_request.completed_at = datetime.utcnow()
    gdpr_request.notes = f"Data {'anonymized' if delete_data.anonymize_only else 'deleted'}. Reason: {delete_data.reason or 'GDPR request'}"
    gdpr_request.updated_by = changed_by or "system"
    gdpr_request.updated_at = datetime.utcnow()
    
    # Create history entry
    history = GDPRRequestHistory(
        request_id=gdpr_request.id,
        action=GDPRRequestHistoryAction.DATA_DELETED,
        old_status=GDPRRequestStatus.IN_PROGRESS,
        new_status=GDPRRequestStatus.COMPLETED,
        notes=delete_data.reason,
        changed_by=gdpr_request.updated_by,
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(gdpr_request)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_gdpr_request_deleted(
        request_id=gdpr_request.id,
        tenant_id=gdpr_request.tenant_id,
        contact_id=gdpr_request.contact_id,
    )
    
    return gdpr_request


@router.post("/requests/{request_id}/reject", response_model=GDPRRequestSchema)
async def reject_gdpr_request(
    request_id: UUID,
    reject_data: GDPRRequestReject,
    db: AsyncSession = Depends(get_db),
    changed_by: str | None = Query(None, description="User ID making the change"),
):
    """Reject a GDPR request."""
    gdpr_request = await db.get(GDPRRequest, request_id)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")
    
    old_status = gdpr_request.status
    gdpr_request.status = GDPRRequestStatus.REJECTED
    gdpr_request.rejected_at = datetime.utcnow()
    gdpr_request.rejection_reason = reject_data.rejection_reason
    gdpr_request.updated_by = changed_by or "system"
    gdpr_request.updated_at = datetime.utcnow()
    
    # Create history entry
    history = GDPRRequestHistory(
        request_id=gdpr_request.id,
        action=GDPRRequestHistoryAction.REJECTED,
        old_status=old_status,
        new_status=GDPRRequestStatus.REJECTED,
        notes=reject_data.rejection_reason,
        changed_by=gdpr_request.updated_by,
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(gdpr_request)
    
    # Publish event
    event_publisher = get_event_publisher()
    await event_publisher.publish_gdpr_request_rejected(
        request_id=gdpr_request.id,
        tenant_id=gdpr_request.tenant_id,
        contact_id=gdpr_request.contact_id,
        reason=reject_data.rejection_reason,
    )
    
    return gdpr_request


@router.get("/requests/{request_id}/history", response_model=list[GDPRRequestHistorySchema])
async def get_gdpr_request_history(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get GDPR request history."""
    gdpr_request = await db.get(GDPRRequest, request_id)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")
    
    stmt = select(GDPRRequestHistory).where(
        GDPRRequestHistory.request_id == request_id
    ).order_by(GDPRRequestHistory.changed_at.desc())
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/requests/{request_id}/download")
async def download_gdpr_export(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Download export file for a GDPR request."""
    gdpr_request = await db.get(GDPRRequest, request_id)
    if not gdpr_request:
        raise HTTPException(status_code=404, detail="GDPR request not found")
    
    if not gdpr_request.response_file_path:
        raise HTTPException(status_code=404, detail="Export file not found")
    
    file_path = Path(gdpr_request.response_file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )


@router.post("/check", response_model=GDPRCheckResponse)
async def check_gdpr_request(
    check_request: GDPRCheckRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
    db: AsyncSession = Depends(get_db),
):
    """Check if a GDPR request exists for a contact."""
    filters = [
        GDPRRequest.tenant_id == tenant_id,
        GDPRRequest.contact_id == check_request.contact_id,
    ]
    
    if check_request.request_type:
        filters.append(GDPRRequest.request_type == GDPRRequestType(check_request.request_type))
    
    stmt = select(GDPRRequest).where(and_(*filters)).order_by(GDPRRequest.requested_at.desc())
    result = await db.execute(stmt)
    gdpr_request = result.scalar_one_or_none()
    
    if not gdpr_request:
        return GDPRCheckResponse(
            has_request=False,
        )
    
    return GDPRCheckResponse(
        has_request=True,
        request_id=gdpr_request.id,
        status=gdpr_request.status.value,
        request_type=gdpr_request.request_type.value,
    )

