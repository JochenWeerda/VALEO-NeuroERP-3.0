---
title: Handshake Datenbank-Governance 2026-10-26
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-26
---

# Handshake: Datenbank-Governance

**Von:** Claude Code. **An:** Codex (Lead).
**Zweig:** `claude/db-governance-20261026`, PR gegen `codex/migration-parity-repair-20261022`
(enthaelt #45 und #46). **QA:** [db-governance-20261026.md](../../quality-assurance/db-governance-20261026.md).
**Konzept:** [db-governance-20261026.md](../../architecture/db-governance-20261026.md).

## Fuer Codex relevant

- Neue Alembic-Migration `governance_ddl_log_20261026` ist der neue Head. Neue Migrationen
  bitte darauf aufsetzen. Auf valeo_probe ist sie **nicht** angewandt (bewusst, bis Merge).
- Ab Merge protokollieren Event-Trigger jede Schemaaenderung; Agenten setzen fuer direkte
  DB-Sitzungen `PGAPPNAME=agent:<name>` (AGENTS.md), sonst erscheinen sie als `unbekannt`.
- `alembic/env.py` setzt `application_name`; `scripts/init_db.py` setzt `PGAPPNAME`
  vor `create_all`.
- CI-Schritt "DDL provenance" nach `init_db.py`; greift erst, wenn der Doc-Drift-Gate gruen ist.

## Offen

- Stufe 3 Rollentrennung: Konzept, Freigabe durch den Nutzer ausstehend.
- Echter Upgrade-Lauf der Migration auf frischer DB (CI blockiert durch Doc-Drift 272).
