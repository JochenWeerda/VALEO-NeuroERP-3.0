---
title: "Fütterungsberatung — Umsetzungsplan (Phase 4)"
type: reference
audience: [entwickler, produkt, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Vertikale, abnahmefähige Inkremente mit Slice-Zuschnitt, Abhängigkeiten und Definition of Done je Paket.
---

# Umsetzungsplan Fütterungsberatung

Vorgehen: jedes Arbeitspaket ist ein eigener Workboard-Slice (Claim → YAML → Code →
Abschluss), vertikal abnahmefähig, mit Traceability-Update (Status → VERIFIED nur mit
Code- **und** Testnachweis). Feature-Gate: Modul-Flag `feeding_advisory` über die
Module-Registry, Pilotmandant vor Breitenaktivierung (Lastenheft Phase 6).

## Release A — Beratungsfähig

### Inkrement 1 — Fachlicher Kern (Aggregate)

| Slice | Inhalt | Requirements | Abhängig von |
|---|---|---|---|
| FEED-CORE-015 | FeedingBusiness/FarmSite/Herd + CRM-Brücke (`business_partner_id`), Grants-Tabelle + `require_business_access`, Backfill Default-Betrieb, Betriebsliste (ListReport) | FEED-BUS-001/002, FEED-RBAC-003 | — |
| FEED-CORE-016 | AnimalGroup-Ausbau (Trächtigkeit, Milchinhaltsstoffe, Risiko, Gültigkeit, typisierte Gruppenprofile Frischmelker…Jungvieh), Gruppen-ObjectPage | FEED-HERD-001/002 | 015 |
| FEED-CORE-017 | NutrientDefinition/UnitDefinition als Daten + zentrale Einheiten-/Rundungsregeln + Property-Tests FM/TM | FEED-MAT-003, FEED-LAB-003, FEED-NFR (7.1) | — |
| FEED-CORE-018 | Feed/FeedProduct/FeedReferenceValue-Persistenz + Adapter → Solver-Dataclass (Golden-Test-Äquivalenz), Futtermittel-ObjectPage-Anbindung | FEED-MAT-001/002 | 017 |
| FEED-CORE-019 | FeedAnalysis/FeedAnalysisValue-Aggregat: Erfassung, DMS-Anhang, aktive Analyse, Historie, Plausibilitätswarnungen; Analyse-Wizard + Import-Vorschau | FEED-LAB-001/002/004 | 017/018 |
| FEED-CORE-020 | EvaluationSystem(Version)/RequirementProfile als Daten + OptimizationRun-Tabelle (solver_version, Parameter, Status) | FEED-REQ-002, FEED-OPT-005 | — |

**DoD Inkrement 1:** Betriebsakte-Datenpfad steht (Betrieb→Herde→Gruppe→Futter→Analyse),
alle neuen Router mit RBAC-403-Regression, Migrationen additiv + Single-Head,
Traceability-Zeilen der 6 Slices auf VERIFIED.

### Inkrement 2 — Produktiver Rationseditor

| Slice | Inhalt | Requirements |
|---|---|---|
| FEED-EDITOR-021 | Rationseditor-Seite (Kopf/Positionsfläche/Bewertungsleiste, Register-Tabs, Undo/Redo, Tastatur, Mischreihenfolge-Sortierung) auf bestehender Workbench-Logik | FEED-RAT-004, FEED-UI-002 |
| FEED-EDITOR-022 | Strukturierte RationEvaluation/Warning-Persistenz + 4-stufige Priorität + Warnung→Ursache-Navigation | FEED-EVAL-001/002 |
| FEED-EDITOR-023 | Variantenvergleich (2 Versionen: Futtermittel-/Nährstoff-/Kosten-Diff, Druckansicht, Kommentar je Variante) | FEED-CMP-001, FEED-RAT-005 |
| FEED-EDITOR-024 | Unlösbarkeits-Erklärung ausbauen (Konfliktgrenzen benennen, Lösungsvorschläge) | FEED-OPT-004 |
| FEED-EDITOR-025 | Vorlagen/Kopieren + Betriebsakte-ObjectPage (bündelt Tabs) + Fütterungsübersicht | FEED-RAT-003, FEED-BUS-003 |

**Meilenstein Release A:** Pilotabnahme durch Fütterungsberater am Referenzbetrieb
(Seed `rations_hof_ostfriesland`), PDF-Bericht aus Editor.

## Release B — Betriebsfähig

### Inkrement 3 — Fütterungsplan

| Slice | Inhalt | Requirements |
|---|---|---|
| FEED-PLAN-026 | FeedingPlanVersion/MixingInstruction-Aggregat (unveränderlich, Skalierung Tierzahl, Rundungs-/Dosierregeln, Gültig-bis) + `feeding.plan.published`-Event | FEED-PLAN-001, FEED-RAT-002-Rest |
| FEED-PLAN-027 | Plan-UI: ObjectPage, Druck/PDF, Mobilroute (bestehendes Protokoll auf Planversion umstellen), Veraltet-Kennzeichnung | FEED-PLAN-001/002, FEED-REP-001 |
| FEED-SUP-028 | Bedarf/Reichweite je Plan (Sicherheitszuschlag, Handelseinheit), Reichweitenwarnung → Einkaufs-Übergabe | FEED-SUP-001/003 |

### Inkrement 4 — Soll-Ist-Vollausbau

| Slice | Inhalt | Requirements |
|---|---|---|
| FEED-ACT-029 | Ist-Erfassung gegen Planversion (je Komponente), Nährstoff-/Kostenfolge, Ursachenklassifikation, CSV-Export | FEED-ACT-002-Rest, FEED-REP-003 |
| FEED-ACT-030 | Warnschwellen + Aufgaben aus Abweichungen (Measure-Aggregat minimal), IOFC + Versionsmarker in Trends | FEED-ACT-004, FEED-PERF-002/003 |

## Release C — Controllingfähig

### Inkrement 5 — Leistung und Beratung

| Slice | Inhalt | Requirements |
|---|---|---|
| FEED-CONS-031 | ConsultingCase/Observation (Besuch, Foto via DMS, Bewertung) + Worklist + mobiler Erfassungspfad | FEED-CONS-001, FEED-MOB-001-Rest |
| FEED-CONS-032 | Maßnahmen-Vollausbau (Verantwortlicher, Fälligkeit, Wirksamkeit, Wiedervorlage) + Benachrichtigung + Beratungsbericht | FEED-CONS-002, FEED-COLLAB-002, FEED-REP-002 |
| FEED-PERF-033 | MLP/Milchgüte-Kennzahlen (Harnstoff, FEQ, Zellzahl) in Tagesreihe/Trends; statistische Erfolgsauswertung | FEED-PERF-004 |

### Inkrement 6 — Integrationen

| Slice | Inhalt | Requirements |
|---|---|---|
| FEED-INT-034 | Import-Vorschau/Validierungsbericht/Quarantäne-UI + Mapping-Oberfläche (Integrationsmonitor) | FEED-INT-001-Rest, FEED-LAB-002-Rest |
| FEED-INT-035 | Mischwagen-Export + Rückmeldeabgleich (agrirouter bidirektional), Chargen-FIFO/Reservierung | FEED-PLAN-003, FEED-SUP-002 |
| FEED-INT-036 | Feeding-Events auf NATS + Aufgaben-/Einkaufs-Konsumenten; DDW-Livepfade **nach Partnervertrag** | FEED-INT-003 (BLOCKED)/004 |

## Querschnitt (laufend je Slice)

Traceability-Pflege · RBAC-403-Regression je neuem Router · Golden-Tests je neuer
Kennzahl · axe auf neuen Kernrouten · Playwright-Journey je Release · Paritätsmatrix-
Update · keine Lösungen aus Lastenheft Kap. 16 (u. a. keine Mocks in Produktivpfaden,
kein Float für Geld — neue Geld-Spalten Numeric/Decimal).

## Offene Auftraggeber-Punkte

1. **Fodjan-Traceability (Kap. 17):** Quelle war nicht abrufbar; Abgleich wird
   nachgeholt, sobald erreichbar → `fodjan-help-traceability.md`.
2. **Feature-Branch-Vorgabe (Phase 0.6)** kollidiert mit der etablierten
   Trunk-Praxis dieses Repos (Slices auf `main`, Parallel-Agenten, CI als
   Schiedsrichter). Empfehlung: Slices weiter auf `main` hinter Modul-Flag
   `feeding_advisory`; abweichende Entscheidung bitte explizit.
3. **Rollen im IdP:** FUTTERMITTEL_*-Rollen müssen betriebsindividuell zugewiesen
   werden (heute Dev-Token/admin) — organisatorisch.
