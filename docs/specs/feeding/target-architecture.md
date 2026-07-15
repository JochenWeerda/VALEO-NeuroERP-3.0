---
title: "Fütterungsberatung — Zielarchitektur (Phase 3)"
type: explanation
audience: [entwickler, architektur, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Zielarchitektur für das integrierte Fütterungsberatungs-System — Aggregate, API-Zielbild, Events, Rechte, Migration, Frontend-Landkarte, Teststrategie.
---

# Zielarchitektur Fütterungsberatung (Phase 3)

Leitplanke aus dem Lastenheft: **keine Big-Bang-Neuentwicklung**. Der vorhandene
Fachkern (Solver, Normsysteme, Lifecycle, Readiness, Controlling, Connectors) wird
weiterverwendet; neue Aggregate docken an, statt zu ersetzen.

## 1. Kontext

```text
CRM (business_partner) ─┐
Einkauf/Lager/Kontrakte ─┤        ┌──────────────────────────────┐
Labor (Adapter) ─────────┼──────▶ │  Feeding-Domäne (domain_agrar)│ ◀── Portal (Landwirt)
Herdenmanagement (DDW) ──┤        │  FastAPI-Router-Familie       │ ◀── ERP-UI (Berater)
Mischtechnik (agrirouter)┘        │  Services + Read Models       │ ◀── Mobil (Fütterer)
                                  └──────────────┬───────────────┘
                                                 ▼
                                   NATS-Outbox (Feeding-Events)
```

## 2. Bounded Context und Aggregate

Ein Bounded Context **Feeding** im Schema `domain_agrar`. Zwei Nachbar-Kontexte bleiben
getrennt: **Feed-Chain** (Handel/Produktion/Qualität, `feed_chain_*`-Migrationen) und
**Ackerbau** (Feldbuch). Verbindung nur über IDs/Events, nie über geteilte Tabellen.

### Aggregat-Zuordnung (Lastenheft Kap. 8 → IST/SOLL)

| Aggregat | IST-Anker | Entscheidung |
|---|---|---|
| FeedingBusiness / FarmSite / Herd | — (feeding_groups flach) | **neu** in Inkrement 1; `business_partner_id`-UUID als CRM-Brücke (bestehender Identitätsstandard); feeding_groups erhält `herd_id`-FK (nullable, Migration additiv) |
| AnimalGroup / AnimalGroupSnapshot | `feeding_groups` + Herd-Data-Deltas | erweitern statt neu; Snapshots verdichten Herd-Data-Beobachtungen (Paritätsmatrix Gruppenhistorie) |
| Feed / FeedProduct / FeedReferenceValue | `solver/feed.py`, DLG-Loader, Futtermittel-Masken | Persistenz-Aggregat neu, Solver-Dataclass wird daraus befüllt (Adapter, kein Solver-Umbau) |
| NutrientDefinition / UnitDefinition | Code-Konstanten | **neu als Daten** (Inkrement 1) — Schlüssel zur flexiblen Nährstoffmatrix (6.3) und Einheitenregeln (7.1) |
| FeedAnalysis / FeedAnalysisValue | verifizierte Analysen in Readiness | **neu**: Aggregat mit Originaldatei (DMS-Ref), Labor/Methode, Versionswahl „aktiv", Historie |
| EvaluationSystem(Version) / RequirementProfile | gfe2023/dlg2025-Konstanten | Registrierung als Daten (Name+Version+Modulreferenz); Berechnung bleibt Code — Golden-Tests sichern Äquivalenz |
| Ration / RationVersion / RationItem / RationConstraint | `rations`, `ration_versions` (Snapshot JSONB) | Bestand behalten; RationItem/Constraint als **projizierte Sicht** aus dem Snapshot, erst bei Editor-Bedarf materialisieren |
| OptimizationRun / OptimizationResult | Snapshot + checksum | **neu klein**: Run-Tabelle (solver_version, Parameter, Status, Dauer, result_ref) für Reproduzierbarkeit (6.7) |
| RationEvaluation / Warning | Erklärschicht (aggregator) | strukturierte Persistenz je Version (Inkrement 2) |
| FeedingPlan(Version) / MixingInstruction | aktive Version + Mobil-Protokoll + solver/mixing | **neu** in Inkrement 3; Plan = unveränderliche Ableitung einer aktiven RationVersion × Tierzahl × Gültigkeit |
| ActualFeeding | `feeding_controlling_daily`, `feeding_logs` | Bestand (idempotent) — Plan-Bezug ergänzen |
| PerformanceRecord | Tagesreihe (ECM/N-Eff/Methan) | Bestand; MLP/Milchgüte-Kennzahlen additiv |
| Observation / ConsultingCase / Recommendation / Measure | — | **neu** in Inkrement 5 |
| Approval / AuditEvent | Lifecycle-Audit | verallgemeinern (ein Audit-Muster je Aggregat, fachlich lesbar) |
| Report | PDF-Pfad | Report-Aggregat mit revisionssicherer Dokumentreferenz (DMS) |
| ImportJob / IntegrationMapping | rations_integration_imports, herd_data_connections | Bestand + Vorschau/Quarantäne-Status |

## 3. API-Zielbild

Die Lastenheft-Endpunktgruppen (`/feeding/…`) werden als **neuer Präfix
`/api/v1/feeding/*`** eingeführt, der die bestehenden `/agrar/rations-optimization/*`-
Router **einbindet statt dupliziert**:

- Neue Aggregate (businesses, herds, animal-groups, feeds, feed-analyses,
  evaluation-systems, requirements, feeding-plans, consulting-cases, reports)
  entstehen direkt unter `/feeding/`.
- Bestehende Verträge (lifecycle, readiness, controlling, integrations) bleiben unter
  ihrem Präfix stabil (Bestandsclients!) und werden unter `/feeding/` als dünne
  Alias-Router re-exponiert; OpenAPI markiert den Alt-Präfix als deprecated erst
  nach Frontend-Migration.
- Grundsätze je Router: Pydantic-Schemas, response_model 100 % (Repo-Gate),
  `require_roles` aus `app/agrar/rations/authz.py`, Pagination/Filter, fachliche
  Fehlercodes, Idempotency-Key für Importe/Planveröffentlichung, Optimistic Locking
  über `expected_*`-Felder (Muster aus Lifecycle bereits etabliert).
- Langläufer (Optimierung, Import, Bericht) als Job-Endpoints mit Statuspolling
  (Muster: bestehende Worker/Outbox), nie synchron > 10 s.

## 4. Eventmodell (NATS-Outbox)

`feeding.analysis.verified` · `feeding.ration.version.approved` ·
`feeding.ration.version.activated` · `feeding.plan.published` ·
`feeding.actuals.recorded` · `feeding.deviation.exceeded` ·
`feeding.measure.created/completed` · `feeding.import.quarantined`.
Konsumenten: Aufgaben/Benachrichtigung, Einkauf (Reichweitenwarnung), Berichte.

## 5. Rechtekonzept

Zwei Ebenen: (1) Domänenrollen (bestehend, `authz.py`: READ/WRITE/APPROVE/
CONNECTOR_ADMIN — serverseitig erzwungen, Slice 013); (2) **Ressourcen-Scope** neu:
`feeding_business_grants(tenant_id, business_id, subject, scope, valid_until)` —
prüfbar als Dependency `require_business_access(business_id, scope)`. Externe Berater
= zeitlich begrenzte Grants (4.2). Portal-Nutzer sehen nur Betriebe mit Grant.

## 6. Datenmigration

Alle Migrationen **additiv** (nullable FKs, neue Tabellen), Alembic Single-Head je
Slice (Repo-Regel). Bestandsdaten: feeding_groups erhalten per Backfill-Skript einen
Default-Betrieb je Tenant („Eigener Betrieb"), damit die Betriebsakte sofort trägt.
Kein Umbau bestehender Controlling-/Lifecycle-Tabellen; neue Bezüge nur als Spalten
mit Default NULL. Rollback = Revert der additiven Migration.

## 7. Frontend-Seitenlandkarte (Kap. 10 → Muster)

| Kernseite | Muster | IST-Anker |
|---|---|---|
| Fütterungsübersicht | native SD-Cockpit (OverviewPage) | `agrar/feed-advice` erweitern |
| Betriebsliste | ListReport (mask-builder) | neu |
| Betriebsakte | ObjectPage mit Register-Tabs (Design-Audit R1) | neu — bündelt bestehende Worklists als Tabs |
| Tiergruppen/Futtermittel/Analyse | ObjectPage + Wizard (Analyse-Import) | `grundfutteranalysen.tsx` ablösen |
| Rationseditor | **neue Seite** (Schichtenregel: freie Prozessmaske → patterns/*) mit Solver-Anbindung; Workbench-Monolith bleibt Experten-Fallback bis Editor-Parität | ADR-041 |
| Variantenvergleich | eigene Seite, Chart-Palette (Soll rezessiv) | Intent-Delta-Logik wiederverwenden |
| Fütterungsplan | ObjectPage + Druck-/PDF-Zweig + Mobilroute | Mobil-Protokoll |
| Soll-Ist/Leistung | bestehende Controlling-Tabs ausbauen | FeedControlling* |
| Beratungsfall | Worklist + ObjectPage | neu |
| Integrationsmonitor | Worklist über ImportJobs/Quarantäne | `rations-schnittstellen-import.tsx` ausbauen |

## 8. Teststrategie

Je Inkrement (Lastenheft Phase 5): pytest-Domänentests ohne DB (Muster
`test_rations_authz.py`), Service-Tests mit DB, Golden-Tests für jede neue Kennzahl
(bestehende DLG-Suite als Vorbild), Property-Tests für Einheitenumrechnung
(FM/TM-Roundtrip), Vitest je neuer Seite (Lade/Leer/Fehler/Erfolg), axe auf neuen
Kernrouten, Playwright-Journey je Release-Meilenstein (Vorbild
`vollnutzung-rations-acker.spec.ts`), RBAC-403-Regression automatisch je neuem Router.
