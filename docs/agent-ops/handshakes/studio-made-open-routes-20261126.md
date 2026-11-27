# Handshake: 2026-11-26 — STUDIO-MADE-OPEN-ROUTES-20261125

**Von:** Cursor Cloud (`bc-da4b7dae-d1f9-5d66-9f4d-0b1eee0c8809`)  
**An:** Lead / Integrator (Merge `main` + Sync `develop`); Codex für Gate-D Rest  
**Ziel des Slices:** Offene Frontend-Routen und Altmasken auf Studio-made Qualität (ObjectPage/ListReport/Wizard → ScreenDefinition/`creation` → UniversalNative*; ProcessBand/Tabs/Tokens/Mutations-Invarianten).

## Stand

- Branch: `cursor/studio-made-open-routes-8809` · PR #213 · Head `14e044510`
- Inventar (`mask_route_migration_inventory.py`): Routen `hand_built` **0**, `legacy_mask_pattern` **0**, `runtime_wired` **1131**/1150, `pages_hand` **37** (bewusst Specialized-Legacy / Dialoge / Charts)
- Gates A/B/C/E: **829/829** (`verify_made_by_studio_gates.py`)
- Gate-D Mock-Smoke: **1160/1160** (580 Masken × Hell/Dunkel); Batch 115 Alias-Pfad-Doppelarbeit verworfen
- Batch 116: Design-Tokens `vordruck-editor-legacy`, `kunden-schlagkartei-legacy`
- Batch 117: Mutations-Invarianten `ernte-annahme-erfassung-legacy` (Berechnung/Abschlag/Endabrechnung + best-effort Flow-Spine-Checkpoint)

## Erledigt

- Routen-Migration auf Runtime/`hand_built` 0
- Generator-Gates A/B/C/E grün, Draft-clean, Advisory Ø 1.0
- Live-Legacy Specialized Surfaces: Tabs/Tokens/Mutations-Nachzüge bis Batch 117
- QA: `docs/quality-assurance/studio-made-open-routes-20261125.md`
- Qualitätsversprechen: `docs/architecture/uix/made-by-studio-qualitaetsversprechen.md`

## Offen

- Gate D **Live-SSO** Browser-Abnahme (Hell/Dunkel der *publizierten* Maske)
- Gate D **Image-CI** / kanonischer `table-catalog` → Codex `STUDIO-ENTITY-RELEASE-20261021` (Dateibesitz Katalog unberührt)
- Systemweites Siegel „alle Masken made by studio“ bleibt Ziel, kein Ist

## Betroffene Dateien (Schwerpunkt)

- `packages/frontend-web/src/pages/**` (Native-Wrapper, `*-legacy` Specialized)
- `packages/frontend-web/tests/e2e/uix-gate-d-studio-cockpit-smoke.spec.ts`
- `docs/quality-assurance/studio-made-open-routes-20261125.md`
- `docs/architecture/uix/made-by-studio-qualitaetsversprechen.md`
- `docs/agent-ops/active-workboard.md` (dieser Slice)

## Tests / Checks

- `python scripts/mask_route_migration_inventory.py`
- `python scripts/verify_made_by_studio_gates.py` → A/B/C/E 829/829
- `python scripts/generate_agent_handbuch.py --check`
- PR-CI auf Head: docs-governance / mkdocs / role-contracts grün (Batch 117)

## Offene Risiken

- Feature-Branch und `main` sind divergent (main hat Commits außerhalb der M6-Basis); Merge nach `main` braucht Integration der main-seitigen Commits.
- `develop` liegt vollständig hinter `main` → Sync als Fast-Forward von `main` vorgesehen.
- Gate-D Live bleibt Codex-Blocker; Merge schließt das Siegel A–D nicht.

## Annahmen

- Nutzerauftrag 26.11.2026 autorisiert Doku-Nachzug sowie Merge nach `main` und Sync `develop` (hebt früheres „Kein Self-Merge“ für diesen Integrationsschritt auf).
- `docs/admin/table-catalog.json|.md` bleiben Codex-Besitz.

## Ratsche M2 (Nachzug 26.11.2026)

| Bucket | Vorher | Nachher |
|--------|--------|---------|
| `handgebaut_routen` | 2 | **0** |
| `altmuster_routen` | 14 | **0** |

Live-Stufen der geschlossenen Routen: `studio_versioniert` / `screen_definition` (kein handgebaut/Altmuster mehr).  
`python scripts/mask_studio_inventory.py --check` bleibt **rot** wegen Codex-Bahn: 3× `aktionen_nicht_deklariert` neu, 17× ohne MCP, 91× ohne CLI.

## Nächster konkreter Schritt

1. PR #213 CI am neuen Head abwarten → Claude Admin-Merge („bereit zum Merge, Head \<sha\>“).
2. Codex: Aktions-Ratsche + Gate D Live-SSO/Image-CI.
3. Cursor Goal Bahn 2–3: M4 `domaenen_abnahme.py --check`, M7 Handbuch/Demo/A11y.
