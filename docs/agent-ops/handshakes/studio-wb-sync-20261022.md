---
title: Handshake Studio Workboard-Sync 2026-10-22
type: handshake
audience: [agent]
owner: Cursor Composer
status: aktiv
last_reviewed: 2026-10-22
---

# Handshake — Studio Workboard-Sync / Dateiwiederherstellung

## Befund

1. Working Tree hatte **63** getrackte Studio-Pfade als gelöscht (`studio_entity_*`,
   `studio_migration*`, `valeo_cli/*`, ADRs 084/085, QA, Frontend screen-studio,
   Tests, Handbuch). **HEAD/main besitzt sie weiterhin** → lokal restored.
2. Workboard fehlten vs `6e40b3212` die Abschnitte STUDIO-TABLE-ROUTES,
   PLAN-HISTORY, PLAN-INTEGRATION, GENERATED-ENTITIES, ENTITY-RELEASE, LIVE-PROBE
   (CLI-BULK/MULTICHANNEL/MIGRATION waren bereits wieder da). Cursor-Kopf 22.10.
   bleibt.

## Kooperation

- Restore Codedateien: dieser Agent (Cursor Composer).
- Workboard-Sync: Koop mit Sync-Agent `a0f22080`; fehlende Abschnitte aus
  `6e40b3212` eingefügt unter `STUDIO-WB-SYNC-20261022`.

## Codex-Claims (nicht stehlen)

| Slice | Status laut Board | Anfassen? |
|---|---|---|
| STUDIO-GENERATED-ENTITIES-20261021 | in Arbeit | nein (Code) |
| STUDIO-ENTITY-RELEASE-20261021 | reserviert | nein |
| STUDIO-BELEG-THEME-20261016 | in Arbeit | nein |
| STUDIO-MODEL / SEMANTIC | in Arbeit | nein |
| BELEG-STORNO-BROWSER | reserviert | nein |

## Qualitätskatalog

Neu: `docs/architecture/uix/made-by-studio-qualitaetsversprechen.md`.
