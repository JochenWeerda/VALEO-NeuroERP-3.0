"""
Closing Checklists API
FIBU-CLS-01: Abschlusschecklisten
"""

from typing import Any, Dict, List, Optional
from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from app.core.uuid7 import uuid7

from ....core.database import get_db
from app.services.closing_checklists_service import (
    ChecklistItem,
    ChecklistTemplateCreate,
    ChecklistItemStatus,
    ClosingChecklistCreate,
    ClosingChecklistResponse,
    ClosingWorkspaceRequest,
    UpdateItemStatusRequest,
    build_closing_checklist_response,
    calculate_closing_workspace,
    close_closing_workspace,
    lock_closing_workspace,
)

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.closing_checklists_schemas import ClosingChecklistsOut


router = APIRouter(prefix="/closing-checklists", tags=["finance", "closing"])


@router.get("/templates", response_model=list[ClosingChecklistsOut], summary="Checklist templates auflisten")
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
                "description": "Standard-Checkliste fÃ¼r monatlichen Abschluss",
                "closing_type": "monthly",
                "items": [
                    {
                        "item_code": "GL-001",
                        "description": "Alle Buchungen fÃ¼r Periode erfasst",
                        "category": "GL",
                        "validation_type": "automatic",
                        "validation_query": "SELECT COUNT(*) FROM journal_entries WHERE period = :period AND status = 'draft'",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "GL-002",
                        "description": "SaldenvortrÃ¤ge geprÃ¼ft",
                        "category": "GL",
                        "validation_type": "manual",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "AR-001",
                        "description": "Debitoren-Abstimmung durchgefÃ¼hrt",
                        "category": "AR",
                        "validation_type": "automatic",
                        "validation_query": "SELECT COUNT(*) FROM offene_posten WHERE debtor_id IS NOT NULL AND offen > 0",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0
                    },
                    {
                        "item_code": "AP-001",
                        "description": "Kreditoren-Abstimmung durchgefÃ¼hrt",
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
                        "validation_query": (
                            "SELECT COUNT(*) FROM vat_returns "
                            "WHERE period = :period AND status IN ('calculated', 'validated', 'submitted')"
                        ),
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
                "description": "Standard-Checkliste fÃ¼r Jahresabschluss",
                "closing_type": "yearly",
                "items": [
                    {
                        "item_code": "GL-001",
                        "description": "Alle Buchungen fÃ¼r Jahr erfasst",
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
                        "description": "Inventur durchgefÃ¼hrt",
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
                        "description": "JahressteuererklÃ¤rung vorbereitet",
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


@router.post("/templates", response_model=ClosingChecklistsOut, status_code=201, summary="Checklist template anlegen")
async def create_checklist_template(
    template: ChecklistTemplateCreate,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Create a new checklist template.
    """
    try:
        template_id = uuid7()

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


@router.post("", response_model=ClosingChecklistResponse, status_code=201, summary="Closing checklist anlegen")
async def create_closing_checklist(
    checklist: ClosingChecklistCreate,
    db: Session = Depends(get_db)
):
    """
    Create a closing checklist for a period.
    """
    try:
        checklist_id = uuid7()

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
                        "description": "Alle Buchungen fÃ¼r Jahr erfasst",
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
                        "description": "JahressteuererklÃ¤rung vorbereitet",
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
                        "description": "Alle Buchungen fÃ¼r Periode erfasst",
                        "category": "GL",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "AR-001",
                        "description": "Debitoren-Abstimmung durchgefÃ¼hrt",
                        "category": "AR",
                        "validation_type": "automatic",
                        "required": True,
                        "responsible_role": "accountant",
                        "due_date_offset": 0,
                        "status": "pending"
                    },
                    {
                        "item_code": "AP-001",
                        "description": "Kreditoren-Abstimmung durchgefÃ¼hrt",
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

        return build_closing_checklist_response(row, items_data=items_data)

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating closing checklist: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create closing checklist: {str(e)}")


@router.get("/{checklist_id}", response_model=ClosingChecklistResponse, summary="Closing checklist abrufen")
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

        return build_closing_checklist_response(row, items_data=items_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting closing checklist: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get closing checklist: {str(e)}")


@router.post("/{checklist_id}/items/{item_code}/complete", summary="Checklist item complete",
    response_model=ClosingChecklistsOut
)
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


@router.post("/{checklist_id}/validate", summary="Checklist items validieren",
    response_model=ClosingChecklistsOut
)
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
                    # :period als gebundener Parameter â€” niemals per String-Ersatz interpolieren.
                    result = db.execute(
                        text(validation_query),
                        {"period": checklist.period},
                    ).fetchone()

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


@router.get("", response_model=List[ClosingChecklistResponse], summary="Closing checklists auflisten")
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

            result.append(build_closing_checklist_response(row, items_data=items_data))

        return result

    except Exception as e:
        logger.error(f"Error listing closing checklists: {e}")
        return []


@router.get("/cockpit/summary", response_model=ClosingChecklistsOut, summary="Closing cockpit summary abrufen")
async def get_closing_cockpit_summary(
    tenant_id: str = Query("system", description="Tenant ID"),
    period: Optional[str] = Query(None, description="Period in YYYY-MM"),
    db: Session = Depends(get_db),
):
    """
    Aggregated summary for Abschluss-Cockpit (period status + checklist progress + blockers).
    """
    result: Dict[str, Any] = {
        "tenant_id": tenant_id,
        "period": period,
        "periods": {"open": 0, "closed": 0, "adjusting": 0},
        "checklists": {"total": 0, "completed": 0, "in_progress": 0, "blocked": 0, "avg_progress": 0.0},
        "blockers": [],
        "latest_checklists": [],
    }
    try:
        period_query = text(
            """
            SELECT
              SUM(CASE WHEN status='OPEN' THEN 1 ELSE 0 END) AS open_cnt,
              SUM(CASE WHEN status='CLOSED' THEN 1 ELSE 0 END) AS closed_cnt,
              SUM(CASE WHEN status='ADJUSTING' THEN 1 ELSE 0 END) AS adjusting_cnt
            FROM finance_accounting_periods
            WHERE tenant_id=:tenant_id
            """
        )
        period_params = {"tenant_id": tenant_id}
        if period:
            period_query = text(str(period_query) + " AND period = :period")
            period_params["period"] = period
        period_row = db.execute(period_query, period_params).first()
        if period_row:
            result["periods"] = {
                "open": int(period_row[0] or 0),
                "closed": int(period_row[1] or 0),
                "adjusting": int(period_row[2] or 0),
            }
    except Exception as exc:
        logger.warning(f"cockpit-summary period aggregation failed: {exc}")

    try:
        cl_query = text(
            """
            SELECT
              COUNT(*) AS total_cnt,
              SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) AS completed_cnt,
              SUM(CASE WHEN status='in_progress' THEN 1 ELSE 0 END) AS in_progress_cnt,
              SUM(CASE WHEN status='blocked' THEN 1 ELSE 0 END) AS blocked_cnt,
              AVG(progress_percentage) AS avg_progress
            FROM domain_erp.closing_checklists
            WHERE tenant_id = :tenant_id
            """
        )
        cl_params = {"tenant_id": tenant_id}
        if period:
            cl_query = text(str(cl_query) + " AND period = :period")
            cl_params["period"] = period
        cl_row = db.execute(cl_query, cl_params).first()
        if cl_row:
            result["checklists"] = {
                "total": int(cl_row[0] or 0),
                "completed": int(cl_row[1] or 0),
                "in_progress": int(cl_row[2] or 0),
                "blocked": int(cl_row[3] or 0),
                "avg_progress": float(cl_row[4] or 0.0),
            }

        latest_rows = db.execute(
            text(
                """
                SELECT id, period, closing_type, status, progress_percentage, completed_required_items, required_items, updated_at
                FROM domain_erp.closing_checklists
                WHERE tenant_id=:tenant_id
                ORDER BY updated_at DESC
                LIMIT 10
                """
            ),
            {"tenant_id": tenant_id},
        ).fetchall()
        latest: list[Dict[str, Any]] = []
        blockers: list[Dict[str, Any]] = []
        for row in latest_rows:
            item = {
                "id": str(row[0]),
                "period": str(row[1]),
                "closing_type": str(row[2]),
                "status": str(row[3]),
                "progress_percentage": float(row[4] or 0.0),
                "completed_required_items": int(row[5] or 0),
                "required_items": int(row[6] or 0),
                "updated_at": row[7].isoformat() if row[7] else None,
            }
            latest.append(item)
            if item["status"] == "blocked" or item["completed_required_items"] < item["required_items"]:
                blockers.append(item)
        result["latest_checklists"] = latest
        result["blockers"] = blockers
    except Exception as exc:
        logger.warning(f"cockpit-summary checklist aggregation failed: {exc}")

    return result


@router.post("/{checklist_id}/approve", response_model=ClosingChecklistResponse, summary="Closing checklist genehmigen")
async def approve_closing_checklist(
    checklist_id: str,
    approved_by: str = Query("system", description="Approver user ID"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db),
):
    """Approve a completed checklist (completed â†’ approved)."""
    checklist = await get_closing_checklist(checklist_id, tenant_id, db)
    if checklist.status not in {"completed", "approved"}:
        raise HTTPException(
            status_code=400,
            detail=f"Only completed checklists can be approved (current: {checklist.status})",
        )
    db.execute(
        text("""
            UPDATE domain_erp.closing_checklists
            SET status = 'approved', completed_at = NOW(), completed_by = :approved_by, updated_at = NOW()
            WHERE id = :checklist_id AND tenant_id = :tenant_id
        """),
        {"checklist_id": checklist_id, "tenant_id": tenant_id, "approved_by": approved_by},
    )
    db.commit()
    return await get_closing_checklist(checklist_id, tenant_id, db)


@router.delete("/{checklist_id}", status_code=204, response_class=Response, response_model=None, summary="Closing checklist lÃ¶schen")
async def delete_closing_checklist(
    checklist_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db),
):
    """Delete a draft or in_progress checklist."""
    checklist = await get_closing_checklist(checklist_id, tenant_id, db)
    if checklist.status in {"approved", "completed"}:
        raise HTTPException(
            status_code=400,
            detail="Approved or completed checklists cannot be deleted",
        )
    db.execute(
        text("DELETE FROM domain_erp.closing_checklists WHERE id = :checklist_id AND tenant_id = :tenant_id"),
        {"checklist_id": checklist_id, "tenant_id": tenant_id},
    )
    db.commit()

