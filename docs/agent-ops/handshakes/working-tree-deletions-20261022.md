---
title: Handshake Working-Tree Deletions 2026-10-22
type: handshake
audience: [agent]
owner: Cursor Composer
status: aktiv
last_reviewed: 2026-10-22
---

# Handshake — Non-Studio Working-Tree-Löschungen wiederhergestellt

## Befund

Nach dem Studio-Restore (63 Pfade, siehe `studio-wb-sync-20261022.md`) blieben
**178** getrackte Dateien als `deleted` im Working Tree. Alle existierten in
`HEAD`; keine untracked Ersetzungen am gleichen Pfad; kein Treffer unter
Touren/Training/Bestellvorschlag-Godfiles.

Muster wie bei den Studio-Löschungen: breite Massen-WIP über QA, Tests, Endpoints,
Services, Mask-Builder, Alembic, Scripts — nicht fokussierte Slice-Arbeit.

## Top-Level vor Restore

| Top-Level | Count |
|---|---|
| tests/ | 56 |
| docs/ | 54 |
| app/ | 24 |
| packages/ | 21 |
| scripts/ | 12 |
| alembic/ | 6 |
| config/ | 1 |
| .github/ | 1 |
| .husky/ | 1 |
| playwright-tests/ | 1 |
| playwright.anmeldung.mjs | 1 |
| **Summe** | **178** |

## Aktion

| | Count |
|---|---|
| **restored** (`git restore -- <path>`) | **178** |
| **remaining deleted** | **0** |
| offen/klären | 0 |

Hinweis: LFS meldete bei drei Beleg-Storno-Screenshots „should have been pointers“;
Dateien sind wieder im Tree.

### Nachtrag `api.py` (2026-10-22, Cursor Composer)

Lokaler Diff `app/api/v1/api.py` war **+1/−44** (kein Studio-Router-Entfernen, aber
`_Sammelrouter` + Kommandos-/Bridge-Includes weg: `sales_order_commands`,
`docflow_return.command_router`, `stammdaten_bearbeiten`, Einkauf-/Agrar-/Finance-/CRM-
Kommandos, `preis_kalkulation_bridge`). Kein dokumentierter aktiver Slice für die
Entfernungen; Muster wie Massen-WIP. **Restored** auf HEAD — Datei wieder clean.

## Nicht angefasst (Claims)

- Tourenplanung / Training / Bestellvorschlag-Godfiles (nicht in der Löschliste)
- STUDIO-BELEG-THEME / STUDIO-MODEL / SEMANTIC / GENERATED-ENTITIES / ENTITY-RELEASE (Code)
- Kein Mass-Commit unrelated modifications; kein Push

## Kooperation

Restore: Cursor Composer. Commit dieses Handshakes nur.
