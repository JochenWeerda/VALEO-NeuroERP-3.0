---
title: FEED-ADVICE-UX-011 Impact Note
type: handoff
audience: [agent, entwickler, produkt, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-07-14
version: 1.0.0
---

# FEED-ADVICE-UX-011 Impact Note

## Ergebnis

Die Portal-Fuetterungsberatung ist kein Re-Export der Expertenmaske mehr. Sie
startet mit der nativen ScreenDefinition `agrar/feed-advice`. Der bisherige Solver
bleibt fachlich unveraendert erreichbar, wird aber als eigener Lazy-Chunk erst nach
der Aufgabe „Ration planen oder optimieren“ geladen.

## Architekturwirkung

- `UniversalNativeCockpitPage` nutzt nun den UniversalMaskRuntime; diese Aenderung
  gilt zentral fuer alle nativen Cockpits.
- ADR-041 setzt Hybrid als Zielbild: native Worklists/ObjectPages/Cockpits plus
  begrenzter spezialisierter Solver.
- Neue Lifecycle-, Bestands- und Controlling-Funktionen gehoeren nicht in
  `rationsoptimierung.tsx`.
- Bestehende interne Route `/futtermittel/rationsoptimierung` bleibt kompatibel.

## Abnahme

```text
pytest ScreenDefinition/Workspaces: 29 passed
Frontend TypeScript: 0 Fehler
Frontend Vitest: 376 passed, 1 skipped
Frontend Produktionsbuild: gruen, Solver separater 151,45-kB-Chunk
Architecture Validate/Drift: gruen
Playwright localhost: 1 passed, Visual Tour 0 Probleme
```

## Direkter Anschluss

`FEED-ADVICE-LIFECYCLE-007` ersetzt statische Cockpitwerte und den vorlaeufigen
Rations-/Freigaben-Sprung durch persistente Gruppen, versionierte Rationen,
Statusautomat und native Worklist/ObjectPage.

