---
title: Bank-Hauptbuchverbindung und Saldennachweis
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-02
version: 1.0.0
---

# Bank-Hauptbuchverbindung und Saldennachweis

## Gepruefter Code

Gespeicherte gl_account_id mit Tenant-FK/Check statt verlorenem alternativen
Kontonummernfeld. Keine automatischen Kontenplan-Eintraege. Beide CRUD-
Antworten und Templates typisiert; Reconcile und Summary identisch.
Decimal-Strings, null fuer fehlende Nachweise, berechnete Differenz und
is_balanced. 404 bei fremdem Konto/Tenant, 409 bei Datenwiderspruch, sichtbarer
500 bei Lesefehler ohne SQL-Leak. Kein Schreiben im Vergleich.

Eine SQL-Abfrage liest alle Vergleichsnachweise in einem MVCC-Snapshot.
Korrekte Journalkoepfe/-zeilen, Tenant, Waehrung und Stichtag; Differenzseite
begrenzt auf 100, Gesamtzahl separat. MATCHED ohne eigenen OP-Nachweis wird
nicht als zugeordnet akzeptiert. PARTIAL/Unknown und CSV_SYNTHETIC bleiben
ungeklaert. Finance-Run meldet bei INCOMPLETE keinen Abschluss.

Masken verwenden echte Bank-IDs, gemeinsame TS-Vertraege und explizite GL-
Auswahl. Keine fiktiven Standardkonten, kein Nullsaldo bei fehlenden Werten.
Lesefehler, Konto-/Tenantwechsel verwerfen alte Erfolgsanzeigen. Bankauskunft ergaenzt nur den lokalen Entwurf: updateData war ein Speicher-
Alias und wird hier durch setData ersetzt; keine automatische Anlage, keine
Endlosschleife und keine doppelten Auskunftstimer. Erstellmasken
laden/bearbeiten keinen nicht existierenden Datensatz mit ID new.

## Nachweise

55 Backend-Vertraege bestanden: 31 neue echte PostgreSQL-Faelle, acht
Direktbuchungs-Retirement-, acht Modell- und acht Finance-Actions-Vertraege.
Fuenf Maskentests bestanden, einschliesslich null und Lesefehler.
Ruff und ESLint der geaenderten Bankdateien bestanden; Typecheck zeigt nur
bestehendes CallWidget.tsx:54 (string | undefined).
Business-Time-Baseline nur um die zwei entfernten eigenen date.today-Quellen
abgesenkt: 203 Stellen/113 Dateien. Agent-Handbuch-Check bestanden.
Architektur-Index um ADR-074/075 nachgezogen, strict-Gate bestanden
(932/259/448); globaler Snapshot-Refresh bleibt
beim vorhandenen Owner. OpenAPI nur eigene Bankpfade und benoetigte Schemas.
Lokale Nachweise: artifacts/bank-proof-full.log, bank-proof-frontend.log,
bank-proof-eslint.log und bank-proof-typecheck.log.

## Ressourcen und Integration

Vorhandener valeo_probe, keine neue Datenbank oder Dockerinstanz. Pro Modul
nur ein eigenes kleines bankproof_-Schema, aus den echten Tabellenstrukturen
abgeleitet; echte Migration darin ausgefuehrt. Eigene Zeilen und Schema werden
gezielt geloescht. Gemeinsame Tabellen, Alembic-Revision und fremde Daten bleiben
unveraendert. Kein Reset oder gemeinsame Migration.

Die Migration bank_gl_binding_20261001 folgt dem letzten committed Head
(eudr_sorgfaltserklaerung_20261001). Die parallel uncommitted EUDR-Kette ist
nicht als Voraussetzung erfunden. Stand 2026-10-02: zwei lokale Heads
(bank_gl_binding_20261001 und eudr_uebermittlung_20261001); der gemeinsame
valeo_probe steht auf eudr_uebermittlung_20261001, die Bankmigration ist dort
noch nicht angewendet. Gemeinsamer Merge-Head, Migration des
Pruefstands/Entwicklungsstandes und Betriebsprobe bleiben offen; dieser
Zwischenmeilenstein darf nicht als bereits integrierter Betrieb bezeichnet
werden. Erst EUDR-Commits/Claims erneut lesen und Merge koordinieren, dann
gezielt migrieren, GL-Verbindung auswaehlen und reale Betriebsprobe ausfuehren.

## Weitere belegte Gaps

FinanceTransactionService._resolve_account_id sucht weiterhin global mit
LIMIT 1. _stamp_gobd verschluckt Stempelfehler. Journalbetragsfelder sind noch
doppelt, chart_of_accounts.account_number ist global eindeutig. Bank-/Journal-
Zeilen haben keinen kanonischen gegenseitigen Beleglink; Saldenkohaerenz allein
loest das nicht. Bankstamm-Audit/RBAC und native Maskenkonvergenz bleiben
separate Abnahmen. Keine fachliche Gesamt-, CI- oder Produktionsfreigabe.
