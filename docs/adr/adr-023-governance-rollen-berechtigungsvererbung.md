# ADR-023 Governance für Rollen- und Berechtigungsvererbung

**Status:** Accepted  
**Date:** 2026-03-11

## Context
Mit Tenant-/Genossenschaftsmodell, Delegation und Agentenfähigkeit wächst die Komplexität der Rollen- und Berechtigungsvererbung. Ohne explizite Governance entstehen implizite Rechteeskalationen, unklare Zuständigkeiten und schwer nachvollziehbare Sonderfälle zwischen Verbund, Tenant, Rolle und Delegation.

## Decision
VALEO NeuroERP führt eine verbindliche Governance für Rollen- und Berechtigungsvererbung ein.

Verbindliche Grundsätze:
1. Berechtigungen werden über definierte Vererbungsebenen modelliert, mindestens Verbund, Tenant, Rolle und Delegation.
2. Vererbte Rechte sind nachvollziehbar und erklärbar, nicht implizit verborgen.
3. Lokale Abweichungen und Entzüge haben definierte Prioritätsregeln.
4. Delegierte Rechte werden zeitlich, fachlich und operativ begrenzt.
5. Policy- und Freigabelogik dürfen Berechtigungsvererbung nicht verdeckt überschreiben.
6. Jede wirksame Berechtigung muss auditierbar auf ihre Herkunft zurückgeführt werden können.

## Consequences
Positiv:
- Klare Verantwortlichkeit im Verbund- und Tenant-Kontext
- Weniger implizite Rechteeskalation
- Bessere Erklärbarkeit und Auditierbarkeit von Zugriffsentscheidungen

Negativ:
- Mehr Modellierungsaufwand für Rechtebeziehungen
- Höhere Anforderungen an UI-Explainability und Governance
- Bestehende Berechtigungsannahmen müssen konsolidiert werden

## References
- [ADR-013 Tenant-/Genossenschaftsmodell](adr-013-tenant-genossenschaftsmodell.md)
- [ADR-019 Sicherheitsmodell für externe Agenten und delegierte Aktionen](adr-019-sicherheitsmodell-externe-agenten-delegierte-aktionen.md)
