"""
Closing Checklists API
FIBU-CLS-01: Abschlusschecklisten
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

router = APIRouter(prefix="/closing-checklists", tags=["finance", "closing"])


class ChecklistItem(BaseModel):
    """Single item in a closing checklist"""
    item_code: str = Field(..., description="Item code (e.g., GL-001, AR-001)")
    description: str = Field(..., description="Item description")
    category: str = Field(..., description="Category: GL, AR, AP, BANK, TAX, REPORTS")
    validation_type: str = Field(..., description="Validation type: manual, automatic, query")
    validation_query: Optional[str] = Field(None, description="SQL query for automatic validation")
    required: bool = Field(default=True, description="Required for closing")
    responsible_role: str = Field(..., description="Responsible role (e.g., accountant, controller)")
    due_date_offset: int = Field(default=0, description="Days before period end (negative = before, positive = after)")
    notes: Optional[str] = None


class ChecklistTemplateCreate(BaseModel):
    """Schema for creating a checklist template"""
    template_name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    closing_type: str = Field(..., description="Closing type: monthly, quarterly, yearly")
    items: List[ChecklistItem] = Field(..., min_items=1, description="Checklist items")
    active: bool = Field(default=True, description="Active status")


class ChecklistItemStatus(BaseModel):
    """Status of a checklist item"""
    item_code: str
    status: str  # pending, in_progress, completed, failed, skipped
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    validation_result: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ClosingChecklistCreate(BaseModel):
    """Schema for creating a closing checklist for a period"""
    period: str = Field(..., description="Period in YYYY-MM format")
    closing_type: str = Field(..., description="Closing type: monthly, quarterly, yearly")
    template_id: Optional[str] = Field(None, description="Template ID (if using template)")
    tenant_id: str = Field(default="system")


class ClosingChecklistResponse(BaseModel):
    """Response schema for closing checklist"""
    id: str
    period: str
    closing_type: str
    template_id: Optional[str]
    status: str  # draft, in_progress, completed, blocked
    progress_percentage: float
    total_items: int
    completed_items: int
    required_items: int
    completed_required_items: int
    items: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    completed_by: Optional[str]


class UpdateItemStatusRequest(BaseModel):
    """Request to update checklist item status"""
    item_code: str = Field(..., description="Item code")
    status: str = Field(..., description="Status: pending, in_progress, completed, failed, skipped")
    completed_by: str = Field(..., description="User completing the item")
    notes: Optional[str] = None


@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_checklist_templates(
    closing_type: Optional[str] = Query(None, description="Filter by closing type"),
    active_only: bool = Query(True, description="Show only active templates"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    List all checklist templates.
    """
    try:
        query = text("""
            SELECT id, template_name, description, closing_type, items, active, created_at, updated_at
            FROM domain_erp.closing_checklist_templates
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        
        if closing_type:
            query = text(str(query) + " AND closing_type = :closing_type")
            params["closing_type"] = closing_type
        
        if active_only:
            query = text(str(query) + " AND active = true")
        
        query = text(str(query) + " ORDER BY closing_type, template_name")
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            import json
            items_data = json.loads(row[4]) if row[4] else []
            
            result.append({
                "id": str(row[0]),
                "template_name": str(row[1]),
                "description": str(row[2]) if row[2] else None,
                "closing_type": str(row[3]),
                "items": items_data,
                "active": bool(row[5]),
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing checklist templates: {e}")
        # Return default templates if table doesn't exist
        return [
            {
                "id": "1",
                "template_name": "Standard Monatsabschluss",
                "description": "Standard-Checkliste für monatlichen Abschluss",
                "closing_type": "monthly",
                "items": [
                    {
                        "item_code": "GL-001",
                        "description": "Alle Buchungen für Periode erfasst",
                        "category": "GL",
                        "validation_type": "automatic",
                        "validation_query": "SELECT COUNT(*) FROM journal_entries WHERE period = :period AND status = 'draft'",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "GL-002",
                        "description": "Saldenvorträge geprüft",
                        "category": "GL",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "AR-001",
                        "description": "Debitoren-Abstimmung durchgeführt",
                        "category": "AR",
                        "validation_type": "automatic",
                        "validation_query": "SELECT COUNT(*) FROM offene_posten WHERE debtor_id IS NOT NULL AND offen > 0",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "AP-001",
                        "description": "Kreditoren-Abstimmung durchgeführt",
                        "category": "AP",
                        "validation_type": "automatic",
                        "validation_query": "SELECT COUNT(*) FROM offene_posten WHERE creditor_id IS NOT NULL AND offen > 0",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "BANK-001",
                        "description": "Bankabstimmung abgeschlossen",
                        "category": "BANK",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "TAX-001",
                        "description": "USt-Voranmeldung erstellt",
                        "category": "TAX",
                        "validation_type": "automatic",
                        "validation_query": "SELECT COUNT(*) FROM vat_returns WHERE period = :period AND status IN ('calculated', 'validated', 'submitted')",
                        "required": True,
                        "responsible_role": "controller",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "REP-001",
                        "description": "Monatsberichte erstellt",
                        "category": "REPORTS",
                        "validation_type": "manual",
                        "required": False,
                        "responsible_role": "controller",
                        "due_date_offset": 2
                    }
                ],
                "active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": "2",
                "template_name": "Standard Jahresabschluss",
                "description": "Standard-Checkliste für Jahresabschluss",
                "closing_type": "yearly",
                "items": [
                    {
                        "item_code": "GL-001",
                        "description": "Alle Buchungen für Jahr erfasst",
                        "category": "GL",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "GL-002",
                        "description": "Jahresabschlussbuchungen erstellt",
                        "category": "GL",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "controller",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "INV-001",
                        "description": "Inventur durchgeführt",
                        "category": "INVENTORY",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "warehouse_manager",
                        "due_date_offset": -7
                    },
                    {
                        "item_code": "AR-001",
                        "description": "Debitoren-Abstimmung abgeschlossen",
                        "category": "AR",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "AP-001",
                        "description": "Kreditoren-Abstimmung abgeschlossen",
                        "category": "AP",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "BANK-001",
                        "description": "Alle Bankabstimmungen abgeschlossen",
                        "category": "BANK",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "TAX-001",
                        "description": "Jahressteuererklärung vorbereitet",
                        "category": "TAX",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "controller",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "REP-001",
                        "description": "Jahresabschluss (Bilanz/GuV) erstellt",
                        "category": "REPORTS",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "controller",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "REP-002",
                        "description": "Anhang erstellt",
                        "category": "REPORTS",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "controller",
                        "due_date_offset": 5
                    }
                ],
                "active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]


@router.post("/templates", response_model=Dict[str, Any], status_code=201)
async def create_checklist_template(
    template: ChecklistTemplateCreate,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Create a new checklist template.
    """
    try:
        template_id = str(uuid.uuid4())
        
        import json
        items_json = json.dumps([item.dict() for item in template.items])
        
        insert_query = text("""
            INSERT INTO domain_erp.closing_checklist_templates
            (id, tenant_id, template_name, description, closing_type, items, active, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :template_name, :description, :closing_type, :items, :active, NOW(), NOW())
            RETURNING id, template_name, description, closing_type, items, active, created_at, updated_at
        """)
        
        row = db.execute(insert_query, {
            "id": template_id,
            "tenant_id": tenant_id,
            "template_name": template.template_name,
            "description": template.description,
            "closing_type": template.closing_type,
            "items": items_json,
            "active": template.active
        }).fetchone()
        
        db.commit()
        
        import json
        items_data = json.loads(row[4]) if row[4] else []
        
        return {
            "id": str(row[0]),
            "template_name": str(row[1]),
            "description": str(row[2]) if row[2] else None,
            "closing_type": str(row[3]),
            "items": items_data,
            "active": bool(row[5]),
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating checklist template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create checklist template: {str(e)}")


@router.post("", response_model=ClosingChecklistResponse, status_code=201)
async def create_closing_checklist(
    checklist: ClosingChecklistCreate,
    db: Session = Depends(get_db)
):
    """
    Create a closing checklist for a period.
    """
    try:
        checklist_id = str(uuid.uuid4())
        
        # Get template if provided
        items = []
        template_id = None
        
        if checklist.template_id:
            template_query = text("""
                SELECT id, items FROM domain_erp.closing_checklist_templates
                WHERE id = :template_id AND tenant_id = :tenant_id AND active = true
            """)
            
            template_row = db.execute(template_query, {
                "template_id": checklist.template_id,
                "tenant_id": checklist.tenant_id
            }).fetchone()
            
            if template_row:
                template_id = str(template_row[0])
                import json
                items = json.loads(template_row[1]) if template_row[1] else []
        
        # If no template, use default items based on closing type
        if not items:
            if checklist.closing_type == "yearly":
                items = [
                    {
                        "item_code": "GL-001",
                        "description": "Alle Buchungen für Jahr erfasst",
                        "category": "GL",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "AR-001",
                        "description": "Debitoren-Abstimmung abgeschlossen",
                        "category": "AR",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "AP-001",
                        "description": "Kreditoren-Abstimmung abgeschlossen",
                        "category": "AP",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "BANK-001",
                        "description": "Alle Bankabstimmungen abgeschlossen",
                        "category": "BANK",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "TAX-001",
                        "description": "Jahressteuererklärung vorbereitet",
                        "category": "TAX",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "controller",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "REP-001",
                        "description": "Jahresabschluss (Bilanz/GuV) erstellt",
                        "category": "REPORTS",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "controller",
                        "due_date_offset": 0,
                        "status": "pending"
                    }
                ]
            else:  # monthly or quarterly
                items = [
                    {
                        "item_code": "GL-001",
                        "description": "Alle Buchungen für Periode erfasst",
                        "category": "GL",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "AR-001",
                        "description": "Debitoren-Abstimmung durchgeführt",
                        "category": "AR",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "AP-001",
                        "description": "Kreditoren-Abstimmung durchgeführt",
                        "category": "AP",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "BANK-001",
                        "description": "Bankabstimmung abgeschlossen",
                        "category": "BANK",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "TAX-001",
                        "description": "USt-Voranmeldung erstellt",
                        "category": "TAX",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "controller",
                        "due_date_offset": 0,
                        "status": "pending"
                    }
                ]
        
        # Initialize all items with pending status
        for item in items:
            if "status" not in item:
                item["status"] = "pending"
        
        import json
        items_json = json.dumps(items)
        
        total_items = len(items)
        required_items = sum(1 for item in items if item.get("required", True))
        
        insert_query = text("""
            INSERT INTO domain_erp.closing_checklists
            (id, tenant_id, period, closing_type, template_id, status, progress_percentage,
             total_items, completed_items, required_items, completed_required_items,
             items, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :period, :closing_type, :template_id, :status, :progress_percentage,
             :total_items, :completed_items, :required_items, :completed_required_items,
             :items, NOW(), NOW())
            RETURNING id, period, closing_type, template_id, status, progress_percentage,
                      total_items, completed_items, required_items, completed_required_items,
                      items, created_at, updated_at, completed_at, completed_by
        """)
        
        row = db.execute(insert_query, {
            "id": checklist_id,
            "tenant_id": checklist.tenant_id,
            "period": checklist.period,
            "closing_type": checklist.closing_type,
            "template_id": template_id,
            "status": "draft",
            "progress_percentage": 0.0,
            "total_items": total_items,
            "completed_items": 0,
            "required_items": required_items,
            "completed_required_items": 0,
            "items": items_json
        }).fetchone()
        
        db.commit()
        
        import json
        items_data = json.loads(row[10]) if row[10] else []
        
        return ClosingChecklistResponse(
            id=str(row[0]),
            period=str(row[1]),
            closing_type=str(row[2]),
            template_id=str(row[3]) if row[3] else None,
            status=str(row[4]),
            progress_percentage=float(row[5]),
            total_items=int(row[6]),
            completed_items=int(row[7]),
            required_items=int(row[8]),
            completed_required_items=int(row[9]),
            items=items_data,
            created_at=row[11],
            updated_at=row[12],
            completed_at=row[13] if row[13] else None,
            completed_by=str(row[14]) if row[14] else None
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating closing checklist: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create closing checklist: {str(e)}")


@router.get("/{checklist_id}", response_model=ClosingChecklistResponse)
async def get_closing_checklist(
    checklist_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get a closing checklist by ID.
    """
    try:
        query = text("""
            SELECT id, period, closing_type, template_id, status, progress_percentage,
                   total_items, completed_items, required_items, completed_required_items,
                   items, created_at, updated_at, completed_at, completed_by
            FROM domain_erp.closing_checklists
            WHERE id = :checklist_id AND tenant_id = :tenant_id
        """)
        
        row = db.execute(query, {
            "checklist_id": checklist_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Closing checklist not found")
        
        import json
        items_data = json.loads(row[10]) if row[10] else []
        
        return ClosingChecklistResponse(
            id=str(row[0]),
            period=str(row[1]),
            closing_type=str(row[2]),
            template_id=str(row[3]) if row[3] else None,
            status=str(row[4]),
            progress_percentage=float(row[5]),
            total_items=int(row[6]),
            completed_items=int(row[7]),
            required_items=int(row[8]),
            completed_required_items=int(row[9]),
            items=items_data,
            created_at=row[11],
            updated_at=row[12],
            completed_at=row[13] if row[13] else None,
            completed_by=str(row[14]) if row[14] else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting closing checklist: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get closing checklist: {str(e)}")


@router.post("/{checklist_id}/items/{item_code}/complete")
async def complete_checklist_item(
    checklist_id: str,
    item_code: str,
    request: UpdateItemStatusRequest,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Complete a checklist item.
    """
    try:
        # Get checklist
        checklist = await get_closing_checklist(checklist_id, tenant_id, db)
        
        # Find item
        item_found = False
        updated_items = []
        
        for item in checklist.items:
            if item.get("item_code") == item_code:
                item_found = True
                item["status"] = request.status
                item["completed_by"] = request.completed_by
                item["completed_at"] = datetime.now().isoformat()
                if request.notes:
                    item["notes"] = request.notes
            updated_items.append(item)
        
        if not item_found:
            raise HTTPException(status_code=404, detail="Checklist item not found")
        
        # Recalculate progress
        completed_items = sum(1 for item in updated_items if item.get("status") == "completed")
        completed_required = sum(1 for item in updated_items if item.get("status") == "completed" and item.get("required", True))
        progress = (completed_items / checklist.total_items * 100) if checklist.total_items > 0 else 0.0
        
        # Update status
        new_status = "in_progress"
        if completed_required >= checklist.required_items:
            new_status = "completed"
        elif any(item.get("status") == "failed" for item in updated_items if item.get("required", True)):
            new_status = "blocked"
        
        import json
        items_json = json.dumps(updated_items)
        
        update_query = text("""
            UPDATE domain_erp.closing_checklists
            SET items = :items, completed_items = :completed_items,
                completed_required_items = :completed_required_items,
                progress_percentage = :progress_percentage, status = :status,
                completed_at = CASE WHEN :status = 'completed' THEN NOW() ELSE completed_at END,
                completed_by = CASE WHEN :status = 'completed' THEN :completed_by ELSE completed_by END,
                updated_at = NOW()
            WHERE id = :checklist_id AND tenant_id = :tenant_id
        """)
        
        db.execute(update_query, {
            "checklist_id": checklist_id,
            "tenant_id": tenant_id,
            "items": items_json,
            "completed_items": completed_items,
            "completed_required_items": completed_required,
            "progress_percentage": progress,
            "status": new_status,
            "completed_by": request.completed_by
        })
        
        db.commit()
        
        return await get_closing_checklist(checklist_id, tenant_id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error completing checklist item: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete checklist item: {str(e)}")


@router.post("/{checklist_id}/validate")
async def validate_checklist_items(
    checklist_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Automatically validate checklist items that have validation queries.
    """
    try:
        checklist = await get_closing_checklist(checklist_id, tenant_id, db)
        
        updated_items = []
        validation_results = []
        
        for item in checklist.items:
            if item.get("validation_type") == "automatic" and item.get("validation_query"):
                # Execute validation query
                try:
                    validation_query = item["validation_query"]
                    # Replace :period placeholder
                    validation_query = validation_query.replace(":period", f"'{checklist.period}'")
                    
                    result = db.execute(text(validation_query)).fetchone()
                    
                    # Determine if validation passed (assumes query returns count or boolean)
                    validation_passed = False
                    if result:
                        value = result[0] if isinstance(result, tuple) else result
                        if isinstance(value, (int, float)):
                            # If count is 0, validation passed (no issues found)
                            validation_passed = (value == 0)
                        elif isinstance(value, bool):
                            validation_passed = value
                    
                    item["validation_result"] = {
                        "passed": validation_passed,
                        "value": str(result[0]) if result else None,
                        "validated_at": datetime.now().isoformat()
                    }
                    
                    # Auto-update status if validation passed
                    if validation_passed and item.get("status") == "pending":
                        item["status"] = "completed"
                        item["completed_at"] = datetime.now().isoformat()
                        item["completed_by"] = "SYSTEM"
                    
                    validation_results.append({
                        "item_code": item.get("item_code"),
                        "passed": validation_passed,
                        "message": "Validation passed" if validation_passed else "Validation failed"
                    })
                    
                except Exception as e:
                    item["validation_result"] = {
                        "passed": False,
                        "error": str(e),
                        "validated_at": datetime.now().isoformat()
                    }
                    validation_results.append({
                        "item_code": item.get("item_code"),
                        "passed": False,
                        "message": f"Validation error: {str(e)}"
                    })
            
            updated_items.append(item)
        
        # Recalculate progress
        completed_items = sum(1 for item in updated_items if item.get("status") == "completed")
        completed_required = sum(1 for item in updated_items if item.get("status") == "completed" and item.get("required", True))
        progress = (completed_items / checklist.total_items * 100) if checklist.total_items > 0 else 0.0
        
        # Update status
        new_status = "in_progress"
        if completed_required >= checklist.required_items:
            new_status = "completed"
        
        import json
        items_json = json.dumps(updated_items)
        
        update_query = text("""
            UPDATE domain_erp.closing_checklists
            SET items = :items, completed_items = :completed_items,
                completed_required_items = :completed_required_items,
                progress_percentage = :progress_percentage, status = :status,
                updated_at = NOW()
            WHERE id = :checklist_id AND tenant_id = :tenant_id
        """)
        
        db.execute(update_query, {
            "checklist_id": checklist_id,
            "tenant_id": tenant_id,
            "items": items_json,
            "completed_items": completed_items,
            "completed_required_items": completed_required,
            "progress_percentage": progress,
            "status": new_status
        })
        
        db.commit()
        
        return {
            "checklist_id": checklist_id,
            "validation_results": validation_results,
            "updated_checklist": await get_closing_checklist(checklist_id, tenant_id, db)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error validating checklist: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate checklist: {str(e)}")


@router.get("", response_model=List[ClosingChecklistResponse])
async def list_closing_checklists(
    period: Optional[str] = Query(None, description="Filter by period (YYYY-MM)"),
    closing_type: Optional[str] = Query(None, description="Filter by closing type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    List all closing checklists.
    """
    try:
        query = text("""
            SELECT id, period, closing_type, template_id, status, progress_percentage,
                   total_items, completed_items, required_items, completed_required_items,
                   items, created_at, updated_at, completed_at, completed_by
            FROM domain_erp.closing_checklists
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        conditions = []
        
        if period:
            conditions.append("period = :period")
            params["period"] = period
        
        if closing_type:
            conditions.append("closing_type = :closing_type")
            params["closing_type"] = closing_type
        
        if status:
            conditions.append("status = :status")
            params["status"] = status
        
        if conditions:
            query = text(str(query) + " AND " + " AND ".join(conditions))
        
        query = text(str(query) + " ORDER BY period DESC, created_at DESC")
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            import json
            items_data = json.loads(row[10]) if row[10] else []
            
            result.append(ClosingChecklistResponse(
                id=str(row[0]),
                period=str(row[1]),
                closing_type=str(row[2]),
                template_id=str(row[3]) if row[3] else None,
                status=str(row[4]),
                progress_percentage=float(row[5]),
                total_items=int(row[6]),
                completed_items=int(row[7]),
                required_items=int(row[8]),
                completed_required_items=int(row[9]),
                items=items_data,
                created_at=row[11],
                updated_at=row[12],
                completed_at=row[13] if row[13] else None,
                completed_by=str(row[14]) if row[14] else None
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing closing checklists: {e}")
        return []

