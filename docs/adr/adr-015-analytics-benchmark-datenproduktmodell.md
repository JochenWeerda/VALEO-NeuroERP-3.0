# ADR-015 Analytics-/Benchmark-Datenproduktmodell

**Status:** Accepted
**Date:** 2026-03-11

## Context
VALEO NeuroERP will Cockpits, Benchmarks, KPI-Drilldowns und agentenfähige Analysepfade nicht als zufälliges Nebenprodukt operativer Daten liefern. Ohne ein Datenproduktmodell entstehen uneinheitliche KPI-Semantiken, unstabile Benchmark-Definitionen und schwer wartbare Analytics-Sichten.

Analytics und Benchmarking brauchen daher ein explizites fachliches Datenproduktmodell.

## Decision
VALEO NeuroERP führt ein explizites Analytics-/Benchmark-Datenproduktmodell ein.

Verbindliche Grundsätze:
1. KPI-, Cockpit- und Benchmark-Sichten werden als fachliche Datenprodukte modelliert, nicht nur als technische SQL-Auswertung.
2. Jedes Datenprodukt besitzt definierte Semantik, Aggregationslogik, Aktualisierungstakt und Verantwortlichkeit.
3. Benchmark-Datenprodukte müssen Vergleichsgruppe, Zeitbezug und Normalisierung explizit machen.
4. Operative Read-Models und analytische Datenprodukte werden bewusst getrennt gehalten.
5. Analytics-Produkte dürfen nicht stillschweigend ihre fachliche Definition ändern.
6. Agenten, Cockpits und Reports konsumieren dieselben fachlich definierten Datenprodukte.

## Consequences
Positiv:
- Stabilere KPI- und Benchmark-Semantik
- Bessere Vergleichbarkeit zwischen Mandanten, Standorten und Zeiträumen
- Saubere Grundlage für Cockpits, Reports und agentische Analysepfade

Negativ:
- Zusätzlicher Modellierungsaufwand für Analytics
- Höhere Anforderungen an Ownership und Definition von Kennzahlen
- Bestehende uneinheitliche KPI-Pfade müssen harmonisiert werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-006 Read-Model / Query-Contract-Prinzip](adr-006-read-model-query-contract-prinzip.md)
- [2026-03-06-top-50-gap-backlog-landhandel.md](../roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md)
