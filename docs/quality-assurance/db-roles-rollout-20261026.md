---
title: Einfuehrung der Datenbankrollen auf valeo_neuro_erp (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Einfuehrung der Datenbankrollen auf valeo_neuro_erp (2026-10-26)

Slice `DB-ROLES-ROLLOUT-20261026`, Zweig `claude/db-roles-20261026` (PR #48). Nutzerauftrag:
Einfuehrung uebernehmen, echte Anmeldung testen, echten `alembic upgrade` auf frischer DB
pruefen. Konzept: [db-governance-20261026.md](../architecture/db-governance-20261026.md).

## Durchgefuehrt auf valeo_neuro_erp

| Schritt | Ergebnis |
| --- | --- |
| Vorab | 96 MB, 5 Verbindungen ohne aktive Abfrage, Revision `loading_stop_fk_20261023` |
| Sicherung | `pg_dump --schema-only` (Eigentuemer und Rechte, 898 `OWNER TO`) und Rueckweg-Skript mit 899 `ALTER … OWNER TO valeo_dev` (beides nur im sitzungsgebundenen Scratch, nicht im Repository; Rueckweg siehe unten); keine Datensicherung noetig, Daten unberuehrt |
| `.env` (Root, gitignoriert) | gesichert; ergaenzt um `VALEO_DB_PASSWORD_{MIGRATOR,APP,AGENT,AUDIT}` (zufaellig, `secrets.token_urlsafe(32)`), `MIGRATION_DATABASE_URL`, `VALEO_{APP,AGENT,AUDIT}_DATABASE_URL`; `DATABASE_URL` unveraendert; Werte nirgends ausgegeben |
| 1 Rollen + Rechte | 6 Rollen; Login-Rollen mit Passwort; `valeo_migrator` mit `role = valeo_owner`; Nachtrag `CREATE ON DATABASE` fuer `valeo_owner` |
| 2 Eigentum | 879 Objekte an `valeo_owner` (815 Tabellen/Sichten/Sequenzen, 30 Schemata, Funktionen, Typen) mit `lock_timeout=5s`; Backend vorher und nachher `healthy`, HTTP 200 |

## Echte Anmeldungen (valeo_neuro_erp, Transaktionen mit Rollback)

| Rolle | Ergebnis |
| --- | --- |
| `valeo_migrator` | session `valeo_migrator`, current `valeo_owner`; SELECT, CREATE TABLE, Aenderung uebertragener Tabelle, neues Schema (Eigentuemer `valeo_owner`) |
| `valeo_app`, `valeo_agent` | SELECT/DELETE ok, temporaere Tabelle ok; CREATE TABLE, `CREATE SCHEMA IF NOT EXISTS` (vorhanden), COMMENT/ALTER verweigert |
| `valeo_audit` | Fachtabelle verweigert |
| `migration_engine` (init_db-Weg) | session `valeo_migrator`, current `valeo_owner`, `application_name` `orm-create-all` |
| `alembic current` ueber `MIGRATION_DATABASE_URL` | laeuft, Revision unveraendert |

0 Abweichungen von der Erwartung.

## Echter `alembic upgrade` auf frischer Datenbank (valeo_probe, Fenster)

Keine Claims und keine Sitzungen auf dem Pruefstand.

1. **Erstlauf scheiterte** (`permission denied for schema public`): Die Rollen gelten
   clusterweit; die frische Datenbank kannte `valeo_owner`, gab ihr aber keine Rechte, und
   die Migration wechselte trotzdem in die Rolle. Pruefstand sofort aus einem Basis-Worktree
   wiederhergestellt (Basis-Head, 767 Tabellen). Korrektur: Rollenwechsel nur, wenn
   `valeo_owner` in dieser Datenbank `CREATE` hat; dabei fehlendes `CREATE ON DATABASE`
   fuer `valeo_owner` im Einrichtungsskript ergaenzt.
2. **Zweitlauf** aus dem PR-Zweig: `pruefstand_db.py` (drop, create, `alembic upgrade head`)
   Exit 0, Head `governance_ddl_log_roles_20261026`, beide Trigger. `init_db.py` Exit 0;
   `create_all` legt 11 Tabellen ausserhalb der Migrationskette an (767 -> 778), im
   Protokoll als `orm-create-all` (46 Ereignisse). Eine unmarkierte Aenderung stammte aus
   `init_db._ensure_wide_version_table`; jetzt gekennzeichnet.
3. Einrichtung des frischen Pruefstands (`--anwenden --eigentum`), zweiter `init_db.py`-Lauf:
   2 Ereignisse `alembic/valeo_owner`, 791 Objekte `valeo_owner`, Protokoll `valeo_governance`.
4. Einrichtungslaeufe erschienen als `unbekannt`; neue Quelle `provisionierung`
   (Folgemigration), auf dem Pruefstand bestaetigt.
5. `check_ddl_provenance.py --erlaubt alembic orm-create-all`: Exit 0, Bewertung nach
   handelnder Rolle; Superuser-DDL als Hinweise.
6. `tests/test_db_roles_integration.py`, `tests/test_governance_ddl_log.py`: 2 passed.
7. Rueckbau aus Basis-Worktree: `loading_stop_fk_20261023`, 767 Tabellen, keine Trigger,
   kein `governance`, keine Sitzungen; Worktree entfernt.

## Nicht umgestellt: Backend auf `valeo_app` (Blocker)

Die Anwendung fuehrt zur Laufzeit DDL aus; PostgreSQL prueft das CREATE-Recht vor der
Existenz, also scheitert auch `CREATE … IF NOT EXISTS` auf Vorhandenes (belegt per Login).
Betroffen:

- `app/api/v1/endpoints/`: `accruals_provisions.py`, `compliance_whistleblower.py`,
  `ers_settlement.py`, `futtermittel_rezepte.py`, `futtermittel_rohwaren.py`,
  `opportunities.py` (ALTER ADD COLUMN), `price_lists.py`, `sales_delivery_notes.py`,
  `sales_orders.py`
- `app/api/v1/schemas/wf_cockpit_persist_schemas.py`, `app/services/geo_pipeline.py`,
  `app/services/lkv_pipeline.py`
- `app/core/database.py` (`create_tables`-Rueckfall beim Start)

Diese Laufzeit-DDL gehoert in Migrationen; erst danach `DATABASE_URL` des Backends
(`docker-compose.yml`, derzeit Codex-WIP) auf `valeo_app`. Bis dahin verbindet sich das
Backend weiter als Superuser; seine neuen Objekte erhalten ueber Default Privileges
trotzdem die Rechte fuer `valeo_app`/`valeo_agent`.

## Wirkung auf laufende Arbeit

- Codex migriert unveraendert als `valeo_dev` (Superuser, darf alles). Basis-Code liest
  `MIGRATION_DATABASE_URL` noch nicht; nach Merge von PR #48 migriert Alembic ueber
  `valeo_migrator`, sofern `DATABASE_URL` dieselbe Datenbank nennt.
- Rueckweg Eigentum: Vor der Uebertragung gehoerten alle 899 betroffenen Objekte `valeo_dev`
  (Sicherung und Skript lagen nur im sitzungsgebundenen Scratch-Verzeichnis). Der Rueckweg
  ist deshalb jederzeit exakt erzeugbar: alle Objekte mit Eigentuemer `valeo_owner` per
  `ALTER … OWNER TO valeo_dev` zuruecksetzen, z. B. mit den Katalogabfragen aus
  `scripts/provision_db_roles.py` (`_OBJECTS_SQL`) mit vertauschten Rollen.

Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.

## CI-Abnahme

| Lauf | Commit | Ergebnis |
| --- | --- | --- |
| Security Scan 40296881565 | c087b2402 | alle Jobs success |
| Quality Gate 40296874581 | c087b2402 | Improvement integrity, Dependency Scan, FSX, Secret Scan, SBOM, WCAG, Production contract u. a. success; Frontend-Unit 214 Faelle mit identischer Fallmenge wie Basis-Lauf 40234161888 (0 neu); Backend bricht wie auf der Basis am Doc-Drift-Gate (272) ab |
