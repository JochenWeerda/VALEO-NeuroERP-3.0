"""
Domain-Mutationen fuer Process-Kernel-Commands (Einkauf).

Registrierung erfolgt beim Laden von app.api.v1.api (siehe register_command_mutations).
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.action_execution import ActionExecutionRequest, ActionExecutionResult

logger = logging.getLogger(__name__)


def _create_purchase_order_mutation(
    db: Session,
    request: ActionExecutionRequest,
    result: ActionExecutionResult,
) -> None:
    """Bestellentwurf in DocFlow, wenn der Payload ``lieferant_id`` traegt (BELEG-052, 09.11.2026).

    Vorher ein Kopf ohne Positionen in ``public.einkauf_bestellungen``, mit ``lieferant_id`` als Ganzzahl (Lieferanten
    tragen UUIDs) und Summen aus dem Payload. Jetzt der Entwurf der Belegart ``purchase_order`` mit den Positionen des
    Payloads (``positionen``: artikel_nr, menge, einheit, einzelpreis, preis_einheit); Summen rechnet DocFlow.
    Wiederholungsschutz ueber den Idempotenzschluessel des Kommandos.
    """
    from app.services.beleg_anlage import lege_beleg_an, position_in_preiseinheit

    payload = request.payload or {}
    lieferant = str(payload.get("lieferant_id") or "").strip()
    if not lieferant:
        logger.debug("CreatePurchaseOrder: keine lieferant_id im Payload - keine DB-Mutation")
        return
    nummer = str(payload.get("bestellnummer") or payload.get("order_number") or "").strip()[:60] or None
    positionen = [position_in_preiseinheit(
        artikel_nr=str(p.get("artikel_nr") or p.get("article_id") or ""), bezeichnung=p.get("artikel_bezeichnung"),
        menge=p.get("menge"), einheit=p.get("einheit"), einzelpreis=p.get("einzelpreis"),
        preis_einheit=p.get("preis_einheit")) for p in (payload.get("positionen") or []) if isinstance(p, dict)]
    akteur = str(payload.get("erstellt_von") or request.issuer_role or "kernel")[:100]
    lege_beleg_an(db, request.tenant_id, "purchase_order", partner_id=lieferant, positionen=positionen,
                  quelle="process_kernel", referenz=str(request.idempotency_key or nummer or "kernel"),
                  entwurf_nr=nummer, akteur=akteur,
                  idempotenz=f"kernel-create-po-{request.idempotency_key}"[:120] if request.idempotency_key else None)


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
