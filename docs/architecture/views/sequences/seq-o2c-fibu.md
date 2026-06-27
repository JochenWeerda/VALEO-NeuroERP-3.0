---
title: Sequenz — Order-to-Cash bis DATEV
type: explanation
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Sequenzdiagramm — O2C → FiBu → DATEV

Technische Interaktion für die Kernkette Angebot → Auftrag → Lieferschein → Rechnung → OP → DATEV. Fachliche Übersicht: [process-map § O2C](../../process-map.md).

```mermaid
sequenceDiagram
  actor User as Sachbearbeiter
  participant FE as frontend-web
  participant BE as backend
  participant PK as Process Kernel
  participant NATS as NATS
  participant PG as PostgreSQL
  participant DATEV as DATEV Export

  User->>FE: Angebot annehmen / in Auftrag wandeln
  FE->>BE: POST /api/v1/sales/orders
  BE->>PK: Command order.create
  BE->>PK: Policy / Workflow prüfen
  BE->>PG: Persist Order
  BE->>PK: Outbox order.confirmed
  PK->>NATS: Event order.confirmed
  BE-->>FE: 201 Order

  User->>FE: Lieferschein aus Auftrag
  FE->>BE: POST delivery (sales_order_id)
  BE->>PG: Validate sales_order_id
  BE->>PK: delivery.shipped Outbox
  PK->>NATS: Event delivery.shipped
  BE->>PG: Persist Delivery

  User->>FE: Rechnung erstellen
  FE->>BE: POST invoice from delivery
  BE->>PG: GoBD invoice_number
  BE->>PK: invoice.posted Outbox
  PK->>NATS: Event invoice.posted
  BE->>PG: OP anlegen

  User->>FE: Zahlung / Auszifferung
  FE->>BE: POST payment + match
  BE->>PG: op_status = ausgeziffert

  User->>FE: Periodenabschluss + DATEV Export
  FE->>BE: POST finance/export/datev
  BE->>PG: Journal / Belegstapel
  BE->>DATEV: Export-Datei / Profil
  DATEV-->>BE: Ack (Steuerberater)
  BE-->>FE: Export-ID
```

## Invarianten

- `sales_order_id` auf Lieferschein = Auftrag-ID
- `invoice_number` nicht null (GoBD)
- OP-Saldo nach Vollzahlung = 0

→ [C4 Component CRM](../components/c4-crm.md) | [C4 Component Finance](../components/c4-finance.md)
