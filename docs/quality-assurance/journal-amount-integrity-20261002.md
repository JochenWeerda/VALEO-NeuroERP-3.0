---
title: Exakte Journalbetraege ohne Scheinbuchungen
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-02
version: 1.0.0
---

# Exakte Journalbetraege ohne Scheinbuchungen

## Vertrag und Implementierung

FinanceTransactionService verlangt mindestens zwei Journalzeilen mit beiden
kanonischen debit_amount/credit_amount-Feldern. Pro Zeile ist genau eine Seite
positiv. Betraege muessen endlich, nichtnegativ, exakt in Cent und innerhalb
NUMERIC(15,2) sein; auch die positiven ausgeglichenen Kopfsummen muessen passen.
Leere/Nullbetragsjournale, NaN/Infinity, negative Werte, Subcent, Overflow,
fehlende Felder und konkurrierende debit/credit/debitAmount/creditAmount-
Payloads werden vor jedem Datenbankzugriff abgewiesen. Keine implizite Null
oder Rundung. Wertgleiche Dezimaldarstellungen werden auf zwei Stellen
normalisiert; negative Null wird zur kanonischen positiven Null auf der
unbebuchten Seite. Konstante Grenzen und lineare Summenpruefung.

Post und Reverse pruefen die tatsaechlich gespeicherten Journalzeilen erneut:
Tenant, exakte Betragsfelder, Uebereinstimmung der physischen debit/credit-
Dubletten mit debit_amount/credit_amount, positive einseitige Buchung,
Kopfsummen und mandantengebundene buchbare Konto-IDs. Erst danach Status,
Stornoobjekt oder Schreibzugriffe erzeugen. Betragsdubletten sind damit
bewacht, aber noch nicht aus dem Schema entfernt.

Der Produktionsabschluss erzeugte Nullbetrags-GL-Platzhalter ohne
Bewertungsmodell. Der komplette Buchungshelfer und seine festen Konten/
Scheinzeilen sind entfernt. Der einzige bestehende Verbraucher meldet jetzt
fehlende Bewertung ausdruecklich ueber Log und vorhandene Fehlermetrik.
Operative Fertigwaren-Charge kann entstehen; fibu_journal_ref bleibt ohne
wirklichen Beleg leer. Kein behaupteter Nachbuchungsweg als Rueckfall und
kein Kompatibilitaetsstub unter dem alten Buchungsnamen.

## Verifikation

231 Tests bestanden (8.74 Sekunden): 46 neue Betrags-/Lifecycle-Vertraege,
davon 18 echte PostgreSQL-Faelle. Stored NaN, Null/negative Werte, falsche
Aliasbetraege, Kopf-/Zeilenwiderspruch, Fremdtenant und inaktives Konto
verhindern Post/Reverse ohne Statuswechsel oder zweiten Journalbeleg.
Gueltige Journale lassen sich tatsaechlich buchen und mit zwei realen
Stornozeilen spiegeln. Ungueltige Create-Payloads fuehren weder SQL noch
Add/Flush/Commit aus; Produktionsguard erzeugt keinen Journalservice/Beleg.
Bestehende Journal-/Posting-/Konto-/Stempel-, CRM-/Storno-/Agrar-/Harvest-
und Procurement-Vertraege bestanden. Ruff der sieben geaenderten Python-
Dateien bestanden. Lokaler Log: artifacts/journal-amount-tests.log.

Vorhandener valeo_probe, aktuelle Revision eudr_uebermittlung_20261001.
Nur eigene kleine Tabellenkopien fuer den realen ORM-/SQL-Lifecycle und
gezieltes Schema-Cleanup, keine neue DB/Dockerinstanz oder gemeinsame
Migration/Ruecksetzung. Die Tests verwenden echte NUMERIC-Spalten aus
vorhandenen Journal-/CoA-Tabellen. Kein Testschreiben in Entwicklungstabellen.

## Grenzen und offene Integration

Keine Produktionsbewertung erfunden: Preis-/Bestandsbewertungsmodell und
Verbuchung bewerteter Verbraeuche sind weiter offen. Andere Journal-Schreiber
nutzen den Betragsvertrag noch nicht zentral. Consumer-Atomizitaet,
konkurrierende Lifecycle-Uebergaenge, vollstaendiger Hash-Payload, Draft-Delete,
Betragsdubletten/Komposit-Tenant-FKs im Schema und Bankmigration bleiben
Folgearbeit. Keine Projekt-/GoBD-/Betriebs-Gesamtabnahme. Handbuch-Drift im
parallelen Worktree bleibt dem vorhandenen Besitzer zugeordnet. Minor-Fix
im vorhandenen Service, keine neue Route/DTO/Maske oder Fachfunktionalitaet.
