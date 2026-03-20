from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


class WorkflowTemplateCategory(str, Enum):
    FINANCE = "finance"
    AGRAR = "agrar"
    CRM = "crm"
    LOGISTICS = "logistics"
    COMPLIANCE = "compliance"


class WorkflowTemplateLifecycle(str, Enum):
    CURATED = "curated"
    INTERNAL = "internal"


class WorkflowTemplateVisibility(str, Enum):
    INTERNAL = "internal"
    TENANT = "tenant"


class WorkflowTemplateScope(str, Enum):
    GLOBAL = "global"
    TENANT = "tenant"
    ROLE = "role"
    EXPERIMENTAL = "experimental"


class WorkflowTemplateRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    REGULATED = "REGULATED"


TENANT_INSTALLS_KEY = "workflow_template_marketplace_installs"
TENANT_LIBRARY_KEY = "workflow_template_library"
TENANT_CLONES_KEY = "workflow_template_marketplace_clones"


@dataclass(frozen=True)
class WorkflowTemplateParameter:
    key: str
    label: str
    required: bool
    default_value: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "required": self.required,
            "default_value": self.default_value,
        }


@dataclass(frozen=True)
class WorkflowTemplateGovernance:
    scope: WorkflowTemplateScope
    owner_role: str
    approval_required: bool = False
    review_roles: list[str] = field(default_factory=list)
    install_roles: list[str] = field(default_factory=list)
    publish_roles: list[str] = field(default_factory=list)
    clone_roles: list[str] = field(default_factory=list)
    risk_level: WorkflowTemplateRiskLevel = WorkflowTemplateRiskLevel.MEDIUM
    compliance_notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "scope": self.scope.value,
            "owner_role": self.owner_role,
            "approval_required": self.approval_required,
            "review_roles": list(self.review_roles),
            "install_roles": list(self.install_roles),
            "publish_roles": list(self.publish_roles),
            "clone_roles": list(self.clone_roles),
            "risk_level": self.risk_level.value,
            "compliance_notes": list(self.compliance_notes),
        }


@dataclass(frozen=True)
class WorkflowTemplateListing:
    template_id: str
    name: str
    process_key: str
    category: WorkflowTemplateCategory
    lifecycle: WorkflowTemplateLifecycle
    description: str
    latest_version: str
    setup_hours: float
    visibility: WorkflowTemplateVisibility = WorkflowTemplateVisibility.INTERNAL
    tags: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    parameters: list[WorkflowTemplateParameter] = field(default_factory=list)
    governance: WorkflowTemplateGovernance = field(
        default_factory=lambda: WorkflowTemplateGovernance(
            scope=WorkflowTemplateScope.GLOBAL,
            owner_role="prozessmanagement",
        )
    )
    installable: bool = True
    cloneable: bool = True
    publishable: bool = True
    catalog_revision: str = ""
    installed: bool = False
    installed_record_id: str = ""
    installed_at: str = ""
    installed_scope: str = ""

    def matches(self, *, category: str | None, search: str | None) -> bool:
        if category and self.category.value != category:
            return False
        if not search:
            return True
        haystack = " ".join(
            [
                self.template_id,
                self.name,
                self.process_key,
                self.description,
                " ".join(self.tags),
                " ".join(self.required_capabilities),
            ]
        ).lower()
        return search.lower() in haystack

    def as_dict(self) -> dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "process_key": self.process_key,
            "category": self.category.value,
            "lifecycle": self.lifecycle.value,
            "visibility": self.visibility.value,
            "description": self.description,
            "latest_version": self.latest_version,
            "setup_hours": self.setup_hours,
            "tags": self.tags,
            "required_capabilities": self.required_capabilities,
            "parameters": [parameter.as_dict() for parameter in self.parameters],
            "governance": self.governance.as_dict(),
            "installable": self.installable,
            "cloneable": self.cloneable,
            "publishable": self.publishable,
            "catalog_revision": self.catalog_revision,
            "installed": self.installed,
            "installed_record_id": self.installed_record_id,
            "installed_at": self.installed_at,
            "installed_scope": self.installed_scope,
        }


@dataclass(frozen=True)
class WorkflowTemplateCatalog:
    generated_at: str
    template_count: int
    categories: list[str]
    templates: list[WorkflowTemplateListing]
    curated_count: int = 0
    tenant_template_count: int = 0
    installable_count: int = 0
    installed_count: int = 0
    scope_summary: dict[str, int] = field(default_factory=dict)
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "template_count": self.template_count,
            "categories": self.categories,
            "templates": [template.as_dict() for template in self.templates],
            "curated_count": self.curated_count,
            "tenant_template_count": self.tenant_template_count,
            "installable_count": self.installable_count,
            "installed_count": self.installed_count,
            "scope_summary": self.scope_summary,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True)
class WorkflowTemplatePreview:
    template_id: str
    tenant_id: str
    process_key: str
    estimated_setup_hours: float
    generated_variant_key: str
    warnings: list[str]
    rollout_steps: list[str]
    preview_context: dict[str, Any]
    target_scope: str = WorkflowTemplateScope.GLOBAL.value
    publishable: bool = True
    blocking_reasons: list[str] = field(default_factory=list)
    governance: WorkflowTemplateGovernance = field(
        default_factory=lambda: WorkflowTemplateGovernance(
            scope=WorkflowTemplateScope.GLOBAL,
            owner_role="prozessmanagement",
        )
    )
    recommended_next_action: str = ""
    catalog_revision: str = ""
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "template_id": self.template_id,
            "tenant_id": self.tenant_id,
            "process_key": self.process_key,
            "estimated_setup_hours": self.estimated_setup_hours,
            "generated_variant_key": self.generated_variant_key,
            "warnings": self.warnings,
            "rollout_steps": self.rollout_steps,
            "preview_context": self.preview_context,
            "target_scope": self.target_scope,
            "publishable": self.publishable,
            "blocking_reasons": self.blocking_reasons,
            "governance": self.governance.as_dict(),
            "recommended_next_action": self.recommended_next_action,
            "catalog_revision": self.catalog_revision,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True)
class WorkflowTemplateCloneResult:
    template_id: str
    tenant_id: str
    clone_id: str
    clone_name: str
    target_scope: str
    persisted: bool
    cloned_template: dict[str, Any]
    governance: WorkflowTemplateGovernance
    warnings: list[str]
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "template_id": self.template_id,
            "tenant_id": self.tenant_id,
            "clone_id": self.clone_id,
            "clone_name": self.clone_name,
            "target_scope": self.target_scope,
            "persisted": self.persisted,
            "cloned_template": self.cloned_template,
            "governance": self.governance.as_dict(),
            "warnings": self.warnings,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True)
class WorkflowTemplateInstallResult:
    template_id: str
    tenant_id: str
    installed_version: str
    process_variant_key: str
    lifecycle_status: str
    required_followups: list[str]
    monitoring_hooks: list[str]
    governance: WorkflowTemplateGovernance = field(
        default_factory=lambda: WorkflowTemplateGovernance(
            scope=WorkflowTemplateScope.GLOBAL,
            owner_role="prozessmanagement",
        )
    )
    registry_key: str = ""
    target_scope: str = WorkflowTemplateScope.TENANT.value
    activated: bool = True
    persisted: bool = False
    installed_template: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "template_id": self.template_id,
            "tenant_id": self.tenant_id,
            "installed_version": self.installed_version,
            "process_variant_key": self.process_variant_key,
            "lifecycle_status": self.lifecycle_status,
            "required_followups": self.required_followups,
            "monitoring_hooks": self.monitoring_hooks,
            "governance": self.governance.as_dict(),
            "registry_key": self.registry_key,
            "target_scope": self.target_scope,
            "activated": self.activated,
            "persisted": self.persisted,
            "installed_template": self.installed_template,
            "warnings": self.warnings,
            "schema_version": self.schema_version,
        }


def _default_templates() -> list[WorkflowTemplateListing]:
    return [
        WorkflowTemplateListing(
            template_id="tpl-harvest-campaign",
            name="Erntekampagne Standard",
            process_key="harvest_campaign",
            category=WorkflowTemplateCategory.AGRAR,
            lifecycle=WorkflowTemplateLifecycle.CURATED,
            description="Kuratiertes Template fuer saisonale Erntekampagnen mit SLA- und Freigabepfaden.",
            latest_version="1.2.0",
            setup_hours=6.0,
            tags=["campaign", "harvest", "season"],
            required_capabilities=["approval-gate", "sla-escalation"],
            parameters=[
                WorkflowTemplateParameter("campaign_type", "Kampagnentyp", True, "GETREIDE"),
                WorkflowTemplateParameter("approval_group", "Freigabegruppe", True, "ERNTE"),
            ],
        ),
        WorkflowTemplateListing(
            template_id="tpl-complaint-e2e",
            name="Reklamation E2E",
            process_key="complaint_e2e",
            category=WorkflowTemplateCategory.CRM,
            lifecycle=WorkflowTemplateLifecycle.CURATED,
            description="CRM- und DMS-gekoppelter Reklamationsprozess mit SLA-Monitoring und Audit.",
            latest_version="1.1.0",
            setup_hours=4.0,
            tags=["complaint", "crm", "dms"],
            required_capabilities=["dms-docflow", "sla-escalation"],
            parameters=[
                WorkflowTemplateParameter("sla_profile", "SLA-Profil", True, "STANDARD"),
                WorkflowTemplateParameter("dms_folder", "DMS-Ablage", True, "reklamationen"),
            ],
        ),
        WorkflowTemplateListing(
            template_id="tpl-ap-approval",
            name="AP-Rechnungsfreigabe 4-Augen",
            process_key="ap_invoice_approval",
            category=WorkflowTemplateCategory.FINANCE,
            lifecycle=WorkflowTemplateLifecycle.CURATED,
            description="Freigabe-Template fuer Eingangsrechnungen mit Sandbox-Preview und Eskalation.",
            latest_version="2.1.0",
            setup_hours=3.5,
            tags=["finance", "approval", "four-eyes"],
            required_capabilities=["approval-gate", "idempotent-commands", "policy-override"],
            parameters=[
                WorkflowTemplateParameter("approval_limit", "Freigabelimit", True, "25000"),
                WorkflowTemplateParameter("escalation_hours", "Eskalation", True, "72"),
            ],
        ),
        WorkflowTemplateListing(
            template_id="tpl-eta-alert",
            name="Lieferkette ETA-Abweichung",
            process_key="supply_chain_eta_alert",
            category=WorkflowTemplateCategory.LOGISTICS,
            lifecycle=WorkflowTemplateLifecycle.CURATED,
            description="Logistik-Template fuer ETA-Tracking, Abweichungsalarme und Eskalation.",
            latest_version="1.0.0",
            setup_hours=5.0,
            tags=["eta", "tracking", "alert"],
            required_capabilities=["background-jobs", "eta-monitoring"],
            parameters=[
                WorkflowTemplateParameter("transport_mode", "Transportmodus", True, "LKW"),
                WorkflowTemplateParameter("critical_delay_hours", "Kritische Verzögerung", True, "6"),
            ],
        ),
    ]


def _template_catalog_payload(template: WorkflowTemplateListing) -> dict[str, Any]:
    return {
        "template_id": template.template_id,
        "name": template.name,
        "process_key": template.process_key,
        "category": template.category.value,
        "lifecycle": template.lifecycle.value,
        "description": template.description,
        "latest_version": template.latest_version,
        "setup_hours": template.setup_hours,
        "tags": template.tags,
        "required_capabilities": template.required_capabilities,
        "parameters": [parameter.as_dict() for parameter in template.parameters],
    }


def _decorate_template(template: WorkflowTemplateListing) -> WorkflowTemplateListing:
    visibility = WorkflowTemplateVisibility.TENANT if template.category in {WorkflowTemplateCategory.CRM, WorkflowTemplateCategory.LOGISTICS} else WorkflowTemplateVisibility.INTERNAL
    approval_required = template.category in {WorkflowTemplateCategory.FINANCE, WorkflowTemplateCategory.COMPLIANCE}
    if template.lifecycle != WorkflowTemplateLifecycle.CURATED:
        approval_required = True
    scope = WorkflowTemplateScope.TENANT if visibility == WorkflowTemplateVisibility.TENANT else WorkflowTemplateScope.GLOBAL
    risk_level = WorkflowTemplateRiskLevel.LOW if template.lifecycle == WorkflowTemplateLifecycle.CURATED else WorkflowTemplateRiskLevel.REGULATED
    governance = WorkflowTemplateGovernance(
        scope=scope,
        owner_role="tenant_admin" if visibility == WorkflowTemplateVisibility.TENANT else "prozessmanagement",
        approval_required=approval_required,
        review_roles=["tenant_admin", "fachbereich"] if visibility == WorkflowTemplateVisibility.TENANT else ["prozessmanagement", "tenant_admin"],
        install_roles=["tenant_admin", "prozessmanagement"],
        publish_roles=["tenant_admin", "fachbereich"] if visibility == WorkflowTemplateVisibility.TENANT else ["prozessmanagement", "tenant_admin"],
        clone_roles=["tenant_admin", "fachbereich"] if visibility == WorkflowTemplateVisibility.TENANT else ["prozessmanagement", "tenant_admin"],
        risk_level=risk_level,
        compliance_notes=[
            "Marketplace-Installationen werden in Tenant-Settings protokolliert.",
            "Scope und Rollen werden vor Publish/Install validiert.",
        ]
        + (["Template erfordert Governance-Pruefung vor Publikation."] if approval_required else []),
    )
    return WorkflowTemplateListing(
        template_id=template.template_id,
        name=template.name,
        process_key=template.process_key,
        category=template.category,
        lifecycle=template.lifecycle,
        visibility=visibility,
        description=template.description,
        latest_version=template.latest_version,
        setup_hours=template.setup_hours,
        tags=list(template.tags),
        required_capabilities=list(template.required_capabilities),
        parameters=list(template.parameters),
        governance=governance,
        installable=template.lifecycle != WorkflowTemplateLifecycle.INTERNAL,
        cloneable=template.lifecycle != WorkflowTemplateLifecycle.INTERNAL,
        publishable=template.lifecycle == WorkflowTemplateLifecycle.CURATED,
        catalog_revision=hashlib.sha256(json.dumps(_template_catalog_payload(template), sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12],
    )


def build_workflow_template_marketplace_catalog(
    *,
    category: str | None = None,
    search: str | None = None,
    tenant_id: str | None = None,
    db: Session | None = None,
) -> WorkflowTemplateCatalog:
    templates = [
        _decorate_template(template)
        for template in _default_templates()
        if template.matches(category=category, search=search)
    ]
    if tenant_id and db is not None:
        settings = _tenant_settings_from_db(db, tenant_id)
        installs = settings.get(TENANT_INSTALLS_KEY, [])
        library = settings.get(TENANT_LIBRARY_KEY, {})
        installed_by_id: dict[str, dict[str, Any]] = {}
        for record in installs if isinstance(installs, list) else []:
            if isinstance(record, dict) and record.get("template_id"):
                installed_by_id[str(record["template_id"])] = record
        for template in templates:
            record = installed_by_id.get(template.template_id)
            if not record and isinstance(library, dict):
                record = library.get(template.template_id)
            if isinstance(record, dict):
                object.__setattr__(template, "installed", True)
                object.__setattr__(template, "installed_record_id", str(record.get("install_id") or record.get("clone_id") or ""))
                object.__setattr__(template, "installed_at", str(record.get("installed_at") or record.get("cloned_at") or ""))
                object.__setattr__(template, "installed_scope", str(record.get("target_scope") or record.get("scope") or ""))

    return WorkflowTemplateCatalog(
        generated_at=datetime.now(timezone.utc).isoformat(),
        template_count=len(templates),
        categories=sorted({template.category.value for template in templates}),
        curated_count=sum(1 for template in templates if template.lifecycle == WorkflowTemplateLifecycle.CURATED),
        tenant_template_count=sum(1 for template in templates if template.visibility == WorkflowTemplateVisibility.TENANT),
        templates=templates,
        installable_count=sum(1 for template in templates if template.installable),
        installed_count=sum(1 for template in templates if template.installed),
        scope_summary={
            scope: sum(1 for template in templates if template.governance.scope.value == scope)
            for scope in {template.governance.scope.value for template in templates}
        },
    )


def get_workflow_template_listing(
    template_id: str,
    *,
    tenant_id: str | None = None,
    db: Session | None = None,
) -> WorkflowTemplateListing | None:
    catalog = build_workflow_template_marketplace_catalog(tenant_id=tenant_id, db=db)
    for template in catalog.templates:
        if template.template_id == template_id:
            if tenant_id and db is not None:
                settings = _tenant_settings_from_db(db, tenant_id)
                installs = settings.get(TENANT_INSTALLS_KEY, [])
                if isinstance(installs, list):
                    for record in installs:
                        if isinstance(record, dict) and record.get("template_id") == template_id:
                            object.__setattr__(template, "installed", True)
                            object.__setattr__(template, "installed_record_id", str(record.get("install_id") or ""))
                            object.__setattr__(template, "installed_at", str(record.get("installed_at") or ""))
                            object.__setattr__(template, "installed_scope", str(record.get("target_scope") or ""))
                            break
            return template
    return None


def _tenant_settings_from_db(db: Session, tenant_id: str) -> dict[str, Any]:
    row = db.execute(
        text("SELECT settings FROM domain_shared.tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id},
    ).first()
    if not row or not row[0]:
        return {}
    raw = row[0]
    if isinstance(raw, dict):
        return deepcopy(raw)
    try:
        parsed = json.loads(raw)
        return deepcopy(parsed) if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _save_tenant_settings(db: Session, tenant_id: str, settings: dict[str, Any]) -> None:
    db.execute(
        text(
            """
            UPDATE domain_shared.tenants
            SET settings = CAST(:settings AS jsonb),
                updated_at = NOW()
            WHERE id = :tenant_id
            """
        ),
        {"tenant_id": tenant_id, "settings": json.dumps(settings, ensure_ascii=False, default=str)},
    )


def _governance_warning_bundle(template: WorkflowTemplateListing) -> tuple[list[str], list[str], bool]:
    warnings: list[str] = []
    blocking_reasons: list[str] = []
    publishable = template.publishable

    if template.governance.approval_required:
        warnings.append("Governance fordert Review vor Install/Publish.")
    if template.lifecycle != WorkflowTemplateLifecycle.CURATED:
        warnings.append(f"Lifecycle ist {template.lifecycle.value}; Template nur fuer Review geeignet.")
    if template.visibility == WorkflowTemplateVisibility.TENANT:
        warnings.append("Template ist tenant-spezifisch und sollte nicht global publiziert werden.")
    if template.lifecycle == WorkflowTemplateLifecycle.INTERNAL:
        blocking_reasons.append("Internes oder nicht kuratiertes Template kann nicht publiziert werden.")
        publishable = False
    if template.category == WorkflowTemplateCategory.COMPLIANCE and template.lifecycle != WorkflowTemplateLifecycle.CURATED:
        blocking_reasons.append("Compliance-Template benoetigt kuratierten Status fuer Publikation.")
        publishable = False
    return warnings, blocking_reasons, publishable


def preview_workflow_template_installation(
    *,
    template_id: str,
    tenant_id: str,
    workflow_definition_version: str | None = None,
    context: dict[str, Any] | None = None,
    target_scope: str | None = None,
    requested_by_role: str | None = None,
    db: Session | None = None,
) -> WorkflowTemplatePreview:
    template = get_workflow_template_listing(template_id, tenant_id=tenant_id, db=db)
    if template is None:
        raise ValueError(f"WorkflowTemplate {template_id!r} nicht gefunden")

    warnings, blocking_reasons, publishable = _governance_warning_bundle(template)
    if "approval-gate" in template.required_capabilities:
        warnings.append("Approval- und Rollenmatrix vor Produktivsetzung gegen Tenant-Regeln pruefen.")
    if "background-jobs" in template.required_capabilities:
        warnings.append("Queue- und Retry-Policies fuer schwere Prozessschritte aktivieren.")
    if workflow_definition_version and workflow_definition_version != template.latest_version:
        warnings.append("Preview nutzt eine abweichende Workflow-Definition gegenueber der kuratierten Template-Version.")
    if requested_by_role and requested_by_role not in template.governance.publish_roles:
        blocking_reasons.append(f"Rolle {requested_by_role!r} ist nicht fuer Publish/Install freigeschaltet.")
        publishable = False
    if target_scope == WorkflowTemplateScope.GLOBAL.value and template.governance.scope == WorkflowTemplateScope.TENANT:
        blocking_reasons.append("Tenant-spezifische Templates koennen nicht direkt global publiziert werden.")
        publishable = False

    rollout_steps = [
        "Template-Parameter gegen Tenant-Standards validieren.",
        "Sandbox-/Preview-Lauf fuer den Zielprozess ausfuehren.",
        "Monitoring, Audit und Freigabepfade vor Aktivierung freischalten.",
    ]
    preview_context = dict(context or {})
    if workflow_definition_version:
        preview_context["workflow_definition_version"] = workflow_definition_version
    if target_scope:
        preview_context["target_scope"] = target_scope
    if requested_by_role:
        preview_context["requested_by_role"] = requested_by_role

    return WorkflowTemplatePreview(
        template_id=template.template_id,
        tenant_id=tenant_id,
        process_key=template.process_key,
        estimated_setup_hours=template.setup_hours,
        generated_variant_key=f"{tenant_id}:{template.process_key}:{template.latest_version}",
        warnings=warnings,
        rollout_steps=rollout_steps,
        preview_context=preview_context,
        target_scope=target_scope or template.governance.scope.value,
        publishable=publishable and not blocking_reasons,
        blocking_reasons=blocking_reasons,
        governance=template.governance,
        recommended_next_action=(
            "Template kann in den Marketplace uebernommen werden."
            if publishable and not blocking_reasons
            else "Governance, Status oder Scope vor der Publikation korrigieren."
        ),
        catalog_revision=template.catalog_revision,
    )


def clone_workflow_template(
    *,
    template_id: str,
    tenant_id: str,
    installed_by: str | None = None,
    clone_name: str | None = None,
    target_scope: str = WorkflowTemplateScope.TENANT.value,
    db: Session | None = None,
) -> WorkflowTemplateCloneResult:
    template = get_workflow_template_listing(template_id, tenant_id=tenant_id, db=db)
    if template is None:
        raise ValueError(f"WorkflowTemplate {template_id!r} nicht gefunden")

    clone_id = f"clone:{uuid7()}"
    cloned_template = {
        **template.as_dict(),
        "clone_id": clone_id,
        "clone_name": clone_name or template.name,
        "target_scope": target_scope,
        "installed_by": installed_by,
        "cloned_at": datetime.now(timezone.utc).isoformat(),
    }
    warnings: list[str] = []
    if installed_by:
        warnings.append(f"Clone angelegt von {installed_by}.")
    if template.lifecycle != WorkflowTemplateLifecycle.CURATED:
        warnings.append("Clone basiert auf einem nicht kuratierten Template.")

    if db is not None:
        settings = _tenant_settings_from_db(db, tenant_id)
        clones = settings.get(TENANT_CLONES_KEY)
        if not isinstance(clones, list):
            clones = []
        clones.append(
            {
                "clone_id": clone_id,
                "template_id": template.template_id,
                "tenant_id": tenant_id,
                "target_scope": target_scope,
                "clone_name": clone_name or template.name,
                "installed_by": installed_by,
                "cloned_at": cloned_template["cloned_at"],
                "cloned_template": deepcopy(cloned_template),
            }
        )
        settings[TENANT_CLONES_KEY] = clones
        _save_tenant_settings(db, tenant_id, settings)
        db.commit()

    return WorkflowTemplateCloneResult(
        template_id=template.template_id,
        tenant_id=tenant_id,
        clone_id=clone_id,
        clone_name=clone_name or template.name,
        target_scope=target_scope,
        persisted=db is not None,
        cloned_template=cloned_template,
        governance=template.governance,
        warnings=warnings,
    )


def install_workflow_template(
    *,
    template_id: str,
    tenant_id: str,
    installed_by: str,
    clone_name: str | None = None,
    target_scope: str = WorkflowTemplateScope.TENANT.value,
    activate: bool = True,
    db: Session | None = None,
) -> WorkflowTemplateInstallResult:
    template = get_workflow_template_listing(template_id, tenant_id=tenant_id, db=db)
    if template is None:
        raise ValueError(f"WorkflowTemplate {template_id!r} nicht gefunden")

    install_id = f"install:{uuid7()}"
    lifecycle_status = "installed_pending_review" if activate else "installed_draft"
    installed_template = {
        **template.as_dict(),
        "install_id": install_id,
        "installed_by": installed_by,
        "installed_version": template.latest_version,
        "process_variant_key": f"{tenant_id}:{template.process_key}:{template.latest_version}",
        "lifecycle_status": lifecycle_status,
        "target_scope": target_scope,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "activated": activate,
        "clone_name": clone_name or template.name,
    }
    warnings: list[str] = []
    if template.lifecycle != WorkflowTemplateLifecycle.CURATED:
        warnings.append("Install basiert auf einer nicht kuratierten Vorlage.")
    if template.governance.approval_required:
        warnings.append("Governance-Pruefung empfohlen, bevor die Vorlage aktiviert wird.")

    if db is not None:
        settings = _tenant_settings_from_db(db, tenant_id)
        installs = settings.get(TENANT_INSTALLS_KEY)
        if not isinstance(installs, list):
            installs = []
        installs.append(
            {
                "install_id": install_id,
                "template_id": template.template_id,
                "tenant_id": tenant_id,
                "installed_by": installed_by,
                "target_scope": target_scope,
                "installed_version": template.latest_version,
                "process_variant_key": installed_template["process_variant_key"],
                "activated": activate,
                "installed_at": installed_template["installed_at"],
                "installed_template": deepcopy(installed_template),
            }
        )
        settings[TENANT_INSTALLS_KEY] = installs
        library = settings.get(TENANT_LIBRARY_KEY)
        if not isinstance(library, dict):
            library = {}
        library[template.template_id] = deepcopy(installed_template)
        settings[TENANT_LIBRARY_KEY] = library
        process_variants = settings.get("process_variants")
        if not isinstance(process_variants, dict):
            process_variants = {}
        process_variants[template.process_key] = {
            "steps": [parameter.key for parameter in template.parameters] or [template.process_key],
            "required_roles": {"install": ["tenant_admin", "prozessmanagement"]},
            "step_sla": {},
            "description": template.description,
            "installed_template_id": template.template_id,
            "install_id": install_id,
            "clone_name": clone_name or template.name,
            "latest_version": template.latest_version,
            "target_scope": target_scope,
            "activated": activate,
            "marketplace_catalog_revision": template.catalog_revision,
        }
        settings["process_variants"] = process_variants
        _save_tenant_settings(db, tenant_id, settings)
        db.commit()

    return WorkflowTemplateInstallResult(
        template_id=template.template_id,
        tenant_id=tenant_id,
        installed_version=template.latest_version,
        process_variant_key=f"{tenant_id}:{template.process_key}:{template.latest_version}",
        lifecycle_status=lifecycle_status,
        required_followups=[
            f"Installiert von {installed_by}",
            "Tenant-spezifische Parameter und Rollenmatrix vervollstaendigen.",
            "Go-Live erst nach Sandbox-Review freigeben.",
        ],
        monitoring_hooks=[
            "/api/v1/workflow/simulation/preview",
            "/api/v1/process/idempotency/audit",
            "/api/v1/process-mining/finance/observation",
        ],
        governance=template.governance,
        registry_key=template.process_key,
        target_scope=target_scope,
        activated=activate,
        persisted=db is not None,
        installed_template=installed_template,
        warnings=warnings,
    )
