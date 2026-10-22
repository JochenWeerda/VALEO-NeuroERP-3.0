"""
AP Approval Workflow API
FIBU-AP-03: Prüf-/Freigabeworkflow
"""

import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from pydantic import BaseModel, Field
import logging
from app.core.uuid7 import uuid7

from ....core.database import get_db
from app.auth.finance_roles import finance_admin, finance_read, finance_write
from app.core.tenant import get_tenant_id
from app.core.ap_approval_status import (
    APPROVAL_STATUS_TO_DOCUMENT_STATUS,
    DOCUMENT_STATUS_TO_APPROVAL_STATUS,
    build_approval_status_response,
)
from app.infrastructure.models import AuditLog

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema, StatusResponse


router = APIRouter(prefix="/ap/approval-workflow", tags=["finance", "ap", "approval"])


from app.api.v1.schemas.ap_approval_workflow_schemas import (
    ApprovalRuleCondition, ApprovalRuleCreate, ApprovalRuleResponse, ApprovalRequest, ApprovalAction,
)
from app.core.ap_approval_status import ApprovalStatusResponse
from app.core.akteur import gepruefter_akteur, verlange_rolle
from app.auth.finance_roles import FINANCE_WRITE_ROLES
from app.services.ap_invoice_approval_service import APApprovalWorkflowService
from sqlalchemy.exc import SQLAlchemyError


class WorkflowBusinessReference(BaseModel):
    reference_type: str
    reference_id: str


class WorkflowInstanceReference(BaseModel):
    process_key: str
    workflow_instance_id: str
    definition_origin: str
    status: str
    current_step: str
    business_reference: WorkflowBusinessReference


APPROVAL_STATUS_TO_INSTANCE_STATUS = {
    "not_requested": "running",
    "pending": "waiting",
    "partially_approved": "waiting",
    "approved": "completed",
    "rejected": "failed",
}


def _build_workflow_instance_reference(
    *,
    invoice_id: str,
    tenant_id: str,
    approval_status: str,
    action: str,
    applicable_rule: dict[str, Any] | None,
) -> WorkflowInstanceReference:
    return WorkflowInstanceReference(
        process_key="ap_approval",
        workflow_instance_id=f"wf-ap-{invoice_id}",
        definition_origin="tenant-override" if applicable_rule else "default",
        status=APPROVAL_STATUS_TO_INSTANCE_STATUS.get(approval_status, "running"),
        current_step=action,
        business_reference=WorkflowBusinessReference(
            reference_type="ap_invoice",
            reference_id=invoice_id,
        ),
    )


def _write_approval_audit_log(
    db,
    *,
    tenant_id: str,
    user_id: str,
    user_email: str,
    action: str,
    invoice_id: str,
    response,
    comment: str | None = None,
) -> None:
    entry = AuditLog(
        id=str(uuid7()),
        timestamp=datetime.utcnow(),
        user_id=user_id,
        user_email=user_email,
        tenant_id=tenant_id,
        action=action,
        entity_type="ap_invoice_approval",
        entity_id=invoice_id,
        changes={
            "override_resolution": response.override_resolution.model_dump(exclude_none=True),
            "explainability": response.explainability.model_dump(exclude_none=True),
            "workflow_instance_ref": _build_workflow_instance_reference(
                invoice_id=invoice_id,
                tenant_id=tenant_id,
                approval_status=response.status,
                action=action,
                applicable_rule=response.applicable_rule,
            ).model_dump(exclude_none=True),
            "comment": comment,
        },
    )
    db.add(entry)


def _json_wert(wert: Any) -> Any:
    """JSONB kommt vom Treiber schon als Liste/Dict, TEXT als String.

    Bis 07.10.2026 rief jeder Lesepfad ``json.loads`` auf — auf einer frischen
    Datenbank (JSONB) scheiterte damit schon das Anlegen einer Freigaberegel mit 500.
    """
    return json.loads(wert) if isinstance(wert, (str, bytes, bytearray)) else wert


def _ensure_invoice_tenant_access(invoice: dict[str, Any] | None, tenant_id: str) -> dict[str, Any]:
    """Die Rechnung gehoert diesem Mandanten — sonst gibt es sie nicht.

    Bis 07.10.2026 liess dieser Helfer Rechnungen **ohne** Mandant durch; weil keine
    gespeicherte AP-Rechnung je einen trug, liess er alles durch. Fremd und
    mandantenlos sind jetzt gleich: 404, ohne die Existenz zu verraten.
    """
    invoice_tenant = str((invoice or {}).get("tenantId") or (invoice or {}).get("tenant_id") or "").strip()
    if not invoice or invoice_tenant != tenant_id:
        raise HTTPException(status_code=404, detail="AP Invoice not found")
    return invoice


@router.get("/rules", response_model=List[ApprovalRuleResponse], summary="Approval rules auflisten",
            dependencies=[Depends(finance_read)])
async def list_approval_rules(
    active_only: bool = Query(True, description="Show only active rules"),
    tenant_id: str = Depends(get_tenant_id),
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
            query = text(str(query) + " AND active = true")  # nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden
        
        query = text(str(query) + " ORDER BY priority DESC, name")  # nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden
        
        rows = db.execute(query, params).fetchall()
        
        result = []
        for row in rows:
            conditions_data = _json_wert(row[3]) if row[3] else []
            roles_data = _json_wert(row[5]) if row[5] else []
            
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
        
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(503, "Freigaberegeln derzeit nicht verfuegbar") from None


@router.post("/rules", response_model=ApprovalRuleResponse, status_code=201, summary="Approval rule anlegen",
             dependencies=[Depends(finance_admin)])
async def create_approval_rule(
    rule: ApprovalRuleCreate,
    user: dict = Depends(finance_admin),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Create a new approval workflow rule.
    """
    actor = gepruefter_akteur(user)
    from app.auth.finance_roles import FINANCE_APPROVAL_ROLES
    verlange_rolle(user, *FINANCE_APPROVAL_ROLES)
    try:
        rule_id = uuid7()
        
        conditions_json = json.dumps([c.model_dump() for c in rule.conditions])
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
        
        
        conditions_data = _json_wert(row[3]) if row[3] else []
        roles_data = _json_wert(row[5]) if row[5] else []
        
        response = ApprovalRuleResponse(
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
        
        db.add(AuditLog(id=str(uuid7()), timestamp=datetime.utcnow(), user_id=actor, user_email="",
            tenant_id=tenant_id, action="ap_approval_rule_create", entity_type="ap_approval_rule",
            entity_id=str(rule_id), changes={"rule": rule.model_dump()}))
        db.commit()
        return response
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(503, "Freigaberegel konnte nicht gespeichert werden") from None


@router.post("/request", response_model=ApprovalStatusResponse, summary="Approval request",
             dependencies=[Depends(finance_write)])
async def request_approval(
    request: ApprovalRequest,
    user: dict = Depends(finance_write),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Request a content-bound AP review using the verified requester."""
    gepruefter_akteur(user)
    verlange_rolle(user, *FINANCE_WRITE_ROLES)
    rules = await list_approval_rules(active_only=True, tenant_id=tenant_id, db=db)
    return APApprovalWorkflowService(db, tenant_id).request(request, user, rules)


@router.post("/approve", response_model=ApprovalStatusResponse, summary="Invoice genehmigen",
             dependencies=[Depends(finance_admin)])
async def approve_invoice(
    action: ApprovalAction,
    user: dict = Depends(finance_admin),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Decide on exactly the displayed request; verified independent human only."""
    return APApprovalWorkflowService(db, tenant_id).decide(action, user)


@router.get("/status/{invoice_id}", response_model=ApprovalStatusResponse, summary="Approval status abrufen",
            dependencies=[Depends(finance_read)])
async def get_approval_status(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user: dict = Depends(finance_read),
):
    """No request, changed content or expired review never grants posting rights."""
    return APApprovalWorkflowService(db, tenant_id).status(invoice_id, user)
