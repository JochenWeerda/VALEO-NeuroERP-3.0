---
title: Datenbank-Governance (DDL-Protokoll, Herkunft, Drift, Rollen)
type: explanation
audience: [entwickler, betrieb, agent]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Datenbank-Governance

Schemaaenderungen kommen in VALEO aus mehreren Werkzeugen: Alembic (Python-Backend),
drizzle-kit (TS-Domaenen), `create_all` der ORM-Metadaten in `scripts/init_db.py`,
Agenten und Menschen mit `psql`. Bis 2026-10-26 war nur der Zustand pruefbar
(`scripts/check_schema_drift.py`), nicht der Weg dorthin. Diese Schicht macht beides
werkzeugunabhaengig sichtbar.

## Bausteine

| Ebene | Baustein | Wirkung |
| --- | --- | --- |
| Erfassen | Migration `governance_ddl_log_20261026`: Event-Trigger `ddl_command_end` und `sql_drop` schreiben nach `governance.ddl_events` | Jede Schemaaenderung jeder Herkunft, mit Rolle, `application_name`, abgeleiteter Quelle, Transaktion; ohne Anweisungstext (kann Geheimnisse enthalten); temporaere Objekte ausgenommen |
| Kennzeichnen | Alembic (`alembic/env.py`), drizzle-Waechter (`PGAPPNAME=drizzle-kit:<paket>`), `init_db.py` (`orm-create-all`), Agenten (`PGAPPNAME=agent:<name>`, AGENTS.md) | Quelle `alembic`, `drizzle-kit`, `orm-create-all`, `agent`, sonst `unbekannt` |
| Auswerten | `scripts/check_ddl_provenance.py` | Exit 2 ohne Protokoll/Trigger, Exit 1 bei Aenderungen aus nicht erlaubten Quellen; CI-Schritt nach `init_db.py` mit `--erlaubt alembic orm-create-all` |
| Abgleichen | `check_schema_drift.py` (Alembic-Domaenen), `pnpm --filter <paket> run migrate:drift` (Drizzle-Domaene gegen Snapshot, nur lesend) | Zustand gegen den Migrationsstand, unabhaengig davon, ob das Protokoll lief |
| Schuetzen | `migrate:apply`/`migrate:check` (drizzle-Waechter) | Kein Drizzle-Lauf gegen fremde Ziele oder Altbestand ohne Journal |

## Grenzen der heutigen Stufe

- **Herkunft ist deklariert, nicht bewiesen.** `application_name` setzt der Client. Alle
  Werkzeuge und Agenten verbinden sich mit derselben Rolle (`valeo_dev`), deshalb kann sich
  jede Sitzung als `alembic` ausgeben. Das Protokoll zeigt also, was angekuendigt wurde, und
  zuverlaessig, *dass* etwas geaendert wurde.
- **Event-Trigger brauchen Superuser.** Ohne diese Rechte legt die Migration Tabelle und
  Funktionen an, aber keine Trigger; `check_ddl_provenance.py` meldet das mit Exit 2.
- **Fail-open:** Scheitert der Protokolleintrag, laeuft die Schemaaenderung mit WARNING
  weiter. Eine blockierte Migration waere im Betrieb schlimmer als eine Luecke, die der
  Abgleich ohnehin findet.
- Nicht erfasst werden gemeinsame Objekte (Rollen, Datenbanken, Tablespaces); dafuer
  gibt es in PostgreSQL keine Event-Trigger.
- Drizzle-Domaenendatenbanken bekommen das Protokoll erst, wenn dieselbe Definition dort
  installiert wird (heute existiert keine solche Datenbank, siehe
  [drizzle-apply-guard-20261026.md](../quality-assurance/drizzle-apply-guard-20261026.md)).
- Die Laufzeitwege der Anwendung werden nicht gesperrt; das leistet erst die Rollentrennung.

## Stufe 3: Rollentrennung (Werkzeuge umgesetzt, Einfuehrung gestaffelt)

Entscheidungen nach Best Practice (Nutzerauftrag 2026-10-26); der Superuser bleibt fuer
Entwicklung, Einrichtung und Anpassungen.

| Rolle | Rechte | Nutzer |
| --- | --- | --- |
| `valeo_owner` (NOLOGIN) | Eigentuemer der Fachschemata und -objekte; INSERT ins Protokoll | niemand direkt |
| `valeo_migrator` | Mitglied von `valeo_owner`, Rollenvorgabe `role = valeo_owner` | Alembic, drizzle-kit, `init_db.py` |
| `valeo_app` | DML auf allen Fachtabellen, Sequenzen, Funktionen; kein CREATE | FastAPI, Domaenendienste |
| `valeo_agent` | wie `valeo_app`; DDL nur ueber `valeo_migrator` im Wartungsfenster | Agenten |
| `valeo_audit` | nur `SELECT` auf `governance.ddl_events` | Pruefungen, Betrieb |
| `valeo_governance` (NOLOGIN) | Eigentuemer des Protokolls | niemand direkt |
| Superuser (`valeo_dev`) | unveraendert | Einrichtung, Anpassungen, Entwicklung |

Umsetzung:

- `scripts/provision_db_roles.py`: Rollen clusterweit und idempotent (Rollen sind
  Cluster-Objekte und gehoeren nicht in Migrationen), Rechte und Default Privileges je
  Datenbank, `--eigentum` uebertraegt Fachobjekte gezielt per `ALTER … OWNER`
  (`REASSIGN OWNED` scheidet aus: Bootstrap-Superuser, und es verschoebe ganze Datenbanken).
  Ohne `--anwenden` nur Plan, `--rollback` als Probelauf. Passwoerter nur aus
  `VALEO_DB_PASSWORD_{MIGRATOR,APP,AGENT,AUDIT}`, nie im Repository oder in Ausgaben.
- `app/core/migration_session.py`: Alembic und `init_db.py` lesen `MIGRATION_DATABASE_URL`
  (Rueckfall `DATABASE_URL`), markieren ihre Sitzung und handeln als `valeo_owner`, sobald
  die Rolle existiert, damit neue Objekte nie einer Login-Rolle gehoeren.
- Migration `governance_ddl_log_roles_20261026`: Protokoll fuer PUBLIC geschlossen;
  temporaere Objekte von Rollen ohne Protokollrecht loesen keinen Schreibversuch aus.
  Die Trigger-Anlage prueft die Login-Rolle und legt die Trigger mit `RESET ROLE` an.
- `check_ddl_provenance.py`: Mit eingerichteten Rollen entscheidet die handelnde Rolle;
  Superuser-DDL ist Hinweis (`--ohne-superuser`: Befund), eine Werkzeugquelle ohne
  Migratorrolle gilt als vorgetaeuscht.
- `create_tables()` beim Anwendungsstart prueft unter `valeo_app` nur noch; fehlende
  Tabellen entstehen ueber Migrationen bzw. `init_db.py`.

Einfuehrung (je Datenbank, als Superuser, im abgestimmten Fenster):

1. `python scripts/provision_db_roles.py --url … --anwenden` (Rollen, Rechte; additiv).
2. `… --anwenden --eigentum` (Eigentum an `valeo_owner`).
3. Passwoerter setzen (Umgebung), `MIGRATION_DATABASE_URL` auf `valeo_migrator`,
   `DATABASE_URL` der Anwendung auf `valeo_app`, Agenten auf `valeo_agent`.
4. `check_ddl_provenance.py` regelmaessig; nach Abschluss der Entwicklungsphase
   `--ohne-superuser`.

Stand 2026-10-26 ([Einfuehrung](../quality-assurance/db-roles-rollout-20261026.md)):
`valeo_neuro_erp` hat Schritte 1-2 hinter sich (Rollen, Rechte, Eigentum), die Zugangsdaten
stehen in der Root-`.env`. Schritt 3 fuer das Backend ist blockiert, bis die Laufzeit-DDL
einiger Endpunkte in Migrationen ueberfuehrt ist. Der Rollenwechsel auf `valeo_owner`
erfolgt nur in Datenbanken, in denen `valeo_owner` `CREATE` hat; frische Datenbanken
migriert die Login-Rolle, die Einrichtung uebertraegt danach. Quellen im Protokoll
zusaetzlich: `provisionierung` (Einrichtungsskript).

Grenzen: Ein Superuser kann alles, auch das Protokoll aendern; das ist die bewusste
Entscheidung fuer die Entwicklungsphase. Rollen gelten clusterweit; Rechte wirken erst in
den Datenbanken, in denen Schritt 1 lief.
