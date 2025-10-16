"""
Proplanta PSM Integration API
API endpoints for Proplanta PSM data synchronization and queries
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from ....core.database import get_db
from ....integrations.proplanta_psm_client import (
    ProplantaPSMClient,
    PSMData,
    sync_psm_data,
    search_psm,
    get_psm_details,
    is_configured
)

router = APIRouter()

logger = logging.getLogger(__name__)

# Global PSM client instance
psm_client = ProplantaPSMClient()


@router.get("/status")
async def get_proplanta_psm_status():
    """Get Proplanta PSM integration status."""
    return {
        "configured": is_configured(),
        "last_sync": psm_client._last_sync.isoformat() if psm_client._last_sync else None,
        "cached_items": len(psm_client._cache)
    }


@router.post("/sync", response_model=Dict[str, Any])
async def sync_proplanta_psm_data(
    background_tasks: BackgroundTasks,
    force: bool = Query(False, description="Force full sync even if recently synced")
):
    """Synchronize PSM data from Proplanta."""
    try:
        if not is_configured():
            raise HTTPException(
                status_code=400,
                detail="Proplanta PSM integration not configured"
            )

        # Start sync in background
        background_tasks.add_task(_perform_psm_sync, force)

        return {
            "message": "PSM synchronization started",
            "status": "running"
        }

    except Exception as e:
        logger.error(f"Failed to start PSM sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _perform_psm_sync(force: bool = False):
    """Background task to perform PSM synchronization."""
    try:
        logger.info("Starting Proplanta PSM synchronization")

        psm_data = psm_client.sync_psm_data()

        logger.info(f"Successfully synchronized {len(psm_data)} PSM items")

        # TODO: Optionally update local database with synced data
        # This could involve creating/updating PSM records in the local database

    except Exception as e:
        logger.error(f"PSM synchronization failed: {e}")
        # TODO: Could send notification or update status


@router.get("/list", response_model=List[Dict[str, Any]])
async def list_proplanta_psm(
    status: Optional[str] = Query(None, description="Filter by status (approved, expired, withdrawn)"),
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer"),
    hazard_class: Optional[str] = Query(None, description="Filter by hazard class"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results")
):
    """List PSM data from Proplanta."""
    try:
        if not is_configured():
            raise HTTPException(
                status_code=400,
                detail="Proplanta PSM integration not configured"
            )

        # Get all cached PSM data
        all_psm = psm_client.get_all_psm()

        # Apply filters
        filtered_psm = all_psm

        if status:
            if status == "active":
                filtered_psm = psm_client.get_active_psm()
            elif status == "expired":
                filtered_psm = psm_client.get_expired_psm()
            else:
                filtered_psm = [psm for psm in filtered_psm if psm.status == status]

        if manufacturer:
            filtered_psm = [psm for psm in filtered_psm
                          if manufacturer.lower() in psm.manufacturer.lower()]

        if hazard_class:
            filtered_psm = [psm for psm in filtered_psm
                          if psm.hazard_class == hazard_class]

        # Apply limit
        limited_psm = filtered_psm[:limit]

        return [psm.to_dict() for psm in limited_psm]

    except Exception as e:
        logger.error(f"Failed to list PSM data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_proplanta_psm(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, ge=1, le=100, description="Maximum number of results")
):
    """Search PSM data from Proplanta."""
    try:
        if not is_configured():
            raise HTTPException(
                status_code=400,
                detail="Proplanta PSM integration not configured"
            )

        psm_results = psm_client.search_psm(q, limit)
        return [psm.to_dict() for psm in psm_results]

    except Exception as e:
        logger.error(f"Failed to search PSM data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{psm_id}", response_model=Dict[str, Any])
async def get_proplanta_psm_details(psm_id: str):
    """Get detailed PSM information from Proplanta."""
    try:
        if not is_configured():
            raise HTTPException(
                status_code=400,
                detail="Proplanta PSM integration not configured"
            )

        psm_data = psm_client.get_psm_details(psm_id)

        if not psm_data:
            raise HTTPException(status_code=404, detail="PSM not found")

        return psm_data.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get PSM details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def get_proplanta_psm_stats():
    """Get PSM statistics from Proplanta data."""
    try:
        if not is_configured():
            raise HTTPException(
                status_code=400,
                detail="Proplanta PSM integration not configured"
            )

        all_psm = psm_client.get_all_psm()
        active_psm = psm_client.get_active_psm()
        expired_psm = psm_client.get_expired_psm()

        # Group by manufacturer
        manufacturers = {}
        for psm in all_psm:
            manufacturers[psm.manufacturer] = manufacturers.get(psm.manufacturer, 0) + 1

        # Group by hazard class
        hazard_classes = {}
        for psm in all_psm:
            hazard_classes[psm.hazard_class] = hazard_classes.get(psm.hazard_class, 0) + 1

        # Group by application areas
        application_areas = {}
        for psm in all_psm:
            for area in psm.application_areas:
                application_areas[area] = application_areas.get(area, 0) + 1

        return {
            "total_psm": len(all_psm),
            "active_psm": len(active_psm),
            "expired_psm": len(expired_psm),
            "by_manufacturer": manufacturers,
            "by_hazard_class": hazard_classes,
            "by_application_area": application_areas,
            "last_updated": psm_client._last_sync.isoformat() if psm_client._last_sync else None
        }

    except Exception as e:
        logger.error(f"Failed to get PSM stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-to-local")
async def import_proplanta_psm_to_local(
    background_tasks: BackgroundTasks,
    tenant_id: Optional[str] = Query("system", description="Tenant ID for imported data"),
    update_existing: bool = Query(True, description="Update existing PSM records"),
    db: Session = Depends(get_db)
):
    """Import Proplanta PSM data into local ERP database."""
    try:
        if not is_configured():
            raise HTTPException(
                status_code=400,
                detail="Proplanta PSM integration not configured"
            )

        # Start import in background
        background_tasks.add_task(_perform_psm_import, tenant_id, update_existing, db)

        return {
            "message": "PSM import to local database started",
            "status": "running"
        }

    except Exception as e:
        logger.error(f"Failed to start PSM import: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _perform_psm_import(tenant_id: str, update_existing: bool, db: Session):
    """Background task to import PSM data into local database."""
    try:
        from ....infrastructure.models import PSM as PSMModel

        logger.info("Starting PSM import to local database")

        # Get PSM data from Proplanta
        psm_data_list = psm_client.get_all_psm()

        imported_count = 0
        updated_count = 0
        skipped_count = 0

        for psm_data in psm_data_list:
            try:
                # Check if PSM already exists (by approval number)
                existing = db.query(PSMModel).filter(
                    PSMModel.bvl_nummer == psm_data.approval_number,
                    PSMModel.tenant_id == tenant_id
                ).first()

                if existing:
                    if update_existing:
                        # Update existing record
                        existing.name = psm_data.name
                        existing.wirkstoff = psm_data.active_ingredient
                        existing.hersteller = psm_data.manufacturer
                        existing.zulassung_datum = psm_data.approval_date
                        existing.zulassung_ablauf = psm_data.expiry_date
                        existing.gefahrenklasse = psm_data.hazard_class
                        existing.kulturen = psm_data.application_areas
                        existing.ist_aktiv = psm_data.status == "approved" and not psm_data.is_expired()
                        existing.updated_at = db.func.now()

                        updated_count += 1
                        logger.debug(f"Updated PSM: {psm_data.approval_number}")
                    else:
                        skipped_count += 1
                else:
                    # Create new record
                    new_psm = PSMModel(
                        name=psm_data.name,
                        wirkstoff=psm_data.active_ingredient,
                        bvl_nummer=psm_data.approval_number,
                        hersteller=psm_data.manufacturer,
                        zulassung_datum=psm_data.approval_date,
                        zulassung_ablauf=psm_data.expiry_date,
                        gefahrenklasse=psm_data.hazard_class,
                        kulturen=psm_data.application_areas,
                        ist_aktiv=psm_data.status == "approved" and not psm_data.is_expired(),
                        tenant_id=tenant_id
                    )

                    db.add(new_psm)
                    imported_count += 1
                    logger.debug(f"Imported PSM: {psm_data.approval_number}")

            except Exception as e:
                logger.warning(f"Failed to import PSM {psm_data.id}: {e}")
                continue

        db.commit()

        logger.info(f"PSM import completed: {imported_count} imported, {updated_count} updated, {skipped_count} skipped")

    except Exception as e:
        logger.error(f"PSM import failed: {e}")
        db.rollback()