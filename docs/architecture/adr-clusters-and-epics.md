# ADR Clusters and Epics

## Zweck
Dieses Dokument verdichtet die vorhandenen ADRs in umsetzbare Themenpakete. Es beantwortet zwei Fragen:

1. Welche ADRs bilden zusammen einen Architektur- oder Produktcluster?
2. Welche Epics und konkreten Arbeitspakete lassen sich daraus ableiten?

## 1. Themenpakete

### Paket A: Domain and Process Core

ADRs:
- [ADR-003 Canonical Domain Model](../adr/adr-003-canonical-domain-model.md)
- [ADR-004 Command-/Action-Layer](../adr/adr-004-command-action-layer.md)
- [ADR-005 Workflow-/Policy-Kern](../adr/adr-005-workflow-policy-kern.md)
- [ADR-009 Workflow-Versionierung und Migration](../adr/adr-009-workflow-versionierung-und-migration.md)
- [ADR-010 Policy-Override-Modell](../adr/adr-010-policy-override-modell.md)
- [ADR-020 Cross-Domain-Referenzmodell für Kontrakt, Charge, Qualität und Settlement](../adr/adr-020-cross-domain-referenzmodell-kontrakt-charge-qualitaet-settlement.md)
- [ADR-022 Regelmodell für Reklamation, Abzug und Ausnahmebehandlung](../adr/adr-022-regelmodell-reklamation-abzug-ausnahmebehandlung.md)

Ziel:
- fachliche Wahrheit, Prozesssteuerung und Ausnahmebehandlung entlang der Kernprozesskette vereinheitlichen

### Paket B: Data, Events and Analytics

ADRs:
- [ADR-006 Read-Model / Query-Contract-Prinzip](../adr/adr-006-read-model-query-contract-prinzip.md)
- [ADR-008 Eventing-/Outbox-Standard](../adr/adr-008-eventing-outbox-standard.md)
- [ADR-015 Analytics-/Benchmark-Datenproduktmodell](../adr/adr-015-analytics-benchmark-datenproduktmodell.md)
- [ADR-024 Datenprodukt-Strategie für Sustainability- und Compliance-Reporting](../adr/adr-024-datenprodukt-strategie-sustainability-compliance-reporting.md)
- [ADR-025 Standard für konfliktarme Parallelbearbeitung in Kernprozessen](../adr/adr-025-standard-konfliktarme-parallelbearbeitung.md)
- [ADR-026 Modell für Import-/Staging-/Prüfpipelines](../adr/adr-026-modell-import-staging-pruefpipelines.md)

Ziel:
- Write-, Read-, Reporting-, Event- und Intake-Pfade sauber trennen und operationalisieren

### Paket C: Tenant, Security and Integration

ADRs:
- [ADR-007 Agent-/Tool-Contract-Governance](../adr/adr-007-agent-tool-contract-governance.md)
- [ADR-013 Tenant-/Genossenschaftsmodell](../adr/adr-013-tenant-genossenschaftsmodell.md)
- [ADR-014 Integrationsgrenzen API / EDI / MCP / Partneradapter](../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md)
- [ADR-019 Sicherheitsmodell für externe Agenten und delegierte Aktionen](../adr/adr-019-sicherheitsmodell-externe-agenten-delegierte-aktionen.md)
- [ADR-021 Tenant-weite Datenresidenz- und Exportregeln](../adr/adr-021-tenant-weite-datenresidenz-und-exportregeln.md)
- [ADR-023 Governance für Rollen- und Berechtigungsvererbung](../adr/adr-023-governance-rollen-berechtigungsvererbung.md)

Ziel:
- Verbundstruktur, Identität, Delegation, Export und Integrationskanäle kontrollierbar machen

### Paket D: Specialized Process Domains

ADRs:
- [ADR-011 UI-Maskenstrategie](../adr/adr-011-ui-maskenstrategie.md)
- [ADR-012 Dokument-/Audit-Evidence-Modell](../adr/adr-012-dokument-audit-evidence-modell.md)
- [ADR-016 IoT-/Telemetrie-Modell](../adr/adr-016-iot-telemetrie-modell.md)
- [ADR-017 Governance für Pricing-/Marktdatenquellen](../adr/adr-017-governance-pricing-marktdatenquellen.md)
- [ADR-018 Qualitäts-/Labordatenmodell](../adr/adr-018-qualitaets-labordatenmodell.md)

Ziel:
- hochspezifische Fachdomänen an denselben Architekturrahmen anbinden

## 2. Überschneidungen

### Hohe Überschneidung

`ADR-004`, `ADR-005`, `ADR-009`, `ADR-010`
- gemeinsamer Kern: Commands, Workflows, Policies, Freigaben
- Risiko: doppelte Semantik für Übergänge, Freigaben und Overrides
- Empfehlung: gemeinsame Referenzmodelle für `command`, `transition`, `decision`, `override`

`ADR-006`, `ADR-008`, `ADR-015`, `ADR-024`, `ADR-026`
- gemeinsamer Kern: Datenflüsse, Ereignisse, Read-Models, Reporting und Intake
- Risiko: getrennte Definitionen für Quelle, Zustand, Historisierung und Ownership
- Empfehlung: ein gemeinsamer Datenfluss-Stack mit klaren Ebenen `ingest -> validate -> command -> event -> read model -> reporting product`

`ADR-013`, `ADR-019`, `ADR-021`, `ADR-023`
- gemeinsamer Kern: Tenant, Rollen, Delegation, Export, Governance
- Risiko: Sicherheits- und Tenantregeln werden doppelt oder widersprüchlich modelliert
- Empfehlung: ein gemeinsames Governance-Modell für `scope`, `inheritance`, `delegation`, `exportability`

`ADR-012`, `ADR-018`, `ADR-022`
- gemeinsamer Kern: prüfungsrelevante Evidenz, Qualität, Ausnahmeentscheidung
- Risiko: Sonderpfade für Dokumente, Labor und Reklamation
- Empfehlung: gemeinsamer Referenzraum für `evidence`, `quality finding`, `exception decision`

### Mittlere Überschneidung

`ADR-011` mit fast allen Prozess-ADRs
- UI-Maskenstrategie greift in Commands, Workflows, Read-Models und Konfliktbehandlung hinein
- Empfehlung: UI-Klassen früh pro Epic festlegen, nicht am Ende

`ADR-016`, `ADR-017`, `ADR-018`
- Spezialisierte Prozessdomänen teilen Datenqualitäts-, Zeitbezug- und Auditprobleme
- Empfehlung: gemeinsame Standards für Herkunft, Zeitstempel, Klassifikation und Explainability

## 3. Abgeleitete Epics

### Epic 1: Process Kernel Platform

ADRs:
- 003, 004, 005, 009, 010, 020, 022

Ziel:
- durchgängiger Prozesskern für Kontrakt, Annahme, Qualität, Settlement und Ausnahmebehandlung

Arbeitspakete:
1. Command-Katalog für Kernprozesse definieren
2. Workflow-Definitionen versionierbar machen
3. Policy-Override- und Explainability-Modell implementieren
4. Cross-Domain-Referenzen Kontrakt/Charge/Qualität/Settlement formal modellieren
5. Ausnahme-, Abzugs- und Reklamationsregeln in den Policy-/Workflow-Kern ziehen

Backlog-Bezug:
- 001, 003, 004, 009, 011, 014, 019

### Epic 2: Read, Event and Data Product Platform

ADRs:
- 006, 008, 015, 024, 025, 026

Ziel:
- stabile Query-, Event-, Reporting- und Importpfade als gemeinsame Plattform

Arbeitspakete:
1. Query-Contracts für Kerncockpits standardisieren
2. Outbox- und Event-Namenskonvention einführen
3. Read-Models und Reporting-Datenprodukte trennen
4. Compliance-/Sustainability-Reporting als versionierte Datenprodukte modellieren
5. Standard für konfliktarme Parallelbearbeitung in Kernobjekten umsetzen
6. Import-/Staging-/Prüfpipelines für CSV, EDI und OCR vereinheitlichen

Backlog-Bezug:
- 018, 031, 033, 035, 036, 039, 040, 045, 046, 047

### Epic 3: Tenant, Security and Integration Governance

ADRs:
- 007, 013, 014, 019, 021, 023

Ziel:
- tenant-fähige Verbundstruktur, saubere Delegation und kontrollierte Integrationskanäle

Arbeitspakete:
1. Verbund- und Tenant-Modell konkretisieren
2. Rollen- und Berechtigungsvererbung definieren
3. Agenten- und Delegationssicherheitsmodell implementieren
4. API-, EDI-, MCP- und Partneradapter-Grenzen durchsetzen
5. Export- und Datenresidenzregeln tenant-weit modellieren

Backlog-Bezug:
- 009, 015, 016, 017, 043, 048, 049

### Epic 4: Specialized Domain Enablers

ADRs:
- 011, 012, 016, 017, 018

Ziel:
- Spezialdomänen auf den Plattformkern aufsetzen, ohne neue Schattenarchitektur aufzubauen

Arbeitspakete:
1. UI-Maskenklassen A/B/C pro Kernseite zuordnen
2. Dokument-/Audit-Evidence-Modell auf DMS, OCR und Freigaben ziehen
3. IoT-/Telemetriepfade für Waage, Silo und Lager modellieren
4. Pricing-/Marktdatenquellen klassifizieren und auditierbar machen
5. Qualitäts-/Labordatenmodell an Charge, Preis und Freigabe anbinden

Backlog-Bezug:
- 002, 006, 012, 021, 024, 041, 045

## 4. Empfohlene Reihenfolge

1. Epic 1 `Process Kernel Platform`
2. Epic 2 `Read, Event and Data Product Platform`
3. Epic 3 `Tenant, Security and Integration Governance`
4. Epic 4 `Specialized Domain Enablers`

## 5. Ergebnis

Die ADR-Landschaft ist jetzt nicht mehr nur dokumentiert, sondern in umsetzbare Pakete überführt:
- Architekturcluster
- Überschneidungsanalyse
- konkrete Epics
- Backlog-Anschluss an die bestehende Roadmap
