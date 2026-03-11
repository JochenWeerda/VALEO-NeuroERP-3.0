# ADR-019 Sicherheitsmodell für externe Agenten und delegierte Aktionen

**Status:** Accepted  
**Date:** 2026-03-11

## Context
VALEO NeuroERP will externe Agenten, MCP-Tools und delegierte Aktionen produktiv nutzbar machen. Damit entsteht eine Sicherheitslage, die sich von klassischem Benutzer- und API-Zugriff unterscheidet: Agenten handeln im Auftrag, können Aktionsketten auslösen und benötigen klare Grenzen für Delegation, Freigabe, Scope und Audit.

Ohne explizites Sicherheitsmodell drohen unklare Verantwortlichkeit, überprivilegierte Tools und schwer prüfbare Agentenaktionen.

## Decision
VALEO NeuroERP führt ein explizites Sicherheitsmodell für externe Agenten und delegierte Aktionen ein.

Verbindliche Grundsätze:
1. Agentenidentität, Benutzeridentität und delegierte Ausführung werden getrennt modelliert.
2. Delegierte Aktionen erfolgen nur mit explizitem Scope, fachlicher Zulässigkeit und nachvollziehbarer Verantwortlichkeit.
3. Prozesskritische Agentenaktionen benötigen definierte Freigabe-, Policy- oder Human-in-the-Loop-Regeln.
4. Jeder Agent- oder Tool-Aufruf ist auditierbar mit Identität, Delegationskontext, Zielaktion und Ergebnis.
5. Sicherheitsgrenzen für Lesen, Vorschlagen, Simulieren und Ausführen werden getrennt bewertet.
6. Externe Agenten erhalten kein implizites Recht auf UI-seitige Sonderpfade oder interne Service-Privilegien.

## Consequences
Positiv:
- Saubere Sicherheits- und Freigabegrenzen für Agentenaktionen
- Höhere Nachvollziehbarkeit und bessere Auditierbarkeit
- Weniger Risiko durch überprivilegierte Tool-Verträge

Negativ:
- Mehr Sicherheits- und Governance-Aufwand für Agentenintegration
- Höhere Anforderungen an Identitäts- und Delegationsmodellierung
- Bestehende lose Agentenpfade müssen in ein kontrolliertes Modell überführt werden

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-007 Agent-/Tool-Contract-Governance](adr-007-agent-tool-contract-governance.md)
- [ADR-010 Policy-Override-Modell](adr-010-policy-override-modell.md)
