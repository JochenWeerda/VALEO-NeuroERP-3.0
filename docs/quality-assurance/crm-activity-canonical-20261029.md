---
title: CRM-Aktivitaeten kanonisieren — QA und Betriebsabnahme
type: reference
audience: [entwickler, qa, betrieb]
owner: domain/crm
status: in-arbeit
last_reviewed: 2026-10-29
version: 1.2.0
description: Vorlaeufige Pruefnachweise, offene Betriebspruefungen und Abnahmekriterien fuer den kanonischen CRM-Aktivitaetsspeicher.
---

# CRM-Aktivitaeten kanonisieren — QA und Betriebsabnahme

## Ziel und Status

`domain_crm.activities` ist der kanonische CRM-Aktivitaetsspeicher. Die
Fachschreibwege verwenden den tenantgebundenen Command-Service. Diese QA-Seite
haelt den gezielten Backend-/Frontend-Nachweis und noch offene Gates fest. Es
wird keine Gesamtsuite-, Live-SSO- oder Produktionsabnahme behauptet.

## Fach- und Sicherheitsvertrag

- REST, MCP, CLI und Studio verwenden denselben Create/Update/Delete-Vertrag.
  Der Service prueft Rolle, verifizierten Mandanten und Subjektidentitaet vor
  der Mutation. Identitaet ist serverseitig; Payload-Identitaet wird nicht als
  Berechtigungsnachweis verwendet.
- Update und Delete verlangen `expected_version`; die Zielzeile wird gesperrt.
  Idempotenz wird im bestehenden `public.mcp_tool_executions`-Register an Actor
  und Payload-Hash gebunden. Fachaenderung, Beleg, Audit und Outbox gehoeren zur
  selben Transaktion.
- Agentenschreiben bleiben bis zur ausdruecklichen Freigabe einer konkreten
  Capability deaktiviert.
- `domain_crm.activities` bleibt als ausdrueckliche Service-Ausnahme in
  `docs/admin/rls-exceptions.json`. RLS ist nicht als aktiv nachgewiesen.
- Der DSGVO-Erasure-Workflow ist ein gesonderter, rechtlich begruendeter
  Loeschpfad. Er stellt keine gewoehnliche CRUD-Mutation dar und bleibt als
  kontrollierter Workflow separat dokumentiert. Der direkte Activity-Loeschschritt
  darf nur den verifizierten Mandanten treffen; ein Match mandantenloser Zeilen
  ist entfernt. Das ersetzt keine allgemeine Aktivierung von RLS.
- Kontakt- und Farm-Masken, die zuvor als Aktivitaetsformular fehlverdrahtet
  waren, schlagen geschlossen fehl und melden keinen Aktivitaetserfolg.
- Die direkten lokalen Activity-Seeds und die ungenutzte lokale ORM-/DTO-Familie
  sind entfernt. Kontakt-, Lead- und Farmprofil-Seeds bleiben erhalten; die
  Seed-Bereinigung fuehrt keine Tabellenloeschung aus.
- Die Activity-Abfrage in `app/domains/crm/services/daily_report_service.py`
  bleibt dormant und ist ein offener Umstellungs-/Stilllegungspunkt; sie gilt
  nicht als auf den kanonischen Speicher umgestellt.

## Vorlaeufige Evidenz

- Gezielt ausgefuehrte Backend-Suites (Activity Contracts, Migration SQL,
  Canonical SQL und Studio List Presets): **85 bestanden**, eine
  Starlette-Deprecation-Warnung, 78,57 Sekunden.
- Frontend: **65 Tests in 9 Dateien bestanden**; regulaeres
  `tsc --noEmit` bestanden. Der Produktionsbuild ist erfolgreich abgeschlossen.
- Evidenzbilder: 24 synthetische PNGs (18 Haupt- und 6 Zusatzansichten) mit
  Ergebnis-/Scrollnachweisen unter
  `docs/quality-assurance/evidence/crm-activity-canonical-20261029/`. Sie
  belegen keine reale Bedienung mit Live-SSO.
- Opportunity- und Kundenmasken verwenden effektive Human-only- und
  Idempotenz-Flags. Opportunity REST/MCP/CLI wurde auf einen Effekt geprueft.
- DSGVO-Erasure verwendet den verifizierten Tenantfilter. Der gesonderte
  Erasure-Weg bleibt eine rechtliche Ausnahme von gewoehnlichem CRUD.
- Gemeinsamer Pruefstand vor/nach Rollback unveraendert auf
  `rls_domain_shared_20261027`; null fremde Sessions. Die Herkunftsspalte ist
  nach dem transaktionalen Rollback nicht vorhanden. Das bestaetigt keinen
  Live-DDL-Einsatz.
- Diese gezielten Ergebnisse sind keine vollstaendige CI-/Gesamtsuite und
  belegen weder Live-SSO noch Produktionsbereitschaft.
- Verwaiste lokale Activity-Symbole sind nach der Verbraucherpruefung entfernt;
  die Activity-Abfrage in `app/domains/crm/services/daily_report_service.py`
  bleibt dormant und offen.
- Die zuvor erfasste Entwicklungsinventur (nur Metadaten/Anzahlen) meldete
  `domain_crm.activities` 0, `public.crm_activities` 0,
  `public.crm_core_activities` 1 bekannten Seed und
  `domain_crm.crm_activities` 0. Das ist eine Momentaufnahme, kein Nachweis fuer
  andere Umgebungen oder Vollstaendigkeit der partiellen Reparaturquelle.

## Uebernahme- und Bedienkriterien

1. Status und Typ werden strikt normalisiert; nicht geplante Faelligkeit bleibt
   `NULL`; Version, Autor, drei JSONB-Stringlisten, Rohquellensnapshot, Herkunft
   und Hash bleiben erhalten.
2. Import aus `public.crm_activities`, `public.crm_core_activities` und
   `domain_crm.crm_activities` erfolgt nur fuer registrierte Mandanten,
   kollisionsfreie IDs und ohne Abschneiden oder verletzte Fremdreferenzen.
3. Listen, Details, Kalender und Opportunity-Aktivitaeten bleiben tenantgebunden
   und verwenden die kanonischen Aliase beziehungsweise den gemeinsamen
   Resolver und Command.
4. Alte Tabellen bleiben intakt, bis Verbraucher stillgelegt, Daten abgeglichen
   und Rollback-/Abnahmefenster dokumentiert sind.

## Migration und Rollout

Vor einem Schemaeinsatz sind Status und Nutzung des vorhandenen gemeinsamen
`valeo_probe` zu pruefen. Keine neue Datenbank oder Container erstellen und
keinen gemeinsamen Pruefstand zuruecksetzen. Das Migrationsrehearsal ist
transaktional und wird zurueckgerollt. Vor dem koordinierten Backend-/Schema-
Rollout muessen Backup und Wiederherstellbarkeit, Quell-/Zielzahlen,
Kollisions-/Fremdreferenzberichte, Hashstichproben und ein Rueckrollplan belegt
sein. Alte Aktivitaetsschreiber werden fuer die Migration eingefroren.

Herkunftssnapshots koennen personenbezogene Quellinhalte enthalten und sind
entsprechend zugriffsgeschuetzt zu behandeln. Physische Altloeschung bleibt ein
spaeterer Schritt nach Verbraucherinventar, Schreibstopp, Datenabgleich und
fachlicher Abnahme.

## Noch einzutragende finale Nachweise

- Schema-/Migrationsrehearsal, Backup und Wiederherstellbarkeit fuer den spaeteren
  koordinierten Live-Einsatz; der derzeitige Rollback hat keine Live-DDL
  hinterlassen
- Realer Bediennachweis mit benoetigter SSO-/Rollenabdeckung, falls gefordert
- Entscheidung zur dormant Activity-Abfrage in `daily_report_service.py` und
  verbleibenden Gaps
- Verbraucher-/Schreibstopp-Nachweis und Rolloutfreigabe

## Build-Abschluss

Regulaere vollstaendige Typpruefung (`tsc --noEmit`) und Vite-Produktionsbuild erfolgreich; 4644 Module, 1m46s. Vorhandene Paketkommentar- und Chunkgroessenwarnungen sind keine Buildfehler. Kein Gesamt-CI- oder Live-SSO-Nachweis.

Zusatzpruefung: 16 zentrale Studio-Gate-/Builder-Fixturetests bestanden. Zwei veraltete Listenabbilder wurden aus den unveraenderten kanonischen Buildern neu erzeugt; keine Ladegrenzen oder Gates gelockert.

Artefaktvertrag ergaenzt: drei MCP-Schema-Gleichheitstests bestanden; Contract-/Preset-Nachlauf 71 bestanden. Zusammen mit den 17 SQL-/Migrationsfaellen und 16 zentralen Strukturtests sind 104 verschiedene Backendfaelle nachgewiesen (keine Addition wiederholter Laeufe). Frontend unveraendert65.

## Synchronisierter Lieferstand

Acht Generatorchecks bestehen: OpenAPI (3256 Pfade), Aktionsrechteprojektion (151), CLI (255 Aktionen), Screen-Registry (31), MCP-Referenz (69 Tools), drei Codeinventare, Agentenhandbuch und Studio-Katalog (842 native Definitionen). Strukturinventar: A/B/C851, E805 von851;46 Runtimepunkte bleiben offen. Dies ersetzt keine fachliche Gesamt-/Browser-/RLS-Abnahme.

CI-Ausgangszustand nachgeprueft: SQL-Vertraege17/17 und zusaetzliche installierter-Head-Gegenprobe1/1 bestanden. Die Migrationstesthilfe rekonstruiert nur innerhalb ihrer aeusseren Rollbacktransaktion die betroffene Vorgaengertabelle; sie stempelt keine Revision und setzt keine Datenbank zurueck. Der Anwendungstest verwendet ein bereits migriertes Schema direkt. Damit sind105verschiedeneBackendfaelle und65Frontendfaelle nachgewiesen. Auch ADR-Navigation, Maskenaktionskatalog, MCP-Maskenkarte und Aktionsmatrix sind synchronisiert; MCP-Registryvalidierung ohne Fehler.

## CI-Nachlauf nach f84db0298

Der erste GitHub-Nachlauf meldete im unabhaengigen Improvement-Gate eine veraltete Business-Time-Ratsche: Der direkte Kalenderzugriff in crm_360 ist entfernt, daher wurde der Bestand exakt um einen Befund auf190 abgesenkt. Die lokale Gegenpruefung besteht; keine neue Ausnahme und keine Schwellenerhoehung.

Die Testgrenze akzeptiert in CI ausschliesslich die deklarierte Jobdatenbank bei exakt passender URL. Lokal bleiben Entwicklungsdatenbanken gesperrt. Vier Positiv-/Negativfaelle pruefen diese Grenze ohne Verbindung. Der FK-Test legt eine fehlende Standardrolle nur NOLOGIN im eigenen zurueckgerollten Savepoint an; keine Rolle oder Rechte bleiben erhalten. Insgesamt109verschiedeneBackendfaelle und65Frontendfaelle nachgewiesen.

Der physische Aktivitaetseintrag im Tabellenkatalog wurde nach realer Upgrade-Transaktion geerntet und anschliessend vollstaendig zurueckgerollt. Andere physische Tabellen bleiben identisch zur veroeffentlichten Git-Basis. Verbraucher-Lineage wurde aus deren vollstaendigem App-Quellbaum nachgezogen; keine fremden physischen Schemastaende aus der partiellen Reparaturquelle uebernommen. Gesamt-CI ist nach dem Nachlauf erneut abzuwarten.

**Abschluss Kundenreferenz im Erasureweg:** Operative Aktivitaeten werden zuerst ueber die feste Kunden-ID zugeordnet; nur ungebundene Altzeilen verwenden den Namen. Ein geaenderter Kundenname verhindert die Loeschung daher nicht; ein anderer gleichnamiger Kunde, Fremdmandant und NULL-Mandant bleiben erhalten. Erweiterter realer SQL-Test bestanden; kein zusaetzlicher Test in der Gesamtzahl109, sondern staerkerer bestehender Fall. Am GitHub-Stand5055a42e7 sind Improvement-Integrity, Secret-Scan, FSX, Docs-Code-Sync und Prozesssimulation gruen; Backend-/Frontend-Gesamtlauf noch nicht fertig.
