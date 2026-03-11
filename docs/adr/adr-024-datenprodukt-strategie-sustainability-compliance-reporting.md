# ADR-024 Datenprodukt-Strategie für Sustainability- und Compliance-Reporting

**Status:** Accepted  
**Date:** 2026-03-11

## Context
Sustainability-, ESG-, Audit- und Compliance-Reporting benötigen andere Stabilitäts- und Nachweisanforderungen als operative UIs. Ohne explizite Datenprodukt-Strategie drohen wechselnde Kennzahlendefinitionen, unklare Datenherkunft und schwer reproduzierbare Reports.

## Decision
VALEO NeuroERP behandelt Sustainability- und Compliance-Reporting als eigene Datenproduktklasse.

Verbindliche Grundsätze:
1. Reporting-Produkte besitzen definierte Semantik, Berechnungslogik und Aktualisierungstakte.
2. Operative Read-Models und regulatorische Datenprodukte bleiben bewusst getrennt.
3. Herkunft, Transformation und Version von Reporting-Daten müssen nachvollziehbar sein.
4. Reports dürfen nicht stillschweigend ihre fachliche Definition ändern.
5. Export-, Audit- und Nachweispfade referenzieren dieselben Reporting-Datenprodukte.
6. Compliance- und Sustainability-Reporting erhalten explizite Ownership.

## Consequences
Positiv:
- Höhere Reproduzierbarkeit von Reports
- Weniger Drift zwischen operativen Cockpits und regulatorischen Auswertungen
- Bessere Grundlage für Audit, ESG und Meldelogik

Negativ:
- Mehr Governance- und Datenpflegeaufwand
- Höhere Anforderungen an Historisierung und Versionsführung
- Bestehende Reporting-Pfade müssen harmonisiert werden

## References
- [ADR-015 Analytics-/Benchmark-Datenproduktmodell](adr-015-analytics-benchmark-datenproduktmodell.md)
- [ADR-021 Tenant-weite Datenresidenz- und Exportregeln](adr-021-tenant-weite-datenresidenz-und-exportregeln.md)
