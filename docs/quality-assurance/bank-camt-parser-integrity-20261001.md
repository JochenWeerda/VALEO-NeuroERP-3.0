# CAMT: gebuchte Salden und eindeutige Einzelzahlungen

Stand 2026-10-01. Slice BANK-CAMT-PARSER-INTEGRITY-20261001,
Claim 5aaa05e54. Nachzug des bestehenden Kontoauszugsimports.

## Fehler und Vertrag

Der Parser benutzte den ersten XML-Saldo als Anfangssaldo, ignorierte dessen
Vorzeichen und berechnete einen Endsaldo statt den Bankwert zu pruefen.
Fehlende Buchungsdaten wurden durch heute ersetzt. Unbekannte Richtung,
ungebuchte/reversierte Eintraege und mehrere Transaktionen in einer Buchung
konnten wie eine einzelne Zahlung verarbeitet werden. Verschachtelte Werte
ersetzten fehlende direkte Felder; Gegenkonto-IBAN und weitere Referenztexte
gingen verloren. 17 gezielte Parservertraege scheiterten vor der Reparatur:
artifacts/camt-before.log.

Feldreferenz: [BIL CAMT.053.001.02, 08.08.2023](https://www.bil.com/BIL-digital/assets/doc/BIL_CAMT053_V2_final.pdf).
OPBD und CLBD sind die gebuchten Anfangs-/Endsalden; BOOK bezeichnet gebuchte
Eintraege. Related Parties enthaelt getrennte Gegenparteien und Gegenkonten.
Die Implementierung bildet ein begrenztes Profil, keine vollstaendige
XSD-/Bankzertifizierung.

Genau ein kanonischer Document/BkToCstmrStmt/Stmt mit IBAN. OPBD und CLBD
je einmal, mit Richtung, Waehrung und Datum; andere Saldoarten beeinflussen
die Auswahl nicht. Anfangssaldo plus alle Eintraege muss dem angegebenen
Endsaldo exakt entsprechen. Buchungsdatum liegt im Saldozeitraum;
Valutadatum wird separat erhalten. Date/DateTime werden explizit gelesen,
DateTime behaelt das gemeldete Kalenderdatum ohne Zeitzonenverschiebung.
Fehlende Daten werden nicht angenommen. Direkte Pfade und eindeutige
Zwischenelemente verhindern widerspruechliche Ersatzwerte.

Nur BOOK mit gueltigem CRDT/DBIT und ohne Reversal. Maximal eine TxDtls
je Entry; Sammel-/Batch-, FX- und Return-Details erfordern eigene Vertraege
und werden abgelehnt. Vorhandenes TxAmt muss Entrybetrag und Waehrung exakt
entsprechen. Alle unstrukturierten Texte und strukturierten Referenzen bleiben
erhalten; Gegenkonto-IBAN wird aus CdtrAcct/DbtrAcct gelesen. Eintragsreferenz
hat Vorrang vor Transaktionsreferenz; sie ist kein neu behaupteter Nachweis
semantischer Datei-Eindeutigkeit. Der bestehende sichere Matchingvertrag
entscheidet weiter ueber volle Referenz, Mehrdeutigkeit und Teilzahlung.

Betragslexik erlaubt unsigned endliche Centwerte. Vorzeichen kommt allein
aus CRDT/DBIT; NUMERIC(15,2)-Speichergrenze wird vor Writes geprueft. Erstimport
und Replay verwenden dieselbe Centdarstellung. Auch leere CAMT-Auszüge
muessen die gespeicherte Kontowaehrung tragen. Striktes UTF-8/BOM-Profil;
DTD-/Entity-Deklarationen werden vor XML-Verarbeitung abgelehnt.

## Abnahme und Betrieb

Finaler gemeinsamer Parser-/Finanz-/DQ-Lauf: **134 bestanden** (28,25 s),
davon 32 neue CAMT-Vertraege und 102 bestehende MT940-/Finanz-/DQ-Vertraege.
artifacts/camt-final-tests.log. Slice-CLI vollstaendig gruen.
Der erste Nachzug hatte 121 bestandene Tests
und einen Replay-Darstellungsfehler (0/25 gegen 0.00/25.00). Dieser wurde im
Code durch Centnormalisierung behoben, nicht durch Abschwaechung der Abnahme.

Vorhandenes valeo_probe, beim Start Revision kontraktregister_20261001,
eigene isolierte Tenant-/Kontodatensaetze und gezielte Bereinigung.
Keine weitere Datenbank/Dockerinstanz, keine Migration und kein Reset.
Replay-Fixture liefert jetzt echte BOOK-/OPBD-/CLBD-Daten statt unvollstaendiger
CAMT-Beispiele. CSV und MT940 behalten ihre bestehenden Vertraege.

## Grenzen und Integration

Weitere CAMT-Versionen, fehlende bankfachliche Daten, nationale Kontonummern,
Sammleraufloesung, FX, Retouren und GL-Rueckbuchung erfordern gesonderte
Abnahme. Historische UUID-Importe und semantische Datei-Duplikate bleiben offen.
Andere Bankimport-Routen sind nicht mit diesem Parser automatisch zertifiziert.
Die Regeln gelten fuer den hier beanspruchten Bankstatement-Import.

Ruff, Handbuch, Pagination und Baseline-Integritaet gegen den Claim gruen.
CRM-Strukturabbau ist im parallelen Stand nachgezogen, Groessenratsche gruen;
keine fremden Dateien oder Baselines uebernommen. GitHub-CI, Bankprofil- und
Deployment-Abnahme bleiben extern.
