---
title: Coding-Konventionen & UI-Invarianten
type: explanation
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Coding-Konventionen & UI-Invarianten

Verbindliche Muster für Backend und Frontend — vollständige Referenz in `CLAUDE.md`.

## Backend

- **FastAPI** mit Pydantic 2.x-Schemas; `response_model` für neue Routen.
- **Services** kapseln Domänenlogik; Router nur Wiring, HTTP-Mapping, Auth.
- **Fehler:** RFC 7807 Problem Details; keine leeren `except`-Blöcke.
- **SQL:** parametrisierte Queries; dynamisches SQL nur aus festen Feldlisten
  (CI-Gate `scripts/check_sql_fstrings.py`).
- **Events:** Outbox + NATS JetStream (ADR-008).

## Frontend (React / TypeScript)

- Pfad-Alias: `@/*` → `src/*`
- Server-State: TanStack React Query; Client-State: Zustand
- Mask Builder für ERP-Masken: `ObjectPage`, `ListReport`, `Wizard` — siehe `docs/MASKEN.md`

## Error-Handling (UI)

Bei nutzergetriggerten Aktionen (Speichern, Löschen, Freigeben, …):

- sichtbares Feedback (`toast`, `setError`) oder Rethrow
- keine stillen Fehler
- optionale Best-effort-Fehler nur mit Kommentar, warum unkritisch

## Mutation-Lifecycle (UI)

Jede **nicht-idempotente** Nutzeraktion braucht:

1. Duplicate-Submit-Guard (`loading` / `isPending` / `loadingActionKey`)
2. Button/Control **disabled** während pending
3. Cleanup in `finally`
4. sichtbares Erfolgs- **und** Fehler-Outcome

**Worker-Funktionen** (`persistX()`) setzen keinen UI-Pending-State — Guards gehören
in den Event-Handler (`handleXClick()`).

Mask Builder: `useMaskActions` + `loadingActionKey` an `ObjectPage` übergeben.

Listen: pro Zeile keyed pending (`Set<string>` / `withPending`), nicht ein globales Boolean.

## Dokument-Konsistenz (Gewohnheits-Prinzip)

Belegketten (Auftrag → Lieferschein → Rechnung) teilen Layout: Kopf, Partner,
Positionen, Summen, Toolbar — `docs/MASKEN.md`.

## Agenten & Slices

Parallele Arbeit: `AGENTS.md`, Workboard claimen, Slice-YAML pflegen.
