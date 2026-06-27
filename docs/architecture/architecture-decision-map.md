---
title: Architecture Decision Map
type: reference
audience: [entwickler, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Uebersicht aller ADRs nach Domainbereich und Entscheidungstyp — Navigation durch die Architekturentscheidungen von VALEO NeuroERP.
---

# Architecture Decision Map

## Ziel
Dieses Dokument verdichtet die akzeptierten Architekturentscheidungen in eine kompakte Landkarte. Es zeigt, welche Entscheidungen den Produktkern tragen und wie sie zusammenhängen.

## Domain Core
- [ADR-003 Canonical Domain Model](../adr/adr-003-canonical-domain-model.md)
- [ADR-020 Cross-Domain-Referenzmodell für Kontrakt, Charge, Qualität und Settlement](../adr/adr-020-cross-domain-referenzmodell-kontrakt-charge-qualitaet-settlement.md)

Rolle:
- definiert fachliche Wahrheit
- verhindert Schattenmodelle
- verbindet Kernaggregate entlang der Hauptprozesskette

## Process Core
- [ADR-004 Command-/Action-Layer](../adr/adr-004-command-action-layer.md)
- [ADR-005 Workflow-/Policy-Kern](../adr/adr-005-workflow-policy-kern.md)
- [ADR-009 Workflow-Versionierung und Migration](../adr/adr-009-workflow-versionierung-und-migration.md)
- [ADR-010 Policy-Override-Modell](../adr/adr-010-policy-override-modell.md)
- [ADR-022 Regelmodell für Reklamation, Abzug und Ausnahmebehandlung](../adr/adr-022-regelmodell-reklamation-abzug-ausnahmebehandlung.md)

Rolle:
- steuert geschäftskritische Aktionen und Übergänge
- hält Freigaben, Ausnahmen und Explainability zentral

## Data, Events and Reporting
- [ADR-006 Read-Model / Query-Contract-Prinzip](../adr/adr-006-read-model-query-contract-prinzip.md)
- [ADR-008 Eventing-/Outbox-Standard](../adr/adr-008-eventing-outbox-standard.md)
- [ADR-015 Analytics-/Benchmark-Datenproduktmodell](../adr/adr-015-analytics-benchmark-datenproduktmodell.md)
- [ADR-024 Datenprodukt-Strategie für Sustainability- und Compliance-Reporting](../adr/adr-024-datenprodukt-strategie-sustainability-compliance-reporting.md)
- [ADR-025 Standard für konfliktarme Parallelbearbeitung in Kernprozessen](../adr/adr-025-standard-konfliktarme-parallelbearbeitung.md)
- [ADR-026 Modell für Import-/Staging-/Prüfpipelines](../adr/adr-026-modell-import-staging-pruefpipelines.md)

Rolle:
- trennt Write-, Read-, Reporting- und Intake-Pfade
- stabilisiert Querys, Events, Reports und Bulk-Datenflüsse

## Tenant, Security and Integration
- [ADR-007 Agent-/Tool-Contract-Governance](../adr/adr-007-agent-tool-contract-governance.md)
- [ADR-013 Tenant-/Genossenschaftsmodell](../adr/adr-013-tenant-genossenschaftsmodell.md)
- [ADR-014 Integrationsgrenzen API / EDI / MCP / Partneradapter](../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md)
- [ADR-019 Sicherheitsmodell für externe Agenten und delegierte Aktionen](../adr/adr-019-sicherheitsmodell-externe-agenten-delegierte-aktionen.md)
- [ADR-021 Tenant-weite Datenresidenz- und Exportregeln](../adr/adr-021-tenant-weite-datenresidenz-und-exportregeln.md)
- [ADR-023 Governance für Rollen- und Berechtigungsvererbung](../adr/adr-023-governance-rollen-berechtigungsvererbung.md)

Rolle:
- trennt Integrationsklassen, Identitäten und Delegation
- verbindet Tenant-Governance, Export und Security

## Specialized Process Domains
- [ADR-011 UI-Maskenstrategie](../adr/adr-011-ui-maskenstrategie.md)
- [ADR-012 Dokument-/Audit-Evidence-Modell](../adr/adr-012-dokument-audit-evidence-modell.md)
- [ADR-016 IoT-/Telemetrie-Modell](../adr/adr-016-iot-telemetrie-modell.md)
- [ADR-017 Governance für Pricing-/Marktdatenquellen](../adr/adr-017-governance-pricing-marktdatenquellen.md)
- [ADR-018 Qualitäts-/Labordatenmodell](../adr/adr-018-qualitaets-labordatenmodell.md)

Rolle:
- bindet Spezialdomänen an denselben Kernrahmen
- verhindert fachliche Sonderinseln

## Entscheidungsfluss
1. Domain truth und Referenzraum klären.
2. Geschäftsaktion und Prozesssteuerung festlegen.
3. Read-, Event-, Reporting- und Intake-Pfade modellieren.
4. Tenant-, Rollen-, Sicherheits- und Integrationsgrenzen bestimmen.
5. Spezialdomänen sauber anschließen.
