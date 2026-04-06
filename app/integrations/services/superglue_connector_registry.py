"""Tenant-aware upstream-first connector bindings for Superglue."""

from __future__ import annotations

from typing import Any

from app.integrations.contracts import SuperglueConnectorBinding, SuperglueSystemBinding
from app.integrations.services.superglue_secret_resolver import resolve_superglue_connector_value


_CONNECTOR_DEFAULTS: dict[str, dict[str, Any]] = {
    "document_search": {
        "tool_family": "sg.document.search",
        "valeo_contract_id": "superglue.document.search",
        "display_name": "Superglue Document Search",
        "target_kind": "document",
        "execution_modes": ["read", "suggest"],
        "system_name": "VALEO Document System",
        "default_url": "https://documents.example.invalid/api",
        "specific_instructions": "Primary external DMS endpoint for document search and metadata retrieval.",
        "credential_fields": ["apiKey", "apiSecret", "accessToken"],
    },
    "partner_edi": {
        "tool_family": "sg.partner.adapter.preview",
        "valeo_contract_id": "superglue.partner.adapter.preview",
        "display_name": "Superglue Partner EDI Mapping",
        "target_kind": "partner_adapter",
        "execution_modes": ["simulate", "suggest"],
        "system_name": "VALEO Partner EDI System",
        "default_url": "https://edi.example.invalid/api",
        "specific_instructions": "External partner/EDI endpoint for payload validation and mapping previews.",
        "credential_fields": ["apiKey", "apiSecret", "accessToken", "username", "password"],
    },
    "customer_profile": {
        "tool_family": "sg.customer.profile.preview",
        "valeo_contract_id": "superglue.customer.profile.preview",
        "display_name": "Superglue Customer Profile Lookup",
        "target_kind": "customer_profile",
        "execution_modes": ["read", "suggest"],
        "system_name": "VALEO Customer Masterdata System",
        "default_url": "https://crm.example.invalid/api",
        "specific_instructions": "External CRM/masterdata endpoint for customer profile reads.",
        "credential_fields": ["apiKey", "accessToken", "username", "password"],
    },
    "supplier_directory": {
        "tool_family": "sg.procurement.supplier.lookup",
        "valeo_contract_id": "superglue.procurement.supplier.lookup",
        "display_name": "Superglue Supplier Directory Lookup",
        "target_kind": "external_api",
        "execution_modes": ["read", "suggest"],
        "system_name": "VALEO Supplier Directory",
        "default_url": "https://suppliers.example.invalid/api",
        "specific_instructions": "External supplier/masterdata endpoint for procurement lookups.",
        "credential_fields": ["apiKey", "accessToken", "username", "password"],
    },
    "finance_export": {
        "tool_family": "sg.finance.export.bundle",
        "valeo_contract_id": "superglue.finance.export.bundle",
        "display_name": "Superglue Finance Export Bundle",
        "target_kind": "external_api",
        "execution_modes": ["simulate", "execute"],
        "system_name": "VALEO Finance Export System",
        "default_url": "https://finance.example.invalid/api",
        "specific_instructions": "External finance/export endpoint for regulated export bundles.",
        "credential_fields": ["apiKey", "accessToken"],
    },
    "carrier_tracking": {
        "tool_family": "sg.logistics.carrier.status",
        "valeo_contract_id": "superglue.logistics.carrier.status",
        "display_name": "Superglue Carrier Tracking",
        "target_kind": "external_api",
        "execution_modes": ["read", "suggest"],
        "system_name": "VALEO Carrier Tracking",
        "default_url": "https://carrier.example.invalid/api",
        "specific_instructions": "External carrier/tracking endpoint for shipments and labels.",
        "credential_fields": ["apiKey", "accessToken"],
    },
    "agribusiness_market": {
        "tool_family": "sg.agribusiness.market.quote",
        "valeo_contract_id": "superglue.agribusiness.market.quote",
        "display_name": "Superglue Agribusiness Market Quote",
        "target_kind": "external_api",
        "execution_modes": ["read", "suggest"],
        "system_name": "VALEO Agribusiness Market Data",
        "default_url": "https://agribusiness.example.invalid/api",
        "specific_instructions": "External agribusiness/market endpoint for commodity and partner data.",
        "credential_fields": ["apiKey", "accessToken"],
    },
    "field_service_tasks": {
        "tool_family": "sg.service.field.tasks",
        "valeo_contract_id": "superglue.service.field.tasks",
        "display_name": "Superglue Field Service Tasks",
        "target_kind": "external_api",
        "execution_modes": ["read", "suggest", "simulate"],
        "system_name": "VALEO Field Service Backend",
        "default_url": "https://service.example.invalid/api",
        "specific_instructions": "External field-service endpoint for task sync and dispatch previews.",
        "credential_fields": ["apiKey", "accessToken"],
    },
    "analytics_dataset": {
        "tool_family": "sg.analytics.dataset.query",
        "valeo_contract_id": "superglue.analytics.dataset.query",
        "display_name": "Superglue Analytics Dataset Query",
        "target_kind": "external_api",
        "execution_modes": ["read", "suggest", "simulate"],
        "system_name": "VALEO Analytics Data Source",
        "default_url": "https://analytics.example.invalid/api",
        "specific_instructions": "External analytics endpoint for dataset and insight retrieval.",
        "credential_fields": ["apiKey", "accessToken"],
    },
}


def list_superglue_connector_bindings(tenant_id: str) -> list[SuperglueConnectorBinding]:
    return [build_superglue_connector_binding(tenant_id=tenant_id, connector_key=key) for key in _CONNECTOR_DEFAULTS]


def build_superglue_connector_binding(*, tenant_id: str, connector_key: str) -> SuperglueConnectorBinding:
    normalized_connector_key = str(connector_key or "").strip()
    if normalized_connector_key not in _CONNECTOR_DEFAULTS:
        raise KeyError(f"Unknown Superglue connector key: {connector_key}")

    defaults = _CONNECTOR_DEFAULTS[normalized_connector_key]
    normalized_tenant = _normalize_tenant_slug(tenant_id)
    tool_family = str(defaults["tool_family"])
    system_id = resolve_superglue_connector_value(
        tenant_id=tenant_id,
        connector_key=normalized_connector_key,
        field_name="SYSTEM_ID",
        fallback=f"{normalized_tenant}.{normalized_connector_key}.system",
    )
    system_url = resolve_superglue_connector_value(
        tenant_id=tenant_id,
        connector_key=normalized_connector_key,
        field_name="SYSTEM_URL",
        fallback=str(defaults["default_url"]),
    )
    tool_id = resolve_superglue_connector_value(
        tenant_id=tenant_id,
        connector_key=normalized_connector_key,
        field_name="TOOL_ID",
        fallback=f"{normalized_tenant}.{tool_family}",
    )
    system_name = resolve_superglue_connector_value(
        tenant_id=tenant_id,
        connector_key=normalized_connector_key,
        field_name="SYSTEM_NAME",
        fallback=str(defaults["system_name"]),
    )
    instructions = resolve_superglue_connector_value(
        tenant_id=tenant_id,
        connector_key=normalized_connector_key,
        field_name="SYSTEM_INSTRUCTIONS",
        fallback=str(defaults["specific_instructions"]),
    )
    credentials = {
        field: value
        for field in defaults.get("credential_fields", [])
        if (value := resolve_superglue_connector_value(tenant_id=tenant_id, connector_key=normalized_connector_key, field_name=field))
    }
    runtime_credentials = {
        key: value
        for key, value in credentials.items()
        if key in {"apiKey", "apiSecret", "accessToken", "username", "password"}
    }
    return SuperglueConnectorBinding(
        connector_key=normalized_connector_key,
        tenant_id=str(tenant_id).strip(),
        valeo_contract_id=str(defaults["valeo_contract_id"]),
        tool_id=tool_id,
        display_name=str(defaults["display_name"]),
        target_kind=str(defaults["target_kind"]),
        execution_modes=[str(item) for item in defaults["execution_modes"]],
        system=SuperglueSystemBinding(
            system_id=system_id,
            name=system_name,
            url=system_url,
            credentials=credentials,
            specific_instructions=instructions,
            metadata={
                "connector_key": normalized_connector_key,
                "tool_family": tool_family,
            },
        ),
        run_credentials=runtime_credentials,
        metadata={
            "tool_family": tool_family,
            "connector_key": normalized_connector_key,
            "credential_fields": list(defaults.get("credential_fields", [])),
        },
    )


def _normalize_tenant_slug(tenant_id: str) -> str:
    slug = "".join(char if char.isalnum() else "-" for char in str(tenant_id or "").strip().lower())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "tenant"
