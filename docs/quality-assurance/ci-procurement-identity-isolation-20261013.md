# RFQ und Beschaffungsabgleich: Testisolation und korrekte Eskalationsrueckgabe

Stand 2026-10-13. Slices CI-PROCUREMENT-IDENTITY-ISOLATION-20261013 und
PROCUREMENT-FOLLOWUP-EXACT-RESULT-20261013.

## Testidentitaet und Daten

Der Ausgangslauf 38360982633 meldete sechs Beschaffungs-Match-Fehler und zwei
RFQ-Setupfehler. Die Tests sendeten dev-token, migrierten fehlende Tabellen,
seedeten gemeinsame DEMO-Daten und loeschten danach anhand von Notizen.

Beide Dateien verwenden nun eine ausdrueckliche Testidentitaet mit signiertem
RSA-JWT. Produktionsmiddleware, Signatur- und Mandantenpruefung bleiben aktiv.
JWKS-Transport und Sitzungsstore sind im vorhandenen Probe-Kontext isoliert;
dies ersetzt keine gesonderte Abnahme des realen Providers oder Redis-Betriebs.
Sechs neue negative Faelle weisen fehlende/alte Zugangsdaten und fremde
Mandantenheader zurueck.

Jeder Fall legt einen eigenen Testmandanten und Lieferanten an. Match-Faelle
bekommen eigene Bestellungen, Wareneingaenge, Rechnung und Lagerplaetze.
Die vorhandenen reinen INSERT-Fabriken werden wiederverwendet; seed() und
get-or-create fuer gemeinsame Demodatensaetze werden nicht ausgefuehrt.
Endpoint-Commits bleiben in Savepoints einer aeusseren Transaktion; Rollback
raeumt die eigenen Wirkungen auf. Keine Migration, Loeschbereinigung, neue
Datenbank oder Container. Fehlendes Schema wird nicht durch Testmigration oder
Skip kaschiert. Bestehende Preis-, ERS- und Lebenszyklusassertions bleiben bestehen.

## Echter Produktfehler

Die zweite Eskalation wurde korrekt als Stufe 2 gespeichert, gab aber Stufe 1
zurueck. create_follow_up las nach INSERT/Commit pauschal die letzte Listenzeile.
PostgreSQL NOW() ist innerhalb einer Transaktion konstant; bei gleichen
Zeitstempeln konnte damit die vorherige oder eine gleichzeitig erzeugte Aktion
in der Antwort stehen.

INSERT RETURNING liefert jetzt unmittelbar die angelegte Zeile. Die gemeinsame
Serialisierung erhaelt ID, Grund, Aktion, Stufe, Zeitstempel und Akteur. Die
zusaetzliche Listenabfrage und deren unvollstaendiger Fallback entfallen.
Die Liste ordnet gleiche Zeitstempel nach Eskalationsstufe und ID deterministisch.
Der echte DB-Vertrag erzwingt gleiche Zeitstempel, prueft verschiedene IDs,
exakten Grund/Stufe und die Reihenfolge beider gespeicherten Aktionen.

## Nachweis und Grenzen

Fuenf Dateien zusammen streng auf valeo_probe: **70 bestanden**, eine Warnung,
58,45 Sekunden. Enthalten sind die acht zuvor blockierten Fachfaelle, sechs
neue negative HTTP-Faelle, Produktionsauth/RSA-/Tenantvertraege und die
Testdatenbankgrenze. Status vorher gelesen: Revision docflow_steuerschluessel_20261013.
Keine Migration, Ruecksetzung, Datenbank- oder Containeranlage. Log:
artifacts/ci-procurement-proof.log.
Vier benachbarte reine Berechnungs-, Validierungs- und Antwortmodell-Dateien:
35 bestanden, eine Warnung, 51,99 Sekunden, ohne Datenbankfreigabe/Seed.
Pagination-Gate bestanden: 278 Abfragen in 251 Funktionen, Baseline unveraendert.

Die Produktdatei wurde um acht Zeilen kleiner. Keine HTTP-Schema-, Rollen-,
Steuerschluessel- oder Buchungsaenderung. Die Rueckgabe ist exakt; parallele
MAX-plus-eins-Vergabe von Eskalationsstufen bleibt ein gesonderter offener Befund.
Aufruferseitiges created_by und fehlende Fachrollen an Beschaffungsaktionen
bleiben innerhalb der bestehenden Identity-Claims zu schliessen.

Sieben weitere rote Fachdateien des Ausgangslaufs sind noch offen: GoBD, die
beiden Feed-Ketten, Logistik, Positionen, Complaint-E2E und Sales-Orders.
Es wird kein vollstaendig gruener GitHub-Lauf behauptet.
