---
title: Universal Mask Runtime — Plattformstatus
type: reference
audience: [agent, entwickler, architektur, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-06-30
version: 2.0.0
description: Maschinenlesbarer Projektstand der Human+Agent Mask Runtime (UIX-021…043) — Lieferstand, Gates, Governance. Migration aller entity-detail Masken abgeschlossen.
---

# Universal Mask Runtime — Plattformstatus

> **Kurzfassung (2026-06-30):** Migration vollständig abgeschlossen (UIX-021…043). **26 native SDs** im Registry — alle `generatorReady=True`, `advisoryScore=1.00`, `temporary=False`. 20 Frontend thin wrapper pages + route-aliases. Frontend-Typecheck, Frontend-Build, BFF-Build und Universal-Masken-Playwright-Smoke sind lokal grün. Keine weiteren Migrations-Kandidaten unter den entity-detail ObjectPage-Masken.

## Lieferstand

| Slice | Inhalt | Status | Commit / Nachweis |
|-------|--------|--------|-------------------|
| UIX-RUNTIME-ROLLOUT-021 | Rollout-Kandidaten auf `useUniversalMaskRuntime` | ✅ abgeschlossen | Workboard 2026-06-29 |
| UIX-RUNTIME-022 | Sort-Whitelist Backend + Frontend | ✅ | `0f6e06f43` |
| UIX-RUNTIME-023 | FilterPlan (Human + Agent) | ✅ | `bf83d8563` |
| UIX-RUNTIME-025 | UniversalFormState | ✅ | `7f95ef674` |
| UIX-RUNTIME-026 | ActionRuntime | ✅ | `7f95ef674` |
| UIX-RUNTIME-027 | WorkflowState + BlockingReasons | ✅ | `b3eea3a20` |
| UIX-RUNTIME-028–029 | CRM 360 native Runtime + AgentMaskContract | ✅ | `81d706da8` |
| UIX-RUNTIME-030 | Generator-Readiness-Gates (Basis) | ✅ | `e6cabb380` |
| UIX-031 | Doku-Konsolidierung | ✅ | diese Datei + Open-Gaps + Workboard |
| UIX-033 | Verschärfte Readiness-Gates (pro Tabelle) | ✅ | `fd2b8a7cf` |
| UIX-032 | CI-/Gate-Nachweis | ✅ lokal | siehe Abschnitt CI |
| UIX-034 | CRM 360 Native Parity-Matrix | ✅ | [`uix-034-crm360-native-parity-matrix.md`](../../adr/uix-034-crm360-native-parity-matrix.md) |
| UIX-035 | ActionRuntime produktiv (CRM Aktivität) | ✅ | `tests/test_uix035_action_runtime_crm.py` |
| UIX-036 | Agent End-to-End-Test | ✅ | propose → dryRun → validate |
| UIX-037 | Rollout-Kandidaten neu bewerten | ✅ | `uix-037-rollout-readiness-report.md` |
| UIX-038 | Einkauf Supplier native ScreenDefinition | ✅ | `generatorReady=true`, `advisoryScore=1.0` |
| UIX-039 | CRM Opportunity native ScreenDefinition | ✅ | `generatorReady=true`, `advisoryScore=1.0` |
| UIX-040 | Lager Article Stock native ScreenDefinition | ✅ | `generatorReady=true`, `advisoryScore=1.0` |
| UIX-041 | 7 native SDs Wave 1 (delivery-note, purchase-order, ap/ar-invoice, stock-movement, harvest-settlement, payment-run) | ✅ | alle 1.00 |
| UIX-042a | Advisory-Score 1.00 für alle SDs inkl. sales-order, kontrakte, crm-360 | ✅ | 13 SDs gesamt |
| UIX-042b | UniversalNativeDetailPage + 7 thin wrapper pages + 7 route-aliases | ✅ | generischer Wrapper |
| UIX-043 | 13 weitere ObjectPage-Masken migriert; vollständige Inventur; 18 bewusst exempt | ✅ | **26 SDs gesamt** |
| UIX-044/045 | FilterPlan-HTTP-Vertrag `filter_plan` + Native ActionRuntime-Anschluss | ✅ lokal | `universal-mask-filter-plan.spec.ts`, `UniversalNativeDetailPage` |
| UIX-046/047 | CommandEndpoint-Stubs (neue_bestellung, mahnen, freigeben) + Bestätigungsdialog | ✅ lokal | `test_uix046_048_command_endpoints_safety.py` |

## Architektur (Single Source of Truth)

```text
ScreenDefinition
  ├── Human: compileRenderPlan → useUniversalMaskRuntime → UniversalMaskRenderer
  │         Sort/Filter (FilterPlan), Form (UniversalFormState), Actions (ActionRuntime), Workflow
  └── Agent: generateAgentMaskContract → readable/editable/sensitive fields, policies, audit
Backend: GET /api/v1/masks/{id}/screen-definition   ({mask_id:path} — Slash in IDs)
         GET /api/v1/masks/{id}/agent-contract
         GET /api/v1/masks/{id}/readiness
         GET /api/v1/masks/{id}/entity/{entity_id}   (generischer Kopf-Stub Wave 2)
         GET /api/v1/mask-rollouts/.../tabs/{tab}?page&limit&q&sort&sort_dir&filter_plan
         POST commandEndpoint aus ScreenDefinition.actions (Human execute via ActionRuntime)
```

Referenz-Code: `packages/frontend-web/src/components/mask-builder/runtime/`

## Readiness-Gates (UIX-030 + UIX-033)

**Mandatory** (blockieren `generatorReady`):

| Gate | Prüfung |
|------|---------|
| `schema_valid` | `validateScreenDefinition` ohne Fehler |
| `non_temporary` | `adapter.temporary !== true` |
| `data_sources` | `dataSources[]` wenn Tabellen existieren |
| `table_data_source_bound` | jede `serverPagination`-Tabelle hat passenden `dataSourceKey` |
| `table_columns_complete` | jede Tabelle ≥2 nicht-triviale Spalten |
| `actions_classified` | jede Action: `dangerLevel` + `permission` oder `stubReason` |

**Advisory** (Warnings, `advisoryScore` 0–1):

| Gate | Prüfung |
|------|---------|
| `sort_whitelist` | pro Tabelle mindestens eine `sortable`-Spalte |
| `filter_columns` | pro Tabelle mindestens eine `filterable`-Spalte |
| `agent_contract` | explizites `agentContract` (Auto-Generate akzeptiert, aber gewarnt) |
| `workflow_declared` | `workflow` oder `noWorkflowReason` |
| `stable_test_selectors` | `screenRoot`, Primary Actions, Table test ids |
| `table_query_contract` | sort/filter-Spalten = stabile Keys, passend zur Backend-Whitelist |

Frontend: `checkGeneratorReadiness()` in `runtime/generatorReadiness.ts`
Backend: `_check_readiness()` in `app/api/v1/endpoints/mask_screen_definition.py`

## Governance für Agenten

1. **Migration abgeschlossen** — alle entity-detail Masken sind native SDs.
2. **Nächster Fokus:** commandEndpoints für gestubte Actions (neue_bestellung, freigeben, mahnen, drucken).
3. **CRM 360** ist produktiver Referenzfall mit vollständiger Action-Runtime.
4. **finance/payment-run** bleibt `forbiddenForAgents=True` — human approval required.
5. **Maschinenlesbare Quellen** bei Masken-Arbeit immer zuerst lesen:
   - diese Datei
   - [`open-gaps-and-known-issues.md`](../../project-context/open-gaps-and-known-issues.md)
   - [`active-workboard.md`](../../agent-ops/active-workboard.md)
   - [`uix-043-mask-migration-inventory.md`](uix-043-mask-migration-inventory.md) — vollständige Inventur aller 26 SDs + Exemptions

## Registry-Übersicht (Stand 2026-06-30)

| Domain | SDs | Schlüssel-IDs |
|--------|-----|---------------|
| CRM | 3 | customer-360, opportunity, lead |
| Einkauf | 6 | supplier, purchase-order, anfrage, angebot, anlieferavis, auftragsbestaetigung |
| Finance | 5 | ap-invoice, ar-open-item, payment-run, debitor, kreditor, bankkonto |
| Lager | 2 | article-stock, stock-movement |
| Sales | 2 | sales-order, delivery-note |
| Agrar | 4 | kontrakte, harvest-settlement, duenger, saatgut |
| Qualität | 1 | reklamation |
| Futtermittel | 2 | einzelfuttermittel, mischfuttermittel |

## UIX-037 — Rollout-Reihenfolge (abgeschlossen)

Alle 10 ursprünglichen Kandidaten sind nativ promoted — Stand nach UIX-043:

1. `einkauf/supplier` — nativ bereit, Frontend-Verdrahtung folgt in UIX-042
2. `crm/opportunity` — nativ bereit, Parity-Matrix aktualisiert
3. `lager/article-stock` — nativ bereit
4. `sales/delivery-note`
5. `einkauf/purchase-order`
6. `finance/ap-invoice`
7. `finance/ar-open-item`
8. `lager/stock-movement`
9. `agrar/harvest-settlement`
10. `finance/payment-run` *(zuletzt — hohes Agenten-Risiko)*

## CI-/Gate-Nachweis (UIX-032)

Pflicht-Checks:

```bash
pnpm --dir packages/frontend-web type-check
pnpm --dir packages/frontend-web build
pnpm --dir packages/frontend-web test:run
pytest tests/test_mask_rollout_batch_w42_51.py
pytest tests/test_agent_mask_contract.py
```

Ergebnis wird nach jedem Lauf hier aktualisiert:

| pytest rollout batch | 2026-06-29 | ✅ 24/24 | `--no-cov`; Coverage-Dateilock unter Windows bei parallelem Lauf umgangen |
| pytest agent/readiness | 2026-06-29 | ✅ 22/22 | `test_agent_mask_contract.py`, inkl. native Promotionen 038–040 |
| Frontend type-check | 2026-06-30 | ✅ | `pnpm --dir packages/frontend-web run type-check` |
| Frontend build | 2026-06-30 | ✅ | `pnpm --dir packages/frontend-web run build` |
| BFF build | 2026-06-30 | ✅ | `pnpm --dir packages/bff run build` |
| Universal-Masken Playwright | 2026-06-30 | ✅ 8/8 | CRM Customer Pilot, Sales Order Pilot, Mask Render Performance; Flags `VITE_ENABLE_UNIVERSAL_MASK_*` |
| FilterPlan Playwright | 2026-06-30 | ✅ 1/1 | `universal-mask-filter-plan.spec.ts`; native `/crm/lead/:id`, Chip + `filter_plan` Request |
| FilterPlan Contract | 2026-06-30 | ✅ 3/3 | `tests/test_uix044_filter_plan_contract.py`; isolierter Pytest-Lauf ohne Plugin-Autoload |
| Frontend vitest (readiness) | 2026-06-29 | ✅ 15/15 | `generatorReadiness.test.ts` |
| Frontend vitest (gesamt) | — | ausstehend | UIX-032 |
| GitHub Actions quality-gate | — | ausstehend | kein sichtbarer Run für UIX-028…030 |

## Bewertung (Stakeholder-Audit 2026-06-29)

| Dimension | Stand |
|-----------|-------|
| Architektur | sehr guter Sprung |
| Human+Agent-Gedanke | umgesetzt |
| Runtime-Basis | vorhanden |
| Readiness-Governance | vorhanden (033 verschärft) |
| CRM 360 native Pfad | vorhanden, Parität offen |
| CI-/Release-Nachweis | fehlt |
| Doku-Konsistenz | nach UIX-031 synchron |
| Produktionsreife | noch nicht bewiesen |

## Verweise

- [RenderPlan Architecture](render-plan-architecture.md)
- [ADR-011 UI-Maskenstrategie](../../adr/adr-011-ui-maskenstrategie.md)
- [Rollout Batch Waves 42–51](mask-rollout-batch-w42-51.md)
- [CRM 360 Native Parity-Matrix](../../adr/uix-034-crm360-native-parity-matrix.md)
- [Einkauf Lieferant Parity (UIX-038)](../domains/einkauf/mask-parity-supplier-native.md)
- [CRM Opportunity Parity (UIX-039)](../domains/crm/mask-parity-opportunity-native.md)
- [Domain Rollout Template](mask-generator-rollout-template.md)
- [Benutzerhandbuch Masken-Plattform](../../benutzerhandbuch/masken-plattform.md)
- [Entwickler Mask Runtime API](../../entwickler/mask-runtime-api.md)
- [Agent-Runbook Mask Runtime Agent-Modus](../../agent-docs/runbooks/mask-runtime-agent-modus.md)
