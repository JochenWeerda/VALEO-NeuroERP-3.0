---
title: Release Notes
description: Änderungsprotokoll und Release-History für VALEO NeuroERP 3.0.
type: reference
audience: [alle]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-29
version: 3.1.0
---

# Release Notes — VALEO NeuroERP 3.0

> Manuell gepflegt · Stand: 2026-06-29

## Version 3.1.0 — 2026-06-29 — Universal Mask Runtime & AgentMaskContract

### Added — Benutzeroberfläche

- **CRM Kundenstamm 360°-Cockpit** (`/crm/kunden/:id`): neue Tabs (Stammdaten,
  Kontakte, Aufträge, Aktivitäten, Dokumente), Kennzahlen-Leiste (Umsatz 12M,
  offene Posten, Aktivitäten 90T, Kreditstatus), Workflow-Panel mit farbiger
  Statusanzeige und Sperrgründen.
- **Sortieren in Tabellen:** Klick auf Spaltenheader sortiert auf- oder absteigend.
  Pfeile zeigen die aktive Sortierrichtung. Nur freigegebene Spalten sind sortierbar.
- **Filtern in Tabellen:** Filter-Chips für vordefinierte Spalten (Status, Typ u. a.),
  Freitextsuche und Entfernen einzelner Filter per ×.
- **Sticky Submit Bar:** beim Bearbeiten von Stammdaten erscheint eine klebrige
  Fußleiste mit Speichern/Zurücksetzen-Buttons; Speichern ist solange deaktiviert
  wie Pflichtfelder fehlen oder ein Speichervorgang läuft.
- **Workflow-Panel:** farbiges Statusfeld zeigt Prozesszustand, nächste erlaubte
  Aktionen und Klärungsbedarf (grün/gelb/rot je nach Eskalationsstufe).
- **Universal Mask Rollout Waves 42–51:** 10 weitere Domänen-Piloten (Lager-Eingang,
  Finance-Beleg, Einkauf-Bestellung, CRM-Opportunity, Sales-Lieferschein u. a.)
  sind über `/mask-rollout/{screenId}/{entityId}` erreichbar (Feature-Flag
  `VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS=true`).

### Added — Technisch / Agenten

- **AgentMaskContract** (`GET /api/v1/masks/{id}/agent-contract`): maschinenlesbarer
  Kontrakt je Maske mit lesbaren/editierbaren/sensiblen Feldern, Action-Policies,
  Validierungsregeln und Audit-Anforderungen. Wird deterministisch aus der
  ScreenDefinition abgeleitet.
- **Generator-Readiness-Gates** (`GET /api/v1/masks/{id}/readiness`): 6-Gate-Report
  (Schema, Sort-Whitelist, Filterbare Spalten, AgentContract, DataSources,
  Non-Temporary) zeigt ob eine Maske vollständig native-fähig ist.
- **ActionRuntime:** Aktionen unterstützen jetzt `dryRun`, `validate` und `propose`
  als Ausführungsmodi — AI-Agenten können Vorschläge generieren ohne Seiteneffekte.
- **Strukturierte FilterPlan-API:** Agenten können Tabellendaten strukturiert filtern
  (8 Operatoren: eq/neq/contains/lt/lte/gt/gte/in/between) via JSON-Parameter.

### Changed

- CRM Kundenstamm-Pilot wechselt automatisch auf nativen Runtime-Pfad wenn die
  ScreenDefinition `adapter.temporary: false` trägt (bisherige Legacy-Pfade bleiben
  vollständig erhalten).

## Version Unreleased

### Added
- Docs-as-Code-Fundament: MkDocs + Material, Diátaxis-Taxonomie, Frontmatter-Standard,
  CI-Build-Gate (`DOC-FOUNDATION-001`).
- Schnittstellenhandbuch: OpenAPI-Generator, MCP-Tool-Referenz, Event-Katalog,
  Swagger-UI-Einbettung (`DOC-INTERFACES-001`).
- Benutzerhandbuch: aufgabenorientierte How-tos, Glossar, In-App-Hilfe-Konzept
  (`DOC-USER-MANUAL-001`).
- Administrations- & Betriebshandbuch (`DOC-ADMIN-OPS-001`).
- Agent-Dokumentation: Capability-/Tool-Katalog, Guardrails, ai_harness-Verträge
  (`DOC-AGENT-CATALOG-001`).
- Doku-Governance: CODEOWNERS, Staleness-Check, mike-Release-Workflow, dieses
  Changelog (`DOC-GOVERNANCE-001`).
### Changed
- Multi-User-Performance: HTTP-Middleware auf reine ASGI umgestellt, Logging
  entschlackt (`PERF-MULTIUSER-001`).
- Doku-Checks erlauben optionalen YAML-Frontmatter-Block vor der H1.

## Version 3.0.0 — 2026-06-25

### Added
- Basisversion VALEO NeuroERP 3.0 (Mehrmandanten-ERP für Agrar/Landhandel).

## Abgeschlossene Slices (2026 · 16 Stück)

| Slice | Titel | Datum |
|---|---|---|
| `COVERAGE-RATCHET-002` | Coverage-Ratchet Schwellwert-Erhöhung | 2026-06-26 |
| `DOC-ASYNCAPI-001` | AsyncAPI 2.6 Event-Katalog | 2026-06-26 |
| `DOC-DRIFT-DASHBOARD-002` | Doku-Code-Drift-Dashboard in MkDocs | 2026-06-26 |
| `DOC-DRIFT-GATE-002` | Doku-Code-Drift-Gate in CI | 2026-06-26 |
| `DOC-INAPP-HELP-002` | In-App-Hilfe Route → Dokumentation Mapping | 2026-06-26 |
| `DOC-OPENAPI-CI-001` | OpenAPI-Drift-Gate in CI | 2026-06-26 |
| `DOC-RELEASE-NOTES-001` | Release-Notes-Generator aus CHANGELOG + Slices | 2026-06-26 |
| `DOCS-CODE-SYNC-002` | Docs-Code-Sync Mapping-Härtung | 2026-06-26 |
| `EXTERNAL-MOCK-WORKFLOW-001` | Playwright External-Mock-Workflow Verträge | 2026-06-26 |
| `INTEGRATION-EVIDENCE-BOARD-001` | Qualitäts-Cockpit: Backend-API + Frontend | 2026-06-26 |
| `MCP-ERP-TOOLS-002` | MCP-Tools Erweiterung: Agrar, Lager, Einkauf, Agent | 2026-06-26 |
| `OPERATOR-AGENT-002` | Operator-Agent DB-Persistenz für Proposals | 2026-06-26 |
| `RELEASE-EVIDENCE-GATE-001` | Release-Evidence Freigabe-Aggregator | 2026-06-26 |
| `SEMANTIC-ACTION-MATRIX-002` | Semantische Action-Matrices YAML + Report | 2026-06-26 |
| `SEMANTIC-E2E-STRICT-001` | Playwright @critical Tags für Kern-Pfade | 2026-06-26 |
| `TRACEABILITY-MATRIX-001` | Slice↔Test↔Doku Traceability-Matrix | 2026-06-26 |

*Generiert 2026-06-26 · 111 Slices · Slice: DOC-RELEASE-NOTES-001*
