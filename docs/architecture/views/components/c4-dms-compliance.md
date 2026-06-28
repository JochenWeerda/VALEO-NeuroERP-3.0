---
title: C4 Component — DMS / Compliance
type: explanation
audience: [entwickler, compliance]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# C4 Component — DMS / Compliance

Komponenten für Belegarchiv (Paperless), GoBD-Dokumentenfluss und Regulatory/Compliance-Meldungen.

```mermaid
flowchart TB
  subgraph ui [Frontend]
    DOCUI[Beleg / Anhang UI]
    COMPUI[Compliance / Meldewesen]
  end

  subgraph erp [backend FastAPI]
    DOC_R[documents / archive Router]
    COMP_R[compliance Router]
  end

  subgraph dms_stack [DMS Stack]
    ADAPTER[dms-adapter :8002]
    PAPERLESS[paperless-ngx]
    PDB[(paperless-db)]
    PRQ[(paperless-redis)]
  end

  subgraph compliance_svc [Compliance Services]
    COMP[compliance_service]
    PCN[compliance_pcn_lifecycle_service]
    VVVO[compliance_vvvo_sachkunde_service]
    SPERRE[compliance_sperre_audit_service]
    GOBD[docflow_gobd_service]
    ARCH[archive_service]
  end

  subgraph external [Externe Gates]
    ELSTER[ELSTER / UStVA]
    ATLAS[ATLAS Zoll]
  end

  subgraph data [Daten]
    PG[(PostgreSQL ERP)]
  end

  DOCUI --> DOC_R
  COMPUI --> COMP_R
  DOC_R --> ARCH
  DOC_R --> ADAPTER
  ADAPTER --> PAPERLESS
  PAPERLESS --> PDB
  PAPERLESS --> PRQ
  GOBD --> ADAPTER
  COMP_R --> COMP
  COMP_R --> PCN
  COMP_R --> VVVO
  COMP_R --> SPERRE
  COMP --> ELSTER
  COMP --> ATLAS
  compliance_svc --> PG
  ARCH --> PG
```

## Kernflüsse

1. **DMS:** Upload → dms-adapter → Paperless; `paperless_doc_id` auf Geschäftsobjekt ([dms-paperless-integration.md](../../dms-paperless-integration.md))
2. **GoBD:** Exportpaket + Archiv-Nachweis (`docflow_gobd_service`)
3. **Compliance-to-Report:** PCN, VVVO, Artikel-Sperre, UStVA/ELSTER ([process-map § QS/Compliance](../../process-map.md))

Quellen: [ADR-012](../../../adr/adr-012-dokument-audit-evidence-modell.md), [dms-paperless-integration.md](../../dms-paperless-integration.md)

→ [Sequenz DMS](../../dms-paperless-integration.md) | [C4 Container](../c4-02-containers.md)
