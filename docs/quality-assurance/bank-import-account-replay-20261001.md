# Bankimport: Kontobindung und Dateiwiederholung

Stand: 2026-10-01. Slice BANK-IMPORT-ACCOUNT-REPLAY-20261001;
Claim 2ef0ed2a3. Nachzug des gemeinsamen Bank-/Zahlungsabgleichs.

## Fehler und Vertrag

Beide Importwege akzeptierten unbekannte Bankkonten. Jeder erneute Upload
erzeugte einen neuen Auszug und damit erneut verfuegbare Zahlungszeilen.
Vor der Reparatur scheiterten sechs gezielte Konto-/Replay-Vertraege:
artifacts/bank-replay-before.log.

Beide Wege lesen jetzt dasselbe aktive Bankkonto im eigenen Header-Tenant
unter Transaktionssperre. Die gespeicherte IBAN muss gueltig sein. CAMT und
MT940 muessen eine passende IBAN liefern; CSV bezieht sie aus dem Konto.
Normalisierung entfernt Leerzeichen und vereinheitlicht Grossschreibung.
Alle Zeilen muessen die Kontowaehrung tragen; keine implizite FX-Umrechnung
oder Summierung verschiedener Waehrungen. CAMT-Entrywaehrung und MT940-
Saldowaehrung werden erhalten. CAMT erlaubt genau einen Auszug je Upload.

SHA-256 aus Tenant, Konto-ID, normalisiertem Format und Originalbytes ergibt
den bestehenden Auszugsschluessel. Eine PostgreSQL-Transaktionssperre wird
vor dem Nachschlagen genommen, auch wenn noch kein Auszug existiert. Der
Primaerschluessel sichert die Eindeutigkeit zusaetzlich. Beide CSV-Routen
verwenden denselben Vertrag. Kein neues Schema, Service oder Container.

Eine Wiederholung liefert die vorhandenen, aktuellen Zahlungszeilen und
den gespeicherten Zuordnungsstatus. Keine erneute Zuordnung oder Auditzeile,
auch wenn auto_match nachtraeglich aktiviert wird. Dafuer bleibt die explizite
Abgleichoperation zustaendig. Unvollstaendige gespeicherte Importe liefern
409 statt eines Erfolgs. Jeder Fehler nach Datenbankzugriff rollt zurueck;
ein fehlgeschlagener erster Commit bleibt ohne Fingerprint und wiederholbar.
Fruehe Datenqualitaetsfehler greifen weiterhin nicht auf die Datenbank zu.

CSV-Valutadatum wird auch im Zahlungsimport erhalten. Der synthetische
CSV-Schlusssaldo ist bei beiden Wegen die Summe der Zeilen ab null;
dies ist kein von der Bank nachgewiesener Anfangs-/Endsaldo.

## Abnahme und Betrieb

27 neue Konto-/Replay-Vertraege plus 30 Matching-, 12 Bankimport-, 10
Zahlungs-CSV- und 17 Zahlungslauf-Vertraege: **96 bestanden** (22,02 s).
artifacts/bank-replay-tests.log. Nachgewiesen sind echte parallele Uploads
ueber beide Routen, SQL-/Commitfehler, Fremdmandant, inaktives/unbekanntes
Konto, IBAN-/Waehrungsfehler, aktuelle Teilzahlungszuordnung ohne zweiten
Nachweis, unvollstaendige Daten und routenuebergreifendes Valutadatum.

Alle Datenbanktests verwenden vorhandenes valeo_probe mit eigenen Tenant-,
Konto- und Zahlungsdatensaetzen sowie gezielter Bereinigung. Keine weitere
Datenbank/Dockerinstanz, kein Reset und keine Migration. Regel gilt weiterhin
fuer alle Agenten. Sperren enden mit Commit/Rollback; unvollstaendige Importe
nicht durch wiederholtes Hochladen reparieren, sondern fachlich untersuchen.

Nach der Ergaenzung des Rollback-Guards: **47 bestanden** (29,08 s), davon
37 Replay-/CSV-Vertraege und zehn weitere bestehende DQ-/Ausfallvertraege.
artifacts/bank-replay-regression.log. Insgesamt 106 verschiedene Vertraege
bestanden. Die letzte Aenderung ist damit erneut abgedeckt.

Ruff, Whitespace, Baseline-Integritaet und Agent-Handbuch-Driftcheck bestanden.
Pagination ohne neuen Fund (286 Abfragen in 259 Funktionen). Slice-YAML,
Readiness und Doku-Governance bestanden. Der erste Slice-CLI-Aufruf fand
Ergebnisbeschreibungen unter tests und versuchte sie auszufuehren (WinError 2).
Im neuen und vorherigen Matching-Slice stehen jetzt ausfuehrbare Checks unter
tests, die bisherigen Abnahmeergebnisse getrennt unter test_evidence.
Beide vollstaendigen Slice-CLI-Pruefläufe bestanden anschliessend.
Projektweite Godfile-Ratsche war beim Lauf rot (1808 Zeilen). Der CRM-Owner hat `crm_360.py` danach unter 1.000 Zeilen zerlegt und die Listenabfrage auf 25 Zeilen begrenzt.
Keine Baseline angehoben. Der vorherige
Matching-Meilenstein ist als PR #18 integriert; GitHub-CI und Deployment
werden dadurch nicht pauschal als erfolgreich bewertet.

## Verbleibende Grenzen

Historische UUID-Importe besitzen keine Dateiidentitaet und werden nicht
nachtraeglich angenommen oder umgeschrieben. Gleiche Geschaeftsvorgaenge in
unterschiedlichen Datei-Bytes, Kontodubletten mit verschiedenen Konto-IDs
und formatuebergreifende Duplikate erfordern Bankreferenz-/Migrationsvertraege.
Der neue Schutz gilt fuer identische Bytes in Tenant/Konto/Format.

Weitergehende CAMT-/MT940-Abnahme (Saldoarten, Datumsregeln, Entrydetails),
Rueckbuchung, GL-Journalintegration und Legacy-PARTIAL ohne Verteilbetrag
bleiben offen. Importvolumen und Antwortumfang folgen weiterhin dem bestehenden
Importvertrag. Keine Behauptung, dass saemtliche Finanz- oder Projektgaps
geschlossen sind. Externe CI-/OpenAPI-/Deployment-Abnahme bleibt separat.
