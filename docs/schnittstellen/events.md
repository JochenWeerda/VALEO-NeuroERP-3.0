---
title: Event-Katalog (NATS / Outbox)
type: reference
audience: [integrator, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Event-Katalog (NATS / Outbox)

VALEO NeuroERP publiziert fachliche Domänen-Events über das **Transactional
Outbox Pattern**: Events werden in derselben DB-Transaktion wie die fachliche
Änderung persistiert und anschließend zuverlässig nach **NATS JetStream**
ausgeliefert. So bleibt der Event-Strom konsistent mit dem Datenbestand.

## Namenskonvention

```text
<domäne>.<aggregat>.<aktion>
```

Beispiele: `inventory.material_flow.transfer_booked`,
`procurement.return.created`, `payment_run.returned`.

## Zustellung & Garantien

- **Transaktional:** Event + Datenänderung sind atomar (Outbox).
- **At-least-once:** Konsumenten müssen idempotent verarbeiten.
- **Mandant:** Jedes Event trägt den Tenant-Bezug; Konsumenten respektieren die
  Mandantentrennung.
- **Korrelation:** Korrelations-ID wird zur Nachvollziehbarkeit propagiert.

## Repräsentativer Katalog

### inventory (Materialfluss / Silo)

| Event | Auslöser |
|---|---|
| `inventory.material_flow.silo_system_created` | Silosystem angelegt |
| `inventory.material_flow.silo_cell_created` | Silozelle angelegt |
| `inventory.material_flow.silo_cell_updated` | Silozelle geändert |
| `inventory.material_flow.node_created` | Materialfluss-Knoten angelegt |
| `inventory.material_flow.edge_created` | Materialfluss-Kante angelegt |
| `inventory.material_flow.flush_charge_booked` | Spülcharge gebucht |
| `inventory.material_flow.transfer_booked` | Umlagerung gebucht |
| `inventory.material_flow.silo_lot_link_booked` | Lot-Silozellen-Verknüpfung gebucht |

### procurement (Einkauf)

| Event | Auslöser |
|---|---|
| `purchase_order.created` | Bestellung angelegt |
| `goods_receipt.created` | Wareneingang erfasst |
| `procurement.return.created` | Einkaufsretoure angelegt |
| `service_entry_sheet.created` | Leistungserfassungsblatt angelegt |
| `procurement.edi.message.created` | EDI-Nachricht erzeugt |
| `procurement.edi.message.ack` | EDI-Nachricht bestätigt |

### finance (Zahlungen)

| Event | Auslöser |
|---|---|
| `payment_run.returned` | Zahllauf-Rückläufer verbucht |

### agrar / QS

| Event | Auslöser |
|---|---|
| `qs_status_changed` | QS-Status eines Lots geändert |

!!! note "Vollständige AsyncAPI"
    Dieser Katalog ist kuratiert und repräsentativ. Eine vollständige,
    generierte AsyncAPI-Spezifikation (analog zu OpenAPI) ist als Folgearbeit
    vorgesehen. Single Source of Truth bleiben die Event-Definitionen im Code
    (`enqueue_event(...)` / Outbox-Service).

## Konsumenten-Leitlinien

1. **Idempotent** verarbeiten (Event-ID/Dedup-Key prüfen).
2. **Mandant** aus dem Event respektieren — keine mandantenübergreifende
   Verarbeitung.
3. **Reihenfolge** nicht voraussetzen; auf fachliche Versionsfelder stützen.
4. **Fehler** mit Backoff/Retry behandeln; Dead-Letter für Giftnachrichten.
