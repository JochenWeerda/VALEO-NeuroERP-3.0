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

Nicht additive Schemaaenderungen bereits bereitgestellter Entity-Vertraege,
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


## Nachlauf nach Docker-Update

GitHub PostgreSQL-Run39592332003:606 bestanden,5 andere Faelle uebersprungen;
alle16 neuen SQL-Vertraege bestanden. Docs, OpenAPI, Maskenplattform, Security,
Rollen und kritische E2E ebenfalls gruen. Quality39592332034 scheitert am
Tabellenkatalog: ausschliesslich read_by fuer domain_shared.tenants fehlte.
Lineage mit bestehendem Generator aktualisiert; physische Tabellen/Spalten/FKs
unveraendert. Kein Gate abgeschwaecht. Regulären Desktop-Neustart nach Engine500
angefordert; bei Nutzerhinweis auf Update keine erzwungene WSL-Beendigung.
Nach bestaetigtem Update: alle laufenden Gesundheitschecks gruen, valeo_probe
erreichbar, Revision merge_hr_tax_20261019. Kein Reset, keine neue DB/Container.
Lokaler SQL-Nachlauf und positive Dreikanalabnahme bleiben gesonderte Nachweise.


Lokaler Nachlauf nach Wiederherstellung:25 bestanden,20 Warnungen,125,93s
(test_studio_entity_generation, test_studio_release_sql,
test_studio_status_idempotency). Saemtliche Anwendungsimporte aus unveraendertem
kanonischem Quellbaum nachgewiesen. Warnungen enthalten bestehende doppelte
CRM-Operation-IDs; daraus wird keine vollstaendige OpenAPI-Fehlerfreiheit behauptet.
Gemeinsamer Pruefstand ist aelter als HEAD (merge_hr_tax_20261019) und besitzt
nicht alle kanonischen Tabellen; seine physische Katalogabweichung wird deshalb
nicht blind eingecheckt. Katalogkorrektur8c3dfac50 aendert nachweislich nur
read_by von domain_shared.tenants. Aktueller CI-PostgreSQL-/Docs-Nachlauf gruen.


## Additive Erweiterung

`python -m valeo_cli studio entitaet-erweitern erweiterung.json --ausgabe paket.json`
verwendet denselben Authoring-Rechteweg wie die Neugenerierung:
POST /api/v1/studio/entity-extension-bundle. Beispiel:

```json
{"name":"studio_silo_gruppen","expected_contract_hash":"64-stelliger Basisfingerprint",
 "columns":[{"name":"lieferhinweis","type":"text","nullable":true}]}
```

Der reale Fingerprint stammt aus dem registrierten Vertrag; das Beispiel
ist bewusst kein ausfuehrbarer Scheinwert. Der Server akzeptiert kein
uebermitteltes Altschema. Nur neue optionale Felder, kein Typwechsel oder
Datenverlust. Antwort enthaelt base_contract_hash und bundle; die Migration
prueft beide Tabellenmarkierungen unter exklusiver Sperre und aktualisiert sie
atomar. Kein DDL im HTTP-/CLI-Aufruf. Neue Registrierung bleibt deaktiviert.
Ein bestehender alter Router sperrt nach der Migration mit409, bis die passende
Vertragsfassung ausgeliefert ist. Keine automatische Publikation oder Freigabe.

Der neue Dreikanalvertrag verwendet den echten MCP-HTTP-Einstieg einschliesslich
Scopepruefung und Weiterleitung desselben Tokens an den echten Commandrouter.
Nur die Netzverbindung wird im Test lokal zurueckgeleitet. Signatur, Rollen,
Tenant, SQL, Audit und Outbox bleiben real. Die synthetische Definition wird
nur im Testregister eingesetzt und ist kein Nachweis einer Studio-Publikation
oder realen visuellen Browserabnahme.


## Abnahme der Kanal- und Erweiterungsintegration

28 Generator-/Negativvertraege bestanden. Kombinierte SQL-Abnahme:27 bestanden,
20 bestehende Warnungen,94,31s. Darin echte signierte HTTP-Anlage, identische
CLI-Wiederholung ohne Dublette und MCP-Aenderung mit demselben Commandrouter;
fehlender Scope vor Weiterleitung403, fehlende Rolle403, fremder Mandant404,
veraltete Version409, fremder Urheber beim Replay409, injizierter Tenant schon
an der zentralen Grenze403. Genau eine Zeile/zwei Audit-Outboxereignisse.

Erweiterungspaket ueber Authoring-API und CLI identisch; vor Ausfuehrung keine
Schema-/Datenwirkung. Generierte Migration in derselben Rollbacktransaktion
ausgefuehrt: vorhandener Datensatz unveraendert mit neuem Feld null, alter
Router409, neuer Vertrag kann versionsgebunden aendern. Erneute Migration
scheitert am Basisnachweis, Daten bleiben erhalten. Alles am gemeinsamen
valeo_probe, keine zusaetzlichen DB/Container/Reset.

Alle lokalen Inventar-/Handbuch-/Architektur-/Ratschengates gruen.
OpenAPI genau ein neuer Authoringpfad; vorhandene Pfade unveraendert.
314/314 Services,472/472 Endpointmodule,931/931 Frontendrouten zugeordnet.

Katalog-Fix-CI: alle zwoelf vorgeschalteten Qualitaetsjobs gruen, SonarCloud
separat rot: new_reliability_rating2 statt1 (cases.py S1226) und new_coverage
59,6 statt mindestens80. Keine Schwellwertsenkung oder Umdeutung in Erfolg.
Live-Studio-Publikation schreibender Stammdaten und reale visuelle Browserabnahme
bleiben offen; dieser Testregister-Nachweis ersetzt sie nicht.
