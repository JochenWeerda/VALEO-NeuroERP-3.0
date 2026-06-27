---
title: Dokumentations-Konsolidierung 2026-06-26
type: explanation
audience: [entwickler, docs]
owner: Claude Code
status: umgesetzt
last_reviewed: 2026-06-27
version: 3.0.0
description: Bericht zur Dokumentations-Konsolidierung vom 2026-06-26 — Ziele, abgeschlossene Schritte, Ergebnis und naechste Schritte fuer die Docs-Pflege.
---

# Documentation Consolidation 2026-06-26

## Ziel

Diese Konsolidierung trennt aktive Restarbeit von historischen Planungs-,
Benchmark- und Gap-Dokumenten. Viele aeltere Aussagen in `docs/project-context/`,
`docs/workflows/`, `docs/cards/` und `docs/quality-assurance/` beschreiben den
damaligen Befund, nicht den heutigen Lieferstand.

## Effiziente Vorgehensweise

Statt alle rund 670 aktiven Markdown-Dateien manuell zu lesen, wurden vier
maschinelle Filter kombiniert:

- `python scripts/doc_drift_report.py`: Code-zu-Doku-Drift.
- `rg` auf Begriffe wie `offen`, `geplant`, `folgt`, `Gap`, `TODO`.
- Source-of-Truth-Abgleich gegen `docs/architecture/process-kernel/STATUS.md`,
  `docs/agent-ops/active-workboard.md` und Slice-YAMLs.
- Stichproben in den hoechst riskanten Altbefunden:
  `domain-depth-plan`, Agrar-Gap-Matrizen, ERP-Referenzanalyse, Admin-Suite-
  Roadmap, Action-/Traceability-Matrix.

Ergebnis: Der harte Code-Drift ist geschlossen; das verbleibende Problem ist
Statussprache in alten Planungsdokumenten.

## Konsolidierter Befund

| Bereich | Ergebnis |
|---|---|
| Code-Inventar | `doc_drift_report.py` meldet 0 Endpoints, 0 Services, 0 Migrationen und 0 Frontend-Seiten ohne Doku-/Route-/Nav-Bezug. |
| Archiv/Dubletten | `DOC-MIGRATION-001...009` hat die Altbestaende archiviert; aktive Dubletten sind ueber Inventare/Indexe eingeordnet. |
| Alte Gap-Matrizen | Bleiben als historische Benchmarks nutzbar, duerfen aber nicht mehr als aktueller Backlog gelesen werden. |
| Generierte QA-Matrizen | `traceability-matrix.md` und `action-matrix-report.md` sind Heuristiken. `GAP` bedeutet dort fehlende maschinelle Verknuepfung, nicht zwingend fehlende Implementierung. |
| Open-Gaps | Bleibt die operative Restliste; externe Gates muessen dort getrennt von repo-seitig schliessbaren Bugs stehen. |

## Quellen- Und Reverse-Update-Register

Dieses Register ist verbindlich fuer spaetere Reverse-Pflege: Wenn eine Quelle
inhaltlich geaendert wird, muessen die abgeleiteten Konsolidierungsaussagen
erneut geprueft und bei Bedarf aktualisiert werden.

| Konsolidierte Aussage | Primaere Quelle | Abgeleitete/markierte Dateien | Reverse-Update-Regel |
|---|---|---|---|
| Aktueller Lieferstand kommt aus Status, Workboard und Slices, nicht aus alten Gap-Matrizen. | `docs/architecture/process-kernel/STATUS.md`, `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/*.yaml` | `docs/project-context/agrar-parity-matrix-2026-05-17.md`, `docs/project-context/agrar-erp-gap-matrix-2026-05-17.md`, `docs/project-context/erp-reference-gap-analysis-amic-community-erp-fiori-2026-04-08.md` | Bei neuem Domain-/Wave-Status: historische Hinweise nicht loeschen, aber Open-Gaps und diesen Bericht gegenpruefen. |
| Code-zu-Doku-Drift ist geschlossen. | `python scripts/doc_drift_report.py`, `artifacts/doc_drift_report.json` | `docs/project-context/documentation-consolidation-2026-06-26.md`, `docs/dokumentation/migrationsplan.md` | Bei neuem Drift > 0: Report neu erzeugen und Restliste ergaenzen; nicht alte Benchmark-Dateien reaktivieren. |
| Action-/Traceability-Gaps sind Heuristik, kein Beweis fuer fehlende Implementierung. | `docs/quality-assurance/action-matrix-report.md`, `docs/quality-assurance/traceability-matrix.md`, jeweilige Generatoren | Diese beiden QA-Reports und dieser Konsolidierungsbericht | Bei Generator-Logik oder neuen Matrixwerten: Konsolidierungshinweis beibehalten, aber konkrete Restbacklog-Punkte neu bewerten. |
| Externe Production-Readiness-Gates bleiben offen, auch wenn Repo-Evidenz vorhanden ist. | `docs/operations/production-readiness-runbook.md`, `scripts/simulate_external_assessors.py`, `docs/project-context/open-gaps-and-known-issues.md` | Restliste P0/P1 in diesem Bericht | Bei realer Abnahme: Open-Gaps zuerst aktualisieren, danach diesen Bericht und ggf. Runbooks nachziehen. |
| Admin-Suite-Roadmap ist Referenz, kein aktueller Umsetzungsplan. | `docs/project-context/admin-suite-roadmap-2026-05-30.md`, Admin-Suite-Slices im Workboard | `docs/project-context/admin-suite-roadmap-2026-05-30.md`, dieser Bericht | Bei neuen Admin-Suite-Slices: Workboard/Slice ist fuehrend; Roadmap nur mit Statushinweis fortschreiben. |
| Randdokumente duerfen offene Card-Gaps nur behalten, wenn Slice/Open-Gaps und Code das bestaetigen. | `docs/cards/**`, `docs/workflows/**`, `docs/agent-ops/slices/*.yaml`, Code-/Testtreffer per `rg` | `FIN-001`, `COM-001`, `open-gaps-and-known-issues.md`, betroffene Slice-YAMLs | Bei Card-Aenderungen immer Workflow, Slice-YAML und Open-Gaps mit derselben Quelle nachziehen. |

## Randdokumente-Nachlauf 2026-06-26

Zusaetzlich zu den grossen Gap-Matrizen wurden aktive Randdokumente in
`docs/cards/`, `docs/workflows/` und `docs/compliance/` gesichtet. Ergebnis:

| Bereich | Befund | Quellen | Aktion |
|---|---|---|---|
| FIN-001 Card | Card fuehrte Abschluss-Stubs noch als offen, obwohl Code, Tests und Workflow die Fachlogik belegen. | `app/services/finance_closing_service.py`, `app/api/v1/endpoints/finance_actions.py`, `tests/test_finance_closing_service.py`, `docs/workflows/fin-001-finance-to-reporting.md` | FIN-Card, Open-Gaps und Slice-YAML geschlossen; externe FiBu-Abnahme bleibt Gate. |
| COM-001 Card | Card fuehrte CamelCase-Register noch als offen, obwohl Backend snake_case + camelCase liefert und Frontend camelCase nutzt. | `app/api/v1/endpoints/compliance.py`, `packages/frontend-web/src/lib/api/betrieb.ts`, Register-Seiten, `docs/workflows/com-001-compliance-to-audit.md` | COM-Card, Open-Gaps und Slice-YAML geschlossen; fachliche Compliance-Abnahme bleibt Gate. |
| CRM-001 Card | Legacy-/Compat-Routen existieren weiterhin bewusst; keine vollstaendige Schliessung ohne erneuten gezielten Frontend-Sweep. | `CRM-LEGACY-API-MIGRATE-001.yaml`, `route-tree.gen.tsx`, CRM-API-Treffer | Bleibt als echter Restpunkt. |
| ISO/A1 Compliance | Roadmap-/Gap-Dokumente sind Referenz fuer Zertifizierungs- und Organisationsgates, nicht aktueller Code-Backlog. | `docs/compliance/iso27001-gap-analysis.md`, `docs/compliance/a-eins-compliance-roadmap.md`, Production-Readiness-Runbook | Keine Code-Gaps daraus ableiten; offene Punkte als externe/organisatorische Gates fuehren. |

## Tatsaechlich Noch Zu Erledigen

### P0/P1 - vor produktiver Freigabe relevant

1. **CI-Head wieder gruen bekommen.**
   Aktuelle rote Gates muessen immer zuerst gelesen und geschlossen werden.
   Stand dieser Konsolidierung: Docs-Governance/Docs-Build wurden mehrfach
   repariert; bekannte Rueckstaende koennen aus neuen Parallel-Commits kommen.
   *Quellen:* `.github/workflows/quality-gate.yml`, `.github/workflows/release-gates.yml`
   *Rueckschreiben bei Schliessung:* `open-gaps-and-known-issues.md` § Build-Health, diesen Bericht.

2. **Dependency-/Security-Backlog abbauen.**
   GitHub meldet weiterhin hunderte Vulnerabilities. Patches und Major-Updates
   muessen ueber den bestehenden Kompatibilitaetsprozess laufen:
   Security-Slice, Advisory-Klassifikation, SBOM/Audit, Contract-/Migration-/
   Browser-Tests, Canary/Rollback oder Forward-Fix.
   *Quellen:* GitHub Dependabot-Alerts, `docs/project-context/open-gaps-and-known-issues.md` § PROD-READINESS-001
   *Rueckschreiben bei Schliessung:* `open-gaps-and-known-issues.md` § PROD-READINESS-001.

3. **Production-Readiness externe Gates real schliessen.**
   Repo-seitig vorbereitet, aber extern offen bleiben insbesondere:
   TSE-/DSFinV-K-Pruefwerkzeug und Hardwareabnahme, Steuerberater-/DATEV-
   Cutover, DSB-/Rechtsfreigaben, produktive Cluster-Secrets, beobachtete
   Restore-/Incident-Drills und UAT-Unterschriften.
   *Quellen:* `docs/operations/production-readiness-runbook.md`, `open-gaps-and-known-issues.md` § PROD-READINESS-001 + § P4
   *Rueckschreiben bei Schliessung:* `open-gaps-and-known-issues.md` § PROD-READINESS-001 + § P4, Runbooks.

4. **Runtime-Sweep-Restliste erneut live verifizieren.**
   `open-gaps-and-known-issues.md` fuehrt noch Restkategorien aus dem
   Live-Sweep: fehlende Tabellen/Migrationen, Response-Envelope-Validierung,
   fehlende Konfiguration und einzelne Feature-Luecken.
   **Welle-5-Nachzug (2026-06-26):** Kat. C (`health/live`, `ebilanz/taxonomie-felder`),
   Kat. E (`mcp/tools`), Kat. F (`logistik/frachtbriefe`) sind in `open-gaps-and-known-issues.md`
   als geschlossen markiert. Verbleibend: Kat. A (fehlende DB-Tabellen), restliche Kat. C
   (`mcp/policy/list`, `einkauf/*`, `inventory/warehouses`), Kat. E (Proplanta).
   Ein neuer Live-Sweep muss die aktuelle Lage der A/C-Restkandidaten verifiizieren.
   *Quellen:* `open-gaps-and-known-issues.md` § RUNTIME-API-SWEEP-001 (Kat. A–F)
   *Rueckschreiben bei Schliessung:* jeweilige Kategorie in § RUNTIME-API-SWEEP-001 als behoben kennzeichnen + § Konsolidiertes Restbacklog.

5. **Semantische E2E-Kernpfade haerten.**
   Die Action-Matrix zeigt vor allem Test-/Nachweis-Gaps. Besonders sinnvoll:
   FiBu OP/Auszifferung/Periodenabschluss/DATEV, O2C Rechnung->Zahlung,
   P2P WE->Rechnung->SEPA, POS Tagesabschluss/DSFinV-K und WMS Waage->Lot->Silo.
   *Quellen:* `docs/quality-assurance/action-matrix-report.md`, `docs/quality-assurance/traceability-matrix.md`
   *Rueckschreiben bei Schliessung:* Neue Tests einchecken, dann QA-Reports neu generieren; `open-gaps-and-known-issues.md` § COVERAGE-001 Ratchet anheben.

### P2 - fachliche Vertiefung, die weiterhin sinnvoll ist

1. **WMS/Agrar Materialfluss.**
   Zielzellen-Regelvorschlag aus WE/Waage, operative Konfliktpruefung bei
   Foerderwegen, Bird-View/Anlagenkarte und spaetere PLC/MES-Anbindung.
   *Quellen:* `open-gaps-and-known-issues.md` § DOMAIN-PARITY-001 WM-AGRI-SUPPLY-LINK-001; `domain-depth-plan-2026-05-17.md` § 3 Lager/WMS Schritt 8
   *Rueckschreiben bei Schliessung:* Slice-YAML WM-AGRI-MAP-001; `open-gaps-and-known-issues.md` § DOMAIN-PARITY-001; § Konsolidiertes Restbacklog Zeile „Zielzellen-Regelengine".

2. **QS/Compliance im Rohwarenfluss.**
   Labor->Lager->Produktion als auditierter Freigabeprozess mit Proben-,
   Analyse-, GMP+/VLOG- und Dokumentenbezug weiter verdichten.
   *Quellen:* `open-gaps-and-known-issues.md` § DOMAIN-PARITY-001 WM-AGRI-QS-003/004; `domain-depth-plan-2026-05-17.md` § 4 Agrar + § 8 Compliance
   *Rueckschreiben bei Schliessung:* Slice-YAML; `open-gaps-and-known-issues.md` § DOMAIN-PARITY-001 nachziehen.

3. **Futtermittelproduktion.**
   Verbrauch Silozelle -> Mischauftrag -> Fertigcharge mit Rueckverfolgbarkeit,
   Rezepturabweichungen, Storno und FIBU-/KORE-Bezug produktionsnah absichern.
   *Quellen:* `domain-depth-plan-2026-05-17.md` § 10 Futtermittel; `open-gaps-and-known-issues.md` § Enterprise-Domain-Gap-Closure; `professional-tail-gap-plan-2026-04-09.md` § 9 + 10 Futtermittel
   *Rueckschreiben bei Schliessung:* Slice-YAML FEED-QS-001; `open-gaps-and-known-issues.md` § Konsolidiertes Restbacklog Zeile Futtermittel; `professional-tail-gap-plan-2026-04-09.md` Status-Aktualisierung.

4. **CRM360/KIM Workflow-Tiefe.**
   Semantische Button-/CRUD-Matrix regelmaessig gegen Playwright laufen lassen:
   jeder Button muss fachlich richtig navigieren, Kontext halten und Back/404
   vermeiden.
   *Quellen:* `docs/agent-ops/slices/KIM-L3-FRONTEND-001.yaml`; `open-gaps-and-known-issues.md` § Konsolidiertes Restbacklog Zeile „CRM RAG-Panel"
   *Rueckschreiben bei Schliessung:* Slice-YAML; `professional-tail-gap-plan-2026-04-09.md` § Status-Aktualisierung TAIL-CRM-001; `open-gaps-and-known-issues.md` § Konsolidiertes Restbacklog.

5. **Lohnbuchhaltung/HRM nur als kontrollierter Integrationspfad.**
   Repo-seitig Payroll-Exportprofile und Closeout-Preview sind vorhanden; echte
   Tiefe braucht externe PAP/ELStAM/DEUEV/DATEV-/Steuerberaterfreigabe.
   *Quellen:* `open-gaps-and-known-issues.md` § P4 HRM/Payroll-Exportprofile; `domain-depth-plan-2026-05-17.md` § 9 HRM
   *Rueckschreiben bei Schliessung:* `open-gaps-and-known-issues.md` § P4 HRM geschlossen markieren; externe Gate-Abnahme dokumentieren.

6. **Traceability-Matrix verbessern.**
   Der aktuelle Generator zaehlt viele abgeschlossene Slices als `GAP`, weil
   Tests/Doku nicht immer maschinenlesbar verknuepft sind. Sinnvoll ist ein
   Slice zur Traceability-Normalisierung, nicht manuelles Schoenfaerben.
   *Quellen:* `docs/quality-assurance/traceability-matrix.md`, Generator-Skript
   *Rueckschreiben bei Schliessung:* Generator-Logik anpassen; `open-gaps-and-known-issues.md` § Build-Health OpenAPI-Routen-Nachweis aktualisieren.

## Konsolidierungsregeln Ab Jetzt

- Aktueller Lieferstand: `STATUS.md`, Workboard, Slice-YAML und Open-Gaps.
- Historische Gap-/Benchmark-Dateien duerfen keine neue Arbeit erzeugen, ohne
  erneute Evidenz gegen Code und Tests.
- Externe Gates werden nicht als repo-seitig erledigt markiert.
- Generierte Reports bleiben Reports; echte Planung landet in Open-Gaps oder
  einem Slice.
- Doku-Dubletten werden bevorzugt archiviert oder mit Statushinweis versehen,
  nicht parallel weitergepflegt.
