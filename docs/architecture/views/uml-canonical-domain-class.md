---
title: UML Klassendiagramm — Canonical Domain Core
type: reference
audience: [entwickler, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: UML classDiagram der Kernaggregate ADR-003 — logisches Modell, keine vollständige Code-Abbildung.
---

# UML Klassendiagramm — Canonical Domain Core

Logisches **UML-Klassendiagramm** der verbindlichen Kernaggregate ([ADR-003](../../adr/adr-003-canonical-domain-model.md)). Gegen ADR-003 geprueft am 2026-09-17: kein neues Kernaggregat seit 2026-03-11. Ergänzt das [ERD](erd-canonical-domain.md) um Verhalten/Ownership — **nicht** eine Code-generierte Abbildung aller SQLAlchemy-Modelle. Physischer Stand: [Tabellenkatalog](../../admin/table-catalog.md).

```mermaid
classDiagram
  direction TB

  class Tenant {
    +UUID id
    +string name
  }
  class Company {
    +UUID id
    +UUID tenantId
  }
  class User {
    +UUID id
    +UUID tenantId
  }
  class Role {
    +UUID id
    +string code
  }
  class Permission {
    +UUID id
    +string code
  }
  class BusinessPartner {
    +UUID id
    +string partnerNumber
  }
  class Item {
    +UUID id
    +string sku
  }
  class Location {
    +UUID id
    +string code
  }
  class Contract {
    +UUID id
    +string contractNumber
  }
  class Order {
    +UUID id
    +UUID sourceOfferId
    +create()
    +confirm()
  }
  class Delivery {
    +UUID id
    +UUID salesOrderId
    +ship()
  }
  class QualityResult {
    +UUID id
    +approve()
  }
  class Invoice {
    +UUID id
    +string invoiceNumber
    +post()
  }
  class Payment {
    +UUID id
    +match()
  }
  class JournalEntry {
    +UUID id
    +date postingDate
    +post()
  }
  class Settlement {
    +UUID id
    +postToJournal()
  }
  class InventoryMove {
    +UUID id
    +apply()
  }
  class WorkflowInstance {
    +UUID id
    +UUID policyId
  }
  class Document {
    +UUID id
    +string paperlessDocId
  }
  class WeighingTicket {
    +UUID id
    +decimal netWeight
  }
  class CommodityLot {
    +UUID id
    +string chargeNumber
  }
  class Field {
    +UUID id
    +string fieldCode
  }
  class Season {
    +UUID id
    +string campaignCode
  }

  Tenant "1" --> "*" Company : owns
  Tenant "1" --> "*" User : has
  User "*" --> "*" Role : assigned
  Role "1" --> "*" Permission : grants
  BusinessPartner "1" --> "*" Order : places
  BusinessPartner "1" --> "*" Contract : signs
  Item "1" --> "*" Order : lineItem
  Order "1" --> "0..1" Delivery : fulfills
  Order "1" --> "0..1" Invoice : bills
  Contract "1" --> "*" Delivery : intake
  Delivery "1" --> "0..1" QualityResult : tested
  Delivery "1" --> "0..1" CommodityLot : creates
  CommodityLot "1" --> "*" InventoryMove : moves
  Location "1" --> "*" InventoryMove : stores
  Invoice "1" --> "0..1" Payment : settled
  Invoice "1" --> "0..1" JournalEntry : posts
  Settlement "1" --> "1" JournalEntry : generates
  WorkflowInstance "1" --> "*" Document : evidences
  Field "1" --> "*" WeighingTicket : source
  Season "1" --> "*" Contract : frames
  WeighingTicket "1" --> "1" CommodityLot : assigns
  QualityResult "1" --> "1" CommodityLot : grades
```

## Abgrenzung

| Artefakt | Zweck |
|---|---|
| Dieses Klassendiagramm | Aggregate, Ownership, zentrale Operationen (logisch) |
| [ERD](erd-canonical-domain.md) | Entitäten und Kardinalitäten |
| [Tabellenkatalog](../../admin/table-catalog.md) | Physische Tabellen, Spalten, Besitz, Verbraucher |
| Alembic / ORM | Physisches Schema — kann mehr Tabellen enthalten |
| [Service-Inventar](../../entwickler/service-inventory.md) | Implementierung pro Modul |
| [MASKEN.md](../../MASKEN.md) | Belegketten-Layout, nicht die Objektmenge |

## Regeln

- Kein monolithisches Klassendiagramm für das gesamte ERP ([ADR-036](../../adr/adr-036-architecture-documentation-stack.md))
- Erweiterungen nur über ADR-003-Prozess — kein Ticket „alle Tabellen ins classDiagram“
- `crm_consents`, Kreditlimite und Geschwistertabellen gehoeren in den Katalog, nicht hierher
- Cross-Domain: [ADR-020](../../adr/adr-020-cross-domain-referenzmodell-kontrakt-charge-qualitaet-settlement.md)

→ [ERD Canonical Domain](erd-canonical-domain.md) | [target-state Landhandel ERP](../../target-state-landhandel-erp.md)
