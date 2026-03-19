# ADR-006 Read-Model / Query-Contract-Prinzip

**Status:** Accepted
**Date:** 2026-03-11

## Context
Die Produktstrategie verlangt prozessfähige Masken, belastbare Cockpits und stabile Agent-/Workflow-Pfade. In der bisherigen Entwicklung waren wiederholt Laufzeitfehler, `undefined`-Query-Daten, inkonsistente API-Antworten und zu stark UI-getriebene Datenmodelle sichtbar.

Für Dashboards, Cockpits, Listen und agentenfähige UIs reicht es nicht aus, direkt auf beliebige Schreibmodelle oder implizite API-Responses zuzugreifen. Es braucht explizite Read-Models und feste Query-Contracts.

## Decision
VALEO NeuroERP führt das Prinzip ein, dass lesende Anwendungsfälle auf expliziten Read-Models und stabilen Query-Contracts basieren.

Verbindliche Grundsätze:
1. Jede fachlich relevante Query liefert einen definierten Contract mit stabilem Initialzustand.
2. UI-Komponenten dürfen keine impliziten `undefined`- oder Halbzustände als normalen Datenpfad voraussetzen.
3. Dashboards, Cockpits und aggregierte Sichten basieren bevorzugt auf Read-Models statt auf zufälligen Live-Joins aus Schreibmodellen.
4. Query-Contracts werden bewusst versioniert oder migrationsfähig gehalten, wenn sich Semantik oder Struktur ändert.
5. Fallbacks, leere Zustände und Fehlerzustände werden fachlich getrennt modelliert.
6. Neue Kernprozesse müssen bewerten, ob ein dediziertes Read-Model nötig ist.

## Consequences
Positiv:
- Weniger Laufzeitfehler und geringere Kopplung zwischen UI und Backend-Implementierungsdetails
- Bessere Performance durch dedizierte Read-Pfade
- Stabilere Grundlage für Analytics, Agenten und Workflow-Transparenz

Negativ:
- Zusätzlicher Modellierungs- und Pflegeaufwand für Query-Seiten
- Höherer Anspruch an API-Disziplin und semantische Vertragsklarheit
- Bestehende uneinheitliche Query-Pfade müssen schrittweise harmonisiert werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [Top-50 Gap Backlog Landhandel](../roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md)
