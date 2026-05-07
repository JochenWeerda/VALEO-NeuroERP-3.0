"""HTTP-Aggregator: CRM-Module für GDPR-Export (korrekte Pfade zum Stand 2026-05)."""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

import httpx

from app.config.settings import settings


def _normalize_base(raw: str | None) -> str | None:
    if raw is None or not str(raw).strip():
        return None
    s = str(raw).strip().rstrip("/")
    return s if s else None


def _headers(*, tenant_id: str) -> dict[str, str]:
    h: dict[str, str] = {"Accept": "application/json", "X-Tenant-ID": tenant_id, "X-Tenant-Id": tenant_id}
    token = settings.INTERNAL_SERVICE_TOKEN
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


async def _get(client: httpx.AsyncClient, url: str, tenant_id: str) -> Any:
    try:
        r = await client.get(url, headers=_headers(tenant_id=tenant_id))
        r.raise_for_status()
        return r.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc), "url": url}


async def collect_contact_modules(
    *,
    tenant_id: str,
    contact_id: UUID,
    data_areas: list[str],
) -> dict[str, Any]:
    cid = str(contact_id)
    timeout = httpx.Timeout(settings.CRM_INTEGRATION_TIMEOUT_SECONDS)
    out: dict[str, Any] = {
        "contact_id": cid,
        "tenant_id": tenant_id,
        "data_areas": data_areas,
        "modules": {},
    }

    area_set = {a.strip().lower() for a in data_areas if a and str(a).strip()}
    if not area_set or "all" in area_set:
        area_set = {"contacts", "opportunities", "activities", "campaigns", "consents"}

    urls: dict[str, str] = {}
    skipped: dict[str, dict[str, Any]] = {}
    base_core = _normalize_base(settings.CRM_CORE_BASE_URL)
    base_sales = _normalize_base(settings.CRM_SALES_BASE_URL)
    base_cons = _normalize_base(settings.CRM_CONSENT_BASE_URL)
    base_mkt = _normalize_base(settings.CRM_MARKETING_BASE_URL)

    def _skip(reason: str) -> dict[str, Any]:
        return {"skipped": True, "reason": reason}

    if "contacts" in area_set:
        if base_core:
            urls["crm_core_contact"] = f"{base_core}/contacts/{cid}?tenant_id={tenant_id}"
        else:
            skipped["crm_core_contact"] = _skip("CRM_CORE_BASE_URL not configured")

    if "activities" in area_set:
        if base_core:
            urls["crm_core_activities"] = (
                f"{base_core}/activities/?tenant_id={tenant_id}&contact_id={cid}&limit=500"
            )
        else:
            skipped["crm_core_activities"] = _skip("CRM_CORE_BASE_URL not configured")

    if "opportunities" in area_set or "sales" in area_set:
        if base_sales:
            urls["crm_sales_opportunities"] = (
                f"{base_sales}/opportunities/?tenant_id={tenant_id}&contact_id={cid}&limit=500"
            )
        else:
            skipped["crm_sales_opportunities"] = _skip("CRM_SALES_BASE_URL not configured")

    if "consents" in area_set:
        if base_cons:
            urls["crm_consent"] = f"{base_cons}/consents?tenant_id={tenant_id}&contact_id={cid}"
        else:
            skipped["crm_consent"] = _skip("CRM_CONSENT_BASE_URL not configured")

    if "campaigns" in area_set or "marketing" in area_set:
        if base_mkt:
            urls["crm_marketing_recipients"] = (
                f"{base_mkt}/campaigns/recipients/by-contact?contact_id={cid}&tenant_id={tenant_id}"
            )
        else:
            skipped["crm_marketing_recipients"] = _skip("CRM_MARKETING_BASE_URL not configured")

    out["modules"].update(skipped)

    async with httpx.AsyncClient(timeout=timeout) as client:

        async def load(key: str, url: str) -> tuple[str, Any]:
            return key, await _get(client, url, tenant_id)

        if urls:
            pairs = await asyncio.gather(*[load(k, u) for k, u in urls.items()])
            for key, payload in pairs:
                out["modules"][key] = payload

    return out
