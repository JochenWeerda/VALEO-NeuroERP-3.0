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

## Themencluster

### Domain Core
- [ADR-003 Canonical Domain Model](../adr/adr-003-canonical-domain-model.md)
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
- [Module Resolution Architecture](module-resolution-architecture.md)
- [React Lifecycle Architecture](react-lifecycle-architecture.md)

### Agent & Integration
- [ADR-007 Agent-/Tool-Contract-Governance](../adr/adr-007-agent-tool-contract-governance.md)
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

Die nächsten sinnvollen Entscheidungen leiten sich direkt aus dem Zielbild ab:

1. UI-Maskenstrategie: generische Builder vs. fachliche Spezialmasken
2. Document/Audit-Evidence-Modell für GoBD-, DMS- und Freigabepfade
3. Tenant-/Genossenschaftsmodell für Verbundstrukturen
4. Integrationsgrenzen API vs. EDI vs. MCP vs. Partneradapter
5. Analytics-/Benchmark-Datenproduktmodell
