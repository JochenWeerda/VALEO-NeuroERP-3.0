"""Kernel adapter: same AP posting command, transaction owned by caller."""
from app.core.identity_context import current_identity
from app.services.ap_invoice_approval_service import APApprovalWorkflowService
from fastapi import HTTPException


def verified_ap_user(tenant_id):
    principal = current_identity()
    if principal.tenant_id != tenant_id:
        raise HTTPException(403, "Ausfuehrungsmandant stimmt nicht ueberein")
    return {"sub": principal.subject, "roles": list(principal.roles), "raw": dict(principal.claims)}


def post_ap_invoice_kernel_sync(db, *, invoice_id, tenant_id, posted_by=None):
    # posted_by is a deprecated compatibility argument and never an identity source.
    return APApprovalWorkflowService(db, tenant_id).post_invoice(
        invoice_id, verified_ap_user(tenant_id), commit=False)
