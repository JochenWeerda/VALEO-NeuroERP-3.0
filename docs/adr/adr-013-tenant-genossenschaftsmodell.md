# ADR-013 Tenant-/Genossenschaftsmodell

**Status:** Accepted
**Date:** 2026-03-11

## Context
VALEO NeuroERP adressiert Agrarhandel, Genossenschaften und Verbundstrukturen. In diesem Zielmarkt reicht ein einfaches isoliertes Tenant-Modell oft nicht aus. Es gibt gemeinsame Services, übergreifende Stammdatenbezüge, gruppenweite Policies, lokale Prozessvarianten und unterschiedliche Grade von Mandantenautonomie.

Ohne explizites Modell drohen technische Tenants, fachliche Genossenschaftsstrukturen und Berechtigungsmodelle unkontrolliert zu vermischen.

## Decision
VALEO NeuroERP führt ein explizites Tenant-/Genossenschaftsmodell ein, das technische Isolation und fachliche Verbundstruktur getrennt, aber konsistent abbildet.

Verbindliche Grundsätze:
1. Technischer Tenant und fachliche Verbundstruktur werden als getrennte, aber verknüpfte Konzepte modelliert.
2. Genossenschafts- oder Verbundeinheiten können gemeinsame Standards, Policies, Stammdaten oder Services definieren, ohne die Mandantengrenzen aufzuheben.
3. Vererbung von Einstellungen, Rollenregeln, Workflow-Defaults und Policies erfolgt explizit und nachvollziehbar.
4. Lokale Mandantenabweichungen müssen bewusst modelliert, priorisiert und auditierbar sein.
5. Cross-tenant-Zugriffe sind nur über explizite, fachlich legitimierte Pfade zulässig.
6. Reporting-, Benchmark- und Governance-Sichten dürfen Verbundstrukturen aggregieren, ohne technische Isolation zu verletzen.

## Consequences
Positiv:
- Saubere Grundlage für Genossenschaften und Verbundmodelle
- Weniger Vermischung von Mandantenlogik, Rollenlogik und Organisationsstruktur
- Bessere Grundlage für gruppenweite Policies, Benchmarks und Services

Negativ:
- Höherer Modellierungsaufwand im Organisations- und Berechtigungsbereich
- Mehr Komplexität bei Vererbung und Override-Regeln
- Bestehende implizite Annahmen über Tenant-Grenzen müssen bereinigt werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-003 Canonical Domain Model](adr-003-canonical-domain-model.md)
- [ADR-010 Policy-Override-Modell](adr-010-policy-override-modell.md)
