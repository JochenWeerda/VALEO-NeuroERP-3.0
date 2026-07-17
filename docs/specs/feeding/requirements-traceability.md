---
title: "Fütterungsberatung — Requirements-Traceability (Phase 2)"
type: reference
audience: [entwickler, fachlich, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Maschinenlesbare Zuordnung jeder Lastenheft-Anforderung zu IST-Code, Gap, Umsetzungspfad und Testnachweis.
---

# Requirements-Traceability Fütterungsberatung

Quelle: `lastenheft-fuetterungsberatung.md`. Granularität: Anforderungsgruppe je
Lastenheft-Abschnitt; Verfeinerung auf Einzelanforderungen erfolgt beim Claim des
jeweiligen Inkrements (IDs bleiben stabil, Unterpunkte werden `-a`, `-b`, …).

Status: `NOT_ANALYZED` · `NOT_IMPLEMENTED` · `PARTIAL` · `IMPLEMENTED_UNVERIFIED` · `VERIFIED` · `BLOCKED` · `NOT_APPLICABLE`.

## Kapitel 4 — Rollen und Mandanten

| ID | Anforderung | Prio | IST-Datei/API | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-RBAC-001 | Mandantentrennung | MUSS | `app/core/tenant.py`, alle Rations-Services tenant-scoped | VERIFIED | — | vorhanden | `test_rations_controlling.py` (Tenant-Isolation), `test_rations_lifecycle_api.py` | Slice 009/013 |
| FEED-RBAC-002 | Rollenbasierte Zugriffe (Lesen/Bearbeiten/Freigabe/Admin) | MUSS | `app/agrar/rations/authz.py` + 4 Router | VERIFIED | Rollen nur auf Domänenebene | IdP-Rollout betriebsindividuell | `test_rations_authz.py` (24) | FEED-ADVICE-ROLES-013 |
| FEED-RBAC-003 | Rechte je Betrieb/Standort/Herde/Beratungsfall | MUSS | `feeding_business_service.py`, `feeding_core.py` | VERIFIED | Beratungsfall-Scoping folgt mit FEED-CASE-030 | Betriebs-Grants zusätzlich zu Domänenrollen; tenant- und hierarchiesichere Verknüpfung | `test_feeding_business_core.py` | FEED-CORE-015 |
| FEED-RBAC-004 | Externe Berater je Betrieb, zeitlich begrenzt | SOLL | `feeding_business_grants.valid_until` + append-only Widerruf | VERIFIED | — | aktive Grants mit Scope-Hierarchie und Gültigkeitsfenster | `test_feeding_business_core.py` | FEED-CORE-015 |
| FEED-RBAC-005 | Änderungsprotokoll fachlicher Änderungen | MUSS | Lifecycle-Audit (`rations_lifecycle_service.py`), Controlling recorded_by | PARTIAL | Audit nur Lifecycle/Controlling, nicht Stammdaten | AuditEvent je Aggregat in Inkrement 1 | `test_rations_lifecycle_domain.py` | Slice 007 |

## Kapitel 6.1 — Betriebs-/Kundenverwaltung

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-BUS-001 | CRM-Partner als Fütterungsbetrieb aktivieren | MUSS | `POST /feeding/businesses/activate-from-partner`, `business_partner_id` | VERIFIED | — | idempotente fachliche Projektion ohne Partnerduplikat | `test_feeding_business_core.py` | FEED-CORE-015 |
| FEED-BUS-002 | Betriebsstätten/Herden/Ställe je Betrieb | MUSS | `feeding_businesses` → `farm_sites` → `herds` → `feeding_groups` | VERIFIED | Stall als Standort-/Herdenmerkmal, kein eigenes Aggregat | tenant- und betriebsgebundene Hierarchie | `test_feeding_business_core.py` + DB-Integration | Migration `feed_core_business_20260715` |
| FEED-BUS-003 | Betriebsakte (Analysen/Rationen/Aufgaben/Berichte gebündelt) | MUSS | native Betriebsakte mit Gruppen, Rationen, Analysereife, Befunden und Vorlagen | PARTIAL | direkte Analysenliste, Aufgaben und Berichte folgen additiv | grant-sichere ObjectPage-Projektion ohne erfundene Null-KPIs | Backend-/Screen-/Vitest `test_feeding_ration_templates*` | FEED-EDITOR-025 |
| FEED-BUS-004 | Beratungsstatus/Risiko-Filter | SOLL | — | NOT_IMPLEMENTED | — | Release C | — | — |

## Kapitel 6.2 — Tiergruppen

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-HERD-001 | Tiergruppen-Stamm (Tierzahl, LM, Laktation, Leistung, System) | MUSS | `feeding_groups` inkl. Trächtigkeit, Inhaltsstoffe, Risiko, Gültigkeit und Revision | VERIFIED | — | typisierte Domain-/API-/DB-Regeln plus native ObjectPage | `test_feeding_groups_core.py`, `test_rations_lifecycle_api.py` | FEED-CORE-016 |
| FEED-HERD-002 | Milchvieh-Gruppentypen (Frischmelker…Jungvieh) | MUSS | `GroupProfile` + `profile_code` mit zehn kontrollierten Profilen | VERIFIED | — | zentraler Enumvertrag und Legacyprofil `custom` | `test_feeding_groups_core.py` | FEED-CORE-016 |
| FEED-HERD-003 | Gruppenwechsel + Parameterhistorie | SOLL | append-only `feeding_group_revisions`; Herd-Data-Deltas erfassen Gruppenwechsel; **`animal_group_snapshots`**: taegliche idempotente Verdichtung der group_kpi-Deltas je Gruppe (Mapping external_ref, Tageskorrektur = juengster Sync gewinnt), Historie via `GET /feeding/groups/{id}/parameter-history`; **Veraltet-Warnung** (`parameters_confirmed_at`, Schwelle 30 Tage) mit Bestaetigen-Endpoint und `group_parameters_stale`-Finding in der Draft-Bewertung (Text mit Alter, nie nur Farbe) | VERIFIED | zeitliche Tiermitgliedschaften (`animal_group_memberships`) bleiben Integrationsrest | `/feeding/groups/{id}/parameter-history`, `/parameter-staleness`, `/confirm-parameters` | `test_feeding_herd_snapshots_api.py`, Core-/Connector-Tests | FEED-CORE-016, FEED-HERD-043 |
| FEED-HERD-004 | Import aus Herdenmanagement | SOLL | Herd-Data-Delta-Sync (DDW-neutral) | PARTIAL | reale Providerpfade | BLOCKED bis Partnervertrag | dito | Slice 010 |

## Kapitel 6.3 — Futtermittel-Stammdaten

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-MAT-001 | Identität/Klassifikation | MUSS | vorhandener Einzelfuttermittelkopf + `feed_kind`, Zertifikate, Konservierung, Freigabe, Gueltigkeit, Revision und native ObjectPage | VERIFIED | — | kanonischer Feed ohne zweite Stammdatenidentitaet | `test_feeding_feed_catalog.py`, `test_feeding_feed_catalog_api.py` | FEED-CORE-018 |
| FEED-MAT-002 | Mengen/Preise (FM/TM, Preisgültigkeit, Min/Max je Tier) | MUSS | FeedProduct mit Gebinde, Mindestabnahme, Preis, Fracht und Gueltigkeit; Bestand/Min-Bestand am Kopf; Min/Max im Solver | VERIFIED | — | Solveradapter rechnet Landed Price deterministisch auf EUR/kg TM | Catalog-/Golden-/Readiness-/LP-Tests | FEED-CORE-018 + Slice 008 |
| FEED-MAT-003 | Nährstoffmatrix erweiterbar (TM…Mykotoxine) | MUSS | `feeding_nutrient_definitions` mit globalem/tenantgebundenem Scope, Herkunft, Wertebereich und Revision | VERIFIED | Solver-Feldadapter folgt separat in FEED-CORE-018 | versionierter Datenkatalog inkl. Mykotoxin-Erweiterung | `test_feeding_reference_data.py`, `test_rations_reference_data_api.py` | FEED-CORE-017 |
| FEED-MAT-004 | Artikelstamm-/Einkaufs-Verknüpfung, Chargen | SOLL | `feed_chain_article_map_20260623`, Feed-Chain-Workstream | PARTIAL | Verknüpfung Beratung↔Handel offen | Inkrement 6 | `test_feed_chain_004.py` | DOM-FEED |
| FEED-MAT-005 | Nachhaltigkeitskennzahlen | KANN | Methan gekennzeichnet (Controlling) | PARTIAL | CO₂/Fläche fehlen | Release C+ | `test_rations_controlling.py` | Slice 009 |

## Kapitel 6.4 — Analysen

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-LAB-001 | Analyse manuell erfassen + historisieren + aktive Analyse | MUSS | kanonischer FeedAnalysis-Kopf, flexible Werte, append-only History und scope-spezifisch aktive Version | VERIFIED | — | native Meridian-Worklist/ObjectPage und optimistischer Lifecycle | `test_feeding_feed_analysis.py`, `test_feeding_feed_analysis_api.py`, Frontend-Komponententest | FEED-CORE-019 |
| FEED-LAB-002 | Labor-Import (Datei/API) mit Vorschau/Validierung | MUSS | nebenwirkungsfreie PDF/CSV-Vorschau, SHA-256, Materialzuordnung, DMS-Belegblocker und Labor-Adapter | VERIFIED | produktiver DMS-Upload/Virenscan bleibt Connector-Betriebsvertrag, nicht Analysepersistenz | Import-Overlay und typisierte Preview-/Document-Reference-API | Import-/DMS-Integrationstest in `test_feeding_feed_analysis_api.py` | FEED-CORE-019; FEED-INT-034 vertieft Provider-Mappings |
| FEED-LAB-003 | FM/TM-Bezug, Einheitenumrechnung, Plausibilität | MUSS | versionierte UnitDefinition, dimensionssichere Decimal-Konvertierung, explizite Mengen-/Konzentrationssemantik und Wertebereiche | VERIFIED | Konsumentenadapter werden inkrementell auf den Vertrag umgestellt | zentrale Domain-/API-Regeln und native Referenzansicht | Property-/Boundary-/API-Tests in `test_feeding_reference_data.py` und `test_rations_reference_data_api.py` | FEED-CORE-017 |
| FEED-LAB-004 | Schätzwerte eindeutig kennzeichnen | MUSS | jeder Analysewert trägt `measured`, `calculated` oder `estimated`; API und UI zeigen Provenienz | VERIFIED | — | kanonischer Analysewertvertrag | Domain-, API- und UI-Test FEED-CORE-019 | FEED-CORE-019 |

## Kapitel 6.5 — Bedarf

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-REQ-001 | Bedarf nach Tiergruppe/Leistung/Stadium (GfE 2023) | MUSS | `constants/gfe2023.py`, Wizard-Requirements | VERIFIED | — | vorhanden | `test_rations_wizard_requirements.py`, `test_process_kernel_wave74_rations_optimization.py` | Fodjan-/DLG-Abgleich 2026-07 (Memory: Formeln korrekt) |
| FEED-REQ-002 | Normsystem-Versionierung als Daten (EvaluationSystemVersion) | MUSS | `evaluation_systems`/`evaluation_system_versions` (idempotent geseedet, append-only, `module_ref` auf golden-getesteten Code) + `requirement_profiles` (Eingaben, gekennzeichnete Schätzwerte, Systemversion, reproduzierbares Ergebnis) | VERIFIED | Formeln bleiben bewusst Code-SSOT | `feeding_requirements_service.py` + `/feeding/evaluation-systems`, `/feeding/requirement-profiles` | `test_feeding_requirements.py`, `test_feeding_requirements_api.py` | FEED-CORE-020 |
| FEED-REQ-003 | Hitzestress/Weide/Übergangsphasen | SOLL | Weide-/Saisonprofile im Solver | PARTIAL | Hitzestress fehlt | Release C | `test_rations_optimization_{pasture,seasonal_profiles,spring_pasture_case}.py` | — |
| FEED-REQ-004 | Trockensteher-Bedarf | MUSS | DLG-2025-Konstanten | VERIFIED | — | vorhanden | `test_rations_dcab_dlg2025.py` | DLG 01/2025 |

## Kapitel 6.6 — Rationserstellung

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-RAT-001 | Zeilen-CRUD, FM/TM, Fixierung, Min/Max in der Ration | MUSS | Native Editor-Journey bewahrt Min/Max in Draft/API/Versionssnapshot und bewertet Grenzverletzungen live; Workbench-Fixierung bleibt kompatibel | VERIFIED | — | `RationEditor`, typisierter Draft-Vertrag und deterministische Bound-Pruefung | Domain/API/Vitest `test_feeding_ration_editor*`, `ration-editor.test.tsx` | Slice 006, FEED-EDITOR-024 |
| FEED-RAT-002 | Versionierung, Status, Gültigkeit, unveränderliche Freigabe | MUSS | Rationsversion/Lifecycle plus unveraenderliche Planversion mit `valid_from`/`valid_until` | VERIFIED | — | freigegebene Rezeptur und zeitlich gueltiger Ausfuehrungssnapshot getrennt | Lifecycle- und `test_feeding_plan*` | Slice 007, FEED-PLAN-026 |
| FEED-RAT-003 | Kopieren/Vorlagen | MUSS | append-only Vorlagenkatalog mit Quellversion; gruppensicheres Apply erzeugt neue Draft-Version | VERIFIED | — | Herkunft, Auditgrund und optimistische Zielversion sind Pflicht | `test_feeding_ration_templates.py`, `test_feeding_ration_templates_api.py`, UI-Test | FEED-EDITOR-025 |
| FEED-RAT-004 | Undo/Redo, Mischreihenfolge-Sortierung, Tastatur | MUSS | Rationseditor-Komfortstufe live (`features/feed-advice/RationEditor.tsx`): Undo/Redo fuer ungespeicherte Aenderungen (zusammenhaengende Feldeingabe = 1 Schritt; Buttons + Strg+Z/Y ueber Window-Listener), Mischreihenfolge-Sortierung per Zeilen-Buttons mit `mixing_sequence` persistiert im Versions-Snapshot (Laden sortiert danach), Enter springt zur naechsten Position, progressive Expertenspalten (Ca/P/Na/Mg/K aus additiv erweiterten `NUTRIENT_KEYS` in `ration_draft.py`; fehlende Werte None/– nie 0) | VERIFIED | Drag-and-drop-Sortierung bleibt optionaler Komfortausbau | FEED-EDITOR-041 | `ration-editor.test.tsx` (10, davon 4 Komfortstufe), `test_feeding_ration_editor.py` (Minerale) | FEED-EDITOR-021, FEED-EDITOR-041 |
| FEED-RAT-005 | Kosten je Tier/Tag, ct/kg ECM, Versionsdiff | MUSS | Praxis-KPIs (ct/kg ECM, KF-TM/kg ECM, €/Kuh/Tag) | VERIFIED | Versionsdiff-Ansicht offen | Inkrement 2 | Vitest Workbench | Slice 006 |

## Kapitel 6.7 — Optimierung

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-OPT-001 | Kostenminimum + harte Nebenbedingungen | MUSS | LP-Solver `solver/lp_constraints.py` | VERIFIED | — | vorhanden | `test_rations_lp_constraints.py` + DLG-Golden-Tests | — |
| FEED-OPT-002 | Mehrstufige Ziele (Kosten/IOFC/Leistung/Gesundheit/Umwelt) | MUSS | `lp_stage2.py`, lexikografisch Milch, Zielstrategie-Kalibrierung | VERIFIED | — | vorhanden | `test_rations_{milk_lexicographic,objective_strategy_calibration}.py` | — |
| FEED-OPT-003 | Weiche Nebenbedingungen/Penalties, SARA-Reopt, peNDF-Demotion | MUSS | FAN-Modus 005 Penalties, SARA-Reopt | VERIFIED | — | vorhanden | `test_rations_optimization_{fan_mode_005_penalties,sara_reopt,pendf_demotion}.py` | — |
| FEED-OPT-004 | Unlösbarkeit erklären, Konfliktgrenzen benennen | MUSS | Solverdiagnose liefert rationale/suggestions; Editor-Vorpruefung benennt min>max, Mengenverletzung und TM-Minimumsummenkonflikt; **Optimieren im Editor** (`POST /feeding/ration-versions/{id}/optimize`) verbindet beide Schichten: bei Unloesbarkeit `explanation` mit Solver-diagnosis/warnings + Grenzbefunden (024) und dokumentiertem Run status `infeasible` | VERIFIED | echte LP-IIS/Shadow-Prices sind SOLL-Ausbau FEED-OPT-006 | deterministische Vorpruefung + Solverdiagnose + Editor-Optimize-Pfad | `test_feeding_ration_editor.py`, `test_feeding_editor_optimize_api.py`, FAN-Infeasibility-Tests | FEED-EDITOR-024, FEED-OPT-042 |
| FEED-OPT-005 | Ergebnis reproduzierbar speichern (OptimizationRun) | MUSS | `optimization_runs` (solver_version, Ziel, Parameter, Status, Dauer, Pflichtbezug auf `ration_version`) **plus automatischer Hook**: Optimieren im Editor erzeugt Candidate-Version (source `optimizer`, nie Aktivierung) und Run in EINER Transaktion — kein Ergebnis ohne persistierten Run; infeasible-Laeufe dokumentieren die Quellversion | VERIFIED | Pareto/Sensitivitaet = FEED-OPT-006 | `/feeding/optimization-runs`, `/feeding/ration-versions/{id}/optimize` | `test_feeding_requirements.py`, `test_feeding_editor_optimize_api.py` | FEED-CORE-020, FEED-OPT-042 |
| FEED-OPT-006 | Pareto-Katalog, Sensitivität, Shadow Prices | SOLL | — | NOT_IMPLEMENTED | Paritätsmatrix „Nächster Ausbau" | Release C | — | — |
| FEED-OPT-007 | Keine ungefragte Aktivierung | MUSS | Solver übergibt nur Entwurfssnapshots (ADR-041) | VERIFIED | — | vorhanden | `test_rations_lifecycle_api.py` | Slice 007 |

## Kapitel 6.8 — Bewertung

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-EVAL-001 | Kennzahl+Ist+Ziel+Bedeutung+Empfehlung | MUSS | Strukturierte Befunde (Code, 4-stufiger Schweregrad, Ist, Ziel, Klartext) + Deltas + Abdeckungsstatus; **persistente `ration_evaluations` je unveränderlicher Version** (append-only per Trigger, serverseitig aus dem Snapshot abgeleitet — keine Client-Payload) mit Profil-/Regelversionsbezug | PARTIAL | Ursache/Folge/Empfehlung als eigene strukturierte Felder + Kategorienabdeckung (Mineralstoffe/Struktur/Gärqualität) | Inkrement 2 Folgepakete | `test_feeding_ration_editor{,_api}.py` (9), DLG-Golden-Tests | FEED-EDITOR-021/022 |
| FEED-EVAL-002 | Warnungs-Priorisierung, nicht nur Farbe | MUSS | 4-stufige Priorität als Datenmodell (`SEVERITY_ORDER` critical/high/medium/info, Befunde priorisiert geordnet, Textlabel je Stufe + Klartext-Message); Befund→Ursache-Navigation fokussiert die verursachende Position | VERIFIED | Kategorienausbau (Mineralstoffe/Struktur) folgt mit weiteren Regeln | Draft-/Versionsbewertung | `test_feeding_ration_editor.py::test_findings_carry_four_level_priority_and_are_ordered`, `ration-editor.test.tsx` (5) | FEED-EDITOR-022 |
| FEED-EVAL-003 | Freigabe trotz Warnung nur mit Begründung | MUSS | Readiness-Blocker + `OVERRIDE:`-Begründung im Lifecycle-Audit | VERIFIED | — | vorhanden | `test_rations_readiness.py` | Slice 008 |

## Kapitel 6.9 — Variantenvergleich

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-CMP-001 | Zwei Rationen/Versionen vergleichen (Futtermittel/Nährstoff/Kosten-Diff) | MUSS | `POST /feeding/ration-versions/compare` (deterministisch, gleiche Gruppe erzwungen → 409, fehlende Seite bleibt unbekannt/nie 0-günstig) + Vergleichsseite `futtermittel/rationsvergleich` (Komponenten-/Kennzahlen-Diff, Befunde beider Seiten) | VERIFIED | Druck-/PDF-Export und Kommentar je Variante folgen mit Berichtspaket (FEED-REP) | compare_drafts + Seite | `test_feeding_ration_editor.py::test_compare_drafts…`, API-Journey (409/404/403), `ration-comparison.test.tsx` (2) | FEED-EDITOR-023 |
| FEED-CMP-002 | Szenarien (Preis/Analyse/Leistung) | SOLL | — | NOT_IMPLEMENTED | Paritätsmatrix Wirtschaftlichkeit | Release C | — | — |

## Kapitel 6.10 — Fütterungsplan

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-PLAN-001 | Freigegebene Ration als Planversion (Skalierung, Mischreihenfolge, PDF) | MUSS | unveraenderliches Aggregat plus native ObjectPage und reproduzierbarer Browserdruck/PDF mit Herkunft | VERIFIED | signierter Server-PDF-Job ist Berichts-Ausbau, nicht Kernplan | Serverpublikation und Meridian-Planansicht | Backend-, Component- und Mobile-Tests | FEED-PLAN-026/027 |
| FEED-PLAN-002 | Mobile Ansicht + Offline-Fallback | MUSS | aktuelle Planversion mit planversionsgebundenem v2-Cache; Legacy-Rationscache wird ignoriert | VERIFIED | Offline-Sync-Konflikte der Ist-Erfassung folgen FEED-ACT | `/feeding/plans/current` statt Snapshot-Nebenwahrheit | Component + Playwright Mobile | FEED-PLAN-027 |
| FEED-PLAN-003 | Mischwagen-/Roboterexport, Rückmeldung | SOLL | Export `GET …/mixer-export` (deterministisch aus unveränderlicher Planversion, Referenz=plan_version_id, stale → 409) + Rückmeldung `POST /feeding/mixer-feedback` (idempotent via client_ref, Soll/Ist-Delta je Instruktion + Mischgenauigkeit, **veraltete Planversion → Quarantäne-Job im 034-Monitor statt Datenverlust**); dazu agrirouter-Import (010) | VERIFIED | reale Provider-Transportanbindung bleibt Teil des externen Partnervertrags-Gates | Mixer-Service + Monitor-Kopplung | `test_feeding_mixer_api.py` (3, inkl. Konflikt-Journey) | Slices 010/034/035 |

## Kapitel 6.11 — Soll-Ist-Controlling

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-ACT-001 | Istmengen erfassen (manuell/Schnittstelle), idempotent | MUSS | `rations_controlling.py` observations + Quellen manual/mixing_wagon/herd_data/import | VERIFIED | — | vorhanden | `test_rations_controlling.py` | Slice 009 |
| FEED-ACT-002 | Abweichung absolut/%, Nährstoff-/Kostenfolge, Verlauf | MUSS | append-only ActualFeeding je Planinstruction mit Decimal Soll/Ist/Delta/%, eingefrorener Preis-/Naehrstofffolge und nativer Komponentenprojektion; Tagestrends vorhanden | VERIFIED | Schwellen/Aufgaben siehe FEED-ACT-030 | FEED-ACT-029 | `test_feeding_actual.py`, `test_feeding_actual_api.py`, `feeding-plan-mobile.test.tsx` | ADR-052, FEED-ACT-029 |
| FEED-ACT-003 | Mischgenauigkeit, Restfutter, Lade-/Mischzeiten | SOLL | `control/feeding_control.py` (<5%-Regelkreis) | VERIFIED | UI-Verlauf offen | Inkrement 4 | `test_rations_{feeding_control_dlg2025,mixing_protocol}.py` | DLG 01/2025 |
| FEED-ACT-004 | Aufgaben aus Abweichungen, Ursachenklassifikation | MUSS | tenant-/klassenbezogene Policyversionen; planversionsgebundene Findings; menschlicher, idempotenter append-only Massnahmen-Command mit Owner, Termin und Grund; Ursachenklasse am ActualRecord | VERIFIED | — | FEED-ACT-029/030 | `test_feeding_actual_measures.py`, `test_feeding_actual_api.py`, `feeding-actual-page.test.tsx` | ADR-052/053, FEED-ACT-030 |

## Kapitel 6.12 — Leistungscontrolling

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-PERF-001 | Milch/ECM, Futterkosten, Effizienz, N-Effizienz, Methan je Gruppe | MUSS | `controlling.py` + Tagesreihe + Trends | VERIFIED | — | vorhanden | `test_rations_controlling.py`, `test_rations_efficiency_dlg2025.py` | Slices 009/012 |
| FEED-PERF-002 | IOFC | MUSS (sofern Daten) | Tagespunkt speichert Milchpreis, Milchumsatz und IOFC mit offengelegter Formel; unvollstaendige Basis bleibt `null`; Trendmetriken enthalten IOFC | VERIFIED | — | FEED-ACT-030 | `test_feeding_actual_measures.py`, `test_rations_controlling.py`, `feed-controlling-trends.test.tsx` | ADR-053, FEED-ACT-030 |
| FEED-PERF-003 | Verlauf vor/nach Rationswechsel (Version im Zeitverlauf) | MUSS | jeder Tagespunkt traegt effektive FeedingPlanVersion-ID/-Nummer; Trend-UI zeigt datierte Textmarker bei Wechseln | VERIFIED | — | FEED-ACT-030 | `test_rations_controlling.py`, `feed-controlling-trends.test.tsx` | ADR-053, FEED-ACT-030 |
| FEED-PERF-004 | MLP/Milchgüte/AMS-Kennzahlen (Harnstoff, FEQ, Zellzahl) | SOLL | Tagesreihe additiv um `milk_urea_mg_dl` + `somatic_cell_count_k` (Provenienz via source je Beobachtung); FEQ deterministisch berechnet (`fat_protein_quotient`, None-sicher — nie 0); **Vorher/Nachher-Auswertung** `GET /feeding/performance/version-impact` je aktivierter Version mit ehrlicher Unsicherheit (n je Seite, Fenster, `insufficient_data`); ICAR-Adapter (010) als Importquelle | VERIFIED | AMS-Livepfade = Partnervertrags-Gate; Trend-Chart für Harnstoff/Zellzahl als FE-Rest | Controlling + Performance-Endpoint | `test_feeding_performance_api.py` (4), `test_rations_controlling.py` | Slices 010/030/033 |
| FEED-PERF-005 | Benchmarking Gruppen/Betriebe | SOLL | Gruppen-Benchmark (kuhzahl-gewichtet); **Zeitraumvergleich** (`GET /feeding/performance/period-comparison`, aktuell vs. Vorzeitraum, `insufficient_data` unter n=7); **tenant-interner Kennzahlprofil-Benchmark** (`GET /feeding/performance/group-benchmark`, Gruppe vs. Peer-Median der uebrigen Tenant-Gruppen, `scope=tenant_internal` explizit); **Benchmark-Export** als `report_type benchmark` der Report-Entitaet inkl. CSV | PARTIAL | **anonymisierter Betriebsvergleich BLOCKED** — wartet auf Auftraggeber-/Datenschutzentscheidung (Opt-in-Modell, externes Gate) | Freier Teil umgesetzt (FEED-PERF-044); Betriebsvergleich Release C nach Opt-in-Entscheid | `feed-controlling-trends.test.tsx`, `test_feeding_benchmark_api.py` | Slice 012, FEED-PERF-044 |

## Kapitel 6.13 — Beratung/Maßnahmen

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-CONS-001 | Beratungsfall (Besuch, Beobachtung, Foto, Bewertung, Bericht) | MUSS | `consulting_cases` (Besuch/Remote, Betrieb-/Gruppenbezug, Ausgangssituation, Abschlussbewertung; geschlossen = keine neuen Beobachtungen → 409) + `consulting_observations` (append-only per Trigger, Kategorien+Freitext, DMS-Fotoreferenzen, **idempotenter Mobil-Vertrag via client_ref**); Worklist+Falldetail `futtermittel/beratung` | PARTIAL | strukturierte fachliche Bewertung/Empfehlung (032) + Beratungsbericht (040) | Inkrement 5 Folgeslices | `test_feeding_consulting_api.py` (6), `consulting-cases.test.tsx` (3) | FEED-CONS-031 |
| FEED-CONS-002 | Maßnahmen (Verantwortlicher, Fälligkeit, Status, Wirksamkeit) | MUSS | append-only Lifecycle mit Owner, Termin, Wiedervorlage, Eskalation, Optimistic Concurrency und verpflichtender Wirksamkeitskontrolle; Business-Grant-sichere Historie und zugänglicher Abschluss im Beratungsfall | VERIFIED | — | FEED-CONS-032 | `test_feeding_measure_lifecycle.py`, `test_feeding_measure_lifecycle_api.py`, `consulting-cases.test.tsx` | ADR-055, FEED-CONS-032 |
| FEED-CONS-003 | Workflow-/CRM-Aufgabenintegration | SOLL | flow_spines/CRM-Aktivitäten existieren systemweit | PARTIAL | Verknüpfung | Inkrement 5/6 | — | — |

## Kapitel 6.14 — Bedarf/Bestand/Einkauf

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-SUP-001 | Reichweite/Unterdeckung aus aktiven Rationen | MUSS | aktuelle FeedingPlanInstructions; Decimal-Netto-/Sicherheits-/Bruttobedarf, Bestand, Reichweite, Unterdeckung und Handelseinheitsrundung; unbekannter Bestand bleibt unbekannt | VERIFIED | Chargen/Reservierungen siehe FEED-SUP-002 | FEED-SUP-028 | `test_feeding_supply.py`, `test_feeding_supply_api.py` | ADR-051, FEED-SUP-028 |
| FEED-SUP-002 | Chargen-FIFO, Reservierungen | SOLL | — | NOT_IMPLEMENTED | Paritätsmatrix Futterbestand | Inkrement 6 | — | — |
| FEED-SUP-003 | Bestellvorschlag/Übergabe Einkauf | SOLL | planbezogener, idempotenter und auditierter Handoff mit atomarem Outbox-Ereignis; keine automatische Bestellung; native Bestaetigungsjourney | VERIFIED | Konsumentenprojektion im Einkauf kann auf Event aufsetzen | FEED-SUP-028 | `test_feeding_supply_api.py`, `feeding-supply-page.test.tsx` | ADR-051, FEED-SUP-028 |

## Kapitel 6.15 — Berichte

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-REP-001 | Rations-PDF mit Version/Freigabe | MUSS | druckfaehige Planprojektion mit Plan-/Quellversion, Gueltigkeit, Druckstand und Mischfolge; zusaetzlich Report-Entitaet mit reproduzierbaren, profilierten Ausgaben (feeder/farmer/advisor) aus unveraenderlicher Planversion, append-only, content_hash-idempotent | VERIFIED | signiertes Archiv-PDF + DMS-Zustellung sind REP-Folgeausbau (dms_document_ref vorbereitet) | Print-Zweig + `feeding_reports` (Tabelle + Trigger, `report_profiles.py`, `feeding_reports_service.py`, `feeding_reports.py`) | `feeding-plan-detail.test.tsx`, `test_feeding_reports_api.py` | FEED-PLAN-027, FEED-REP-039 |
| FEED-REP-002 | Beratungsbericht, Soll-Ist-, Verlaufsbericht | MUSS | Beratungsbericht (aus unveraenderlichem Fall-Entwurf, farmer ohne interne Steuerfelder), Soll-Ist-Bericht (Komponenten-Aggregation je Planversion, advisor mit Ursachenverteilung; Datenstand-Aenderung ⇒ neuer Bericht statt stiller Ueberschreibung) und Verlaufsbericht (Controlling-Tagesreihe je Gruppe, deterministisch ohne today()-Fenster, advisor mit Versionsmarkern) als `report_type`s der Report-Entitaet; CSV fuer strukturierte Typen | VERIFIED | PDF/DMS/Zustellung und Berichte-Maske bleiben REP-Rest | FEED-CONS-032, FEED-REP-039, FEED-REP-040 | `test_feeding_consulting_report_api.py`, `test_feeding_reports_pack2_api.py`, `consulting-cases.test.tsx` | ADR-055, FEED-CONS-032, FEED-REP-040 |
| FEED-REP-003 | CSV/Excel-Export | MUSS | grant-gefilterter UTF-8-CSV-Export der Ist-Fuetterung; zusaetzlich CSV-Export strukturierter Berichtsdaten (`GET /feeding/reports/{id}/csv`, Mischfolge mit Kopfzeile) | VERIFIED | weitere Berichtstypen bleiben eigene Requirements | FEED-ACT-029, FEED-REP-039 | `test_feeding_actual_api.py`, `feeding-actual-page.test.tsx`, `test_feeding_reports_api.py` | ADR-052, FEED-ACT-029 |

## Kapitel 6.16 — Zusammenarbeit/Freigaben

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-COLLAB-001 | Statusworkflow + Freigabehistorie + Unveränderlichkeit | MUSS | Lifecycle-Statusautomat + Audit + Checksum | VERIFIED | — | vorhanden | `test_rations_lifecycle_domain.py` | Slice 007 |
| FEED-COLLAB-002 | Kommentare, Änderungsanforderung, Benachrichtigung | MUSS | Reviewgründe persistent; idempotente Overdue-Events und tenant-/grant-/empfängersicheres In-App-Read-Model mit stabilem Deep-Link | PARTIAL | globale Glocke, Kanalpräferenzen und externe Push-Zustellung | FEED-CONS-032 plus Folgeausbau | `test_feeding_measure_lifecycle_api.py` | ADR-055, FEED-CONS-032 |
| FEED-COLLAB-003 | Vier-Augen-Prinzip konfigurierbar | SOLL | APPROVE-Rollen getrennt von WRITE | PARTIAL | erzwungene Fremd-Prüfung | Release B | `test_rations_authz.py` | Slice 013 |

## Kapitel 6.17/6.18 — UI/Mobil

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-UI-001 | Mask-Builder-Muster, Design-Tokens, WCAG 2.2 AA | MUSS | native SDs, Token-System, axe 8/8, Chart-Palette validiert | VERIFIED | — | laufend | axe-E2E, Vitest | Design-Audit (alle 8 Punkte) |
| FEED-UI-002 | Betriebsakte/Fütterungsübersicht/Rationseditor-Seiten | MUSS | Cockpit `agrar/feed-advice` + Aufgabenkacheln; Rationseditor-Kernseite (FEED-MASK-009 Split-Layout: Positionsfläche + sticky Bewertung) unter `futtermittel/rationseditor?ration_id=…` | PARTIAL | Betriebsakte, Fütterungsübersicht, Variantenvergleich, Berichte, Integrationsmonitor (Kap. 10) | Inkremente 2–5 | `feed-advice-entry.test.tsx`, `ration-editor.test.tsx` | ADR-041, FEED-EDITOR-021 |
| FEED-MOB-001 | Mobile MUSS-Fälle (Plan, Istmengen, Beobachtung, Foto) | MUSS | Mobil-Protokoll (Plan+Istmengen); Beobachtung+Foto-Referenz über idempotenten `client_ref`-Vertrag; **Offline-Queue** (`lib/offline/feeding-offline-queue.ts`): Netzwerkfehler reiht die unveraenderte API-Payload mit fixiertem idempotency_key ein (kein zweiter Datenpfad), Replay bei Mount/online über dieselbe API, 409 → sichtbarer Konflikt "Plan veraltet" (nie blind erneut), Fehler → failed mit Text + explizitem Erneut-senden/Verwerfen | PARTIAL | Kamera-Anbindung für Beobachtungsfotos braucht den DMS-Upload-Vertrag (expliziter Rest); Maßnahme abhaken mobil (032) | Inkrement 7-Rest | Playwright, `feeding-offline-queue.test.ts`, `fuetterungsdokumentation-mobil-offline.test.tsx` | Slices 007/031, FEED-MOB-045 |

## Kapitel 6.19 — Schnittstellen

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-INT-001 | Idempotente Importe, Dubletten, Audit, Vorschau, Quarantäne | MUSS | payload_hash + ON CONFLICT (010) **plus Integrationsmonitor**: `feeding_import_jobs` mit Statusautomat validated→accepted / quarantined→rejected, Vorschau ohne Persistenz (Adapter = Validierungs-SSOT), Übernahme über den bestehenden idempotenten Pfad, Verwerfen nur mit Pflicht-Begründung; Monitor-Worklist `futtermittel/integrationsmonitor` | VERIFIED | interaktives Material-Mapping als eigene Worklist folgt (FEED-INT-034-Rest/035) | Monitor + Direktpfad | `test_feeding_import_monitor_api.py` (7), `import-monitor.test.tsx` (3), Bestandstests 010 | Slices 010/034 |
| FEED-INT-002 | Connector-Gates (Consent/Contract/Secret/Egress) | MUSS | HerdDataSyncService-Gates, Admin-Level | VERIFIED | Mapping-UI/Quarantäne je Betrieb | Inkrement 6 | `test_rations_herd_data_connectors.py` (10) | Slice 010 |
| FEED-INT-003 | Reale DDW-/MLP-/Mischwagen-Livepfade | MUSS | Templates konfigurierbar, bewusst offen | BLOCKED | lizenzierter Partnervertrag erforderlich | extern | — | Paritätsmatrix |
| FEED-INT-004 | Event-Bus/Webhooks | SOLL | geschlossene Feeding-Typliste und Schema-1.0-Huelle; atomare Outbox-Emission fuer Analyse, Rationsaktivierung, Plan, Actual, Abweichung, Massnahme, Quarantaene und Einkaufsuebergabe; at-least-once mit `event_id`-Deduplizierung | VERIFIED | optionale Tenant-Webhooks bleiben Admin-Ausbau, kein Muss-Gap | FEED-INT-036 | `test_feeding_events.py`, Plan-/Actual-/Analyse-/Import-API-Tests | ADR-054, FEED-INT-036 |

## Kapitel 6.20 — KI

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-AI-001 | KI nur unterstützend, keine stille Freigabe, keine erfundenen Werte | MUSS | Copilot-/Intent-Vorschläge mit Delta-Anzeige; Freigabe nur via Lifecycle | VERIFIED | — | Leitplanke bleibt | `test_rations_lifecycle_api.py` | ADR-041 |
| FEED-AI-002 | Erklärungen/Ursachen/Maßnahmenvorschläge | SOLL | Erklärschicht + Diagnose; **deterministische Assistenzstufe** nach dem Proposal-Schema (11-agenten.md §3.1): `POST /feeding/assist/explain-findings` (facts/assumptions/recommendations mit evidence_refs, confidence aus Datenlage, requires_human_approval; append-only auditiert), `POST /feeding/assist/propose-measures` (bestätigungspflichtige proposed_commands für den bestehenden Maßnahmen-Vertrag — **nichts wird committed**), `GET /feeding/assist/substitutes` (gleiche Futterklasse, nach Preis, mit Provenienz; fehlende Analyse = benannte Unsicherheit statt Schätzung) | VERIFIED | LLM-Gateway-Anbindung inkl. Kill Switch/Injection-Suite = expliziter Folgeausbau (Modellpfad); Leitplanken FEED-AI-001..012 gelten unverändert | deterministische Rechendienste statt Modell (FEED-AI-003-konform) | `test_feeding_assist_api.py`, `test_rations_aggregator.py` | FEED-AI-046 |

## Kapitel 7 — NFR (Zusammenfassung)

| ID | Anforderung | Status | Nachweis |
|---|---|---|---|
| FEED-NFR-001 | Deterministische, reproduzierbare Berechnung + Golden-Tests | VERIFIED | ~30 Solver-/DLG-Golden-Testdateien |
| FEED-NFR-002 | Kein 0-Fabrizieren unbekannter Werte | VERIFIED | `test_rations_controlling.py`; SimpleLineChart-Lücken |
| FEED-NFR-003 | Performance (Virtualisierung, Pending-Guards, Caching) | VERIFIED (Bestand) | VirtualDataTable, Mutation-Lifecycle-Invarianten (CLAUDE.md) |
| FEED-NFR-004 | Betrieb (Logs/Metriken/Health/Alembic) | VERIFIED (Bestand) | Prometheus-Middleware, AuditMiddleware, Alembic Single-Head |
| FEED-NFR-005 | Security (OIDC/RBAC/Tenant) | VERIFIED | `test_rations_authz.py` (Slice 013) |
| FEED-NFR-006 | A11y WCAG 2.2 AA | VERIFIED (Kernrouten) | axe-E2E 8/8 |
| FEED-NFR-007 | Feature Flag + Pilot vor Rollout | PARTIAL | Module-Registry vorhanden; Feeding-Flag bei Inkrement 1 |

## Gap-Kurzbild

- **VERIFIED:** 20 Gruppen — Solver/Normsysteme/Lifecycle/Controlling/Connector-Gates/RBAC/NFR-Kern.
- **PARTIAL:** 30 Gruppen — meist „Fachkern vorhanden, Aggregat/UI fehlt".
- **NOT_IMPLEMENTED:** 9 Gruppen — Betriebsakte, Analyse-Aggregat-Vollausbau, Fütterungsplan-Aggregat, Maßnahmen/Beratungsfall, Berichte, Pareto.
- **BLOCKED:** 1 — reale Provider-Livepfade (Partnervertrag).

Der größte strukturelle Hebel ist **Inkrement 1** (Betrieb/Herde/Analyse/RequirementProfile
als Aggregate), weil fast alle PARTIAL-Zeilen darauf zeigen.
