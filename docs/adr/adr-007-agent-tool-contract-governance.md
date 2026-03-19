# ADR-007 Agent-/Tool-Contract-Governance

**Status:** Accepted
**Date:** 2026-03-11

## Context
VALEO NeuroERP positioniert sich als AI-fähiges Vertical ERP. Damit werden externe und interne Agenten, MCP-Tools, OpenAPI-Endpunkte und UI-Aktionspfade Teil derselben Produktoberfläche. Ohne Governance drohen instabile Tool-Verträge, unscharfe Sicherheitsgrenzen, nicht auditierbare Aktionen und inkonsistente Agentenfähigkeiten.

Agenten- und Tool-Integration ist deshalb kein lose angehängtes Feature, sondern ein kontrollierter Vertragsraum.

## Decision
VALEO NeuroERP führt eine verbindliche Governance für Agent- und Tool-Contracts ein.

Verbindliche Grundsätze:
1. Agent- und Tool-Contracts sind produktive Schnittstellen und werden wie öffentliche APIs behandelt.
2. Jeder produktive Tool-Contract besitzt klar definierte Eingaben, Ausgaben, Fehlerfälle und Sicherheitsgrenzen.
3. Prozesskritische Agent-Aktionen binden auf den gemeinsamen Command-/Action-Layer statt auf ad-hoc UI- oder CRUD-Endpunkte.
4. Tool-Freigaben, Policy-Prüfungen und Human-in-the-Loop-Anforderungen werden explizit modelliert.
5. Agent-Manifest, OpenAPI-Subset und MCP-Definitionen müssen konsistent auf dieselbe fachliche Semantik referenzieren.
6. Tool-Nutzung und Agent-Aktionen sind auditierbar.

## Consequences
Positiv:
- Höhere Sicherheit und Stabilität bei Agent-Integrationen
- Weniger Drift zwischen UI, API, MCP und externen Tool-Definitionen
- Saubere Grundlage für skalierbare Agent-Use-Cases

Negativ:
- Mehr Governance-Aufwand bei neuen Agent-Features
- Schnell improvisierte Tooling-Pfade werden bewusst ausgebremst
- Bestehende lose Integrationen müssen vereinheitlicht werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-004 Command-/Action-Layer](adr-004-command-action-layer.md)
- [AGENT-INTEGRATION.md](../AGENT-INTEGRATION.md)
