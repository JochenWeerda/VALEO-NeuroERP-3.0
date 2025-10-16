"""
CRM Activity management endpoints
RESTful API for activity management with clean architecture
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.repositories import ActivityRepository, ActivityRepositoryImpl
from ....core.dependency_container import container
from ..schemas.crm import (
    ActivityCreate, ActivityUpdate, Activity
)
from ..schemas.base import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=Activity, status_code=201)
async def create_activity(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new activity.

    This endpoint allows creating a new CRM activity (meeting, call, email, note).
    """
    try:
        activity_repo = ActivityRepositoryImpl(db)
        activity = await activity_repo.create(activity_data.model_dump(), "system")
        db.commit()
        db.refresh(activity)
        return Activity.model_validate(activity)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create activity: {str(e)}")


@router.get("/", response_model=PaginatedResponse[Activity])
async def list_activities(
    type: Optional[str] = Query(None, description="Filter by activity type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title, customer, or contact"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List activities with pagination and filtering.

    Retrieve a paginated list of activities with optional filtering.
    """
    try:
        activity_repo = ActivityRepositoryImpl(db)

        activities = await activity_repo.get_all("system", skip, limit, type=type, status=status)
        total = await activity_repo.count("system", type=type, status=status)

        return PaginatedResponse[Activity](
            items=[Activity.model_validate(activity) for activity in activities],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 0,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list activities: {str(e)}")


@router.get("/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: str,
    db: Session = Depends(get_db)
):
    """
    Get activity by ID.

    Retrieve detailed information about a specific activity.
    """
    try:
        activity_repo = ActivityRepositoryImpl(db)
        activity = await activity_repo.get_by_id(activity_id, "system")
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        return Activity.model_validate(activity)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve activity: {str(e)}")


@router.put("/{activity_id}", response_model=Activity)
async def update_activity(
    activity_id: str,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db)
):
    """
    Update activity information.

    Modify activity details such as status, date, or description.
    """
    try:
        activity_repo = ActivityRepositoryImpl(db)
        activity = await activity_repo.update(activity_id, activity_data.model_dump(exclude_unset=True), "system")
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        db.commit()
        db.refresh(activity)
        return Activity.model_validate(activity)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update activity: {str(e)}")


@router.delete("/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete activity.

    Remove an activity from the system.
    """
    try:
        activity_repo = ActivityRepositoryImpl(db)
        success = await activity_repo.delete(activity_id, "system")
        if not success:
            raise HTTPException(status_code=404, detail="Activity not found")
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete activity: {str(e)}")

