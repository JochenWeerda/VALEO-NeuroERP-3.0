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
| CI-GRUEN / develop-Identität | Claude/CI | CI-Skripte, Hooks |
| Tourenplanung / Training / Bestellvorschlag | parallel | Godfiles / Prozessmasken |
| UIX-BELEG-FAMILIE-VERERBUNG-20261022 | Plan offen | eigener Beleg-Slice — nicht überschreiben |
| MASK-BESTELLUNG Create Legacy | abgeschlossen Nav / Create offen | keine Regressions-Nav |

## Was dieser Slice darf

- `docs/architecture/uix/maskenfamilien-taxonomie.md`
- Querverweise in UMR-Status, Open-Gaps, Beleg-Vererbungsdoku
- Workboard-Eintrag Status `offen`

## Was erst nach neuem Claim + Handshake

- Parent-Factory in `screen_definitions.py`
- Page-/Nav-Migrationen
- Beleg ProcessBand/Ribbon-Implementierung
