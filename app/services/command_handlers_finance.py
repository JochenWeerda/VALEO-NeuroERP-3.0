"""AP kernel transport delegates to the same tenant-bound domain commands."""
from app.api.v1.schemas.ap_approval_workflow_schemas import ApprovalAction
from app.services.ap_invoice_approval_service import APApprovalWorkflowService
from app.services.ap_invoice_kernel_posting import verified_ap_user, post_ap_invoice_kernel_sync
from fastapi import HTTPException
from pydantic import ValidationError


def _decision(db, request, action):
    user = verified_ap_user(request.tenant_id)
    try:
        payload = ApprovalAction(invoice_id=request.aggregate_id, action=action,
            approval_request_id=request.payload.get("approval_request_id"),
            comment=request.payload.get("comment"))
    except ValidationError:
        raise HTTPException(422, "Gueltige Freigabeantragsreferenz erforderlich") from None
    return APApprovalWorkflowService(db, request.tenant_id).decide(payload, user, commit=False)


def _approve_ap_invoice_mutation(db, request, result):
    return _decision(db, request, "approve")


def _reject_ap_invoice_mutation(db, request, result):
    return _decision(db, request, "reject")


def _post_ap_invoice_mutation(db, request, result):
    return post_ap_invoice_kernel_sync(db, invoice_id=request.aggregate_id, tenant_id=request.tenant_id)


def register_finance_command_mutations():
    from app.services.action_execution_mutations import register_domain_mutation
    register_domain_mutation("ApproveAPInvoice", _approve_ap_invoice_mutation)
    register_domain_mutation("RejectAPInvoice", _reject_ap_invoice_mutation)
    register_domain_mutation("PostAPInvoice", _post_ap_invoice_mutation)
