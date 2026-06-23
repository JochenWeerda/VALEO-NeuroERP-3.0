# AI-assisted Development Implementation Plan

**Status:** umgesetzt
**Datum:** 2026-06-23
**Referenz:** `docs/architecture/ai-assisted-enterprise-development-standard.md`

## Ziel

Den AI-assisted Enterprise Development Standard operativ in VALEO verankern. Das Ergebnis soll nicht nur eine Richtlinie sein, sondern ein pruefbarer Entwicklungsbetrieb mit:

- harten Slice-Vertraegen
- Doku-/Code-Sync
- AI-spezifischer Definition of Done
- semantischen QA-Gates
- Security-/Compliance-Pruefer-Simulation
- wartbarer Modell- und Vendor-Unabhaengigkeit

## Leitprinzip

Bestehende Mechanismen werden erweitert statt ersetzt:

- `docs/agent-ops/*` bleibt zentrale Agentenkoordination.
- `.github/workflows/*` bleibt Gate-Ort fuer CI.
- `docs/quality-assurance/*` bleibt Nachweisort fuer fachliche Tests.
- `docs/project-context/open-gaps-and-known-issues.md` bleibt Risikoregister.
- ADRs und Process-Kernel-Status bleiben Source of Truth fuer Architektur- und Lieferstand.

## Phase P0 - Harness verbindlich machen

**Ziel:** Jeder AI- oder Agenten-Slice bekommt einen maschinenlesbaren Mindestvertrag.

**Umsetzung:**

1. `docs/agent-ops/task-slice-template.md` um AI-Harness-Felder erweitern:
   - fachlicher Vertrag
   - Architekturvertrag
   - Datenvertrag
   - Testvertrag
   - Security-Vertrag
   - Betriebsvertrag
   - Dokumentationsvertrag
   - externe Gates
2. Neue Slice-YAML-Konvention fuer `ai_harness` einfuehren.
3. Docs-Governance prueft bei neuen/veraenderten Slice-Dateien, ob Pflichtfelder vorhanden sind.
4. Workboard-Regel ergaenzen: AI-Slice ohne Harness ist nicht `in arbeit` faehig.

**Dateibesitz:**

- `docs/agent-ops/task-slice-template.md`
- `docs/agent-ops/parallel-work-protocol.md`
- `docs/agent-ops/README.md`
- `scripts/docs-governance-check.cjs`
- `.github/workflows/docs-governance.yml`

**Abnahmekriterien:**

- Beispiel-Slice mit vollstaendigem AI-Harness validiert gruen.
- Unvollstaendiger Test-Slice wird lokal vom Governance-Check abgelehnt.

## Phase P1 - Doku-/Code-Sync Gate

**Ziel:** Relevante Codeaenderungen duerfen nicht ohne passende Doku- oder Gap-Aktualisierung landen.

**Umsetzung:**

1. Mapping-Datei anlegen: Codepfade -> erwartete Doku-Bereiche.
2. Script `scripts/docs-code-sync-check.cjs` einfuehren.
3. CI-Job in `docs-governance.yml` erweitern.
4. Ausnahmen nur mit explizitem Marker erlauben, z. B. `docs-sync-exception` in Slice-YAML.

**Beispiel-Mapping:**

| Codepfad | Erwartete Doku |
|----------|----------------|
| `app/api/v1/endpoints/**` | API-/Workflow-/QA-Doku oder Open-Gaps |
| `app/services/**` | Fach-/Workflow-Doku oder Tests |
| `packages/frontend-web/src/pages/**` | UI-/Browser-Use-/QA-Doku |
| `alembic/versions/**` | Migrations-/Runbook-/Domain-Doku |
| `.github/workflows/**` | Operations-/QA-Doku |

**Dateibesitz:**

- `config/docs-code-sync-map.yaml`
- `scripts/docs-code-sync-check.cjs`
- `.github/workflows/docs-governance.yml`
- `docs/operations/production-readiness-runbook.md`

**Abnahmekriterien:**

- Code-only-Aenderung an kritischem Pfad faellt im Check durch.
- Code+Doku-Aenderung besteht.
- Explizite, dokumentierte Ausnahme besteht und wird im Report sichtbar.

## Phase P2 - AI Definition of Done automatisieren

**Ziel:** Die AI-Slice-DoD wird nicht nur gelesen, sondern lokal und in CI geprueft.

**Umsetzung:**

1. Script `scripts/ai-slice-readiness-check.cjs` einfuehren.
2. Check prueft:
   - Slice-YAML vorhanden
   - Workboard-Eintrag vorhanden
   - Tests/Checks dokumentiert
   - Doku-Update oder Ausnahme vorhanden
   - externe Gates benannt, wenn Compliance-relevant
3. CI-Workflow `quality-gate.yml` oder neuer Job `ai-slice-readiness` ergaenzen.
4. README und Agent-Ops-Doku aktualisieren.

**Dateibesitz:**

- `scripts/ai-slice-readiness-check.cjs`
- `.github/workflows/quality-gate.yml`
- `docs/agent-ops/README.md`
- `docs/README.md`

**Abnahmekriterien:**

- Ein abgeschlossener Slice ohne Tests oder begruendete Ausnahme faellt durch.
- Ein Slice mit externem Gate wird als intern bestanden, extern offen reportet.

## Phase P3 - Semantische QA-Templates ausrollen

**Ziel:** Kritische Domain-Flows werden nach fachlichem Vertrag getestet, nicht nur nach Klickbarkeit.

**Umsetzung:**

1. QA-Template fuer semantische Action-Matrix anlegen.
2. Template fuer Playwright-Vertrag definieren:
   - sichtbare Aktion
   - Zielroute/Zielmaske
   - Entity-Kontext
   - CRUD-Typ
   - Back-Verhalten
   - Console-/Request-Fehler
   - fachliche Workflow-Kategorie
3. Muster aus CRM360 auf POS, WMS, FiBu, HR und QS uebertragen.
4. Externe-Pruefer-Simulationen als eigene QA-Dokumente fuehren.

**Priorisierte Flows:**

1. POS/TSE: Bon, Tagesabschluss, Zahlungsarten, Fibu-Uebergabe.
2. WMS/Silo: Annahme -> Waage -> Lot -> Silo -> QS -> Trace.
3. FiBu/Payroll: Monatsabschluss, DATEV/Kanzlei-Export, OP-/Fibu-Buchungssaetze.
4. CRM360: Kundenakte -> Angebot -> Auftrag -> Lieferschein -> Rechnung -> Zahlung.
5. QS/Reklamation: Labor -> Sperre/Freigabe -> Retoure/Gutschrift/CAPA.

**Dateibesitz:**

- `docs/quality-assurance/semantic-action-matrix-template.md`
- `docs/quality-assurance/external-auditor-simulation-template.md`
- `playwright-tests/specs/**` nur je Domain-Slice

**Abnahmekriterien:**

- Mindestens ein neuer Domain-Flow nutzt das Template.
- QA-Report unterscheidet OK, falsches Ziel, fehlender CRUD, 404/Back-Bug, fachlich fragwuerdig, externes Gate offen.

## Phase P4 - Nightly AI Documentation Sync

**Ziel:** Doku-Drift wird regelmaessig sichtbar.

**Umsetzung:**

1. Nightly Workflow `ai-doc-sync.yml` anlegen.
2. Kein automatisches Ueberschreiben produktiver Doku.
3. Job erzeugt Report-Artefakt:
   - geaenderte APIs ohne Doku-Hinweis
   - neue Routen ohne Routing-/QA-Nachweis
   - neue DB-Migrationen ohne Runbook/Gaps
   - neue Tests ohne QA-Verweis
4. Optional spaeter: Bot-PR mit vorgeschlagenem Doku-Update.

**Dateibesitz:**

- `.github/workflows/ai-doc-sync.yml`
- `scripts/docs-drift-report.cjs`
- `docs/operations/production-readiness-runbook.md`

**Abnahmekriterien:**

- Nightly Report wird als Artefakt publiziert.
- Keine automatische Doku-Mutation ohne Review.
- Drift wird als Warnung gestartet, spaeter fuer kritische Pfade als Gate gehaertet.

## Phase P5 - Modell-/Vendor-Unabhaengigkeit

**Ziel:** Agentenarbeit bleibt fortsetzbar, auch wenn ein Anbieter ausfaellt oder Modellwechsel noetig wird.

**Umsetzung:**

1. Prompt-/Harness-Artefakte repo-stabil halten.
2. Modellannahmen in `docs/operations/dependency-and-compatibility-maintenance.md` aufnehmen.
3. AI-Tool-Kompatibilitaetsmatrix erweitern:
   - Codex
   - Claude Code
   - lokale Modelle
   - Aider/Continue
   - GitHub/CodeRabbit/SonarCloud
4. Sensible Datenklassen markieren: was darf in externe Modelle, was nur lokal.

**Dateibesitz:**

- `docs/operations/dependency-and-compatibility-maintenance.md`
- `docs/architecture/tooling-quality-governance.md`
- optional `artifacts/ai-tool-compatibility-matrix.json`

**Abnahmekriterien:**

- Kritische Agentenprozesse sind nicht nur in Chatverlaeufen dokumentiert.
- Datenschutz-/Datenresidenzregeln fuer AI-Nutzung sind explizit.

## Phase P6 - Security- und Major-Update-Prozess verbinden

**Ziel:** Sicherheitsluecken und Major Updates werden als kontrollierte Kompatibilitaetsarbeit behandelt.

**Umsetzung:**

1. Existing Dependency-Maintenance um AI-Slice-Bezug erweitern.
2. Major-Update-Runbook mit:
   - Advisory-Klassifikation
   - betroffene Module
   - Contract-Test-Auswahl
   - Canary/Feature Flag
   - Rollback
   - externe Gate-Relevanz
3. Audit-Reports muessen zwischen "fixable minor", "forced major", "accepted temporary risk" unterscheiden.

**Dateibesitz:**

- `docs/operations/dependency-and-compatibility-maintenance.md`
- `docs/quality-assurance/production-readiness-assessment-2026-06-09.md`
- `.github/workflows/quality-gate.yml`

**Abnahmekriterien:**

- Major Update darf nicht ohne Contract-Testliste dokumentiert werden.
- Temporär akzeptierte Security-Risiken haben Ablaufdatum und Owner.

## Reihenfolge der Umsetzung

1. **P0 Harness verbindlich machen** - hoechster Hebel, geringe technische Risiken.
2. **P1 Doku-/Code-Sync Gate** - verhindert neue Doku-Drift.
3. **P2 AI Definition of Done automatisieren** - macht Abschlussmeldungen belastbar.
4. **P3 Semantische QA-Templates** - direkt nutzbar fuer aktuelle Domain-Vertiefungen.
5. **P4 Nightly Documentation Sync** - nach P1/P2 sinnvoll, damit Reports verwertbar sind.
6. **P5 Vendor-Unabhaengigkeit** - parallel moeglich, aber weniger dringend als Gates.
7. **P6 Security/Major-Update-Prozess** - mit vorhandener Dependency-Doku zusammenfuehren.

## Empfohlener erster Slice

```yaml
slice_id: AI-HARNESS-GOV-001
title: AI-assisted Development Harness Governance
owner: Codex
status: offen
goal: >-
  AI-Slice-Harness in Agent-Ops, Slice-Template und Docs-Governance verbindlich
  machen, damit neue Agentenarbeit pruefbare Fach-, Architektur-, Test-,
  Security-, Betriebs- und Doku-Vertraege enthaelt.
file_ownership:
  - docs/agent-ops/task-slice-template.md
  - docs/agent-ops/parallel-work-protocol.md
  - docs/agent-ops/README.md
  - scripts/docs-governance-check.cjs
  - .github/workflows/docs-governance.yml
  - docs/project-context/ai-assisted-development-implementation-plan-2026-06-23.md
acceptance:
  - Slice-Template enthaelt AI-Harness-Pflichtfelder.
  - Governance-Check erkennt fehlende Pflichtfelder in Slice-YAML.
  - docs:check laeuft gruen.
  - Bestehende Slices werden nicht massenhaft umgeschrieben; Legacy bleibt grandfathered.
risks:
  - Zu harte Gates koennen laufende parallele Arbeit blockieren.
  - Deshalb zuerst nur neue oder veraenderte Slices pruefen.
```

## Nicht-Ziele

- Keine automatische Codegenerierung durch Nightly Jobs.
- Kein ungeprueftes automatisches Umschreiben der Dokumentation.
- Keine neuen Pflichttools, solange vorhandene CI-/Docs-Governance reicht.
- Kein Gate, das bestehende Altlasten sofort repo-weit blockiert.

## Erfolgsmessung

Nach Umsetzung von P0 bis P3 gilt der Standard als operativ eingefuehrt, wenn:

- neue Slices einen Harness haben
- Doku-Drift bei kritischen Pfaden erkannt wird
- AI-Slice-Abschluss maschinell pruefbar ist
- mindestens ein neuer semantischer Domain-Flow nach Template getestet wurde
- offene externe Gates transparent im Report erscheinen

## Umsetzungsstand 2026-06-23

`AI-HARNESS-GOV-001` hat den Plan operativ umgesetzt:

- P0: Slice-Template, Parallel-Work-Protokoll und Agent-Ops README um AI-Harness erweitert.
- P1: `scripts/docs-code-sync-check.cjs`, `config/docs-code-sync-map.yaml` und Quality-Gate-Job eingefuehrt.
- P2: `scripts/ai-slice-readiness-check.cjs` und Slice-YAML-Governance eingefuehrt.
- P3: Semantische Action-Matrix und externe Pruefer-Simulation als QA-Templates angelegt.
- P4: `scripts/docs-drift-report.cjs` und Nightly Workflow `ai-doc-sync.yml` angelegt.
- P5: AI-Tool-Kompatibilitaetsmatrix angelegt und Tooling-Doku erweitert.
- P6: Dependency-/Compatibility-Doku um AI-gestuetzte Major-Update- und Security-Regeln erweitert.

Verifiziert mit `node --check`, AI-Slice-Readiness, Docs-/Code-Sync und `pnpm.cmd run docs:check`.
