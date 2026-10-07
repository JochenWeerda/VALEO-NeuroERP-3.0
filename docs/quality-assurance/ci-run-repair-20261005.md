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


## Mandantengebundene Futtermittel-Leselisten am 2026-10-06

Die zuerst registrierten Compat-GETs fuer Einzelfutter/Mischfutter lasen alle
aktiven ArticleModel-Datensaetze ohne tenant_id-Filter und ohne READ_ROLES.
Spaeter registrierte Futter-Stamm-Handler verwenden andere Fachmodelle; die
Mischfutter-Fachliste hatte selbst ebenfalls keinen READ_ROLES-Guard.

Die Verbraucherpruefung zeigt, dass lib/api/futter.ts und seine Listen noch
die bestehende Artikelprojektion verwenden. Ein sofortiger GET-Modellwechsel
wuerde deren Feldvertrag brechen. Deshalb wird in diesem Sicherheits-Slice
nur die vorhandene Projektion abgesichert: beide Service-Listen verwenden
ArticleModel.tenant_id == self.tenant_id, behalten Aktivfilter, Limits 500/200
und ihre Antwortfelder. Beide tatsaechlich ausgefuehrten GETs pruefen den
bestehenden get_current_user/READ_ROLES-Vertrag vor dem Datenbankzugriff.
Die Mischfutter-Fachliste erhaelt dieselbe fehlende Lesepruefung.

Die zwei bisherigen Compat-GET-Funktionen sind als unveraenderte Antwort-
projektion nach futter_read.py extrahiert und am bisherigen Registrierungspunkt
in compat.router eingebunden. Keine neue Fachfunktion/oeffentlicher Pfad;
keine zusätzliche Datenhaltung oder Adapter fuer historische Entwicklungsdaten.
Compat-Godfile-Grenze sinkt von 3631 auf 3621, statt sie fuer Guards anzuheben.

15 Tests bestehen in 30,21 Sekunden: bestehende kanonische Router-Vertraege
und fuenf fokussierte Sicherheitsabnahmen. Die First-FULL-Match-Funktion der
echten main:app wird ausgewaehlt und ausgefuehrt: falsche Rolle liefert 403
vor DB-Zugriff, erlaubte Rolle fuehrt die tenantgebundene, aktive und begrenzte
Artikelabfrage aus. Bestehende Antwortfelder artikelnummer/preis sind geprueft.
Zusaetzlich wird die Mischfutter-Fachliste mit einer fachfremden Rolle abgewiesen.
QueryRecorder verifiziert reale SQL-Ausdruecke; kein Datenbank-Fachschreibtest.
Probe --status meldet bereits die fremde Revision
bewerbung_statuswoerterbuch_20261006. Dieser Slice migriert oder setzt sie nicht
zurueck und legt keine DB/Container an.

Groessen-, Paginierungs- (284 Abfragen/257 Funktionen) und Baseline-Integritaets-
gate bestehen. Drei committed-source Code-Inventare sind aktuell. Architektur-
index --require-complete und --check: 932/932 Routen, 270/270 Services,
454/454 Endpoint-Module. Neues internes Endpoint-Modul nutzt bestehende
Futter-Prefix-Zuordnung; keine Domänengrenze oder Container geaendert.

Offen: zwei konkurrierende GET-Modelle, Compat-Einzel-/Bulk-Loeschpfade mit
Artikelmodell und fehlendem Fach-Guard. Einzel-DELETE verdeckt den Fachhandler
trotz unterschiedlicher Pfadparameternamen. Der naechste Rueckbau muss
Frontend-Datentypen, Stammlisten, Einzel-/Bulk-Loeschung und kanonischen Feed-
Katalog gemeinsam harmonisieren. Keine abgeschlossene Schreibberechtigungs-
oder globale Futter-Abnahme behauptet.

GitHub 7017d6660: Docs Governance und Docs Build erfolgreich; PostgreSQL laeuft,
weitere Jobs queued. Gesamt-CI und Security bleiben offen. Keine Gate-Ausnahme.


Spec-Abnahme aus committed 59fa73073 plus vier eigenen Sicherheitsdateien:
alle bisherigen 3096 Pfade/Methoden exakt erhalten und erneutes render(build_spec())
kanonisch. 41 Doppelgruppen unveraendert; kein verfruehtes Kanonisierungsversprechen.
Artefakte nur indexseitig integriert, fremde Arbeitsbaumfassungen erhalten.


## Integration der parallelen Bewerbungs-Lieferung

15fc04c88 wurde waehrend der Futter-Abnahme committed und fuegt einen
Bewerbungsservice, eine Migration und GET auf dem bestehenden Personal-
Detailpfad hinzu. Dessen Fachcode/Migration/Masken wurden nicht angefasst.
Alle drei Code-Inventare werden erneut aus committed 817987519 erzeugt;
die exakte Zuordnung bewerbung_service: hr folgt domain_hr.applications.
Architekturindex --require-complete und --check bestehen mit 932/932 Routen,
271/271 Services und 454/454 Endpoint-Modulen. 20 Architektur-Vertragstests
bestehen in 0,51 Sekunden. Artefakte werden indexseitig integriert, fremde
Arbeitsbaumversionen bleiben erhalten. Die zusaetzliche Integration schliesst
keine der dokumentierten Futter-Schreib-/Modellluecken.


Die finale Spec aus committed 817987519 besteht erneut render(build_spec()).
Alle 3096 Pfade bleiben erhalten; alle alten Methoden bleiben erhalten und
exakt GET /api/v1/personal/applications/{application_id} wird aus 15fc04c88
zusaetzlich dokumentiert. 41 doppelte Gruppen bleiben offen. Kein fremder WIP
wurde fuer die Generierung importiert. Zusammen 15 Futter-/Router- und
20 Architekturtests bestanden; keine vollstaendige CI-/Security-Freigabe.


## Tabellenkatalog: direkter CLI-Start

Quality Gate 37425708197 auf 25d1dcd92 bricht beim direkten Start von
generate_table_catalog.py --check vor Datenbankzugriff ab: ModuleNotFoundError
fuer scripts. Der Generator setzt jetzt seinen absoluten Repository-Pfad vor
den lokalen Hilfsmodul-Imports auf sys.path. Kein Import-Fallback, kein
Katalog-/Tabellen-/Schemawechsel und keine Gate-Abschwaechung.

Zwei echte Unterprozessvertraege starten die CLI unter python -I mit --help,
einmal aus dem Repository und einmal aus tmp_path. Rueckgabecode, vorhandene
--check-Option und fehlerfreier Import werden geprueft. Der isolierte Modus
schliesst einen zufaellig geerbten PYTHONPATH als vermeintliche Reparatur aus.
26 Katalog-/Lineage-/Besitz-Unitvertraege bestehen in 1,60 Sekunden. Zwei
bestehende DB-Integrationstests wurden mit -m 'not integration' ausgewaehlt
ausgeschlossen; die erste unselektierte Ausfuehrung meldete nur deren fehlende
require_db-Fixture bei --noconftest (26 bestanden, zwei Setup-Fehler). Keine
DB-Integrationsabnahme behauptet; keine DB, Migration oder Docker-Ressource.

Auf 25d1dcd92 bestehen OpenAPI, PostgreSQL, beide E2E-Pruefungen, Erntepeak,
Docs Governance, Docs Build und Full Security Agent. Quality-Frontend bleibt
mit zwei Fehlern bei 946 bestandenen Tests offen: Schulungen-Altvertrag nurPsm
und drei statt einer zentralen Worklist-Ueberschrift. Security Scan
37425707748 und Service Security 37425707763 bleiben fehlgeschlagen; Gesamt-CI
war bei Sichtung noch in Arbeit. Dieser Fix ist lokal abgenommen; seine neue
Actions-Abnahme und die unabhaengigen Restbefunde bleiben offen.


## Multichannel: ungenutzte Plattform-SDKs entfernt

Service Security 37425707763 scheitert ausschliesslich im Audit von
services/crm-multichannel/requirements.txt; alle anderen Service-Audits,
Inventar und crm-ai bestehen. Der heruntergeladene Rohbericht umfasst 62
Linux-Pakete und genau oauthlib 3.3.1 / PYSEC-2026-4114
(CVE-2026-49265, GHSA-xpv3-w29h-x7cv), ohne vorhandene reviewed decision.
Quelle: [Hersteller-Advisory](https://github.com/oauthlib/oauthlib/security/advisories/GHSA-xpv3-w29h-x7cv).
Scannerbericht nennt 4.0.0 als Fix; Herstellerseite nennt inzwischen 3.3.2.
Dieser Slice haengt nicht von einer dieser Upgrade-Aussagen ab.

Die gesamte Dienstquelle, inklusive Migrationen und dynamischer Ladepfade,
verbraucht keines der sieben SDKs facebook-sdk, tweepy, linkedin-api,
slack-sdk, stripe, shopifyapi und woocommerce. Plattformnamen sind lediglich
Enum-/Schemawerte oder Beispielantworten; spezifische Connector-Router sind
nur auskommentiert. Deshalb werden ungenutzte Pins entfernt statt OAuth-Major-
Upgrades oder not_affected-Ausnahmen einzufuehren (ADR-071/User-Altlastenfreigabe).
README kennzeichnet den tatsaechlichen Stand: Beispiel-/Platzhalterantworten,
fehlende Webhook-Signaturpruefung und keine garantierte externe Zustellung.
Fachcode, Settings, DB-Schemas, API-Pfade und Antworten bleiben unveraendert.

Abnahme:

- python scripts/check_service_import_pins.py services/crm-multichannel:
  keine fehlenden Pflicht-Pins.
- python scripts/audit_service_dependencies.py --manifest
  services/crm-multichannel/requirements.txt: komplette transitive Aufloesung
  unter Windows/Python 3.11, pip-audit 2.10.1; 48 Pakete, null Befunde,
  Scanner und unveraendertes Security-Gate Exit 0. oauthlib ist entfallen.
  Der Linux-Ausgangsbericht und Windows-Abnahme sind verschiedene Plattformen;
  62 auf 48 wird deshalb nicht als exakte Image-Groessenreduktion verkauft.
- Dienststart im eigenen Service-Arbeitsverzeichnis mit MetaPathFinder, der
  die sieben SDK-Module sowie oauthlib/requests_oauthlib aktiv sperrt:
  17 registrierte Routen, 12 OpenAPI-Pfade, GET /health per echter ASGI-
  Verarbeitung HTTP 200 mit healthy/crm-multichannel. Null SDK-Imports und
  null DB-Verbindungen. Lokaler Probe: artifacts/ci-multichannel-no-sdk-probe.py.
  Engine-URL nutzt absichtlich einen unerreichbaren lokalen Port; kein SQL.
- 9 Audit-Runner- und 9 Security-Gate-Regressionen bestanden (0,369/0,430 s).
  Keine Schwellen/Baselines, Workflows oder Entscheidungen abgeschwaecht.

Die erste Startprobe aus dem Repository las dessen fremde .env und scheiterte
an Extra-Settings. Danach korrekt im Service-cwd ausgefuehrt; keine Settings-
Aenderung vorgenommen. Eine erste Pfadzahl verwechselt Pfade mit registrierten
Routen; tatsaechlicher unveraenderter Vertrag ist 12 Pfade/17 Routen.
Keine Datenbank, Migration, Dockerinstanz oder Installationen in der globalen
Laufzeit. Neue Linux-/GitHub-Abnahme bleibt nach Push ausstehend. Service
Security 37428294647 auf d52139d83 ist noch vor diesem Fix rot; weitere
Frontend-, Container-/Node-Security- und Futter-Befunde bleiben offen.


## Katalog-Drift offen; committed Bewerbungs-Loeschlauf integriert

Quality Gate 37428294896 bestaetigt den vorherigen Generator-Importfix und
meldet jetzt echte Abweichung beider physischer Katalogdateien. Gemeinsamer
valeo_probe --status laeuft auf Port 5432 in Timeout. User startet Docker
Desktop wieder; erneute lesende Statuspruefung bleibt Timeout, Engine-
Containerstatus liefert zunaechst HTTP 500, danach keine Antwort. Lang
wartende reine Leseabfragen abgebrochen. Keine neue DB/Dockerinstanz, kein
Reset, Start oder Migration, keine Fachtests auf der Entwicklungsdatenbank.

Ein geplanter optionaler Driftexport aus derselben CI-Datenbank mit
GitHub-Artefaktupload wurde durch automatische Freigabepruefung wegen
Uebertragung interner Schema-Metadaten abgelehnt. Es fand keine Uebertragung
oder Commit dieses Vorschlags statt. Die drei eigenen uncommitteten Hunk-
Bloecke in Generator, Tests und Workflow sind entfernt; Direktstart-Fix
bleibt unveraendert. Keine Umgehung, Export- oder Gate-Ausnahme. Bestehender
versionierter Tabellenkatalog unveraendert und Drift ausdruecklich offen.

Unabhaengige Integration: paralleler committed b9a71eab4 liefert den
Bewerbungs-Loeschlauf. Spec/Inventare wurden aus genau dieser Backendquelle
erzeugt; Fachcode, Migration, Masken und laufende neue Einwilligungsarbeit
nicht angefasst. Exakte Servicezuordnung bewerbung_loeschlauf_service: hr
folgt dessen domain_hr-Tabellen. 21 Architekturtests bestehen (1,75 s).
Drei Code-Inventare sind aktuell; Architekturindex --require-complete
und --check: 932/932 Routen, 272/272 Services, 454/454 Endpoint-Module.

Spec-Abnahme erhaelt alle alten 3096 Pfade und Methoden und erlaubt exakt:

- GET/PUT /api/v1/personal/applications/aufbewahrung
- GET /api/v1/personal/applications/loeschlauf/faellig
- GET /api/v1/personal/applications/loeschlaeufe
- POST /api/v1/personal/applications/loeschlauf

3100 Pfade; render(build_spec()) erneut kanonisch. 41 doppelte
Pfad-/Methodengruppen bleiben unveraendert offen. Artefakte nur indexseitig
aus committed Quelle; fremde Arbeitsbaumfassungen bleiben erhalten.
Kein API-Gate abgeschwaecht; tatsaechliche Katalogerneuerung benoetigt
weiterhin den erreichbaren bestehenden gemeinsamen Pruefstand.

Auf 22bf4b927 ist Service Security 37449627295 vollstaendig erfolgreich
(Multichannel-Fix in Linux/GitHub bestaetigt). PostgreSQL, kritische E2E,
Doku und Superglue bestehen. Smoke, Quality, Gesamt-CI und andere
Security-Pruefungen sind rot; neue Integrationsabnahme nach Push ausstehend.


## Futter-Loeschung: Schreibrolle und strikte Mandantentrennung

Die vier tatsaechlich zuerst ausgefuehrten Artikel-Einzel-/Bulk-
Loeschhandler in compat.py pruefen get_current_user/WRITE_ROLES vor
Service-/DB-Zugriff. Auch der nachrangige Mischfutter-Fachdelete hat den
bisher fehlenden Guard. Keine neue Rolle, Route oder Antwortform; der
Frontend-Artikelvertrag bleibt bestehen. Andere Futter-Schreibpfade und
die Katalog-/Frontend-Modellmigration sind weiterhin offene Folgeslices.

soft_delete_artikel bindet die SQL-Abfrage obligatorisch an self.tenant_id.
Artikel ohne Mandantenzuordnung werden nicht mehr mitgeloescht; fremde und
null-Mandanten werden wie unbekannte IDs als missing/404 behandelt. Fehlender
Mandant wirft ValidationFailedError vor DB-Zugriff. Der redundante externe
tenant_id-Parameter wird nach Abgleich aller vier Verbraucher entfernt,
so dass die Serviceinstanz die einzige Mandantenquelle ist. Der alte
_soft_delete_futter_articles-Helfer hat keine Verbraucher und ist entfernt.

37 Tests bestehen in 299,22 Sekunden inklusive main-Import: 22 neue
Loesch-/SQL-/Rollen-/Dispatchvertraege plus 15 bestehende Listen-/Router-
Vertraege. First-FULL-Match der echten main:app wird ausgewaehlt; Leser
und fachfremde Rolle erhalten 403 bevor NoDatabase ueberhaupt eine Abfrage
akzeptiert. Erlaubter Writer erreicht den echten Service mit SQLAlchemy-
SQLite-Session; nur eigener Artikel wird deaktiviert. Fremde/null/fehlende
Einzel-ID liefert 404, Bulk liefert unveraenderte requested/deleted/
missing_ids/errors. Ein gemeinsamer SQLite-In-Memory-Speicher fuer die
Suite; explizites BEGIN plus Session-Commit innerhalb Savepoint und aeusserer
Rollback isolieren alle Tests. Keine PostgreSQL-Fachschreibtests, neue
Datenbank oder Dockerinstanz. Initiale Pytest-Collectionwarnung durch den
Hilfsklassennamen TestBase beseitigt (FeedDeleteBase), unveraenderte Logik.
Bestehende Starlette/httpx-Deprecation ist kein neuer Funktionsfehler.

Groessengate bestanden, ausschliesslich compat.py-Grenze 3621 auf 3589
gesenkt. Paginierungs-Alt-Eintrag des entfernten Helfers 1 auf 0 entfernt,
283 Abfragen/256 Funktionen; Baseline-Integritaet gegen ed5650ad2 bestanden.
Keine Ausnahme oder Schwellenanhebung. 22 Architekturtests bestehen
(3,34 s); exakte bewerbung_einwilligung_service: hr-Zuordnung integriert
parallel committed b7b6a042c. Dessen fehlende DB-Abnahme bleibt offen;
Fachcode, Migration und Masken werden nicht angefasst. Inventare/Index
aus committed 173a80fbc plus drei eigenen Sicherheitsdateien: 932/932
Routen, 273/273 Services, 454/454 Endpoint-Module; keine neue Domänengrenze.

Gemeinsamer valeo_probe --status weiterhin Timeout; Docker-Engine HTTP 500,
Windows-Dienst com.docker.service ist gestoppt. Start-Service wurde versucht,
scheitert aber am Windows-Recht zum Oeffnen dieses Dienstes. Kein Restart
laufender Ressourcen, Start neuer Container, Reset oder Migration.
Katalog bleibt unveraendert und Drift offen. Kein neuer CI-Schema-Upload.

GitHub auf ed5650ad2 bestaetigt OpenAPI, Service Security, PostgreSQL,
beide E2E, Full Security Agent und Doku. Quality (Katalog plus zwei
Frontend-Tests), anderer Security Scan und Gesamt-CI weiterhin rot.


Finale OpenAPI-Abnahme aus committed 173a80fbc plus drei eigenen
Sicherheitsdateien: alle bisherigen 3100 Pfade und HTTP-Methoden erhalten;
exakt neuer /api/v1/personal/applications/{application_id}/einwilligung
mit GET/POST/DELETE aus b7b6a042c integriert (3101 Pfade).
render(build_spec()) erneut kanonisch, 41 Routerkonflikte unveraendert.
Fuer die vier bisherigen Futter-Loeschpfade wurden responses und
requestBody exakt gegen vorherige Spec verglichen, alle drei Bulk-DTO-
Schemata ebenfalls identisch. 59 Tests insgesamt bestanden. Generierte
Artefakte werden nur aus dieser Quelle indexseitig integriert; fremde
Arbeitsbaumversionen bleiben erhalten. Fehlende Einwilligungs-DB-Abnahme
und Katalog-/Frontend-Modellharmonisierung werden damit nicht geschlossen.


## Sharp-Herstellerfix 2026-10-06

Sharp-Herstellerfix 2026-10-06: Root-Override und direkter Procurement-Pin ^0.35.4 -> ^0.35.5; Lock ausschliesslich Sharp-/libvips-Familie (je 54 geaenderte Schluessel in packages/snapshots) und Procurement-Importer. Automatische lightningcss/detect-libc-Nebenaenderung entfernt. Frozen-Lock aller 36 Workspaces offline bestanden. Echter isolierter Windows-Nativtest: Sharp 0.35.5, libvips 8.18.7, librsvg 2.63.2; SVG -> skalierter PNG, Dimensionen, rote RGB-Pixel, JPEG und Ablehnung ungueltiger Bilddaten bestanden. Keine Codeimporte im Procurement-src; tsup external erhalten. Voll-Audit: Sharp-Advisory entfallen, weiterhin 2 high (node-forge/braces), 1 critical (shell-quote), 14 moderate/1 low; Exit 1, keine Ausnahme. Keine lokale Docker-/Linux-Scanfreigabe behauptet. Probe --status lesend erreichbar auf bewerbung_einwilligung_20261006; keine neue DB/Container, Migration, Reset oder Fachschreibtests. Fremde Katalog-/Frontend-WIP erhalten. GitHub 1a77ee718: Docs/OpenAPI/PG/beide E2E/Service Security/Full Security Agent/Erntepeak erfolgreich; Quality/Security Scan/Gesamt-CI fehlgeschlagen. Neue Actions-Abnahme des Fixes ausstehend.

Ausgangslauf: [Security Scan 37502096089](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/37502096089). Herstellerfix: [GHSA-wq5f-xc86-pv6w](https://github.com/advisories/GHSA-wq5f-xc86-pv6w).


## Shell-Quote-Herstellerfix 2026-10-06

Shell-Quote-Abnahme 2026-10-06: Zentraler Override exakt 1.11.0 statt ^1.9.0; Lock ersetzt 1.10.0 durch geprueften Herstellerfix mit neuer Integritaet und drei Verbraucherreferenzen (React-Native CLI, Detox, React-Devtools). Keine anderen Pakete/Importer/Overrides geaendert; automatische lightningcss/detect-libc-Nebenaenderung entfernt. Isolierter Herstellertest bestanden: acht Injection-Versuche (LF, CR, U+2028, U+2029 jeweils unmittelbar und spaeter nach Kommentar) werfen TypeError; zwei normale quote/parse-Roundtrips mit Sonderzeichen, gueltiger Kommentar und Ablehnung ungueltigen Kommentars bestanden. Frozen-Lock aller 36 Workspaces offline bestanden. Finaler vollstaendiger Production-Audit auf exakt 1.11.0: 0 critical, 2 high (node-forge/braces), 14 moderate, 1 low; Sharp und Shell-Quote nicht mehr betroffen. Audit weiterhin Exit 1 wegen verbleibender Befunde; keine Ausnahme oder Gate-Abschwaechung. Keine neue Datenbank/Container, Reset, Migration oder fremde Fach-/Frontend-WIP. Neue GitHub-Abnahme ausstehend.

Herstellerentscheidung: [GHSA-pqg4-j6r4-53mv](https://github.com/advisories/GHSA-pqg4-j6r4-53mv). Der erste Resolver waehlte mit ^1.11.0 bereits 1.12.0; final exakt die funktional gepruefte 1.11.0 gepinnt und Audit wiederholt.


## Fassungsintegration und lokaler Katalogabgleich 2026-10-07

Fassungsintegration 2026-10-07: Spec/Inventare aus committed 0dbd76e6f (Backend ac69c26f0) ohne fremde Arbeitsbaumquellen. Alle 3101 bisherigen Pfade/Methoden erhalten; genau zwei neue Erklaerungspfade mit GET/POST und GET {fassung}, jetzt 3103 Pfade. EinwilligungIn verlangt fassung >=1 statt freiem einwilligungstext; render(build_spec()) kanonisch. 41 bestehende Routerkonflikte bleiben offen. Drei Code-Inventare --check und Architekturindex --check --require-complete bestanden: 932 Routen/273 Services/454 Endpoint-Module. Gemeinsamer Probe lesend auf bewerbung_erklaerung_fassung_20261006; Katalog aus committed Generator/Backend zweimal geerntet und --check bestanden, 659 Tabellen (vorher 641), 41 neue und 23 entfallene Tabellennamen gegen altes Artefakt. Keine Datenbankaenderung, Migration, Reset, neue DB/Container oder CI-Schema-Upload. Lokal bestandener Katalogabgleich ist keine frische CI-Schemaabnahme; diese folgt im neuen Lauf. Fremde Frontend-/Generator-/Spec-WIP erhalten. GitHub ac69c26f0: PG/Service Security/Full Security Agent/kritische E2E/Doku-Governance/Erntepeak erfolgreich; Docs Build wegen Migration-Inventar, OpenAPI und Quality wegen fehlender Specintegration rot. Zwei Frontend-Testbefunde, Security, Smoke/UAT/Gesamt-CI bleiben offen.


## Vollstaendiger Recruiting-Rollenschutz 2026-10-07

Personal-Rollenschutz abgeschlossen: Alle 16 Bewerbungswege verwenden die zentrale Rollen-Factory mit get_current_user vor DB-Zugriff. Acht Lesepfade, vier Bearbeitungswege, vier Verwaltungswege; manager hat keine Verwaltungsrechte, fachfremde Rollen werden abgewiesen. 161 Rollen-/Token-/Dispatch-Vertraege plus 163 bestehende Bewerbungs-/Loeschlauf-/Einwilligungs-/Fassungsvertraege auf gemeinsamem Probe: 324 bestanden, null Skip, Exit 0 in 65,99 s. Strukturvergleich alle Handlerkoerper/Signaturen/Tenantfilter unveraendert. main.app bestaetigt alle 16 als erste FULL-Matches; 3103 Pfade und saemtliche DTO-/Request-/Response-/Parametervertraege exakt erhalten, kanonische Spec. 41 Routerkonflikte unveraendert offen. Drei Inventare und Architekturindex --check bestanden (committed Frontend-Routen aus 81407bc6d integriert: 935 Routen/273 Services/454 Endpoint-Module). Katalog 659 Tabellen mit aktueller committed Masken-Lineage lesend geerntet, --check bestanden. Fremde Masken-/Aktions-WIP erhalten; keine neue Datenbank/Container, Migration oder Reset. Alte Rollen-Handshakes in vier QA-Dokumenten nachgezogen; zentrale Rollen-QA erklaert Akteursidentitaet, Bewerber-Selbstwiderruf und UI-Rollensteuerung als separate offene Punkte. Initiale lokale Teilsuite-Coverage/Diagnoseabsturz dokumentiert, final gezielt --no-cov; globaler CI-Gate unveraendert. GitHub bea6fbbdb Docs Build/Governance/OpenAPI/PostgreSQL erfolgreich; Quality/kritische E2E/Service Security abgebrochen, Smoke/Security/Gesamt-CI fehlgeschlagen. Neue Abnahme dieses Fixes ausstehend.

Details: [Rollenvertrag](personal-bewerbungen-rollenschutz-20261007.md).
