---
title: Datenbank-Governance Stufe 1-2 (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Datenbank-Governance Stufe 1-2 (2026-10-26)

Slice `DB-GOVERNANCE-20261026`, Zweig `claude/db-governance-20261026`, PR gegen
`codex/migration-parity-repair-20261022` (enthaelt die offenen PRs #45 und #46).
Konzept und Grenzen: [db-governance-20261026.md](../architecture/db-governance-20261026.md).

## Umfang

- Migration `governance_ddl_log_20261026` (Head nach `loading_stop_fk_20261023`, einziger
  Head): Schema `governance` (bewusst nicht `domain_*`, damit der Tabellenkatalog
  unberuehrt bleibt), `governance.ddl_events`, zwei Trigger-Funktionen, zwei Event-Trigger
  (nur mit Superuser; sonst WARNING und Exit 2 im Pruefskript), Downgrade entfernt alles.
- Kennzeichnung: `alembic/env.py` (`SET application_name = 'alembic'`), drizzle-Waechter
  (`PGAPPNAME=drizzle-kit:<paket>`), `scripts/init_db.py` (`PGAPPNAME=orm-create-all` vor
  `create_all`), AGENTS.md-Regel fuer Agenten (`PGAPPNAME=agent:<name>`).
- `scripts/check_ddl_provenance.py` + CI-Schritt nach `init_db.py`
  (`--erlaubt alembic orm-create-all`).
- `scripts/check_drizzle_drift.cjs`, je Drizzle-Paket `migrate:drift` (nur lesend,
  `SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY`).
- Rollentrennung: nur Konzept.

## Abnahme

| Pruefung | Ergebnis |
| --- | --- |
| `tests/test_check_ddl_provenance.py` (ohne DB) | 4/4 |
| `check_alembic_single_head.py` | Head `governance_ddl_log_20261026` |
| `migrate:drift` audit gegen `valeo_neuro_erp` (lesend) | Exit 2, kein Vergleich gegen fremdes Ziel |
| valeo_probe: `upgrade()` direkt, ohne `alembic_version` | Schema, Tabelle, Trigger `O` (aktiv); Revision unveraendert |
| Agent-Sitzung (`agent:claude-code`) | 3 Ereignisse, Quelle `agent` |
| unmarkierte `psql`-Sitzung | CREATE/DROP TABLE, Quelle `unbekannt` |
| `migrate:apply` audit in eigenem Schema | 15 Ereignisse, Quelle `drizzle-kit`, `application_name` `drizzle-kit:audit-domain` (inkl. Journal-Schema `drizzle`) |
| `check_ddl_provenance.py --erlaubt alembic drizzle-kit` | Exit 1, listet 3x agent und 2x unbekannt mit Zeit, Rolle, Objekt |
| gleicher Lauf mit allen Quellen erlaubt | Exit 0 |
| `alembic current` | `ALTER TABLE public.alembic_version` mit Quelle `alembic` (No-op aus env.py); Revision unveraendert |
| `tests/test_governance_ddl_log.py` auf valeo_probe | 1 passed (nicht uebersprungen): agent/unbekannt/temporaer korrekt; nach Rollback 0 Zeilen |
| `migrate:drift` frisch angewandtes Schema | "matches the snapshot", Exit 0 |
| nach Handaenderung (Spalte ergaenzt, Index entfernt) | genau 2 Abweichungen, Exit 1 |
| `downgrade()` | Trigger, Funktionen, Schema entfernt |

Pruefstand: Wartungsfenster vom Nutzer am 2026-10-26 freigegeben; vorher und nachher
Revision `loading_stop_fk_20261023`, keine fremde Sitzung, keine Event-Trigger;
Restkontrolle 0 (`governance`, `drizzle`, eigene Pruefschemata, Funktionen). Die Trigger
waren nur waehrend des Fensters aktiv; `alembic_version` wurde nie veraendert, damit der
gemeinsame Pruefstand keine Revision kennt, die auf der Basis fehlt.

## Nicht abgenommen

- **Echter `alembic upgrade` der neuen Migration** und die Kennzeichnung `orm-create-all`
  in `init_db.py`: Das braucht eine frische Datenbank. In CI liegt der neue Schritt nach
  `init_db.py`, der Backend-Job bricht aber vorher am vorbestehend roten Doc-Drift-Gate
  (272) ab; bis dieser gruen ist, laeuft dort weder die Migration noch der neue Gate.
- Event-Trigger ohne Superuser (Pfad nur per Code/Unit-Test abgedeckt).
- Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.

## CI-Abnahme

| Lauf | Commit | Ergebnis |
| --- | --- | --- |
| Security Scan 40286824850 | 2cc3545c5 | alle Jobs success |
| Quality Gate 40286821617 | 2cc3545c5 | Dependency Scan, Improvement integrity, FSX, Secret Scan, SBOM, WCAG, Production contract u. a. success; Frontend-Unit 214 Faelle mit identischer Fallmenge wie Basis-Lauf 40234161888 (0 neu); Backend bricht wie auf der Basis am Doc-Drift-Gate (272) ab, `init_db.py` und der neue Schritt "DDL provenance" laufen deshalb nicht |
