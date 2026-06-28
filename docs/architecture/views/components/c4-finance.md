---
title: C4 Component — Finance / FiBu
type: explanation
audience: [entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# C4 Component — Finance / FiBu

Komponenten für Offene Posten, Journal, Periodenabschluss, DATEV/ELSTER und Agrar-Settlement-Übergabe.

```mermaid
flowchart TB
  subgraph ui [Frontend]
    FIBUUI[FiBu Masken / UStVA]
  end

  subgraph api [backend + erp-domain]
    FIN_ROUTER[finance / ap / ar Router]
    PK_CMD[command_handlers_finance]
  end

  subgraph services [Domain Services]
    AP[ap_invoice_kernel_posting]
    CLS[closing_checklists_service]
    EXP[accounting_export_profiles]
    JOURNAL[settlement_journal_bridge]
    EXPORT[DATEV Export Pipeline]
  end

  subgraph external [Externe Gates]
    DATEV[DATEV Export]
    ELSTER[ELSTER ERiC]
  end

  subgraph data [Daten]
    ERPDB[(domain_erp PostgreSQL)]
    NATS[(NATS invoice.posted)]
  end

  FIBUUI --> FIN_ROUTER
  FIN_ROUTER --> AP
  FIN_ROUTER --> CLS
  PK_CMD --> AP
  AP --> ERPDB
  AP --> NATS
  JOURNAL --> ERPDB
  EXPORT --> DATEV
  FIBUUI --> ELSTER
```

## Kernflüsse

1. **O2C:** Rechnung → OP → Zahlung → Auszifferung ([process-map § O2C](../process-map.md))
2. **P2P:** Eingangsrechnung → Kreditoren-OP ([process-map § P2P](../process-map.md))
3. **FiBu:** Periodenabschluss → DATEV ([process-map § FiBu](../process-map.md))
4. **Agrar:** Settlement → Journal Bridge → FiBu

Quellen: [ADR-001 FiBu Reuse](../../adr/adr-001-fibu-domain-reuse-vs-rewrite.md), [packages/erp-domain](../../../packages/erp-domain/README.md)

→ [seq-o2c-fibu](../sequences/seq-o2c-fibu.md)
