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

## Release C — Controllingfähig (Slice-Specs, verbindlich ab FEED-ACT-030)

> **Stand 2026-07-16:** Slices bis einschließlich FEED-ACT-030 sind umgesetzt
> bzw. in Arbeit (Owner Codex). Die folgenden Specs definieren die vollständige
> Restumsetzung. Für jedes Slice gelten unverändert: TDD-Pflicht
> (Red→Green→Refactor mit Evidenz im YAML), Meridian-Runtime-Kette für neue
> Masken, Traceability-Update (VERIFIED nur mit Code+Testnachweis), additive
> Migrationen, `require_roles`/Grants serverseitig, Definition of Done aus
> Lastenheft Kap. 15.

### Inkrement 5 — Leistung und Beratung

#### FEED-CONS-031 — Beratungsfall und Beobachtungen

- **Requirements:** FEED-CONS-001, FEED-MOB-001-Rest. **Pakete:** 17-beratung (WP-171ff). **Abhängig von:** 030 (Measure-Kern).
- **Scope:** Aggregate `ConsultingCase` (Besuch/Remote, Betrieb-/Gruppenbezug, Ausgangssituation, Status offen→abgeschlossen) und `Observation` (strukturierte Kategorien + Freitext, DMS-Fotoreferenzen, Verknüpfung zu Ration/Analyse/Tagesreihe); Beratungs-Worklist (native SD) + ObjectPage; mobiler Erfassungspfad (Beobachtung + Foto) auf bestehender Mobilroute.
- **Akzeptanz:** Fall bündelt Beobachtungen/Verknüpfungen chronologisch; mobile Erfassung landet idempotent am Fall; RBAC advise/READ; Fotos nur als DMS-Referenz (kein Upload-Bypass).
- **TDD-Kern:** Red = Fall-Lifecycle-/Verknüpfungs-Contract, mobiler Idempotenz-Test, 403-Matrix.

#### FEED-CONS-032 — Maßnahmen-Vollausbau, Benachrichtigung, Beratungsbericht-Kern

- **Requirements:** FEED-CONS-002, FEED-COLLAB-002, FEED-REP-002-Kern. **Abhängig von:** 030/031.
- **Scope:** `Measure` vervollständigen (Verantwortlicher, Fälligkeit, Wiedervorlage, Wirksamkeitskontrolle mit Ergebnisfeld, Eskalationsstatus); Benachrichtigungs-Port über NATS-Outbox (`feeding.measure.created/overdue/completed`) mit In-App-Konsument; Beratungsbericht als strukturierter Entwurf aus Fall+Befunden+Maßnahmen (Persistenz als Report-Entwurf, PDF folgt FEED-REP-039/040).
- **Akzeptanz:** Überfällige Maßnahmen erzeugen genau-einmal ein Ereignis; Wirksamkeitskontrolle erzwingt Ergebnis vor Abschluss; Berichtentwurf reproduzierbar aus Falldaten.

#### FEED-PERF-033 — Leistungskennzahlen-Vollausbau

- **Requirements:** FEED-PERF-002/003/004. **Abhängig von:** 029/030.
- **Scope:** `PerformanceRecord` um MLP/Milchgüte-Kennzahlen (Harnstoff, Fett-Eiweiß-Quotient, Zellzahl) über den ICAR-Adapter erweitern (Provenienz je Wert); IOFC vollständig in Tagesreihe+Trends (Milchpreis-Quelle dokumentiert); Rationsversions-Marker in den Trend-Charts (Wechsel sichtbar); Vorher/Nachher-Auswertung je Rationswechsel mit ehrlicher Unsicherheitsangabe (n, Zeitraum — keine Scheinsignifikanz).
- **Akzeptanz:** Kennzahlen erscheinen nur mit Herkunft; Versionsmarker exakt am Aktivierungsdatum; IOFC nie aus geschätzten Preisen ohne Kennzeichnung.

### Inkrement 6 — Integrationen

#### FEED-INT-034 — Integrationsmonitor: Vorschau, Validierung, Quarantäne, Mapping

- **Requirements:** FEED-INT-001-Rest, FEED-LAB-002-Rest. **Maske:** FEED-MASK-014.
- **Scope:** ImportJob-Status (empfangen→validiert→quarantäne→übernommen/verworfen) für Labor-/agrirouter-/Herd-Data-Importe; Vorschau + Validierungsbericht vor Übernahme; interaktive Mapping-Oberfläche (Labor-Material→Feed, offene Zuordnungen als Worklist); Quarantäne-Begründung pflichtig.
- **Akzeptanz:** Kein Import wird ohne bestandene Validierung fachlich wirksam; Wiederholung ohne Dubletten (payload_hash bleibt Vertrag); Mapping-Entscheidungen auditiert.

#### FEED-INT-035 — Mischtechnik bidirektional + Bestandsbindung

- **Requirements:** FEED-PLAN-003, FEED-SUP-002. **Abhängig von:** 026/027 (Planversion), 034 (Monitor).
- **Scope:** Planexport an Mischwagen/Roboter (agrirouter-Format, je Planversion, QR-/Referenzcode); Rückmeldeabgleich lädt Ist-Mengen idempotent auf die Planversion (Sync-Konflikte sichtbar, nie stilles Überschreiben); Chargen-FIFO und reservierte Mischmengen gegen den Lagerbestand (Reservierung bei Planveröffentlichung, Verbrauch bei Rückmeldung).
- **Akzeptanz:** Export↔Rückmeldung über stabile Referenz; Konfliktfälle (Plan veraltet, Menge doppelt) enden im Monitor statt in Datenverlust; Reichweite berücksichtigt Reservierungen.

#### FEED-INT-036 — Feeding-Events und Konsumenten

- **Requirements:** FEED-INT-004, FEED-COLLAB-002-Rest. **Hinweis:** FEED-INT-003 (reale DDW-/MLP-Livepfade) bleibt **BLOCKED bis Partnervertrag** — keine erfundenen Providerpfade.
- **Scope:** Outbox-Events schemafest (`feeding.analysis.verified`, `feeding.ration.version.activated`, `feeding.plan.published`, `feeding.actuals.recorded`, `feeding.deviation.exceeded`, `feeding.measure.*`, `feeding.import.quarantined`) mit Replay-/Genau-einmal-Vertrag; Konsumenten: Aufgaben/Benachrichtigung (032), Einkaufs-Reichweitenwarnung (028), Berichtsauslöser; optional Webhooks je Mandant (Admin-Level).
- **Akzeptanz:** Contract-/Replay-Tests je Event; Konsumentenwirkung idempotent.

### Inkrement 7 — Vervollständigung (neue Slices für die Lastenheft-Reste)

#### FEED-REP-039 — Berichtspaket 1: profilierte PDF-Ausgaben + Report-Entität

- **Requirements:** FEED-REP-001/003, FEED-CMP-001-Druckrest. **Maske:** FEED-MASK-013-Kern.
- **Scope:** `Report`-Entität (revisionssicher, DMS-Dokumentreferenz, Version/Freigabe/Empfängerprofil); profilierte Ausgaben Landwirt/Berater/Fütterer für Rationsübersicht, Fütterungsplan, Variantenvergleich; CSV-Export strukturierter Daten vereinheitlicht (Serien, Positionen, Diffs); Logo/Betrieb/Einheiten/Versionsangaben pflichtig.
- **Akzeptanz:** Jeder Bericht referenziert exakt eine unveränderliche Quellversion; erneuter Druck derselben Version erzeugt denselben Inhalt.

#### FEED-REP-040 — Berichtspaket 2: Beratungs-, Soll-Ist- und Verlaufsberichte

- **Requirements:** FEED-REP-002. **Abhängig von:** 031/032/033/039.
- **Scope:** Beratungsbericht (aus Fall+Maßnahmen), Soll-Ist-Auswertung und Verlaufsbericht als Berichtstypen der Report-Entität; Berichte-Maske (Liste, Erzeugen, Zustellprofil); optionale Portalbereitstellung.

#### FEED-EDITOR-041 — Editor-Komfortstufe

- **Requirements:** FEED-RAT-004-Rest. **Pakete:** WP-073/075/078-Kern.
- **Scope:** Undo/Redo für ungespeicherte Änderungen; vollständige Tastatur-Journey (Zeilenwechsel, Hinzufügen, Sortieren); Mischreihenfolge-Sortierung in der UI (persistiert im Snapshot); progressive Expertenspalten (Mineralstoffe) in kontrollierter Detailansicht.
- **Akzeptanz:** Tastatur-only-Durchlauf im Component-Test; Undo stellt exakt den vorherigen Draft her; Reihenfolge wird Teil der Version.

#### FEED-OPT-042 — Optimieren im Editor + Requirements-Modularisierung

- **Requirements:** FEED-OPT-004-Rest, FEED-OPT-005-Hook; baut Schulden aus 020/021 ab.
- **Scope:** `_gfe_requirements` aus dem Endpoint-Monolithen in `app/agrar/rations/requirements.py` extrahieren (Golden-Test-Äquivalenz beweist Drift-Freiheit); Optimieren-Aktion im Editor erzeugt Candidate-Version (nie Aktivierung) **mit automatischem OptimizationRun-Hook** (Parameter/Status atomar zur Version); Unlösbarkeit nutzt die bestehende Solver-Erklärschicht und zeigt Konfliktgrenzen im Editor-Kontext (Verknüpfung zu Grenzbefunden aus 024).
- **Akzeptanz:** Kein Optimierungsergebnis ohne persistierten Run; Monolith-Import aus Services entfällt.

#### FEED-HERD-043 — Gruppenhistorie aus Herd-Deltas

- **Requirements:** FEED-HERD-003 + Veraltet-Warnung (6.2 SOLL).
- **Scope:** `AnimalGroupSnapshot`-Verdichtung aus `herd_data_observations` (täglich, idempotent); Gruppen-ObjectPage zeigt Parameterhistorie; Warnung bei veralteten Gruppenparametern (Alter der letzten Bestätigung) in Editor/Bedarf.

#### FEED-PERF-044 — Benchmarking-Ausbau

- **Requirements:** FEED-PERF-005. **Achtung:** betriebsübergreifend anonymisiert erfordert eine **Auftraggeber-/Datenschutzentscheidung (Opt-in-Modell)** — bis dahin nur Konzeptteil, Umsetzung des Betriebsvergleichs BLOCKED.
- **Scope (frei):** Gruppen-Benchmark vertiefen (Zeitraumvergleich, Kennzahlprofile); Benchmark-Export in Berichte. **Scope (blocked):** anonymisierter Betriebsvergleich.

#### FEED-MOB-045 — Mobile Offline-Stufe

- **Requirements:** Kap. 6.18 SOLL (Offline, Sync-Queue, Konfliktauflösung).
- **Scope:** Offline-Warteschlange für Istmengen/Beobachtungen (idempotente Replays über bestehende Verträge), Konfliktanzeige (Plan veraltet), Kamera-Anbindung für Beobachtungsfotos; ausdrücklich KEIN zweiter Datenpfad — Queue nutzt dieselben APIs.

#### FEED-AI-046 — Assistenzfunktionen (Kap. 6.20/11)

- **Requirements:** FEED-AI-002; Leitplanken FEED-AI-001 bleiben unverändert MUSS.
- **Scope:** Erklär-Assistent für Befunde (Ursachenanalyse aus Bewertung+Historie), Maßnahmenvorschläge (bestätigungspflichtig, erzeugen Measure-Entwürfe), Ersatzfuttermittel-Vorschläge nach Bestand/Preis/Restriktionen; jede Ausgabe mit Datenquellen und Unsicherheit; keine stille Freigabe, keine erfundenen Werte (Kap. 16).
- **Abhängig von:** 032/033/035 (Datengrundlagen). Agentenverträge gemäß `11-agenten.md`.

#### FEED-RBAC-048 — Audit-Vereinheitlichung + Vier-Augen-Konfiguration

- **Requirements:** FEED-RBAC-005-Rest, FEED-COLLAB-003.
- **Scope:** fachlich lesbare AuditEvents für Stammdaten-Mutationen (Betriebe, Futter, Analysen, Grants) nach dem Lifecycle-Muster; mandantenkonfigurierbares Vier-Augen-Prinzip für Freigaben (Einreicher ≠ Freigeber erzwingbar).

### Inkrement 8 — Pilot und Rollout (FEED-REL-047)

- **Requirements:** FEED-NFR-007 → VERIFIED; Lastenheft Phase 6.
- **Scope:** Modul-Flag `feeding_advisory` über die Module-Registry (Portal-Kacheln + Router-Gate); Playwright-Release-Journeys A (Betrieb→Analyse→Bedarf→Ration→Bewertung→Freigabe→Bericht), B (Plan→mobil→Ist→Soll-Ist), C (Leistung→Beratung→Maßnahme→Bericht) gegen Docker-Prod; Vergleich Alt-/Neuberechnung am Referenzbetrieb (`rations_hof_ostfriesland`-Seed); Runbook + Rollback; **Abnahme durch fachkundigen Fütterungsberater vor Breitenaktivierung** (Auftraggeber-Gate).

### Reihenfolge und Abhängigkeiten (nach 030)

```text
031 ──▶ 032 ──▶ 040        034 ──▶ 035 ──▶ 036 ──▶ 046
029/030 ──▶ 033 ──▶ 044(frei)         039 ──▶ 040
021–025 ──▶ 041 ──▶ 042    010 ──▶ 043     045 (nach 031)
048 parallel ab 031 · 047 zuletzt (nach 036/040/042)
```

### Offen / extern gebunden (nicht planbar ohne Entscheidung)

1. **FEED-INT-003** DDW-/MLP-/Mischwagen-Livepfade: lizenzierter Partnervertrag.
2. **FEED-PERF-044 (Betriebsvergleich):** Datenschutz-/Opt-in-Entscheidung des Auftraggebers.
3. **IdP-Rollenzuweisung** FUTTERMITTEL_* betriebsindividuell (organisatorisch).
4. **Pilotabnahme** durch Fütterungsberater (Auftraggeber-Gate vor Rollout, Inkrement 8).

## Querschnitt (laufend je Slice)

Traceability-Pflege · RBAC-403-Regression je neuem Router · Golden-Tests je neuer
Kennzahl · axe auf neuen Kernrouten · Playwright-Journey je Release · Paritätsmatrix-
Update · keine Lösungen aus Lastenheft Kap. 16 (u. a. keine Mocks in Produktivpfaden,
kein Float für Geld — neue Geld-Spalten Numeric/Decimal).

## Offene Auftraggeber-Punkte

1. **Fodjan-Traceability (Kap. 17): abgeschlossen 2026-07-15.** Oeffentliche
   Hilfe-Hubs, Themen und erreichbare Detailseiten sind in
   `fodjan-help-traceability.md` auf FEED-IDs und Slices gemappt; Texte, Screens
   und Produktdesign wurden nicht uebernommen.
2. **Feature-Branch-Vorgabe (Phase 0.6)** kollidiert mit der etablierten
   Trunk-Praxis dieses Repos (Slices auf `main`, Parallel-Agenten, CI als
   Schiedsrichter). Empfehlung: Slices weiter auf `main` hinter Modul-Flag
   `feeding_advisory`; abweichende Entscheidung bitte explizit.
3. **Rollen im IdP:** FUTTERMITTEL_*-Rollen müssen betriebsindividuell zugewiesen
   werden (heute Dev-Token/admin) — organisatorisch.
