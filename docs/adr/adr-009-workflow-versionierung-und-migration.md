# ADR-009 Workflow-Versionierung und Migration

**Status:** Accepted
**Date:** 2026-03-11

## Context
Workflow ist als Produktkern gesetzt. Sobald Prozesse versioniert, tenant-spezifisch angepasst und über längere Zeit produktiv betrieben werden, reicht eine statische Workflow-Definition nicht aus. Ohne klare Regeln für Versionierung und Migration drohen laufende Instanzen zu brechen, Simulationen ihre Aussagekraft zu verlieren und Tenant-Varianten unkontrolliert zu divergieren.

## Decision
VALEO NeuroERP führt verbindliche Regeln für Workflow-Versionierung und Migration ein.

Verbindliche Grundsätze:
1. Workflow-Definitionen sind versionierte Artefakte.
2. Neue Prozesslogik wird nicht stillschweigend in bestehende Definitionen überschrieben, sondern als neue Version eingeführt.
3. Laufende Workflow-Instanzen referenzieren explizit ihre Definitionsversion.
4. Migrationen laufender Instanzen sind bewusst zu modellieren und zu dokumentieren; sie sind kein impliziter Nebeneffekt eines Deployments.
5. Tenant-spezifische Varianten bauen nachvollziehbar auf Basisdefinitionen auf.
6. Simulation und Sandbox müssen gegen konkrete Workflow-Versionen laufen.

## Consequences
Positiv:
- Höhere Stabilität bei Prozessänderungen und Releases
- Saubere Auditierbarkeit historischer Prozessläufe
- Bessere Beherrschbarkeit von Tenant-Varianten

Negativ:
- Mehr Governance-Aufwand für Workflow-Änderungen
- Zusätzliche Migrationslogik bei Prozessreleases
- Höhere Anforderungen an Test- und Simulationsdisziplin

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-005 Workflow-/Policy-Kern](adr-005-workflow-policy-kern.md)
- [Open Gaps](../project-context/open-gaps-and-known-issues.md)
