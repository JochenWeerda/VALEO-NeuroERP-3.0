"""Modulübergreifende Lösch-/Anonymisierung (HTTP-Orchestrierung).

Zielbild nach Abnahme: Erasure-Anfragen laufen zweiphasig (evaluate → execute) gemäß
``docs/architecture/adr-2026-05-06-erasure-decision-api-and-audit.md`` und Policy
``docs/policies/erasure-retention-audit-policy.md``; diese direkten HTTP-Schritte bleiben
bis dahin Übergangsweg und ersetzen weder Decision API noch ERP-/Retention-Policy.
"""

from __future__ import annotations

import logging
from uuid import UUID

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    if settings.INTERNAL_SERVICE_TOKEN:
        return {"Authorization": f"Bearer {settings.INTERNAL_SERVICE_TOKEN}"}
    return {}


async def orchestrate_erasure(*, tenant_id: str, contact_id: UUID, anonymize_only: bool) -> dict:
    timeout = httpx.Timeout(settings.CRM_INTEGRATION_TIMEOUT_SECONDS)
    log: dict = {"steps": [], "warnings": []}

    async with httpx.AsyncClient(timeout=timeout, headers=_headers()) as client:
        # 1 Sales: Kontakt-Referenzen lösen
        r = await client.post(
            f"{settings.CRM_SALES_BASE_URL}/opportunities/by-contact/{contact_id}/unlink-references",
            params={"tenant_id": tenant_id, "changed_by": "crm-gdpr"},
        )
        log["steps"].append({"sales_unlink": r.status_code})
        if r.status_code >= 400:
            log["warnings"].append(f"sales unlink: HTTP {r.status_code} {r.text[:200]}")

        # 2 Core: Aktivitäten zum Kontakt
        r = await client.delete(
            f"{settings.CRM_CORE_BASE_URL}/activities/by-contact/{contact_id}",
            params={"tenant_id": tenant_id},
        )
        log["steps"].append({"activities_deleted": r.status_code})
        if r.status_code >= 400:
            log["warnings"].append(f"activities: HTTP {r.status_code}")

        # 3 Marketing: Empfänger/ Segmente pseudonymisieren
        r = await client.post(
            f"{settings.CRM_MARKETING_BASE_URL}/campaigns/contact-data/anonymize",
            params={"contact_id": str(contact_id)},
            headers={"X-Tenant-ID": tenant_id},
        )
        log["steps"].append({"marketing_anonymize": r.status_code})
        if r.status_code >= 400:
            log["warnings"].append(f"marketing: HTTP {r.status_code} {r.text[:200]}")

        # 4 Einwilligungen löschen (personenbezogen)
        r = await client.get(
            f"{settings.CRM_CONSENT_BASE_URL}/consents",
            params={"tenant_id": tenant_id, "contact_id": str(contact_id)},
        )
        consents = r.json() if r.status_code == 200 else []
        if not isinstance(consents, list):
            consents = []

        deleted = 0
        for c in consents:
            cid = c.get("id")
            if not cid:
                continue
            dr = await client.delete(f"{settings.CRM_CONSENT_BASE_URL}/consents/{cid}")
            if dr.status_code in (204, 200):
                deleted += 1
        log["steps"].append({"consents_deleted": deleted, "fetch_status": r.status_code})

        # 5 Kontakt löschen sobald keine personenbezogenen Zweckbindungen mehr bestehen (oder hard delete)
        if not anonymize_only:
            dl = await client.delete(
                f"{settings.CRM_CORE_BASE_URL}/contacts/{contact_id}",
                params={"tenant_id": tenant_id},
            )
            log["steps"].append({"contact_delete": dl.status_code})
            if dl.status_code >= 400:
                log["warnings"].append(f"contact delete: HTTP {dl.status_code} {dl.text[:200]} — Retention/GoBD may block")
        else:
            log["steps"].append({"contact_delete": "skipped_anonymize_only"})

    return log
