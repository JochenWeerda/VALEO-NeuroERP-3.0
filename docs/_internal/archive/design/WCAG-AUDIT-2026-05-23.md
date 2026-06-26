# WCAG 2.2 AA — Design-Rollout Audit (Kernrouten)

Stand: **2026-05-23** | Slice: `DESIGN-MERIDIAN-PHASE4-001`

## Gepruefte Bereiche

| Route / Komponente | Kriterium | Ergebnis |
|---|---|---|
| ERP-Shell Sidebar | 2.5.5 Target Size (44px) | OK — Buttons/Nav h-11 |
| Button / Input defaults | 2.5.5 | OK — h-11 (44px) |
| `muted-foreground` | 1.4.3 Contrast | OK — neutral-600 (~5.9:1) |
| TableHead | 1.4.12 Text Spacing | OK — 11px uppercase, tracking |
| `:focus-visible` | 2.4.11 Focus Appearance | OK — 2px ring in index.css |
| `prefers-reduced-motion` | 2.3.3 | OK — index.css media query |
| Badge / Alert semantic | 1.4.3 | OK — Token-basiert, Dark-Mode-Varianten |
| ObjectPage split | 1.4.10 Reflow | OK — stacked unter lg, Split ab lg |
| Portal Terra | 1.4.3 | OK — Terra-Tokens WCAG-geplant in design-tokens-terra.css |

## Manuelle Restpruefung (extern)

- Screen-Reader-Durchgang Dashboard + ObjectPage (NVDA/VoiceOver)
- Produktive Farbkalibrierung auf Lager-Terminals (theme-warehouse separat)

## Repo-Checks

```bash
pnpm --filter @valero-neuroerp/frontend-web type-check
python scripts/agent_workboard_supervisor.py validate
```

Empfehlung: Playwright `@axe-core/playwright` in CI als Folgeslice verankern.

**Stand Phase 2–4:** repo-seitig abgeschlossen (2026-05-23).

## axe-core CI (DESIGN-MERIDIAN-AXE-CI-001)

Stand: **2026-05-23** — implementiert und in `quality-gate.yml` als blockierendes Gate.

**Kernrouten (8):** `/`, `/agrar`, `/einkauf/bestellungen`, `/finance`, `/lager`, `/portal/feldbuch`, `/portal/naehrstoffbilanzen`, `/portal/rationsoptimierung`

```bash
pnpm --filter @valero-neuroerp/frontend-web test:e2e:accessibility
```

**Behobene Shell-Verstoesse:** Breadcrumbs Home-Link, CopilotDockPanel inert/Contrast, ShortcutHelpPanel labels/inert, AskVALEO FAB aria-label, NativeSelect ariaLabel.

Verbleibend extern: manueller Screen-Reader-UAT (NVDA/VoiceOver).
