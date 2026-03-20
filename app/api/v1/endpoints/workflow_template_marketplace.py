from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.workflow_template_marketplace import (
    WorkflowTemplateScope,
    build_workflow_template_marketplace_catalog,
    clone_workflow_template,
    get_workflow_template_listing,
    install_workflow_template,
    preview_workflow_template_installation,
)

router = APIRouter(prefix="/workflow/templates/marketplace", tags=["workflow", "templates", "marketplace"])


@router.get("", summary="Interner Workflow-Template-Marketplace")
def list_workflow_templates(
    category: str | None = Query(default=None, description="Optional category filter"),
    search: str | None = Query(default=None, description="Optional free-text filter"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    return build_workflow_template_marketplace_catalog(category=category, search=search, tenant_id=tenant_id, db=db).as_dict()


@router.get("/installed", summary="Bereits installierte Workflow-Templates")
def list_installed_workflow_templates(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    catalog = build_workflow_template_marketplace_catalog(tenant_id=tenant_id, db=db)
    catalog.templates = [template for template in catalog.templates if template.installed]
    catalog.template_count = len(catalog.templates)
    catalog.installable_count = sum(1 for template in catalog.templates if template.installable)
    catalog.installed_count = len(catalog.templates)
    catalog.categories = sorted({template.category.value for template in catalog.templates})
    catalog.scope_summary = {
        scope: sum(1 for template in catalog.templates if template.governance.scope.value == scope)
        for scope in {template.governance.scope.value for template in catalog.templates}
    }
    return catalog.as_dict()


@router.get("/{template_id}", summary="Einzelnes Workflow-Template")
def get_workflow_template(
    template_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    template = get_workflow_template_listing(template_id, tenant_id=tenant_id, db=db)
    if template is None:
        raise HTTPException(status_code=404, detail=f"WorkflowTemplate {template_id!r} nicht gefunden")
    return template.as_dict()


@router.post("/{template_id}/preview", summary="Workflow-Template vor Installation previewen")
def preview_workflow_template(
    template_id: str,
    payload: dict,
    db: Session = Depends(get_db),
) -> dict:
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Feld 'tenant_id' ist erforderlich")
    try:
        return preview_workflow_template_installation(
            template_id=template_id,
            tenant_id=tenant_id,
            workflow_definition_version=payload.get("workflow_definition_version"),
            context=dict(payload.get("context", {})),
            target_scope=payload.get("target_scope"),
            requested_by_role=payload.get("requested_by_role"),
            db=db,
        ).as_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{template_id}/publish-preview", summary="Workflow-Template fuer Publikation previewen")
def publish_preview_workflow_template(
    template_id: str,
    payload: dict,
    db: Session = Depends(get_db),
) -> dict:
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Feld 'tenant_id' ist erforderlich")
    try:
        return preview_workflow_template_installation(
            template_id=template_id,
            tenant_id=tenant_id,
            workflow_definition_version=payload.get("workflow_definition_version"),
            context=dict(payload.get("context", {})),
            target_scope=payload.get("target_scope", WorkflowTemplateScope.GLOBAL.value),
            requested_by_role=payload.get("requested_by_role"),
            db=db,
        ).as_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{template_id}/clone", summary="Workflow-Template klonen")
def clone_workflow_template_endpoint(
    template_id: str,
    payload: dict,
    db: Session = Depends(get_db),
) -> dict:
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Feld 'tenant_id' ist erforderlich")
    try:
        return clone_workflow_template(
            template_id=template_id,
            tenant_id=tenant_id,
            installed_by=payload.get("installed_by"),
            clone_name=payload.get("clone_name"),
            target_scope=payload.get("target_scope", WorkflowTemplateScope.TENANT.value),
            db=db,
        ).as_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{template_id}/install", summary="Workflow-Template intern installieren")
def install_workflow_template_endpoint(
    template_id: str,
    payload: dict,
    db: Session = Depends(get_db),
) -> dict:
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Feld 'tenant_id' ist erforderlich")
    try:
        return install_workflow_template(
            template_id=template_id,
            tenant_id=tenant_id,
            installed_by=payload.get("installed_by"),
            clone_name=payload.get("clone_name"),
            target_scope=payload.get("target_scope", WorkflowTemplateScope.TENANT.value),
            activate=bool(payload.get("activate", True)),
            db=db,
        ).as_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

