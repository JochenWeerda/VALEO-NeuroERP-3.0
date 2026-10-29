---
title: CRM Activity Canonicalization — Handoff
type: handoff
audience: [agent, entwickler, qa, betrieb]
owner: Codex
status: in-arbeit
last_reviewed: 2026-10-29
version: 1.1.0
description: Uebergabe des kanonischen CRM-Aktivitaetsslices mit vorlaeufiger Evidenz und offenen Abnahmegates.
---

# CRM Activity Canonicalization — Handoff

## Stand

`domain_crm.activities` ist der kanonische CRM-Aktivitaetsspeicher. REST, MCP,
CLI und Studio verwenden den tenant- und subjectgebundenen
`crm_activity_service`-Command-Vertrag. Update/Delete verlangen Version und
Idempotenz; Auditbeleg und Outbox werden mit der Fachaenderung atomar behandelt.
Agentenschreiben bleiben ohne ausdrueckliche Capability-Freigabe gesperrt.

Gezielte Backend-Suites (Activity Contracts, Migration SQL, Canonical SQL,
Studio List Presets): **85 bestanden**, eine Starlette-Deprecation-Warnung,
78,57 Sekunden. Frontend: **65 Tests in 9 Dateien bestanden** und regulaeres
`tsc --noEmit` gruen. Der Produktionsbuild ist erfolgreich abgeschlossen. 24 synthetische
Evidenzbilder (18 Haupt-, 6 Zusatzansichten) mit Ergebnis-/Scrollnachweisen
liegen unter `docs/quality-assurance/evidence/crm-activity-canonical-20261029/`.
Keine Gesamt-CI-, Live-SSO- oder Produktionsabnahme wird behauptet.

Opportunity- und Kundenmasken haben effektive Human-only-/Idempotenz-Flags;
Opportunity REST/MCP/CLI wurde auf einen Effekt geprueft. DSGVO-Erasure nutzt
den verifizierten Tenantfilter und bleibt ein gesonderter rechtlicher
Erasureweg. Pruefstand: unveraendert `rls_domain_shared_20261027`, null fremde
Sessions; Herkunftsspalte nach Rollback nicht vorhanden. Das ist kein
Live-DDL-Nachweis.

Die ungenutzte lokale Activity-ORM-/DTO-Familie und beide direkten Activity-
Seedpfade sind entfernt; Kontakte, Leads und Farmprofile bleiben in ihren
Seedpfaden erhalten. Vorhandene alte Tabellen werden dadurch nicht geloescht.

## Sicherheits- und Betriebshinweise

- `domain_crm.activities` bleibt eine dokumentierte Ausnahme in
  `docs/admin/rls-exceptions.json`; RLS ist nicht aktiv nachgewiesen.
- Der DSGVO-Erasure-Workflow ist ein gesonderter rechtlicher Loeschpfad, keine
  gewoehnliche CRUD-Mutation. Der Activity-Schritt bleibt separat autorisiert;
  sein Match fuer mandantenlose Zeilen wird entfernt, sodass er auf den
  verifizierten Mandanten begrenzt bleibt.
- Kontakt-/Farm-Fehlverdrahtungen schlagen geschlossen fehl und duerfen keinen
  Aktivitaetserfolg darstellen.
- Die Activity-Abfrage in `app/domains/crm/services/daily_report_service.py` ist
  dormant, offen und kein belegter kanonischer Verbraucher.
- Alte Quelltabellen bleiben unveraendert, bis Verbraucher stillgelegt,
  Daten abgeglichen und Rueckrollfenster freigegeben sind. Rehearsal nur auf dem
  bestehenden gemeinsamen `valeo_probe`, transaktional mit Rollback; keine
  neue Datenbank, kein Reset.

## Naechste Abnahmeschritte

2. Schema-/Migrationsrehearsal, Backup und Wiederherstellbarkeit fuer einen
   spaeteren koordinierten Live-Einsatz belegen.
3. Dormante Activity-Abfrage in `daily_report_service.py` aufloesen.
4. Reale Bedien-/SSO-Abnahme und Rolloutfreigabe separat belegen.

## Referenzen

- [ADR: Kanonischer CRM-Aktivitaetsspeicher](../../adr/adr-crm-activity-canonical-20261029.md)
- [QA und Betriebsabnahme](../../quality-assurance/crm-activity-canonical-20261029.md)

## Build-Abschluss

Regulaere vollstaendige Typpruefung (`tsc --noEmit`) und Vite-Produktionsbuild erfolgreich; 4644 Module, 1m46s. Vorhandene Paketkommentar- und Chunkgroessenwarnungen sind keine Buildfehler. Kein Gesamt-CI- oder Live-SSO-Nachweis.

Zusatzpruefung: 16 zentrale Studio-Gate-/Builder-Fixturetests bestanden. Zwei veraltete Listenabbilder wurden aus den unveraenderten kanonischen Buildern neu erzeugt; keine Ladegrenzen oder Gates gelockert.

Artefaktvertrag ergaenzt: drei MCP-Schema-Gleichheitstests bestanden; Contract-/Preset-Nachlauf 71 bestanden. Zusammen mit den 17 SQL-/Migrationsfaellen und 16 zentralen Strukturtests sind 104 verschiedene Backendfaelle nachgewiesen (keine Addition wiederholter Laeufe). Frontend unveraendert65.

## Synchronisierter Lieferstand

Acht Generatorchecks bestehen: OpenAPI (3256 Pfade), Aktionsrechteprojektion (151), CLI (255 Aktionen), Screen-Registry (31), MCP-Referenz (69 Tools), drei Codeinventare, Agentenhandbuch und Studio-Katalog (842 native Definitionen). Strukturinventar: A/B/C851, E805 von851;46 Runtimepunkte bleiben offen. Dies ersetzt keine fachliche Gesamt-/Browser-/RLS-Abnahme.

CI-Ausgangszustand nachgeprueft: SQL-Vertraege17/17 und zusaetzliche installierter-Head-Gegenprobe1/1 bestanden. Die Migrationstesthilfe rekonstruiert nur innerhalb ihrer aeusseren Rollbacktransaktion die betroffene Vorgaengertabelle; sie stempelt keine Revision und setzt keine Datenbank zurueck. Der Anwendungstest verwendet ein bereits migriertes Schema direkt. Damit sind105verschiedeneBackendfaelle und65Frontendfaelle nachgewiesen. Auch ADR-Navigation, Maskenaktionskatalog, MCP-Maskenkarte und Aktionsmatrix sind synchronisiert; MCP-Registryvalidierung ohne Fehler.
