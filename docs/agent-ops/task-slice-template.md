# Task Slice Template

```markdown
## Slice: {{SLICE_ID}} - {{TITEL}}

**Owner:**
**Status:** geplant | in arbeit | blocked | review | abgeschlossen
**Ziel:**
**Fachlicher Scope:**
**Dateibesitz:**
**Abnahmekriterien:**
**Tests / Checks:**
**Doku-Updates:**
**Risiken / Blocker:**
**Naechster konkreter Schritt:**
```

## AI-Harness-Pflichtfelder fuer neue Agenten-Slices

Neue oder wesentlich geaenderte Slice-YAMLs muessen zusaetzlich diese Felder enthalten:

```yaml
slice_id: EXAMPLE-001
title: Beispiel-Slice
owner: Codex
status: reserved
created_at: 2026-06-23
coordination: >-
  Abstimmung mit parallelen Agenten und ausgeschlossene Dateien.
goal: >-
  Konkretes Ziel des Slices.
file_ownership:
  - docs/agent-ops/example.md
acceptance:
  - Messbares Abnahmekriterium.
tests:
  - Reproduzierbarer Check oder begruendete Ausnahme.
risks:
  - Bekannter Blocker oder Risiko.
ai_harness:
  fachlicher_vertrag: User Story, Akzeptanzkriterien, Soll-Prozess, Randfaelle.
  architektur_vertrag: ADR-/Statusbezug, erlaubte Module, Schnittstellen.
  daten_vertrag: Schema, Tenant-Scope, Idempotenz, Audit, Versionierung.
  test_vertrag: Unit-, Contract-, Integration-, Playwright- oder Workflow-Test.
  security_vertrag: Auth, Tenant-Isolation, Secrets, PII, Injection, Audit.
  betriebs_vertrag: Healthcheck, Logs, Observability, Rollback, Feature Flag.
  dokumentations_vertrag: Workboard, Doku, QA-Report, Open-Gaps.
external_gates:
  - not_applicable
```

`external_gates` darf `not_applicable` enthalten. In POS, FiBu, Payroll, HR,
DMS, QS, TSE, DATEV, Security oder Datenschutz muss stattdessen ein konkretes
externes oder simuliertes Gate benannt werden.
