"""CRM Service Cases API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.session import get_db
from ....schemas.case import Case, CaseCreate, CaseUpdate, CaseHistory
from ....schemas.base import PaginatedResponse
from ....db.models import Case as CaseModel, CaseHistory as CaseHistoryModel

router = APIRouter()


@router.post("/", response_model=Case, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new support case."""
    # Generate case number
    case_number = f"CASE-{UUID(case_data.tenant_id).hex[:8].upper()}"

    case = CaseModel(**case_data.model_dump(), case_number=case_number)
    db.add(case)
    await db.commit()
    await db.refresh(case)

    # Create initial history entry
    history = CaseHistoryModel(
        case_id=case.id,
        action="created",
        performed_by="system",
        notes="Case created"
    )
    db.add(history)
    await db.commit()

    return Case.model_validate(case)


@router.get("/", response_model=PaginatedResponse[Case])
async def list_cases(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List support cases with pagination and filtering."""
    filters = []
    if tenant_id:
        filters.append(CaseModel.tenant_id == tenant_id)
    if status:
        filters.append(CaseModel.status == status)
    if priority:
        filters.append(CaseModel.priority == priority)
    if assigned_to:
        filters.append(CaseModel.assigned_to == assigned_to)
    if customer_id:
        filters.append(CaseModel.customer_id == customer_id)

    count_stmt = select(func.count()).select_from(CaseModel)
    if filters:
        count_stmt = count_stmt.where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = select(CaseModel)
    if filters:
        stmt = stmt.where(*filters)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    cases = result.scalars().all()

    current_page = (skip // limit) + 1
    total_pages = max(1, (total + limit - 1) // limit) if total else 1

    return PaginatedResponse[Case](
        items=[Case.model_validate(case) for case in cases],
        total=total,
        page=current_page,
        size=limit,
        pages=total_pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{case_id}", response_model=Case)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific support case by ID."""
    case = await db.get(CaseModel, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return Case.model_validate(case)


@router.put("/{case_id}", response_model=Case)
async def update_case(
    case_id: UUID,
    case_data: CaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a support case."""
    case = await db.get(CaseModel, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    update_data = case_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    await db.commit()
    await db.refresh(case)
    return Case.model_validate(case)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a support case."""
    case = await db.get(CaseModel, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    await db.delete(case)
    await db.commit()


@router.post("/{case_id}/escalate", response_model=dict)
async def escalate_case(
    case_id: UUID,
    reason: str = Query(..., description="Reason for escalation"),
    escalated_by: str = Query(..., description="User performing escalation"),
    db: AsyncSession = Depends(get_db)
):
    """Escalate a support case."""
    case = await db.get(CaseModel, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Update case status to escalated
    case.status = "escalated"

    # Create history entry
    history = CaseHistoryModel(
        case_id=case.id,
        action="escalated",
        performed_by=escalated_by,
        notes=f"Case escalated: {reason}"
    )
    db.add(history)

    await db.commit()
    await db.refresh(case)

    return {"message": "Case escalated successfully", "case_id": str(case_id)}


@router.get("/{case_id}/history", response_model=list[CaseHistory])
async def get_case_history(
    case_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get the history of changes for a case."""
    case = await db.get(CaseModel, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    stmt = select(CaseHistoryModel).where(CaseHistoryModel.case_id == case_id)
    result = await db.execute(stmt)
    history = result.scalars().all()
    return [CaseHistory.model_validate(entry) for entry in history]
