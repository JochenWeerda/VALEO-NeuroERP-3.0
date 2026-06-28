---
title: Architektur — Viewpoint-Katalog
type: reference
audience: [entwickler, architect]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Viewpoint-Katalog

Welche Sicht für welche Frage — Schnellnavigation.

| Frage | Viewpoint | Dokument |
|---|---|---|
| Mit wem spricht das System extern? | C4 Context | [c4-01-system-context.md](c4-01-system-context.md) |
| Welche deploybaren Bausteine gibt es? | C4 Container | [c4-02-containers.md](c4-02-containers.md) |
| Wie ist CRM/Agrar/FiBu intern aufgebaut? | C4 Component | [components/](components/) |
| Wie ist Einkauf/Lager aufgebaut? | C4 Component | [components/c4-procurement-inventory.md](components/c4-procurement-inventory.md) |
| Wie ist DMS/Compliance aufgebaut? | C4 Component | [components/c4-dms-compliance.md](components/c4-dms-compliance.md) |
| Welche Fachdomänen gibt es? | Enterprise | [enterprise-landscape.md](enterprise-landscape.md) |
| Wie läuft O2C technisch ab? | UML Sequenz | [sequences/seq-o2c-fibu.md](sequences/seq-o2c-fibu.md) |
| Welche Kern-Entitäten gibt es? | ERD | [erd-canonical-domain.md](erd-canonical-domain.md) |
| Wie sehen Aggregate + Operationen aus? | UML Klassen | [uml-canonical-domain-class.md](uml-canonical-domain-class.md) |
| Welche Geschäftskette gilt? | Prozess (Mermaid) | [process-map.md](../process-map.md) |
| Was ist implementiert / getestet? | Delivery | [process-kernel/STATUS.md](../process-kernel/STATUS.md) |
| Warum wurde X so entschieden? | ADR | [adr/README.md](../../adr/README.md) |
| Gesamtstruktur Doku | arc42 | [arc42/01-einfuehrung.md](../arc42/01-einfuehrung.md) |

## Notation

| Standard | Verwendung in VALEO |
|---|---|
| ISO 42010 | Diese Matrix + [stakeholder-concerns.md](stakeholder-concerns.md) |
| ArchiMate | Vereinfacht in [enterprise-landscape.md](enterprise-landscape.md) |
| C4 | Mermaid C4 in `c4-*.md` |
| UML | Mermaid `sequenceDiagram` + `classDiagram` (Canonical Core) in `sequences/`, `uml-canonical-domain-class.md` |
| BPMN | **Nicht** als XML — Mermaid-Flowcharts ([ADR-035](../../adr/adr-035-kein-workflow-designer.md)) |
| arc42 | Hub unter `docs/architecture/arc42/` |
