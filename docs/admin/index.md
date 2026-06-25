---
title: Administration & Betrieb
type: explanation
audience: [tenant-admin, betrieb]
owner: Cursor
status: entwurf
last_reviewed: 2026-06-25
version: 3.0.0
---

# Administration & Betrieb

Zweigeteilt nach Verantwortung: Mandanten-Administration (fachlich) und
System-/Betriebsführung (technisch).

## Mandanten-Admin

- Module & Feature-Flags (`INSTALLED_MODULES`, `TENANT_MODULE_FLAGS`).
- RBAC, Rollen, Berechtigungen.
- Nummernkreise, Stammdaten, Belegvorlagen, Übersetzungen.

## Betrieb / System-Admin

- Deployment (Docker Compose), Secrets-Handling.
- Backup & Restore, Alembic-Migrationen (Single-Head).
- Monitoring (Prometheus/SLO), Incident-Response.
- Skalierung (Worker, vgl. PERF-MULTIUSER-001), Production-Readiness-Gates.

> Inhalte folgen in `DOC-ADMIN-OPS-001`.
