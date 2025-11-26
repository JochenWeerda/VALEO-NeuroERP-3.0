"""
Finance Journal Entry management endpoints
RESTful API for journal entry management with clean architecture
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from ....core.database import get_db
from ....infrastructure.repositories import JournalEntryRepository
from ....core.dependency_container import container
from ..schemas.finance import (
    JournalEntryCreate, JournalEntryUpdate, JournalEntry, JournalEntryLine
)
from ..schemas.base import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=JournalEntry, status_code=201)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new journal entry.

    This endpoint allows creating a new journal entry with multiple lines.
    The entry must balance (total debit = total credit).
    """
    try:
        # Validate that the entry balances
        total_debit = sum(line.debit_amount for line in entry_data.lines)
        total_credit = sum(line.credit_amount for line in entry_data.lines)

        if abs(total_debit - total_credit) > 0.01:  # Allow for small rounding differences
            raise HTTPException(
                status_code=400,
                detail=f"Journal entry does not balance. Debit: {total_debit}, Credit: {total_credit}"
            )

        # FIBU-GL-05: Check if period is open for bookings
        if entry_data.period:
            from sqlalchemy import text
            period_check = db.execute(
                text("""
                    SELECT status FROM finance_accounting_periods
                    WHERE tenant_id = :tenant_id AND period = :period
                """),
                {"tenant_id": entry_data.tenant_id, "period": entry_data.period}
            ).fetchone()

            if period_check and period_check[0] != "OPEN":
                raise HTTPException(
                    status_code=403,
                    detail=f"Period {entry_data.period} is {period_check[0]}. Bookings are blocked for closed periods."
                )

        entry_repo = container.resolve(JournalEntryRepository)

        # Create the entry data
        entry_dict = entry_data.model_dump()
        entry_dict['total_debit'] = total_debit
        entry_dict['total_credit'] = total_credit

        entry = await entry_repo.create(entry_dict, entry_data.tenant_id)
        return JournalEntry.model_validate(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create journal entry: {str(e)}")


@router.get("/", response_model=PaginatedResponse[JournalEntry])
async def list_journal_entries(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List journal entries with pagination and filtering.

    Retrieve a paginated list of journal entries with optional filtering.
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)

        # Use provided tenant_id or default to system for now
        effective_tenant_id = tenant_id or "system"

        # Convert date strings to datetime if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        entries = await entry_repo.get_entries_by_date_range(
            start_date, end_date, effective_tenant_id
        ) if start_date and end_date else await entry_repo.get_all(effective_tenant_id, skip, limit)

        # Apply status filter if provided
        if status:
            entries = [e for e in entries if e.status == status]

        # Apply pagination
        total = len(entries)
        paginated_entries = entries[skip:skip + limit]

        return PaginatedResponse[JournalEntry](
            items=[JournalEntry.model_validate(entry) for entry in paginated_entries],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list journal entries: {str(e)}")


@router.get("/{entry_id}", response_model=JournalEntry)
async def get_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Get journal entry by ID.

    Retrieve detailed information about a specific journal entry including all lines.
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)
        entry = await entry_repo.get_by_id(entry_id, "system")  # TODO: tenant context
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        return JournalEntry.model_validate(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve journal entry: {str(e)}")


@router.put("/{entry_id}", response_model=JournalEntry)
async def update_journal_entry(
    entry_id: str,
    entry_data: JournalEntryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update journal entry information.

    Modify journal entry details. Note: Only draft entries can be modified.
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)

        # Check if entry is still in draft status
        existing_entry = await entry_repo.get_by_id(entry_id, "system")
        if not existing_entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        if existing_entry.status != "draft":
            raise HTTPException(status_code=400, detail="Only draft entries can be modified")

        entry = await entry_repo.update(entry_id, entry_data.model_dump(exclude_unset=True), "system")  # TODO: tenant context
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        return JournalEntry.model_validate(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update journal entry: {str(e)}")


@router.post("/{entry_id}/post", response_model=JournalEntry)
async def post_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Post a journal entry.

    Change the status of a draft journal entry to posted.
    This will update account balances and make the entry permanent.
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)
        success = await entry_repo.post_entry(entry_id, "system")  # TODO: tenant context
        if not success:
            raise HTTPException(status_code=400, detail="Failed to post journal entry")

        # Return the updated entry
        entry = await entry_repo.get_by_id(entry_id, "system")
        return JournalEntry.model_validate(entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post journal entry: {str(e)}")


@router.post("/{entry_id}/reverse", response_model=dict)
async def reverse_journal_entry(
    entry_id: str,
    reason: str = Query(..., description="Reason for reversal"),
    db: Session = Depends(get_db)
):
    """
    Create a reversal entry.

    Create a new journal entry that reverses the original entry.
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)
        reversal_entry = await entry_repo.reverse_entry(entry_id, reason, "system")  # TODO: tenant context
        if not reversal_entry:
            raise HTTPException(status_code=400, detail="Failed to create reversal entry")

        return {
            "message": "Reversal entry created successfully",
            "original_entry_id": entry_id,
            "reversal_entry_id": reversal_entry.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reverse journal entry: {str(e)}")


@router.delete("/{entry_id}", status_code=204)
async def delete_journal_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete journal entry.

    Only draft entries can be deleted.
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)

        # Check if entry is still in draft status
        existing_entry = await entry_repo.get_by_id(entry_id, "system")
        if not existing_entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        if existing_entry.status != "draft":
            raise HTTPException(status_code=400, detail="Only draft entries can be deleted")

        success = await entry_repo.delete(entry_id, "system")  # TODO: tenant context
        if not success:
            raise HTTPException(status_code=404, detail="Journal entry not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete journal entry: {str(e)}")