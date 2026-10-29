---
title: Handshake Drizzle-Migrationen und Betriebsfaehigkeit 2026-10-26
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-26
---

# Handshake: Drizzle-Migrationen und Betriebsfaehigkeit

**Von:** Claude Code. **An:** Codex (Lead).
**Zweig:** `claude/drizzle-migrations-ops-20261025`, PR gegen `codex/migration-parity-repair-20261022`.
**QA:** [drizzle-migrations-ops-20261025.md](../../quality-assurance/drizzle-migrations-ops-20261025.md).

## Fuer Codex relevant

- Der Zweig enthaelt PR #42 (drizzle-kit 0.31) als Vorstufe; PR #43 hast du als `5ee0c882c`
  uebernommen, der Merge ist konfliktfrei. #42/#43 koennen nach diesem PR geschlossen werden.
- Review-Hashes: nur `lock_sha256` (node-forge, braces) auf das zusammengefuehrte Lockfile
  neu gebunden; `review_by` 2026-10-28 unveraendert, Wiedervorlage bei dir.
- Neue Werkzeuge: `scripts/verify_drizzle_migrations_probe.cjs` (Kette auf valeo_probe in
  einer Transaktion mit Rollback gegen den Snapshot), `migrate:apply` in audit/document/notifications.
- scheduler: `calculateNextFireTime` ist synchron; neuer Eingang `validateScheduleInput`
  (Nutzerentscheidung: `ScheduleEntity` bleibt Invariante). Validate-Route nutzt ihn.
- hr: Indexnamen geaendert (Schema), keine Migration betroffen; Integrationstest braucht
  `TEST_DATABASE_URL` auf valeo_probe.
- Keine Studio-, Inbox-, Adaptive-Workspace-, zentralen API-Vertrags- oder generierten Artefakte beruehrt.

## Offen

- RTO-Drill und Ganz-DB-Restore (`restore-db.sh`) gegen produktionsnahe Umgebung (Betrieb).
- hr: `TIMESTAMPTZ` in der Handmigration vs. `timestamp` im Schema; keine Drizzle-Kette.
- Migrationsketten fuer analytics, contracts, crm, pricing, quality, regulatory, scheduler, weighing.
- scheduler-Lint: `tsconfig.eslint.json` fehlt (vorbestehend).
