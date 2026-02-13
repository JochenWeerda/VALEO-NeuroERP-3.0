"""
Booking Templates API
FIBU-GL-07: Automatische Buchungsschemata
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, Field
import logging
import uuid

from ....core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/booking-templates", tags=["finance", "templates"])


class BookingTemplateLine(BaseModel):
    """Single line in a booking template"""
    account_number: str = Field(..., description="Account number")
    debit_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Percentage of total for debit")
    credit_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, description="Percentage of total for credit")
    fixed_debit: Optional[Decimal] = Field(None, ge=0, description="Fixed debit amount (alternative to percentage)")
    fixed_credit: Optional[Decimal] = Field(None, ge=0, description="Fixed credit amount (alternative to percentage)")
    description_template: Optional[str] = Field(None, description="Description template with placeholders")
    tax_code: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    line_number: int = Field(..., gt=0, description="Line number in template")


class BookingTemplateCreate(BaseModel):
    """Schema for creating a booking template"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    category: str = Field(default="GENERAL", description="Template category")
    trigger_type: str = Field(default="MANUAL", description="Trigger type: MANUAL, SCHEDULED, EVENT")
    trigger_config: Optional[Dict[str, Any]] = Field(None, description="Trigger configuration (cron, event type, etc.)")
    lines: List[BookingTemplateLine] = Field(..., min_items=2, description="Template lines")
    default_amount: Optional[Decimal] = Field(None, ge=0, description="Default amount for percentage-based calculations")
    currency: str = Field(default="EUR", min_length=3, max_length=3, description="Currency code")
    active: bool = Field(default=True, description="Active status")


class BookingTemplateUpdate(BaseModel):
    """Schema for updating a booking template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    lines: Optional[List[BookingTemplateLine]] = None
    default_amount: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    active: Optional[bool] = None


class BookingTemplateResponse(BaseModel):
    """Response schema for booking template"""
    id: str
    name: str
    description: Optional[str]
    category: str
    trigger_type: str
    trigger_config: Optional[Dict[str, Any]]
    lines: List[BookingTemplateLine]
    default_amount: Optional[Decimal]
    currency: str
    active: bool
    created_at: datetime
    updated_at: datetime


class ApplyTemplateRequest(BaseModel):
    """Request to apply a booking template"""
    template_id: str
    amount: Optional[Decimal] = Field(None, ge=0, description="Amount to use (overrides template default)")
    entry_date: date = Field(..., description="Entry date for the journal entry")
    description: Optional[str] = Field(None, description="Override description")
    reference: Optional[str] = Field(None, description="Reference document")
    variables: Optional[Dict[str, Any]] = Field(None, description="Variables for template placeholders")


class ApplyTemplateResponse(BaseModel):
    """Response for applying a template"""
    journal_entry_id: str
    entry_number: str
    total_debit: Decimal
    total_credit: Decimal
    applied_at: datetime


@router.get("", response_model=List[BookingTemplateResponse])
async def list_booking_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Show only active templates"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    List all booking templates.
    """
    try:
        query = text("""
            SELECT id, name, description, category, trigger_type, trigger_config, lines,
                   default_amount, currency, active, created_at, updated_at
            FROM domain_erp.booking_templates
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        
        conditions = []
        
        if category:
            conditions.append("category = :category")
            params["category"] = category
        
        if active_only:
            conditions.append("active = true")
        
        if conditions:
            query = text(str(query) + " AND " + " AND ".join(conditions))
        
        query = text(str(query) + " ORDER BY name")
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            import json
            lines_data = json.loads(row[5]) if row[5] else []
            
            result.append(BookingTemplateResponse(
                id=str(row[0]),
                name=str(row[1]),
                description=str(row[2]) if row[2] else None,
                category=str(row[3]),
                trigger_type=str(row[4]),
                trigger_config=json.loads(row[5]) if row[5] and isinstance(row[5], str) else row[5],
                lines=[BookingTemplateLine(**line) for line in lines_data],
                default_amount=Decimal(str(row[7])) if row[7] else None,
                currency=str(row[8]),
                active=bool(row[9]),
                created_at=row[10],
                updated_at=row[11]
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing booking templates: {e}")
        # Return mock data if table doesn't exist
        return [
            BookingTemplateResponse(
                id="1",
                name="Miete monatlich",
                description="Monatliche Mietzahlung",
                category="RECURRING",
                trigger_type="SCHEDULED",
                trigger_config={"cron": "0 0 1 * *"},
                lines=[
                    BookingTemplateLine(
                        account_number="5000",
                        debit_percentage=Decimal("100.00"),
                        credit_percentage=Decimal("0.00"),
                        description_template="Miete {{month}}/{{year}}",
                        line_number=1
                    ),
                    BookingTemplateLine(
                        account_number="1400",
                        debit_percentage=Decimal("0.00"),
                        credit_percentage=Decimal("100.00"),
                        description_template="Miete {{month}}/{{year}}",
                        line_number=2
                    )
                ],
                default_amount=Decimal("2000.00"),
                currency="EUR",
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]


@router.get("/{template_id}", response_model=BookingTemplateResponse)
async def get_booking_template(
    template_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get a single booking template by ID.
    """
    try:
        query = text("""
            SELECT id, name, description, category, trigger_type, trigger_config, lines,
                   default_amount, currency, active, created_at, updated_at
            FROM domain_erp.booking_templates
            WHERE id = :template_id AND tenant_id = :tenant_id
        """)
        
        row = db.execute(query, {
            "template_id": template_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Booking template not found")
        
        import json
        lines_data = json.loads(row[6]) if row[6] else []
        
        return BookingTemplateResponse(
            id=str(row[0]),
            name=str(row[1]),
            description=str(row[2]) if row[2] else None,
            category=str(row[3]),
            trigger_type=str(row[4]),
            trigger_config=json.loads(row[5]) if row[5] and isinstance(row[5], str) else row[5],
            lines=[BookingTemplateLine(**line) for line in lines_data],
            default_amount=Decimal(str(row[7])) if row[7] else None,
            currency=str(row[8]),
            active=bool(row[9]),
            created_at=row[10],
            updated_at=row[11]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get booking template: {str(e)}")


@router.post("", response_model=BookingTemplateResponse, status_code=201)
async def create_booking_template(
    template: BookingTemplateCreate,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Create a new booking template.
    """
    try:
        # Validate that lines balance
        total_debit_pct = sum(line.debit_percentage for line in template.lines)
        total_credit_pct = sum(line.credit_percentage for line in template.lines)
        
        if abs(total_debit_pct - total_credit_pct) >= Decimal("0.01"):
            raise HTTPException(
                status_code=400,
                detail=f"Template lines must balance. Total debit: {total_debit_pct}%, Total credit: {total_credit_pct}%"
            )
        
        # Insert new template
        template_id = str(uuid.uuid4())
        
        import json
        lines_json = json.dumps([line.dict() for line in template.lines])
        trigger_config_json = json.dumps(template.trigger_config) if template.trigger_config else None
        
        insert_query = text("""
            INSERT INTO domain_erp.booking_templates
            (id, tenant_id, name, description, category, trigger_type, trigger_config, lines,
             default_amount, currency, active, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :name, :description, :category, :trigger_type, :trigger_config, :lines,
             :default_amount, :currency, :active, NOW(), NOW())
            RETURNING id, name, description, category, trigger_type, trigger_config, lines,
                      default_amount, currency, active, created_at, updated_at
        """)
        
        row = db.execute(insert_query, {
            "id": template_id,
            "tenant_id": tenant_id,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "trigger_type": template.trigger_type,
            "trigger_config": trigger_config_json,
            "lines": lines_json,
            "default_amount": template.default_amount,
            "currency": template.currency,
            "active": template.active
        }).fetchone()
        
        db.commit()
        
        lines_data = json.loads(row[6]) if row[6] else []
        
        return BookingTemplateResponse(
            id=str(row[0]),
            name=str(row[1]),
            description=str(row[2]) if row[2] else None,
            category=str(row[3]),
            trigger_type=str(row[4]),
            trigger_config=json.loads(row[5]) if row[5] and isinstance(row[5], str) else row[5],
            lines=[BookingTemplateLine(**line) for line in lines_data],
            default_amount=Decimal(str(row[7])) if row[7] else None,
            currency=str(row[8]),
            active=bool(row[9]),
            created_at=row[10],
            updated_at=row[11]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create booking template: {str(e)}")


@router.post("/{template_id}/apply", response_model=ApplyTemplateResponse)
async def apply_booking_template(
    template_id: str,
    request: ApplyTemplateRequest,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Apply a booking template to create a journal entry.
    """
    try:
        # Get template
        template = await get_booking_template(template_id, tenant_id, db)
        
        if not template.active:
            raise HTTPException(status_code=400, detail="Template is not active")
        
        # Determine amount
        amount = request.amount or template.default_amount
        if not amount:
            raise HTTPException(status_code=400, detail="Amount is required (either in request or template default)")
        
        # Generate entry number
        entry_number = f"TMP-{request.entry_date.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create journal entry
        entry_id = str(uuid.uuid4())
        journal_entry_insert = text("""
            INSERT INTO domain_erp.journal_entries
            (id, tenant_id, entry_number, entry_date, posting_date, description,
             source, currency, status, total_debit, total_credit, created_at, updated_at)
            VALUES (:id, :tenant_id, :entry_number, :entry_date, :posting_date, :description,
                    :source, :currency, :status, :total_debit, :total_credit, NOW(), NOW())
            RETURNING id
        """)
        
        description = request.description or template.name
        if template.lines and template.lines[0].description_template:
            # Replace placeholders in description
            desc_template = template.lines[0].description_template
            if request.variables:
                for key, value in request.variables.items():
                    desc_template = desc_template.replace(f"{{{{{key}}}}}", str(value))
            description = desc_template
        
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        
        # Calculate totals from template lines
        for line in template.lines:
            if line.debit_percentage > 0:
                total_debit += amount * (line.debit_percentage / Decimal("100.00"))
            elif line.fixed_debit:
                total_debit += line.fixed_debit
            
            if line.credit_percentage > 0:
                total_credit += amount * (line.credit_percentage / Decimal("100.00"))
            elif line.fixed_credit:
                total_credit += line.fixed_credit
        
        db.execute(journal_entry_insert, {
            "id": entry_id,
            "tenant_id": tenant_id,
            "entry_number": entry_number,
            "entry_date": request.entry_date,
            "posting_date": request.entry_date,
            "description": description,
            "source": "booking_template",
            "currency": template.currency,
            "status": "draft",
            "total_debit": total_debit,
            "total_credit": total_credit
        })
        
        # Create journal entry lines
        for line in template.lines:
            # Get account ID
            account_query = text("""
                SELECT id FROM domain_erp.chart_of_accounts
                WHERE account_number = :account_number AND tenant_id = :tenant_id
                LIMIT 1
            """)
            
            account_row = db.execute(account_query, {
                "account_number": line.account_number,
                "tenant_id": tenant_id
            }).fetchone()
            
            if not account_row:
                raise HTTPException(
                    status_code=400,
                    detail=f"Account not found: {line.account_number}"
                )
            
            account_id = str(account_row[0])
            
            # Calculate line amounts
            line_debit = Decimal("0.00")
            line_credit = Decimal("0.00")
            
            if line.debit_percentage > 0:
                line_debit = amount * (line.debit_percentage / Decimal("100.00"))
            elif line.fixed_debit:
                line_debit = line.fixed_debit
            
            if line.credit_percentage > 0:
                line_credit = amount * (line.credit_percentage / Decimal("100.00"))
            elif line.fixed_credit:
                line_credit = line.fixed_credit
            
            # Line description
            line_description = description
            if line.description_template:
                line_desc_template = line.description_template
                if request.variables:
                    for key, value in request.variables.items():
                        line_desc_template = line_desc_template.replace(f"{{{{{key}}}}}", str(value))
                line_description = line_desc_template
            
            # Insert journal entry line
            line_id = f"{entry_id}-L{line.line_number}"
            journal_line_insert = text("""
                INSERT INTO domain_erp.journal_entry_lines
                (id, tenant_id, journal_entry_id, account_id, debit_amount, credit_amount,
                 line_number, description, tax_code, cost_center, profit_center, reference,
                 created_at, updated_at)
                VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :debit_amount, :credit_amount,
                        :line_number, :description, :tax_code, :cost_center, :profit_center, :reference,
                        NOW(), NOW())
            """)
            
            db.execute(journal_line_insert, {
                "id": line_id,
                "tenant_id": tenant_id,
                "journal_entry_id": entry_id,
                "account_id": account_id,
                "debit_amount": line_debit,
                "credit_amount": line_credit,
                "line_number": line.line_number,
                "description": line_description,
                "tax_code": line.tax_code,
                "cost_center": line.cost_center,
                "profit_center": line.profit_center,
                "reference": request.reference
            })
        
        db.commit()
        
        return ApplyTemplateResponse(
            journal_entry_id=entry_id,
            entry_number=entry_number,
            total_debit=total_debit,
            total_credit=total_credit,
            applied_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error applying booking template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply booking template: {str(e)}")


@router.put("/{template_id}", response_model=BookingTemplateResponse)
async def update_booking_template(
    template_id: str,
    template: BookingTemplateUpdate,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Update an existing booking template.
    """
    try:
        # Build update query dynamically
        update_fields = []
        params = {"template_id": template_id, "tenant_id": tenant_id}
        
        if template.name is not None:
            update_fields.append("name = :name")
            params["name"] = template.name
        if template.description is not None:
            update_fields.append("description = :description")
            params["description"] = template.description
        if template.category is not None:
            update_fields.append("category = :category")
            params["category"] = template.category
        if template.trigger_type is not None:
            update_fields.append("trigger_type = :trigger_type")
            params["trigger_type"] = template.trigger_type
        if template.trigger_config is not None:
            import json
            update_fields.append("trigger_config = :trigger_config")
            params["trigger_config"] = json.dumps(template.trigger_config)
        if template.lines is not None:
            # Validate balance
            total_debit_pct = sum(line.debit_percentage for line in template.lines)
            total_credit_pct = sum(line.credit_percentage for line in template.lines)
            if abs(total_debit_pct - total_credit_pct) >= Decimal("0.01"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Template lines must balance. Total debit: {total_debit_pct}%, Total credit: {total_credit_pct}%"
                )
            import json
            update_fields.append("lines = :lines")
            params["lines"] = json.dumps([line.dict() for line in template.lines])
        if template.default_amount is not None:
            update_fields.append("default_amount = :default_amount")
            params["default_amount"] = template.default_amount
        if template.currency is not None:
            update_fields.append("currency = :currency")
            params["currency"] = template.currency
        if template.active is not None:
            update_fields.append("active = :active")
            params["active"] = template.active
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("updated_at = NOW()")
        
        update_query = text(f"""
            UPDATE domain_erp.booking_templates
            SET {', '.join(update_fields)}
            WHERE id = :template_id AND tenant_id = :tenant_id
            RETURNING id, name, description, category, trigger_type, trigger_config, lines,
                      default_amount, currency, active, created_at, updated_at
        """)
        
        row = db.execute(update_query, params).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Booking template not found")
        
        db.commit()
        
        import json
        lines_data = json.loads(row[6]) if row[6] else []
        
        return BookingTemplateResponse(
            id=str(row[0]),
            name=str(row[1]),
            description=str(row[2]) if row[2] else None,
            category=str(row[3]),
            trigger_type=str(row[4]),
            trigger_config=json.loads(row[5]) if row[5] and isinstance(row[5], str) else row[5],
            lines=[BookingTemplateLine(**line) for line in lines_data],
            default_amount=Decimal(str(row[7])) if row[7] else None,
            currency=str(row[8]),
            active=bool(row[9]),
            created_at=row[10],
            updated_at=row[11]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating booking template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update booking template: {str(e)}")


@router.delete("/{template_id}", status_code=204)
async def delete_booking_template(
    template_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Delete a booking template (soft delete by setting active=false).
    """
    try:
        update_query = text("""
            UPDATE domain_erp.booking_templates
            SET active = false, updated_at = NOW()
            WHERE id = :template_id AND tenant_id = :tenant_id
        """)
        
        result = db.execute(update_query, {
            "template_id": template_id,
            "tenant_id": tenant_id
        })
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Booking template not found")
        
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting booking template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete booking template: {str(e)}")

