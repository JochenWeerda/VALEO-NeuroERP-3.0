"""Domain-specific Superglue rollout summaries and preview helpers."""

from __future__ import annotations

from typing import Any

from app.integrations.services.superglue_connector_registry import build_superglue_connector_binding
from app.integrations.services.superglue_execution_service import SuperglueExecutionService


_DOMAIN_CONNECTOR_MAP: dict[str, list[str]] = {
    "crm": ["customer_profile"],
    "procurement": ["supplier_directory"],
    "finance": ["finance_export"],
    "logistics": ["carrier_tracking"],
    "agribusiness": ["agribusiness_market"],
    "service": ["field_service_tasks"],
    "analytics": ["analytics_dataset"],
}


def build_superglue_domain_rollout_summary(tenant_id: str) -> dict[str, Any]:
    domains: list[dict[str, Any]] = []
    for domain_key, connector_keys in _DOMAIN_CONNECTOR_MAP.items():
        connectors = [build_superglue_connector_binding(tenant_id=tenant_id, connector_key=key) for key in connector_keys]
        domains.append(
            {
                "domain_key": domain_key,
                "connector_count": len(connectors),
                "connectors": [
                    {
                        "connector_key": binding.connector_key,
                        "tool_id": binding.tool_id,
                        "valeo_contract_id": binding.valeo_contract_id,
                        "execution_modes": list(binding.execution_modes),
                        "system_url": binding.system.url,
                    }
                    for binding in connectors
                ],
            }
        )
    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "domain_count": len(domains),
        "domains": domains,
        "schema_version": 1,
    }


def preview_superglue_domain_rollout(
    *,
    tenant_id: str,
    domain_key: str,
    parameters: dict[str, Any] | None = None,
    execution_service: SuperglueExecutionService | None = None,
) -> dict[str, Any]:
    connector_keys = _DOMAIN_CONNECTOR_MAP.get(domain_key)
    if not connector_keys:
        raise KeyError(domain_key)
    service = execution_service or SuperglueExecutionService()
    previews: list[dict[str, Any]] = []
    for connector_key in connector_keys:
        binding = build_superglue_connector_binding(tenant_id=tenant_id, connector_key=connector_key)
        payload = {
            "tenantId": tenant_id,
            "connector_key": connector_key,
            "human_confirmation": False,
            **dict(parameters or {}),
        }
        if connector_key == "supplier_directory":
            payload.setdefault("supplierId", "supplier-preview")
        elif connector_key == "finance_export":
            payload.setdefault("exportKind", "finance")
            payload.setdefault("recordCount", 1)
            payload.setdefault("artifactLabel", "preview-export.csv")
        elif connector_key == "carrier_tracking":
            payload.setdefault("shipmentId", "shipment-preview")
        elif connector_key == "agribusiness_market":
            payload.setdefault("commodity", "wheat")
            payload.setdefault("region", "de")
        elif connector_key == "field_service_tasks":
            payload.setdefault("status", "open")
            payload.setdefault("limit", 5)
        elif connector_key == "analytics_dataset":
            payload.setdefault("dataset", "operations")
            payload.setdefault("query", "latest")
        elif connector_key == "customer_profile":
            payload.setdefault("customerId", "customer-preview")
        envelope = service.execute_tool(
            tenant_id=tenant_id,
            correlation_id=f"{domain_key}-{connector_key}-preview",
            tool_id=binding.tool_id,
            execution_mode=binding.execution_modes[0],
            target_kind=binding.target_kind,
            payload=payload,
        )
        previews.append(
            {
                "connector_key": connector_key,
                "tool_id": binding.tool_id,
                "result_status": envelope.result_status,
                "artifacts": [artifact.model_dump() for artifact in envelope.artifacts],
                "payload": envelope.payload,
            }
        )
    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "domain_key": domain_key,
        "preview_count": len(previews),
        "previews": previews,
        "schema_version": 1,
    }
