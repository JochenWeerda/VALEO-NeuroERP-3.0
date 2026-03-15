# Process Kernel Status

## Gesamtstatus

- Stand: `2026-03-15`
- Status: `Waves 1 bis 41 abgeschlossen`
- Gesamtsuite: `2120 Tests gruen, 0 Fehler, 5 skipped, 1 xfailed`
- Letzte abgeschlossene Waves:
  - `Wave 37`: DMS + OCR-Extraktion + Agenten-Integration (Gap 045, Gap 048)
  - `Wave 38`: Nachhaltigkeit/CO2-Reporting + Branchenbenchmarking (Gap 046, Gap 047)
  - `Wave 39`: Command-Surfacing-Contracts + Prozess-Benachrichtigungs-Contracts
  - `Wave 40`: Workflow-Versionierungs-Contracts + Canonical Process Audit Trail (PKP-02, PKP-03)
  - `Wave 41`: Process Capacity Contracts + Event Replay Contracts

## Wave-Uebersicht

| Wave | Status | Tests | Referenz |
|------|--------|-------|----------|
| Wave 1 | abgeschlossen | 35 | `wave-1/STATUS.md` |
| Wave 2 | abgeschlossen | 37 | `wave-2/STATUS.md` |
| Wave 3 | abgeschlossen | 30 | `wave-3/STATUS.md` |
| Wave 4 | abgeschlossen | 49 | `wave-4/STATUS.md` |
| Wave 5 | abgeschlossen | 41 | `wave-5/STATUS.md` |
| Wave 6 | abgeschlossen | 44 | `wave-6/STATUS.md` |
| Wave 7 | abgeschlossen | 56 | `wave-7/STATUS.md` |
| Wave 8 | abgeschlossen | 69 | `wave-8/STATUS.md` |
| Wave 9 | abgeschlossen | 50 | `wave-9/STATUS.md` |
| Wave 10 | abgeschlossen | 11 | `wave-10/STATUS.md` |
| Wave 11 | abgeschlossen | 30 | `wave-11/STATUS.md` |
| Wave 12 | abgeschlossen | 22 | `wave-12/STATUS.md` |
| Wave 13 | abgeschlossen | 27 | `wave-13/STATUS.md` |
| Wave 14 | abgeschlossen | 31 | `wave-14/STATUS.md` |
| Wave 15 | abgeschlossen | 34 | `wave-15/STATUS.md` |
| Wave 16 | abgeschlossen | 31 | `wave-16/STATUS.md` |
| Wave 17 | abgeschlossen | 17 | `wave-17/STATUS.md` |
| Wave 18 | abgeschlossen | 55 | `wave-18/STATUS.md` |
| Wave 19 | abgeschlossen | 62 | `wave-19/STATUS.md` |
| Wave 20 | abgeschlossen | 43 | `wave-20/STATUS.md` |
| Wave 21 | abgeschlossen | 37 | `wave-21/STATUS.md` |
| Wave 22 | abgeschlossen | 8 | `wave-22/STATUS.md` |
| Wave 23 | abgeschlossen | 46 | `wave-23/STATUS.md` |
| Wave 24 | abgeschlossen | 41 | `wave-24/STATUS.md` |
| Wave 25 | abgeschlossen | 10 | `wave-25/STATUS.md` |
| Wave 26 | abgeschlossen | 37 | `wave-26/STATUS.md` |
| Wave 27 | abgeschlossen | 21 | `wave-27/STATUS.md` |
| Wave 28 | abgeschlossen | 47 | `wave-28/STATUS.md` |
| Wave 29 | abgeschlossen | 52 | `wave-29/STATUS.md` |
| Wave 30 | abgeschlossen | 44 | `wave-30/STATUS.md` |
| Wave 31 | abgeschlossen | 105 | `wave-31/STATUS.md` |
| Wave 32 | abgeschlossen | 47 | `wave-32/STATUS.md` |
| Wave 33 | abgeschlossen | 59 | `wave-33/STATUS.md` |
| Wave 34 | abgeschlossen | 55 | `wave-34/STATUS.md` |
| Wave 35 | abgeschlossen | 54 | `wave-35/STATUS.md` |
| Wave 36 | abgeschlossen | 60 | `wave-36/STATUS.md` |
| Wave 37 | abgeschlossen | 60 | `wave-37/STATUS.md` |
| Wave 38 | abgeschlossen | 60 | `wave-38/STATUS.md` |
| Wave 39 | abgeschlossen | 60 | `wave-39/STATUS.md` |
| Wave 40 | abgeschlossen | 60 | `wave-40/STATUS.md` |
| Wave 41 | abgeschlossen | 82 | `wave-41/STATUS.md` |

## Aktuell relevante Lieferungen

### Wave 21

- Referenz: `wave-21/STATUS.md`
- Scope:
  - `app/core/price_formula_engine.py`
  - `app/core/settlement_journal_bridge.py`
  - `app/core/settlement_e2e_reference.py`
  - `app/api/v1/endpoints/process_kernel_api.py`
- Ergebnis:
  - Preislogik fuer Fix-, Formel- und Terminmarktpreise ist vereinheitlicht
  - Settlement kann in eine GoBD-faehige Journal-Vorschau ueberfuehrt werden
  - E2E-Referenzkette reicht bis zum Journal-Entry

### Wave 22

- Referenz: `wave-22/STATUS.md`
- Scope:
  - `packages/frontend-web/src/features/ki-usability/context/ActionDispatchContext.tsx`
  - `packages/frontend-web/src/components/navigation/CommandPalette.tsx`
  - `packages/frontend-web/src/components/navigation/command-palette-model.ts`
  - `packages/frontend-web/src/lib/api/mask-registry.ts`
  - `packages/frontend-web/src/components/navigation/AppShell.tsx`
- Ergebnis:
  - Command Palette nutzt denselben Dispatch-Contract wie Toolbar, Shortcut und Voice
  - Prozessmasken aus `/api/v1/ui/mask-registry` werden in der Palette surfacet
  - Navigation-Wiring erkennt auch Verzeichnis-Module mit `index.tsx` korrekt

### Wave 25

- Referenz: `wave-25/STATUS.md`
- Scope:
  - `app/core/ki_action_registry.py`
  - `app/api/v1/endpoints/ki_usability.py`
  - `packages/frontend-web/src/features/ki-usability/toolbar-actions.ts`
  - `packages/frontend-web/src/components/patterns/OverviewPage.tsx`
  - `packages/frontend-web/src/components/patterns/ObjectPage.tsx`
  - `packages/frontend-web/src/components/patterns/ListReport.tsx`
  - `packages/frontend-web/src/components/patterns/Wizard.tsx`
- Ergebnis:
  - Quick Actions werden kontextsensitiv nach Maske, Domain und Global-Fallback aufgeloest
  - Toolbar-Primary/Overflow, Palette und Voice teilen sich denselben Action-Contract
  - Pattern-Komponenten nutzen denselben Mapper statt lokaler Button-Sonderpfade

### Wave 27

- Referenz: `wave-27/STATUS.md`
- Scope:
  - `packages/frontend-web/src/features/role-density/role-density.ts`
  - `packages/frontend-web/src/components/navigation/PageToolbar.tsx`
  - `packages/frontend-web/src/components/patterns/OverviewPage.tsx`
  - `packages/frontend-web/src/components/patterns/ObjectPage.tsx`
  - `packages/frontend-web/src/components/patterns/ListReport.tsx`
  - `packages/frontend-web/src/components/patterns/Wizard.tsx`
  - `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx`
  - `app/core/ui_density_manifest.py`
  - `app/api/v1/endpoints/command_catalog.py`
- Ergebnis:
  - Rollen werden auf fokussierte, standardisierte oder verdichtete Informationsdichte aufgeloest
  - Tenant-, Domain-, Action- und Approval-Kontext duerfen die Dichte kontrolliert anheben
  - Produktive Backend-Command- sowie Policy-/Approval-Contracts speisen ueber `ui-density-manifest` das Mindestniveau fuer die UI-Dichte
  - Toolbar, Listen-/Detail-Pattern, Wizard sowie AP-, Closing-, USTVA-, Zahlungslauf-, Lastschrift-, Settlement- und kompakte Listen-/Badge-Explainability nutzen denselben Dichte-Contract
  - Sichtbare Informationsmenge wird konsistent nach Rolle und Prozesskontext reduziert oder erweitert statt pro Seite separat

### PKP-06 Frontend Explainability

- Scope:
  - `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx`
  - `packages/frontend-web/src/policy/decision-view.ts`
- Ergebnis:
  - Explainability-Rendering ist zentralisiert
  - Prozessmasken nutzen denselben UI-Block statt Inline-Duplikate

## Stabiler Kernbestand

### Process-Kernel-Core

- `app/core/workflow_runtime.py`
- `app/core/projection_consumer.py`
- `app/core/process_sla.py`
- `app/core/operational_governance.py`
- `app/core/finance_followup.py`
- `app/core/runtime_operations.py`

### Process- und Command-Contracts

- `app/core/process_commands.py`
- `app/core/business_commands.py`
- `app/core/command_dispatcher.py`
- `app/core/agent_command_manifest.py`
- `app/core/action_execution.py`
- `app/core/action_idempotency.py`

### Wave-18 Prozessfundament

- `app/core/canonical_process_definitions.py`
- `app/core/workflow_versioning.py`
- `app/core/process_audit_contracts.py`
- `app/core/settlement_compatibility.py`

### Wave-21 Settlement-Fortsetzung

- `app/core/price_formula_engine.py`
- `app/core/settlement_journal_bridge.py`
- `app/core/settlement_e2e_reference.py`

### Wave-23 Nebenkosten + Intrastat

- `app/core/nebenkosten_engine.py`
- `app/core/intrastat_model.py`

### Wave-24 Prozessvarianten + Kampagnen

- `app/core/tenant_prozess_variante.py`
- `app/core/kampagnen_vorlage.py`

### Wave-26 Observability-Fundament

- `app/core/trocknungs_abrechnung.py`
- `app/core/workflow_migrations_guard.py`

### Wave-28 SLA + OTel

- `app/core/sla_eskalation_engine.py`
- `app/core/otel_span_contracts.py`

### Wave-29 Policy-as-Code + Query-Contracts

- `app/core/policy_code_engine.py`
- `app/core/query_contracts.py`

### Wave-30 Human-Approval + SLO/SLI

- `app/core/human_approval_gate.py`
- `app/core/slo_definitions.py`

### Wave-31 MCP Tool Contracts + Datenqualitaet

- `app/core/mcp_tool_contracts.py`
- `app/core/data_quality_rules.py` (Wave-31-Contract-Schicht)

### Wave-32 Dashboard Snapshots + Query-Fallbacks

- `app/core/dashboard_snapshots.py`
- `app/core/query_fallback_contracts.py`

### Wave-33 Bulk-Operationen + Background-Jobs

- `app/core/bulk_operations.py`
- `app/core/background_jobs.py`

### Wave-34 Tenant-Rate-Limits + Security-Hardening

- `app/core/tenant_rate_limits.py`
- `app/core/security_hardening_contracts.py`

### Wave-35 Inline-Validierung + Error-Guidance

- `app/core/inline_validation_contracts.py`
- `app/core/error_guidance_contracts.py`

### Frontend-Power-User-Schicht

- `packages/frontend-web/src/features/ki-usability/context/ActionDispatchContext.tsx`
- `packages/frontend-web/src/components/navigation/CommandPalette.tsx`
- `packages/frontend-web/src/components/navigation/command-palette-model.ts`
- `packages/frontend-web/src/lib/api/mask-registry.ts`
- `app/core/ki_action_registry.py`
- `app/api/v1/endpoints/ki_usability.py`
- `packages/frontend-web/src/features/ki-usability/toolbar-actions.ts`
- `packages/frontend-web/src/features/role-density/role-density.ts`
- `packages/frontend-web/src/lib/api/ui-density-manifest.ts`
- `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx`
- `app/core/ui_density_manifest.py`

## Architekturregeln

1. `schema_version` bestehender Contracts nicht aendern.
2. `app/core/` importiert keine API-/Endpoint-Module.
3. Endpoints importieren keine anderen Endpoint-Module direkt.
4. `app/api/v1/api.py` nur additiv erweitern; bestehende Router-Registrierung nicht rueckbauen.
5. Neue Kernlogik in neue oder bestehende Core-Module legen, nicht in Route-Helper.
6. Tests der abgeschlossenen Waves 1 bis 4 sind Abnahme-Contracts und werden nicht angepasst.
7. DB-Tests mit Schreibvorgaengen nutzen Savepoint-Isolation analog `tests/test_position_service.py`.
8. Gateway-Registrierungen in Tests nur per `monkeypatch.setattr(...)`, nicht per globalem `register_*()`.

## Verifikation

### Letzter Vollbeleg

```bash
pytest -q --no-cov
# Ergebnis: 1688 passed, 5 skipped, 1 xfailed (2026-03-15, nach Wave 35)
```

### Zusaetzliche aktuelle Belege

```bash
pytest tests/test_process_kernel_wave21_price_journal.py -q --no-cov
# Ergebnis: 37 passed

npm run test:run -- src/__tests__/components/navigation/command-palette-model.test.ts src/__tests__/components/navigation/CommandPalette.test.tsx src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx src/__tests__/navigation-wiring.test.ts
# Ergebnis: 8 passed

pytest tests/test_process_kernel_wave25_quick_actions.py -q --no-cov
# Ergebnis: 4 passed

npm run test:run -- src/__tests__/features/ki-usability/toolbar-actions.test.ts src/__tests__/components/patterns/Wizard.test.tsx
# Ergebnis: 6 passed

npm run test:run -- src/__tests__/components/navigation/CommandPalette.test.tsx src/__tests__/features/ki-usability/toolbar-actions.test.ts
# Ergebnis: 3 passed

npm run test:run -- src/__tests__/features/role-density/role-density.test.ts src/__tests__/components/navigation/PageToolbar.role-density.test.tsx src/__tests__/components/workflow/ProcessStatusPanel.test.tsx src/__tests__/components/patterns/Wizard.test.tsx
# Ergebnis: 15 passed

pytest tests/test_process_kernel_wave27_ui_density_manifest.py -q --no-cov
# Ergebnis: 4 passed

npm run test:run -- src/__tests__/features/role-density/role-density.test.ts src/__tests__/components/workflow/ProcessStatusPanel.test.tsx
# Ergebnis: 9 passed

pytest tests/l3_import/test_import_l3.py tests/l3_import/test_validate_mapping.py -q --no-cov
# Ergebnis: 16 passed

pytest tests/test_reflect_archive_loader.py tests/l3_import/test_import_l3.py tests/l3_import/test_validate_mapping.py -q --no-cov
# Ergebnis: 21 passed

pytest tests/test_apm_pipeline_contract.py tests/test_reflect_archive_loader.py tests/l3_import/test_import_l3.py tests/l3_import/test_validate_mapping.py -q --no-cov
# Ergebnis: 25 passed

pytest tests/test_json_state_contract.py tests/test_apm_pipeline_contract.py tests/test_reflect_archive_loader.py tests/l3_import/test_import_l3.py tests/l3_import/test_validate_mapping.py -q --no-cov
# Ergebnis: 29 passed

pytest tests/test_genxais_cycle_contract.py tests/test_dashboard_prompt_module_contracts.py tests/test_json_state_contract.py tests/test_apm_pipeline_contract.py tests/test_reflect_archive_loader.py tests/l3_import/test_import_l3.py tests/l3_import/test_validate_mapping.py -q --no-cov
# Ergebnis: 37 passed

npm run test:run -- src/__tests__/components/workflow/CompactDecisionCard.test.tsx src/__tests__/components/workflow/ProcessStatusPanel.test.tsx src/__tests__/features/role-density/role-density.test.ts
# Ergebnis: 11 passed

npm run type-check
# Ergebnis: gruen
```

## Offene Punkte

- Der globale Roadmap-Status ausserhalb von `docs/architecture/process-kernel/STATUS.md` ist nicht automatisch synchron und muss bei groesseren Wave-Abschluessen separat nachgezogen werden.
- Neue Frontend- und Integrationsarbeit hat auf den bestehenden Bausteinen aus Wave 9 bis Wave 27 aufzusetzen; keine neuen Parallelpfade fuer Routing, Dispatch, Audit, SLA oder Prozesssurfacing.
- Bei jeder neuen Lieferung sind Schichtgrenzen aktiv zu verifizieren:
  - kein Import von `app/api/` aus `app/core/`
  - keine Endpoint-Querimporte
  - Pruefung standardmaessig per `rg`

## Naechster sinnvoller Ausbau

- Rollen- und prozessbezogene Surfacing-Contracts fuer Wave 22, Wave 25 und Wave 27 weiter aus produktiven Backend-Manifesten speisen
- Explainability- und Berechtigungs-Hinweise direkt im Command-Surfacing
- Rollen-Density kuenftig tenant- und prozessbezogen breiter aus produktiven Command-/Policy-Manifests statt primaer aus Frontend-Kontextsignalen ableiten

## Referenzen

- Strategischer Plan: `C:\Users\Jochen\.cursor\plans\valeo_wettbewerbsanalyse_spitzenposition_79027aec.plan.md`
- Detailstaende: `wave-*/STATUS.md`
