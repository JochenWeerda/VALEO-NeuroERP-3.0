---
title: ERD — Canonical Domain Model
type: reference
audience: [entwickler, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: Mermaid ERD der Kernaggregate aus ADR-003 — logisches Modell, nicht physisches DB-Schema.
---

# ERD — Canonical Domain Model

Logisches **Entity-Relationship-Diagramm** der verbindlichen Kernaggregate ([ADR-003](../../adr/adr-003-canonical-domain-model.md)). Gegen ADR-003 geprueft am 2026-09-17: kein neues Kernaggregat seit 2026-03-11. Physische Tabellen, Spalten, Besitz und Verbraucher stehen im [Tabellenkatalog](../../admin/table-catalog.md), nicht in diesem Diagramm. Tenancy: [Datenmodell & Tenancy](../../entwickler/datenmodell-tenancy.md). Belegketten-**Layout**: [MASKEN.md](../../MASKEN.md).

```mermaid
erDiagram
  TENANT ||--o{ COMPANY : owns
  TENANT ||--o{ USER : has
  USER }o--o{ ROLE : assigned
  ROLE ||--o{ PERMISSION : grants

  BUSINESS_PARTNER ||--o{ ORDER : places
  BUSINESS_PARTNER ||--o{ CONTRACT : signs
  ITEM ||--o{ ORDER_LINE : references
  ORDER ||--o{ ORDER_LINE : contains
  ORDER ||--o| DELIVERY : fulfills
  ORDER ||--o| INVOICE : bills

  CONTRACT ||--o{ DELIVERY : intake
  DELIVERY ||--o| QUALITY_RESULT : tested
  DELIVERY ||--o| COMMODITY_LOT : creates
  COMMODITY_LOT ||--o{ INVENTORY_MOVE : moves
  LOCATION ||--o{ INVENTORY_MOVE : stores

  INVOICE ||--o| PAYMENT : settled
  INVOICE ||--o| JOURNAL_ENTRY : posts
  SETTLEMENT ||--|| JOURNAL_ENTRY : generates

  WORKFLOW_INSTANCE ||--o| DOCUMENT : evidences
  DOCUMENT ||--o{ ATTACHMENT : contains

  FIELD ||--o{ WEIGHING_TICKET : source
  SEASON ||--o{ CONTRACT : frames
  WEIGHING_TICKET ||--|| COMMODITY_LOT : assigns
  QUALITY_RESULT ||--|| COMMODITY_LOT : grades

  TENANT {
    uuid id
    string name
  }
  BUSINESS_PARTNER {
    uuid id
    string partner_number
  }
  CONTRACT {
    uuid id
    string contract_number
  }
  ORDER {
    uuid id
    uuid source_offer_id
  }
  DELIVERY {
    uuid id
    uuid sales_order_id
  }
  INVOICE {
    uuid id
    string invoice_number
  }
  COMMODITY_LOT {
    uuid id
    string charge_number
  }
  WEIGHING_TICKET {
    uuid id
    decimal net_weight
  }
  JOURNAL_ENTRY {
    uuid id
    date posting_date
  }
```

## Agrar-Pflichtaggregate (Zusatz)

| Aggregat | Beziehung |
|---|---|
| Field / Schlag | → Weighing Ticket, Contract |
| Season / Campaign | → Contract, Harvest Window |
| Weighing Ticket | → Commodity Lot / Charge |
| Commodity Lot | → Quality, Inventory, Settlement |
| PSM / Duenger / Saatgut-Anwendung | Item auf Field (ADR-003 Pflichtaggregat; physische Tabellen im Katalog, kein drittes Klassendiagramm) |

## Regeln

1. Keine konkurrierenden Schattenmodelle pro Modul ([ADR-003](../../adr/adr-003-canonical-domain-model.md))
2. Cross-Domain-Referenzen: [ADR-020](../../adr/adr-020-cross-domain-referenzmodell-kontrakt-charge-qualitaet-settlement.md)
3. Tenant-Isolation: [ADR-034](../../adr/adr-034-tenant-isolation-klassifizierungssystem.md)
4. Belegketten-Layout bleibt [MASKEN.md](../../MASKEN.md); die Objekte bleiben dieses ERD
5. Kein Ticket, alle physischen Tabellen hier einzuzeichnen — das ist der [Tabellenkatalog](../../admin/table-catalog.md)

→ [C4 Component Agrar](components/c4-agrar.md) | [C4 Component Finance](components/c4-finance.md) | [UML Klassendiagramm](uml-canonical-domain-class.md)
