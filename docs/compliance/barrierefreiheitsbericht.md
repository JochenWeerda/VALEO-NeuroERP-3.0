---
title: Barrierefreiheitsbericht (Gerüst)
type: reference
audience: [betrieb, entwickler, qs]
owner: Cursor Cloud
status: aktiv
last_reviewed: 2026-11-26
version: 0.1.0
description: Gerüst BFSG / EN 301 549 aus vorhandenen axe-Läufen (WCAG 2.2 AA). Keine Gesamtfreigabe.
---

# Barrierefreiheitsbericht (Gerüst)

Stand: 2026-11-26. Bezug: BFSG / EN 301 549; technische Teilprüfung über
axe-core (WCAG 2.2 A/AA) in
`packages/frontend-web/tests/e2e/accessibility.spec.ts`.

## Geltungsbereich (automatisiert)

Kernrouten des axe-Laufs (Tag `@accessibility`):

| Route | Zweck |
|-------|--------|
| `/` | Start / Shell |
| `/agrar` | Agrar-Bereich |
| `/einkauf/bestellungen` | Einkauf |
| `/finance` | Finanzen |
| `/lager` | Lager |
| `/portal/feldbuch` | Portal Feldbuch |
| `/portal/naehrstoffbilanzen` | Portal Nährstoff |
| `/portal/rationsoptimierung` | Portal Ration |

Ausführung (Frontend-Paket):

```bash
cd packages/frontend-web
npx playwright test tests/e2e/accessibility.spec.ts --grep @accessibility
```

Erwartung im Gerüst: **0 axe-Violations** auf den gelisteten Routen (CI/lokal
mit UI-Testsitzung; API wird für den Lauf mit 503 abgefangen — siehe Spec).

## Designregeln (Repo)

- WCAG-AA-Kontrast über semantische Status-/Theme-Utilities (siehe `CLAUDE.md`)
- Tabs über `components/ui/tabs.tsx` (ARIA)
- Keine Rohpalette / keine `text-[10px]`-Mikrolabels in Masken

## Offen (Stichproben / Gesamtbericht)

- Manuelle Stichproben Tastatur / Screenreader an Fachmasken — **offen**
- Erweiterter Routenkatalog über die acht Kernrouten — **offen**
- Formale Konformitätserklärung EN 301 549 für das Verkaufsprodukt — **offen**
  (dieses Dokument ist nur das Gerüst aus der automatischen Prüfung)

## Verweise

- `packages/frontend-web/tests/e2e/accessibility.spec.ts`
- `docs/roadmap/m7-m8-vorarbeiten.md` §1 (Barrierefreiheitsbericht)
- `docs/design/frontend-design-skill-audit.md`
