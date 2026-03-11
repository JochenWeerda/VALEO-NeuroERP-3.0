# ADR-021 Tenant-weite Datenresidenz- und Exportregeln

**Status:** Accepted  
**Date:** 2026-03-11

## Context
Mandanten, Genossenschaften und externe Partner stellen unterschiedliche Anforderungen an Datenhaltung, Exportfähigkeit, Aufbewahrung und Nachweisführung. Ohne explizite tenant-weite Regeln drohen unscharfe Datenresidenz, inkonsistente Exportpfade und Konflikte zwischen Audit, Datenschutz und Integrationsbedarf.

## Decision
VALEO NeuroERP führt tenant-weite Datenresidenz- und Exportregeln als expliziten Architekturstandard ein.

Verbindliche Grundsätze:
1. Datenresidenz, Exportierbarkeit und Aufbewahrungsanforderungen werden tenant- oder verbundbezogen modelliert.
2. Fachliche Datenklassen können unterschiedliche Regeln für Speicherung, Export und Löschbarkeit besitzen.
3. Exportpfade für Audit, DMS, Compliance, Agenten und Partnerintegration müssen auf dieselben Grundregeln referenzieren.
4. Tenant-weite Residenz- und Exportregeln dürfen technische Isolation nicht unterlaufen.
5. Abweichungen und Ausnahmen müssen explizit freigegeben und auditierbar sein.
6. Datenresidenz- und Exportregeln sind Teil von Governance, nicht nur Infrastrukturkonfiguration.

## Consequences
Positiv:
- Bessere Steuerbarkeit von Audit-, Datenschutz- und Exportpflichten
- Klare Grundlage für tenant-spezifische Governance
- Weniger Sonderlogik in Integrations- und Dokumentpfaden

Negativ:
- Mehr Modellierungs- und Governance-Aufwand
- Höhere Anforderungen an Klassifikation von Daten und Exportfällen
- Bestehende Exportpfade müssen gegen die neuen Regeln geprüft werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-012 Dokument-/Audit-Evidence-Modell](adr-012-dokument-audit-evidence-modell.md)
- [ADR-013 Tenant-/Genossenschaftsmodell](adr-013-tenant-genossenschaftsmodell.md)
