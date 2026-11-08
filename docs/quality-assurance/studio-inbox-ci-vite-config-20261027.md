---
title: Kanonische Vite-Konfiguration und Testinitialisierung
type: qa
audience: [entwickler, qa, agent]
owner: Codex
status: active
last_reviewed: 2026-10-27
---

# STUDIO-INBOX-CI Vite-Konfiguration – QA 2026-10-27

## Umfang

Gepruefter Snapshot: `artifacts/migration-repair-source`, Claim-Commit
`48fa099e89e7f04c91ef7daf9605db4d2b1a80a8`.

- Die veraltete `packages/frontend-web/vite.config.js` und ihre erzeugte
  `vite.config.d.ts` wurden entfernt. Vor dem Edit stimmten beide Datei-Hashes
  bytegenau mit den entsprechenden unveraenderten Dateien im Claim-Commit
  ueberein.
- `packages/frontend-web/vite.config.ts` bleibt die massgebliche Konfiguration
  und verweist auf das bestehende `src/test-setup.ts`.
- `packages/frontend-web/tsconfig.node.json` schreibt TypeScript-Projektbuilds
  und Build-Info nach `node_modules/.tmp/`, ausserhalb der Quellwurzel.
- Keine Abhaengigkeiten installiert oder Lockdateien, Tests und Produktquellen
  geaendert.

## Abnahme

| Pruefung | Ergebnis |
|---|---|
| Bestehende `inbox-widget.test.tsx` mit automatischer Vite-Konfigurationssuche | 21/21 bestanden; bestaetigt Jest-DOM-Systemmatcher `toBeInTheDocument` ohne explizites Config-Argument |
| `tsc -b tsconfig.node.json` und `tsc --noEmit --project tsconfig.json` | Beide erfolgreich |
| `vite build --mode production` | Erfolgreich; 4.641 Module verarbeitet |

Der Produktionsbuild meldete Hinweise zu nicht interpretierbaren
Zod-Kommentarannotationen, einem zirkulaeren TanStack-Chunk und mehreren leeren
Dependency-Chunks. Der Build endete erfolgreich.

Als zusaetzliche Probe schlug `ProcessStatusPanel.test.tsx` (3 Faelle) mit
`Invalid Chai property: toBeInTheDocument` fehl. Die Datei ruft in ihrem
Testhelfer `vi.resetModules()` auf. Die Systemmatcher-Abnahme ist durch die
bestehende `inbox-widget.test.tsx`-Suite bestaetigt; es wurden keine per-File
Matcher-Workarounds ergaenzt.


## Lead-Nachlauf

Der Reset der Modulregistry im ProcessStatusPanel-Test wurde durch einen
explizit pro Test zurueckgesetzten Mockzustand ersetzt. Die drei urspruenglichen
Rollen-/Freigabe-Dichtepruefungen bleiben unveraendert. Kein per-Datei-Matcher-
Workaround und keine Aenderung der Produktrollen. Gemeinsamer Lauf nach den
Detailroutenreparaturen: sechs Dateien, 65/65 Tests bestanden (41 Routen-/
Anlagefaelle, drei Prozessdichtefaelle und 21 InboxWidget-Faelle). Vollstaendige
Frontend-Typpruefung nach den Produktkorrekturen ebenfalls erfolgreich.
