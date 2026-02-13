"""
Bank Account management endpoints
RESTful API for bank account master data management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal

from ....core.database import get_db
from ..schemas.finance import BankAccount, BankAccountCreate, BankAccountUpdate
from ..schemas.base import PaginatedResponse

router = APIRouter(prefix="/bank-accounts", tags=["finance", "bank-accounts"])


@router.post("/", response_model=BankAccount, status_code=201)
async def create_bank_account(
    account_data: BankAccountCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new bank account.
    """
    try:
        # Check if account number already exists
        check_query = text("""
            SELECT id FROM domain_erp.bank_accounts 
            WHERE account_number = :account_number AND tenant_id = :tenant_id
        """)
        existing = db.execute(
            check_query,
            {
                "account_number": account_data.account_number,
                "tenant_id": account_data.tenant_id
            }
        ).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Bank account with number {account_data.account_number} already exists"
            )

        # Insert new bank account
        insert_query = text("""
            INSERT INTO domain_erp.bank_accounts 
            (tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active)
            VALUES (:tenant_id, :account_number, :bank_name, :iban, :bic, :currency, :balance, :is_active)
            RETURNING id, tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active, created_at, updated_at
        """)
        
        result = db.execute(
            insert_query,
            {
                "tenant_id": account_data.tenant_id,
                "account_number": account_data.account_number,
                "bank_name": account_data.bank_name,
                "iban": account_data.iban,
                "bic": account_data.bic,
                "currency": account_data.currency or "EUR",
                "balance": account_data.balance or Decimal("0.00"),
                "is_active": account_data.is_active if account_data.is_active is not None else True
            }
        ).fetchone()
        
        db.commit()
        
        return BankAccount(
            id=str(result[0]),
            tenant_id=result[1],
            account_number=result[2],
            bank_name=result[3],
            iban=result[4],
            bic=result[5],
            currency=result[6],
            balance=float(result[7]) if result[7] else 0.0,
            is_active=result[8],
            created_at=result[9].isoformat() if result[9] else None,
            updated_at=result[10].isoformat() if result[10] else None
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create bank account: {str(e)}")


@router.get("/", response_model=PaginatedResponse[BankAccount])
async def list_bank_accounts(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List bank accounts with pagination and filtering.
    """
    try:
        effective_tenant_id = tenant_id or "system"
        
        # Build query
        where_clauses = ["tenant_id = :tenant_id"]
        params = {"tenant_id": effective_tenant_id}
        
        if is_active is not None:
            where_clauses.append("is_active = :is_active")
            params["is_active"] = is_active
        
        where_sql = " AND ".join(where_clauses)
        
        # Count total
        count_query = text(f"""
            SELECT COUNT(*) FROM domain_erp.bank_accounts WHERE {where_sql}
        """)
        total = db.execute(count_query, params).scalar()
        
        # Get paginated results
        list_query = text(f"""
            SELECT id, tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active, created_at, updated_at
            FROM domain_erp.bank_accounts
            WHERE {where_sql}
            ORDER BY account_number
            LIMIT :limit OFFSET :skip
        """)
        params.update({"limit": limit, "skip": skip})
        
        rows = db.execute(list_query, params).fetchall()
        
        accounts = [
            BankAccount(
                id=str(row[0]),
                tenant_id=row[1],
                account_number=row[2],
                bank_name=row[3],
                iban=row[4],
                bic=row[5],
                currency=row[6],
                balance=float(row[7]) if row[7] else 0.0,
                is_active=row[8],
                created_at=row[9].isoformat() if row[9] else None,
                updated_at=row[10].isoformat() if row[10] else None
            )
            for row in rows
        ]
        
        return PaginatedResponse[BankAccount](
            items=accounts,
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit if total > 0 else 1,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list bank accounts: {str(e)}")


@router.get("/{account_id}", response_model=BankAccount)
async def get_bank_account(
    account_id: str,
    db: Session = Depends(get_db)
):
    """
    Get bank account by ID.
    """
    try:
        query = text("""
            SELECT id, tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active, created_at, updated_at
            FROM domain_erp.bank_accounts
            WHERE id = :account_id
        """)
        
        row = db.execute(query, {"account_id": account_id}).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        return BankAccount(
            id=str(row[0]),
            tenant_id=row[1],
            account_number=row[2],
            bank_name=row[3],
            iban=row[4],
            bic=row[5],
            currency=row[6],
            balance=float(row[7]) if row[7] else 0.0,
            is_active=row[8],
            created_at=row[9].isoformat() if row[9] else None,
            updated_at=row[10].isoformat() if row[10] else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bank account: {str(e)}")


@router.put("/{account_id}", response_model=BankAccount)
async def update_bank_account(
    account_id: str,
    account_data: BankAccountUpdate,
    db: Session = Depends(get_db)
):
    """
    Update bank account information.
    """
    try:
        # Check if account exists
        existing = db.execute(
            text("SELECT id FROM domain_erp.bank_accounts WHERE id = :account_id"),
            {"account_id": account_id}
        ).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Build update query dynamically
        update_fields = []
        params = {"account_id": account_id}
        
        if account_data.bank_name is not None:
            update_fields.append("bank_name = :bank_name")
            params["bank_name"] = account_data.bank_name
        
        if account_data.iban is not None:
            update_fields.append("iban = :iban")
            params["iban"] = account_data.iban
        
        if account_data.bic is not None:
            update_fields.append("bic = :bic")
            params["bic"] = account_data.bic
        
        if account_data.currency is not None:
            update_fields.append("currency = :currency")
            params["currency"] = account_data.currency
        
        if account_data.balance is not None:
            update_fields.append("balance = :balance")
            params["balance"] = Decimal(str(account_data.balance))
        
        if account_data.is_active is not None:
            update_fields.append("is_active = :is_active")
            params["is_active"] = account_data.is_active
        
        if not update_fields:
            # No fields to update, return existing account
            return await get_bank_account(account_id, db)
        
        update_fields.append("updated_at = NOW()")
        
        update_query = text(f"""
            UPDATE domain_erp.bank_accounts
            SET {', '.join(update_fields)}
            WHERE id = :account_id
            RETURNING id, tenant_id, account_number, bank_name, iban, bic, currency, balance, is_active, created_at, updated_at
        """)
        
        result = db.execute(update_query, params).fetchone()
        db.commit()
        
        return BankAccount(
            id=str(result[0]),
            tenant_id=result[1],
            account_number=result[2],
            bank_name=result[3],
            iban=result[4],
            bic=result[5],
            currency=result[6],
            balance=float(result[7]) if result[7] else 0.0,
            is_active=result[8],
            created_at=result[9].isoformat() if result[9] else None,
            updated_at=result[10].isoformat() if result[10] else None
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update bank account: {str(e)}")


@router.delete("/{account_id}", status_code=204)
async def delete_bank_account(
    account_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete bank account (soft delete by setting is_active = false).
    """
    try:
        # Check if account exists
        existing = db.execute(
            text("SELECT id FROM domain_erp.bank_accounts WHERE id = :account_id"),
            {"account_id": account_id}
        ).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        # Soft delete
        update_query = text("""
            UPDATE domain_erp.bank_accounts
            SET is_active = false, updated_at = NOW()
            WHERE id = :account_id
        """)
        
        db.execute(update_query, {"account_id": account_id})
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete bank account: {str(e)}")

