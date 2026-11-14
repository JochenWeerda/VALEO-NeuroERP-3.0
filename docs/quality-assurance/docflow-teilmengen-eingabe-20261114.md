---
title: DocFlow Teilmengen Eingabe und Leseoptionen
status: aktiv
last_reviewed: 2026-11-14
owner: Codex
---

# Teilmengenvertrag

`DocflowConvertRequest` lehnt negative und nicht endliche Mengen ab. Der
bestehende Umwandlungsdienst weist unbekannte Positionskennungen ab, auch wenn
zugleich eine gueltige Position angegeben ist. Ohne Mengenangabe und mit leerem
Dictionary bleibt die bisherige Erstumwandlung des gesamten Rests erhalten;
Nullmengen erzeugen keine Position. Restmengenpruefung bleibt bestehen.

`conversion_options` liest einen tenantgebundenen kanonischen Beleg ohne
Bootstrap, prueft die erlaubte Relation und den Rechnungsweg und gibt nur
Positionsidentitaet, Artikel, Einheit, Menge und Restmenge sowie Belegversion
zurueck. Keine Preise, keine Schreib-/Commit-/Rollbackoperation. Die
Berechtigungspruefung des neuen HTTP-Lesewegs liegt beim Endpunkt.

Gegenprobe vor der Korrektur: fuenf Tests scheiterten, weil NaN, positive und
negative Unendlichkeit, negative Mengen sowie die gemischte fremde Position
akzeptiert wurden. Danach bestanden elf gezielte Tests (34,40 s) gegen das echte
Modell und den echten Dienst mit simuliertem Datenbankrand; auch leere und
positive Auswahl, Null und Uebermenge sowie der schreibfreie Lesevertrag sind
geprueft. Eine Starlette-Deprecation-Warnung und ein pyreadline-Aufraeumhinweis
traten auf. Keine Datenbank, kein Container und keine SQL-/OIDC-Abnahme.
Bestehender `convert` kann vor der Mengenpruefung einen Legacy-Lieferschein in
der laufenden Transaktion bootstrappen; der HTTP-Endpunkt rollt bei
Validierungsfehlern zurueck. Fuer kanonische vorhandene Belege erfolgen vor der
Positionspruefung keine Folgebelegschreibungen.

## Integrierte Studio- und Kanalbedienung

Die Belegfamilie hat append-only Version 1.9.0 erhalten. Der semantische
Vergleich saemtlicher vorheriger Basis- und Variantenfassungen mit Git HEAD
bestaetigt unveraenderte Inhalte. Alle neun Varianten materialisieren den
kanonischen Builder; nur Varianten mit Folgebeleg erhalten die Positionsauswahl.
Kein neuer Endpoint-Cluster, Service, Container oder Datenbankmodell; bestehender
DocFlow-Kontext mit einem ergaenzenden schreibfreien Lesevertrag.

Die generische Detailseite laedt die vollstaendige, zielartbezogene Auswahl
statt eines paginierten Positionsreiters. Beleg, Art und Version muessen zum
aktuellen Kontext passen. Null ist die Voreinstellung; fehlende, nur-null,
doppelte, negative, nicht endliche und uebergrosse Auswahlen werden nicht als
Volluebernahme interpretiert. Alle Positionskennungen werden serverseitig gegen
den Quellbeleg geprueft. UI und CLI bilden Tabellenwerte auf das gleiche
kanonische Mengen-Dictionary ab. Der bisherige aggregierte Belegaktionsweg
ueberschreibt explizite Teilmengen ebenfalls nicht mehr mit dem ganzen Rest.
Die alte direkte API-Erstumwandlung ohne Mengen bleibt bewusst kompatibel.

HTTP-Nachweis: sechs echte Routertests bestanden mit produktiven Rollenregeln
und simuliertem SQL-/Identitaetsrand: fehlende Anmeldung 401, fehlende
Zielbearbeitung 403 vor Quellzugriff, fehlendes Quellleserecht 403,
widersprechender Mandant 403, fremde Kennung 404 und preis-/schreibfreie
Antwort. Der erste lokale Testclient-Start war beim internen Windows-Socket
blockiert; nach Diagnose und Ausfuehrung mit erlaubtem lokalem Socket bestanden
die Tests in 5,87 Sekunden. Keine Produktlockerung oder Testueberspringung.

Weitere Nachweise: fuenf Belegadaptertests fuer explizite Menge und
Invalid-Eingaben bestanden; 43 CLI-Transporttests bestanden. 199 gemeinsame
Parent-/Mengenfaelle sowie 88 ueberlappende Versions-/CLI-/Mengenfaelle bestanden;
diese Zahlen werden nicht zu einem Gesamtergebnis addiert. Frontendnachweise
und Grenzen stehen im [Dialogbericht](docflow-konvertierung-dialog-20261114.md).

Der Pruefstand-Status meldete fehlende TEST_DATABASE_URL/DATABASE_URL in dieser
Sitzung. Es wurde keine Datenbank angelegt, zurueckgesetzt oder beschrieben.
Die Action-Matrix wird dadurch nicht auf gruen gesetzt: realer SQL-/OIDC-/
Browser- und exakter CI-Nachweis bleiben eigenstaendige Abnahmen.

Finaler Nachlauf: sechs Belegadapter-/Fixture-Vertraege und 48 Frontendfaelle
fuer Auswahl, Transport und Dialog bestanden. Alle Befehle aus dem
Doc-Generator-Meta-Check bestanden, einschliesslich OpenAPI, MCP-Register und
Architekturindex (1145/1145 Routen); Belegversionen, CLI und Studio-Katalog
separat synchron. Godfile-Ratsche unveraendert gruen, Docs-Governance gruen.
