---
title: Batch 8 - Schutz vor Verlust von Altbestand
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-05
version: 1.1.0
description: Seed-Signaturen, konservative Datenbereinigung und PostgreSQL-Abnahme fuer Batch 8.
---

# Batch 8: Schutz vor Verlust von Altbestand

Die Seed-Signaturen stammen aus den `_seed`-Funktionen im Git-Vorgaenger von `f8bbdac5c`. Foerder- und Labor-Seeds werden nur bei vollstaendiger Geschaeftssignatur entfernt; doppelte Foerdernummern, bereits vorhandene Mandanten oder vorhandene Befundspalten verhindern die entsprechende Bereinigung.

Die spaetere Nutzerentscheidung vom 04.11.2026 lautet: "vorhandene zeilen sin nur testdaten. tabelle kann entfernt werden, wenn nicht mehr passend". Deshalb darf die durch CRM ersetzte Marketingtabelle auch mit vorhandenen Testzeilen entfallen. Der Hauptanwendungsweg und seine Verbraucher wurden bereits in #102 auf CRM umgestellt. DROP verwendet kein CASCADE; verbliebene Datenbankabhaengigkeiten verhindern die Entfernung. Die vorherige Abbruchpflicht bei Nicht-Seed-Zeilen dieser ausgemusterten Tabelle ist damit ersetzt.

Die weiter verwendeten Foerder- und Labortabellen bleiben erhalten. Deren Testauftraege und Befunde ohne vollstaendige Signatur folgen weiterhin der vorhandenen Altbestand-Mandantenregel.

Die gezielten Migrationstests verwenden ausschliesslich temporaere PostgreSQL-Tabellen innerhalb einer zurueckgerollten Transaktion im konfigurierten gemeinsamen Pruefstand. Abnahme 04.11.2026: `pytest tests/test_batch8_seed_schutz.py --noconftest -o addopts= -q` mit `valeo_agent`: 2 bestanden. `pruefstand_db.py --status` davor und danach: Revision `ruestlisten_tabelle_20261103`. Temporäre Tabellen liegen in einer Transaktion, die auch bei Fehlern zurückgerollt wird. Der erste Lauf mit den globalen Fixtures wurde nach längerem Warten abgebrochen.

Dieser erste Nachweis betrifft den Stand vor der neuen Nutzerentscheidung. Der Nachlauf vom 05.11.2026 besteht: zwei Batch-8-Faelle und ein Batch-9-Fall wurden gemeinsam sequentiell mit deaktiviertem Plugin-Autoload, `--noconftest -p no:cacheprovider -o addopts= -q` ausgefuehrt: **3 passed**, Exit 0. Der angepasste Marketingtest entfernt eine belegte Alttabelle und stellt ihre beiden Zeilen durch Savepoint-Rollback wieder her. PostgreSQL-Rolle: `valeo_agent`; Revision vor/nach dem Lauf `ruestlisten_tabelle_20261103`, fremde Clients jeweils 0. Alle DDL-/Datenaenderungen lagen in zurueckgerollten Transaktionen; kein Reset oder Migrationsstempel.
