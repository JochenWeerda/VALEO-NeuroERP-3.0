---
title: Kanonischer CRM-Aktivitaetsspeicher und gemeinsamer Command-Vertrag
type: adr
audience: [architektur, entwickler, qa, betrieb]
owner: domain/crm
status: accepted
last_reviewed: 2026-10-29
version: 1.2.0
description: Fuehrt CRM-Aktivitaeten auf domain_crm.activities mit einem tenantgebundenen Service- und Command-Vertrag zusammen.
---

# Kanonischer CRM-Aktivitaetsspeicher und gemeinsamer Command-Vertrag

**Status:** Accepted. **Datum:** 2026-10-29.

## Kontext

CRM-Aktivitaeten wurden ueber mehrere Tabellen und Endpunkte abgebildet. Dadurch
konnten Listen, Detailansichten und Schreibwege unterschiedliche Felder,
Mandantenfilter und Identitaetsannahmen verwenden. Die bereits bestehende
Migration `mandant_finanz_crm_20261007` fuehrt `domain_crm.activities` als
kanonischen Speicher ein. Die Reparaturquelle `artifacts/migration-repair-source`
ist ein partieller Spiegel: Ein dort fehlender Eintrag gilt nicht als geloescht
oder als Beleg dafuer, dass er im akzeptierten Quellstand nicht existiert.

## Entscheidung

`domain_crm.activities` ist der einzige kanonische CRM-Aktivitaetsspeicher. Die
Reparaturmigration `crm_activity_canonical_20261029.py` vereinheitlicht Status-
und Typwerte strikt, laesst ein nicht gesetztes Faelligkeitsdatum als `NULL` zu
und erhaelt Version, Autor, drei JSONB-Stringlisten sowie Herkunft und einen
unveraenderten Rohquellensnapshot mit Hash.

Uebernahmen aus `public.crm_activities`, `public.crm_core_activities` und
`domain_crm.crm_activities` sind nur zulaessig, wenn Mandant registriert ist,
keine ID kollidiert und weder abgeschnitten noch eine Fremdreferenz verletzt
wird. Alte Tabellen bleiben bis zur koordinierten Ausserbetriebnahme ihrer
Verbraucher unveraendert erhalten; die Migration ist keine Berechtigung, sie
vorzeitig zu leeren oder zu entfernen. Die ungenutzte lokale Activity-ORM-
Familie und ihre DTOs wurden aus `app/crm/models.py` und `app/crm/schemas.py`
entfernt. Die Seed-Pfade legen keine Aktivitaeten mehr direkt an; Kontakte,
Leads und Farmprofile bleiben davon unberuehrt. Diese Bereinigung loescht keine
vorhandenen Datenbanktabellen.

`crm_activity_service.py` fuehrt Erstellen, Aendern und Loeschen als Commands in
einer Transaktion aus. Jeder Command prueft die CRM-/SALES-Rolle oder Adminrolle,
den verifizierten Mandanten und die verifizierte Subjektidentitaet. Identitaet
kommt aus dem authentifizierten Kontext, nicht aus dem Payload. Aendern und
Loeschen verlangen `expected_version` und sperren die Zielzeile. Idempotenz
verwendet das bestehende dauerhafte Register `public.mcp_tool_executions` und
bindet Schluessel an Actor und Payload-Hash. Vorher-/Nachher-Beleg,
`performed_by`, Korrelation und Outbox-Eintrag werden gemeinsam mit der
Fachaenderung gespeichert.

REST, MCP, CLI und Studio verwenden dieselben Command-Vertraege. MCP-Schemas
werden aus den kanonischen Eingabefeldern abgeleitet; Identitaetsfelder sind
nicht Teil der Eingabe. Agenten-Schreibzugriff bleibt bis zu einer ausdruecklichen
Freigabe der konkreten Capability deaktiviert. Studio-Aktivitaetsliste,
-Details und -Erstellung verwenden denselben Speicher und verlangen Version und
Idempotenzschluessel. Kontakt- oder Farm-Masken, die zuvor irrtuemlich als
Aktivitaetsformular dienten, schlagen geschlossen fehl und melden keinen
Aktivitaetserfolg. Kalenderabfragen verwenden kanonische Aliasfelder;
Opportunity-Aktivitaeten verwenden den gemeinsamen Resolver und Command.

Der DSGVO-Erasure-Workflow ist ein gesonderter, rechtlich begruendeter
Loeschpfad und keine gewoehnliche CRUD-Mutation. Er bleibt als kontrollierter
Workflow separat autorisiert. Sein Activity-Loeschschritt muss ausschliesslich
auf den verifizierten Mandanten begrenzt sein; mandantenlose Zeilen werden nicht
mitgeloescht. Diese Ausnahme erweitert nicht den allgemeinen Command-Vertrag.
Die dormant gebliebene Activity-Abfrage in
`app/domains/crm/services/daily_report_service.py` bleibt ein offener
Folgepunkt. Sie ist kein bestaetigter Verbraucher des kanonischen Speichers.

## Mandantengrenze und RLS

Jeder gewoehnliche Listen-, Detail- und Schreibzugriff begrenzt Daten auf den
verifizierten Mandanten. Der separat autorisierte DSGVO-Erasure-Workflow muss
dieselbe Mandantengrenze einhalten. Die Tabelle `domain_crm.activities` bleibt
als ausdrueckliche Service-Ausnahme im Register
`docs/admin/rls-exceptions.json`; Row-Level Security ist weiterhin nicht als
aktiv nachgewiesen. Die Datenbankverbindung und der Service muessen die
Mandantengrenze gemeinsam durchsetzen. Eine spaetere RLS-Umstellung erfordert
einen eigenen geprueften Slice.

## Migration und Rollout

Der Rollout folgt Expand, Migrate, Contract. Vor der Migration werden alte
Aktivitaetsschreiber eingefroren. Migration und Backend-/Schemawechsel werden
koordiniert ausgerollt. Vorab sind Backup, Migrationsrehearsal und Rueckrollplan
auf dem bestehenden gemeinsamen `valeo_probe` zu pruefen; die Rehearsal-
Transaktion wird zurueckgerollt. Es werden weder neue Testdatenbanken noch
Container angelegt und keine gemeinsame Datenbank pauschal zurueckgesetzt.
Herkunftssnapshots koennen personenbezogene Inhalte enthalten und unterliegen
denselben Zugriffsschutz- und Aufbewahrungsregeln wie die Quelldaten.

Alte Tabellen werden erst physisch entfernt, wenn Verbraucherinventar,
Schreibstopp, Datenabgleich, Rueckrollfenster und fachliche Abnahme belegt sind.

## Folgen und offene Grenzen

- Es gibt einen Speicher und einen Schreibvertrag fuer CRM-Aktivitaeten.
- Ein nicht geplantes Faelligkeitsdatum bleibt ausdruecklich leer; es wird kein
  Ersatzdatum erfunden.
- Ein fehlgeschlagener oder mehrdeutiger Import darf keine Quelle als migriert
  markieren und keine Zeilen stillschweigend verlieren.
- Die bekannte Entwicklungsdatenbank-Inventur ist eine Bestandsaufnahme, kein
  Nachweis, dass keine weiteren Daten oder Verbraucher existieren.
- Gezielte Backend-Suites (Activity Contracts, Migration SQL, Canonical SQL,
  Studio List Presets) bestanden mit 85 Faellen; eine Starlette-Deprecation-
  Warnung, Laufzeit 78,57 Sekunden. Das Frontend meldete 65 Tests in 9 Dateien
  und `tsc --noEmit` gruen. Der Produktionsbuild ist erfolgreich abgeschlossen.
- 24 synthetische Evidenzbilder (18 Haupt- und 6 Zusatzansichten) liegen unter
  `docs/quality-assurance/evidence/crm-activity-canonical-20261029/`. Sie sind
  kein Live-SSO-Nachweis. Opportunity- und Kundenmasken verwenden Human-only-
  und Idempotenz-Flags; Opportunity REST/MCP/CLI wurde auf einen Effekt geprueft.
- Der Pruefstand blieb vor und nach Rollback auf `rls_domain_shared_20261027`;
  null fremde Sessions. Die Herkunftsspalte ist nach Rollback nicht vorhanden.
  Es wurde damit keine Live-DDL bestaetigt. Die gezielten Pruefungen belegen
  weder Gesamt-CI noch eine Produktionsabnahme.
- Der Rollout ist erst abgeschlossen, wenn finale Tests, Schema-/Migrations-
  abnahme und reale Bedienpfade belegt sind. Eine Gesamt- oder Produktions-
  abnahme wird durch diese ADR nicht behauptet.

## Quellen

- Bestehende Migration: `mandant_finanz_crm_20261007`
- Reparaturquelle: `artifacts/migration-repair-source` (partieller Spiegel)
- [FastAPI: groessere Anwendungen und Router](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [PostgreSQL: Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

## Build-Abschluss

Regulaere vollstaendige Typpruefung (`tsc --noEmit`) und Vite-Produktionsbuild erfolgreich; 4644 Module, 1m46s. Vorhandene Paketkommentar- und Chunkgroessenwarnungen sind keine Buildfehler. Kein Gesamt-CI- oder Live-SSO-Nachweis.

Zusatzpruefung: 16 zentrale Studio-Gate-/Builder-Fixturetests bestanden. Zwei veraltete Listenabbilder wurden aus den unveraenderten kanonischen Buildern neu erzeugt; keine Ladegrenzen oder Gates gelockert.

Artefaktvertrag ergaenzt: drei MCP-Schema-Gleichheitstests bestanden; Contract-/Preset-Nachlauf 71 bestanden. Zusammen mit den 17 SQL-/Migrationsfaellen und 16 zentralen Strukturtests sind 104 verschiedene Backendfaelle nachgewiesen (keine Addition wiederholter Laeufe). Frontend unveraendert65.

## Konsequenzen

Es gibt einen operationalen Aktivitaetsvertrag und einen gemeinsamen Schreibservice statt konkurrierender Transportmodelle. Die additive Migration muss zusammen mit dem Backend bereitgestellt werden; erst danach darf die laufende Oberflaeche den erweiterten Vertrag verwenden. Alte Quelltabellen bleiben fuer den nachgewiesenen Datenabgleich vorerst intakt. RLS und die restlichen Masken behalten ihre separat dokumentierten Abnahmegrenzen.

CI-Ausgangszustand nachgeprueft: SQL-Vertraege17/17 und zusaetzliche installierter-Head-Gegenprobe1/1 bestanden. Die Migrationstesthilfe rekonstruiert nur innerhalb ihrer aeusseren Rollbacktransaktion die betroffene Vorgaengertabelle; sie stempelt keine Revision und setzt keine Datenbank zurueck. Der Anwendungstest verwendet ein bereits migriertes Schema direkt. Damit sind105verschiedeneBackendfaelle und65Frontendfaelle nachgewiesen. Auch ADR-Navigation, Maskenaktionskatalog, MCP-Maskenkarte und Aktionsmatrix sind synchronisiert; MCP-Registryvalidierung ohne Fehler.
