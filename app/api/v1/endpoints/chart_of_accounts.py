"""
Chart of Accounts management endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import Account as AccountModel
from ..schemas.base import PaginatedResponse
from ..schemas.finance import Account

router = APIRouter()

DEFAULT_TENANT = "system"


@router.get("/", response_model=PaginatedResponse[Account])
async def list_accounts(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    search: Optional[str] = Query(None, description="Search in account number or name"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of chart-of-account entries."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(AccountModel).filter(AccountModel.is_active == True)  # noqa: E712
    query = query.filter(AccountModel.tenant_id == effective_tenant)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (AccountModel.account_number.ilike(like)) | (AccountModel.account_name.ilike(like))
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse[Account](
        items=[Account.model_validate(item) for item in items],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{account_id}", response_model=Account)
async def get_account(account_id: str, db: Session = Depends(get_db)):
    """Fetch a single account by identifier."""
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return Account.model_validate(account)

