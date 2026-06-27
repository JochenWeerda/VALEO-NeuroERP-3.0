---
title: Sequenz — Agrar Annahme bis Journal
type: explanation
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Sequenzdiagramm — Annahme → Qualität → Settlement → Journal

Agrar-Kernkette Harvest-to-Settlement. Fachliche Übersicht: [process-map § Agrar](../../process-map.md).

```mermaid
sequenceDiagram
  actor User as Annahme-Mitarbeiter
  participant FE as frontend-web
  participant BE as backend
  participant WAAGE as Waage / L3
  participant QS as agri_qs_workflow
  participant PARTIE as agrar_partie_aggregate
  participant SETTLE as agrar_settlement
  participant FIBU as settlement_journal_bridge
  participant NATS as NATS
  participant PG as PostgreSQL

  User->>FE: LKW registrieren / Wiegung
  FE->>BE: POST annahme / weighing ticket
  opt L3 Anbindung
    BE->>WAAGE: Sync Wiegeschein
    WAAGE-->>BE: WaageId / Gewichte
  end
  BE->>PG: Weighing Ticket persist

  User->>FE: Qualitätsprobe / Labor
  FE->>BE: POST quality result
  BE->>QS: QS-Workflow + Freigabe
  QS->>PG: Quality Result
  QS->>NATS: quality.approved

  BE->>PARTIE: Aggregate Ernteannahmen → Partie
  PARTIE->>PG: Commodity Lot / Charge

  User->>FE: Selbstabrechnung / Settlement
  FE->>BE: POST agrar settlement
  BE->>SETTLE: Kalkulation Trocknung / Preis
  SETTLE->>PG: Settlement Document
  SETTLE->>NATS: settlement.posted

  BE->>FIBU: Journal Bridge
  FIBU->>PG: Journal Entry (domain_erp)
  FIBU->>NATS: invoice.posted / journal.posted
  BE-->>FE: Settlement + FiBu-Referenz
```

## Referenzen

- [C4 Component Agrar](../components/c4-agrar.md)
- [agrar-event-hook-contracts.md](../../agrar-event-hook-contracts.md)
- [ADR-020 Cross-Domain Referenzmodell](../../../adr/adr-020-cross-domain-referenzmodell-kontrakt-charge-qualitaet-settlement.md)
