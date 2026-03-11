# ADR-005 Workflow-/Policy-Kern

**Status:** Accepted  
**Date:** 2026-03-11

## Context
Die angestrebte Spitzenposition entsteht nicht durch mehr CRUD-Seiten, sondern durch prozessfähige, auditable und agentenfähige End-to-End-Abläufe. Harte Prozesslogik in UI oder Services skaliert dafür nicht ausreichend. Freigaben, Tenant-Varianten, SLA, Eskalation, Simulation und Explainability müssen konsistent modelliert werden.

Das Zielbild priorisiert Workflow und Policy deshalb als zentralen Produktkern.

## Decision
Workflow und Policy werden als zentrale Plattformfähigkeit des Produkts behandelt, nicht als optionale Zusatzfunktion.

Verbindliche Grundsätze:
1. Prozessübergänge werden nicht implizit in einzelnen UIs oder Services versteckt.
2. Kritische Prozesse werden als versionierte, mandantenfähige Workflows modelliert.
3. Policies bewerten Commands, Übergänge, Freigaben und Ausnahmen zentral.
4. Workflow-Definitionen und Policy-Entscheidungen sind auditierbar.
5. Explainability ist Teil des Kerns: Entscheidungen müssen im UI nachvollziehbar erklärt werden.
6. Simulation, Sandbox, SLA und Eskalation gelten als Standard für neue kritische Prozessketten.

## Consequences
Positiv:
- Hohe Wiederverwendbarkeit für Freigaben, Eskalation und Tenant-Varianten
- Bessere Auditierbarkeit, Governance und Supportfähigkeit
- Saubere Grundlage für Agenten mit Human-in-the-Loop

Negativ:
- Höherer Plattformaufwand vor schneller Einzelfunktionsentwicklung
- Bestehende implizite Prozesslogik muss sichtbar gemacht und migriert werden
- Mehr Abstimmungsbedarf zwischen Fachdomain, Architektur und UX

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [Top-50 Gap Backlog Landhandel](../roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md)
