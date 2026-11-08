---
title: Handshake — Workboard Sync wt-msi / 6e40b3212
type: handshake
audience: [agent, entwickler]
owner: Cursor Composer
status: aktiv
last_reviewed: 2026-10-22
date: 2026-10-22
---

# Handshake: Workboard wt-msi-Sync 2026-10-22

## Absicht

Selektiver Abgleich der kanonischen `docs/agent-ops/active-workboard.md`
(Hauptbaum) mit der abweichenden Kopie unter `C:/Users/Jochen/wt-msi/...`
sowie Nachzug fehlender Studio-Abschnitte aus Commit `6e40b3212`.
Keine Mass-Ersetzung der Datei. Cursor-Eintraege vom 22.10. bleiben.

## Nachgezogen aus wt-msi (fehlten im Haupt)

Claude-Code / Mask-Pipeline:

- `MASK-STUDIO-ROLLOUT-20261020` (in Arbeit)
- `MASK-CLI-20261019` (reserviert) + Meilensteine
- `STAMMDATEN-BEARBEITEN-20261019` (abgeschlossen)
- `WRITE-ROLES-AREAS-20261019` (abgeschlossen)
- `ADMIN-WRITE-ROLES-20261019` (abgeschlossen)
- `MASK-COMMANDS-ROLLOUT-20261019` (abgeschlossen)
- `MCP-MASK-GENERIC-20261019` (abgeschlossen)
- `MASK-STUDIO-INVENTAR-20261019` (abgeschlossen)
- Handshake-Hinweis „Index im Hauptarbeitsbaum“ (2026-10-20)

Codex-Slices (19./20.10., Auszug):

- `WORKFLOW-SAGA-LIFECYCLE`, `POS-WS-CLEANUP`, `CI-COMPLIANCE-REAL`,
  `GDPR-SUBJECT-BOUNDARY`, `CHROMA-DEPLOY-REVIEW`, `RUNTIME-AUTH-PROOF`,
  `RUNTIME-EVIDENCE-CLEANUP`, `AUDIT-IDENTITY-INTEGRITY` (reserviert),
  `WRITE-AUTHORIZATION-DECISION`, `ROLE-DESCRIPTIONS`,
  `MANAGER-ROLE-ENFORCEMENT`, `PERSONAL-FILE-AUTH-PERSISTENCE`,
  `COMMITTED-API-INTEGRATION`, `ROLE-PROVIDER-ROLLOUT`,
  `GIT-MAIN-HISTORY-GUARD`, `PARALLEL-MIGRATION-MERGE`,
  `AP-WORKFLOW-SECURITY`, `AP-CI-SELECTION`, `AP-MASK-CONTRACT-CI`,
  `STUDIO-CLI-BULK` (abgeschlossen), `STUDIO-MIGRATION-ENGINE`,
  `STUDIO-MULTICHANNEL-READ` (abgeschlossen)

## Nachgezogen / bestaetigt aus `6e40b3212` (Studio)

Parallel-Agent `d41fc2ec` hat gelöschte Studio-Codedateien aus HEAD restored
und Studio-Abschnitte wieder eingefuegt. Sync-Lauf danach mit
skip-if-present: alle unten bereits vorhanden, kein Doppelinsert.

| Slice | Status im Board |
|---|---|
| `STUDIO-CLI-BULK-20261020` | abgeschlossen |
| `STUDIO-TABLE-QUERY-20261020` | abgeschlossen |
| `STUDIO-TABLE-ROUTES-20261021` | abgeschlossen |
| `STUDIO-PLAN-HISTORY-20261021` | abgeschlossen |
| `STUDIO-PLAN-INTEGRATION-20261021` | abgeschlossen |
| `STUDIO-LIVE-PROBE-20261021` | abgeschlossen |
| `STUDIO-MIGRATION-ENGINE-20261020` | in Arbeit (vs. wt-msi `reserviert`) |
| `STUDIO-GENERATED-ENTITIES-20261021` | in Arbeit |
| `STUDIO-ENTITY-RELEASE-20261021` | reserviert |

## Statuskonflikte

| Slice | Haupt vorher | Quelle neuer | Aufgeloest |
|---|---|---|---|
| `BELEG-STORNO-BROWSER-20261019` | reserviert | wt-msi abgeschlossen + QA-Ergebnis | **abgeschlossen** |
| `STUDIO-MIGRATION-ENGINE-20261020` | reserviert (wt-msi) | `6e40b3212` in Arbeit | **in Arbeit** |

Begruendung Storno: wt-msi enthaelt abgeschlossenen Browser-/CI-Nachweis
(`docs/quality-assurance/beleg-storno-browser-20261019.md`); reserviert war
stale.

## Erhalten (nur Haupt, 22.10. Cursor)

- `UIX-MASKENFAMILIEN-TAXONOMIE-20261022` (offen Plan)
- `UIX-BELEG-FAMILIE-VERERBUNG-20261022` (offen Plan)
- `MASK-BESTELLUNG-NAV-NATIVE-20261022` (abgeschlossen)
- `MASK-PRIMARY-NAV-NATIVE-20261022` (abgeschlossen)

## Sonstiges

- `last_reviewed` auf `2026-10-22` gesetzt.
- `docs/architecture/process-kernel/STATUS.md`: lokaler Drift zu wt-msi
  (Studio-Abnahme-Absatz + AP-Sicherheitsnachtrag 20.10. nur in wt-msi).
  **Nicht** blind gemerged/revertiert — Klaerung separat.
- Parallel `d41fc2ec`: siehe `studio-wb-sync-20261022.md` (Code-Restore);
  Studio-Claims nicht stehlen.
- Kein Push, kein Mass-WIP, keine tmp-Skripte im Commit.
