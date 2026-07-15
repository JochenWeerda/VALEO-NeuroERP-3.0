---
title: "Spezifikation Fütterungsberatung — Index"
type: reference
audience: [produkt, fachlich, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Single Source of Truth für das Fütterungsberatungs-Programm — Dokumentlandkarte mit Füllstand.
---

# Spezifikation Fütterungsberatung — Index

Zielstruktur folgt dem Fachkonzept-Auftrag (00–17). Mit Auftraggeberentscheidung
vom 15.07.2026 wird sie zu einem vollstaendigen Architektur-Referenzwerk mit
300–500 Seiten Zielumfang und 200–300 vertikalen Arbeitspaketen ausgebaut. Der
verbindliche Pflege- und Driftvertrag steht in `reference-maintenance.md`.

| Nr. | Dokument | Status | Heutiger Ort |
|---|---|---|---|
| 00 | Vision | ✅ Referenzkapitel | `00-vision.md` |
| 01 | Glossar | ✅ Referenzkapitel | `01-glossar.md` |
| 02 | Lastenheft | ✅ Referenzkapitel | `02-lastenheft.md` (normativer Index) + `lastenheft-fuetterungsberatung.md` (Vollquelle) |
| 03 | Fachkonzept | ✅ Referenzkapitel | `03-fachkonzept.md` (Gesamtprozess) + `ist-audit.md` + `target-architecture.md` |
| 04 | Domänenmodell | ✅ Referenzkapitel | `04-domaenenmodell.md` (Context Map, Aggregate, VOs, Events, UML, Event Storming) |
| 05 | Datenmodell | ✅ Referenzkapitel | `05-datenmodell.md` (Tabellen, Relationen, Tenant, Historisierung, Audit, Indizes) |
| 06 | API | ✅ Referenzkapitel | `06-api.md` (Bestand/Zielbild, Schemas, Fehler, OpenAPI- und Contract-Governance) |
| 07 | Maskenkatalog | ✅ Referenzkapitel | `07-maskenkatalog.md` (22 Masken, Rollen, Felder, Zustände, Aktionen, Mockups, Meridian-Vertrag) |
| 08 | Workflows | ✅ Referenzkapitel | `08-workflows.md` (15 E2E-Workflows, States, Guards, Kompensation, Audit, Tests) |
| 09 | Berechnungsregeln | ✅ Referenzkapitel | `09-berechnungsregeln.md` (GfE/DLG/NRC-Status, Grenzen, Prioritäten, Plausibilität, Tests; Formeln bleiben Code-SSOT) |
| 10 | UI/UX | ✅ Referenzkapitel | `10-ui-ux.md` (Aufgabenmodi, Editor, Warnungen, Provenienz, Responsive, Research, Metriken) |
| 11 | Agenten | ✅ Referenzkapitel | `11-agenten.md` (6 Fachagenten, Tools, Human Gates, Security, Audit, Evals) |
| 12 | Integrationen | ✅ Referenzkapitel | `12-integrationen.md` (Labor, Herd-Data/DDW-Klasse, ICAR, agrirouter, Mixer, ERP, Security, Resilienz) |
| 13 | Tests | ✅ Referenzkapitel | `13-tests.md` (200 stabile Abnahmetests plus Golden, Property, Playwright, A11y, Performance, Security) |
| 14 | Migration | ✅ Referenzkapitel | `14-migration.md` (Ist→Soll, Daten/API/Regeln/UI, Schulden, Rollback) |
| 15 | Rollout | ✅ Referenzkapitel | `15-rollout.md` (R0–R4, Gates, Flags, SLO, Cutover, Hypercare) |
| 16 | Traceability | ✅ | `requirements-traceability.md` |
| 17 | Roadmap | ✅ | `implementation-plan.md` (Inkremente 1–6, Slices 015–036) |
| — | Fodjan-Abgleich | ✅ | `fodjan-help-traceability.md` (Funktions-Traceability, Stand 2026-07-15) |
| — | Pflegevertrag | ✅ | `reference-maintenance.md` |

## Entscheidung zum Umfang (historisch, am 2026-07-15 aufgehoben)

Die Foundation-Empfehlung war zunaechst eine wachsende Struktur statt eines
vollstaendigen Vorabwerks. Der Auftraggeber hat diese Empfehlung am 15.07.2026
explizit aufgehoben. Die damaligen Risiken bleiben als Pflegeanforderungen erhalten:

1. **Doku-Drift ist das Hauptrisiko** dieses Repos (eigene Gates: docs-code-sync,
   Drift-Check). Ein vorab vollständig ausgeschriebener Masken-/Test-/Datenkatalog
   über 6 Inkremente veraltet vor seiner Umsetzung und verletzt dann die eigenen
   Governance-Regeln.
2. **Berechnungsregeln haben bereits eine Single Source:** den getesteten Code
   (~30 Golden-Test-Dateien gegen GfE 2023/DLG 01/2025). Eine Prosa-Kopie im
   Regelwerk-Dokument würde eine zweite, driftende Wahrheit schaffen.
3. **Verbindlichkeit entsteht hier über Slices:** jedes Inkrement liefert seinen
   Spezifikationsteil (Masken, Tabellen, Tests) mit dem Claim — die Struktur oben
   füllt sich, IDs und Kapitel bleiben stabil.

Das Referenzwerk wird deshalb nicht als freie Prosa gepflegt: normative Aussagen
tragen stabile IDs und eine Code-/OpenAPI-/Migrationsquelle; Formeln verweisen auf
versionierten Code und Golden-Tests; Kapitel besitzen Stand, Owner und Driftstatus.
Details und Konfliktregeln: `reference-maintenance.md`.
