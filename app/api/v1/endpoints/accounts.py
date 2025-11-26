"""
Finance Account management endpoints
RESTful API for chart of accounts management with clean architecture
"""

from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.repositories import AccountRepository
from ....core.dependency_container import container
from ..schemas.finance import (
    AccountCreate, AccountUpdate, Account, AccountHierarchy
)
from ..schemas.base import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=Account, status_code=201)
async def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new account in the chart of accounts.

    This endpoint allows creating a new account in the chart of accounts.
    """
    try:
        account_repo = container.resolve(AccountRepository)
        account = await account_repo.create(account_data.model_dump(), account_data.tenant_id)
        return Account.model_validate(account)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create account: {str(e)}")


@router.get("/", response_model=PaginatedResponse[Account])
async def list_accounts(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List accounts with pagination and filtering.

    Retrieve a paginated list of accounts with optional filtering by type and category.
    """
    try:
        account_repo = container.resolve(AccountRepository)

        # Use provided tenant_id or default to system for now
        effective_tenant_id = tenant_id or "system"

        accounts = await account_repo.get_all(
            effective_tenant_id,
            skip,
            limit,
            account_type=account_type,
            category=category
        )
        total = await account_repo.count(
            effective_tenant_id,
            account_type=account_type,
            category=category
        )

        return PaginatedResponse[Account](
            items=[Account.model_validate(account) for account in accounts],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list accounts: {str(e)}")


@router.get("/{account_id}", response_model=Account)
async def get_account(
    account_id: str,
    db: Session = Depends(get_db)
):
    """
    Get account by ID.

    Retrieve detailed information about a specific account.
    """
    try:
        account_repo = container.resolve(AccountRepository)
        account = await account_repo.get_by_id(account_id, "system")  # TODO: tenant context
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return Account.model_validate(account)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve account: {str(e)}")


@router.get("/number/{account_number}", response_model=Account)
async def get_account_by_number(
    account_number: str,
    db: Session = Depends(get_db)
):
    """
    Get account by account number.

    Retrieve account information using the account number.
    """
    try:
        account_repo = container.resolve(AccountRepository)
        account = await account_repo.get_by_number(account_number, "system")  # TODO: tenant context
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return Account.model_validate(account)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve account: {str(e)}")


@router.put("/{account_id}", response_model=Account)
async def update_account(
    account_id: str,
    account_data: AccountUpdate,
    db: Session = Depends(get_db)
):
    """
    Update account information.

    Modify account details such as name, type, or category.
    """
    try:
        account_repo = container.resolve(AccountRepository)
        account = await account_repo.update(account_id, account_data.model_dump(exclude_unset=True), "system")  # TODO: tenant context
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return Account.model_validate(account)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update account: {str(e)}")


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete account (soft delete).

    Mark an account as inactive. This is a soft delete operation.
    """
    try:
        account_repo = container.resolve(AccountRepository)
        success = await account_repo.delete(account_id, "system")  # TODO: tenant context
        if not success:
            raise HTTPException(status_code=404, detail="Account not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")


@router.get("/{account_id}/balance", response_model=dict)
async def get_account_balance(
    account_id: str,
    db: Session = Depends(get_db)
):
    """
    Get account balance.

    Retrieve the current balance of a specific account.
    """
    try:
        account_repo = container.resolve(AccountRepository)
        balance = await account_repo.get_balance(account_id, "system")  # TODO: tenant context
        return {"account_id": account_id, "balance": balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve account balance: {str(e)}")


@router.get("/hierarchy", response_model=List[AccountHierarchy])
async def get_accounts_hierarchy(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    db: Session = Depends(get_db)
):
    """
    Get accounts as hierarchical tree.

    Retrieve all accounts organized in a hierarchical structure based on parent_account_id.
    """
    try:
        from ....infrastructure.models import Account as AccountModel
        
        effective_tenant_id = tenant_id or "system"
        
        # Query all accounts
        query = db.query(AccountModel).filter(
            AccountModel.tenant_id == effective_tenant_id,
            AccountModel.is_active == True,
            AccountModel.deleted_at.is_(None)
        )
        
        if account_type:
            query = query.filter(AccountModel.account_type == account_type)
        
        all_accounts = query.all()
        
        # Build account map
        account_map: Dict[str, AccountHierarchy] = {}
        root_accounts: List[AccountHierarchy] = []
        
        # First pass: create all account objects
        from datetime import datetime
        for acc in all_accounts:
            account_dict = {
                "id": str(acc.id),
                "tenant_id": acc.tenant_id,
                "account_number": acc.account_number,
                "account_name": acc.account_name,
                "account_type": acc.account_type,
                "category": acc.category,
                "currency": getattr(acc, 'currency', 'EUR') or "EUR",
                "allow_manual_entries": getattr(acc, 'allow_manual_entries', True),
                "balance": float(acc.balance) if acc.balance else 0.0,
                "is_active": acc.is_active,
                "parent_account_id": str(acc.parent_account_id) if acc.parent_account_id else None,
                "created_at": acc.created_at if acc.created_at else datetime.now(),
                "updated_at": acc.updated_at if acc.updated_at else datetime.now(),
                "children": []
            }
            account_hierarchy = AccountHierarchy(**account_dict)
            account_map[str(acc.id)] = account_hierarchy
        
        # Second pass: build hierarchy
        for acc in all_accounts:
            account_hierarchy = account_map[str(acc.id)]
            if acc.parent_account_id:
                parent_id = str(acc.parent_account_id)
                if parent_id in account_map:
                    account_map[parent_id].children.append(account_hierarchy)
            else:
                root_accounts.append(account_hierarchy)
        
        return root_accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve account hierarchy: {str(e)}")
