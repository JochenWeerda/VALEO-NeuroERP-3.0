---
title: Geschaeftstag und Mitternacht in neuen Fachdiensten
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: lokal_geprueft
last_reviewed: 2026-10-07
---

# Neue Fachdienste verwenden denselben Geschaeftstag

Quality `b2a63f451` scheiterte in der unabhaengigen Business-Time-Inventur:
je eine neue `date.today()`-Quelle in Einwilligung, Bewerbungs-Loeschlauf und
Schaden sowie zwei im Avis-Wareneingang. Diese fuenf Quellen verwenden jetzt
`app.core.business_time.business_today`; bestehende technische Zeitstempel
und Fachtransaktionen bleiben erhalten.

Die Fristpruefung der Einwilligung und die Anzeige ihres wirksamen Standes
folgen derselben konfigurierten Betriebszeitzone. Im Loeschlauf verwenden
Stichtag, Einwilligung und Loeschsperre denselben gebundenen Tageswert statt
unterschiedlicher Host-/Datenbanktage. Lauf und Protokoll teilen diesen Wert
auch bei einem Mitternachtswechsel. Beim Avis teilen alle Lagerbewegungen und
das tatsaechliche Lieferdatum einen einmal bestimmten Tag; ein Wareneingang
kann nicht zwei Buchungstage durch einen Zeitwechsel erhalten.

## Abnahme

- 209 Tests ohne Skip bestanden (41,58 s), einschliesslich realer gemeinsamer
  Probe-Vertraege fuer Einwilligung/Fassung, Loeschlauf, Schaden und Avis.
- 24 neue Grenzvertraege fuer Europe/Berlin und Pacific/Honolulu am selben
  UTC-Zeitpunkt vor Monatswechsel: Frist heute abgelaufen fuer Neuerteilen,
  Morgen und exakt 1095 Tage erlaubt, 1096 Tage abgewiesen; Schadenfrist am
  letzten Tag einschliesslich; vorhandener expliziter Retentionstag erhalten;
  SQL-Vergleiche gebunden und mandantenrein; Lauf-/Avis-Uhr nur einmal gelesen.
- Fuenf bestehende AST-Ratschenvertraege bestanden (0,55 s).
- Business-Time-Baseline ausschliesslich customers.py von drei auf zwei
  reduziert, weil eine Altstelle bereits entfernt war. Keine neue Ausnahme.
  Gate exakt 201 vorhandene Stellen in 112 Dateien.
- Alle neun unabhaengigen Improvement-Pruefungen im gemeinsamen Arbeitsbaum
  bestanden (24,53 s), Eingabesnapshot stabil: Toolchain, SQL-Bind-Casts,
  SQL-F-Strings, Geschaeftstag, Transaktionen, Pagination, Godfiles,
  Tenantklassifikation und Baselineintegritaet.
- Der erste Gesamt-Runner im Quellenarchiv bestand acht Checks, konnte seine
  Git-basierte Baselineintegritaet jedoch dort nicht belegen: Git-Pfadprefix
  im Archivverzeichnis. Im echten Repository separat und im stabilen Gesamt-
  Runner bestanden; kein Gate abgeschwaecht.
- Vor Integration vorhandener `valeo_probe` auf
  `mandant_finanz_crm_20261007` lesend bestaetigt. Eigene Testdaten;
  keine neue Datenbank/Container, kein Reset/Migration.

## Handshake und verbleibende Arbeit

Avis-Fachverbuchung, Mandantenregeln, Bestandssummen und bestehende Commits
bleiben im fremden Fachumfang unveraendert. Keine Produkt-API-/Maskenform
geaendert; OpenAPI-/Handbuch-Neuerzeugung dafuer nicht erforderlich.

Neuer GitHub-Nachweis bleibt erforderlich. Physischer Tabellenkatalog hat
weiterhin Drift und lokale WIP; die neue Kalenderabnahme schliesst ihn nicht.
Zwei Node-High-Befunde ohne Herstellerfix, 33 doppelte API-Gruppen und die
weiteren im Gesamtzielbericht benannten Reparaturen bleiben offen.
