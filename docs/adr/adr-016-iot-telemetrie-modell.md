# ADR-016 IoT-/Telemetrie-Modell

**Status:** Accepted  
**Date:** 2026-03-11

## Context
Im Zielbild für Agrarhandel und Genossenschaften spielen Waage, Silo, Lager, Sensorik und operative Telemetrie eine wachsende Rolle. Ohne gemeinsames IoT-/Telemetrie-Modell entstehen unverbundene Gerätedaten, schwer nachvollziehbare Zustandswechsel und Sonderlogik je Integrationspfad.

Telemetriedaten müssen fachlich anschlussfähig sein an Bestände, Chargen, Annahmen, Qualitätsprozesse, Audit und Commands.

## Decision
VALEO NeuroERP führt ein explizites IoT-/Telemetrie-Modell für Geräte-, Sensor- und Ereignisdaten ein.

Verbindliche Grundsätze:
1. Geräte, Sensorquellen und Telemetrieereignisse werden als eigenständige fachliche Konzepte modelliert.
2. Telemetriedaten referenzieren fachliche Objekte wie Standort, Silo, Waage, Charge, Partie oder Annahmeprozess.
3. Rohtelemetrie und fachlich verdichtete Zustände werden getrennt gehalten.
4. Telemetriedaten lösen nicht direkt versteckte Geschäftslogik aus, sondern binden kontrolliert auf Events, Commands und Workflows.
5. Qualitäts-, Zeit- und Herkunftsinformationen sind verpflichtender Bestandteil von Telemetriedaten.
6. Historisierung und Auditierbarkeit sind für dispositive und prüfungsrelevante Telemetriepfade sicherzustellen.

## Consequences
Positiv:
- Saubere Grundlage für Silo-, Waage- und Lagerintegration
- Bessere Nachvollziehbarkeit von Gerätedaten und Prozessreaktionen
- Weniger Sonderlogik je Hardware- oder Sensorkanal

Negativ:
- Zusätzlicher Modellierungs- und Integrationsaufwand
- Höhere Anforderungen an Datenqualität und Zeitbezug
- Bestehende punktuelle Hardwareanbindungen müssen harmonisiert werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-008 Eventing-/Outbox-Standard](adr-008-eventing-outbox-standard.md)
- [ADR-013 Tenant-/Genossenschaftsmodell](adr-013-tenant-genossenschaftsmodell.md)
