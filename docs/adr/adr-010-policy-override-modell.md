# ADR-010 Policy-Override-Modell

**Status:** Accepted
**Date:** 2026-03-11

## Context
Policy ist als Produktkern etabliert. In einem mandantenfähigen ERP für Agrarhandel und Genossenschaften müssen globale Regeln, Tenant-Besonderheiten, Rollenlogik, saisonale Varianten und Ausnahmefreigaben zusammenwirken. Ohne explizites Override-Modell werden Policy-Entscheidungen intransparent, Support-intensiv und schwer auditierbar.

## Decision
VALEO NeuroERP führt ein explizites Policy-Override-Modell mit definierter Prioritäts- und Explainability-Logik ein.

Verbindliche Grundsätze:
1. Policies werden als Basisregeln modelliert, die gezielt überschrieben oder erweitert werden können.
2. Overrides besitzen eine definierte Prioritätsreihenfolge, mindestens für global, tenant-spezifisch, rollenbezogen und prozessbezogen.
3. Jede Policy-Entscheidung muss ihre wirksame Regelkette nachvollziehbar erklären können.
4. Ausnahmen und Freigaben werden nicht außerhalb des Policy-Modells versteckt.
5. Tenant- und Rollen-Overrides müssen auditierbar und versionierbar sein.
6. Simulation und Sandbox müssen auch Override-Kombinationen korrekt bewerten können.

## Consequences
Positiv:
- Höhere Transparenz und bessere Explainability im Policy-System
- Saubere Unterstützung für Mandanten- und Rollenvarianten
- Weniger implizite Sonderlogik in UI und Services

Negativ:
- Mehr Komplexität im Policy-Design
- Höhere Anforderungen an Testabdeckung für Prioritätsregeln
- Bestehende Sonderfälle müssen in das zentrale Modell überführt werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-005 Workflow-/Policy-Kern](adr-005-workflow-policy-kern.md)
- [ADR-007 Agent-/Tool-Contract-Governance](adr-007-agent-tool-contract-governance.md)
