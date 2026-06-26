---
title: Administration & Betrieb
type: explanation
audience: [tenant-admin, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# Administration & Betrieb

Zweigeteilt nach Verantwortung: Mandanten-Administration (fachlich) und
System-/Betriebsführung (technisch).

## Mandanten-Admin

- [Mandanten-Administration](mandanten-administration.md) — Überblick & Aufgaben.
- [Module & Feature-Flags](module-und-feature-flags.md) — `INSTALLED_MODULES`, `TENANT_MODULE_FLAGS`.
- [RBAC & Rollen](rbac-und-rollen.md) — Authentifizierung, Scopes, Least Privilege.

## Betrieb / System-Admin

- [Deployment](deployment.md) — Docker Compose, Env-Variablen, Secrets.
- [Backup & Restore](backup-restore.md) — Datensicherung, Restore-Tests.
- [Datenbank-Migrationen](datenbank-migrationen.md) — Alembic, Single-Head.
- [Migrations-Inventar](migration-inventory.md) — Alembic-Skripte (generiert).
- [Monitoring & SLO](monitoring-und-slo.md) — Prometheus, Health-Checks, Logging.
- [Incident-Response](incident-response.md) — Störungen, Eskalation, Post-Mortem.
- [Skalierung & Performance](skalierung-performance.md) — Worker, ASGI, Lasttests.
