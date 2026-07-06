# Handshake: Claude Code zu UIX Meridian Single Mask Builder

Stand: 2026-07-06
Von: Codex
An: Claude Code

## Kontext in einem Satz

Meridian ist jetzt zentral im Single Mask Builder verankert und zusätzlich mit einem fokussierten Visual-Audit abgesichert; Referenzmasken bleiben Abnahmefälle, keine separaten UI-Implementierungen.

## Gelieferte Commits

| Commit | Inhalt |
|---|---|
| `a79fcf8c5` | Claim `UIX-MERIDIAN-BUILDER-001` |
| `ab89601f9` | Meridian-Vertrag in `ScreenDefinition.layout`, `RenderPlan.shell`, Universal/Fast-Renderern und Readiness-Gates |
| `6a96958e9` | Claim `UIX-MERIDIAN-VISUAL-AUDIT-002` |
| `d897eafc4` | Fokussierter Meridian Visual-Audit mit Benutzerhandbuch-Screenshot-Helfern |

## Architekturentscheidung

- Strategische Zieloberflaeche bleibt:
  `ScreenDefinition -> RenderPlan -> useUniversalMaskRuntime -> UniversalMaskRenderer`.
- `ScreenDefinition.layout` traegt `floorplan`, `density`, `contextRail` und `tableProfile`.
- `RenderPlan.shell` ist der zentrale Transport fuer Meridian-Layoutentscheidungen.
- Finance, CRM 360 und Lager werden als Referenzabnahmen validiert, nicht als eigene UI-Pfade gebaut.
- Low-Fidelity-/Wireframe-Triage ist im Design-Regelwerk dokumentiert, um Klickwege kurz zu halten und Nebenfelder frueh in Tabs oder Kontextbereiche zu verschieben.

## Wichtige Dateien

- `app/core/screen_definitions.py`
- `app/api/v1/endpoints/mask_screen_definition.py`
- `packages/frontend-web/src/components/mask-builder/**`
- `packages/frontend-web/tests/e2e/uix-056-native-route-smoke.spec.ts`
- `packages/frontend-web/tests/e2e/meridian-visual-audit.spec.ts`
- `docs/design/valeo-meridian-experience.md`
- `docs/architecture/uix/universal-mask-runtime-status.md`
- `docs/project-context/open-gaps-and-known-issues.md`
- `docs/agent-ops/slices/UIX-MERIDIAN-BUILDER-001.yaml`
- `docs/agent-ops/slices/UIX-MERIDIAN-VISUAL-AUDIT-002.yaml`

## Verifikation

- `pnpm --dir packages/frontend-web test:run src/__tests__/components/mask-builder/runtime/generatorReadiness.test.ts src/__tests__/components/mask-builder/UniversalMaskRenderer.test.tsx src/__tests__/render-plan/schema-compiler.test.ts` -> 25 passed
- `pytest tests/test_agent_mask_contract.py tests/test_uix046_048_command_endpoints_safety.py -q --no-cov` -> 270 passed
- `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false` -> gruen
- `python scripts/generate_agent_handbuch.py --check` -> gruen
- `pnpm --dir packages/frontend-web exec playwright test tests/e2e/uix-056-native-route-smoke.spec.ts --project=chromium` -> 7 passed
- `pnpm --dir packages/frontend-web exec playwright test tests/e2e/mask-render-performance.spec.ts --project=chromium` -> 2 passed
- `pnpm --dir packages/frontend-web exec playwright test tests/e2e/meridian-visual-audit.spec.ts --project=chromium` -> 9 passed

## Bekannte Hinweise

- Playwright `globalTeardown` meldet bestehende repo-weite Visual-Tour-Console-Issues aus `packages/frontend-web/visual-tour-results/issues.json`; die fokussierten Meridian-Smokes und der Meridian-Visual-Audit sind gruen.
- `python scripts/agent_workboard_supervisor.py validate` scheitert an alten Slice-YAMLs ohne `file_ownership`; das ist nicht durch die Meridian-Slices verursacht.
- Im Working Tree lagen waehrend der Codex-Arbeit fremde A6/Coverage-Aenderungen. Diese wurden nicht committet oder reverted.

## Claude: Bitte beachten

- Vor neuen UIX-/Mask-Builder-Aenderungen einen eigenen Slice claimen und sofort committen.
- Keine neuen page-spezifischen Referenzmasken fuer Finance, CRM oder Lager bauen.
- Wenn eine Maske schwach wirkt: Schema, Compiler, Renderer oder Gates verbessern.
- Tabellenprofile respektieren: Finance `financial`, Lager `inventory`, Audit-Listen `audit`.
- Bei Detail-/Workflow-Masken `contextRail` nicht auf `none` setzen.

## Naechster sinnvoller Schritt

Nur bei neuem fachlichem Bedarf weitere native ScreenDefinitions gegen den Meridian-Vertrag haerten. Der aktuelle Builder- und Visual-Audit-Scope ist abgeschlossen.
