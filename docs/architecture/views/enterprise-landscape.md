---
title: Enterprise-Landkarte (ArchiMate-äquivalent)
type: explanation
audience: [architect, product, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
description: Vereinfachte Enterprise-Architektur — Business, Application, Technology Layers.
---

# Enterprise-Landkarte

Vereinfachtes **ArchiMate-äquivalentes** Schichtenmodell (80/20, Mermaid). Kein `.archimate`-Modell — siehe [ADR-036](../../adr/adr-036-architecture-documentation-stack.md).

```mermaid
flowchart TB
  subgraph business [Business Layer — Fachdomänen]
    CRMb[CRM / Vertrieb]
    FIBUb[Finanzbuchhaltung]
    EINKb[Einkauf / P2P]
    LAGERb[Lager / Silo]
    AGRb[Agrar / Annahme / Waage]
    QSb[Qualität / Labor]
    POSb[Kasse / POS / TSE]
    DMSb[DMS / Archiv]
    COMPb[Compliance / Regulatory]
    BIb[BI / Controlling]
  end

  subgraph application [Application Layer]
    FE[frontend-web]
    BE[backend FastAPI Monolith]
    CRMapp[crm-* Microservices]
    INVapp[inventory-service]
    DMSapp[dms-adapter + paperless]
    KIapp[ki-usability / ai]
    BFFapp[bff-web]
  end

  subgraph data [Data Layer]
    PG[(PostgreSQL ERP)]
    NATS[(NATS Events)]
    REDIS[(Redis Cache)]
    DMSDB[(Paperless DB)]
  end

  subgraph technology [Technology Layer]
    KC[Keycloak OIDC]
    DOCK[Docker Compose / K8s]
    MON[Prometheus Grafana]
  end

  CRMb --> FE
  FIBUb --> FE
  EINKb --> FE
  LAGERb --> FE
  AGRb --> FE
  QSb --> FE
  POSb --> FE
  DMSb --> FE
  COMPb --> FE
  BIb --> FE

  FE --> BFFapp
  FE --> BE
  BFFapp --> BE
  BE --> CRMapp
  BE --> INVapp
  BE --> DMSapp
  BE --> KIapp
  BE --> PG
  BE --> NATS
  BE --> REDIS
  CRMapp --> PG
  INVapp --> PG
  DMSapp --> DMSDB
  FE --> KC
  BE --> KC
  DOCK --> application
  MON --> BE
```

## Domäne → Container → Prozess

| Fachdomäne | Application | Kernprozess |
|---|---|---|
| CRM | crm-*, backend CRM services | O2C, Lead-to-Customer |
| FiBu | backend finance services | Finance-to-Close, DATEV |
| Einkauf | backend procurement | P2P |
| Lager | inventory-service, backend | Inventory-to-Settlement |
| Agrar | modules/agrar, backend agrar_* | Harvest-to-Settlement |
| Waage | backend annahme, L3 | Wiegeschein → Partie |
| DMS | dms-adapter, paperless | Belegarchiv |
| POS/TSE | backend POS, Fiskaly | KassenSichV |
| Compliance | compliance_* services | Compliance-to-Report |
| QS | agri_qs_*, quality | QS-Freigabe |

## Referenzen

- [C4 System Context](c4-01-system-context.md)
- [C4 Container](c4-02-containers.md)
- [process-map.md](../process-map.md)
- [target-state-landhandel-erp.md](../target-state-landhandel-erp.md)
