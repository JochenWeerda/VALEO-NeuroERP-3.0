---
title: "Fütterungsberatung — IST-Audit (Phase 1)"
type: explanation
audience: [entwickler, fachlich, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Datei-evidenzbasierte Bestandsaufnahme des Fütterungs-/Rationsbereichs als Grundlage der Traceability gegen das Lastenheft.
---

# IST-Audit Fütterungsberatung (Phase 1 des Lastenhefts)

Stand 2026-07-15. Jede Aussage trägt einen Dateinachweis. Grundlage: Repository-Inventur
plus die abgeschlossenen Slices FEED-ADVICE-LIFECYCLE-007 bis FEED-ADVICE-ROLES-013
(Belege: `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/`).

## 1. Backend-Landkarte

### 1.1 Fachkern `app/agrar/rations/`

| Bereich | Dateien | Inhalt |
|---|---|---|
| Solver | `solver/{lp_constraints,lp_stage2,constraint_registry,feed,mixing}.py` | LP auf `scipy.optimize.linprog`, mehrstufig (Stage 2, lexikografisch Milch), Constraint-Registry, Mischprotokoll |
| Normsysteme | `constants/{gfe2023,dlg2025,feeding_system,solver_defaults}.py` | GfE-2023-Energie, DLG-01/2025-Kennzahlen (ECM, DCAB, peNDF, Effizienz), Fütterungssystem-Konstanten |
| Protein | `fan_precision.py` | sidP_FAN1-Präzisionsmodus (mehrere Iterationsstufen, Tests `test_rations_optimization_fan_mode_*.py`) |
| Lifecycle | `lifecycle/domain.py` | Statusautomat draft→in_review→approved→scheduled→active→retired→archived, TransitionError |
| Readiness | `readiness.py` | Bestand/Reichweite/Analysealter/Preisgültigkeit, Befundcodes, OVERRIDE-Regel |
| Controlling | `controlling.py` | ECM (mit Laktose), N-Effizienz, Abweichungsrechnung — unbekannt bleibt `None`, nie 0 |
| Fütterungskontrolle | `control/feeding_control.py` | Soll/Ist-Mischkontrolle (LoadedComponent, Restfutter, Mischgenauigkeit) |
| Integrationen | `integrations/{adapters,herd_data}.py` | agrirouter-, ICAR-ADE-, Labor-Adapter; providerneutraler Herd-Data-/DDW-Vertrag |
| Referenzdaten | `repository/dlg_loader.py`, `compound_feed/{models,parser}.py` | DLG-Futterwerttabellen, Mischfutter-Deklarationsparser |
| Ergebnis | `response/aggregator.py` | Erklärschicht/Aggregation (Test `test_rations_aggregator.py`) |
| Authz | `authz.py` | READ/WRITE/APPROVE/CONNECTOR_ADMIN-Rollensets + `require_roles` (seit FEED-ADVICE-ROLES-013 in allen 4 Routern) |
| Proxy | `http/proxy.py` | optionaler externer Optimierungsdienst |

### 1.2 API-Router `app/api/v1/endpoints/`

| Router | Präfix | Endpoints (Auszug) | Rollen |
|---|---|---|---|
| `rations_optimization.py` | `/agrar/rations-optimization` | optimize, optimize/demo, Portal-Workbench-Verträge | dev/portal |
| `rations_lifecycle.py` | `…/lifecycle` | groups, rations, versions, transitions, audit | READ/WRITE/APPROVE |
| `rations_readiness.py` | `…/readiness` | evaluate, materials | READ |
| `rations_controlling.py` | `…/controlling` | POST observations (idempotent), GET series | WRITE/READ |
| `rations_integrations.py` | `…/integrations` | {adapter}/import, imports, herd-data/{connections,sync,mock-import,observations} | WRITE/READ/ADMIN |
| `rations_zugang.py` | — | DSGVO-konformer Rations-Zugang (Migration `rations_zugang_dsgvo_20260420`) | — |
| `feed_produktion_actions.py` | — | Produktions-Lifecycle-Aktionen (DOM-FEED-PROD-004) | — |

### 1.3 Services `app/services/`

`rations_lifecycle_service.py` (Audit je Transition, Ein-Aktiv-Regel),
`rations_controlling_service.py` (idempotenter Upsert je tenant/group/date/source/source_ref,
Soll aus aktivem Versions-Snapshot), `rations_readiness_service.py`,
`rations_herd_data_sync_service.py` (Consent/Contract/Secret/Egress-Gates, Delta-Sync,
Worker 03:30).

### 1.4 Persistenz (Alembic, Schema `domain_agrar`)

| Migration | Tabellen |
|---|---|
| `feed_advice_lifecycle_20260714` | feeding_groups, rations, ration_versions, ration_version_lifecycle (+Audit) |
| `feed_advice_controlling_20260714` | feeding_controlling_daily (Soll/Ist/ECM/N-Eff/Methan, Unique tenant+group+date+source+ref) |
| `feed_advice_connectors_20260714` | herd_data_connections, herd_data_observations |
| `rations_feeding_control_20260711` | feeding_logs (Mischkontrolle) |
| `rations_integrations_20260712` | rations_integration_imports (payload_hash, Dubletten) |
| `rations_zugang_dsgvo_20260420` | Zugangs-/DSGVO-Strukturen |
| Feed-Chain-Familie (`feed_chain_*`, `feed_produktion_lifecycle_*`) | Produktions-/Qualitäts-/Verbrauchskette (eigener Workstream DOM-FEED) |

## 2. Frontend-Landkarte

| Bereich | Dateien | Inhalt |
|---|---|---|
| Portal-Einstieg | `pages/portal/rationsoptimierung.tsx` | hybride Aufgabenarchitektur (ADR-041): nativer SD-Start `agrar/feed-advice`, Solver lazy |
| Experten-Workbench | `pages/futtermittel/rationsoptimierung.tsx` (~5.000 Z.) | Solver-UI, Wizard, Zeilen-CRUD/Fixierung, Intent-Vorschläge, TS/FM-Umschalter, KPI-Trio, sidLys:sidMet (RATIONS-UX-Slices 001–005) |
| Lifecycle | `features/feed-advice/RationLifecycle{Worklist,Detail}.tsx` | Versionen, Transitionen, Reviewgründe |
| Controlling | `features/feed-advice/FeedControlling{Page,Trends}.tsx` | native Worklist SD `agrar/feed-controlling`, Tageserfassung, 5 Soll-Ist-Trendcharts + Gruppen-Benchmark (kuhzahl-gewichtet) |
| Native SDs | `app/core/screen_definitions.py` | `agrar/feed-advice`, `agrar/feed-readiness`, `agrar/feed-controlling` |
| Futtermittel-Masken | `pages/futtermittel/{einzelfuttermittel,mischfuttermittel}-{liste,stamm,native}.tsx`, `grundfutteranalysen.tsx`, `rations-schnittstellen-import.tsx`, `fuetterungsdokumentation-mobil.tsx`, `rations-zugang.tsx` u. a. | Stammdaten-, Analyse-, Import-, Mobil-Seiten |
| API-Clients | `lib/api/{rations-lifecycle,feed-controlling}.ts` | typisierte Read/Write-Clients |

## 3. Testlandschaft

~60 Backend-Testdateien `tests/test_rations_*.py` (Solver-Golden-Tests je DLG-2025-Kennzahl,
FAN-Modi 001–005, Weide/Saison/SARA-Reopt, Mixing, Lifecycle-Domain+API, Readiness,
Controlling, Herd-Data-Connectors, Authz 24 Fälle) + `test_feed_advice_screen_definition.py`;
Frontend-Vitest `feed-advice-entry`, `feed-controlling-trends`; Playwright
`vollnutzung-rations-acker.spec.ts` (14 Schritte gegen Docker-Prod); Seed
`scripts/seed_simulation_rations_acker.py` + `data/seed/rations_hof_ostfriesland.json`.

## 4. Governance-Bestand

Paritätsmatrix `docs/project-context/fuetterungsberatung-feature-parity-2026-07-14.md`
(17 Arbeitsbereiche, Stand + Nächster Ausbau), UX-Architekturentscheid ADR-041
(`docs/design/feed-advice-experience-architecture-2026-07-14.md`), ADRs 042–044,
Domain Pack Agrar, Slice-YAMLs FEED-ADVICE-007…013.

## 5. Bekannte technische Schulden und Risiken

1. **Experten-Workbench ist ein ~5.000-Zeilen-Monolith** (`rationsoptimierung.tsx`) —
   per ADR-041 bewusst als begrenzter Experten-Arbeitsplatz erhalten; darf laut
   Workboard nicht weiter wachsen. Risiko für Rationseditor-Anforderungen 6.6 (Undo/
   Redo, Drag-and-drop) — Neubau als Editor-Inkrement statt Anbau.
2. **Kein eigenständiges Analyse-Aggregat**: Grundfutteranalysen existieren als Werte
   am Futtermittel (verifizierte Analysen fließen in Readiness), aber ohne
   FeedAnalysis/FeedAnalysisValue-Entität, Originaldatei-Anhang, Methoden-/Labor-Metadaten
   und Versionswahl (Lastenheft 6.4 überwiegend offen).
3. **Kein Betriebs-/Herden-Aggregat**: Tiergruppen (`feeding_groups`) hängen direkt am
   Tenant; FeedingBusiness/FarmSite/Herd fehlen; keine CRM-Business-Partner-Verknüpfung
   (Lastenheft 6.1/6.2 teiloffen). `business_partner_id`-Standard existiert
   (`docs/…/db_identity_satellite_standard`-Memory, CRM-Domain).
4. **Kein Fütterungsplan-Aggregat**: aktive Version + Mobil-Protokoll existieren,
   aber keine FeedingPlanVersion/MixingInstruction mit Skalierung/PDF (6.10).
5. **Bedarfsrechnung steckt im Solver-Wizard**: GfE/DLG-Profile vorhanden, aber kein
   eigenständiges RequirementProfile-Aggregat mit Normsystem-Versionierung als Daten (6.5 PARTIAL).
6. **Berichte**: PDF-/Review-Pfad für Rationen vorhanden (Ausgabe-Zeile Paritätsmatrix);
   Beratungsbericht/Berichtspakete fehlen (6.13/6.15).
7. **Beratung/Maßnahmen**: keine ConsultingCase/Measure-Entitäten (6.13) — Paritätsmatrix
   führt „Maßnahmen mit Verantwortlichem und Fälligkeit" als offenen Ausbau.
8. **DDW-Live-Pfade** bewusst offen bis Partnervertrag (BLOCKED, extern).
9. **Geldwerte**: Solver rechnet float (fachlich ok für Optimierung); abrechnungsrelevante
   Pfade müssen bei Plan/Bericht-Aggregaten Decimal verwenden (Modellierungsgrundsatz 8).
10. **Doppelte Namensräume Futtermittel**: `pages/futtermittel/*` (Handel/Produktion,
    DOM-FEED-Kette) vs. Feed-Advice (Beratung) — bei Betriebsakte sauber trennen.
