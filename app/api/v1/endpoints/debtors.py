"""
Debtor (Debitoren) master data management endpoints
RESTful API for debtor master data management
Adapted to existing database schema (debitor_number, name, address JSONB)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
import json

from ....core.database import get_db
from ..schemas.finance import Debtor, DebtorCreate, DebtorUpdate
from ..schemas.base import PaginatedResponse

router = APIRouter(prefix="/debtors", tags=["finance", "debtors"])


def _parse_address_jsonb(address_jsonb) -> dict:
    """Parse address JSONB field"""
    if address_jsonb is None:
        return {}
    if isinstance(address_jsonb, str):
        return json.loads(address_jsonb)
    return address_jsonb


def _build_address_jsonb(debtor_data) -> str:
    """Build address JSONB from debtor data"""
    address_data = {
        "contact_person": debtor_data.contact_person,
        "street": debtor_data.street,
        "postal_code": debtor_data.postal_code,
        "city": debtor_data.city,
        "country": debtor_data.country or "DE",
        "phone": debtor_data.phone,
        "email": debtor_data.email,
        "vat_id": debtor_data.vat_id,
        "tax_number": debtor_data.tax_number,
        "iban": debtor_data.iban,
        "bic": debtor_data.bic,
        "bank_name": debtor_data.bank_name,
        "account_holder": debtor_data.account_holder,
        "payment_terms_days": debtor_data.payment_terms_days or 30,
        "discount_days": debtor_data.discount_days or 0,
        "discount_percent": float(debtor_data.discount_percent) if debtor_data.discount_percent else 0.0,
        "notes": debtor_data.notes
    }
    return json.dumps(address_data)


def _row_to_debtor(row) -> Debtor:
    """Convert database row to Debtor schema"""
    address_data = _parse_address_jsonb(row[4])  # address column
    
    return Debtor(
        id=str(row[0]),
        tenant_id=row[1],
        debtor_number=row[2],  # debitor_number
        company_name=row[3],  # name
        contact_person=address_data.get("contact_person"),
        street=address_data.get("street", ""),
        postal_code=address_data.get("postal_code", ""),
        city=address_data.get("city", ""),
        country=address_data.get("country", "DE"),
        phone=address_data.get("phone"),
        email=address_data.get("email"),
        vat_id=address_data.get("vat_id"),
        tax_number=address_data.get("tax_number"),
        iban=address_data.get("iban"),
        bic=address_data.get("bic"),
        bank_name=address_data.get("bank_name"),
        account_holder=address_data.get("account_holder"),
        payment_terms_days=address_data.get("payment_terms_days", 30),
        discount_days=address_data.get("discount_days", 0),
        discount_percent=Decimal(str(address_data.get("discount_percent", 0.0))),
        credit_limit=float(row[6]) if row[6] else 0.0,  # credit_limit column
        is_active=row[7],  # is_active column
        notes=address_data.get("notes"),
        created_at=row[8].isoformat() if row[8] else None,
        updated_at=row[9].isoformat() if row[9] else None
    )


@router.post("/", response_model=Debtor, status_code=201)
async def create_debtor(
    debtor_data: DebtorCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new debtor.
    """
    try:
        # Check if debtor number already exists
        check_query = text("""
            SELECT id FROM domain_erp.debitors 
            WHERE debitor_number = :debtor_number AND tenant_id = :tenant_id
        """)
        existing = db.execute(
            check_query,
            {
                "debtor_number": debtor_data.debtor_number,
                "tenant_id": debtor_data.tenant_id
            }
        ).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Debtor with number {debtor_data.debtor_number} already exists"
            )

        # Insert new debtor
        address_json = _build_address_jsonb(debtor_data)
        payment_terms = f"{debtor_data.payment_terms_days or 30}_days"
        
        insert_query = text("""
            INSERT INTO domain_erp.debitors 
            (tenant_id, debitor_number, name, address, payment_terms, credit_limit, is_active)
            VALUES (:tenant_id, :debtor_number, :company_name, :address::jsonb, :payment_terms, :credit_limit, :is_active)
            RETURNING id, tenant_id, debitor_number, name, address, payment_terms, credit_limit, 
                      is_active, created_at, updated_at
        """)
        
        result = db.execute(
            insert_query,
            {
                "tenant_id": debtor_data.tenant_id,
                "debtor_number": debtor_data.debtor_number,
                "company_name": debtor_data.company_name,
                "address": address_json,
                "payment_terms": payment_terms,
                "credit_limit": debtor_data.credit_limit or Decimal("0.00"),
                "is_active": debtor_data.is_active if debtor_data.is_active is not None else True
            }
        ).fetchone()
        
        db.commit()
        
        return _row_to_debtor(result)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create debtor: {str(e)}")


@router.get("/", response_model=PaginatedResponse[Debtor])
async def list_debtors(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in company name, debtor number"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List debtors with pagination and filtering.
    """
    try:
        effective_tenant_id = tenant_id or "system"
        
        # Build query
        where_clauses = ["tenant_id = :tenant_id"]
        params = {"tenant_id": effective_tenant_id}
        
        if is_active is not None:
            where_clauses.append("is_active = :is_active")
            params["is_active"] = is_active
        
        if search:
            where_clauses.append("(name ILIKE :search OR debitor_number ILIKE :search)")
            params["search"] = f"%{search}%"
        
        where_sql = " AND ".join(where_clauses)
        
        # Count total
        count_query = text(f"""
            SELECT COUNT(*) FROM domain_erp.debitors WHERE {where_sql}
        """)
        total = db.execute(count_query, params).scalar()
        
        # Get paginated results
        list_query = text(f"""
            SELECT id, tenant_id, debitor_number, name, address, payment_terms, credit_limit, 
                   is_active, created_at, updated_at
            FROM domain_erp.debitors
            WHERE {where_sql}
            ORDER BY debitor_number
            LIMIT :limit OFFSET :skip
        """)
        params.update({"limit": limit, "skip": skip})
        
        rows = db.execute(list_query, params).fetchall()
        
        debtors = [_row_to_debtor(row) for row in rows]
        
        return PaginatedResponse[Debtor](
            items=debtors,
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=(total + limit - 1) // limit if total > 0 else 1,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list debtors: {str(e)}")


@router.get("/{debtor_id}", response_model=Debtor)
async def get_debtor(
    debtor_id: str,
    db: Session = Depends(get_db)
):
    """
    Get debtor by ID.
    """
    try:
        query = text("""
            SELECT id, tenant_id, debitor_number, name, address, payment_terms, credit_limit, 
                   is_active, created_at, updated_at
            FROM domain_erp.debitors
            WHERE id = :debtor_id
        """)
        
        row = db.execute(query, {"debtor_id": debtor_id}).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Debtor not found")
        
        return _row_to_debtor(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve debtor: {str(e)}")


@router.put("/{debtor_id}", response_model=Debtor)
async def update_debtor(
    debtor_id: str,
    debtor_data: DebtorUpdate,
    db: Session = Depends(get_db)
):
    """
    Update debtor information.
    """
    try:
        # Get existing debtor
        existing_query = text("""
            SELECT id, tenant_id, debitor_number, name, address, payment_terms, credit_limit, 
                   is_active, created_at, updated_at
            FROM domain_erp.debitors
            WHERE id = :debtor_id
        """)
        existing_row = db.execute(existing_query, {"debtor_id": debtor_id}).fetchone()
        
        if not existing_row:
            raise HTTPException(status_code=404, detail="Debtor not found")
        
        # Parse existing address
        existing_debtor = _row_to_debtor(existing_row)
        existing_address = _parse_address_jsonb(existing_row[4])
        
        # Merge updates
        updated_address = existing_address.copy()
        if debtor_data.contact_person is not None:
            updated_address["contact_person"] = debtor_data.contact_person
        if debtor_data.street is not None:
            updated_address["street"] = debtor_data.street
        if debtor_data.postal_code is not None:
            updated_address["postal_code"] = debtor_data.postal_code
        if debtor_data.city is not None:
            updated_address["city"] = debtor_data.city
        if debtor_data.country is not None:
            updated_address["country"] = debtor_data.country
        if debtor_data.phone is not None:
            updated_address["phone"] = debtor_data.phone
        if debtor_data.email is not None:
            updated_address["email"] = debtor_data.email
        if debtor_data.vat_id is not None:
            updated_address["vat_id"] = debtor_data.vat_id
        if debtor_data.tax_number is not None:
            updated_address["tax_number"] = debtor_data.tax_number
        if debtor_data.iban is not None:
            updated_address["iban"] = debtor_data.iban
        if debtor_data.bic is not None:
            updated_address["bic"] = debtor_data.bic
        if debtor_data.bank_name is not None:
            updated_address["bank_name"] = debtor_data.bank_name
        if debtor_data.account_holder is not None:
            updated_address["account_holder"] = debtor_data.account_holder
        if debtor_data.payment_terms_days is not None:
            updated_address["payment_terms_days"] = debtor_data.payment_terms_days
        if debtor_data.discount_days is not None:
            updated_address["discount_days"] = debtor_data.discount_days
        if debtor_data.discount_percent is not None:
            updated_address["discount_percent"] = float(debtor_data.discount_percent)
        if debtor_data.notes is not None:
            updated_address["notes"] = debtor_data.notes
        
        # Build update query
        update_fields = []
        params = {"debtor_id": debtor_id}
        
        # Note: We can't update company_name directly as it's stored in 'name' column
        # For now, we'll keep it as-is unless explicitly needed
        
        if debtor_data.credit_limit is not None:
            update_fields.append("credit_limit = :credit_limit")
            params["credit_limit"] = Decimal(str(debtor_data.credit_limit))
        
        if debtor_data.is_active is not None:
            update_fields.append("is_active = :is_active")
            params["is_active"] = debtor_data.is_active
        
        # Always update address JSONB
        update_fields.append("address = :address::jsonb")
        params["address"] = json.dumps(updated_address)
        
        # Update payment_terms if payment_terms_days changed
        payment_terms_days = updated_address.get("payment_terms_days", 30)
        update_fields.append("payment_terms = :payment_terms")
        params["payment_terms"] = f"{payment_terms_days}_days"
        
        update_fields.append("updated_at = NOW()")
        
        update_query = text(f"""
            UPDATE domain_erp.debitors
            SET {', '.join(update_fields)}
            WHERE id = :debtor_id
            RETURNING id, tenant_id, debitor_number, name, address, payment_terms, credit_limit, 
                      is_active, created_at, updated_at
        """)
        
        result = db.execute(update_query, params).fetchone()
        db.commit()
        
        return _row_to_debtor(result)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update debtor: {str(e)}")


@router.delete("/{debtor_id}", status_code=204)
async def delete_debtor(
    debtor_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete debtor (soft delete by setting is_active = false).
    """
    try:
        # Check if debtor exists
        existing = db.execute(
            text("SELECT id FROM domain_erp.debitors WHERE id = :debtor_id"),
            {"debtor_id": debtor_id}
        ).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Debtor not found")
        
        # Soft delete
        update_query = text("""
            UPDATE domain_erp.debitors
            SET is_active = false, updated_at = NOW()
            WHERE id = :debtor_id
        """)
        
        db.execute(update_query, {"debtor_id": debtor_id})
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete debtor: {str(e)}")
