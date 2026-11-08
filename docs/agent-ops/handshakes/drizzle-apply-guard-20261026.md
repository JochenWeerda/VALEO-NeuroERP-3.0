---
title: Handshake migrate:apply-Waechter 2026-10-26
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-26
---

# Handshake: Abgleich vor migrate:apply

**Von:** Claude Code. **An:** Codex (Lead).
**Zweig:** `claude/drizzle-apply-guard-20261026`, gestapelt auf PR #45.
**QA:** [drizzle-apply-guard-20261026.md](../../quality-assurance/drizzle-apply-guard-20261026.md).

## Fuer Codex relevant

- Kein Push-Altbestand gefunden; das reale Risiko ist der `DATABASE_URL`-Rueckfall auf die
  Backend-Hauptdatenbank in neun drizzle.config.ts.
- `migrate:apply` laeuft jetzt ueber `scripts/drizzle_apply_guard.cjs`; `migrate:check`
  prueft nur. Direkte `drizzle-kit migrate`/`push`-Aufrufe umgehen den Waechter.

## Offen

- Laufzeitverbindungen der Dienste fallen ebenfalls auf `DATABASE_URL` zurueck
  (analytics, audit, document, notifications, pricing, quality, regulatory, weighing);
  eigener Slice, falls die Dienste je betrieben werden.
