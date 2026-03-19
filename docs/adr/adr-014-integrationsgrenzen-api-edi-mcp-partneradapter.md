# ADR-014 Integrationsgrenzen API / EDI / MCP / Partneradapter

**Status:** Accepted
**Date:** 2026-03-11

## Context
VALEO NeuroERP benötigt mehrere Integrationsformen gleichzeitig: klassische APIs, EDI-Dokumentflüsse, MCP-/Tool-Contracts für Agenten und spezifische Partneradapter. Ohne klare Integrationsgrenzen werden fachliche Semantik, Sicherheitsmodell, Fehlerverhalten und Change-Management unscharf.

Die Integrationskanäle müssen deshalb bewusst getrennt werden, obwohl sie auf denselben Fachkern referenzieren.

## Decision
VALEO NeuroERP führt eine explizite Abgrenzung für API-, EDI-, MCP- und Partneradapter-Integrationen ein.

Verbindliche Grundsätze:
1. Jeder Integrationskanal besitzt einen klaren Zweck:
- API für systematische Anwendungsintegration
- EDI für standardisierte Dokument- und Belegaustausche
- MCP/Tool-Contracts für agentische und interaktive Werkzeugnutzung
- Partneradapter für systemspezifische Sonderanbindungen
2. Alle Integrationskanäle referenzieren denselben Fachkern und dürfen keine eigene konkurrierende Geschäftslogik etablieren.
3. Sicherheits-, Audit- und Freigaberegeln werden pro Integrationsklasse explizit definiert.
4. Partneradapter kapseln Fremdsystem-Spezifika und dürfen nicht in den Domain Core ausstrahlen.
5. Prozesskritische Integrationen binden auf Commands, Events und Read-Models statt auf UI-seitige Sonderpfade.
6. Change-Management und Versionierung werden je Integrationsklasse klar geregelt.

## Consequences
Positiv:
- Weniger Vermischung von Integrationszielen und Verantwortlichkeiten
- Stabilere externe Verträge und sauberere Sicherheitsgrenzen
- Bessere Wartbarkeit bei Partner- und Agentenintegrationen

Negativ:
- Höherer Governance-Aufwand für neue Integrationen
- Zusätzliche Klassifizierungsarbeit vor Implementierung
- Bestehende hybride Integrationspfade müssen bereinigt werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-004 Command-/Action-Layer](adr-004-command-action-layer.md)
- [ADR-007 Agent-/Tool-Contract-Governance](adr-007-agent-tool-contract-governance.md)
