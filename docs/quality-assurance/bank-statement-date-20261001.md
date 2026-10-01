---
title: Ein Auszugsstichtag statt Importdatum
type: reference
audience: [entwickler, agent, qa]
owner: Codex-01a0f3fc
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
---

# Bankauszugsdatum

## Nachgewiesener Widerspruch

CAMT und MT940 prueften datierte Anfangs-/Schlusssalden, verloren aber deren
Datum in der Parserantwort. Der Import schrieb date.today() in statement_date.
Der Zahlungs-CSV-Import schrieb den ersten Buchungstag, der Bank-CSV-Import
den Importtag. Dieselbe Datei konnte dadurch je Einstieg einen anderen
Saldenstichtag erhalten. Bankreconciliation konsumiert genau dieses Kopfdatum.

## Kanonischer Vertrag

CAMT/MT940: Datum des geprueften Schlusssaldos. MT940-Buchungstage muessen im
Intervall der beiden Saldodaten liegen. Auch ein leerer Auszug besitzt ein
Salden-Datum und eine Waehrung; die Kontowaehrungspruefung kann nicht mehr
durch fehlende Zeilen umgangen werden.

CSV: kein Banksaldonachweis, daher ausdruecklich synthetischer Stichtag
max(booking_date), unabhaengig von Dateireihenfolge und Valuta. Beide bestehenden
CSV-Routen speichern dasselbe Datum und dieselbe Dateiidentitaet. Leerer
Bank-CSV-Import liefert 422 ohne Header; der Payments-Leerimport bleibt ein
Nebenwirkungs-freier Leerlistenaufruf. Kein Ersatz durch heute.

prepare_statement_import verlangt den Stichtag explizit. Replay vergleicht ihn
mit dem gespeicherten Kopfdatum und liefert bei Widerspruch 409, ohne den
alten Kopf still umzuschreiben oder erneut zu matchen. Keine neuen API-Felder,
Module oder Schemaaenderungen.

## Verifikation

Red-Green: 11 von 13 neuen Anfangsvertraegen scheiterten vor Reparatur; reale
Fehldaten, verlorene Parserdaten, ausserhalb liegende Buchungstage und leere
Fremdwaehrung nachgewiesen. Zwei weitere Vertraege pruefen widerspruechliches
Replay fuer beide CSV-Einstiege. Gemeinsamer Lauf: **169 Tests bestanden**,
davon **15 neue**. Parser-, Import-, Replay-, Payment-Matching- und
Payment-Execution-Vertraege auf bestehendem valeo_probe; nur eigene Daten
gezielt aufgeraeumt, keine neue Datenbank/Dockerinstanz und kein Reset.
Logs: artifacts/bank-date-before.log, artifacts/bank-date-final-tests.log.

Ruff bestanden. Business-Time-Baseline senkt ausschliesslich zwei beseitigte
date.today-Quellen; keine neue Kalenderquelle oder Schwellenaufweichung.

## Offene Folgepunkte

Historische kanonische Kopfdatensaetze koennen das falsche Importdatum tragen;
sie sind nicht ohne Originalbankdatei auf ein Saldodatum rueckfuehrbar. Kein
stiller Rueckschluss aus dem letzten Buchungstag fuer echte Banksalden.
Entwicklungsaltlasten duerfen nach User-Freigabe entfernt werden, brauchen
aber eine zusammenhaengende Datenbereinigung bei bereits zugeordneten OPs.
Der Bank-Saldenvergleich selbst (Tenant, Kontobindung, echtes Hauptbuch und
keine angenommene Abstimmbarkeit) bleibt separater priorisierter Slice.
Inventory-Belegreferenzpaare sind zusaetzlich gefunden; aktuelle fremde
Inventory-WIP-Dateien werden nicht uebernommen. GitHub-CI/Deployment offen.
