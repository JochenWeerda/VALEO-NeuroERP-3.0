---
title: Architecture Impact Note L3-DOCRET-INBOX-004
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-DOCRET-INBOX-004

- **Domains:** DMS/Compliance, Finance, CRM
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-058](../../adr/adr-058-document-return-on-docflow.md)
- **Containeraenderung:** keine; vorhandener API-/Frontend-/DMS-Rand
- **Datenmodell:** additive Ruecklauffaelle und append-only Audit in
  `domain_docflow`
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Externe Gates

Provider-Zustellnachweise, produktiver Storage-Preview-Adapter und Pilotdaten
werden mandantenspezifisch angebunden. Die repo-seitigen Status-, Vorschau- und
Deep-Link-Vertraege sind davon unabhaengig testbar.

## Checks

Ergebnis 2026-08-21: 15 Docflow-Backendtests, zwei fokussierte Frontendtests,
TypeScript und Ruff sind gruen. Die Maske ist `generatorReady=true`.
OpenAPI, Route-Inventar, Architekturindex, ADR-Navigation und Agent-Handbuch
wurden regeneriert; der gemeinsame Architekturdrift ist gruen. Der Alembic-
Nachfolger `document_control_20260821` baut linear auf
`docflow_returns_20260821` auf.
