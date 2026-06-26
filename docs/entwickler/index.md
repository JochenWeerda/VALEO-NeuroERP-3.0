---
title: Entwicklerdokumentation
type: explanation
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.1.0
---

# Entwicklerdokumentation

Einstieg für Entwickler:innen in Architektur, Setup und Konventionen.

## Architektur & Entscheidungen

| Bereich | Pfad | In der Site |
|---------|------|-------------|
| Architektur-Index | `docs/architecture/index.md` | Navigation → Architektur |
| Process-Kernel (Lieferstand) | `docs/architecture/process-kernel/STATUS.md` | Navigation → Process Kernel |
| ADR-Index | `docs/adr/README.md` | Navigation → ADRs |
| Wave-STATUS (historisch) | `docs/architecture/process-kernel/wave-*/` | Repo only (vom Build ausgeschlossen) |

## Weitere Quellen

- `CLAUDE.md` / `AGENTS.md` (Repo-Root) — Konventionen, Invarianten, Agent-Operating-Guide.
- `docs/workflows/` — Prozessketten (intern, Ergebnisse in Open-Gaps).
- `docs/project-context/open-gaps-and-known-issues.md` — bekannter Lieferstand.

## Geplante Inhalte

- Lokales Setup (Backend, Frontend, Datenbank).
- Datenmodell & Multi-Schema-Tenancy.
- Coding-Konventionen, Error-Handling-/Mutation-Invarianten.
- Test-Strategie (pytest, Vitest, Playwright).

> Setup- und Konventionsseiten folgen in Folge-Slices.
