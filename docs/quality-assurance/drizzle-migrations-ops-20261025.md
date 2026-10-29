---
title: Drizzle-Migrationen und Betriebsfaehigkeit (2026-10-25/26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Drizzle-Migrationen und Betriebsfaehigkeit (2026-10-25/26)

Slice `DRIZZLE-MIGRATIONS-OPS-20261025`, Zweig `claude/drizzle-migrations-ops-20261025`,
PR gegen `codex/migration-parity-repair-20261022` (Basis zuletzt `5ee0c882c`). Der Zweig
enthaelt die offenen Vorstufen PR #42 (drizzle-kit 0.31) und PR #43 (scheduler-Schema;
von Codex in `5ee0c882c` bereits uebernommen).

## 1. audit, document, notifications: Migrationskette

**Ursache:** Die Paket-`.gitignore` schlossen `migrations/*.sql` aus. Die Journale
verwiesen auf `0000_lying_greymalkin`, `0000_curved_thaddeus_ross`, `0000_right_king_bedlam`;
eingecheckt waren nur Snapshot und Journal. Die SQL lag in keinem Commit (`git log --all`).

**Massnahme:** Ignore-Regel entfernt. SQL mit drizzle-kit 0.31.11 aus dem Schema erzeugt
(in ein Scratch-Verzeichnis) und unter dem jeweiligen Journal-Tag abgelegt. Nachweis, dass
die Datei genau zum eingecheckten Stand gehoert: Der dabei erzeugte Snapshot ist mit dem
eingecheckten semantisch identisch (Tiefenvergleich; abweichend nur neue, leere
Formatfelder von 0.31 wie `policies`, `roles`, `sequences`). Eingecheckte Snapshot-IDs und
Journal bleiben unveraendert; keine Journalbereinigung. Neues Skript `migrate:apply`
(`drizzle-kit migrate`), bisher gab es nur `push`, das an der Kette vorbeiarbeitet.

| Pruefung | Ergebnis |
| --- | --- |
| `drizzle-kit check` im Paket | "Everything's fine" (alle drei) |
| `drizzle-kit generate` im Paket | "No schema changes" (alle drei), nichts geschrieben |
| `scripts/verify_drizzle_migrations_probe.cjs` auf valeo_probe | audit 8, document 10, notifications 15 Anweisungen; 2/3/4 Tabellen; Katalog = Snapshot, 0 Abweichungen |
| Negativprobe (manipulierte Kopie: Index entfernt, `integer`->`bigint`) | genau beide Abweichungen gemeldet, Exit 1 |
| `drizzle-kit migrate` (= `migrate:apply`) im eigenen Schema | angewendet, `__drizzle_migrations__` 1 Zeile |

Das Pruefskript spielt die Kette in **einer Transaktion** im Schema `drizzle_chain_check`
ein, vergleicht Spalten (Typ, NOT NULL, PK, Default) und Indizes (Spalten, unique) mit dem
letzten Snapshot und rollt immer zurueck; danach prueft es, dass das Schema nicht besteht.

## 2. RELEASE-RUNBOOK.md: Wiederherstellung

`npm run migrate:down` (Phase 5, Checkliste) gab es nie; drizzle-kit hat keine
Down-Migrationen. Ebenso existiert `migrate:gen --dry-run` nicht (Phase 2). Ersetzt durch:
Sicherung vor dem Release (`scripts/backup-db.sh`, Phase 1), Pre-Check mit
`drizzle-kit check`/`generate`, Rollback-Wege a) nur Anwendung (Expand/Contract),
b) Vorwaertskorrektur (`migrate:gen`, Probe, `migrate:apply`), c) Restore aus der Sicherung
(`scripts/restore-db.sh`). Vorhandene Wege geprueft: `backup-db.sh`/`restore-db.sh`
syntaktisch ok; `backup-restore-test.sh` legt eine eigene Datenbank an und wurde nach
Pruefstandsregel **nicht** ausgefuehrt; `check_restore_drill_evidence.py` meldet
`EXTERNAL_GATE` (kein Drill-Protokoll im Repo).

**Restore-Probe auf valeo_probe** (eigenes Schema `drizzle_restore_check`, im vorhandenen
Container `valeo-neuro-erp-postgres`, PostgreSQL 15.14):

1. Schema angelegt, Kette per `drizzle-kit migrate` angewendet (3 Tabellen inkl. Journal).
2. Zwei eigene Testzeilen (`tenant_id = 'restore-probe'`).
3. Sicherung im Format von `backup-db.sh` (`pg_dump --format=plain --no-owner --no-acl | gzip`), auf das Schema begrenzt.
4. Schaden: Schema geloescht (nachweislich weg).
5. Wiederherstellung `gunzip | psql --single-transaction`: beide Testzeilen und Journalzeile zurueck.
6. Erneutes `drizzle-kit migrate` wendet nichts doppelt an (Journal weiter 1), `check` ok.
7. Schema entfernt, Restkontrolle 0.

**Grenze:** `restore-db.sh` ersetzt eine ganze Datenbank (DROP/CREATE DATABASE). Das wurde
auf dem gemeinsamen Pruefstand bewusst nicht ausgefuehrt; geprueft ist derselbe
Mechanismus (plain dump -> psql) auf Schema-Ebene. Der 15-min-RTO-Drill gegen eine
produktionsnahe Umgebung bleibt Betriebsaufgabe.

## 3. analytics, scheduler: Seed-Einstiege

`db:seed` rief `tsx scripts/seed-database.ts` auf. Die Datei existiert in keinem Commit
beider Pakete; ausser dem Skripteintrag verweist nichts darauf (Doku, CI, Dockerfiles).
Befehl entfernt, keine Beispieldaten erfunden. (`db:reset` war bereits in PR #42 entfallen.)

## 4. hr: Indexnamen und Pruefstand-Test

- **Indexnamen:** `tenant_status_idx` (4 Tabellen), `tenant_employee_idx` und
  `employee_date_range_idx` (je 2) waren doppelt. Vorhandene Migration
  `20241004120000_create_time_entries.sql` benennt die `time_entries`-Indizes mit
  Tabellenpraefix; das Schema uebernimmt jetzt exakt diese Namen (Spaltenlisten identisch
  verglichen). Die uebrigen Duplikate tragen ihr Tabellenpraefix. `drizzle-kit generate`:
  7 Tabellen, keine Duplikatwarnung mehr.
- **Testcontainers ersetzt:** `tests/setup/testcontainers.ts` startete je Lauf einen
  Container und eine neue Datenbank; das Paket deklarierte `testcontainers` nicht (auf der
  Basis scheiterte die Datei schon am Import). Neu `tests/setup/probe-database.ts`: nur
  `TEST_DATABASE_URL` auf `valeo_probe`, eine Transaktion, eigenes Schema `hr_domain_it`,
  Savepoint je Testfall, Rollback am Ende. Keine neue Abhaengigkeit.
- **Testdaten:** Der Test schrieb `'tenant-default'`, `'id-…'` und `'system'` in
  UUID-Spalten; auf dem Pruefstand belegt: `invalid input syntax for type uuid`. Jetzt
  eigene UUID-Datensaetze (Mandant, Mitarbeiter, Akteur). Der unbenutzte Seed-Helfer mit
  denselben ungueltigen IDs ist entfernt.
- Auf valeo_probe: 2 Testdateien, 5/5 gruen; ohne `TEST_DATABASE_URL` bricht der
  Integrationstest mit klarer Meldung ab (kein stilles Ueberspringen).

## 5. scheduler: neun rote Tests

| Ursache | Faelle | Korrektur |
| --- | --- | --- |
| `calculateNextFireTime` war `async` ohne I/O; Aufrufer erhielten eine Promise statt `Date \| null` | 4 | synchron; `await` in Route entfernt (Dienstaufrufer unveraendert gueltig) |
| `executeEventTarget` schluckte Publish-Fehler; Ergebnis `success: false` ohne Grund | 1 | Fehler propagiert, `executeSchedule` meldet ihn und protokolliert den Feuerversuch weiter |
| Dienst-Tests bauten Schedules, die `ScheduleEntity` im Konstruktor ablehnt (Widerspruch zu den gruenen Entitaetstests bei identischer Eingabe) | 4 | Nutzerentscheidung: Entitaet bleibt Invariante. `validateScheduleInput` konstruiert und meldet Verletzungen als `valid: false`; die Validate-Route nutzt ihn; `validateSchedule` behaelt nur die Cron-Syntaxpruefung statt unerreichbarer Duplikate. Die vier Faelle laufen mit gleichen Eingaben und exakten Meldungen ueber diesen Weg; ein Positivfall ergaenzt |

Ergebnis: 34/34 (Basis 9 failed / 24 passed). Lint des Pakets ist auf der Basis kaputt
(`tsconfig.eslint.json` fehlt) und bleibt es.

## Abnahme gegen die exakte Basis

Basis `5ee0c882c` in einem temporaeren Worktree (gleiche `node_modules` per Junction,
keine Installation), beide Seiten ohne Datenbank gemessen; Worktree danach entfernt.

| Paket | tsc Basis / jetzt | Tests Basis | Tests jetzt | Schemaimport |
| --- | --- | --- | --- | --- |
| audit | 1 / 1 (identisch) | 3 passed | 3 passed | ok / ok |
| document | 1 / 1 (identisch) | 5 passed | 5 passed | ok / ok |
| notifications | 1 / 1 (identisch) | 3 passed | 3 passed | ok / ok |
| analytics | 28 / 28 (identisch) | 4 passed | 4 passed | ok / ok |
| scheduler | 11 / 11 (identisch) | 9 failed, 24 passed | **34 passed** | ok / ok |
| hr | 1 / 1 (identisch) | 4 passed, Integrationsdatei rot (`Cannot find package 'testcontainers'`) | 4 passed, Integrationsdatei bricht ohne `TEST_DATABASE_URL` mit klarer Meldung ab; **auf valeo_probe 5/5** | ok / ok |

Offline-Generierung: `drizzle-kit generate` meldet fuer audit/document/notifications "No
schema changes", fuer hr 7 Tabellen ohne Duplikatwarnung (Basis: Warnung zu doppelten
Indexnamen). Restabweichung: keine neue; die vorbestehenden Typfehler (siehe Zahlen) sind
unveraendert und nicht Teil des Auftrags.

## Pruefstand-Nutzung

Nutzerfreigabe des Wartungsfensters am 2026-10-26. Vorher und nachher
`pruefstand_db.py --status`: vorhanden, Revision `loading_stop_fk_20261023`, keine fremde
Sitzung. Genutzte Schemata `drizzle_chain_check`, `hr_domain_it` (nur in Transaktionen mit
Rollback) und `drizzle_restore_check` (kurzzeitig festgeschrieben, entfernt). Restkontrolle:
0 dieser Schemata und kein Schema `drizzle`. Kein Reset, keine neue Datenbank, kein neuer
Container. Zugangsdaten nur in der Prozessumgebung, nicht im Repository.

## Grenzen

- `restore-db.sh` (ganze Datenbank) und der RTO-Drill sind nicht ausgefuehrt (siehe 2).
- hr: Die handgeschriebene Migration nutzt `TIMESTAMPTZ` fuer `created_at`/`updated_at`,
  das Drizzle-Schema `timestamp` ohne Zeitzone; hr hat keine Drizzle-Kette, `out` zeigt auf
  denselben Ordner wie die Handmigration. Nicht Teil dieses Auftrags, offen.
- analytics, contracts, crm, pricing, quality, regulatory, scheduler und weighing haben weiter keine eingecheckte Migrationskette.
- Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.

## CI-Abnahme

| Lauf | Commit | Ergebnis |
| --- | --- | --- |
| Quality Gate 40273248149 | 14a8503f9 | Dependency Scan, Improvement integrity, FSX, Secret Scan, SBOM, WCAG, Production contract u. a. success; Frontend-Unit 214 Faelle mit identischer Fallmenge wie Basis-Lauf 40234161888 (`5ee0c882c`, 0 neu); Doc-Drift 272 wie Basis |
| Security Scan 40273251199 | 14a8503f9 | Erstlauf: Trivy brach ab, weil die Schwachstellendatenbank nicht ladbar war (`mirror.gcr.io … 404`, kein Befund); als Scannerausfall blockierend gewertet und neu gestartet. Neulauf: alle Jobs success |
