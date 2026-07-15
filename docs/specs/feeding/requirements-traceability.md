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
| FEED-BUS-003 | Betriebsakte (Analysen/Rationen/Aufgaben/Berichte gebündelt) | MUSS | Einzelseiten vorhanden, keine Akte | NOT_IMPLEMENTED | zentrale ObjectPage fehlt | Inkrement 2 (UI) | — | — |
| FEED-BUS-004 | Beratungsstatus/Risiko-Filter | SOLL | — | NOT_IMPLEMENTED | — | Release C | — | — |

## Kapitel 6.2 — Tiergruppen

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-HERD-001 | Tiergruppen-Stamm (Tierzahl, LM, Laktation, Leistung, System) | MUSS | `feeding_groups` inkl. Trächtigkeit, Inhaltsstoffe, Risiko, Gültigkeit und Revision | VERIFIED | — | typisierte Domain-/API-/DB-Regeln plus native ObjectPage | `test_feeding_groups_core.py`, `test_rations_lifecycle_api.py` | FEED-CORE-016 |
| FEED-HERD-002 | Milchvieh-Gruppentypen (Frischmelker…Jungvieh) | MUSS | `GroupProfile` + `profile_code` mit zehn kontrollierten Profilen | VERIFIED | — | zentraler Enumvertrag und Legacyprofil `custom` | `test_feeding_groups_core.py` | FEED-CORE-016 |
| FEED-HERD-003 | Gruppenwechsel + Parameterhistorie | SOLL | append-only `feeding_group_revisions`; Herd-Data-Deltas erfassen Gruppenwechsel | PARTIAL | zeitliche Tiermitgliedschaften/überlappungsfreie Providerwechsel offen | `animal_group_memberships` in Integrationsinkrement | Core-/Connector-Tests | FEED-CORE-016 + Slice 010 |
| FEED-HERD-004 | Import aus Herdenmanagement | SOLL | Herd-Data-Delta-Sync (DDW-neutral) | PARTIAL | reale Providerpfade | BLOCKED bis Partnervertrag | dito | Slice 010 |

## Kapitel 6.3 — Futtermittel-Stammdaten

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-MAT-001 | Identität/Klassifikation | MUSS | `solver/feed.py`-Dataclass, DLG-Referenz (`repository/dlg_loader.py`), Masken `einzelfuttermittel-*`/`mischfuttermittel-*` | PARTIAL | QS/VLOG/Bio-Status, Konservierung, Freigabestatus, Gültigkeit fehlen als Felder | Inkrement 1 | `test_rations_feed_dataclass.py` | — |
| FEED-MAT-002 | Mengen/Preise (FM/TM, Preisgültigkeit, Min/Max je Tier) | MUSS | Preisgültigkeit in Readiness; Min/Max je Komponente im Solver/Workbench | PARTIAL | Fracht/Gebinde/Mindestabnahme fehlen | Inkrement 1 | `test_rations_readiness.py`, `test_rations_lp_constraints.py` | Slice 008 |
| FEED-MAT-003 | Nährstoffmatrix erweiterbar (TM…Mykotoxine) | MUSS | `feeding_nutrient_definitions` mit globalem/tenantgebundenem Scope, Herkunft, Wertebereich und Revision | VERIFIED | Solver-Feldadapter folgt separat in FEED-CORE-018 | versionierter Datenkatalog inkl. Mykotoxin-Erweiterung | `test_feeding_reference_data.py`, `test_rations_reference_data_api.py` | FEED-CORE-017 |
| FEED-MAT-004 | Artikelstamm-/Einkaufs-Verknüpfung, Chargen | SOLL | `feed_chain_article_map_20260623`, Feed-Chain-Workstream | PARTIAL | Verknüpfung Beratung↔Handel offen | Inkrement 6 | `test_feed_chain_004.py` | DOM-FEED |
| FEED-MAT-005 | Nachhaltigkeitskennzahlen | KANN | Methan gekennzeichnet (Controlling) | PARTIAL | CO₂/Fläche fehlen | Release C+ | `test_rations_controlling.py` | Slice 009 |

## Kapitel 6.4 — Analysen

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-LAB-001 | Analyse manuell erfassen + historisieren + aktive Analyse | MUSS | `grundfutteranalysen.tsx`, verifizierte Analysen in Readiness (Alter/Wechsel) | PARTIAL | eigenes FeedAnalysis-Aggregat, Versionswahl, Datei-Anhang fehlen | **Inkrement 1 (Kernstück)** | `test_rations_readiness.py` | Slice 008 |
| FEED-LAB-002 | Labor-Import (Datei/API) mit Vorschau/Validierung | MUSS | Labor-Adapter `integrations/adapters.py` (idempotent, payload_hash) | PARTIAL | Vorschau/Zuordnungs-UI, Originaldatei | Inkrement 1 + `rations-schnittstellen-import.tsx`-Ausbau | `test_rations_integrations_f5.py` | Migration `rations_integrations_20260712` |
| FEED-LAB-003 | FM/TM-Bezug, Einheitenumrechnung, Plausibilität | MUSS | versionierte UnitDefinition, dimensionssichere Decimal-Konvertierung, explizite Mengen-/Konzentrationssemantik und Wertebereiche | VERIFIED | Konsumentenadapter werden inkrementell auf den Vertrag umgestellt | zentrale Domain-/API-Regeln und native Referenzansicht | Property-/Boundary-/API-Tests in `test_feeding_reference_data.py` und `test_rations_reference_data_api.py` | FEED-CORE-017 |
| FEED-LAB-004 | Schätzwerte eindeutig kennzeichnen | MUSS | Methan `methane_estimated`; Readiness warnt statt 0 | PARTIAL | durchgängig je Kennzahl | Inkrement 1 | `test_rations_controlling.py` | Slices 008/009 |

## Kapitel 6.5 — Bedarf

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-REQ-001 | Bedarf nach Tiergruppe/Leistung/Stadium (GfE 2023) | MUSS | `constants/gfe2023.py`, Wizard-Requirements | VERIFIED | — | vorhanden | `test_rations_wizard_requirements.py`, `test_process_kernel_wave74_rations_optimization.py` | Fodjan-/DLG-Abgleich 2026-07 (Memory: Formeln korrekt) |
| FEED-REQ-002 | Normsystem-Versionierung als Daten (EvaluationSystemVersion) | MUSS | Konstanten versioniert im Code (gfe2023/dlg2025-Module) | PARTIAL | Auswahl/Versionierung als Entität | Inkrement 1 | Golden-Tests | — |
| FEED-REQ-003 | Hitzestress/Weide/Übergangsphasen | SOLL | Weide-/Saisonprofile im Solver | PARTIAL | Hitzestress fehlt | Release C | `test_rations_optimization_{pasture,seasonal_profiles,spring_pasture_case}.py` | — |
| FEED-REQ-004 | Trockensteher-Bedarf | MUSS | DLG-2025-Konstanten | VERIFIED | — | vorhanden | `test_rations_dcab_dlg2025.py` | DLG 01/2025 |

## Kapitel 6.6 — Rationserstellung

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-RAT-001 | Zeilen-CRUD, FM/TM, Fixierung, Min/Max in der Ration | MUSS | Workbench (UIX-P0-PORTAL-RATIONS-006): add/remove/fix=Min=Max | VERIFIED | — | vorhanden | Vitest `rationsoptimierung-workbench.test.ts`, Playwright Rations-Smoke | Slice 006 |
| FEED-RAT-002 | Versionierung, Status, Gültigkeit, unveränderliche Freigabe | MUSS | `lifecycle/domain.py`, `ration_versions` (snapshot_checksum) | VERIFIED | Gültig-bis fehlt (nur feeding_start + Ein-Aktiv) | Feld in Inkrement 3 | `test_rations_lifecycle_{domain,api}.py` | Slice 007 |
| FEED-RAT-003 | Kopieren/Vorlagen | MUSS | `based_on_version_id` bei Versionen | PARTIAL | Vorlagenkatalog fehlt | Inkrement 2 | `test_rations_lifecycle_api.py` | — |
| FEED-RAT-004 | Undo/Redo, Mischreihenfolge-Sortierung, Tastatur | MUSS | Mischreihenfolge im Solver (`solver/mixing.py`), UI-Sortierung fehlt | PARTIAL | Editor-Bedienkomfort | **Inkrement 2 (Rationseditor)** | `test_rations_solver_mixing.py` | Paritätsmatrix |
| FEED-RAT-005 | Kosten je Tier/Tag, ct/kg ECM, Versionsdiff | MUSS | Praxis-KPIs (ct/kg ECM, KF-TM/kg ECM, €/Kuh/Tag) | VERIFIED | Versionsdiff-Ansicht offen | Inkrement 2 | Vitest Workbench | Slice 006 |

## Kapitel 6.7 — Optimierung

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-OPT-001 | Kostenminimum + harte Nebenbedingungen | MUSS | LP-Solver `solver/lp_constraints.py` | VERIFIED | — | vorhanden | `test_rations_lp_constraints.py` + DLG-Golden-Tests | — |
| FEED-OPT-002 | Mehrstufige Ziele (Kosten/IOFC/Leistung/Gesundheit/Umwelt) | MUSS | `lp_stage2.py`, lexikografisch Milch, Zielstrategie-Kalibrierung | VERIFIED | — | vorhanden | `test_rations_{milk_lexicographic,objective_strategy_calibration}.py` | — |
| FEED-OPT-003 | Weiche Nebenbedingungen/Penalties, SARA-Reopt, peNDF-Demotion | MUSS | FAN-Modus 005 Penalties, SARA-Reopt | VERIFIED | — | vorhanden | `test_rations_optimization_{fan_mode_005_penalties,sara_reopt,pendf_demotion}.py` | — |
| FEED-OPT-004 | Unlösbarkeit erklären, Konfliktgrenzen benennen | MUSS | Erklärschicht `response/aggregator.py` | PARTIAL | IIS-artige Konfliktbenennung ausbaufähig | Inkrement 2 | `test_rations_aggregator.py` | — |
| FEED-OPT-005 | Ergebnis reproduzierbar speichern (OptimizationRun) | MUSS | Snapshot in `ration_versions.snapshot` + checksum | PARTIAL | eigenes Run-Aggregat mit Solverparametern | Inkrement 1 | `test_rations_lifecycle_api.py` | Slice 007 |
| FEED-OPT-006 | Pareto-Katalog, Sensitivität, Shadow Prices | SOLL | — | NOT_IMPLEMENTED | Paritätsmatrix „Nächster Ausbau" | Release C | — | — |
| FEED-OPT-007 | Keine ungefragte Aktivierung | MUSS | Solver übergibt nur Entwurfssnapshots (ADR-041) | VERIFIED | — | vorhanden | `test_rations_lifecycle_api.py` | Slice 007 |

## Kapitel 6.8 — Bewertung

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-EVAL-001 | Kennzahl+Ist+Ziel+Bedeutung+Empfehlung | MUSS | Diagnose/Warnungen + Erklärschicht; DLG-Kontrollregelkreis | PARTIAL | strukturierte RationEvaluation-Entität mit Ursache/Folge/Quelle je Kennzahl | Inkrement 1/2 | `test_rations_feeding_control_dlg2025.py` | DLG 01/2025 |
| FEED-EVAL-002 | Warnungs-Priorisierung, nicht nur Farbe | MUSS | Warnungsanpassung vorhanden; text-status-Utilities + Icons | PARTIAL | 4-stufige Priorität als Datenmodell | Inkrement 2 | axe-E2E 8/8 | Design-Audit 7a |
| FEED-EVAL-003 | Freigabe trotz Warnung nur mit Begründung | MUSS | Readiness-Blocker + `OVERRIDE:`-Begründung im Lifecycle-Audit | VERIFIED | — | vorhanden | `test_rations_readiness.py` | Slice 008 |

## Kapitel 6.9 — Variantenvergleich

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-CMP-001 | Zwei Rationen/Versionen vergleichen (Futtermittel/Nährstoff/Kosten-Diff) | MUSS | Intent-Vorschläge mit Delta (RATIONS-UX-INTENT-002); Versionsliste | PARTIAL | dedizierte Vergleichsansicht + Druck | Inkrement 2 | Vitest Workbench | — |
| FEED-CMP-002 | Szenarien (Preis/Analyse/Leistung) | SOLL | — | NOT_IMPLEMENTED | Paritätsmatrix Wirtschaftlichkeit | Release C | — | — |

## Kapitel 6.10 — Fütterungsplan

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-PLAN-001 | Freigegebene Ration als Planversion (Skalierung, Mischreihenfolge, PDF) | MUSS | aktive Serverversion + Mobil-Protokoll liest sie; Mischreihenfolge im Solver | PARTIAL | FeedingPlanVersion/MixingInstruction-Aggregat, PDF, Rundungsregeln | **Inkrement 3** | `test_rations_solver_mixing.py`, `feed-advice-entry.test.tsx` | Slice 007/011 |
| FEED-PLAN-002 | Mobile Ansicht + Offline-Fallback | MUSS | `fuetterungsdokumentation-mobil.tsx` (Browsercache-Fallback) | VERIFIED | Sync-Konflikte offen | Inkrement 3/6 | Playwright Lifecycle 1/1 | Slice 007 |
| FEED-PLAN-003 | Mischwagen-/Roboterexport, Rückmeldung | SOLL | agrirouter-Adapter (Feeding-Log-Import) | PARTIAL | Export-Richtung + Rückmeldeabgleich | Inkrement 6 | `test_rations_integrations_f5.py` | Slice 010 |

## Kapitel 6.11 — Soll-Ist-Controlling

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-ACT-001 | Istmengen erfassen (manuell/Schnittstelle), idempotent | MUSS | `rations_controlling.py` observations + Quellen manual/mixing_wagon/herd_data/import | VERIFIED | — | vorhanden | `test_rations_controlling.py` | Slice 009 |
| FEED-ACT-002 | Abweichung absolut/%, Nährstoff-/Kostenfolge, Verlauf | MUSS | deviations + Trends (5 Soll-Ist-Charts) | VERIFIED | Nährstofffolge je Komponente offen | Inkrement 4 | `feed-controlling-trends.test.tsx` (4) | Slice 012 |
| FEED-ACT-003 | Mischgenauigkeit, Restfutter, Lade-/Mischzeiten | SOLL | `control/feeding_control.py` (<5%-Regelkreis) | VERIFIED | UI-Verlauf offen | Inkrement 4 | `test_rations_{feeding_control_dlg2025,mixing_protocol}.py` | DLG 01/2025 |
| FEED-ACT-004 | Aufgaben aus Abweichungen, Ursachenklassifikation | MUSS | — | NOT_IMPLEMENTED | Measure/Task-Aggregat | **Inkrement 4/5** | — | Paritätsmatrix Tiergesundheit |

## Kapitel 6.12 — Leistungscontrolling

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-PERF-001 | Milch/ECM, Futterkosten, Effizienz, N-Effizienz, Methan je Gruppe | MUSS | `controlling.py` + Tagesreihe + Trends | VERIFIED | — | vorhanden | `test_rations_controlling.py`, `test_rations_efficiency_dlg2025.py` | Slices 009/012 |
| FEED-PERF-002 | IOFC | MUSS (sofern Daten) | Milchpreis in feeding_control (IOFC-Basis) | PARTIAL | IOFC in Tagesreihe/Trends | Inkrement 4 | `test_rations_feeding_control_dlg2025.py` | — |
| FEED-PERF-003 | Verlauf vor/nach Rationswechsel (Version im Zeitverlauf) | MUSS | ration_version_id an jedem Tagespunkt | PARTIAL | Versionsmarker in Trend-UI | Inkrement 4 | Slice 009 | — |
| FEED-PERF-004 | MLP/Milchgüte/AMS-Kennzahlen (Harnstoff, FEQ, Zellzahl) | SOLL | ICAR-ADE-Adapter (Kuhprofil) | PARTIAL | Kennzahlenpfad in Controlling | Inkrement 6 | `test_rations_integrations_f5.py` | Slice 010 |
| FEED-PERF-005 | Benchmarking Gruppen/Betriebe | SOLL | Gruppen-Benchmark (kuhzahl-gewichtet) | PARTIAL | Betriebsvergleich anonymisiert offen | Release C | `feed-controlling-trends.test.tsx` | Slice 012 |

## Kapitel 6.13 — Beratung/Maßnahmen

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-CONS-001 | Beratungsfall (Besuch, Beobachtung, Foto, Bewertung, Bericht) | MUSS | Reviewgründe/Kommentare im Lifecycle | PARTIAL | ConsultingCase/Observation-Aggregat | **Inkrement 5** | `test_rations_lifecycle_api.py` | — |
| FEED-CONS-002 | Maßnahmen (Verantwortlicher, Fälligkeit, Status, Wirksamkeit) | MUSS | — | NOT_IMPLEMENTED | Measure-Aggregat | Inkrement 5 | — | Paritätsmatrix |
| FEED-CONS-003 | Workflow-/CRM-Aufgabenintegration | SOLL | flow_spines/CRM-Aktivitäten existieren systemweit | PARTIAL | Verknüpfung | Inkrement 5/6 | — | — |

## Kapitel 6.14 — Bedarf/Bestand/Einkauf

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-SUP-001 | Reichweite/Unterdeckung aus aktiven Rationen | MUSS | Readiness: Bestand + deterministische Reichweite | VERIFIED | Sicherheitszuschlag/Handelseinheit offen | Inkrement 3 | `test_rations_readiness.py` | Slice 008 |
| FEED-SUP-002 | Chargen-FIFO, Reservierungen | SOLL | — | NOT_IMPLEMENTED | Paritätsmatrix Futterbestand | Inkrement 6 | — | — |
| FEED-SUP-003 | Bestellvorschlag/Übergabe Einkauf | SOLL | Bestellvorschlags-Framework (`einkauf/bestellvorschlag-*`), `futtermittel-bestellung.tsx` | PARTIAL | Kopplung an Rationsbedarf | Inkrement 6 | — | — |

## Kapitel 6.15 — Berichte

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-REP-001 | Rations-PDF mit Version/Freigabe | MUSS | PDF-/Review-Pfad vorhanden (Paritätsmatrix Ausgabe) | PARTIAL | profilierte Landwirt/Berater/Fütterer-Ausgaben | Inkrement 3 | — | UIX-011 |
| FEED-REP-002 | Beratungsbericht, Soll-Ist-, Verlaufsbericht | MUSS | — | NOT_IMPLEMENTED | Report-Aggregat | Inkrement 5 | — | — |
| FEED-REP-003 | CSV/Excel-Export | MUSS | Serien-API liefert strukturierte Daten | PARTIAL | Export-Buttons | Inkrement 4 | — | — |

## Kapitel 6.16 — Zusammenarbeit/Freigaben

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-COLLAB-001 | Statusworkflow + Freigabehistorie + Unveränderlichkeit | MUSS | Lifecycle-Statusautomat + Audit + Checksum | VERIFIED | — | vorhanden | `test_rations_lifecycle_domain.py` | Slice 007 |
| FEED-COLLAB-002 | Kommentare, Änderungsanforderung, Benachrichtigung | MUSS | Reviewgründe persistent; Benachrichtigungskanäle offen | PARTIAL | Notification-Anbindung | Inkrement 5 | Slice 007 | Paritätsmatrix |
| FEED-COLLAB-003 | Vier-Augen-Prinzip konfigurierbar | SOLL | APPROVE-Rollen getrennt von WRITE | PARTIAL | erzwungene Fremd-Prüfung | Release B | `test_rations_authz.py` | Slice 013 |

## Kapitel 6.17/6.18 — UI/Mobil

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-UI-001 | Mask-Builder-Muster, Design-Tokens, WCAG 2.2 AA | MUSS | native SDs, Token-System, axe 8/8, Chart-Palette validiert | VERIFIED | — | laufend | axe-E2E, Vitest | Design-Audit (alle 8 Punkte) |
| FEED-UI-002 | Betriebsakte/Fütterungsübersicht/Rationseditor-Seiten | MUSS | Cockpit `agrar/feed-advice` + Aufgabenkacheln | PARTIAL | Kernseiten 1/3/7/8/13/14 des Kap. 10 | Inkremente 1–5 | `feed-advice-entry.test.tsx` | ADR-041 |
| FEED-MOB-001 | Mobile MUSS-Fälle (Plan, Istmengen, Beobachtung, Foto) | MUSS | Mobil-Protokoll (Plan+Istmengen) | PARTIAL | Beobachtung/Foto/Maßnahme | Inkrement 5 | Playwright | Slice 007 |

## Kapitel 6.19 — Schnittstellen

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-INT-001 | Idempotente Importe, Dubletten, Audit | MUSS | payload_hash + ON CONFLICT (Imports, Observations, Logs) | VERIFIED | Vorschau/Validierungsbericht | Inkrement 6 | `test_rations_integrations_f5.py`, `test_rations_herd_data_connectors.py` | Slices 010 |
| FEED-INT-002 | Connector-Gates (Consent/Contract/Secret/Egress) | MUSS | HerdDataSyncService-Gates, Admin-Level | VERIFIED | Mapping-UI/Quarantäne je Betrieb | Inkrement 6 | `test_rations_herd_data_connectors.py` (10) | Slice 010 |
| FEED-INT-003 | Reale DDW-/MLP-/Mischwagen-Livepfade | MUSS | Templates konfigurierbar, bewusst offen | BLOCKED | lizenzierter Partnervertrag erforderlich | extern | — | Paritätsmatrix |
| FEED-INT-004 | Event-Bus/Webhooks | SOLL | NATS-Outbox systemweit | PARTIAL | Feeding-Events | Inkrement 6 | — | — |

## Kapitel 6.20 — KI

| ID | Anforderung | Prio | IST | Status | Gap | Umsetzung | Test | Nachweis |
|---|---|---|---|---|---|---|---|---|
| FEED-AI-001 | KI nur unterstützend, keine stille Freigabe, keine erfundenen Werte | MUSS | Copilot-/Intent-Vorschläge mit Delta-Anzeige; Freigabe nur via Lifecycle | VERIFIED | — | Leitplanke bleibt | `test_rations_lifecycle_api.py` | ADR-041 |
| FEED-AI-002 | Erklärungen/Ursachen/Maßnahmenvorschläge | SOLL | Erklärschicht + Diagnose | PARTIAL | Maßnahmen-Ableitung nach Inkrement 5 | Release C | `test_rations_aggregator.py` | — |

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
