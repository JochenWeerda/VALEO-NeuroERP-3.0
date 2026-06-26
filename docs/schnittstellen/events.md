---
title: Event-Katalog (NATS / Outbox) — generiert
description: Maschinenlesbar generierter AsyncAPI-Event-Katalog für VALEO NeuroERP 3.0.
type: reference
audience: [integrator, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Event-Katalog (NATS / Outbox)

> Maschinenlesbare Quelle: [`docs/schnittstellen/asyncapi.yaml`](asyncapi.yaml)
> Generiert via `scripts/generate_asyncapi.py`

VALEO NeuroERP publiziert fachliche Domänen-Events über das **Transactional Outbox Pattern**:
Events werden atomar mit der fachlichen Änderung persistiert und über **NATS JetStream** ausgeliefert.

## Namenskonvention

```
tenant.{tenantId}.<domäne>.<aggregat>.<aktion>
```

## Zustellgarantien

| Eigenschaft | Wert |
|---|---|
| Zustellung | At-least-once (Konsumenten müssen idempotent sein) |
| Transaktionalität | Outbox-Pattern: Event + Datenänderung atomar |
| Mandantentrennung | Jedes Event trägt `tenant_id` |
| Korrelation | `correlation_id` für verteiltes Tracing |

## Agrar

| Event | Kanal | Quelle |
|---|---|---|
| `agrar.contract.allocated` | outbox | `api/v1/endpoints/weighing_tickets.py` |
| `agrar.weighing_ticket.allocated` | outbox | `api/v1/endpoints/weighing_tickets.py` |

## Außendienst

| Event | Kanal | Quelle |
|---|---|---|
| `field_service_task.completed` | outbox | `services/agribusiness_service.py` |
| `field_service_task.created` | outbox | `services/agribusiness_service.py` |

## CRM

| Event | Kanal | Quelle |
|---|---|---|
| `crm_case.created` | outbox | `services/crm_compat_service.py` |

## Einkauf

| Event | Kanal | Quelle |
|---|---|---|
| `goods_receipt.created` | outbox | `services/einkauf_compat_service.py` |
| `procurement.edi.message.ack` | outbox | `services/einkauf_compat_service.py` |
| `procurement.edi.message.created` | outbox | `services/einkauf_compat_service.py` |
| `procurement.return.created` | outbox | `services/einkauf_compat_service.py` |
| `purchase_order.approved` | outbox | `api/v1/endpoints/compat.py` |
| `purchase_order.cancelled` | outbox | `api/v1/endpoints/compat.py` |
| `purchase_order.communication.sent` | outbox | `api/v1/endpoints/compat.py` |
| `purchase_order.created` | outbox | `api/v1/endpoints/compat.py` |
| `service_entry_sheet.created` | outbox | `services/einkauf_compat_service.py` |

## Finanzbuchhaltung

| Event | Kanal | Quelle |
|---|---|---|
| `payment_run.returned` | outbox | `api/v1/endpoints/payment_runs.py` |

## Lager

| Event | Kanal | Quelle |
|---|---|---|
| `lager.auslagerung.created` | outbox | `services/inventory_compat_service.py` |
| `lager.einlagerung.created` | outbox | `services/inventory_compat_service.py` |

## Lager / Materialfluss

| Event | Kanal | Quelle |
|---|---|---|
| `inventory.material_flow.edge_created` | outbox | `services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.edge_updated` | outbox | `services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.flush_charge_booked` | outbox | `services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.node_created` | outbox | `services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.node_updated` | outbox | `services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.silo_cell_created` | outbox | `services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.silo_cell_updated` | outbox | `services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.silo_lot_link_booked` | outbox | `services/agri_lot_link_booking_service.py` |
| `inventory.material_flow.silo_lot_synced` | outbox | `services/agri_silo_lot_link_service.py` |
| `inventory.material_flow.silo_system_created` | outbox | `services/agri_silo_material_flow_service.py` |
| `inventory.material_flow.transfer_booked` | outbox | `services/agri_silo_material_flow_service.py` |

## Logistik

| Event | Kanal | Quelle |
|---|---|---|
| `lkw.registered` | outbox | `services/annahme_service.py` |

## POS / Kasse

| Event | Kanal | Quelle |
|---|---|---|
| `pos.tagesabschluss.created` | outbox | `services/pos_compat_service.py` |

## Portal

| Event | Kanal | Quelle |
|---|---|---|
| `portal_order.cancelled` | outbox | `services/portal_compat_service.py` |
| `portal_order.created` | outbox | `services/portal_compat_service.py` |

## Qualitätssicherung

| Event | Kanal | Quelle |
|---|---|---|
| `qualitaets_check.completed` | outbox | `services/annahme_service.py` |
| `qualitaets_check.created` | outbox | `services/annahme_service.py` |

## Sonstige

| Event | Kanal | Quelle |
|---|---|---|
| `cash_closing.posted` | outbox | `api/v1/endpoints/compat.py` |
| `compliance.violations_detected` | outbox | `workers/compliance_monitor.py` |
| `inventur.abgeschlossen` | outbox | `services/inventory_compat_service.py` |
| `settlement.created` | outbox | `core/settlement_audit_chain.py` |

## System

| Event | Kanal | Quelle |
|---|---|---|
| `tenant.*.agrar_settlement.{verb}` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.ap_invoice.{verb}` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.audit_evidence.created` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.command.dispatched` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.duenge_bilanz.calculated` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.e2e_chain.link_completed` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.iot_device.telemetry` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.payment_run.{verb}` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.process.state_changed` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.silo.transfer` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.sla.violated` | nats | `core/event_consumer_wiring.py` |
| `tenant.*.workflow.{verb}` | nats | `core/event_consumer_wiring.py` |

## Tierernährung

| Event | Kanal | Quelle |
|---|---|---|
| `ration.created` | outbox | `services/inventory_compat_service.py` |

## AsyncAPI-Spec

Die maschinenlesbare Spec im AsyncAPI 2.6 Format:

```yaml
# docs/schnittstellen/asyncapi.yaml
asyncapi: '2.6.0'
info:
  title: VALEO NeuroERP Event-Katalog
  version: '3.0.0'
# ... (vollständige Spec in asyncapi.yaml)
```

## Externe Mock-Endpunkte (E2E / Integration)

Für Playwright-Semantiktests und lokale Integration ohne echte DATEV/TSE/ELSTER-Anbindung
stehen Dev-/Test-Stubs unter `/api/v1/dev/external-mocks/*` bereit. Alle Antworten enthalten
`simulated: true`.

| Endpunkt | Verwendung in Specs |
|---|---|
| `/dev/external-mocks/datev/export` | `fibu-semantic-chain`, `o2c-semantic-chain`, `p2p-semantic-chain` |
| `/dev/external-mocks/tse/sign` | `pos-tse-semantic-chain` |
| `/dev/external-mocks/bank/camt-import` | `fibu-semantic-chain`, `p2p-semantic-chain` |

Vertragsdokumentation: [`docs/agent-docs/runbooks/external-mock-vertraege.md`](../agent-docs/runbooks/external-mock-vertraege.md) (Slice: EXTERNAL-MOCK-WORKFLOW-001).

*Stand: 2026-06-26 · 51 Events · Slice: DOC-ASYNCAPI-001*