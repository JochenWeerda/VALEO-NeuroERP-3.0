"""Provision canonical VALEO pilot tools into a Superglue self-host instance."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.tool_sync import refresh_superglue_sync_snapshot
from app.integrations.services.superglue_connector_registry import (
    SuperglueConnectorBinding,
    build_superglue_connector_binding,
    list_superglue_connector_bindings,
)


_PILOT_TOOL_PAYLOADS: tuple[dict[str, Any], ...] = (
    {
        "id": "sg.document.search",
        "name": "Superglue Document Search",
        "folder": "valeo/pilots/document",
        "instruction": "Read-only document search preview for VALEO pilots.",
        "steps": [
            {
                "id": "document_search_preview",
                "instruction": "Build a deterministic read-only document preview payload.",
                "config": {
                    "type": "transform",
                    "transformCode": (
                        "(sourceData) => {"
                        " const rawQuery = (sourceData.query ?? 'document').toString().trim();"
                        " const slug = (rawQuery || 'document').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'document';"
                        " const limit = Number(sourceData.limit ?? 10) || 10;"
                        " return {"
                        "   documents: [{"
                        "     id: `doc-${slug}`,"
                        "     title: `Document Preview: ${rawQuery || 'Document'}`,"
                        "     source_system: 'superglue',"
                        "     mime_type: 'application/pdf',"
                        "     url: `https://superglue.local/documents/${slug}`,"
                        "     tags: ['pilot', 'document', 'search'],"
                        "     metadata: { tenant_id: String(sourceData.tenantId ?? ''), query: rawQuery, limit: String(limit) }"
                        "   }]"
                        " };"
                        "}"
                    ),
                },
            }
        ],
        "outputTransform": "(sourceData) => sourceData.document_search_preview",
    },
    {
        "id": "sg.partner.adapter.preview",
        "name": "Superglue Partner Adapter Preview",
        "folder": "valeo/pilots/edi",
        "instruction": "Read-only partner adapter preview for VALEO pilots.",
        "steps": [
            {
                "id": "partner_adapter_preview",
                "instruction": "Build a deterministic partner mapping preview.",
                "config": {
                    "type": "transform",
                    "transformCode": (
                        "(sourceData) => {"
                        " const partnerKey = (sourceData.partnerKey ?? 'partner').toString().trim() || 'partner';"
                        " const payloadKeys = Object.keys(sourceData.samplePayload || {});"
                        " return {"
                        "   title: `Partner Preview: ${partnerKey}`,"
                        "   mapped_steps: ['extract', 'map', 'preview'],"
                        "   notices: payloadKeys.length ? [`payload keys: ${payloadKeys.join(', ')}`] : ['read-only preview'],"
                        "   metadata: { tenant_id: String(sourceData.tenantId ?? ''), partner: partnerKey }"
                        " };"
                        "}"
                    ),
                },
            }
        ],
        "outputTransform": "(sourceData) => sourceData.partner_adapter_preview",
    },
    {
        "id": "sg.customer.profile.preview",
        "name": "Superglue Customer Profile Preview",
        "folder": "valeo/pilots/crm",
        "instruction": "Read-only customer profile preview for VALEO pilots.",
        "steps": [
            {
                "id": "customer_profile_preview",
                "instruction": "Build a deterministic customer profile preview.",
                "config": {
                    "type": "transform",
                    "transformCode": (
                        "(sourceData) => {"
                        " const customerId = (sourceData.customerId ?? 'customer').toString().trim() || 'customer';"
                        " return {"
                        "   customer_id: customerId,"
                        "   display_name: `Customer ${customerId}`,"
                        "   status: 'active',"
                        "   email: `${customerId}@example.test`,"
                        "   city: 'Bremen',"
                        "   tags: ['crm', 'preview'],"
                        "   metadata: { tenant_id: String(sourceData.tenantId ?? ''), source: 'superglue-pilot' }"
                        " };"
                        "}"
                    ),
                },
            }
        ],
        "outputTransform": "(sourceData) => sourceData.customer_profile_preview",
    },
)


def provision_superglue_pilot_tools(client: SuperglueClient | None = None) -> dict[str, Any]:
    provision_client = client or SuperglueClient()
    created: list[str] = []
    updated: list[str] = []

    for payload in _PILOT_TOOL_PAYLOADS:
        tool_id = str(payload["id"])
        existing = provision_client.request("GET", f"/v1/tools/{tool_id}", mode="rest", allow_statuses={404})
        if existing.get("error"):
            provision_client.request("POST", "/v1/tools", mode="rest", json=payload)
            created.append(tool_id)
        else:
            update_payload = {key: value for key, value in payload.items() if key != "id"}
            provision_client.request("PUT", f"/v1/tools/{tool_id}", mode="rest", json=update_payload)
            updated.append(tool_id)

    sync_snapshot = refresh_superglue_sync_snapshot(provision_client)
    return {
        "provider_key": "superglue",
        "provisioned_at": datetime.now(timezone.utc).isoformat(),
        "created": created,
        "updated": updated,
        "tool_ids": [str(item["id"]) for item in _PILOT_TOOL_PAYLOADS],
        "tool_count": len(_PILOT_TOOL_PAYLOADS),
        "sync_snapshot": sync_snapshot,
        "schema_version": 1,
    }


def provision_superglue_tenant_connectors(tenant_id: str, client: SuperglueClient | None = None) -> dict[str, Any]:
    provision_client = client or SuperglueClient()
    bindings = list_superglue_connector_bindings(tenant_id)
    systems_created: list[str] = []
    systems_updated: list[str] = []
    tools_created: list[str] = []
    tools_updated: list[str] = []

    for binding in bindings:
        if _upsert_system(provision_client, binding):
            systems_created.append(binding.system.system_id)
        else:
            systems_updated.append(binding.system.system_id)
        if _upsert_tool(provision_client, binding):
            tools_created.append(binding.tool_id)
        else:
            tools_updated.append(binding.tool_id)

    sync_snapshot = refresh_superglue_sync_snapshot(provision_client)
    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "provisioned_at": datetime.now(timezone.utc).isoformat(),
        "connector_count": len(bindings),
        "system_ids": [binding.system.system_id for binding in bindings],
        "tool_ids": [binding.tool_id for binding in bindings],
        "systems_created": systems_created,
        "systems_updated": systems_updated,
        "tools_created": tools_created,
        "tools_updated": tools_updated,
        "sync_snapshot": sync_snapshot,
        "schema_version": 1,
    }


def build_superglue_tool_lifecycle_summary(tenant_id: str) -> dict[str, Any]:
    bindings = list_superglue_connector_bindings(tenant_id)
    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "connector_count": len(bindings),
        "connectors": [
            {
                "connector_key": binding.connector_key,
                "tool_id": binding.tool_id,
                "system_id": binding.system.system_id,
                "system_url": binding.system.url,
                "execution_modes": list(binding.execution_modes),
                "target_kind": binding.target_kind,
                "credential_fields": sorted(binding.run_credentials.keys()),
                "schema_version": 1,
            }
            for binding in bindings
        ],
        "schema_version": 1,
    }


def run_superglue_pilot_smoke(client: SuperglueClient | None = None) -> dict[str, Any]:
    smoke_client = client or SuperglueClient()
    result = smoke_client.request(
        "POST",
        "/v1/tools/sg.document.search/run",
        mode="rest",
        json={
            "inputs": {
                "tenantId": "smoke-tenant",
                "query": "smoke-check",
                "limit": 1,
            },
            "options": {
                "async": False,
                "traceId": "valeo-superglue-smoke",
            },
        },
    )
    return {
        "provider_key": "superglue",
        "tool_id": "sg.document.search",
        "status": result.get("status", "unknown"),
        "run_id": result.get("runId"),
        "data": result.get("data", {}),
        "schema_version": 1,
    }


def _upsert_system(client: SuperglueClient, binding: SuperglueConnectorBinding) -> bool:
    existing = client.request("GET", f"/v1/systems/{binding.system.system_id}", mode="rest", allow_statuses={404})
    payload = {
        "id": binding.system.system_id,
        "name": binding.system.name,
        "url": binding.system.url,
        "credentials": binding.system.credentials,
        "specificInstructions": binding.system.specific_instructions,
        "metadata": {
            **binding.system.metadata,
            "tenantId": binding.tenant_id,
            "valeoContractId": binding.valeo_contract_id,
        },
    }
    if existing.get("error"):
        client.request("POST", "/v1/systems", mode="rest", json=payload)
        return True
    update_payload = {key: value for key, value in payload.items() if key != "id"}
    client.request("PATCH", f"/v1/systems/{binding.system.system_id}", mode="rest", json=update_payload)
    return False


def _upsert_tool(client: SuperglueClient, binding: SuperglueConnectorBinding) -> bool:
    existing = client.request("GET", f"/v1/tools/{binding.tool_id}", mode="rest", allow_statuses={404})
    payload = _build_tool_payload(binding)
    if existing.get("error"):
        client.request("POST", "/v1/tools", mode="rest", json=payload)
        return True
    update_payload = {key: value for key, value in payload.items() if key != "id"}
    client.request("PUT", f"/v1/tools/{binding.tool_id}", mode="rest", json=update_payload)
    return False


def _build_tool_payload(binding: SuperglueConnectorBinding) -> dict[str, Any]:
    if binding.connector_key == "document_search":
        return {
            "id": binding.tool_id,
            "name": binding.display_name,
            "folder": f"valeo/{binding.tenant_id}/document",
            "instruction": "Search documents in the external DMS and return normalized document metadata.",
            "steps": [
                {
                    "id": "document_search_request",
                    "instruction": "Run a document search against the tenant-specific DMS endpoint.",
                    "config": {
                        "type": "request",
                        "url": f"{binding.system.url.rstrip('/')}/documents/search",
                        "method": "GET",
                        "queryParams": {
                            "q": "<<(sourceData) => sourceData.query>>",
                            "limit": "<<(sourceData) => sourceData.limit ?? 10>>",
                        },
                        "headers": {
                            "Authorization": "Bearer <<(sourceData) => sourceData.credentials.apiKey || sourceData.credentials.accessToken || ''>>",
                            "Accept": "application/json",
                        },
                        "systemId": binding.system.system_id,
                    },
                }
            ],
            "outputTransform": (
                "(sourceData) => {"
                " const response = sourceData.document_search_request || {};"
                " const body = response.data || response;"
                " return body.documents || body.items || body;"
                "}"
            ),
        }
    if binding.connector_key == "partner_edi":
        return {
            "id": binding.tool_id,
            "name": binding.display_name,
            "folder": f"valeo/{binding.tenant_id}/edi",
            "instruction": "Simulate or preview partner EDI mappings against the configured external adapter.",
            "steps": [
                {
                    "id": "partner_mapping_request",
                    "instruction": "Submit the sample payload to the external partner mapping endpoint.",
                    "config": {
                        "type": "request",
                        "url": f"{binding.system.url.rstrip('/')}/partner-mappings/preview",
                        "method": "POST",
                        "headers": {
                            "Authorization": "Bearer <<(sourceData) => sourceData.credentials.apiKey || sourceData.credentials.accessToken || ''>>",
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                        },
                        "body": (
                            '{"partnerKey":"<<(sourceData) => sourceData.partnerKey>>",'
                            '"samplePayload":"<<(sourceData) => JSON.stringify(sourceData.samplePayload || {})>>"}'
                        ),
                        "systemId": binding.system.system_id,
                    },
                }
            ],
            "outputTransform": (
                "(sourceData) => {"
                " const response = sourceData.partner_mapping_request || {};"
                " const body = response.data || response;"
                " return body.preview || body;"
                "}"
            ),
        }
    if binding.connector_key == "customer_profile":
        return {
            "id": binding.tool_id,
            "name": binding.display_name,
            "folder": f"valeo/{binding.tenant_id}/crm",
            "instruction": "Read customer profile data from the external masterdata system.",
            "steps": [
                {
                    "id": "customer_profile_request",
                    "instruction": "Fetch a customer profile from the configured external CRM endpoint.",
                    "config": {
                        "type": "request",
                        "url": f"{binding.system.url.rstrip('/')}/customers/<<(sourceData) => sourceData.customerId>>",
                        "method": "GET",
                        "headers": {
                            "Authorization": "Bearer <<(sourceData) => sourceData.credentials.apiKey || sourceData.credentials.accessToken || ''>>",
                            "Accept": "application/json",
                        },
                        "systemId": binding.system.system_id,
                    },
                }
            ],
            "outputTransform": (
                "(sourceData) => {"
                " const response = sourceData.customer_profile_request || {};"
                " const body = response.data || response;"
                " return body.customer || body;"
                "}"
            ),
        }
    if binding.connector_key == "supplier_directory":
        return _build_generic_request_tool(
            binding,
            folder="procurement",
            instruction="Read supplier masterdata from the external supplier directory.",
            step_id="supplier_directory_request",
            url=f"{binding.system.url.rstrip('/')}/suppliers/<<(sourceData) => sourceData.supplierId || sourceData.supplierKey>>",
            method="GET",
            output_transform_key="supplier",
        )
    if binding.connector_key == "finance_export":
        return _build_generic_request_tool(
            binding,
            folder="finance",
            instruction="Create or simulate finance export bundles against the configured external export endpoint.",
            step_id="finance_export_request",
            url=f"{binding.system.url.rstrip('/')}/exports/finance",
            method="POST",
            body=(
                '{"tenantId":"<<(sourceData) => sourceData.tenantId>>",'
                '"exportKind":"<<(sourceData) => sourceData.exportKind || \'finance\'>",'
                '"recordCount":"<<(sourceData) => String(sourceData.recordCount || 0)>>",'
                '"artifactLabel":"<<(sourceData) => sourceData.artifactLabel || \'finance-export.csv\'>"}'
            ),
            output_transform_key="export",
        )
    if binding.connector_key == "carrier_tracking":
        return _build_generic_request_tool(
            binding,
            folder="logistics",
            instruction="Read carrier and shipment status from the configured external logistics endpoint.",
            step_id="carrier_tracking_request",
            url=f"{binding.system.url.rstrip('/')}/shipments/<<(sourceData) => sourceData.shipmentId>>",
            method="GET",
            output_transform_key="shipment",
        )
    if binding.connector_key == "agribusiness_market":
        return _build_generic_request_tool(
            binding,
            folder="agribusiness",
            instruction="Read agribusiness market and partner data from the configured external endpoint.",
            step_id="agribusiness_market_request",
            url=f"{binding.system.url.rstrip('/')}/markets/quotes",
            method="GET",
            query_params={
                "commodity": "<<(sourceData) => sourceData.commodity || 'wheat'>>",
                "region": "<<(sourceData) => sourceData.region || 'de'>>",
            },
            output_transform_key="quote",
        )
    if binding.connector_key == "field_service_tasks":
        return _build_generic_request_tool(
            binding,
            folder="service",
            instruction="Read field-service tasks and dispatch previews from the configured external service endpoint.",
            step_id="field_service_tasks_request",
            url=f"{binding.system.url.rstrip('/')}/field-service/tasks",
            method="GET",
            query_params={
                "status": "<<(sourceData) => sourceData.status || 'open'>>",
                "limit": "<<(sourceData) => sourceData.limit || 25>>",
            },
            output_transform_key="tasks",
        )
    if binding.connector_key == "analytics_dataset":
        return _build_generic_request_tool(
            binding,
            folder="analytics",
            instruction="Query analytics datasets and insight payloads from the configured external endpoint.",
            step_id="analytics_dataset_request",
            url=f"{binding.system.url.rstrip('/')}/analytics/datasets/query",
            method="POST",
            body=(
                '{"dataset":"<<(sourceData) => sourceData.dataset || \'default\'>",'
                '"query":"<<(sourceData) => sourceData.query || \'latest\'>"}'
            ),
            output_transform_key="dataset",
        )
    return {
        "id": binding.tool_id,
        "name": binding.display_name,
        "folder": f"valeo/{binding.tenant_id}/crm",
        "instruction": "Read customer profile data from the external masterdata system.",
        "steps": [
            {
                "id": "customer_profile_request",
                "instruction": "Fetch a customer profile from the configured external CRM endpoint.",
                "config": {
                    "type": "request",
                    "url": f"{binding.system.url.rstrip('/')}/customers/<<(sourceData) => sourceData.customerId>>",
                    "method": "GET",
                    "headers": {
                        "Authorization": "Bearer <<(sourceData) => sourceData.credentials.apiKey || sourceData.credentials.accessToken || ''>>",
                        "Accept": "application/json",
                    },
                    "systemId": binding.system.system_id,
                },
            }
        ],
        "outputTransform": (
            "(sourceData) => {"
            " const response = sourceData.customer_profile_request || {};"
            " const body = response.data || response;"
            " return body.customer || body;"
            "}"
        ),
    }


def _build_generic_request_tool(
    binding: SuperglueConnectorBinding,
    *,
    folder: str,
    instruction: str,
    step_id: str,
    url: str,
    method: str,
    output_transform_key: str,
    query_params: dict[str, str] | None = None,
    body: str | None = None,
) -> dict[str, Any]:
    config: dict[str, Any] = {
        "type": "request",
        "url": url,
        "method": method,
        "headers": {
            "Authorization": "Bearer <<(sourceData) => sourceData.credentials.apiKey || sourceData.credentials.accessToken || ''>>",
            "Accept": "application/json",
        },
        "systemId": binding.system.system_id,
    }
    if query_params:
        config["queryParams"] = query_params
    if body:
        config["headers"]["Content-Type"] = "application/json"
        config["body"] = body
    return {
        "id": binding.tool_id,
        "name": binding.display_name,
        "folder": f"valeo/{binding.tenant_id}/{folder}",
        "instruction": instruction,
        "steps": [
            {
                "id": step_id,
                "instruction": instruction,
                "config": config,
            }
        ],
        "outputTransform": (
            "(sourceData) => {"
            f" const response = sourceData.{step_id} || {{}};"
            " const body = response.data || response;"
            f" return body.{output_transform_key} || body.items || body;"
            "}"
        ),
    }
