---
title: C4 Component — Einkauf / Lager
type: explanation
audience: [entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# C4 Component — Einkauf / Lager (P2P & Inventory)

Komponenten für Procure-to-Pay und Lager/Inventur — Monolith-Services plus `inventory-service` Microservice.

```mermaid
flowchart TB
  subgraph ui [Frontend]
    EINKUI[Einkauf Masken]
    LAGERUI[Lager / Inventur / Silo]
  end

  subgraph api [backend FastAPI]
    EINK_R[einkauf / procurement Router]
    LAGER_R[inventory / lager Router]
    PK_P[command_handlers_procurement]
  end

  subgraph monolith [Monolith Domain Services]
    PROC[procurement_service]
    MATCH[procurement_match_service]
    EINK_C[einkauf_compat_service]
    INV_C[inventory_compat_service]
    LOT[inventory_lot_trace_service]
    COUNT[inventory_count_close_service]
    CORR[inventory_correction_service]
    WH[warehouse_service]
    FEED[feed_inventory_link_service]
  end

  subgraph ms [inventory-service Microservice]
    INV_MS[inventory-service :5400]
  end

  subgraph events [Events]
    NATS[(NATS goods.received)]
  end

  subgraph data [Daten]
    PG[(PostgreSQL domain_inventory)]
  end

  EINKUI --> EINK_R
  LAGERUI --> LAGER_R
  EINK_R --> PROC
  EINK_R --> MATCH
  EINK_R --> PK_P
  PK_P --> PROC
  MATCH --> PROC
  LAGER_R --> INV_C
  LAGER_R --> LOT
  LAGER_R --> COUNT
  LAGER_R --> WH
  LAGER_R --> INV_MS
  PROC --> NATS
  monolith --> PG
  INV_MS --> PG
```

## Kernflüsse

1. **P2P:** Bestellung → Wareneingang → 3-Wege-Match → Eingangsrechnung ([process-map § P2P](../../process-map.md))
2. **Lager:** Bestand, Umlagerung, Inventur, FEFO/Chargen ([DOM-INV Services](../../../entwickler/service-inventory.md))
3. **Futtermittel-Kette:** `feed_inventory_link_service` ↔ `domain_inventory.articles`

Quellen: [inventory-service](../../../services/inventory/), [process-map § P2P](../../process-map.md)

→ [C4 Container](../c4-02-containers.md) | [Enterprise-Landkarte](../enterprise-landscape.md)
