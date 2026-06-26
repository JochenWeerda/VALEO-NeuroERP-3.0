---
title: Entwicklerdokumentation
type: explanation
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.3.0
---

# Entwicklerdokumentation

Einstieg für Entwickler:innen in Architektur, Setup und Konventionen.

## Erste Schritte

| Thema | Seite |
|-------|-------|
| Lokales Setup (Backend, Frontend, DB) | [Lokales Setup](lokales-setup.md) |
| Multi-Tenancy & Schemas | [Datenmodell & Tenancy](datenmodell-tenancy.md) |
| Error-Handling & Mutation-Invarianten | [Konventionen](konventionen.md) |
| pytest, Vitest, Playwright | [Test-Strategie](test-strategie.md) |
| Backend-Service-Module (Inventar) | [Service-Inventar](service-inventory.md) |

## Architektur & Entscheidungen

| Bereich | Pfad | In der Site |
|---------|------|-------------|
| Architektur-Index | `docs/architecture/index.md` | Navigation → Architektur |
| Process-Kernel (Lieferstand) | `docs/architecture/process-kernel/STATUS.md` | Navigation → Process Kernel |
| ADR-Index | `docs/adr/README.md` | Navigation → ADRs → Index (+ 38 Einzel-ADRs via Generator) |
| Wave-STATUS (historisch) | `docs/architecture/process-kernel/wave-*/` | Repo only (vom Build ausgeschlossen) |

## Weitere Quellen

- `CLAUDE.md` / `AGENTS.md` (Repo-Root) — Konventionen, Invarianten, Agent-Operating-Guide.
- [Schnittstellen](../schnittstellen/index.md) — REST, MCP, Events.
- `docs/workflows/` — Prozessketten (intern, Ergebnisse in Open-Gaps).
- `docs/project-context/open-gaps-and-known-issues.md` — bekannter Lieferstand (repo-only).
