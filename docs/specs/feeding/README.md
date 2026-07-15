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
| 02 | Lastenheft | ✅ | `lastenheft-fuetterungsberatung.md` |
| 03 | Fachkonzept | ✅ Kern | `ist-audit.md` + `target-architecture.md` |
| 04 | Domänenmodell | ✅ Referenzkapitel | `04-domaenenmodell.md` (Context Map, Aggregate, VOs, Events, UML, Event Storming) |
| 05 | Datenmodell | ✅ Referenzkapitel | `05-datenmodell.md` (Tabellen, Relationen, Tenant, Historisierung, Audit, Indizes) |
| 06 | API | ✅ Referenzkapitel | `06-api.md` (Bestand/Zielbild, Schemas, Fehler, OpenAPI- und Contract-Governance) |
| 07 | Maskenkatalog | ✅ Referenzkapitel | `07-maskenkatalog.md` (22 Masken, Rollen, Felder, Zustände, Aktionen, Mockups, Meridian-Vertrag) |
| 08 | Workflows | ✅ Referenzkapitel | `08-workflows.md` (15 E2E-Workflows, States, Guards, Kompensation, Audit, Tests) |
| 09 | Berechnungsregeln | ✅ im Code+Tests | `app/agrar/rations/constants/` + Golden-Tests (Single Source: Code, nicht Doku-Kopie) |
| 10 | UI/UX | ✅ | `docs/design/frontend-design-skill-audit.md` + ADR-041 |
| 11 | Agenten | 🔜 Release C | Leitplanken: Lastenheft Kap. 6.20 (verbindlich) |
| 12 | Integrationen | ✅ Kern | `target-architecture.md` §3–4; Connector-Verträge Slice 010 |
| 13 | Tests | ✅ Strategie | `target-architecture.md` §8; Bestand `ist-audit.md` §3 |
| 14 | Migration | ✅ Konzept | `target-architecture.md` §6 |
| 15 | Rollout | ✅ Konzept | `implementation-plan.md` (Flag `feeding_advisory`, Pilot) |
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
