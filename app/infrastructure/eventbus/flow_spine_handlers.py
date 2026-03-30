"""
Flow-Spine Event Handlers — NC-14 / NC-G6+
Domain-spezifische Handler fuer Flow-Spine-Events.
Registrieren sich beim NATSEventConsumer.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def handle_order_state_changed(event: dict[str, Any]) -> None:
    """Handler: Bestellungs-Status aendert sich (z.B. created -> approved -> shipped)."""
    payload = event.get("payload", event)
    order_id = payload.get("order_id") or payload.get("aggregate_id")
    new_state = payload.get("new_state") or payload.get("state")
    old_state = payload.get("old_state")

    logger.info(
        "Flow-Spine: Bestellung %s wechselt von '%s' nach '%s'",
        order_id, old_state, new_state,
    )

    if new_state == "approved":
        logger.info("Trigger: Lieferschein-Erstellung fuer Bestellung %s", order_id)
    elif new_state == "cancelled":
        logger.info("Trigger: Storno-Workflow fuer Bestellung %s", order_id)


async def handle_invoice_created(event: dict[str, Any]) -> None:
    """Handler: Rechnung wurde erstellt — Buchhaltung und OP-Liste benachrichtigen."""
    payload = event.get("payload", event)
    invoice_id = payload.get("invoice_id") or payload.get("aggregate_id")
    amount = payload.get("total_amount") or payload.get("amount")

    logger.info(
        "Flow-Spine: Rechnung %s erstellt (Betrag: %s)",
        invoice_id, amount,
    )


async def handle_settlement_completed(event: dict[str, Any]) -> None:
    """Handler: Abrechnung abgeschlossen — Gutschrift/Rechnung erzeugen."""
    payload = event.get("payload", event)
    settlement_id = payload.get("settlement_id") or payload.get("aggregate_id")
    settlement_type = payload.get("settlement_type", "unknown")

    logger.info(
        "Flow-Spine: Abrechnung %s abgeschlossen (Typ: %s)",
        settlement_id, settlement_type,
    )


async def handle_inventory_movement(event: dict[str, Any]) -> None:
    """Handler: Lagerbewegung — Bestandsaktualisierung + Warnung bei Unterdeckung."""
    payload = event.get("payload", event)
    article_id = payload.get("article_id")
    warehouse = payload.get("warehouse_id")
    quantity = payload.get("quantity", 0)
    movement_type = payload.get("movement_type", "unknown")

    logger.info(
        "Flow-Spine: Lagerbewegung %s — Artikel %s, Menge %s, Lager %s",
        movement_type, article_id, quantity, warehouse,
    )

    if isinstance(quantity, (int, float)) and quantity < 0:
        logger.warning(
            "Bestandswarnung: Abgang von %s fuer Artikel %s — Unterdeckungspruefung empfohlen",
            abs(quantity), article_id,
        )


async def handle_contract_position_changed(event: dict[str, Any]) -> None:
    """Handler: Kontraktposition aendert sich — Long/Short-Monitor aktualisieren."""
    payload = event.get("payload", event)
    contract_id = payload.get("contract_id") or payload.get("aggregate_id")
    article = payload.get("article_group") or payload.get("article_id")
    net_position = payload.get("net_position_mt")

    logger.info(
        "Flow-Spine: Kontraktposition geaendert — Kontrakt %s, Artikel %s, Netto-Position: %s MT",
        contract_id, article, net_position,
    )

    if isinstance(net_position, (int, float)) and net_position < 0:
        logger.warning(
            "SHORT-Position: Artikel %s ist um %s MT unterdeckt — Risiko-Alarm",
            article, abs(net_position),
        )


async def handle_neuro_decision(event: dict[str, Any]) -> None:
    """Handler: Neuro-Core hat eine Entscheidung getroffen — Audit-Trail + Observability."""
    payload = event.get("payload", event)
    decision_id = payload.get("decision_id") or payload.get("trace_id")
    intent = payload.get("intent")
    confidence = payload.get("confidence_score")

    logger.info(
        "Flow-Spine: Neuro-Entscheidung %s — Intent: %s (Confidence: %s)",
        decision_id, intent, confidence,
    )


async def handle_channel_message(event: dict[str, Any]) -> None:
    """Handler: Nachricht ueber Kanal empfangen — fuer Multi-Channel-Observability."""
    payload = event.get("payload", event)
    channel = payload.get("channel_type") or payload.get("channel")
    sender = payload.get("sender_id")

    logger.info(
        "Flow-Spine: Kanal-Nachricht empfangen — Kanal: %s, Absender: %s",
        channel, sender,
    )


FLOW_SPINE_HANDLER_REGISTRY: dict[str, Any] = {
    "order.state_changed": handle_order_state_changed,
    "invoice.created": handle_invoice_created,
    "settlement.completed": handle_settlement_completed,
    "inventory.movement": handle_inventory_movement,
    "contract.position_changed": handle_contract_position_changed,
    "neuro.decision": handle_neuro_decision,
    "channel.message_received": handle_channel_message,
}


def register_flow_spine_handlers(consumer: Any) -> None:
    """Registriert alle Flow-Spine-Handler beim NATSEventConsumer."""
    for event_type, handler in FLOW_SPINE_HANDLER_REGISTRY.items():
        consumer.register_handler(event_type, handler)
    logger.info(
        "Flow-Spine: %d Handler registriert (%s)",
        len(FLOW_SPINE_HANDLER_REGISTRY),
        ", ".join(FLOW_SPINE_HANDLER_REGISTRY.keys()),
    )
