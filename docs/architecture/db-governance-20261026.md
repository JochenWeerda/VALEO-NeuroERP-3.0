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

## Stufe 3: Rollentrennung (Konzept, nicht umgesetzt)

Erst getrennte Rollen machen die Herkunft belastbar und Aenderungen durchsetzbar.
Umsetzung nur nach Freigabe, weil sie Betrieb, Zugangsdaten und alle Verbindungen beruehrt.

| Rolle | Rechte | Nutzer |
| --- | --- | --- |
| `valeo_owner` (NOLOGIN) | Eigentuemer aller Schemata und Objekte | niemand direkt |
| `valeo_migrator` | `SET ROLE valeo_owner`; DDL | Alembic, drizzle-kit (je eigene Login-Rolle moeglich) |
| `valeo_app` | DML auf Fachtabellen, kein `CREATE`/`ALTER`/`DROP` | FastAPI, Domaenendienste |
| `valeo_agent_<name>` | wie `valeo_app` bzw. nur lesend; DDL nur ueber `valeo_migrator` im Wartungsfenster | Agenten |
| `valeo_audit` | nur `SELECT` auf `governance.*` | Pruefungen, Betrieb |

Dazu: `governance.ddl_events` nur fuer `valeo_owner` schreibbar (Trigger-Funktion
`SECURITY DEFINER`), fuer alle anderen kein `UPDATE`/`DELETE`; Event-Trigger einmalig
durch den Superuser. Offene Entscheidungen: Superuser-Zugriff im Betrieb, Verteilung der
Zugangsdaten (Secrets-Quelle), Uebergang der bestehenden Objekte (`REASSIGN OWNED`), Folgen
fuer `create_all` in `init_db.py` (braucht dann Migratorrechte oder entfaellt zugunsten
echter Migrationen).
