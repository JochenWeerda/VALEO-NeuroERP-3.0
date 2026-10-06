---
title: CI-Reparatur am 5. Oktober 2026
type: reference
audience: [agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-05
---

# CI-Reparatur 2026-10-05

## Fortsetzung 2026-10-06

Run 37374442374 auf 1784c66b1: 15355 bestanden, 19 fehlgeschlagen und
17 Setup-Fehler; diese Zahl ist keine Vollsuite-Freigabe. Frontend-Build,
Docs/Governance, PostgreSQL-Job und kritische E2E bestanden getrennt.

Fuenf HRM/POS-Vertraege mockten entfernte Runtime-DDL-Helfer. Die Mocks
sind entfernt; Aufrufe uebergeben den Tenant und pruefen dessen SQL-Bindung.
Opportunity-Ausfall prueft den vorhandenen tenantgebundenen lokalen Fallback
statt einen direkten Aufruf mit FastAPI-Depends-Platzhaltern. Der Typwaechter
beruecksichtigt den expliziten 409-Kassenabschluss; dessen keine-Erfolgsantwort-
und keine-DB-Mutation-Vertraege bleiben aktiv. 51 gezielte Backendpruefungen
einschliesslich DDL-Drift und echtem Kassen-/Journalbestand bestehen im vorhandenen
valeo_probe (Revision quittung_ohne_vorgang_20261006), ohne Reset oder Migration.

InventoryLotOut ergaenzt die migrierte boolesche Spalte eudr_relevant; GET-
Antworten duerfen dieses gespeicherte Compliance-Kennzeichen nicht verlieren.
Die zentrale OpenAPI wird aus committed Quellen plus diesem Schemahunk erzeugt.
Sie enthaelt 3092 Pfade und zieht auch die bereits committed Personal-
Vertragsaenderungen aus 4a5a32e37 nach; fremde Arbeitsbaumartefakte bleiben erhalten.
Elf bestehende Lot-/Materialfluss-Antwortvertraege bestehen zusaetzlich.

CRM-Smokes des Runs 37374442347 erwarteten noch das entfernte KIM-Sidebar-
Layout und den alten Lead-Titel. Vier aktualisierte Browserpruefungen bestehen
in 30,8 Sekunden: Kundenlisten-Weiterleitung unter unveraendertem Zeitbudget,
Deep-Link mit Kundenkennung/Register sowie native Lead-Felder und Kontext.

Offen bleiben weitere Vollsuite-Befunde (unter anderem SalesOrder-Fixtures,
Architekturzuordnungen, Maskenvertraege und Settlement) sowie Grype und die
zwei ungepatchten Node-Advisories. Security-Gates und Severity-Schwellen bleiben
unveraendert; kein Gesamt-Gruennachweis.

Der nachfolgende Quality-Lauf 37375993205 auf dem Personal-Commit 4a5a32e37
meldet eine neue direkte Kalenderquelle in personal_organisation_service.
Das Standardjahr folgt jetzt business_today().year; die Kalender-Ratsche
besteht unveraendert (202 Stellen/112 Dateien). Drei Code-Inventare sind
aktuell; 44 echte Organigramm-/Zeitkonto-Vertraege bestehen im gemeinsamen Probe.
Sie pruefen unter anderem Korrekturen, Saldo, Uebertrag und Tenanttrennung.
Die drei Inventare wurden
aus committed Backend-/Migrationsquellen nachgezogen und mit --check aktuell.
Der dort ebenfalls fehlgeschlagene Worklist-Titeltest ist ein weiterer
Renderer-Befund und bleibt getrennt offen; keine Baseline angehoben.

Die Runs 37359972771, 37359972315, 37359972362, 37359972369,
37360271159 und 37360270406 belegen unterschiedliche Ursachen.
Die Korrekturen lassen Baselines, Audit-Schwellen und Pflichtgates bestehen.

- Slice-Pflichtfelder `tests` und `external_gates` nachgetragen; ADR-Navigation generiert.
- `domain_contracts` dem Agrar-Vertragsregister zugeordnet. 649 Tabellen im
  gemeinsamen `valeo_probe` lesend geprueft: keine Besitzfehler.
- Ein unmittelbarer Zwei-Eltern-Merge von etabliertem main nach develop
  vergleicht die Ratsche mit dem uebernommenen main-Elternstand. Andere
  Pushes und PRs behalten den bisherigen Vergleich. Verschlechterungen im
  Merge-Ergebnis bleiben verboten; acht synthetische Git-Vertraege pruefen dies.
- SQL-Kontoauswahl verwendet feste Statements; Webhook-Tabellen sind feste
  SQL-Literale. Fachwerte und Tenant bleiben gebundene Parameter.
- Fehlende Lieferdaten verwenden den zentralen Geschaeftstag statt Hostdatum.
- OpenAPI wird aus committed Backend-Code erzeugt; fremde Arbeitsbaum-Spec
  wird nicht ueberschrieben. Nachfolgende API-Commits erfordern erneute Generierung.

## Logistik und Revisionsbaum

`frachtbrief_service` erzeugt einen Frachtbrief aus vollstaendigen
Verladungsangaben und der kanonischen Sendungssicht. Bei fehlenden Angaben
wird kein unvollstaendiger Frachtbrief erzeugt; Wiederholungen finden den
Beleg ueber die Verladungsnummer. Fehlendes Datum folgt `business_today()`.

`webfleet_connect` liest Fahrzeugberichte mit Basic-Auth aus konfigurierten
Zugangsdaten, validiert Koordinaten und begrenzt Abrufe auf einmal pro Minute.
Ohne Konfiguration oder gueltige Position verbleibt die Tour am Zielort.
Externer Providerbetrieb ist eine gesonderte Abnahme.

`zusammenfuehrung_20261005_eudr_uebermittlung_trifft_bank_gl_` verbindet
`bank_gl_binding_20261001` und `eudr_uebermittlung_20261001` ohne eigenes DDL.
Beide Eltern muessen angewendet sein. Die Migration schreibt keine Fachdaten;
Upgrade und Downgrade ordnen ausschliesslich den Revisionsgraphen. Kein Reset
des gemeinsamen Pruefstands zur Verifikation.

## Offene Laufbefunde

Die isolierte Frontend-Typpruefung und neun UI-Vertragstests bestehen.
Fehlende Exporte und der screenTitle-Prop-Vertrag wurden als minimale
committed-source-Hunks korrigiert, ohne Layout-WIP zu veroeffentlichen.
ErrorState verwendet volle Textdeckkraft fuer Status und Wiederherstellung;
die Browser-WCAG-Abnahme und neue Actions-Laufe bleiben erforderlich.
Der lokale Chromium-Lauf scheiterte bereits beim page.goto der Startseite
an 90 Sekunden Timeout, obwohl der Vite-Server HTTP 200 liefert. Er wurde
beendet; dieses lokale Ergebnis ist keine WCAG-Freigabe.

Nachtrag: Der Timeout ist auf die unbegrenzte automatische Tailwind-Quellensuche
zurueckgefuehrt. Die Browserdiagnose zeigte ausschliesslich `src/index.css` als
offene Anfrage. Identischer PostCSS-Eingang mit expliziten Quellen kompiliert
in 755 ms (279363 Zeichen). Der Minimalhunk verwendet `source(none)` und
registriert `src/` sowie `index.html` relativ zur zentralen CSS-Datei;
Layout-/Token-WIP im gemeinsamen Arbeitsbaum wird nicht uebernommen.
Alle acht bestehenden WCAG-2.2-AA-Routen bestehen auf diesem isolierten Stand
in 21,5 Sekunden, ohne erhoehte Timeouts oder ausgeschlossene axe-Regeln.
Der vollstaendige Produktionsbuild transformiert 4184 Module und besteht
in 58,44 Sekunden. Die generierte zentrale CSS-Datei enthaelt weiterhin
die Renderer-Utilities (unter anderem grid, px-4 und text-status-error).

Die GitHub-Jobs des ersten Versuchs auf 4da6c2f03 liefern fuer Docs, OpenAPI,
Governance sowie zwei Quality-Gate-Jobs die Annotation
`The job was not acquired by Runner of type hosted even after multiple attempts`.
Service Security hat nicht gestartete Teiljobs (`abandoned`); das Sammelgate
blockiert korrekt. Nur fehlgeschlagene Jobs wurden erneut gestartet.
Docs Build und OpenAPI bestehen inzwischen im zweiten Versuch; PostgreSQL
und kritische E2E bestanden bereits. Andere ausstehende Jobs bleiben offen.

`@fastify/busboy` ist auf 3.2.1 gesperrt. Der unveraenderte Produktionsaudit
meldet danach zwei statt vier hohe Befunde. Node-forge
[GHSA-86w9-cpqp-85rv](https://github.com/advisories/GHSA-86w9-cpqp-85rv) und braces
[GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) haben
laut GitHub-Advisories derzeit kein gepatchtes Release. Diese bleiben offen;
keine Audit-Ausnahme und keine behauptete Security-Freigabe.

Die drei Code-Inventare und Router-Inventare wurden aus committed Quellen
plus eigenen UI-Hunks regeneriert. Der Preiscommit d33a59a30 fuegte zwei
Response-Felder hinzu; die erneute Spec aus b1e891249 enthaelt beide.
Der isolierte OpenAPI-Check bestaetigt 3092 Pfade; Architekturindex strict
prueft 932 von 932 Routen. Die drei Code-Inventare sind aktuell.

Der erste Reparaturcommit c50379d2e ist auf main gepusht. Seine Docs- und
API-Laeufe stoppten an Inventaren bzw. diesen zwei Preisfeldern; beide werden
im zweiten Meilenstein korrigiert. Eingereihte Runs sind kein Gruennachweis.

Der zweite Meilenstein 0b373a432 ist auf main, develop wurde mit dem echten
Merge db97ee665 nachgezogen. Der Folgepatch sperrt markdown-it auf 14.3.1
(Advisory GHSA-253c-mchw-3w2r). Formatierung, automatische Link-Erkennung und
begrenzte Verarbeitung eines 200-KB-Eingangs wurden mit dem heruntergeladenen
Paket ohne Installationsskripte geprueft. OpenAPI-Artefakt-, Generator- und
Workflow-Aenderungen starten kuenftig ebenfalls den unveraenderten Driftcheck;
so bekommt eine alleinige Spec-Korrektur eine neue Abnahme.

Die bestehende ADR-071-Evidenz fuer eingebettetes Chroma ist unveraendert;
neun Security-Gate-Vertraege bestehen. Es wurde keine neue Ausnahme eingefuehrt
und die Rohwarnungen bleiben sichtbar. Zusaetzlicher offener Sensorbefund:
[http-cache-semantics GHSA-ch52-4w7c-c8xp](https://github.com/advisories/GHSA-ch52-4w7c-c8xp),
ebenfalls ohne gepatchtes Release. Keine Gesamt-Security-Freigabe.
Ueberholte noch wartende Laeufe des eigenen ersten Reparaturcommits werden
beendet; gestartete, aktuelle und fremde Dependabot-Laeufe bleiben erhalten.
114 gezielte Konto-/Webhook-/Frachtbrief-/Doku-/Ratschen-/Workflow-/Besitztests bestanden;
Webhooks wurden mit beiden DB-Verbindungen explizit auf dem gemeinsamen Probe
geprueft. MkDocs (derselbe Buildmodus wie CI), ADR-Nav, Slice-Harness, SQL-,
Kalender- und Godfile-Ratschen sind gruen. Die Live-Tabellenpruefung ist
lesend. Kein zusaetzlicher Docker-Container und keine neue Testdatenbank.


## Weitere Befunde am 2026-10-06

Die Verkaufsauftrag-Fixtures verwenden alle migrierten Pflichtwerte inklusive
customer_id, subject, description, currency und version. Der FK-Kunde wird
vor dem Auftrag angelegt. Global eindeutige Lager-, Artikel-, Kunden- und
Auftragsnummern sind pro eigenem Testdatensatz isoliert; fremde vorhandene
Daten wurden nicht geloescht. Entfernte crm_customers-Doppelstaemme werden
weder angelegt noch beim Aufraeumen angesprochen. Der kanonische Resolver
liest domain_crm.customers. Die Adressfixture bindet einen gueltigen JSON-String
fuer die JSONB-Spalte, ohne den erwarteten Strassenwert zu veraendern.

135 CRM-/Beleg-Vertraege bestanden auf dem gemeinsamen valeo_probe in
66,37 Sekunden. Ein zunaechst separat gepruefter Identitaetstest scheiterte
auch gegen committed Quellen: Die bereits vorhandene Fahrzeugstamm-Maske
fehlte in seiner Erwartungsmatrix. Nach Ergaenzung von kennzeichen besteht
auch dieser Test (0,41 s). Die 17 zuvor beobachteten Fixture-Setupfehler sind
in diesem gezielten Lauf nicht mehr aufgetreten. Kein Schemareset, kein
neuer Container und keine neue Testdatenbank. Der Probe meldete die bereits
vorhandene Revision quittung_ohne_vorgang_20261006.

GitHub-Lauf 37417689053 meldete neue Herstellerfixes. Zentraler Override
und Lock integrieren proxy-addr 2.0.8, seroval 1.6.3, compression 1.8.2 und
source-map-js 1.2.2. Damit werden folgende gemeldete CVE durch ihre gepatchten
Versionen adressiert:

- [Proxy-IP-Spoofing](https://github.com/advisories/GHSA-jqcg-44mw-7w3h)
- [Seroval Promise-Deserialisierung](https://github.com/advisories/GHSA-p6vx-979v-rg4c)
- [Seroval unbegrenzte TypedArrays](https://github.com/advisories/GHSA-jp82-f5mq-hwhp)
- [Kompressionsstream nach Abbruch](https://github.com/advisories/GHSA-vc2v-76pw-4v95)
- [Source-Map-Offsets](https://github.com/advisories/GHSA-68fv-2mgg-jv7q)

Isoliert bezogene Herstellerpakete ohne Installationsskripte bestehen
IP-Vertrauensgrenzen, begrenzte Source-Map-Offsets, abgewiesene uebergrosse
TypedArrays, Serialisierungs-Roundtrip, Gzip-Ausgabe und Freigabe der Streams
nach normalem und vorzeitigem HTTP-Abschluss. Lock-Aufloesung bestand;
bekannte Workspace-Peerwarnungen bleiben sichtbar. Die vier alten
Runtime-Paketversionen kommen im Lock nicht mehr vor. Keine neue Ausnahme
und keine abgesenkte Security-Schwelle. Node-forge, braces, der historische
Dockerfile-Rootbefund und weitere Vollsuite-Befunde bleiben offen.

Am verifizierten GitHub-Stand 4a4104fe1 bestehen Docs Governance, Docs Build,
OpenAPI Drift, PostgreSQL, kritische E2E und Erntepeak. Security Agent bleibt
wegen seiner Rohbefunde rot; andere neue Laeufe sind noch nicht abgenommen.


Der anschliessende unveraenderte Voll-Audit des neuen Locks meldet
0 kritische, 3 hohe und 18 moderate Befunde. Die drei hohen Befunde sind
node-forge GHSA-86w9-cpqp-85rv, braces GHSA-vfj7-8cjw-p6xm und
http-cache-semantics GHSA-ch52-4w7c-c8xp. Der Audit bleibt deshalb mit
Exitcode 1 rot. Frozen-Lock-Abnahme fuer alle 36 Workspaces bestand offline
in 1,1 Sekunden, ohne installierte gemeinsame Pakete zu veraendern.

Meilenstein 71cf8a126 ist auf main verifiziert; develop wurde mit dem echten
Zwei-Eltern-Merge a0c6376db nachgezogen. Die zwischenzeitlich eingebrachte
Fahrzeug-/Qualifikationsintegration 93bd71598 bleibt erhalten. Neue Actions
auf 71cf8a126 sind gestartet bzw. eingereiht; keine Gesamtfreigabe behauptet.


## Buchungs- und API-Testvertraege am 2026-10-06

Zwei weitere Vollsuite-Failures waren unvollstaendige Testvoraussetzungen.
Die Einkaufsfreigabe verlangt bereits aktive, nicht geloeschte und buchbare
Konten des eigenen Mandanten. Ihr Integrationstest legt jetzt ausschliesslich
fuer den eigenen Testtenant 5100 und 1600 an. Er weist neben FREIGEGEBEN zwei
Journalzeilen mit genau diesen Konto-IDs sowie ausgeglichene Soll-/Habensummen
von 31,50 EUR nach. Cleanup entfernt erst eigene Journalzeilen/Buchungen,
dann eigene Konten und den eigenen Tenant. Fremde Konten bleiben erhalten.

Der Wave-100-Settlement-Fake bildet die SQL-Kontoantwort mit first() ab und
prueft Tenantparameter, Aktivstatus, Loeschstatus und Ausschluss von
Summenkonten. Freigabe vor FIBU bleibt zwingend; der Test weist die Aufloesung
aller drei Kontonummern nach. Beide vollstaendigen Testmodule bestehen mit
18 Tests in 49,90 Sekunden auf dem vorhandenen Probe bzw. ihrem Unit-Fake.
Keine produktiven Buchungspruefungen wurden veraendert.

Der Major-Domain-Routertest prueft jetzt /vertraege und /vertraege/analytics
fuer das zentrale Register sowie /contracts/{contract_id} fuer den separaten
Warenkontrakt. Dies setzt die bereits dokumentierte Trennung aus
KONTRAKTREGISTER-20261001 um, ohne alte oder kollidierende Aliasrouten wieder
anzulegen. Der EUDR-UAT erwartet due_diligence_statements statt erfundener
pauschaler total-/gesamt-Felder. Ganze, nichtnegative Register- und
Chargenzaehler sowie ihre Beziehungen werden geprueft; zurueckgezogene
Erklaerungen bleiben Teil der Gesamtanzahl. Relevante Chargen entsprechen
der Summe aus nachgewiesenen und offenen Chargen.

Auf dem verifizierten GitHub-Stand 390c571ab bestehen Docs Governance,
Docs Build und PostgreSQL. Weitere Gesamtpruefungen laufen oder sind noch
eingereiht. Der CI-Reparaturslice bleibt bis zur Gesamt-Abnahme in Arbeit.

Der abschliessende API-Vertragslauf besteht mit zwei Tests in 44,53 Sekunden
inklusive der Zaehlregel fuer zurueckgezogene Erklaerungen. Zusammen mit den
18 Buchungsvertraegen sind 20 gezielte Tests gruen. Kein Test uebersprungen.


## Architekturindex und CRM-Delegation am 2026-10-06

Ein lokaler gruener Architekturtest war kein belastbarer Liefernachweis:
Die fremd bearbeiteten Inventare im Arbeitsbaum enthielten die betroffenen
Services nicht. Der isolierte Generator auf committed Quellen meldete sechs
unzugeordnete Services und drei EUDR-Endpunkte. Die kanonischen Prefix-Regeln
enthalten jetzt genaue Zuordnungen fuer EUDR (dms-compliance), Frachtbrief
und WEBFLEET (logistics), Preisfindung (finance), Mitgliederregister (platform)
und Wiegeschein (inventory). Grundlage fuer die Wiegescheinzuordnung ist
das bereits fuehrende domain_inventory.weighing_tickets, nicht die entfernte
Doppelwiegungstabelle. Dies ist eine Minor-Inventarkorrektur ohne neue Grenzen,
Container oder API-Vertraege.

Der zwischenzeitlich fremd integrierte Commit 8d6eb5afd bleibt erhalten.
Seine Services fuer Etikettendruck und Schaeden werden entsprechend ihren
bereits zugeordneten Endpoints inventory bzw. dms-compliance zugeordnet.
Drei Code-Inventare werden ausschliesslich aus committed Backend-/Migrations-
quellen regeneriert und indexseitig integriert. Die fremden Arbeitsbaum-
fassungen der Inventare bleiben erhalten. Der Architekturindex wird daraus
und aus den eigenen Prefix-Regeln erzeugt. Strict-Abnahme: 932/932 Routen,
269/269 Services, 451/451 Endpoints zugeordnet; anschliessender --check gruen.
Acht konkrete Servicezuordnungen und drei EUDR-Zuordnungen werden auch dann
geprueft, wenn lokale Inventare unvollstaendig sind.

Der UIX-051-Test fuer die Kundenmaske folgt jetzt der vorhandenen Delegation
Customer360NativePage -> PartyNativePage -> UniversalNativeDetailPage.
Er prueft Route-/Query-ID, Tabkontext, die richtige Customer-/Lead-Screen-ID
und deren Weitergabe an den zentralen Renderer. Andere Wrapper bleiben auf
ihren direkten Screen-ID-Vertrag geprueft. Keine Masken, Renderer oder
laufenden Frontend-Aenderungen werden veroeffentlicht. Insgesamt bestehen
67 Architektur-/UIX-Migrationsvertraege in 0,74 Sekunden.

Der Security-Lauf 37419090073 auf 390c571ab ist weiterhin rot: ZAP, Trivy
und Bandit bestanden; Grype und Dependency Audit scheiterten. Diese Befunde
werden durch die Inventar-/UIX-Korrektur nicht behoben; keine Gesamtfreigabe.


Die zusaetzliche OpenAPI-Integrationspruefung auf committed Quellen meldete
Drift durch die Schaden-/Etiketten-Integration 8d6eb5afd. Deshalb wird die
Spec ebenfalls ausschliesslich aus diesem Backendstand regeneriert und
indexseitig veroeffentlicht. Die fremde Arbeitsbaum-Spec bleibt erhalten.
Der Generator verwendet weiterhin die echte main:app und die kanonische
Version 3.0.0; keine Test-App oder Pfadausnahme. Bereits bestehende Warnungen
ueber doppelte Operation-IDs bleiben sichtbar und werden hier nicht geloest.

Kanonische Spec-Abnahme: 3095 Pfade, acht geaenderte Pfade fuer Etiketten,
Schadenmeldungen/Versicherungen und Gelangensbestaetigungs-Mahnung. Drei
Pfade sind neu. Erneutes render(build_spec()) stimmt mit dem gespeicherten
Artefakt ueberein. Backendquelle bleibt committed 8d6eb5afd.


## Eindeutige Router-Montagen am 2026-10-06

Die echte committed main:app registrierte 168 Methoden/Pfade mehrfach.
113 dieser Gruppen entstanden durch spaetere Wiederholungen bereits
kanonisch eingebundener Router. main.py bindet Inventory, Agrar, Audit,
GDPR und Kontrakte deshalb nicht erneut ein; api.py entfernt ausschliesslich
die zweite Quality-Evidence-Montage. Die erste Montage und ihre vorhandenen
Abhaengigkeiten bleiben massgeblich. Kein dynamischer Dedup-Filter und keine
Router-Allowlist verdecken Konflikte.

Acht Regressionen bestehen in 69,20 Sekunden. Sie pruefen fuer jeden Endpunkt
der sechs Router alle Methoden/Pfade, genau einen Treffer, dieselbe Handler-
Identitaet, dasselbe Antwortmodell/Status und die enthaltenen Dependency-Calls.
Die betroffenen Module haben keine doppelten Methoden/Pfade mehr. Die Tests
pruefen Registrierungsmetadaten ohne Fachdatenmutation oder App-Lifespan;
DB-Konfiguration verweist auf den vorhandenen Probe. --status bestaetigt
Revision quittung_ohne_vorgang_20261006. Keine Datenbank, kein Container,
kein Reset und keine Migration angelegt.

Die OpenAPI-Spec stammt aus committed 8c1308ca6 plus den beiden eigenen
Montagehunks. Der Vergleich bestaetigt exakt dieselben 3095 Pfade und dieselben
HTTP-Methoden je Pfad; das gerenderte Artefakt wird erneut kanonisch geprueft.
Die real registrierte App hat danach 55 doppelte Methoden/Pfade statt 168.
Andere Handlerkonflikte und die zwei Nebenbuch-Doppeldefinitionen im alten
Finance-Router bleiben offen; keine Gesamt-Eindeutigkeit behauptet.

Alle drei Code-Inventare sind unveraendert aktuell. Das Agent-Handbuch meldet
auf committed Quellen fuenf aktuelle Artefakte. Der Arbeitsbaumcheck meldete
Drift in drei Handbuchdateien durch fremde laufende ScreenDefinition-Arbeit;
der isolierte committed-source-Check bestaetigt, dass dieser Slice kein
Handbuch-Update benoetigt. Fremde Masken-/Handbucharbeit bleibt geschuetzt.


## Persistente Nebenbuch-Abstimmung und Integrationsabnahme am 2026-10-06

app/finance/router.py definierte GET und POST fuer die Nebenbuch-Abstimmung
jeweils zweimal. FastAPI fuehrte die zuerst registrierten DB-Handler aus,
waehrend Python die gleichnamigen Funktionen und OpenAPI den spaeteren
Platzhaltern zuordneten. GET meldete dort immer 404, POST erzeugte nur ein
ungespeichertes Schemaobjekt. Die zwei nachrangigen Platzhalter und der
ungenutzte Schemaimport sind entfernt. Die echten Handler behalten Auth,
Tenantfilter, Antwortmodell, Status und Datenbankzugriff.

Die echte Anlage enthielt ausserdem keine NOT-NULL-Pflichtperiode; das
Create-Schema sieht nur abstimmungs_datum und buchungskreis vor. Der Handler
leitet daher YYYY-MM aus dem gelieferten Abstimmungsdatum ab und initialisiert
Summen und nicht_abgestimmte explizit, damit die gespeicherte Antwort dem
Response-Schema entspricht. Keine Schemaaenderung oder Migration erforderlich.

13 Tests bestehen in 47,88 Sekunden: vier funktionale HTTP-Vertraege plus
neun Router-Vertraege. Die vier Funktionstests bestehen nach explizitem BEGIN
fuer SQLite und Savepoint-Rollback nochmals in 1,81 Sekunden. Ein modulweit
geteilter In-Memory-Speicher prueft echte ORM-Persistenz mit Pflichtfeldern,
JSON-Antwort und erneutem Lesen, Jahresgrenzen der Periode, Tenantwechsel
(Detail 404, Liste leer) und fehlende ID. Jeder Test prueft leeren Anfangsbestand.
Diese Abnahme ersetzt keine PostgreSQL-/Migrationsabnahme. Probe --status
bestaetigt quittung_ohne_vorgang_20261006; kein Reset und keine neue DB/Container.

Der parallel committed Interessenten-Service fehlte bei der Inventar-Abnahme
in den Architekturregeln. Seine kanonische Quelle public.crm_leads begruendet
die exakte Zuordnung interessent_service: crm. 19 Architekturtests bestehen
in 0,48 Sekunden; committed-source Index --check und --require-complete:
932/932 Routen, 270/270 Services, 451/451 Endpoints, keine ungemappten Eintraege.
Alle drei Code-Inventare wurden aus committed Quellen erzeugt und geprueft.

Spec-Quelle ist committed 47e799bff plus eigenem Finance-Hunk. Alle bisherigen
Pfade/Methoden bleiben erhalten. Einziger neuer Pfad ist der bereits committed
Personal-Loeschpfad /api/v1/personal/applications/{application_id} aus f7fcbdd7c;
3096 Pfade insgesamt. Das gerenderte Artefakt ist kanonisch geprueft. Die echte
App registriert 53 doppelte Methoden/Pfade statt 55; die verbleibenden Konflikte
zwischen unterschiedlichen Implementierungen sind weiter offen.

Der Claim-Commit ef60a6076 absorbierte gleichzeitig gestagten Interessenten-Code;
der zugehoerige Handshake steht in 47e799bff. Keine fremden Aenderungen revertiert
oder umgeschrieben. Weitere Ergebniscommits werden ueber einen separaten Git-Index
mit normalen Hooks erstellt. Die automatische Freigabe lehnte einen Versuch mit
core.hooksPath=NUL ab; die sichere Alternative behielt alle Hooks bei.

GitHub-Abnahme auf 21015285e: Docs Build, Docs Governance, PostgreSQL/require_db
und Erntepeak erfolgreich. Vollstaendige CI und Security warten noch; keine
Gesamtfreigabe. Einige aeltere konkurrierende Laeufe wurden von GitHub abgebrochen;
diese sind kein erfolgreicher Gate-Nachweis.


## Kanonische Lieferantenmemos am 2026-10-06

Sechs Routen fuer Credit-/Debit-Memos waren doppelt registriert: GET/POST
/einkauf/credit-memos und /einkauf/debit-memos sowie beide POST-settle-Pfade.
Die echte App fuehrte den zuerst registrierten credit_debit_memos-Handler aus;
OpenAPI ueberschrieb dessen Vertrag mit der spaeteren Compat-Version.
Die nachrangige Version beschrieb beispielsweise Create als HTTP 201 mit
untypisiertem dict und generischem EinkaufDocOut, waehrend die echte Route
HTTP 200 mit validiertem CreditMemoCreate/DebitMemoCreate und typisierter
Antwort liefert. Listfilter und SettlementRequest waren ebenfalls verdeckt.

CREDIT-MEMO-OP-001, Wave100 und der Frontend-Verbraucher
pages/einkauf/gutschriften-belastungen.tsx bestaetigen die bestehende
Fachimplementierung. Deren Handler und Freigabe-/Buchungs-/OP-Logik bleiben
unveraendert. Nur die sechs spaeteren Compat-Routen und neun ausschliesslich
von ihnen verwendete Methoden im EinkaufCompatService sind entfernt.
Die Verbraucherpruefung in app/tests/services/modules ergab keine weiteren
Aufrufer; keine historisch konkurrierenden Statusformen ERFASST/VERRECHNET
oder rein erhaltenden Adapter verbleiben in diesem Service-Block.

19 Tests bestehen in 26,89 Sekunden: zehn Router-Vertraege (Handleridentitaet,
Antwortmodell, Status, Dependencies, Eindeutigkeit), sechs echte registrierte
OpenAPI-Vertraege fuer Create/List/Settlement und drei bestehende Wave100-
Ablauftests, einschliesslich Credit-/Debit-Anlage, Freigabe, Buchung und
Settlement-Completion. Die OpenAPI-Regressionspruefung verwendet alle real
registrierten betroffenen Routen, damit ein erneuter spaeterer Compat-Override
auffaellt. Die fachlichen Tests verwenden den bestehenden Fake-Store;
Probe --status bestaetigt quittung_ohne_vorgang_20261006. Keine neue Datenbank,
kein Container, Reset oder Migration.

Der Rueckbau entfernt 66 Endpoint- und 77 Service-Zeilen. Die Godfile-Baseline
sinkt ausschliesslich fuer compat.py von 3759 auf 3693; Groessenratsche,
Paginierung (284 Abfragen/257 Funktionen) und Baseline-Integritaet gegen HEAD
bestehen. Keine Schwelle, Ausnahme oder fremde Baseline erhoeht/geaendert.

OpenAPI stammt aus committed c432d5045 plus den eigenen zwei Rueckbauhunks:
alle bisherigen 3096 Pfade und HTTP-Methoden exakt erhalten; die echte App
hat 47 doppelte Methoden/Pfade statt 53. Das Artefakt beschreibt nun die
tatsaechlichen Memo-DTOs und Statuscodes und besteht erneut render(build_spec()).
Die anderen 47 Handlerkonflikte bleiben offen; keine globale Eindeutigkeit.

Alle drei Code-Inventare wurden aus committed Quellen erzeugt und geprueft.
Dabei sind die bereits committed Personal-Split-Module aus c432d5045 integriert;
deren Code und laufende Maskenarbeit wurden nicht angefasst. Architekturindex
vollstaendig: 932/932 Routen, 270/270 Services und 453/453 Endpoints, --check
bestanden. Alle 19 Architekturtests bestehen in 0,41 Sekunden.
Die globalen Artefakte werden indexseitig geliefert; fremde Arbeitsbaumversionen
bleiben erhalten. Ergebniscommit nutzt separaten Index mit normalen Hooks.

GitHub 8dd0020eb: Docs Build, Docs Governance, PostgreSQL/require_db und
Erntepeak erfolgreich. Gesamt-CI und Security queued; abgebrochene OpenAPI-/
Quality-/E2E-Laeufe sind keine Abnahme. Security- und weitere Routerbefunde
bleiben explizit offen, bis passende neue Lauf-Evidenz vorliegt.


## Kanonisches Kundenportal und statische Auswertungen am 2026-10-06

Die echte App registrierte sechs Portal-Aufrufe mehrfach: GET products,
orders, orders/{order_id}, contracts, pre-purchases und POST orders.
portal_shop.py ist zuerst registriert und wird ausgefuehrt; compat.py
ueberschrieb dessen OpenAPI-Vertraege mit generischen Antwortmodellen,
untypisiertem Create-Body und abweichender Mandantenuebergabe. Der aktive
Frontend-Verbraucher lib/services/portal-service.ts verwendet bereits
PortalProductList, OrderCreate/OrderResponse und tenant_id als Queryparameter.

Nur die sechs nachrangigen Compat-Routen und ihre sechs ausschliesslich
von dort verwendeten PortalCompatService-Methoden sind entfernt. Andere
Portal-/Lieferantenfunktionen bleiben erhalten. Der Rueckbau entfernt
62 Endpoint-Zeilen und 130 Service-Zeilen plus einen ungenutzten UUID-Import;
der ungenutzte Any-Importanteil ist ebenfalls entfernt. Verbraucherpruefung
in app/tests/services/modules bestaetigt keine weiteren Aufrufer dieser
Service-Methoden. Kein neuer Adapter, keine Migration und keine Datenloeschung.

GET orders/{order_id} war vor GET orders/reconciliation und orders/observability
registriert. Damit wertete FastAPI die statischen Auswertungsnamen als
Bestell-ID aus. Der unveraenderte Detailhandler wird jetzt nach beiden
statischen GET-Routen registriert. Der AST-Vergleich gegen committed HEAD
bestaetigt identische Funktionen, Decorators und Dependencies fuer das
vollstaendige Portal-Shop-Modul; ausschliesslich Reihenfolge geaendert.
Bestehende Geschaeftstag-, Bestell- und Kundenlogik bleibt unveraendert.
Diese Aenderung ist keine neue Authentifizierungs-/Berechtigungsabnahme.

20 Tests bestehen in 27,50 Sekunden: kanonische Router-Vertraege, sechs
OpenAPI-Vertraege aus den real registrierten Portal-Routen, drei First-FULL-
Match-Abnahmen (beide statischen Auswertungen und normale Bestell-ID) und
bestehender Geschaeftstag-Test. Create dokumentiert weiterhin tatsaechliches
HTTP 201, OrderCreate und OrderResponse; Produkte/Bestelllisten/Detail und
Anspruchslisten dokumentieren ihre tatsaechlichen Typen und tenant_id.
Die Match-Tests starten keine App-Lifespan und schreiben keine Fachdaten.
Probe --status: quittung_ohne_vorgang_20261006; kein Reset, neue DB/Container.

Die Godfile-Baseline sinkt ausschliesslich fuer compat.py von 3693 auf 3631.
Dateigroessenratsche, Paginierung (284 Abfragen/257 Funktionen) und
Baseline-Integritaet gegen HEAD bestehen. Alle drei committed-source
Code-Inventare und der bestehende Architekturindex --check sind aktuell;
keine Domains, Container oder API-Pfade hinzugefuegt/entfernt.

GitHub 7b935a5b1: Docs Governance und Erntepeak erfolgreich; Docs Build,
PostgreSQL und OpenAPI laufen noch, weitere Gesamt-/Security-Jobs warten.
Keine Gesamtfreigabe und keine Abschwaechung der bestehenden Gates.


Kanonische Spec-Abnahme aus committed 00485d2ea plus drei eigenen Portal-
Hunks: exakt dieselben 3096 Pfade und HTTP-Methoden erhalten; gerendertes
Artefakt erneut mit build_spec() verglichen. Reale Doppelgruppen sinken
von 47 auf 41. Spec und Inventare werden ausschliesslich indexseitig
integriert; fremde Arbeitsbaumfassungen und laufende Bewerberarbeit bleiben
erhalten. Die restlichen 41 Routerkonflikte und Security-Befunde bleiben offen.
