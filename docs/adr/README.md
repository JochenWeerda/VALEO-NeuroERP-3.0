# ADR Index

**Zweck:** `Referenzdokument` fuer den ADR-Bestand. Nicht der operative Lieferstand.

## Einordnung

Diese Datei ist eine `abgeleitete Sicht` auf die Architecture Decision Records. Operative Architektur- und Delivery-Sichten liegen in [Architecture Index](../architecture/index.md) und [Process Kernel Status](../architecture/process-kernel/STATUS.md).

Die MkDocs-Sidebar listet alle ADRs einzeln (Generator: `python scripts/generate_adr_nav.py`).

- [ADR-001 FiBu Domain Reuse vs Rewrite](adr-001-fibu-domain-reuse-vs-rewrite.md)
- [ADR-002 FiBu Frontend API Layer](adr-002-fibu-frontend-api-layer.md)
- [ADR-003 Canonical Domain Model](adr-003-canonical-domain-model.md)
- [ADR-004 Command-/Action-Layer](adr-004-command-action-layer.md)
- [ADR-005 Workflow-/Policy-Kern](adr-005-workflow-policy-kern.md)
- [ADR-006 Read-Model / Query-Contract-Prinzip](adr-006-read-model-query-contract-prinzip.md)
- [ADR-007 Agent-/Tool-Contract-Governance](adr-007-agent-tool-contract-governance.md)
- [ADR-008 Eventing-/Outbox-Standard](adr-008-eventing-outbox-standard.md)
- [ADR-009 Workflow-Versionierung und Migration](adr-009-workflow-versionierung-und-migration.md)
- [ADR-010 Policy-Override-Modell](adr-010-policy-override-modell.md)
- [ADR-011 UI-Maskenstrategie](adr-011-ui-maskenstrategie.md)
- [ADR-012 Dokument-/Audit-Evidence-Modell](adr-012-dokument-audit-evidence-modell.md)
- [ADR-013 Tenant-/Genossenschaftsmodell](adr-013-tenant-genossenschaftsmodell.md)
- [ADR-014 Integrationsgrenzen API / EDI / MCP / Partneradapter](adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md)
- [ADR-015 Analytics-/Benchmark-Datenproduktmodell](adr-015-analytics-benchmark-datenproduktmodell.md)
- [ADR-016 IoT-/Telemetrie-Modell](adr-016-iot-telemetrie-modell.md)
- [ADR-017 Governance für Pricing-/Marktdatenquellen](adr-017-governance-pricing-marktdatenquellen.md)
- [ADR-018 Qualitäts-/Labordatenmodell](adr-018-qualitaets-labordatenmodell.md)
- [ADR-019 Sicherheitsmodell für externe Agenten und delegierte Aktionen](adr-019-sicherheitsmodell-externe-agenten-delegierte-aktionen.md)
- [ADR-020 Cross-Domain-Referenzmodell für Kontrakt, Charge, Qualität und Settlement](adr-020-cross-domain-referenzmodell-kontrakt-charge-qualitaet-settlement.md)
- [ADR-021 Tenant-weite Datenresidenz- und Exportregeln](adr-021-tenant-weite-datenresidenz-und-exportregeln.md)
- [ADR-022 Regelmodell für Reklamation, Abzug und Ausnahmebehandlung](adr-022-regelmodell-reklamation-abzug-ausnahmebehandlung.md)
- [ADR-023 Governance für Rollen- und Berechtigungsvererbung](adr-023-governance-rollen-berechtigungsvererbung.md)
- [ADR-024 Datenprodukt-Strategie für Sustainability- und Compliance-Reporting](adr-024-datenprodukt-strategie-sustainability-compliance-reporting.md)
- [ADR-025 Standard für konfliktarme Parallelbearbeitung in Kernprozessen](adr-025-standard-konfliktarme-parallelbearbeitung.md)
- [ADR-026 Modell für Import-/Staging-/Prüfpipelines](adr-026-modell-import-staging-pruefpipelines.md)
- [ADR-027 Process-Kernel Event-Namenskonvention](adr-027-process-kernel-event-namenskonvention.md)
- [ADR-028 Workflow Access Control und Delegation](adr-028-workflow-access-control-und-delegation.md)
- [ADR-029 Process-Betrieb — Timeout, Batch, Archiv und Metriken](adr-029-process-betrieb-timeout-batch-archiv-metriken.md)
- [ADR-031 Standardmaske vs Spezialmaske](adr-031-standardmaske-vs-spezialmaske.md)
- [ADR-032 Auth-Enforcement über Router-Level Global Dependency](adr-032-auth-enforcement-router-global-dependency.md)
- [ADR-033 Rollback-Strategie — Zentral in get_db()](adr-033-rollback-strategie-get-db.md)
- [ADR-034 Tenant-Isolation-Klassifizierungssystem](adr-034-tenant-isolation-klassifizierungssystem.md)
- [ADR-035 Kein interaktiver Workflow-Designer](adr-035-kein-workflow-designer.md)
- [ADR-036 Architektur-Dokumentations-Stack](adr-036-architecture-documentation-stack.md)
- [ADR-037 Structurizr C4 Source of Truth](adr-037-structurizr-c4-source-of-truth.md)
- [ADR-056 Herstellerneutraler ERP-Gewohnheitsvertrag](adr-056-vendor-neutral-erp-habit-contract.md)
- [ADR-CRM-001](ADR-CRM-001.md)

## Hinweis zu Doppelnummern

Einige ADRs teilen sich historische Nummern (parallele Entscheidungsstränge):

| Nummer | Datei A | Datei B |
|---|---|---|
| ADR-014 | [Integrationsgrenzen](adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md) | [Service-Layer-Pattern](adr-014-service-layer-pattern.md) |
| ADR-015 | [Analytics-Datenprodukt](adr-015-analytics-benchmark-datenproduktmodell.md) | [Auth-Enforcement-Strategie](adr-015-auth-enforcement-strategie.md) |
| ADR-016 | [IoT/Telemetrie](adr-016-iot-telemetrie-modell.md) | [Pagination-Standard](adr-016-pagination-standard.md) |
| ADR-017 | [Pricing-Marktdaten](adr-017-governance-pricing-marktdatenquellen.md) | [Error-Response-Format](adr-017-error-response-format.md) |

ADR-030 ist **nicht vergeben** (Lücke in der Nummerierung).

## Referenzen

- [Architecture Index](../architecture/index.md)
- [Process Kernel Status](../architecture/process-kernel/STATUS.md)
