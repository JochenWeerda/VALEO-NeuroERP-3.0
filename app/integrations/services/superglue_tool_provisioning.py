"""Provision canonical VALEO pilot tools into a Superglue self-host instance."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.tool_sync import refresh_superglue_sync_snapshot


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
