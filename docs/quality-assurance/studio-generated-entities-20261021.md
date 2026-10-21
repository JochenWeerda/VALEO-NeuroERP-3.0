# Studio-Stammdatengenerierung (2026-10-21)

Claim STUDIO-GENERATED-ENTITIES-20261021. ADR-085 Proposed.

## Bedienung und Integration

`python -m valeo_cli studio entitaet-generieren vertrag.json --ausgabe paket.json`
verwendet POST /api/v1/studio/entity-bundle mit bestehendem beleg_write-Recht.
Der Server liefert ein unveraendertes Paket mit Migration, Router, ScreenDefinition,
Typvertraegen und Registrierungsfragment. Keine SQL-Ausfuehrung oder Aktivierung.
Beispiel fuer einen Vertrag:

```json
{"version":1,"name":"studio_silo_gruppen","domain":"crm","label":"Silogruppen",
 "columns":[{"name":"bezeichnung","label":"Bezeichnung","type":"text","nullable":false}]}
```

Die Dateien liegen im files-Objekt, ihre Inhaltsbindung in file_hashes. Migration
pruefen und ueber den bestehenden Alembic-Prozess ausliefern. Das generated_entities-
Fragment in den bestehenden config/studio_data_sources.yaml einpflegen und Backend
neu starten; der gemeinsame Adapter und Katalog werden daraus verdrahtet. Beide
Schreibschalter bleiben zunaechst aus: writes_enabled=false und agent_roles=[].
Erst nach positiver Fach-/Kanalabnahme gezielt einschalten. Kein alternativer
MCP-Datenbankweg. Die bestehende Studio-Veroeffentlichung verlangt weiterhin ihre
eigenen Nachweise; das Paket liefert keine faelschliche grain.v1-Zertifizierung.

Nur neue Studio-Stammdaten in CRM/Agrar/Lager. Keine generische Bearbeitung von
Bestand, Finanzbuchungen, Belegen oder bestehenden Fach-/Stammdatentabellen.
Aendern ersetzt die fachlichen Felder vollstaendig und verlangt expected_version;
Deaktivieren erhaelt den Datensatz. Typpruefung verhindert Identitaetsueberschreiben,
Fremdfelder, Dezimalrundungsverlust und unzulaessige Pflichtfeldluecken. Auditgrund
und Wiederholungsschluessel sind Pflicht. UI-Felder werden mit demselben zentralen
Maskenrenderer gezeichnet; fuer generierte Updates/Deaktivierung uebertraegt die
zentrale ActionRuntime die angezeigte Version. JSON-Commands akzeptieren zusaetzlich
die dokumentierte verschachtelte data-Form. Beide enden in derselben Validierung.

## Abnahme

Pruefung auf gemeinsamem valeo_probe; generierte DDL in der bestehenden auesseren
Rueckrolltransaktion. Echte signierte JWT/JWKS-Identitaeten, Rollen und Mandanten-
Middleware. Kein Rollen-/Mandantenmock. Eigene Tabellen und synthetische Datensaetze
werden ueber die aeussere Transaktion zurueckgenommen. Outbox bleibt dabei fuer
andere Verbindungen unsichtbar. Keine weiteren DB/Container/Reset.

Die Tests pruefen Erzeugen, Lesen, Wiederholung, Aendern, veraltete Version,
Deaktivieren, Historie, unveraenderbaren Auditbeleg und atomare Outbox. Zusaetzlich
Rollen, Tenantheader, fremde Objekte, Identitaetsinjektion, Praezision, Previewmodi,
veraltete Bereitstellungsmarkierung und gesonderte Agentenfreischaltung. REST und
CLI erzeugen dasselbe deaktivierte Authoringpaket. Eine positive MCP-/Browser-
Fachkette der neu generierten Maske ist damit noch nicht nachgewiesen.

CI-Nachlauf des vorherigen Meilensteins: fehlende ADR-Navigation verursachte Docs-
und Quality-Fehler. Bestehende SQL-/Status-Tests erwarteten noch Historien ohne den
nun verpflichtenden Migrationsplan. Erwartungen wurden um diesen echten Schritt
erweitert; keine Freigabepruefung entfernt. Der reale grain.v1-SQL-Test erhaelt vor
Publikation denselben gespeicherten Plan. Weitere UAT-/Runtime-Sweep-Befunde sind
separat zu bewerten und hier nicht als behoben erklaert.

## Weiter offene Abnahmen

Allgemeine Schemaerweiterung bereits bereitgestellter Entity-Vertraege,
weitere Domaenen, fachliche Referenz-/Freigaberegeln und die positive
UI/CLI/MCP-Publikationsabnahme sind nicht aus einem Typvertrag ableitbar.
Diese Luecken sind keine automatisch bestandenen Simulationen. Das Gesamtziel
bleibt offen, bis die konkreten fachlichen Ketten dieselben realen Nachweise haben.


## Aktueller Pruefstand und Liefergrenze

23 reine Generator-/Typ-/Registrierungsvertraege bestanden; die Unit-Abnahme
verwendet ausdruecklich keine Anwendungs-Lifespan-/DB-Fixtures und beweist daher
keine Signatur- oder SQL-Sicherheit.24 bestehende und erweiterte Frontendtests
bestanden, TypeScript ohne Fehler. Alle lokalen Inventar-/Handbuch-/Architektur-
und Ratschenchecks bestanden; OpenAPI3244 Pfade,313 Services,931 Frontendrouten.
Kanonischer physischer Tabellenkatalog unveraendert. ADR-Navigation92 Eintraege.

Ein erster SQL-Lauf hatte59 Erfolge und einen fehlerhaften erwarteten HTTP-Status:
Identitaetsinjektion wurde bereits an der Tenantgrenze mit403 statt erwarteter422
abgewiesen. Die Erwartung ist korrigiert. Danach wurden Schutz-/Verdrahtungs-
Details ergaenzt, darunter deklarierte Tabellenquelle, Bereitstellungsmarker,
Standard-Sperre, Agentenrollen und flache Eingaben. Diese spaeteren SQL-Vertraege
sind lokal noch nicht final abgenommen: PostgreSQL wurde unerreichbar und die
bestehende Docker-Engine antwortete mit500. Den wartenden breiten Lauf beendet,
keinen Erfolg daraus abgeleitet. Keine fremden Dienste neu gestartet, kein Reset
und keine Ersatzdatenbank erstellt. GitHub-CI verwendet die ohnehin bereitgestellte
Jobdatenbank. Der Claim bleibt bis zu diesem Nachweis und der noch ausstehenden
positiven Dreikanal-/Fachkettenabnahme in arbeit; das Gesamtziel ist nicht erledigt.

Das Paket enthaelt ausserdem openapi.json aus genau derselben Routerfactory wie
zur Laufzeit. Ein eigener Vertrag vergleicht Pfade und Komponenten vollstaendig;
Anlage/Aenderung, Detail, Paging und Antworten sind generisch aus dem typisierten
Entity-Vertrag abgeleitet. Numerische Spalten sind zentral numerisch ausgerichtet,
Lagerdefinitionen erhalten das bestehende inventory-Tabellenprofil. Noch nicht
unterstuetzte Serversortierung/-filterung wird nicht angeboten.
