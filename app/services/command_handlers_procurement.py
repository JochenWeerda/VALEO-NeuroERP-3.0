"""
Domain-Mutationen fuer Process-Kernel-Commands (Einkauf).

Registrierung erfolgt beim Laden von app.api.v1.api (siehe register_command_mutations).
"""

from __future__ import annotations

import logging
import os
from datetime import date, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.action_execution import ActionExecutionRequest, ActionExecutionResult
from app.services.numbering_service import get_numbering

logger = logging.getLogger(__name__)


def _create_purchase_order_mutation(
    db: Session,
    request: ActionExecutionRequest,
    result: ActionExecutionResult,
) -> None:
    """
    Legt eine Bestellzeile an, wenn Payload `lieferant_id` und optional `bestellnummer` enthaelt.
    Idempotenz: gleiche bestellnummer pro Tenant wird uebersprungen.
    """
    payload = request.payload or {}
    lid = payload.get("lieferant_id")
    if lid is None:
        logger.debug("CreatePurchaseOrder: keine lieferant_id im Payload — keine DB-Mutation")
        return

    lieferant_id = str(lid).strip()

    tenant_id = request.tenant_id
    if payload.get("bestellnummer") or payload.get("order_number"):
        bn = str(
            payload.get("bestellnummer") or payload.get("order_number")
        ).strip()[:50]
    else:
        safe_tenant = "".join(c if c.isalnum() else "_" for c in tenant_id)[:48]
        tenant_prefix = os.environ.get(f"TENANT_PO_PREFIX_{safe_tenant.upper()}")
        core = get_numbering().next_number("purchase_order")
        bn = (
            f"{tenant_prefix}{core}"
            if tenant_prefix
            else core
        )[:50]
    if not bn:
        bn = f"AE-{request.idempotency_key}"[:40]

    check = db.execute(
        text(
            "SELECT id FROM domain_einkauf.bestellungen "
            "WHERE bestellnummer = :nummer AND tenant_id = :tenant_id LIMIT 1"
        ),
        {"nummer": bn, "tenant_id": tenant_id},
    ).fetchone()
    if check:
        logger.debug("CreatePurchaseOrder: Bestellnummer %s existiert bereits", bn)
        return

    from uuid import uuid4
    bestelldatum = date.today()
    gd = payload.get("gewuenschtes_lieferdatum")
    gew_dt = None
    if isinstance(gd, str) and gd:
        try:
            gew_dt = datetime.fromisoformat(gd[:10]).date()
        except Exception:
            gew_dt = None

    status = str(payload.get("status") or "entwurf")[:30]
    netto = payload.get("netto_summe")
    mwst = payload.get("mwst_betrag")
    brutto = payload.get("brutto_summe")

    db.execute(
        text(
            """
            INSERT INTO domain_einkauf.bestellungen (
                id, tenant_id, bestellnummer, lieferant_id, bestelldatum, lieferdatum_wunsch,
                status, netto_summe, mwst_betrag, brutto_summe
            ) VALUES (
                :id, :tenant_id, :bestellnummer, :lieferant_id, :bestelldatum, :lieferdatum_wunsch,
                :status, :netto_summe, :mwst_betrag, :brutto_summe
            )
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "bestellnummer": bn,
            "lieferant_id": lieferant_id,
            "bestelldatum": bestelldatum,
            "lieferdatum_wunsch": gew_dt,
            "status": status,
            "netto_summe": float(netto) if netto is not None else None,
            "mwst_betrag": float(mwst) if mwst is not None else None,
            "brutto_summe": float(brutto) if brutto is not None else None,
        },
    )


def register_command_mutations() -> None:
    from app.services.action_execution_mutations import register_domain_mutation

    register_domain_mutation("CreatePurchaseOrder", _create_purchase_order_mutation)


def build_procurement_superglue_rollout(tenant_id: str) -> dict[str, object]:
    """Thin wrapper for procurement-specific Superglue rollout metadata."""
    from app.integrations.services.superglue_domain_rollouts import build_superglue_domain_rollout_summary

    summary = build_superglue_domain_rollout_summary(tenant_id)
    domain = next((item for item in summary["domains"] if item["domain_key"] == "procurement"), None)
    return {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "domain_key": "procurement",
        "rollout": domain or {"domain_key": "procurement", "connector_count": 0, "connectors": []},
        "schema_version": 1,
    }
