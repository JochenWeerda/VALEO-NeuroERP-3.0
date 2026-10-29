# Gemeinsame Tabellenprojektion – 21.10.2026

Claim STUDIO-TABLE-QUERY-20261020, Codex. Keine Fachmasken oder fremden Builder geaendert.

Explizite GET-Datenquellen von Tabellen ohne Serverpagination werden zentral ueber
mask.data.read / GET masks/{screen}/data/{source} gelesen. Human-Runtime, CLI und MCP
verwenden denselben Projektor fuer Suche, neun Filteroperatoren, stabile natuerliche
Sortierung und Seiten. Suchtext wird akzentunabhaengig normalisiert; Suche betrifft
deklarierte Tabellenspalten. Dies ersetzt fuer diese Tabellen die bisherige lokale
Browserprojektion und deren abweichende Sortier-/Suchsemantik.

Vor Projektion wird die vollstaendige Quelle begrenzt gesammelt: maximal 5000 Zeilen,
100 Seiten, kumulativ 2 MiB und ein Zeitbudget zwischen Abrufen von 30 Sekunden.
Jeder einzelne HTTP-Aufruf besitzt zusaetzlich ein Timeout von 30 Sekunden; dies ist
kein harter Gesamtdeadline waehrend eines laufenden Streams. Veraenderte Gesamtzahlen,
wiederholte Seiten/IDs und nicht vollstaendige Quellen werden abgelehnt. Das ersetzt
keine Snapshot-Transaktion: Aenderungen gleicher Gesamtzahl zwischen Seiten sind ohne
Versionsvertrag der Quelle weiterhin moeglich. Grosse Tabellen brauchen einen expliziten
serverseitigen Vertrag statt stiller Abschneidung.

Nur deklarierte Spalten duerfen filtern/sortieren; explizite Verbote bleiben wirksam.
Der Ziel-Fachendpunkt erhaelt ausschliesslich das Bearer-Token des Aufrufers und prueft
seine eigenen Rollen, Datensatzrechte und Mandantenbindung. Keine erweiterten Rechte.
Serverpagination und alte Tab-Endpunkte ohne explizite Quelle bleiben bestehende
Vertraege; daraus folgt keine allgemeine Kanalgleichwertigkeit aller Masken.

CLI: daten MASKE QUELLE --tabelle TABELLE --sortieren SPALTE --richtung asc|desc
--filter FILTERDATEI --seite N --limit N. Filterdatei ist ein JSON-Objekt aus
Spaltennamen und {op, value, label?}. label dient ausschliesslich der Anzeige.

Abnahme: 103 Backendtests bestanden, darunter echte signierte REST-/CLI-/MCP-
Abrufe derselben Debitorenliste mit SQL-Daten zweier Mandanten, neun Operatoren,
Paging-Aliasse und Fehlvertraege. Sieben Frontendtests und vollstaendige
TypeScript-Pruefung bestanden. Alle lokalen Projektions-/Architektur-Driftgates
bestanden. HTTP-Transport ist im SQL-Vertrag inprocess; Fachhandler/JWT/
Mandantenbindung sind real, der gemeinsame Sitzungsdienst ist im Fixture isoliert.
Keine Browser-Sichtpruefung oder Live-Bereitstellung in diesem Meilenstein. Keine Aktivierung oder DDL,
kein neuer Container oder Datenbank; SQL-Vertraege verwenden valeo_probe mit Rollback.
Gesamtziel made by Studio bleibt offen: immutable Freigabenachweise je Version,
allgemeine CRUD-/Schema-Verdrahtung und vollstaendige Migration der Altmasken.


Integrationsabnahme mit main bis a059c51bf: 205 Backendtests bestanden,
einschliesslich der beiden zuvor roten Maskenvertraege (Zeilenformen und
Belegidentitaet). Claudes Quell-/Testkorrekturen bleiben erhalten. Alle
Projektions-/Architekturgates gruen; 3242 OpenAPI-Pfade, 931 Routen,
307 Services, 472 Endpunktmodule. follow-redirects-Sicherheitsbefunde
bleiben als eigener Folgeschritt offen. Kein pauschal gruener CI-Status.


## Routenprojektion nach CI-Nachlauf

882ffbd9a liess in der Universal-Mask-CI zwei generierte Suchschluessellisten
zurueck. Eigener Folgeclaim STUDIO-TABLE-ROUTES-20261021 fuehrt den bestehenden
Generator unveraendert aus: in route-inventory.gen.json und route-tree.gen.tsx
jeweils ausschliesslich filter_plan hinzugefuegt. 931 Routen, zweite Generierung
byteidentisch. Keine Route geloescht, kein Gate gelockert.
