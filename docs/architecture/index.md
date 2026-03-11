# Architecture Index

## Zielbild
- [Target State Landhandel ERP](target-state-landhandel-erp.md)
- [Target Processes](target-processes.md)
- [Current Processes](current-processes.md)

## Decision Status

| ADR | Thema | Status | Cluster |
|-----|-------|--------|---------|
| [ADR-003](../adr/adr-003-canonical-domain-model.md) | Canonical Domain Model | Accepted | Domain Core |
| [ADR-004](../adr/adr-004-command-action-layer.md) | Command-/Action-Layer | Accepted | Process Core |
| [ADR-005](../adr/adr-005-workflow-policy-kern.md) | Workflow-/Policy-Kern | Accepted | Process Core |
| [ADR-006](../adr/adr-006-read-model-query-contract-prinzip.md) | Read-Model / Query-Contract-Prinzip | Accepted | Data & Query |
| [ADR-007](../adr/adr-007-agent-tool-contract-governance.md) | Agent-/Tool-Contract-Governance | Accepted | Agent & Integration |
| [ADR-008](../adr/adr-008-eventing-outbox-standard.md) | Eventing-/Outbox-Standard | Accepted | Data & Query |
| [ADR-009](../adr/adr-009-workflow-versionierung-und-migration.md) | Workflow-Versionierung und Migration | Accepted | Process Core |
| [ADR-010](../adr/adr-010-policy-override-modell.md) | Policy-Override-Modell | Accepted | Process Core |
| [ADR-011](../adr/adr-011-ui-maskenstrategie.md) | UI-Maskenstrategie | Accepted | UX & Process UI |
| [ADR-012](../adr/adr-012-dokument-audit-evidence-modell.md) | Dokument-/Audit-Evidence-Modell | Accepted | Audit & Document |
| [ADR-013](../adr/adr-013-tenant-genossenschaftsmodell.md) | Tenant-/Genossenschaftsmodell | Accepted | Tenant & Organization |
| [ADR-014](../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md) | Integrationsgrenzen API / EDI / MCP / Partneradapter | Accepted | Agent & Integration |
| [ADR-015](../adr/adr-015-analytics-benchmark-datenproduktmodell.md) | Analytics-/Benchmark-Datenproduktmodell | Accepted | Data & Analytics |
| [ADR-016](../adr/adr-016-iot-telemetrie-modell.md) | IoT-/Telemetrie-Modell | Accepted | Operations & Telemetry |
| [ADR-017](../adr/adr-017-governance-pricing-marktdatenquellen.md) | Governance für Pricing-/Marktdatenquellen | Accepted | Pricing & Market Data |
| [ADR-018](../adr/adr-018-qualitaets-labordatenmodell.md) | Qualitäts-/Labordatenmodell | Accepted | Quality Core |
| [ADR-019](../adr/adr-019-sicherheitsmodell-externe-agenten-delegierte-aktionen.md) | Sicherheitsmodell für externe Agenten und delegierte Aktionen | Accepted | Agent Security |
| [ADR-020](../adr/adr-020-cross-domain-referenzmodell-kontrakt-charge-qualitaet-settlement.md) | Cross-Domain-Referenzmodell Kontrakt / Charge / Qualität / Settlement | Accepted | Domain Core |
| [ADR-021](../adr/adr-021-tenant-weite-datenresidenz-und-exportregeln.md) | Tenant-weite Datenresidenz- und Exportregeln | Accepted | Tenant & Governance |
| [ADR-022](../adr/adr-022-regelmodell-reklamation-abzug-ausnahmebehandlung.md) | Regelmodell für Reklamation, Abzug und Ausnahmebehandlung | Accepted | Quality & Exception Handling |
| [ADR-023](../adr/adr-023-governance-rollen-berechtigungsvererbung.md) | Governance für Rollen- und Berechtigungsvererbung | Accepted | Tenant & Governance |
| [ADR-024](../adr/adr-024-datenprodukt-strategie-sustainability-compliance-reporting.md) | Datenprodukt-Strategie für Sustainability- und Compliance-Reporting | Accepted | Data & Analytics |
| [ADR-025](../adr/adr-025-standard-konfliktarme-parallelbearbeitung.md) | Standard für konfliktarme Parallelbearbeitung in Kernprozessen | Accepted | Process Reliability |
| [ADR-026](../adr/adr-026-modell-import-staging-pruefpipelines.md) | Modell für Import-/Staging-/Prüfpipelines | Accepted | Data Intake |

## Themencluster

### Domain Core
- [ADR-003 Canonical Domain Model](../adr/adr-003-canonical-domain-model.md)
- [ADR-020 Cross-Domain-Referenzmodell für Kontrakt, Charge, Qualität und Settlement](../adr/adr-020-cross-domain-referenzmodell-kontrakt-charge-qualitaet-settlement.md)
- [Business Logic Architecture](business-logic-architecture.md)
- [Fundamental Architecture Principles](fundamental-architecture-principles.md)

### Process Core
- [ADR-004 Command-/Action-Layer](../adr/adr-004-command-action-layer.md)
- [ADR-005 Workflow-/Policy-Kern](../adr/adr-005-workflow-policy-kern.md)
- [ADR-009 Workflow-Versionierung und Migration](../adr/adr-009-workflow-versionierung-und-migration.md)
- [ADR-010 Policy-Override-Modell](../adr/adr-010-policy-override-modell.md)
- [Current Processes](current-processes.md)
- [Target Processes](target-processes.md)

### Data & Query
- [ADR-006 Read-Model / Query-Contract-Prinzip](../adr/adr-006-read-model-query-contract-prinzip.md)
- [ADR-008 Eventing-/Outbox-Standard](../adr/adr-008-eventing-outbox-standard.md)
- [ADR-015 Analytics-/Benchmark-Datenproduktmodell](../adr/adr-015-analytics-benchmark-datenproduktmodell.md)
- [ADR-024 Datenprodukt-Strategie für Sustainability- und Compliance-Reporting](../adr/adr-024-datenprodukt-strategie-sustainability-compliance-reporting.md)
- [Module Resolution Architecture](module-resolution-architecture.md)
- [React Lifecycle Architecture](react-lifecycle-architecture.md)

### Pricing & Market Data
- [ADR-017 Governance für Pricing-/Marktdatenquellen](../adr/adr-017-governance-pricing-marktdatenquellen.md)
- [ADR-015 Analytics-/Benchmark-Datenproduktmodell](../adr/adr-015-analytics-benchmark-datenproduktmodell.md)

### Quality Core
- [ADR-018 Qualitäts-/Labordatenmodell](../adr/adr-018-qualitaets-labordatenmodell.md)
- [ADR-022 Regelmodell für Reklamation, Abzug und Ausnahmebehandlung](../adr/adr-022-regelmodell-reklamation-abzug-ausnahmebehandlung.md)
- [ADR-012 Dokument-/Audit-Evidence-Modell](../adr/adr-012-dokument-audit-evidence-modell.md)

### Operations & Telemetry
- [ADR-016 IoT-/Telemetrie-Modell](../adr/adr-016-iot-telemetrie-modell.md)
- [ADR-008 Eventing-/Outbox-Standard](../adr/adr-008-eventing-outbox-standard.md)

### Agent Security
- [ADR-019 Sicherheitsmodell für externe Agenten und delegierte Aktionen](../adr/adr-019-sicherheitsmodell-externe-agenten-delegierte-aktionen.md)
- [ADR-007 Agent-/Tool-Contract-Governance](../adr/adr-007-agent-tool-contract-governance.md)

### Tenant & Governance
- [ADR-021 Tenant-weite Datenresidenz- und Exportregeln](../adr/adr-021-tenant-weite-datenresidenz-und-exportregeln.md)
- [ADR-013 Tenant-/Genossenschaftsmodell](../adr/adr-013-tenant-genossenschaftsmodell.md)
- [ADR-023 Governance für Rollen- und Berechtigungsvererbung](../adr/adr-023-governance-rollen-berechtigungsvererbung.md)

### Process Reliability
- [ADR-025 Standard für konfliktarme Parallelbearbeitung in Kernprozessen](../adr/adr-025-standard-konfliktarme-parallelbearbeitung.md)
- [ADR-006 Read-Model / Query-Contract-Prinzip](../adr/adr-006-read-model-query-contract-prinzip.md)

### Data Intake
- [ADR-026 Modell für Import-/Staging-/Prüfpipelines](../adr/adr-026-modell-import-staging-pruefpipelines.md)
- [ADR-012 Dokument-/Audit-Evidence-Modell](../adr/adr-012-dokument-audit-evidence-modell.md)

### UX & Process UI
- [ADR-011 UI-Maskenstrategie](../adr/adr-011-ui-maskenstrategie.md)
- [Current Processes](current-processes.md)
- [Target Processes](target-processes.md)

### Audit & Document
- [ADR-012 Dokument-/Audit-Evidence-Modell](../adr/adr-012-dokument-audit-evidence-modell.md)
- [DMS Paperless Integration](dms-paperless-integration.md)

### Tenant & Organization
- [ADR-013 Tenant-/Genossenschaftsmodell](../adr/adr-013-tenant-genossenschaftsmodell.md)
- [ADR-010 Policy-Override-Modell](../adr/adr-010-policy-override-modell.md)

### Agent & Integration
- [ADR-007 Agent-/Tool-Contract-Governance](../adr/adr-007-agent-tool-contract-governance.md)
- [ADR-014 Integrationsgrenzen API / EDI / MCP / Partneradapter](../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md)
- [KI Usability Microservices](KI-USABILITY-MICROSERVICES.md)
- [Agrar Event Hook Contracts](agrar-event-hook-contracts.md)
- [DMS Paperless Integration](dms-paperless-integration.md)

### Foundations
- [Fundamental Architecture Principles](fundamental-architecture-principles.md)
- [Context Architecture Revolution](context-architecture-revolution.md)
- [Business Logic Architecture](business-logic-architecture.md)
- [Module Resolution Architecture](module-resolution-architecture.md)
- [TypeScript Generic Architecture](typescript-generic-architecture.md)
- [React Lifecycle Architecture](react-lifecycle-architecture.md)

## Nächste ADR-Kandidaten

Die nächste sinnvolle ADR-Pipeline verschiebt sich jetzt von Grundsatzarchitektur zu tieferer Domänenausprägung:

1. Lifecycle-Modell für Kontraktänderungen, Amendments und Versionen
2. Referenzmodell für Chargen-/Partienverschneidung über Lager, Qualität und Settlement
3. Standards für Explainability von KI- und Policy-Entscheidungen
4. Governance für Simulationsdaten und Sandbox-Isolation
