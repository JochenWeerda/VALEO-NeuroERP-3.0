"""
Booking Templates API
FIBU-GL-07: Automatische Buchungsschemata
"""

from typing import List, Optional, Dict, Any
from fastapi import Response, APIRouter, Depends, HTTPException, Query, Request
from app.core.exceptions import kontosperre_meldung
from app.auth.finance_roles import finance_admin, finance_read, finance_write
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, Field
import logging
from app.core.uuid7 import uuid7
from app.core.exceptions import DomainError
from app.services.finance_transaction_service import FinanceTransactionService

from ....core.database import get_db
from app.core.tenant import get_tenant_id
from ....core.fibu_audit import log_fibu_audit

logger = logging.getLogger(__name__)



router = APIRouter(prefix="/booking-templates", tags=["finance", "templates"])

# Gemeinsame Vorlagen stehen allen Mandanten zur Verfuegung (Nutzerentscheidung 27.10.2026,
# docs/admin/rls-exceptions.json -> system_lesbar). Lesen und Anwenden ja, Aendern nein.
SHARED_TENANT = "system"


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
    lines: List[BookingTemplateLine] = Field(..., min_length=2, description="Template lines")
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
    shared: bool = Field(default=False, description="Gemeinsame Vorlage fuer alle Mandanten (nur lesen und anwenden)")


class ApplyTemplateRequest(BaseModel):
    """Request to apply a booking template"""
    template_id: Optional[str] = Field(None, description="Template ID (optional, taken from URL path)")
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


def _reject_shared(db: Session, template_id: str) -> None:
    """A shared template is visible but belongs to no tenant: changing it is refused, not 'not found'."""
    shared = db.execute(
        text("SELECT 1 FROM domain_erp.booking_templates WHERE id = :template_id AND tenant_id = :shared"),
        {"template_id": template_id, "shared": SHARED_TENANT},
    ).fetchone()
    if shared:
        raise HTTPException(status_code=403, detail="Gemeinsame Buchungsvorlage: nur lesen und anwenden, nicht aendern")


@router.get("", response_model=List[BookingTemplateResponse], summary="Booking templates auflisten", dependencies=[Depends(finance_read)])
async def list_booking_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Show only active templates"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    List all booking templates.
    """
    try:
        query = text("""
            SELECT id, name, description, category, trigger_type, trigger_config, lines,
                   default_amount, currency, active, created_at, updated_at, tenant_id = :shared
            FROM domain_erp.booking_templates
            WHERE tenant_id IN (:tenant_id, :shared)
        """)
        
        params = {"tenant_id": tenant_id, "shared": SHARED_TENANT}
        
        conditions = []
        
        if category:
            conditions.append("category = :category")
            params["category"] = category
        
        if active_only:
            conditions.append("active = true")
        
        if conditions:
            query = text(str(query) + " AND " + " AND ".join(conditions))  # nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden
        
        query = text(str(query) + " ORDER BY name")  # nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            import json
            lines_raw = row[6]
            lines_data = json.loads(lines_raw) if isinstance(lines_raw, str) else (lines_raw or [])
            trigger_raw = row[5]
            trigger_config = json.loads(trigger_raw) if isinstance(trigger_raw, str) else (trigger_raw or {})

            result.append(BookingTemplateResponse(
                id=str(row[0]),
                name=str(row[1]),
                description=str(row[2]) if row[2] else None,
                category=str(row[3]),
                trigger_type=str(row[4]),
                trigger_config=trigger_config,
                lines=[BookingTemplateLine(**line) for line in lines_data],
                default_amount=Decimal(str(row[7])) if row[7] else None,
                currency=str(row[8]),
                active=bool(row[9]),
                created_at=row[10],
                updated_at=row[11],
                shared=bool(row[12]),
            ))
        
        return result
        
    except Exception as e:
        # Bis 20.10.2026 wurde jeder Fehler zur leeren Liste — nicht von "keine Vorlagen" unterscheidbar.
        db.rollback()
        logger.error("Error listing booking templates: %s", e, exc_info=True)
        raise HTTPException(status_code=503, detail="Buchungsvorlagen derzeit nicht verfuegbar") from e


@router.get("/{template_id}", response_model=BookingTemplateResponse, summary="Booking template abrufen", dependencies=[Depends(finance_read)])
async def get_booking_template(
    template_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get a single booking template by ID.
    """
    try:
        query = text("""
            SELECT id, name, description, category, trigger_type, trigger_config, lines,
                   default_amount, currency, active, created_at, updated_at, tenant_id = :shared
            FROM domain_erp.booking_templates
            WHERE id = :template_id AND tenant_id IN (:tenant_id, :shared)
            ORDER BY tenant_id = :shared
            LIMIT 1
        """)
        
        row = db.execute(query, {
            "template_id": template_id,
            "tenant_id": tenant_id,
            "shared": SHARED_TENANT,
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Booking template not found")
        
        import json
        lines_raw = row[6]
        lines_data = json.loads(lines_raw) if isinstance(lines_raw, str) else (lines_raw or [])
        trigger_raw = row[5]
        trigger_config = json.loads(trigger_raw) if isinstance(trigger_raw, str) else (trigger_raw or {})

        return BookingTemplateResponse(
            id=str(row[0]),
            name=str(row[1]),
            description=str(row[2]) if row[2] else None,
            category=str(row[3]),
            trigger_type=str(row[4]),
            trigger_config=trigger_config,
            lines=[BookingTemplateLine(**line) for line in lines_data],
            default_amount=Decimal(str(row[7])) if row[7] else None,
            currency=str(row[8]),
            active=bool(row[9]),
            created_at=row[10],
            updated_at=row[11],
            shared=bool(row[12]),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get booking template: {str(e)}")


@router.post("", response_model=BookingTemplateResponse, status_code=201, summary="Booking template anlegen", dependencies=[Depends(finance_write)])
async def create_booking_template(
    template: BookingTemplateCreate,
    tenant_id: str = Depends(get_tenant_id),
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
        template_id = uuid7()
        
        import json
        lines_json = json.dumps([json.loads(line.model_dump_json()) for line in template.lines])
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
        
        # JSONB kommt von psycopg2 schon als Liste; json.loads darauf liess jede Anlage mit 500 scheitern (20.10.2026).
        lines_data = json.loads(row[6]) if isinstance(row[6], str) else (row[6] or [])
        
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


@router.post("/{template_id}/apply", response_model=ApplyTemplateResponse, summary="Booking template apply", dependencies=[Depends(finance_write)])
async def apply_booking_template(
    template_id: str,
    request: ApplyTemplateRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    http_request: Request = None,
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
        
        entry_number = f"TMP-{request.entry_date.strftime('%Y%m%d')}-{uuid7()[:6].upper()}"

        def _ersetze(vorlage: str) -> str:
            for key, value in (request.variables or {}).items():
                vorlage = vorlage.replace(f"{{{{{key}}}}}", str(value))
            return vorlage

        description = request.description or template.name
        if template.lines and template.lines[0].description_template:
            description = _ersetze(template.lines[0].description_template)

        def _betrag(prozent: Decimal, fest: Optional[Decimal]) -> Decimal:
            if prozent > 0:
                return (amount * (prozent / Decimal("100.00"))).quantize(Decimal("0.01"))
            return Decimal(str(fest or 0)).quantize(Decimal("0.01"))

        # Gebucht wird ueber den kanonischen Buchungsdienst (Periodensperre, eigene buchbare Konten, Belegbezug,
        # Sequenz und Hash). Bis 19.11.2026 schrieb dieser Weg Kopf und Zeilen roh, mit Konten auch des gemeinsamen
        # Kontenrahmens ("system") und ohne Periodenpruefung. Die Vorlage nennt Kontonummern; gebucht wird auf das
        # eigene Konto des Mandanten mit dieser Nummer.
        buchung = FinanceTransactionService(db, tenant_id, commit_on_success=False)
        try:
            zeilen = [
                {
                    "account_id": buchung.account_id_for_number(line.account_number),
                    "debit_amount": _betrag(line.debit_percentage, line.fixed_debit),
                    "credit_amount": _betrag(line.credit_percentage, line.fixed_credit),
                    "description": (_ersetze(line.description_template) if line.description_template else description)[:200],
                    "tax_code": line.tax_code, "cost_center": line.cost_center, "profit_center": line.profit_center,
                    "reference": request.reference,
                }
                for line in sorted(template.lines, key=lambda zeile: zeile.line_number)
            ]
            eintrag = buchung.create(
                entry_number=entry_number,
                description=description[:200],
                entry_date=request.entry_date,
                lines=zeilen,
                reference=request.reference,
                source="booking_template",
                currency=template.currency,
            )
        except DomainError as fehler:
            db.rollback()
            raise HTTPException(status_code=fehler.http_status, detail=str(fehler)) from fehler
        log_fibu_audit(
            db, tenant_id, "create", "journal_entry", str(eintrag.id),
            {"source": "booking_template", "template_id": template_id, "entry_number": entry_number},
            request=http_request,
        )
        db.commit()

        return ApplyTemplateResponse(
            journal_entry_id=str(eintrag.id),
            entry_number=entry_number,
            total_debit=eintrag.total_debit,
            total_credit=eintrag.total_credit,
            applied_at=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        sperre = kontosperre_meldung(e)
        if sperre:
            raise HTTPException(status_code=409, detail=sperre)
        logger.error(f"Error applying booking template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to apply booking template: {str(e)}")


@router.put("/{template_id}", response_model=BookingTemplateResponse, summary="Booking template aktualisieren", dependencies=[Depends(finance_write)])
async def update_booking_template(
    template_id: str,
    template: BookingTemplateUpdate,
    tenant_id: str = Depends(get_tenant_id),
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
            params["lines"] = json.dumps([json.loads(line.model_dump_json()) for line in template.lines])
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
        """)  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        
        row = db.execute(update_query, params).fetchone()
        
        if not row:
            _reject_shared(db, template_id)
            raise HTTPException(status_code=404, detail="Booking template not found")
        
        db.commit()
        
        import json
        lines_raw = row[6]
        lines_data = json.loads(lines_raw) if isinstance(lines_raw, str) else (lines_raw or [])
        trigger_raw = row[5]
        trigger_config = json.loads(trigger_raw) if isinstance(trigger_raw, str) else (trigger_raw or {})

        return BookingTemplateResponse(
            id=str(row[0]),
            name=str(row[1]),
            description=str(row[2]) if row[2] else None,
            category=str(row[3]),
            trigger_type=str(row[4]),
            trigger_config=trigger_config,
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


@router.delete("/{template_id}", status_code=204, response_class=Response, response_model=None, summary="Booking template löschen", dependencies=[Depends(finance_admin)])
async def delete_booking_template(
    template_id: str,
    tenant_id: str = Depends(get_tenant_id),
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
            _reject_shared(db, template_id)
            raise HTTPException(status_code=404, detail="Booking template not found")
        
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting booking template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete booking template: {str(e)}")

