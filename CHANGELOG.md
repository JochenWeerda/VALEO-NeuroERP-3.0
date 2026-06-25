# Changelog

Alle nennenswerten Änderungen an VALEO NeuroERP werden hier dokumentiert.

Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
die Versionierung an [Semantic Versioning](https://semver.org/lang/de/).

## [Unreleased]

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

## [3.0.0] - 2026-06-25

### Added

- Basisversion VALEO NeuroERP 3.0 (Mehrmandanten-ERP für Agrar/Landhandel).
