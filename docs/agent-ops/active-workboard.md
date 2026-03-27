# Active Workboard

## Zweck

Gemeinsame operative Sicht fuer parallele Agentenarbeit.

Diese Datei ist absichtlich schlank und soll bei jeder Session schnell lesbar bleiben.

## Aktueller Stand

- Datum: `2026-03-27`
- Branch: `main` (Wave 104 + Repo-Hygiene committed, kein offener develop-Branch)
- Source of Truth: `docs/architecture/process-kernel/STATUS.md`

## Aktive Slices

| Slice-ID | Thema | Status | Owner | Dateibesitz | Naechster Schritt | Blocker |
|----------|-------|--------|-------|-------------|-------------------|---------|
| OPS-001 | Workflow-Analyse-Methodik und Agent-Ops-Doku | abgeschlossen | — | `AGENTS.md`, `docs/agent-ops/**`, `docs/workflows/**`, `docs/project-context/**`, `docs/quality-assurance/**` | bei neuen Workflow-Slices wiederverwenden | keine |
| DOCS-105 | Wave-104-Dokumentations-Nachzug (GAP-G/H/I, Repo-Hygiene) | abgeschlossen | — | `docs/architecture/process-kernel/STATUS.md`, `DELIVERY-MAP.md`, `wave-104/STATUS.md`, `docs/roadmap/status/2026-03-27-wave-104-abschluss.md`, `docs/project-context/open-gaps-and-known-issues.md` | committen | keine |
| P2P-001 | Procure-to-Pay Direktbestellung: Workflow-Analyse, QA und Handover-Haertung | in arbeit | naechster Agent | `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/cards/einkauf/**`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` | Workflow/Card-Doku anlegen, Pflichtvalidierung und Lieferadress-Handover absichern | keine |

## Reservierungsregel

- Pro Slice ein Owner.
- Dateibesitz klar dokumentieren.
- Ueberschneidungen nur mit explizitem Integrationshinweis.

## Letzte wichtige Entscheidungen

- Workflow-Analyse wird dokumentationsbasiert und card-basiert durchgefuehrt.
- Standardmaske vor Spezialmaske ist verbindliche Entscheidungsregel.
- Restart-sicherer Kontext laeuft ueber `AGENTS.md` plus `docs/agent-ops/`.
- Wave 104 vollstaendig abgeschlossen (GAP-A bis GAP-I, 5931 Tests gruen, commit `1ad5ea4d`).
- Naechste Prioritaeten: P2P-001 (Procure-to-Pay Workflow-Doku und QA), danach Landhandel-Kernprozesse.

## Handoff: 2026-03-27 — DOCS-105

**Von:** Claude Sonnet 4.6
**An:** naechste Session / naechster Agent
**Ziel:** Vollstaendiger Dokumentations-Nachzug Wave 104 GAP-G/H/I + Repo-Hygiene
**Stand:** abgeschlossen
**Erledigt:**
- `docs/architecture/process-kernel/STATUS.md` — Gesamtstatus auf 2026-03-27 / 5931 Tests, Waves 102–104, neuer Abschnitt "Waves 102 bis 104"
- `docs/architecture/process-kernel/DELIVERY-MAP.md` — Stand 2026-03-27, Wave-104-Eintrag GAP-A–I
- `docs/architecture/process-kernel/wave-104/STATUS.md` — Governance-Headings komplett
- `docs/roadmap/status/2026-03-27-wave-104-abschluss.md` — NEU: Detaildoku, Architekturabgleich, Commitliste
- `docs/project-context/open-gaps-and-known-issues.md` — geschlossene Punkte markiert, neue Realitaet dokumentiert
- `docs/agent-ops/active-workboard.md` — Slices aktualisiert, Handoff-Block erstellt
**Offen:** Docs-Commit ausstehend. P2P-001 folgt als naechster Slice.
**Naechster konkreter Schritt:** DOCS-105-Dateien committen, dann P2P-001 aufnehmen.
**Tests / Checks:** `node scripts/docs-governance-check.cjs` muss gruen bleiben.
**Annahmen:** Testzahl 5931 = 5916 (Wave-100-Baseline) + 15 (Wave-104); bei naechstem vollstaendigen pytest-Lauf verifizieren.

## Slice-Details

## Slice: P2P-001 - Procure-to-Pay Direktbestellung

**Owner:** aktuell offener Agent
**Status:** in arbeit
**Ziel:** Ersten belastbaren Workflow-/QA-Slice fuer den Flow-Spine-Einstieg `Procure-to-Pay` in die Standard-Bestellmaske dokumentieren und einen gefundenen Workflow-Bruch direkt beheben.
**Fachlicher Scope:** Flow-Spine-Handover, Standardmaske `Bestellung anlegen`, Direktbestellung als Standardstart, Bedarfsmeldung und Rahmenabruf als Alternativpfade.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/cards/einkauf/**`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Abnahmekriterien:** Workflow-Doku nach Master-Prompt vorhanden; mindestens eine Card nach Template vorhanden; Bestellmaske verhindert leere oder fachlich unbrauchbare Anlage; Lieferadresse wird konsistent an den Backend-Contract uebergeben; Regressionstest ist gruen.
**Tests / Checks:** `pnpm --dir packages/frontend-web test:run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Doku-Updates:** Workboard, Workflow-Analyse, Card-Datei, Resume-/Handoff-Block.
**Risiken / Blocker:** Backend-Compat-Contract erzwingt Pflichtfelder nicht serverseitig; Frontend muss fuer diesen Slice eine belastbare Mindestvalidierung sicherstellen.
**Naechster konkreter Schritt:** Workflow-Doku und Card aufbauen, dann den validierten Handover in der Bestellmaske absichern.
