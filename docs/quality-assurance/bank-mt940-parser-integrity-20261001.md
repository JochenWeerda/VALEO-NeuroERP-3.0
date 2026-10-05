# MT940: vollstaendige Zeilen und nachgewiesener Saldo

Stand 2026-10-01. Slice BANK-MT940-PARSER-INTEGRITY-20261001,
Claim 72e1f6ac0. Begrenzter Bugfix des vorhandenen Bankimport-Parsers.

## Fehler und Entscheidung

Der Parser las das optionale Buchungsdatum als sechs statt vier Stellen,
speicherte Zahlungszeilen erst bei :86: und verlor damit Zeilen ohne
Beschreibung. Sollsalden wurden positiv gelesen; der angegebene
Schlusssaldo wurde ignoriert und aus dem unvollstaendigen Bestand berechnet.
Sechs gezielte Vertraege scheiterten vor der Reparatur:
artifacts/mt940-before.log. Weitere ungueltige Eingaben wurden schon wegen
des falschen Datumsparsers abgewiesen; das bewies keine korrekte Verarbeitung.

Feldreferenz: [UniCredit MT940/MT942, V1.1](https://www.unicredit.ro/content/dam/cee2020-pws-ro/DocumentePDF/DocumenteCIB/MT94x_General_V1.1.pdf),
Felder 60a, 61, 86 und 62a. Das optionale MMDD-Buchungsdatum ist vom
YYMMDD-Valutadatum getrennt; :86: ist optional. Implementiert ist ein
begrenztes Profil, keine vollstaendige Bank-/SWIFT-Zertifizierung.

Jede :61:-Zeile wird sofort erhalten. Beschreibungen einschliesslich
Fortsetzungszeilen ergaenzen sie. Betragsgrammatik, Datum, Richtung,
Waehrung und Funds-Code werden geprueft; kein Weglassen defekter Zeichen
durch errors=ignore. Konto, Anfangs- und Endsaldo sind erforderlich und
nur einmal erlaubt. Salden tragen ihr C/D-Vorzeichen. Anfangssaldo plus
alle Zahlungszeilen muss dem angegebenen Endsaldo exakt entsprechen;
Saldo-Waehrung und Datumsfolge muessen konsistent sein. Jeder Parserfehler
verhindert alle Datenbankschreibvorgaenge.

Jahresregel als explizite Implementierungsentscheidung: MMDD wird zum
zeitlich naechsten Datum aus dem Valutajahr und dessen Nachbarjahren
aufgeloest; gleicher Abstand zu zwei Jahren oder mehr als 183 Tage Abstand
wird abgewiesen. YYMMDD verwendet
weiterhin die vorhandene Python-Jahresaufloesung. Keine Annahme eines
sechsstelligen Buchungsdatums, kein Ersatz durch heutiges Datum.

## Abnahme

19 neue Parser-/HTTP-Vertraege zusammen mit 79 bestehenden Import-, Replay-
und Matching-Vertraegen: **98 bestanden** (28,66 s),
artifacts/mt940-tests.log. Nachgewiesen sind fehlendes :86:, mehrere
Zeilen, vorzeichenrichtige Salden, optionale Buchungsdaten, Jahreswechsel,
Funds-Code/Waehrung, mehrzeilige Beschreibung, ungueltige Daten, Saldo-
Widerspruch, Mehrfachauszug, Wiederholung und Import ohne Teilwirkungen.

Nach dem zusaetzlichen Guard fuer zwei gleich nahe Jahre: **102 bestanden**
(37,72 s), davon 20 neue MT940-Vertraege, 79 bestehende Finanzvertraege und
drei bestehende DQ-Vertraege. artifacts/mt940-final-tests.log.
Slice-CLI, Ruff, Handbuch und Whitespace gruen; letzter Codezustand getestet.

Vorhandenes valeo_probe, Revision webhook_zustellprotokoll_20261001,
eigene Daten und gezielte Bereinigung. Keine weitere DB/Dockerinstanz,
keine Migration und kein Reset. Parservertraege selbst brauchen keine DB.

## Grenzen und Integration

RC/RD werden bis zur fachlichen Rueckbuchungsintegration ausdruecklich
abgelehnt. Nationale Kontokennungen statt IBAN, SWIFT-Umschlaege,
Supplementary-Details/Fortsetzungen ausserhalb :86: und unbekannte Felder
verlangen eigene Profile und Abnahme. Optionale Metadaten 20/21/28C/64/65
werden erkannt, aber nicht als bankfachlicher Identitaetsnachweis verwendet.
Semantische Duplikate und historische UUID-Dateiimporte bleiben offen.
CAMT-Saldoarten und Einzeltransaktionsdetails sind im Nachzug
[BANK-CAMT-PARSER-INTEGRITY](bank-camt-parser-integrity-20261001.md) fuer
das begrenzte Profil abgesichert; weitere Bankprofile bleiben offen.

Parallelstand: CRM-Owner baut die Godfile ab; Groessenratsche aktuell gruen.
Seine neue Pagination-Baselinezuordnung crm_360_sql::_query_many verletzt
aktuell die Baselineintegritaet gegen den Claim. Keine fremde Baseline
angepasst oder mit diesem Slice gestaged. GitHub-CI/Deployment bleiben extern.
