"""
Accounting Period Management API
FIBU-GL-05: Periodensteuerung
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class AccountingPeriod(BaseModel):
    """Accounting period model."""
    id: Optional[str] = None
    tenant_id: str
    period: str  # YYYY-MM format
    status: str  # OPEN, CLOSED, ADJUSTING
    start_date: date
    end_date: date
    closed_at: Optional[datetime] = None
    closed_by: Optional[str] = None
    metadata: dict = {}

    class Config:
        from_attributes = True


class PeriodCreate(BaseModel):
    """Create accounting period."""
    tenant_id: str
    period: str  # YYYY-MM format
    start_date: date
    end_date: date
    status: str = "OPEN"


class PeriodUpdate(BaseModel):
    """Update accounting period."""
    status: Optional[str] = None
    closed_by: Optional[str] = None


@router.post("/", response_model=AccountingPeriod, status_code=201)
async def create_period(
    period_data: PeriodCreate,
    db: Session = Depends(get_db)
):
    """Create a new accounting period."""
    try:
        # Validate period format (YYYY-MM)
        if len(period_data.period) != 7 or period_data.period[4] != '-':
            raise HTTPException(
                status_code=400,
                detail="Period must be in YYYY-MM format"
            )

        # Check if period already exists
        existing = db.execute(
            text("""
                SELECT id FROM finance_accounting_periods
                WHERE tenant_id = :tenant_id AND period = :period
            """),
            {"tenant_id": period_data.tenant_id, "period": period_data.period}
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Period {period_data.period} already exists for tenant {period_data.tenant_id}"
            )

        # Validate dates
        if period_data.start_date >= period_data.end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date"
            )

        # Insert period
        period_id = str(datetime.now().timestamp())
        db.execute(
            text("""
                INSERT INTO finance_accounting_periods
                (id, tenant_id, period, status, start_date, end_date, created_at)
                VALUES (:id, :tenant_id, :period, :status, :start_date, :end_date, NOW())
            """),
            {
                "id": period_id,
                "tenant_id": period_data.tenant_id,
                "period": period_data.period,
                "status": period_data.status,
                "start_date": period_data.start_date,
                "end_date": period_data.end_date
            }
        )
        db.commit()

        # Fetch created period
        result = db.execute(
            text("""
                SELECT id, tenant_id, period, status, start_date, end_date,
                       closed_at, closed_by, metadata, created_at
                FROM finance_accounting_periods
                WHERE id = :id
            """),
            {"id": period_id}
        ).fetchone()

        return AccountingPeriod(
            id=result[0],
            tenant_id=result[1],
            period=result[2],
            status=result[3],
            start_date=result[4],
            end_date=result[5],
            closed_at=result[6],
            closed_by=result[7],
            metadata=result[8] or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating period: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create period: {str(e)}")


@router.get("/", response_model=List[AccountingPeriod])
async def list_periods(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List accounting periods with filters."""
    try:
        query = """
            SELECT id, tenant_id, period, status, start_date, end_date,
                   closed_at, closed_by, metadata, created_at
            FROM finance_accounting_periods
            WHERE 1=1
        """
        params = {}

        if tenant_id:
            query += " AND tenant_id = :tenant_id"
            params["tenant_id"] = tenant_id

        if status:
            query += " AND status = :status"
            params["status"] = status

        query += " ORDER BY period DESC LIMIT :limit OFFSET :skip"
        params["limit"] = limit
        params["skip"] = skip

        results = db.execute(text(query), params).fetchall()

        return [
            AccountingPeriod(
                id=r[0],
                tenant_id=r[1],
                period=r[2],
                status=r[3],
                start_date=r[4],
                end_date=r[5],
                closed_at=r[6],
                closed_by=r[7],
                metadata=r[8] or {},
            )
            for r in results
        ]

    except Exception as e:
        logger.error(f"Error listing periods: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list periods: {str(e)}")


@router.get("/{period_id}", response_model=AccountingPeriod)
async def get_period(
    period_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific accounting period."""
    try:
        result = db.execute(
            text("""
                SELECT id, tenant_id, period, status, start_date, end_date,
                       closed_at, closed_by, metadata, created_at
                FROM finance_accounting_periods
                WHERE id = :id
            """),
            {"id": period_id}
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Period not found")

        return AccountingPeriod(
            id=result[0],
            tenant_id=result[1],
            period=result[2],
            status=result[3],
            start_date=result[4],
            end_date=result[5],
            closed_at=result[6],
            closed_by=result[7],
            metadata=result[8] or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting period: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get period: {str(e)}")


@router.put("/{period_id}", response_model=AccountingPeriod)
async def update_period(
    period_id: str,
    period_update: PeriodUpdate,
    db: Session = Depends(get_db)
):
    """Update an accounting period (e.g., close it)."""
    try:
        # Get existing period
        existing = db.execute(
            text("""
                SELECT id, tenant_id, period, status, start_date, end_date,
                       closed_at, closed_by, metadata, created_at
                FROM finance_accounting_periods
                WHERE id = :id
            """),
            {"id": period_id}
        ).fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Period not found")

        # Update status
        update_query = "UPDATE finance_accounting_periods SET"
        params = {"id": period_id}
        updates = []

        if period_update.status:
            if period_update.status not in ["OPEN", "CLOSED", "ADJUSTING"]:
                raise HTTPException(
                    status_code=400,
                    detail="Status must be OPEN, CLOSED, or ADJUSTING"
                )
            updates.append(" status = :status")
            params["status"] = period_update.status

            # If closing, set closed_at and closed_by
            if period_update.status == "CLOSED":
                updates.append(" closed_at = NOW()")
                if period_update.closed_by:
                    updates.append(" closed_by = :closed_by")
                    params["closed_by"] = period_update.closed_by

        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_query += ",".join(updates) + " WHERE id = :id"
        db.execute(text(update_query), params)
        db.commit()

        # Fetch updated period
        result = db.execute(
            text("""
                SELECT id, tenant_id, period, status, start_date, end_date,
                       closed_at, closed_by, metadata, created_at
                FROM finance_accounting_periods
                WHERE id = :id
            """),
            {"id": period_id}
        ).fetchone()

        return AccountingPeriod(
            id=result[0],
            tenant_id=result[1],
            period=result[2],
            status=result[3],
            start_date=result[4],
            end_date=result[5],
            closed_at=result[6],
            closed_by=result[7],
            metadata=result[8] or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating period: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update period: {str(e)}")


@router.get("/check/{tenant_id}/{period}", response_model=dict)
async def check_period_status(
    tenant_id: str,
    period: str,
    db: Session = Depends(get_db)
):
    """Check if a period is open for bookings."""
    try:
        result = db.execute(
            text("""
                SELECT status FROM finance_accounting_periods
                WHERE tenant_id = :tenant_id AND period = :period
            """),
            {"tenant_id": tenant_id, "period": period}
        ).fetchone()

        if not result:
            # Period doesn't exist, assume it's open (create on first booking)
            return {
                "period": period,
                "status": "OPEN",
                "is_open": True,
                "message": "Period does not exist, will be created on first booking"
            }

        status = result[0]
        is_open = status == "OPEN"

        return {
            "period": period,
            "status": status,
            "is_open": is_open,
            "message": "Period is open for bookings" if is_open else f"Period is {status}, bookings are blocked"
        }

    except Exception as e:
        logger.error(f"Error checking period status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check period status: {str(e)}")

