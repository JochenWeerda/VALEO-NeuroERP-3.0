---
title: Universal Mask Runtime — Plattformstatus
type: reference
audience: [agent, entwickler, architektur, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-19
version: 2.2.0
description: Maschinenlesbarer Projektstand der Human+Agent Mask Runtime (UIX-021…050) — Lieferstand, Gates, Governance. ActionRuntime produktiv. Alle nativen commandEndpoints verdrahtet (SPEC-P1-04).
---

# Universal Mask Runtime — Plattformstatus

> **Nachtrag 2026-08-19 (`L3-HABIT-BRIDGE-001`):** Der Single Mask Builder
> transportiert herstellerneutrale ERP-Gewohnheitsvertraege fuer Aktionszonen,
> Summary-Position, Sticky-Regionen, deklarative Shortcuts und Enter-Fokus.
> Aktiviert fuer CRM Customer 360, Lager Artikelbestand und Sales
> Lieferschein; L3-Originalbilder mit Echtdaten bleiben ausserhalb von Git.

> **Kurzfassung (2026-07-06):** **SPEC-P1-04/08 abgeschlossen** — alle nativen ScreenDefinitions ohne `stubReason`; gemeinsamer `MaskActionRuntime` (validate/dryRun/propose/execute → Audit + Outbox); Inventur `scripts/check_mask_command_endpoint_inventory.py` Exit 0. Chargen-FEFO sortiert nach MHD. Siehe Handshake [`cursor-claude-spec-p1-04-08-2026-07-06.md`](../../agent-ops/handshakes/cursor-claude-spec-p1-04-08-2026-07-06.md).

> **Kurzfassung (2026-07-01):** Migration vollständig abgeschlossen (UIX-021…043). **26 native SDs** im Registry — alle `generatorReady=True`, `advisoryScore=1.00`, `temporary=False`. ActionRuntime produktiv verdrahtet (UIX-045). Erste CommandEndpoints aktiv: `create_activity`, `neue_bestellung`, `mahnen`, `freigeben`, `stornieren`, `bestellen`, `wareneingang`, `abschliessen`, `qualifizieren` (UIX-046/053). Multi-Stage Dialog Flow (Confirm→dryRun→AuditReason→Execute) mit menschenlesbarer proposedChanges-Anzeige und Toast-Feedback (UIX-047). Agent Safety auf alle 26 SDs ausgeweitet (UIX-048). CI-Workflow mit BFF-Build-Stage ergänzt (UIX-049).


> **Nachtrag 2026-07-05:** Meridian ist als Builder-Capability im Single Mask Builder verankert. `ScreenDefinition.layout` liefert `floorplan`, `density`, `contextRail` und `tableProfile`; `RenderPlan.shell` uebernimmt diese Felder zentral; Frontend- und Backend-Readiness blockieren fehlende Meridian-Metadaten.

> **Visual-Audit 2026-07-05:** `tests/e2e/meridian-visual-audit.spec.ts` nutzt die Benutzerhandbuch-Screenshot-Helfer (`waitUntilRenderable`, Content-QC, Capture-Locator) fuer Finance, CRM 360 und Lager bei 1366x768, 1440x900 und 1920x1080. Lokal gruen: `pnpm --dir packages/frontend-web exec playwright test tests/e2e/meridian-visual-audit.spec.ts --project=chromium` (9 passed). Der Playwright-Global-Teardown meldet bestehende Repo-weite Visual-Tour-Console-Issues, nicht den fokussierten Meridian-Audit.

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
| UIX-044/045 | FilterPlan-HTTP-Vertrag `filter_plan` + Native ActionRuntime-Anschluss | ✅ | `universal-mask-filter-plan.spec.ts`, `UniversalNativeDetailPage` |
| UIX-046 | CommandEndpoints aktiviert: `create_activity`, `neue_bestellung`, `mahnen`, `freigeben` | ✅ | `test_uix046_048_command_endpoints_safety.py` |
| UIX-047 | ActionResult UX: human-readable proposedChanges, validationErrors-Liste, Danger-Dialoge, Toast | ✅ | `UniversalNativeDetailPage.tsx` — TypeScript grün |
| UIX-048 | Agent Safety auf alle 26 nativen SDs ausgeweitet (dynamisch aus Registry) | ✅ 219/219 | `test_uix046_048_command_endpoints_safety.py` |
| UIX-049 | CI-Workflow: BFF-Build-Stage + UIX-050/053-Tests + `--no-cov` überall | ✅ | `.github/workflows/universal-mask-ci.yml` |
| UIX-050/053 | 5 weitere CommandEndpoints (stornieren, bestellen, wareneingang, abschliessen, qualifizieren) + AuditReasonDialog + dryRun-Preview + BFF MCP-Tool | ✅ | `mask_actions.py`, `maskActions.ts` |
| UIX-051 | Alle 26 nativen SDs mit `/:id`-Routen + native Wrapper (sales-order, kontrakte) | ✅ | `d87de90a5`, `test_uix051_legacy_route_migration.py` |
| UIX-054 | Finale Route-Wahrheit: `route-inventory.gen.json` + `route-tree.gen.tsx` | ✅ lokal | `test_uix054_route_inventory_verification.py` |
| UIX-055 | GitHub Actions `universal-mask-ci` + `workflow_dispatch` | ✅ | Run `28540744515` — backend/frontend/bff/e2e grün |
| UIX-056 | Browser-Smoke native `/:id`-Routen (5 repräsentative Masken) | ✅ lokal | `uix-056-native-route-smoke.spec.ts` |
| UIX-057 | Rollback-/Fallback-Matrix | ✅ | [`uix-057-native-route-rollback-matrix.md`](uix-057-native-route-rollback-matrix.md) |
| SPEC-P1-04 | Alle nativen commandEndpoints — `MaskActionRuntime`, Inventur 0 stubReason | ✅ | `mask_action_runtime_service.py`, `check_mask_command_endpoint_inventory.py` |
| SPEC-P1-08 | Chargen-Tiefenmodell + FEFO über MHD | ✅ | `inventory_lot_trace_service.py`, `inv_lot_depth_spec_p1_08` |
| UIX-060 | Omnibox-Shell + Backend-Katalog/Telemetry | ✅ | Workboard 2026-07-07 |
| UIX-061 | Rollen-Workspaces + Tiles-Primitive + Rollen-Redirect | ✅ | 27 pytest, 6 Vitest, Workspace Playwright grün |
| UIX-062 | Collab-Rail v1: `contextRailSections`, datensatzgebundene Notizen, Mentions, Inbox/Outbox | ✅ lokal | 4 pytest, 7 Vitest, TypeScript 0, Playwright 1/1 |
| UIX-063 | Planungskalender v1: `calendar`-Contract, Projektionsservice, ICS-Feed, CalendarRenderer | ✅ lokal | 33 pytest, 3 Vitest, TypeScript 0, Playwright 1/1 |
| L3-HABIT-BRIDGE-001 | Herstellerneutrale Desktop-Gewohnheitsvertraege + 3 Referenzmasken | ✅ technisch abgeschlossen, Human Review vor Rollout | 125 Mask-Builder/RenderPlan-Tests, 4 Backend-Tests, 12 Visual-Audits; ADR-056 + Paritaetsmatrix |

| L3-MDE-INBOX-003 | Native MDE-Worklist + zentrale statusabhaengige Tabellenzeilen-Aktionen | technisch abgeschlossen, Provider-Pilot extern | `schnittstelle/mde-inbox`, Quarantaene/Retry-Audit, ADR-057 |

| L3-DOCRET-INBOX-004 | Dokumentenruecklauf mit Versandstatus, Audit und Ursprungsbeleg | technisch abgeschlossen, Provider-Pilot extern | `docflow/dokumenten-ruecklauf`, ADR-058 |

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
| `layout_metadata` | `layout.floorplan`, `layout.density`, `layout.contextRail`; Detail-/Cockpit-/Workflow-Masken nicht `contextRail=none` |
| `table_profile` | Tabellenmasken haben `layout.tableProfile`; Finance=`financial`, Lager/Inventory=`inventory` |
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

## Aktive CommandEndpoints (Stand 2026-07-06)

Alle **26 nativen ScreenDefinitions** (`temporary=False`) haben für Mutations-Actions einen `commandEndpoint` — **kein `stubReason` mehr** (Inventur-Skript + `test_spec_p1_04_mask_commands.py`).

Gemeinsame Runtime: `app/services/mask_action_runtime_service.py` — Modi `validate` / `dryRun` / `propose` / `execute`; bei `execute`: Audit (`crm_action_audit_log`) + Outbox (`outbox_events`).

| Action | Screen | Endpoint |
|--------|--------|----------|
| `create_activity` | crm/customer-360, crm/opportunity | `/api/v1/crm/customers|…/actions/create_activity` |
| `neue_bestellung` | einkauf/supplier | `/api/v1/einkauf/lieferanten/{entity_id}/actions/neue_bestellung` |
| `mahnen` | finance/ar-open-item | `/api/v1/finance/open-items/{entity_id}/actions/mahnen` |
| `freigeben` | finance/ap-invoice, finance/payment-run | AP + Zahlungslauf (auditReasonRequired) |
| `stornieren` | lager/stock-movement | `/api/v1/lager/stock-movements/{entity_id}/actions/stornieren` |
| `bestellen` | einkauf/angebot | `/api/v1/einkauf/bestellungen/{entity_id}/actions/bestellen` |
| `wareneingang` | einkauf/anlieferavis, lager/article-stock | `/api/v1/lager/artikel/{entity_id}/actions/wareneingang` |
| `abschliessen` | qualitaet/reklamation | `/api/v1/reklamationen/{entity_id}/actions/abschliessen` |
| `qualifizieren` | crm/lead | `/api/v1/crm/leads/{entity_id}/actions/qualifizieren` |
| `drucken` | sales/delivery-note, agrar/harvest-settlement | `/api/v1/.../actions/drucken` |

Vollständige Liste: `python scripts/check_mask_command_endpoint_inventory.py` (Exit 0 = OK).

**Hinweis:** `execute` simuliert derzeit Status-Mutation + Outbox/Audit; volle Domain-Persistenz (PDF-Druck, echte Buchungen) folgt bei Bedarf pro Action.

## Governance für Agenten

1. **Migration abgeschlossen** — alle entity-detail Masken sind native SDs.
2. **ActionRuntime produktiv** — alle nativen Mutations-Actions mit `commandEndpoint`; Dialog-Flow Confirm→dryRun→AuditReason→Execute.
3. **Agent Safety** — alle 26 SDs geprüft (dynamisch, nicht hart kodiert); `sensitiveFields`, `dangerousActions`, `forbiddenForAgents`, `humanApprovalRequired` validiert.
4. **CRM 360** ist produktiver Referenzfall mit vollständiger Action-Runtime.
5. **finance/payment-run** bleibt `forbiddenForAgents=True` — human approval required.
5. **Maschinenlesbare Quellen** bei Masken-Arbeit immer zuerst lesen:
   - diese Datei
   - [`open-gaps-and-known-issues.md`](../../project-context/open-gaps-and-known-issues.md)
   - [`active-workboard.md`](../../agent-ops/active-workboard.md)
   - [`uix-043-mask-migration-inventory.md`](uix-043-mask-migration-inventory.md) — vollständige Inventur aller 26 SDs + Exemptions
   - [`uix-057-native-route-rollback-matrix.md`](uix-057-native-route-rollback-matrix.md) — Legacy-Fallback je native Route

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

| pytest rollout batch | 2026-06-29 | ✅ 24/24 | `--no-cov` |
| pytest agent/readiness | 2026-06-29 | ✅ 22/22 | `test_agent_mask_contract.py` |
| pytest UIX-046/048 Safety | 2026-07-01 | ✅ 219/219 | alle 26 SDs, dynamisch aus Registry |
| pytest UIX-050/053 Advanced | 2026-07-01 | ✅ 15/16 | BFF-File-Checks + dryRun-Stubs |
| pytest UIX-044 FilterPlan | 2026-06-30 | ✅ 3/3 | `test_uix044_filter_plan_contract.py` |
| Frontend type-check | 2026-07-01 | ✅ | TypeScript 0 Fehler (inkl. UIX-047 Änderungen) |
| Frontend build | 2026-06-30 | ✅ | `npm run build` |
| BFF build | 2026-06-30 | ✅ | `npm run build` in `packages/bff/bff-web` |
| Universal-Masken Playwright | 2026-06-30 | ✅ 8/8 | CRM Customer Pilot, Sales Order Pilot, Mask Render Performance |
| FilterPlan Playwright | 2026-06-30 | ✅ 1/1 | `universal-mask-filter-plan.spec.ts` |
| Frontend vitest (gesamt) | — | ausstehend | CI-Job `continue-on-error: true` |
| pytest UIX-051 Route Migration | 2026-07-01 | ✅ 49/49 | `test_uix051_legacy_route_migration.py` |
| pytest UIX-054 Route Inventory | 2026-07-01 | ✅ 46/46 | `route-inventory.gen.json` + native Priorität |
| UIX-056 Native Route Playwright | 2026-07-01 | ✅ 6/6 lokal | `uix-056-native-route-smoke.spec.ts` |
| GitHub Actions universal-mask-ci | 2026-07-01 | ✅ | Run `28540744515` — UIX-051/054 + routes:generate-Drift + E2E-Smoke |
| UIX-062 Collab-Rail Backend | 2026-07-07 | ✅ 4/4 | `pytest tests/test_uix062_collab_notes.py -q --no-cov` |
| UIX-062 Collab-Rail Vitest | 2026-07-07 | ✅ 7/7 | `schema-compiler.test.ts`, `WorkflowPanelRenderer.test.tsx` |
| UIX-062 Frontend type-check | 2026-07-07 | ✅ | `pnpm exec tsc --noEmit` |
| UIX-062 Playwright Collab-Smoke | 2026-07-07 | ✅ 1/1 | `collab-rail-smoke.spec.ts`; globaler Visual-Tour-Teardown meldet bestehende Fremdseiten-Console-Issues |
| UIX-063 Planungskalender Backend | 2026-07-07 | ✅ 33/33 | `pytest tests/test_uix063_planning_calendar.py tests/test_workspace_cockpits_uix061.py -q --no-cov` |
| UIX-063 CalendarRenderer Vitest | 2026-07-07 | ✅ 3/3 | `calendar-renderer.test.tsx` |
| UIX-063 Frontend type-check | 2026-07-07 | ✅ | `pnpm --dir packages/frontend-web type-check` |
| UIX-063 Playwright Kalender-Smoke | 2026-07-07 | ✅ 1/1 | `planung-kalender-smoke.spec.ts`; globaler Visual-Tour-Teardown meldet bestehende Fremdseiten-Console-Issues |

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

## FEED-ADVICE-UX-011 - Cockpits ueber den UniversalMaskRuntime

Seit 2026-07-14 kompiliert `UniversalNativeCockpitPage` nicht mehr direkt am
Runtime-Vertrag vorbei. Cockpits durchlaufen nun dieselbe Kette wie native
Objektmasken:

`ScreenDefinition -> RenderPlan -> useUniversalMaskRuntime -> UniversalMaskRenderer`.

Erster produktiver Agrar-Anwendungsfall ist `agrar/feed-advice`: ein nativer,
rollenorientierter Einstieg, der die spezialisierte Solver-Workbench nur fuer eine
konkrete Planungsaufgabe lazy laedt. Architekturentscheid und Variantenbewertung:
ADR-041 sowie `docs/design/feed-advice-experience-architecture-2026-07-14.md`.

## Feeding-Kernausbau 2026-07-15

FEED-CORE-015 bis 017 ergaenzen drei weitere native Agrar-Screens ueber dieselbe
Runtime-Kette: `agrar/feeding-businesses`, `agrar/feeding-group` und den
read-only ListReport `agrar/feeding-reference-data`. Das generierte Agent-
Handbuch inventarisiert damit 41 Masken. Alle drei Screens sind
`temporary=False` und generator-ready; fachliche Dialoge bleiben schmale
Domain-Overlays. Das globale Command-Inventar hat unabhaengig davon fuenf offene
High-Risk-Aktionen auf `agrar/ration`, dokumentiert unter Open Gaps.

## L3-PRODUCTION-CONTROL-006

`produktion/produktionsleitstand` fuehrt Produktionsliste, Muehlenlauf,
Umbuchung, Stapelbuchung und Nachbearbeitung als native, generatorfaehige
Meridian-Worklist zusammen. Die Maske bleibt ein duennes Cockpit ueber der
zentralen Runtime; Quellfachlogik fuer Bestand, Charge und FIBU wird nicht
dupliziert.

## L3-INVENTORY-AUX-007

`lager/inventur-nebenlaeufe` nutzt dieselbe zentrale Runtime fuer
hashgebundene Zaehllisten-/Import-/Kontroll-/Bewertungs-/Vortragsbatches mit
Vier-Augen-Freigabe und append-only Audit.

## L3-BILLING-BATCH-008

`finance/rechnungstapel` verbindet Ausgangs-/Eingangsrechnung und beide
Selbstabrechnerarten als native, generatorfaehige Worklist mit Vier-Augen-
Freigabe, Fehlerzeilen, Retry und Belegnachweis.

## L3-ROHWARE-OPERATOR-009

`lager/fremdware` stellt die vorhandene Fremdwaren-Einlagerung als native,
generatorfaehige Operator-Worklist bereit. Mandant/Eigentuemer, Lager und
Restbestand sind sichtbar; Umbuchung sowie Teil-/Vollauslagerung laufen
statusvalidiert, begruendet und append-only auditiert.

## L3-QUERY-CENTER-010

`auswertungen/abfrage-center` ist eine native, generatorfaehige Worklist fuer
allowlistgebundene Read-Model-Abfragen. Vorschau, Favoriten, Druck und
signierter Import/Export werden zentral gerendert; beliebiges SQL bleibt
ausgeschlossen.

## L3-TEAM-CALENDAR-011

`planung/kalender` nutzt seine vorhandene native Kalender-Primitive nun fuer
autorisierte Benutzer-/Teamansichten. Private Fremdtermine werden auf
Frei/Belegt redigiert; Teamdetails sind berechtigt und Ablehnungen optional.

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
