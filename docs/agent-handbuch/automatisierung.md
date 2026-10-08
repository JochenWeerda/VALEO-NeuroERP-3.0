---
title: Automatisierung
type: reference
audience: [ki-agent, entwickler, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-10-08
version: 3.0.0
description: MCP-Tools, Domain-Events und Automatisierungsregeln für Agenten.
---

# Automatisierung

> MCP aus `config/mcp_erp_tools.yaml`, Events aus `scripts/extract_events.py`.

## Automatisierungstypen

| Typ | Mechanismus | Agent-Regel |
|---|---|---|
| **Synchron lesen** | MCP-Tool / GET REST | Idempotent, kein Approval |
| **Vorschlagen** | ActionRuntime `dryRun` / `propose` | Keine Persistenz ohne Freigabe |
| **Ausführen** | ActionRuntime `execute` / POST commandEndpoint | Human-Approval bei HIGH-risk |
| **Prozessgesteuert** | Flow-Spine Instanz + transitions | Nur erlaubte Knoten, Timeline auditieren |
| **Eventgetrieben** | NATS/Outbox (AsyncAPI) | Idempotent reagieren, nicht doppelt auslösen |

## MCP-Tools (Operator-Agent)

Vollständige Referenz: [mcp-tools.md](../schnittstellen/mcp-tools.md)

| tool_id | Domäne | scope | idempotent | Risiko | Human-Approval | endpoint |
|---|---|---|---|---|---|---|
| `agent.proposal.list` | agent | `agent:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `agrar.contract.get` | agrar | `agrar:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `agrar.feed_analysis.transition` | agrar | `agrar:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `agrar.feeding.actual_measure` | agrar | `agrar:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `agrar.feeding.configure_threshold` | agrar | `agrar:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `agrar.feeding.supply_handoff` | agrar | `agrar:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `agrar.ration.transition` | agrar | `agrar:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `agrar.weighing_ticket.list` | agrar | `agrar:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `compliance.gate.status` | compliance | `compliance:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `crm.activity.create` | crm | `crm:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `crm.contact.log` | crm | `crm:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `crm.customer.open` | crm | `crm:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `crm.customer.search` | crm | `crm:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `crm.customer.summary360` | crm | `crm:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `crm.lead.qualify` | crm | `crm:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `dms.document.search` | nachweisraum | `nachweisraum:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `dms.gobd.export_status` | nachweisraum | `nachweisraum:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `einkauf.angebot.bestellen` | einkauf | `einkauf:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `einkauf.anlieferavis.wareneingang` | einkauf | `einkauf:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `einkauf.bestellung.list` | einkauf | `einkauf:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `einkauf.bestellung.status` | einkauf | `einkauf:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `einkauf.bestellung.versenden` | einkauf | `einkauf:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `fibu.dunning.status` | finance | `finance:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `fibu.open_items.list` | finance | `finance:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `finance.ap_invoice.freigeben` | finance | `finance:write` | ja | hoch | ja | `POST /api/v1/mcp/tools/call` |
| `finance.ap_invoice.propose` | finance | `finance:write` | nein | hoch | ja | `POST /api/v1/mcp/tools/call` |
| `lager.bestand.get` | lager | `lager:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `lager.inventur.propose_opening` | lager | `lager:write` | nein | hoch | ja | `POST /api/v1/mcp/tools/call` |
| `lager.inventur.status` | lager | `lager:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `lager.stock_movement.stornieren` | lager | `lager:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `mobile.sync.process_pending` | mobile | `mobile:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `planung.calendar.reproject` | planung | `planung:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `produktion.control.sync` | produktion | `ops:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `qualitaet.reklamation.abschliessen` | qualitaet | `quality:write` | ja | mittel | nein | `POST /api/v1/mcp/tools/call` |
| `sales.invoice.post` | sales | `sales:write` | ja | hoch | ja | `POST /api/v1/mcp/tools/call` |
| `sales.invoice.propose` | sales | `sales:write` | nein | hoch | ja | `POST /api/v1/mcp/tools/call` |
| `sales.order.status` | sales | `sales:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `wms.cell.status` | inventory | `inventory:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |
| `wms.lot.trace` | inventory | `inventory:read` | ja | niedrig | nein | `POST /api/v1/mcp/tools/call` |

## Domain-Events (Auszug)

Vollständiger Katalog: [events.md](../schnittstellen/events.md)

Namenskonvention: `tenant.{tenantId}.<domäne>.<aggregat>.<aktion>`

### Agrar

| Event-ID | Kanal | Quelle |
|---|---|---|
| `agrar.contract.allocated` | outbox | `app/api/v1/endpoints/weighing_tickets.py` |
| `agrar.settlement.pdf_archived` | outbox | `app/api/v1/endpoints/mask_actions.py` |
| `agrar.weighing_ticket.allocated` | outbox | `app/api/v1/endpoints/weighing_tickets.py` |

### Außendienst

| Event-ID | Kanal | Quelle |
|---|---|---|
| `field_service_task.completed` | outbox | `app/services/agribusiness_service.py` |
| `field_service_task.created` | outbox | `app/services/agribusiness_service.py` |

### CRM

| Event-ID | Kanal | Quelle |
|---|---|---|
| `crm.lead.qualified` | outbox | `app/api/v1/endpoints/leads.py` |
| `crm.opportunity.activity_created` | outbox | `app/api/v1/endpoints/mask_actions.py` |
| `crm_case.created` | outbox | `app/services/crm_compat_service.py` |

### Einkauf

| Event-ID | Kanal | Quelle |
|---|---|---|
| `goods_receipt.created` | outbox | `app/services/einkauf_compat_service.py` |
| `procurement.edi.message.ack` | outbox | `app/services/einkauf_compat_service.py` |
| `procurement.edi.message.created` | outbox | `app/services/einkauf_compat_service.py` |
| `procurement.return.created` | outbox | `app/services/einkauf_compat_service.py` |
| `purchase_order.approved` | outbox | `app/services/purchase_order_service.py` |
| `purchase_order.cancelled` | outbox | `app/services/purchase_order_service.py` |
| `purchase_order.communication.sent` | outbox | `app/api/v1/endpoints/compat.py` |
| `purchase_order.created` | outbox | `app/api/v1/endpoints/compat.py` |
| `service_entry_sheet.created` | outbox | `app/services/einkauf_compat_service.py` |

### Finanzbuchhaltung

| Event-ID | Kanal | Quelle |
|---|---|---|
| `payment_run.returned` | outbox | `app/api/v1/endpoints/payment_runs.py` |

### Lager

| Event-ID | Kanal | Quelle |
|---|---|---|
| `lager.auslagerung.created` | outbox | `app/services/inventory_compat_service.py` |
| `lager.einlagerung.created` | outbox | `app/services/inventory_compat_service.py` |
| `lager.stock_movement.storniert` | outbox | `app/api/v1/endpoints/mask_actions.py` |

### Lager / Materialfluss

| Event-ID | Kanal | Quelle |
|---|---|---|
| `inventory.material_flow.edge_created` | outbox | `app/services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.edge_updated` | outbox | `app/services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.flush_charge_booked` | outbox | `app/services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.node_created` | outbox | `app/services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.node_updated` | outbox | `app/services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.silo_cell_created` | outbox | `app/services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.silo_cell_updated` | outbox | `app/services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.silo_lot_link_booked` | outbox | `app/services/agri_lot_link_booking_service.py` |
| `inventory.material_flow.silo_lot_synced` | outbox | `app/services/agri_silo_lot_link_service.py` |
| `inventory.material_flow.silo_system_created` | outbox | `app/services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.transfer_booked` | outbox | `app/services/agri_silo_material_flow_service.py` |

### Logistik

| Event-ID | Kanal | Quelle |
|---|---|---|
| `lkw.registered` | outbox | `app/services/annahme_service.py` |

### Portal

| Event-ID | Kanal | Quelle |
|---|---|---|
| `portal_order.cancelled` | outbox | `app/services/portal_compat_service.py` |
| `portal_order.created` | outbox | `app/services/portal_compat_service.py` |

### Qualitätssicherung

| Event-ID | Kanal | Quelle |
|---|---|---|
| `qualitaets_check.completed` | outbox | `app/services/annahme_service.py` |
| `qualitaets_check.created` | outbox | `app/services/annahme_service.py` |

### Sonstige

| Event-ID | Kanal | Quelle |
|---|---|---|
| `...` | outbox | `scripts/extract_events.py` |
| `cash_closing.posted` | outbox | `app/api/v1/endpoints/compat.py` |
| `collab.note.created` | outbox | `app/api/v1/endpoints/collab_notes.py` |
| `compliance.violations_detected` | outbox | `app/workers/compliance_monitor.py` |
| `einkauf.bestellung.created_from_angebot` | outbox | `app/api/v1/endpoints/mask_actions.py` |
| `einkauf.wareneingang.gebucht` | outbox | `app/api/v1/endpoints/mask_actions.py` |
| `finance.ap_invoice.approved` | outbox | `app/api/v1/endpoints/ap_invoices.py` |
| `finance.ar_open_item.dunning_created` | outbox | `app/api/v1/endpoints/open_items.py` |
| `finance.payment_run.approved` | outbox | `app/api/v1/endpoints/mask_actions.py` |
| `inventur.abgeschlossen` | outbox | `app/services/inventory_compat_service.py` |
| `qualitaet.reklamation.closed` | outbox | `app/api/v1/endpoints/mask_actions.py` |
| `sales.delivery_note.print_requested` | outbox | `app/api/v1/endpoints/mask_actions.py` |
| `settlement.created` | outbox | `app/core/settlement_audit_chain.py` |

### System

| Event-ID | Kanal | Quelle |
|---|---|---|
| `tenant.*.agrar_settlement.{verb}` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.ap_invoice.{verb}` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.audit_evidence.created` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.command.dispatched` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.duenge_bilanz.calculated` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.e2e_chain.link_completed` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.iot_device.telemetry` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.payment_run.{verb}` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.process.state_changed` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.silo.transfer` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.sla.violated` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.workflow.{verb}` | nats | `app/core/event_consumer_wiring.py` |
| `tenant.*.xxx` | nats | `scripts/extract_events.py` |

### Tierernährung

| Event-ID | Kanal | Quelle |
|---|---|---|
| `feeding.actual.recorded` | outbox | `app/services/feeding_actual_service.py` |
| `feeding.analysis.released` | outbox | `app/services/feeding_feed_analysis_service.py` |
| `feeding.deviation.exceeded` | outbox | `app/services/feeding_actual_measure_service.py` |
| `feeding.import.quarantined` | outbox | `app/services/feeding_import_monitor_service.py` |
| `feeding.measure.completed` | outbox | `app/services/feeding_measure_lifecycle_service.py` |
| `feeding.measure.created` | outbox | `app/services/feeding_actual_measure_service.py` |
| `feeding.measure.overdue` | outbox | `app/services/feeding_measure_lifecycle_service.py` |
| `feeding.plan.published` | outbox | `app/services/feeding_plan_service.py` |
| `feeding.ration.version.activated` | outbox | `app/services/rations_lifecycle_service.py` |
| `feeding.supply.procurement_handoff.created` | outbox | `app/services/feeding_supply_service.py` |
| `ration.created` | outbox | `app/services/inventory_compat_service.py` |

## Verbotene Automatisierung

- Kein `execute` bei `humanApprovalRequired=true` ohne menschliche Freigabe
- Kein blindes Wiederholen nicht-idempotenter Tools/POSTs
- Kein Umgehen der Mandantentrennung (`X-Tenant-ID`)
- Zahlungslauf, Ernte-Abrechnung, Storno: nur nach expliziter Policy (siehe Guardrails)
