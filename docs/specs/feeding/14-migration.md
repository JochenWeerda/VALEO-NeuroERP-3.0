---
title: "Fuetterungsberatung — Migrations- und Refactoringkonzept"
type: specification
audience: [architektur, entwickler, devops, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Additive Ist-zu-Soll-Migration fuer Daten, APIs, Berechnung, UI und Integrationen mit Rollback- und Testvertrag.
---

# 14 — Migration

## 1. Ziel und Grundsatz

Die bestehende Rationsoptimierung wird schrittweise in den integrierten
Beratungsprozess ueberfuehrt. Es gibt keinen Big-Bang und keine parallele zweite
Fachanwendung. Jede Migration ist additiv, tenant-sicher, beobachtbar,
restart-faehig und durch Red-Green-Refactor nachgewiesen.

## 2. Ist-zu-Soll-Landkarte

| Ist | Ziel | Strategie | Slice |
|---|---|---|---|
| tenantweite flache Gruppen | Betrieb → Standort → Herde → Gruppe | nullable FKs, Default-Backfill, spaeter Pflichtgrad | FEED-CORE-015/016 |
| Solver-Dataclasses | persistente Futter-/Analyse-/Regelaggregate plus Adapter | Golden-Aequivalenz vor Umschaltung | 017–020 |
| Lifecycle-Ration | vollstaendige versionierte Rationsentscheidung | Felder/Events additiv, Snapshot beim Freigeben | 020–025 |
| Protokoll-/Mobilansicht | unveraenderliche FeedingPlanVersion | Dual Read, dann Plan als Quelle | 026/027 |
| Tagesbeobachtung | komponentenbezogene Ausfuehrung und Wirkung | neue Execution-Zeilen, historische Verdichtung | 029/030 |
| einzelne Beratungsnotizen | ConsultingCase/Measure | kontrollierter Import mit Herkunft | 031/032 |
| providernahe Mockpfade | neutrale Ports, Journal, Quarantaene | Vertragstest; Live nur per Gate | 034–036 |
| freie Agrar-Spezialseiten | native Meridian-ScreenDefinitions | Route fuer Route, keine zweite Runtime | laufend |

## 3. Datenmigrationsmuster

1. Expand: Tabellen/Spalten/Indizes nullable oder mit sicherem Default anlegen.
2. Dual Write nur wenn unvermeidbar und zeitlich begrenzt; Outbox/Idempotenz nutzen.
3. Backfill tenantweise in kleinen, wiederholbaren Batches mit Checkpoint.
4. Validate: Counts, Nullraten, FKs, Summen, Stichprobe und Fachinvarianten.
5. Read Switch hinter Feature-Flag und messbarer Vergleichsprojektion.
6. Contract: Pflichtgrad/Constraint erst nach 100-%-Nachweis verschaerfen.
7. Cleanup erst in eigenem Slice nach mindestens einer stabilen Releaseperiode.

Backfills schreiben `migration_run_id`, Tenant, Cursor, Zaehler, Fehler und
Pruefsumme in ein Betriebsjournal. Ein erneuter Lauf darf keine Duplikate oder
abweichende fachliche Wirkung erzeugen.

## 4. Tenant- und Identitaetsregeln

- Fremde IDs werden vor Upsert erkannt; `ON CONFLICT(id)` allein ist kein
  Tenant-Schutz.
- Beziehungen werden durch Repository/Service und soweit moeglich Constraints
  auf denselben Tenant und fachlichen Parent begrenzt.
- CRM-Partner bleiben Master; FeedingBusiness ist eine fachliche Projektion.
- Externe IDs werden nur zusammen mit Provider/Connection und Tenant eindeutig.
- UUID-/opake IDs werden nie aus Anzeigenamen oder fremden Nummern abgeleitet.

## 5. API-Migration

Neue Vertraege sind typisiert und additiv. Alte Pfade erhalten befristete
Adapter, die auf denselben Application Service zeigen. Deprecation umfasst
Header, Telemetrie, dokumentiertes Enddatum und Konsumenteninventar. Breaking
Changes erfordern neue Version oder explizite Kompatibilitaetsschicht.

## 6. Berechnungs- und Regelmigration

Vor jeder Persistenz-/Adapterumstellung werden bestehende Golden-Vektoren gegen
Alt- und Neupfad ausgefuehrt. Unterschiede werden als fachlich gewollt,
Rundungseffekt, Datenmapping oder Defekt klassifiziert. Eine neue Regelversion
veraendert niemals rueckwirkend gespeicherte Freigaben.

## 7. UI-Migration

Die zentrale Kette bleibt:

```text
ScreenDefinition → RenderPlan → schema compiler → useUniversalMaskRuntime
→ UniversalMaskRenderer
```

Ein bestehender Spezialscreen wird zuerst fachlich auditiert. Nur benoetigte
Domain-Interaktion bleibt als kleines Overlay; Tabellen, Aktionen, Layout,
Permissions und Data Binding werden zentral deklariert. Route und Deep Links
bleiben waehrend der Umschaltung stabil.

## 8. Technische Schulden und Prioritaet

| Prioritaet | Schuld | Exit-Kriterium |
|---|---|---|
| P0 | fehlende Tenant-/Business-Grenze | Isolationstest und serverseitige Policy gruen |
| P0 | veraenderbare freigegebene Fachstaende | unveraenderlicher Snapshot + Audit |
| P1 | untypisierte API/Einheiten | Pydantic/OpenAPI + Property-Tests |
| P1 | High-Risk-ScreenAction ohne commandEndpoint | Inventory gruen, ActionRuntime-Audit |
| P1 | Mock als scheinbare Liveintegration | Deployment-Gate und klare Kennzeichnung |
| P2 | doppelte UI-Logik | native ScreenDefinition und entfernte Altkomponente |
| P2 | fehlende Langzeitprojektion | rebuildbare Read Models und Metriken |

## 9. TDD- und Abnahmevertrag

Jeder Migrationsslice beginnt mit einem fehlschlagenden Schema-, Isolation-,
Backfill-, Aequivalenz- oder Route-Contract-Test. Pflichtgates: Upgrade von
aktuellem Head, Single-Head, idempotenter Backfill, Downgrade/Forward-Fix-Plan,
Tenant-Stichprobe, API-Regression, Datenvergleich, Observability und Doku-Drift.

## 10. Rollback

Bevorzugt wird Forward Fix. Feature-Flag kann Reads/Actions auf den stabilen Pfad
zurueckschalten. Additive Spalten bleiben bestehen; destruktiver Downgrade ist
nicht das primaere Produktionsrollback. Bereits extern wirksame Aktionen werden
kompensiert, nicht durch Datenloeschung verborgen.

## 11. Aktueller Stand

FEED-CORE-015 hat das Muster erstmals umgesetzt: additive Migration,
tenant-sichere Hierarchie, idempotenter Default-Backfill, append-only Grants,
typisierte API und native Meridian-Worklist. Lieferstatus je Requirement steht
in Kapitel 16; naechste Migrationen folgen den Paketen in Kapitel 17.
