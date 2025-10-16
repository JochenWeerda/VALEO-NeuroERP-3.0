"""
CRM Farm Profile management endpoints
RESTful API for farm profile management with clean architecture
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.repositories import FarmProfileRepositoryImpl
from ....core.dependency_container import container
from ..schemas.crm import (
    FarmProfileCreate, FarmProfileUpdate, FarmProfile
)
from ..schemas.base import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=FarmProfile, status_code=201)
async def create_farm_profile(
    profile_data: FarmProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new farm profile.

    This endpoint allows creating a new farm profile with crops, livestock, and location data.
    """
    try:
        profile_repo = FarmProfileRepositoryImpl(db)
        profile = await profile_repo.create(profile_data.model_dump(), "system")
        db.commit()
        db.refresh(profile)
        return FarmProfile.model_validate(profile)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create farm profile: {str(e)}")


@router.get("/", response_model=PaginatedResponse[FarmProfile])
async def list_farm_profiles(
    search: Optional[str] = Query(None, description="Search in farm name or owner"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List farm profiles with pagination and filtering.

    Retrieve a paginated list of farm profiles with optional search.
    """
    try:
        profile_repo = FarmProfileRepositoryImpl(db)

        profiles = await profile_repo.get_all("system", skip, limit, search=search)
        total = await profile_repo.count("system", search=search)

        return PaginatedResponse[FarmProfile](
            items=[FarmProfile.model_validate(profile) for profile in profiles],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list farm profiles: {str(e)}")


@router.get("/{profile_id}", response_model=FarmProfile)
async def get_farm_profile(
    profile_id: str,
    db: Session = Depends(get_db)
):
    """
    Get farm profile by ID.

    Retrieve detailed information about a specific farm profile.
    """
    try:
        profile_repo = FarmProfileRepositoryImpl(db)
        profile = await profile_repo.get_by_id(profile_id, "system")
        if not profile:
            raise HTTPException(status_code=404, detail="Farm profile not found")
        return FarmProfile.model_validate(profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve farm profile: {str(e)}")


@router.put("/{profile_id}", response_model=FarmProfile)
async def update_farm_profile(
    profile_id: str,
    profile_data: FarmProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update farm profile information.

    Modify farm profile details such as area, crops, livestock, or certifications.
    """
    try:
        profile_repo = FarmProfileRepositoryImpl(db)
        profile = await profile_repo.update(profile_id, profile_data.model_dump(exclude_unset=True), "system")
        if not profile:
            raise HTTPException(status_code=404, detail="Farm profile not found")
        db.commit()
        db.refresh(profile)
        return FarmProfile.model_validate(profile)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update farm profile: {str(e)}")


@router.delete("/{profile_id}", status_code=204)
async def delete_farm_profile(
    profile_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete farm profile.

    Remove a farm profile from the system.
    """
    try:
        profile_repo = FarmProfileRepositoryImpl(db)
        success = await profile_repo.delete(profile_id, "system")
        if not success:
            raise HTTPException(status_code=404, detail="Farm profile not found")
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete farm profile: {str(e)}")

