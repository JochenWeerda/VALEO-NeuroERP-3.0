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

## Pruefstand-Nachpruefung und CI

Die vorhandene lokale Root-Konfiguration wurde danach ausschliesslich im
Prozessspeicher verwendet. `pruefstand_db.py --status` bestaetigte den
bestehenden `valeo_probe`, Revision `psm_register_entfernt_20261104`.
Eine nachfolgende lesende Verbindung als `valeo_agent` mit
`application_name=agent:codex` sah keine andere aktive Sitzung. Dieser Rolle
fehlt jedoch USAGE auf `domain_docflow` und `domain_shared` (public ist
zugaenglich). Deshalb keine Fachschreibpruefung, kein Reset, keine Migration
und keine stillschweigende Rollen- oder Eigentumsaenderung. Die fehlende
Umgebungsvariable beim ersten Versuch ist damit eingegrenzt; das aktuelle
Hindernis fuer diesen lokalen SQL-Nachweis ist die Schema-Berechtigung.

Auf Commit `09a7616d0` bestand der reale Scanner-Imagebuild
(Run 43625391754); die Pythonruntime-Korrektur ist damit im Neubau belegt.
Der uebrige Gesamtnachlauf war zu diesem Zeitpunkt noch nicht abgeschlossen.
Die finale Frontend-Typpruefung nach allen Quellaenderungen endete mit Exit0.

CI auf unveraendertem Commit 09a7616d0: CI/CD 43625391808 bestanden,
28368 passed/72 skipped/1 deselected/36 subtests (25:31 Minuten).
Quality-Gate-Backend: 28367 passed/73 skipped/1 deselected (25:46 Minuten),
kritische Backend-Coverage bestanden; unterschiedliche Seed-/Strict-Einstellungen
werden nicht als identische Testumgebung ausgegeben. Die lokale Diagnose zeigt
die doppelte Vollsuite in beiden Workflows. Eine spaetere Konsolidierung muss
PYTEST_REQUIRE_DB_STRICT und Inventory-Seed in die kanonische Suite uebernehmen
und vorhandene SHA-/Inhaltssiegel fuer Coverage erhalten; sie ist hier noch
nicht implementiert. Sonar verwendet diese Artefakte ohne erneuten Testlauf.

Finale CI-Abnahme fuer Codecommit `09a7616d0`: 72 erfolgreiche Checks,
keine roten oder laufenden Checks. Quality Gate 43625391909 abgeschlossen
mit success; Sonar-Job 132550001404 meldete am 14.11.2026 um 19:53 MEZ
`QUALITY GATE STATUS: PASSED`. Der Docker Build Smoke bestand ebenfalls.
[Sonar-PR-Abnahme](https://sonarcloud.io/dashboard?id=JochenWeerda_VALEO-NeuroERP-3.0&pullRequest=134).
Dies ist die Abnahme des genannten PR-/Codeumfangs, keine Behauptung einer
Gesamtprojektabdeckung von 80 Prozent oder einer Browser-/SQL-Gesamtabnahme.
Der anschliessende Dokumentationsnachtrag aendert keinen Produktivcode.
