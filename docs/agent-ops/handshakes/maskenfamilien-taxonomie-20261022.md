---
title: Handshake — Maskenfamilien-Taxonomie vs. Codex/Parallel-Claims
type: handshake
status: aktiv
date: 2026-10-22
---

# Handshake: UIX-MASKENFAMILIEN-TAXONOMIE-20261022

## Absicht

Systemweite Familien-Taxonomie und Cluster-Roadmap (nur Doku). Keine Änderungen an Beleg-Builder, Studio-Theme, CI oder Godfiles.

## Geschützte Claims (nicht kollidieren)

| Claim / Bereich | Owner | Schutz |
|---|---|---|
| STUDIO-BELEG-THEME | Codex | Theme, Beleg-SD, Versionsregister |
| STUDIO-MODEL / STUDIO-SEMANTIC | Codex | Semantic/LLM-Studio |
| STUDIO-GENERATED-ENTITIES / ENTITY-RELEASE | Codex | Compiler, `studio.entity.v1`, Freigabeprofil |
| BELEG-STORNO-BROWSER | Codex | reservierte Browser-Storno-Abnahme |
| CI-GRUEN / develop-Identität | Claude/CI | CI-Skripte, Hooks |
| Tourenplanung / Training / Bestellvorschlag | parallel | Godfiles / Prozessmasken |
| UIX-BELEG-FAMILIE-VERERBUNG-20261022 | Plan offen | eigener Beleg-Slice — nicht überschreiben |
| MASK-BESTELLUNG Create Legacy | abgeschlossen Nav / Create offen | keine Regressions-Nav |

## Sync 2026-10-22 (Cursor)

Kanonisches Board bleibt `active-workboard.md` (kein zweites). Qualitätskatalog:
[`made-by-studio-qualitaetsversprechen.md`](../../architecture/uix/made-by-studio-qualitaetsversprechen.md).
WIP hatte Studio-CLI/Entity-Dateien lokal gelöscht — aus HEAD restored. Nächster freier
Siegel-Schritt: Stamm-Parent via CLI-Lebenszyklus, nicht Beleg-Theme.

## Was dieser Slice darf

- `docs/architecture/uix/maskenfamilien-taxonomie.md`
- Querverweise in UMR-Status, Open-Gaps, Beleg-Vererbungsdoku
- Workboard-Eintrag Status `offen`

## Was erst nach neuem Claim + Handshake

- Parent-Factory in `screen_definitions.py`
- Page-/Nav-Migrationen
- Beleg ProcessBand/Ribbon-Implementierung
