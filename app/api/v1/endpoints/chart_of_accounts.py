"""
Chart of Accounts management endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import Account as AccountModel
from ..schemas.base import PaginatedResponse
from ..schemas.finance import Account, AccountCreate, AccountUpdate

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


@router.post("/", response_model=Account)
async def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Create a new account."""
    # Check if account number already exists
    existing = db.query(AccountModel).filter(
        AccountModel.account_number == account.account_number,
        AccountModel.tenant_id == account.tenant_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account number already exists")

    db_account = AccountModel(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return Account.model_validate(db_account)


@router.put("/{account_id}", response_model=Account)
async def update_account(
    account_id: str,
    account_update: AccountUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing account."""
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check if updating to an existing account number
    if account_update.account_name is not None:
        update_data = account_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)

    db.commit()
    db.refresh(account)
    return Account.model_validate(account)


@router.delete("/{account_id}")
async def delete_account(account_id: str, db: Session = Depends(get_db)):
    """Delete an account (soft delete by setting is_active to False)."""
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check if account has any journal entries
    if hasattr(account, 'journal_entry_lines') and account.journal_entry_lines:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete account with existing journal entries"
        )

    account.is_active = False
    db.commit()
    return {"message": "Account deactivated successfully"}

