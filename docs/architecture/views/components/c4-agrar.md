---
title: C4 Component — Agrar / Annahme
type: explanation
audience: [entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# C4 Component — Agrar / Annahme

Komponenten für Ernteannahme, Qualität, Partie, Settlement und Materialfluss.

```mermaid
flowchart TB
  subgraph ui [Frontend]
    ANNUI[Annahme / Waage Masken]
    SILOUI[Silo / Materialfluss Studio]
  end

  subgraph api [backend FastAPI]
    ROUTER[agrar / annahme Router]
  end

  subgraph services [Domain Services]
    ANN[annahme_service / annahme_service]
    PARTIE[agrar_partie_aggregate_service]
    SETTLE[agrar_settlement_service]
    DRY[agrar_drying_rule_service]
    TROCK[agrar_trocknung_abrechnung_service]
    SELBST[agrar_selbstabrechnung_lifecycle_service]
    CONTRACT[agrar_contract_service]
    QS[agri_qs_workflow_service]
    LOT[agri_silo_lot_link_service]
    MF[agri_silo_material_flow_service]
    WEIGH[agri_lot_link_booking_service]
  end

  subgraph module [modules/agrar]
    CALC[Harvest Calc / Pricing]
    RULES[Drying Rules Engine]
  end

  subgraph events [Events]
    HOOKS[Agrar Event Hooks]
    NATS[(NATS)]
  end

  ANNUI --> ROUTER
  SILOUI --> ROUTER
  ROUTER --> ANN
  ROUTER --> PARTIE
  ROUTER --> SETTLE
  ROUTER --> CONTRACT
  ROUTER --> QS
  ROUTER --> MF
  SETTLE --> DRY
  SETTLE --> TROCK
  PARTIE --> LOT
  LOT --> MF
  module --> services
  services --> HOOKS
  HOOKS --> NATS
```

## Kernaggregate (Agrar)

Weighing Ticket, Commodity Lot/Charge, Quality Result, Contract, Settlement — siehe [ADR-003](../../adr/adr-003-canonical-domain-model.md), [ADR-020](../../adr/adr-020-cross-domain-referenzmodell-kontrakt-charge-qualitaet-settlement.md).

Quellen: [agrar-event-hook-contracts.md](../../agrar-event-hook-contracts.md), [process-map § Agrar](../process-map.md)

→ [seq-agrar-settlement](../sequences/seq-agrar-settlement.md)
