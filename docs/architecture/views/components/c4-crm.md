---
title: C4 Component — CRM
type: explanation
audience: [entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# C4 Component — CRM Bounded Context

Komponenten innerhalb des CRM-Clusters und Monolith-Compat-Layer. Siehe [ADR-CRM-001](../../adr/ADR-CRM-001.md).

```mermaid
flowchart TB
  subgraph ui [Frontend]
    CRMUI[CRM Masken / Cockpit]
  end

  subgraph gateway [API Gateway]
    BE[backend FastAPI]
  end

  subgraph crm_ms [CRM Microservices]
    CORE[crm-core :5600]
    SALES[crm-sales :5700]
    SVC[crm-service :5800]
    WF[crm-workflow :5900]
    ANA[crm-analytics :6000]
    COMM[crm-communication :6100]
    MC[crm-multichannel :6300]
    SEC[crm-security :6400]
  end

  subgraph monolith_svc [Monolith CRM Services]
    BP[business_partner_service]
    LEAD[crm_lead_gen_service]
    KONT[crm_kontakt_service]
    MERGE[crm_merge_service]
    OWN[crm_ownership_service]
    CAP[crm_auto_capture_service]
  end

  subgraph data [Daten]
    PG[(PostgreSQL)]
    NATS[(NATS)]
  end

  CRMUI --> BE
  BE --> CORE
  BE --> SALES
  BE --> SVC
  BE --> BP
  BE --> LEAD
  BE --> KONT
  WF --> NATS
  ANA --> CORE
  ANA --> SALES
  COMM --> CORE
  MC --> COMM
  CORE --> PG
  SALES --> PG
  monolith_svc --> PG
```

## Kernaggregate (CRM)

- Business Partner / Kunde / Interessent
- Ansprechpartner, Kontakthistorie, Wiedervorlage
- Angebot → Auftrag (O2C-Einstieg)
- Lead-Kandidaten, Dubletten, Merge

Quellen: [Service-Inventar](../../entwickler/service-inventory.md) (`crm_*`), [process-map O2C](../process-map.md)

→ [C4 Container](../c4-02-containers.md) | [seq-o2c-fibu](../sequences/seq-o2c-fibu.md)
