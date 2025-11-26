"""
AP Approval Workflow API
FIBU-AP-03: Prüf-/Freigabeworkflow
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

router = APIRouter(prefix="/ap/approval-workflow", tags=["finance", "ap", "approval"])


class ApprovalRuleCondition(BaseModel):
    """Condition for approval rule"""
    field: str = Field(..., description="Field to check (amount, material_group, supplier_id)")
    operator: str = Field(..., description="Operator (gt, gte, lt, lte, eq, in)")
    value: Any = Field(..., description="Value to compare")


class ApprovalRuleCreate(BaseModel):
    """Schema for creating an approval rule"""
    name: str = Field(..., min_length=1, max_length=100, description="Rule name")
    description: Optional[str] = Field(None, max_length=500, description="Rule description")
    conditions: List[ApprovalRuleCondition] = Field(..., min_items=1, description="Conditions that trigger this rule")
    required_approvals: int = Field(..., ge=1, le=4, description="Number of required approvals (2/3/4-eyes)")
    approval_roles: List[str] = Field(..., min_items=1, description="Roles that can approve (e.g., ['manager', 'finance'])")
    priority: int = Field(default=0, description="Rule priority (higher = checked first)")
    active: bool = Field(default=True, description="Active status")


class ApprovalRuleResponse(BaseModel):
    """Response schema for approval rule"""
    id: str
    name: str
    description: Optional[str]
    conditions: List[Dict[str, Any]]
    required_approvals: int
    approval_roles: List[str]
    priority: int
    active: bool
    created_at: datetime
    updated_at: datetime


class ApprovalRequest(BaseModel):
    """Schema for requesting approval"""
    invoice_id: str = Field(..., description="AP Invoice ID")
    requested_by: str = Field(..., description="User requesting approval")
    comment: Optional[str] = Field(None, description="Comment/notes")


class ApprovalAction(BaseModel):
    """Schema for approving/rejecting"""
    invoice_id: str = Field(..., description="AP Invoice ID")
    approved_by: str = Field(..., description="User approving/rejecting")
    action: str = Field(..., description="Action: approve or reject")
    comment: Optional[str] = Field(None, description="Comment/notes")


class ApprovalStatusResponse(BaseModel):
    """Response schema for approval status"""
    invoice_id: str
    status: str  # pending, approved, rejected, partially_approved
    required_approvals: int
    current_approvals: int
    approvals: List[Dict[str, Any]]
    rejections: List[Dict[str, Any]]
    applicable_rule: Optional[Dict[str, Any]]
    can_post: bool
    can_pay: bool


@router.get("/rules", response_model=List[ApprovalRuleResponse])
async def list_approval_rules(
    active_only: bool = Query(True, description="Show only active rules"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    List all approval workflow rules.
    """
    try:
        query = text("""
            SELECT id, name, description, conditions, required_approvals, approval_roles,
                   priority, active, created_at, updated_at
            FROM domain_erp.ap_approval_rules
            WHERE tenant_id = :tenant_id
        """)
        
        params = {"tenant_id": tenant_id}
        
        if active_only:
            query = text(str(query) + " AND active = true")
        
        query = text(str(query) + " ORDER BY priority DESC, name")
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            import json
            conditions_data = json.loads(row[3]) if row[3] else []
            roles_data = json.loads(row[5]) if row[5] else []
            
            result.append(ApprovalRuleResponse(
                id=str(row[0]),
                name=str(row[1]),
                description=str(row[2]) if row[2] else None,
                conditions=conditions_data,
                required_approvals=int(row[4]),
                approval_roles=roles_data,
                priority=int(row[6]),
                active=bool(row[7]),
                created_at=row[8],
                updated_at=row[9]
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing approval rules: {e}")
        # Return default rules if table doesn't exist
        return [
            ApprovalRuleResponse(
                id="1",
                name="Standard 2-Augen für Beträge > 1000 EUR",
                description="Rechnungen über 1000 EUR benötigen 2 Freigaben",
                conditions=[
                    {"field": "amount", "operator": "gt", "value": 1000.0}
                ],
                required_approvals=2,
                approval_roles=["manager", "finance"],
                priority=10,
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ApprovalRuleResponse(
                id="2",
                name="Standard 3-Augen für Beträge > 10000 EUR",
                description="Rechnungen über 10000 EUR benötigen 3 Freigaben",
                conditions=[
                    {"field": "amount", "operator": "gt", "value": 10000.0}
                ],
                required_approvals=3,
                approval_roles=["manager", "finance", "controller"],
                priority=20,
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ApprovalRuleResponse(
                id="3",
                name="Standard 4-Augen für Beträge > 50000 EUR",
                description="Rechnungen über 50000 EUR benötigen 4 Freigaben",
                conditions=[
                    {"field": "amount", "operator": "gt", "value": 50000.0}
                ],
                required_approvals=4,
                approval_roles=["manager", "finance", "controller", "ceo"],
                priority=30,
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]


@router.post("/rules", response_model=ApprovalRuleResponse, status_code=201)
async def create_approval_rule(
    rule: ApprovalRuleCreate,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Create a new approval workflow rule.
    """
    try:
        rule_id = str(uuid.uuid4())
        
        import json
        conditions_json = json.dumps([c.dict() for c in rule.conditions])
        roles_json = json.dumps(rule.approval_roles)
        
        insert_query = text("""
            INSERT INTO domain_erp.ap_approval_rules
            (id, tenant_id, name, description, conditions, required_approvals, approval_roles,
             priority, active, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :name, :description, :conditions, :required_approvals, :approval_roles,
             :priority, :active, NOW(), NOW())
            RETURNING id, name, description, conditions, required_approvals, approval_roles,
                      priority, active, created_at, updated_at
        """)
        
        row = db.execute(insert_query, {
            "id": rule_id,
            "tenant_id": tenant_id,
            "name": rule.name,
            "description": rule.description,
            "conditions": conditions_json,
            "required_approvals": rule.required_approvals,
            "approval_roles": roles_json,
            "priority": rule.priority,
            "active": rule.active
        }).fetchone()
        
        db.commit()
        
        import json
        conditions_data = json.loads(row[3]) if row[3] else []
        roles_data = json.loads(row[5]) if row[5] else []
        
        return ApprovalRuleResponse(
            id=str(row[0]),
            name=str(row[1]),
            description=str(row[2]) if row[2] else None,
            conditions=conditions_data,
            required_approvals=int(row[4]),
            approval_roles=roles_data,
            priority=int(row[6]),
            active=bool(row[7]),
            created_at=row[8],
            updated_at=row[9]
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating approval rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create approval rule: {str(e)}")


@router.post("/request", response_model=ApprovalStatusResponse)
async def request_approval(
    request: ApprovalRequest,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Request approval for an AP invoice.
    """
    try:
        # Get invoice
        from app.documents.router_helpers import get_repository, get_from_store
        repo = get_repository(db)
        invoice = get_from_store("ap_invoice", request.invoice_id, repo)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="AP Invoice not found")
        
        # Check if already approved
        if invoice.get("status") == "FREIGEGEBEN":
            raise HTTPException(status_code=400, detail="Invoice is already approved")
        
        # Find applicable approval rule
        rules = await list_approval_rules(active_only=True, tenant_id=tenant_id, db=db)
        
        applicable_rule = None
        invoice_amount = float(invoice.get("totalGross", 0))
        
        for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
            matches = True
            for condition in rule.conditions:
                field = condition.get("field")
                operator = condition.get("operator")
                value = condition.get("value")
                
                if field == "amount":
                    field_value = invoice_amount
                elif field == "material_group":
                    field_value = invoice.get("materialGroup", "")
                elif field == "supplier_id":
                    field_value = invoice.get("customerId", "")  # customerId = supplier_id for AP
                else:
                    field_value = invoice.get(field, "")
                
                if operator == "gt" and not (field_value > value):
                    matches = False
                    break
                elif operator == "gte" and not (field_value >= value):
                    matches = False
                    break
                elif operator == "lt" and not (field_value < value):
                    matches = False
                    break
                elif operator == "lte" and not (field_value <= value):
                    matches = False
                    break
                elif operator == "eq" and not (field_value == value):
                    matches = False
                    break
                elif operator == "in" and field_value not in value:
                    matches = False
                    break
            
            if matches:
                applicable_rule = rule
                break
        
        # If no rule matches, default to 1 approval (no workflow)
        required_approvals = applicable_rule.required_approvals if applicable_rule else 1
        
        # Create approval request
        approval_id = str(uuid.uuid4())
        
        import json
        rule_data = {
            "id": applicable_rule.id,
            "name": applicable_rule.name,
            "required_approvals": applicable_rule.required_approvals,
            "approval_roles": applicable_rule.approval_roles
        } if applicable_rule else None
        
        insert_query = text("""
            INSERT INTO domain_erp.ap_approval_requests
            (id, tenant_id, invoice_id, requested_by, required_approvals, applicable_rule,
             status, comment, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :invoice_id, :requested_by, :required_approvals, :applicable_rule,
             :status, :comment, NOW(), NOW())
            RETURNING id, invoice_id, status, required_approvals, applicable_rule, created_at, updated_at
        """)
        
        row = db.execute(insert_query, {
            "id": approval_id,
            "tenant_id": tenant_id,
            "invoice_id": request.invoice_id,
            "requested_by": request.requested_by,
            "required_approvals": required_approvals,
            "applicable_rule": json.dumps(rule_data) if rule_data else None,
            "status": "pending",
            "comment": request.comment
        }).fetchone()
        
        # Update invoice status
        from app.documents.router_helpers import save_to_store
        invoice["status"] = "ZUR_FREIGABE"
        invoice["approvalRequestId"] = approval_id
        save_to_store("ap_invoice", request.invoice_id, invoice, repo)
        
        db.commit()
        
        return ApprovalStatusResponse(
            invoice_id=request.invoice_id,
            status="pending",
            required_approvals=required_approvals,
            current_approvals=0,
            approvals=[],
            rejections=[],
            applicable_rule=rule_data,
            can_post=False,
            can_pay=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error requesting approval: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to request approval: {str(e)}")


@router.post("/approve", response_model=ApprovalStatusResponse)
async def approve_invoice(
    action: ApprovalAction,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Approve or reject an AP invoice.
    """
    try:
        # Get approval request
        query = text("""
            SELECT id, invoice_id, required_approvals, applicable_rule, status
            FROM domain_erp.ap_approval_requests
            WHERE invoice_id = :invoice_id AND tenant_id = :tenant_id
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        row = db.execute(query, {
            "invoice_id": action.invoice_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Approval request not found")
        
        approval_request_id = str(row[0])
        required_approvals = int(row[2])
        import json
        applicable_rule = json.loads(row[3]) if row[3] else None
        current_status = str(row[4])
        
        if current_status in ["approved", "rejected"]:
            raise HTTPException(status_code=400, detail=f"Approval request is already {current_status}")
        
        # Get existing approvals/rejections
        approvals_query = text("""
            SELECT approved_by, approved_at, comment
            FROM domain_erp.ap_approvals
            WHERE approval_request_id = :approval_request_id AND action = 'approve'
            ORDER BY approved_at
        """)
        
        approvals_rows = db.execute(approvals_query, {
            "approval_request_id": approval_request_id
        }).fetchall()
        
        rejections_query = text("""
            SELECT approved_by, approved_at, comment
            FROM domain_erp.ap_approvals
            WHERE approval_request_id = :approval_request_id AND action = 'reject'
            ORDER BY approved_at
        """)
        
        rejections_rows = db.execute(rejections_query, {
            "approval_request_id": approval_request_id
        }).fetchall()
        
        # Check if user already approved/rejected
        existing_approval = db.execute(text("""
            SELECT id FROM domain_erp.ap_approvals
            WHERE approval_request_id = :approval_request_id AND approved_by = :approved_by
        """), {
            "approval_request_id": approval_request_id,
            "approved_by": action.approved_by
        }).fetchone()
        
        if existing_approval:
            raise HTTPException(status_code=400, detail="You have already approved/rejected this invoice")
        
        # Insert approval/rejection
        approval_id = str(uuid.uuid4())
        insert_approval = text("""
            INSERT INTO domain_erp.ap_approvals
            (id, approval_request_id, approved_by, action, comment, approved_at)
            VALUES (:id, :approval_request_id, :approved_by, :action, :comment, NOW())
        """)
        
        db.execute(insert_approval, {
            "id": approval_id,
            "approval_request_id": approval_request_id,
            "approved_by": action.approved_by,
            "action": action.action,
            "comment": action.comment
        })
        
        # Update approval request status
        if action.action == "reject":
            update_status = "rejected"
        else:
            # Count approvals
            new_approvals_count = len(approvals_rows) + 1
            if new_approvals_count >= required_approvals:
                update_status = "approved"
            else:
                update_status = "partially_approved"
        
        update_query = text("""
            UPDATE domain_erp.ap_approval_requests
            SET status = :status, updated_at = NOW()
            WHERE id = :approval_request_id
        """)
        
        db.execute(update_query, {
            "status": update_status,
            "approval_request_id": approval_request_id
        })
        
        # Update invoice status if fully approved
        if update_status == "approved":
            from app.documents.router_helpers import get_repository, get_from_store, save_to_store
            repo = get_repository(db)
            invoice = get_from_store("ap_invoice", action.invoice_id, repo)
            if invoice:
                invoice["status"] = "FREIGEGEBEN"
                invoice["approvedBy"] = action.approved_by
                invoice["approvedAt"] = datetime.now().isoformat()
                save_to_store("ap_invoice", action.invoice_id, invoice, repo)
        
        db.commit()
        
        # Get updated approvals/rejections
        approvals_rows = db.execute(approvals_query, {
            "approval_request_id": approval_request_id
        }).fetchall()
        
        rejections_rows = db.execute(rejections_query, {
            "approval_request_id": approval_request_id
        }).fetchall()
        
        approvals = [
            {
                "approved_by": str(row[0]),
                "approved_at": row[1].isoformat() if row[1] else None,
                "comment": str(row[2]) if row[2] else None
            }
            for row in approvals_rows
        ]
        
        rejections = [
            {
                "approved_by": str(row[0]),
                "approved_at": row[1].isoformat() if row[1] else None,
                "comment": str(row[2]) if row[2] else None
            }
            for row in rejections_rows
        ]
        
        return ApprovalStatusResponse(
            invoice_id=action.invoice_id,
            status=update_status,
            required_approvals=required_approvals,
            current_approvals=len(approvals),
            approvals=approvals,
            rejections=rejections,
            applicable_rule=applicable_rule,
            can_post=(update_status == "approved"),
            can_pay=(update_status == "approved")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving invoice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve invoice: {str(e)}")


@router.get("/status/{invoice_id}", response_model=ApprovalStatusResponse)
async def get_approval_status(
    invoice_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get approval status for an AP invoice.
    """
    try:
        # Get approval request
        query = text("""
            SELECT id, invoice_id, required_approvals, applicable_rule, status
            FROM domain_erp.ap_approval_requests
            WHERE invoice_id = :invoice_id AND tenant_id = :tenant_id
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        row = db.execute(query, {
            "invoice_id": invoice_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not row:
            # No approval request - check invoice status
            from app.documents.router_helpers import get_repository, get_from_store
            repo = get_repository(db)
            invoice = get_from_store("ap_invoice", invoice_id, repo)
            
            if not invoice:
                raise HTTPException(status_code=404, detail="AP Invoice not found")
            
            invoice_status = invoice.get("status", "ENTWURF")
            return ApprovalStatusResponse(
                invoice_id=invoice_id,
                status="not_requested" if invoice_status == "ENTWURF" else "approved",
                required_approvals=0,
                current_approvals=0,
                approvals=[],
                rejections=[],
                applicable_rule=None,
                can_post=(invoice_status == "FREIGEGEBEN"),
                can_pay=(invoice_status == "FREIGEGEBEN")
            )
        
        approval_request_id = str(row[0])
        required_approvals = int(row[2])
        import json
        applicable_rule = json.loads(row[3]) if row[3] else None
        current_status = str(row[4])
        
        # Get approvals/rejections
        approvals_query = text("""
            SELECT approved_by, approved_at, comment
            FROM domain_erp.ap_approvals
            WHERE approval_request_id = :approval_request_id AND action = 'approve'
            ORDER BY approved_at
        """)
        
        approvals_rows = db.execute(approvals_query, {
            "approval_request_id": approval_request_id
        }).fetchall()
        
        rejections_query = text("""
            SELECT approved_by, approved_at, comment
            FROM domain_erp.ap_approvals
            WHERE approval_request_id = :approval_request_id AND action = 'reject'
            ORDER BY approved_at
        """)
        
        rejections_rows = db.execute(rejections_query, {
            "approval_request_id": approval_request_id
        }).fetchall()
        
        approvals = [
            {
                "approved_by": str(row[0]),
                "approved_at": row[1].isoformat() if row[1] else None,
                "comment": str(row[2]) if row[2] else None
            }
            for row in approvals_rows
        ]
        
        rejections = [
            {
                "approved_by": str(row[0]),
                "approved_at": row[1].isoformat() if row[1] else None,
                "comment": str(row[2]) if row[2] else None
            }
            for row in rejections_rows
        ]
        
        return ApprovalStatusResponse(
            invoice_id=invoice_id,
            status=current_status,
            required_approvals=required_approvals,
            current_approvals=len(approvals),
            approvals=approvals,
            rejections=rejections,
            applicable_rule=applicable_rule,
            can_post=(current_status == "approved"),
            can_pay=(current_status == "approved")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting approval status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get approval status: {str(e)}")

