# ADR-008 Eventing-/Outbox-Standard

**Status:** Accepted
**Date:** 2026-03-11

## Context
Das Zielbild von VALEO NeuroERP verlangt belastbare End-to-End-Prozesse, Auditierbarkeit, Read-Models, Workflow-Transparenz und agentenfähige Aktionen. Dafür reichen synchrone Service-Aufrufe allein nicht aus. Ohne einheitlichen Eventing-Standard entstehen implizite Kopplungen, unklare Zustellgarantien und inkonsistente Reaktionen auf fachliche Änderungen.

Ein verbindlicher Outbox- und Eventing-Standard ist deshalb nötig, damit Commands, Audit, Read-Models und Integrationen auf denselben fachlichen Ereignissen aufbauen.

## Decision
VALEO NeuroERP führt einen verbindlichen Eventing-/Outbox-Standard für fachliche Domänenereignisse ein.

Verbindliche Grundsätze:
1. Prozessrelevante Zustandsänderungen werden als fachliche Domänenereignisse modelliert.
2. Persistenz des fachlichen Zustands und Publikation des Ereignisses werden über ein Outbox-Muster entkoppelt, aber konsistent abgesichert.
3. Read-Models, Workflow-Reaktionen, Audit-Erweiterungen und Integrationen konsumieren bevorzugt Domänenereignisse statt impliziter Nebenwirkungen.
4. Ereignisse erhalten stabile Namen, Versionen und minimale fachliche Semantik.
5. Ereignisse transportieren keine zweite Wahrheit, sondern referenzieren das Canonical Domain Model.
6. Retry-, Dead-Letter- und Idempotenzanforderungen sind für jeden Event-Konsumenten explizit zu bewerten.

## Consequences
Positiv:
- Saubere Grundlage für Read-Models, Workflow-Reaktionen und Integrationen
- Weniger implizite Kopplung zwischen Schreibpfad und Nebenwirkungen
- Bessere Nachvollziehbarkeit von Prozessketten

Negativ:
- Höherer Infrastruktur- und Betriebsaufwand für Event-Pfade
- Mehr Modellierungsdisziplin bei Ereignisnamen und Versionierung
- Bestehende direkte Nebenwirkungen müssen schrittweise auf Events umgestellt werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-003 Canonical Domain Model](adr-003-canonical-domain-model.md)
- [ADR-006 Read-Model / Query-Contract-Prinzip](adr-006-read-model-query-contract-prinzip.md)
