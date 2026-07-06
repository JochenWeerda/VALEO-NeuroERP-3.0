---
title: Production-Readiness-Audit 2026-07-02
type: audit
audience: [betrieb, entwickler, agent, qa, security]
owner: Codex
status: aktiv
last_reviewed: 2026-07-02
version: 1.0.0
description: Production-Readiness-Audit, Spec-Backlog und Agenten-Programm fuer VALEO NeuroERP 3.0.
---

# VALEO NeuroERP 3.0 — Production-Readiness-Audit, Spec-Backlog & Agenten-Programm

**Stand:** 2026-07-02 · **Basis:** `main` (2.076 Commits), README (Doku-Stand 2026-06-28), `docs/project-context/open-gaps-and-known-issues.md` (v3.3.0, Review 2026-06-30), `docs/operations/production-readiness-runbook.md` (v3.0.0)

---

## 1. Executive Summary

VALEO NeuroERP 3.0 ist ein bemerkenswert breites, agentengetriebenes Multi-Domain-ERP (12+ Fachdomänen, FastAPI/React, 3.041 OpenAPI-Routen, ~160 Service-Module). Das Projekt trägt selbst die Einstufung **Beta**: Kernprozesse operativ, externe Go-Live-Gates offen.

**Gesamturteil:** Repo-seitig ist das Projekt deutlich weiter als typische Beta-Systeme (harte CI-Gates, Alembic Single Head, arc42/C4/36 ADRs, fail-closed Release-Modell, simulierte Prüferprofile). **"Production ready" scheitert derzeit nicht primär an fehlendem Code, sondern an drei Dingen:**

1. **Verifizierbarkeit:** Zentrale Qualitätsaussagen (9.500+ Tests, 0×5xx, Coverage) sind zuletzt *lokal* nachgewiesen; ein sichtbar grüner GitHub-Actions-Voll-Lauf steht laut eigenem Tracker aus (UIX-032/055). Letzter dokumentierter Voll-Pass der Backend-Suite: 2026-05-26 — über einen Monat alt.
2. **Betriebs-/Compliance-Evidenz:** Alle externen Gates (Keycloak-Prod-Credentials, TSE/DSFinV-K, ERiC/ELSTER, DATEV-Cutover, Backup/Restore-Drill, Lasttest, UAT-Unterschriften, DSB-Freigabe) sind offen — per Design Betriebsverantwortung, aber ohne sie kein Go-Live.
3. **Repo-Hygiene & Governance:** Temporäre Dateien, Build-Artefakte und eine Lead-Datei mit potenziell personenbezogenen Daten liegen im *öffentlichen* Repo; Coverage-Ratchets wurden mehrfach nach unten "kalibriert"; Bus-Faktor ≈ 1.

**Ampel-Bewertung:**

| Dimension | Status | Kernbefund |
|---|---|---|
| Fachliche Breite/Tiefe | 🟢 | DOM-*-004-Welle abgeschlossen, O2C/P2P/FIBU/Agrar operativ tief |
| Architektur | 🟡 | Solider modularer Monolith, aber Struktur-Sprawl & Parallel-Backends |
| Code-Qualität | 🟡 | Coverage 64,85 %, 80 untypisierte Routen, 62 nosec-SQL-Stellen |
| CI/Verifizierbarkeit | 🟠 | GHA-Voll-Grün offen, Live-Sweep-Wiederholung offen |
| Security/Compliance (Repo) | 🟡 | Gute Gates, aber PII-/Tmp-Dateien im Repo, Ratchet-Absenkungen |
| Betrieb/Go-Live-Gates | 🔴 | Alle externen Gates offen (erwartbar, aber blockierend) |
| Audit-Fähigkeit ISO/SOC2 | 🟠 | ISO-27001-Simulation vorhanden; SOC-2-Profil fehlt komplett |

---

## 2. Methodik & Grenzen dieser Analyse

- Analysebasis: öffentliche Repo-Ansicht (README, Gap-Tracker, Runbook, Verzeichnisstruktur). Kein lokaler Build/Testlauf in dieser Analyse — deshalb enthält Kapitel 6 einen **Verifikations-Agenten (Prompt A0)**, der alle Selbstauskünfte des Repos unabhängig nachprüft, bevor irgendetwas anderes passiert.
- Aussagen wie "9.527 Tests collected" oder "1.059 GET-Endpoints live getestet" werden hier als *Behauptungen mit Repo-Evidenz* behandelt, nicht als verifizierte Fakten.
- "Agentisch simulierte TÜV-/ISO-/SOC2-Prüfungen" (Kapitel 7) sind **Readiness-Assessments**. Sie ersetzen keine akkreditierte ISO-27001-Zertifizierung (z. B. durch TÜV/DEKRA), kein SOC-2-Testat (nur durch WP/CPA-Gesellschaft, Type II mit 3–12 Monaten Beobachtungszeitraum) und keine DSFinV-K-/Eich-/Hardware-Abnahmen. Das Repo formuliert dieses fail-closed-Prinzip selbst korrekt im Runbook.

---

## 3. Architektur-Validierung

### 3.1 Stärken (validiert gegen Doku & Struktur)

- **Modularer Monolith mit thin-router/Service-Pattern** (`app/services/`, ~160 Module) statt verfrühter Microservices — für ein 1-Team-/Agenten-Projekt die richtige Wahl.
- **Multi-Schema-PostgreSQL** (14 `domain_*`-Schemas) mit Ownership-Check-Skript — sauberer Domänenschnitt auf DB-Ebene, Migrationspfad zu Services später möglich.
- **Alembic Single Head** nach Schließung von 55+ Parallel-Branches — für ein agentengetriebenes Repo eine kritische und gelöste Hürde.
- **Eventing über NATS JetStream + Outbox-Pattern**, Workflow-Cockpit mit Retry/Kompensation/Dead-Letter — korrektes Muster für exactly-once-Semantik.
- **Security-Grundgerüst:** OIDC/JWKS RS256, zentrale `TenantEnforcementMiddleware`, RFC-7807, Bearer-Enforcement, gitleaks/grype/ZAP/Trivy/Bandit in CI, SBOM (CycloneDX), unveränderliche SHA-Images, Helm `--atomic`, fail-closed Preflight (`check_production_readiness.py` blockiert u. a. `API_DEV_TOKEN`, DEBUG, Wildcard-Hosts, mutable Tags, exponierte DB-Ports).
- **Architektur-Governance:** arc42, C4 als Structurizr-DSL (Source of Truth, ADR-037), 895/895 Routen + 205/205 Services domänen-gemappt, Drift-Checks in CI.
- **Human+Agent-Dualität:** `ScreenDefinition` als Single Source of Truth für UI-Rendering *und* `AgentMaskContract` (lesbare/editierbare/sensible Felder, Action-Policies, Audit-Anforderungen) — architektonisch der interessanteste und zukunftssicherste Teil des Systems.

### 3.2 Findings (Risiken & Schwächen)

**ARCH-F1 — Struktur-Sprawl / unklare Ownership (P1).**
Im Root koexistieren `app/`, `src/`, `services/`, `modules/`, `domains/`, `packages/`, `mains/crm`, `ols/`, `gap/`, `swarm/`, `memory/`, `guacamole-l3-migration/`, `l3-migration-toolkit/`, `rationsoptimierung/`, `knowledge-base/`. Für neue Entwickler und Agenten ist nicht deterministisch, wo Code hingehört. Besonders kritisch: `domains/inventory` ist ein **paralleles TypeScript-Backend** mit eigener CI, eigenem `tsconfig.ci.json`-Kompatibilitätsprofil und laut Tracker "noch nicht produktiv verdrahtet" — totes bzw. halbtotes Parallel-System neben dem Python-Backend. → Konsolidieren oder archivieren (Prompt A9).

**ARCH-F2 — API-Fläche als Blast-Radius (P1).**
3.041 Routen in einem Deployment bedeuten: jede Regression kann jede Domäne treffen; OpenAPI-Generierung war bereits einmal *global* defekt (cached_read_model/`__globals__`-Bug legte die gesamte `/openapi.json` lahm). Empfehlung: **Feature-Freeze auf Breite**, Route-Deprecation-Plan für Legacy-Pfade, Modul-Level-Smoke pro Domäne als eigenständiges CI-Gate.

**ARCH-F3 — Graceful Degradation maskiert Fehlkonfiguration (P0).**
Kategorie-B-Endpoints liefern *by design* 503 bei fehlenden Migrationen/Configs (analytics, contracts, compliance/DSGVO-Erasure, LkSG, Whistleblower, Anlagenbuchhaltung, Budgets, WhatsApp-Webhook). Mehrere Kat.-D-Fixes degradieren zusätzlich auf **leere Listen statt Fehler** (`journal-entries`, CRM-Listen, Bestellvorschläge). Im Dev sinnvoll — in Produktion ist ein FIBU-Endpoint, der still eine leere Liste liefert, ein **Datenintegritätsrisiko**. Erforderlich: pro Modul eine explizite Prod-Entscheidung (aktiv+migriert *oder* Flag off + aus OpenAPI entfernt) und `/readyz`-Verdrahtung kritischer Module (Prompt A5).

**ARCH-F4 — SQL-/Typisierungs-Restrisiko (P1).**
62 Endpoints tragen `nosec S608`-Annotationen (dynamisches SQL, laut Doku nur feste Feldlisten, Werte parametrisiert) plus 9 review-markierte Neufunde; 80 Legacy-Routen ohne `response_model`. Beides ist dokumentiert und gedeckelt, aber vor Go-Live gehört ein dedizierter Injection-Review + Property-Tests auf die 71 Stellen (Prompt A7).

**ARCH-F5 — Governance/Bus-Faktor (P0, organisatorisch).**
Ein Maintainer, 0 Forks, Entwicklung in hochfrequenten Agenten-"Waves". Es fehlen: CODEOWNERS, erzwungene Branch-Protection (laut Runbook selbst noch externes Gate), Vier-Augen-Review für sicherheits-/finanzkritische Pfade. Ein ERP, das GoBD-relevante Buchungen erzeugt, braucht nachweisbare Änderungskontrolle — das ist auch ISO-27001- (A.8.32) und SOC-2-relevant (CC8.1).

**ARCH-F6 — Coverage-Ratchet-Erosion (P0, kulturell).**
COV-RATCHET-006 und -010 dokumentieren, dass Gate-Schwellen mehrfach **auf Ist-Werte abgesenkt** wurden statt Tests zu schreiben. Aktuelle Tiefstände auf produktkritischen Pfaden: `psm_proplanta` 15 %, `financial_reports` 25 %, `sales_invoice_einvoice` 30 %, `portal_innendienst` 30 %, `rohware_sammelabrechnung` 32 %, `ai_engineering_metrics` 38 %. Für ein Finanz-/Abrechnungssystem sind 25–32 % auf Rechnungs-/Report-Pfaden nicht go-live-fähig. Regel ab sofort: **Ratchet darf nur steigen** (Prompt A6).

**ARCH-F7 — Repo-Hygiene & Datenschutz im öffentlichen Repo (P0).**
Im Root liegen: `dist/`, `playwright-results.json`, `.tmp_changed_files.txt`, `.tmp_dlg01_23.txt`, `.tmp_dlg01_25.txt`, `.tmp_export/`, `tmp_playwright_mask_test/`, `evidence/screenshots/` — und vor allem **`PLZ_26XXX_final_leads.json`**: eine Datei, die dem Namen nach reale Vertriebs-Leads (Firmen/Kontakte im PLZ-Raum 26xxx) enthält. In einem öffentlichen Repo ist das ein potenzieller **DSGVO-Vorfall** (Art. 5/6, ggf. Art. 33-Meldepflicht prüfen) und in jedem ISO-/SOC-2-Audit ein sofortiger Major-Finding. Zusätzlich existiert eine `.gitleaks-baseline.json` — Baselines können echte Alt-Funde dauerhaft stummschalten und gehören auditiert. → Sofortmaßnahme Prompt A2 inkl. Git-History-Bereinigung.

**ARCH-F8 — Lizenz-Unschärfe (P2).**
"MIT — sofern in Teilbereichen nicht abweichend dokumentiert" plus FSL-1.1-Apache-2.0 (superglue). Für kommerziellen Vertrieb: vollständiges Lizenzinventar aus SBOM ableiten, abweichende Teilbereiche explizit listen.

**ARCH-F9 — Fachliche Restlücken (P2).**
Trotz DOM-004-Tiefe explizit offen: tieferes **Chargen-/MHD-Modell** jenseits des `charge`-Felds (für Futtermittel/QS relevant), gestubte `commandEndpoints` (drucken, stornieren, wareneingang …), Legacy-`:id`-Routen noch nicht auf native SDs umgehängt, Agent-Contract-E2E über alle 26 ScreenDefinitions.

---

## 4. Verifizierbare Code-/Qualitätsbefunde (aus Repo-Selbstauskunft)

| # | Befund | Quelle | Bewertung |
|---|---|---|---|
| Q1 | 9.527 Tests collected (2026-06-11), letzter Voll-Pass 9.228 (2026-05-26) | open-gaps §Build-Health | 🟠 >1 Monat kein dokumentierter grüner Voll-Lauf |
| Q2 | GHA `universal-mask-ci` "nach Push offen"; UIX-032 nur "✅ lokal" | open-gaps UIX-Tabelle | 🟠 CI-Nachweis fehlt öffentlich |
| Q3 | Live-Sweep 1.059 GET: Kat. A–F repo-seitig geschlossen, "erneuter Live-Sweep muss Restliste verifizieren" | RUNTIME-API-SWEEP-001 | 🟠 Wiederholung ist P0 |
| Q4 | E2E-Produktionsteststand 2026-07-02: 73/73 grün (Lager/Pricing/Scan) | API-GAP-STABILIZATION-001 | 🟢 aktuellster Nachweis |
| Q5 | Coverage gesamt 64,85 %, 33 Ratchet-Pfade grün, aber Ratchets 2× abgesenkt | COVERAGE-001 | 🟠 s. ARCH-F6 |
| Q6 | TypeScript 0 Fehler; Alembic Single Head; OpenAPI 3.041/3.041 mit summary | README/Build-Health | 🟢 |
| Q7 | Tenant-Isolation CI-Gate aktiv; systemische Endpunkte klassifiziert | Build-Health | 🟢 |
| Q8 | UIX-054/055/056/057 (Route-Inventory, CI grün, Native-Route-Smoke, Rollback-Matrix) offen, alle P1 | UIX-Folgearbeit | 🟠 |

---

## 5. Konsolidierter Spec-Backlog (was noch umgesetzt werden muss)

### 5.1 P0 — Go-Live-blockierend, repo-seitig lösbar

| Spec-ID | Titel | Akzeptanzkriterium |
|---|---|---|
| SPEC-P0-01 | **CI-Voll-Grün öffentlich nachweisen** | `quality-gate.yml`, `security-scan.yml`, `universal-mask-ci` auf `main` grün; Badge + Run-Link in README; Voll-pytest mit Pass-Count ≤ 7 Tage alt |
| SPEC-P0-02 | **Live-API-Sweep-Wiederholung** | Sweep-Skript (`tmp_endpoint_sweep.py`) als `scripts/api_runtime_sweep.py` einchecken; nightly CI-Job; Ergebnis: 0×5xx über alle GET-Routen gegen frisch migrierte DB |
| SPEC-P0-03 | **Kat.-B/D-Produktionsentscheidung** | Für jedes 503-by-design- und Leere-Liste-Fallback-Modul: Entscheidung aktiv+migriert ODER Feature-Flag off + Route aus Prod-OpenAPI; kritische Module in `/readyz` verdrahtet; kein FIBU-/Bestands-Endpoint darf still leer liefern |
| SPEC-P0-04 | **Repo-Hygiene & PII-Bereinigung** | `PLZ_26XXX_final_leads.json`, `.tmp_*`, `dist/`, `playwright-results.json`, `tmp_playwright_mask_test/`, `.tmp_export/` entfernt; Git-History gefiltert (git-filter-repo); `.gitignore` erweitert; gitleaks-Baseline auditiert; DSGVO-Bewertung des Lead-Datei-Exposures dokumentiert (Art.-33-Prüfung) |
| SPEC-P0-05 | **Coverage-Ratchet-Politik "only up"** | Ratchet-Skript verweigert Absenkungen; Pfade <50 % auf kritischen Belegen (Rechnung, Sammelabrechnung, Finanzreports) auf ≥70 % gehoben |
| SPEC-P0-06 | **Branch-Protection & CODEOWNERS** | `main` geschützt (Review + Status-Checks required), CODEOWNERS für `app/services/finance*`, `pos/`, `alembic/`, `.github/` |
| SPEC-P0-07 | **SOC-2-Prüferprofil ergänzen** | `simulate_external_assessors.py` um SOC-2-TSC-Profil erweitert (s. Kap. 7); Report in `artifacts/` |
| SPEC-P0-08 | **Restore-/Backup-Drill automatisiert vorbereiten** | Skript + Doku, sodass Ops den 15-min-RTO-Drill reproduzierbar fahren kann; CI-Gate prüft Existenz des letzten Drill-Protokolls (external_gate, fail-closed) |

### 5.2 P1 — Vor bzw. unmittelbar nach Go-Live

| Spec-ID | Titel |
|---|---|
| SPEC-P1-01 | UIX-054 Route-Inventory (`route-inventory.gen.json`) generiert + CI-Drift-Check |
| SPEC-P1-02 | UIX-056 Playwright-Smoke über 5 repräsentative native `/:id`-Routen |
| SPEC-P1-03 | UIX-057 Rollback-Matrix: Legacy-Fallback je kritischer Maske dokumentiert + getestet |
| SPEC-P1-04 | Gestubte `commandEndpoints` fachlich implementieren (drucken, stornieren, wareneingang, …) |
| SPEC-P1-05 | SQL-Injection-Review der 62+9 nosec-S608-Stellen + parametrisierte Property-Tests |
| SPEC-P1-06 | 80 untypisierte Legacy-Routen mit `response_model` versehen |
| SPEC-P1-07 | `domains/inventory` (TS-Parallel-Backend) konsolidieren: produktiv verdrahten ODER nach `docs/_internal/archive` |
| SPEC-P1-08 | Chargen-/MHD-Tiefenmodell (Lot-Attribute, FEFO über MHD, Sperrgründe) |
| SPEC-P1-09 | Lizenzinventar aus SBOM + THIRD_PARTY_NOTICES vervollständigen |
| SPEC-P1-10 | Lasttest-Profil Erntepeak lokal reproduzierbar (k6 gegen docker-compose), damit das externe Staging-Gate nur noch Ausführung ist |

### 5.3 P2/P3 — Mittelfristig

Legacy-`:id`-Routen auf native SDs umhängen · Agent-Contract-E2E über alle 26 SDs · HR-TIME Tacho-/Telematik-Anbindung (nach externer Rechtsprüfung) · Struktur-Sprawl-Bereinigung Root-Verzeichnisse · moderate Jest/ts-jest-Transitive in `domains/inventory` (falls behalten).

### 5.4 Externe Go-Live-Gates (nicht per Code lösbar — nur vorbereitbar)

Produktive Keycloak/OIDC-Credentials · Cluster-Secrets + GitHub-Environment-Reviewer · TSE-Hardware & DSFinV-K-2.4-Prüfwerkzeugabnahme · ERiC/ELSTER-Livesubmission · zertifizierter DATEV-EXTF + Steuerberater-Cutover (SKR03/04) · Paperless-DMS-Liveprobe · Staging-Domain/DNS/TLS · Backup-/Restore-Drill (15-min RTO) · Erntepeak-Lasttest auf Staging · reale UAT-Unterschriften · AVV/DSFA/DSB-Freigabe · ArbZG-Rechtsprüfung Fahrerzeit. **Empfehlung:** Für jedes Gate einen Owner + Zieldatum in ein Freigabe-Protokoll außerhalb des Repos, wie im Runbook vorgesehen — Kapitel 8 liefert die Sequenz.

---

## 6. Agenten-Prompt-Serie: Gap-Closure

Die folgenden Prompts sind so formuliert, dass sie einzeln an einen Coding-Agenten (z. B. Claude Code) im Repo-Root übergeben werden können. Reihenfolge einhalten — A0 zuerst, da alle weiteren Prompts auf verifizierten Ist-Daten aufsetzen müssen. Jeder Prompt endet mit harten Akzeptanzkriterien und einer Evidenzpflicht (`artifacts/`).

### Prompt A0 — Verifikations-Agent (zuerst ausführen)

```
Rolle: Unabhängiger Verifikations-Agent für VALEO NeuroERP 3.0. Du traust keiner
Doku-Aussage, nur reproduzierten Ergebnissen.

Aufgaben:
1. docker compose -f docker-compose.dev.yml up -d; alembic upgrade head auf leerer DB.
2. pytest --collect-only -q (Zahl protokollieren), danach pytest -x -q Voll-Lauf
   mit --cov=app; Pass/Fail/Skip-Zahlen und Gesamt-Coverage erfassen.
3. pnpm --dir packages/frontend-web exec tsc --noEmit; pnpm build; pnpm lint.
4. python scripts/check_alembic_single_head.py, check_required_domain_schemas.py,
   check_critical_backend_coverage.py, check_toolchain_pins.py,
   check_sql_fstrings.py, check_production_readiness.py --contract-only.
5. Alle Ergebnisse gegen die Behauptungen in README und
   docs/project-context/open-gaps-and-known-issues.md diffen.

Output: artifacts/verification-report-<datum>.md mit Tabelle
Behauptung | Gemessen | Delta | Bewertung. KEINE Codeänderungen in diesem Lauf.
Akzeptanz: Jeder Claim aus README-Statusblock ist als bestätigt/widerlegt markiert.
```

### Prompt A1 — CI-Voll-Grün (SPEC-P0-01)

```
Rolle: CI-Hardening-Agent.
Aufgabe: Bringe quality-gate.yml, security-scan.yml und universal-mask-ci auf
main sichtbar grün. Analysiere die letzten fehlgeschlagenen/nie gelaufenen Runs,
behebe Ursachen (fehlende Secrets als skip-with-notice statt fail, flaky Tests
mit Retry-Markierung + Issue, echte Fehler fixen). Verboten: Tests löschen,
Schwellen senken, continue-on-error auf fachliche Gates.
Akzeptanz: 3 aufeinanderfolgende grüne Runs auf main; README-Badges verlinken
echte Runs; artifacts/ci-green-evidence.md mit Run-URLs.
```

### Prompt A2 — Repo-Hygiene & PII-Notfall (SPEC-P0-04)

```
Rolle: Security-/Datenschutz-Remediation-Agent. Höchste Priorität.
Aufgaben:
1. Inhalt von PLZ_26XXX_final_leads.json prüfen: enthält sie personenbezogene
   Daten (Namen, E-Mail, Telefon)? Ergebnis dokumentieren.
2. Datei + .tmp_changed_files.txt, .tmp_dlg01_23.txt, .tmp_dlg01_25.txt,
   .tmp_export/, tmp_playwright_mask_test/, dist/, playwright-results.json,
   evidence/screenshots (sofern reale Daten) aus dem Arbeitsbaum entfernen.
3. Git-History mit git-filter-repo für die PII-Datei bereinigen; Force-Push-Plan
   + Mitteilung an alle Clones dokumentieren.
4. .gitignore erweitern (tmp_*, dist/, *-results.json, .tmp_export/).
5. .gitleaks-baseline.json auditieren: jeden Baseline-Eintrag begründen oder
   entfernen und Finding beheben.
6. DSGVO-Bewertung schreiben: War die Lead-Datei öffentlich? Wie lange? Ist eine
   Art.-33-Meldung/Betroffeneninformation zu prüfen? → Vorlage für DSB.
Akzeptanz: Repo-Scan (gitleaks, trufflehog) 0 Funde ohne Baseline;
artifacts/pii-remediation-report.md.
```

### Prompt A3 — Runtime-Sweep als Dauergate (SPEC-P0-02)

```
Rolle: Runtime-Quality-Agent.
Aufgabe: Portiere den beschriebenen Endpoint-Sweep (tmp_endpoint_sweep.py) als
scripts/api_runtime_sweep.py: liest OpenAPI, ruft alle parameterlosen GETs mit
dev-Token + Tenant-UUID gegen frisch migrierte Compose-DB, klassifiziert
2xx/4xx-erwartet/503-by-design/5xx. 5xx > 0 => Exit 1. Whitelist für bewusste
503 aus config/runtime_sweep_allowlist.yaml, jede Ausnahme mit Begründung + Ablaufdatum.
Nightly-Workflow .github/workflows/runtime-sweep.yml.
Akzeptanz: Erster Lauf dokumentiert in artifacts/runtime-sweep-<datum>.json; 0×5xx.
```

### Prompt A4 — UIX-054/056/057 (SPEC-P1-01..03)

```
Rolle: Frontend-Release-Agent.
Aufgaben: (1) route-inventory.gen.json Generator + CI-Drift-Check (UIX-054).
(2) Playwright-Smoke über 5 repräsentative native /:id-Routen inkl. Mobile-Viewport
(UIX-056). (3) Rollback-Matrix: je kritischer Maske (Waage, POS, Ernteannahme,
Rechnung, Mahnwesen) dokumentierter + getesteter Legacy-Fallback-Pfad (UIX-057).
Akzeptanz: Alle drei als CI-Gates; docs/architecture/uix/rollback-matrix.md.
```

### Prompt A5 — Kat.-B/D-Produktionsentscheidung (SPEC-P0-03)

```
Rolle: Reliability-Agent.
Aufgabe: Inventarisiere alle Endpoints mit (a) 503-by-design und (b)
Leere-Liste-Fallback bei DB-Fehlern. Pro Modul Entscheidung herbeiführen:
AKTIV (Migration+Config Pflicht, in /readyz verdrahtet, Fallback entfernt) oder
AUS (Feature-Flag, Route in Prod-OpenAPI ausgeblendet). Harte Regel: Finance-,
Bestands- und Beleg-Endpoints dürfen bei DB-Fehlern niemals still leere Daten
liefern — dort Fallbacks durch RFC-7807-Fehler ersetzen + Alerting-Metrik.
Akzeptanz: docs/operations/module-activation-matrix.md; Regressionstests, dass
kritische Endpoints bei simuliertem DB-Fehler 5xx+Problem-Details liefern.
```

### Prompt A6 — Coverage-Offensive (SPEC-P0-05)

```
Rolle: Test-Engineering-Agent.
Regeln: Ratchet-Skript so ändern, dass Absenkungen CI-Fehler sind ("only up").
Zielpfade und Mindestwerte: financial_reports.py ≥70, sales_invoice_einvoice.py ≥70,
rohware_sammelabrechnung.py ≥70, psm_proplanta.py ≥60, portal_innendienst.py ≥60,
hrm_abwesenheit.py ≥60, kaeufergruppe.py ≥60. Tests als reine Service-Logik-Tests
(pytest -m unit), Fehlerpfade (DB-Fehler, Validierung, Tenant-Fremdzugriff) zuerst.
Verboten: triviale Assertions, Coverage durch Import-Tricks.
Akzeptanz: check_critical_backend_coverage.py grün mit neuen Schwellen;
Gesamt-Coverage ≥68 %.
```

### Prompt A7 — SQL-/Typ-Härtung (SPEC-P1-05/06)

```
Rolle: AppSec-Agent.
Aufgaben: (1) Alle 62+9 nosec-S608-Stellen listen; je Stelle nachweisen, dass
Identifier aus festen Whitelists stammen und Werte gebunden sind; wo nicht:
auf SQLAlchemy Core/parametrisierte Statements umbauen. Hypothesis-Property-Tests
mit Injection-Payloads auf die 10 exponiertesten Endpunkte. (2) Die 80 Routen
ohne response_model typisieren (Regex-Gate danach auf 0 senken).
Akzeptanz: check_sql_fstrings.py-Gate ohne neue Ausnahmen; response_model-Gate = 0;
artifacts/appsec-s608-review.md mit Stelle-für-Stelle-Verdikt.
```

### Prompt A8 — commandEndpoints & Chargen/MHD (SPEC-P1-04/08)

```
Rolle: Domain-Agent.
Aufgaben: (1) Gestubte Actions (drucken, stornieren, wareneingang, …) je
ScreenDefinition fachlich implementieren: commandEndpoint → Service → Outbox-Event
→ Audit-Eintrag; ActionPolicy (dryRun/validate/execute) respektieren.
(2) Chargen-Tiefenmodell: lot-Attribute (MHD, Herkunft, Sperrgrund, QS-Status),
FEFO über MHD statt nur Eingangsdatum, Migration idempotent am Single Head.
Akzeptanz: Kein commandEndpoint mehr als Stub (Inventur-Skript beweist es);
FEFO-Pick berücksichtigt MHD in Unit-Tests.
```

**Stand 2026-07-06:** ✅ Umgesetzt — Workboard `SPEC-P1-04-08-A8`; Inventur Exit 0; Tests `test_spec_p1_04_mask_commands.py`, `test_spec_p1_08_lot_fefo_pick.py`.

### Prompt A9 — Architektur-Konsolidierung (ARCH-F1, SPEC-P1-07)

```
Rolle: Architektur-Refactoring-Agent (nur Struktur, keine Fachlogik-Änderung).
Aufgaben: (1) Entscheidungsvorlage domains/inventory: produktiv verdrahten
(BFF-Typverträge konsolidieren, strikte tsconfig) ODER nach docs/_internal/archive
verschieben + CI-Workflows entfernen. (2) Root-Sprawl: ols/, gap/, swarm/, memory/,
mains/, l3-migration-toolkit/, guacamole-l3-migration/ je als aktiv/archiv
klassifizieren, Archiv-Kandidaten per git mv verschieben (Historie erhalten).
(3) ADR schreiben (adr-038-repo-layout.md) mit Ziel-Layout.
Akzeptanz: Root ≤ 20 Verzeichnisse; architecture-index.yaml aktualisiert;
alle CI-Gates weiter grün.
```

### Prompt A10 — Doku-Drift & Evidenzkette

```
Rolle: Evidence-Agent.
Aufgabe: Nach Abschluss A0–A9: README-Statusblock, open-gaps-and-known-issues.md
und Process-Kernel-STATUS auf gemessene Werte aktualisieren (kein Wunschstand);
release_evidence_report.py --fail-on-red ausführen und Report committen;
doc_drift_report.py --fail-over 0 grün.
Akzeptanz: Drift 0; artifacts/release_evidence.{json,md} aktuell (<24 h).
```

**Stand 2026-07-06:** ⚠️ Teilstand — Drift 0 ✅; `release_evidence` regeneriert (overall **WARN**, kein FAIL); OpenAPI/Open-Gaps/README/Process-Kernel nachgezogen. Vollständig nach A9 + CI-Assessment-Artefakt.

---

## 7. Agentisch simulierte TÜV-/ISO-/SOC-2-Prüfungen

### 7.1 Rechtliche Einordnung (wichtig)

- **ISO/IEC 27001:2022**: Zertifikat nur durch akkreditierte Stelle (z. B. TÜV SÜD/Nord/Rheinland, DEKRA). Agentische Simulation = internes Audit/Stage-1-Readiness (das ISO selbst als Pflicht-Input fordert — insofern voll verwertbar).
- **SOC 2**: Testat nur durch WP-/CPA-Gesellschaft. Type I = Design-Wirksamkeit zum Stichtag; Type II = operative Wirksamkeit über 3–12 Monate. Die Simulation erzeugt die *Evidenz- und Kontrollmatrix*, die den echten Audit-Zeitraum startklar macht.
- **"TÜV-Prüfung"** ist kein einzelner Standard; gemeint ist hier eine produkt-/betriebsbezogene technische Prüfung (Pen-Test, Lasttest, Wiederanlauf, Fail-Safe-Verhalten) nach dem Vorbild akkreditierter Prüfhäuser.
- Das Repo bringt bereits `scripts/simulate_external_assessors.py` mit 5 Profilen mit (GoBD, KassenSichV/DSFinV-K, BSI/ISO-27001, Datenschutz, Betrieb/Notfall) und dem korrekten fail-closed-Prinzip: fehlende technische Evidenz = fail, fehlende Live-Evidenz = external_gate. **Es fehlt ein SOC-2-Profil und ein maschinenlesbares Annex-A-Mapping.** Genau das schließen die folgenden Prompts.

### Prompt AUDIT-1 — ISO/IEC 27001:2022 Gap-Assessment-Agent

```
Rolle: Simulierter ISO-27001:2022-Lead-Auditor (Stage-1-Readiness). Fail-closed:
"in Doku behauptet" ohne technischen Nachweis = Nichtkonformität.
Aufgaben:
1. Erzeuge config/audit/iso27001-annex-a-matrix.yaml: alle 93 Annex-A-Controls
   (Kap. 5 Organisatorisch, 6 Personen, 7 Physisch, 8 Technologisch) mit Feldern:
   control_id, anwendbar (j/n + Begründung => Statement of Applicability),
   implementierung (Repo-Pfad/Workflow/Skript), evidenz (Artefakt), status
   (conform/minor/major/external_gate).
2. Prüfe automatisiert mindestens: A.5.15/8.3 Zugriffskontrolle (OIDC, Tenant-
   Middleware, negative Tenant-Tests), A.8.8 Schwachstellenmanagement (Trivy/
   Grype/pip-audit-Läufe + offene Highs), A.8.9 Konfigurationsmanagement
   (Preflight-Blocker), A.8.12 DLP (gitleaks + Baseline-Audit!), A.8.13 Backup
   (Restore-Drill-Protokoll vorhanden?), A.8.15/8.16 Logging/Monitoring
   (Grafana/Prometheus-Regeln), A.8.24 Kryptografie (TLS, RS256/JWKS),
   A.8.25–8.31 Secure SDLC (CI-Gates, Branch-Protection => aktuell Major-Finding),
   A.8.32 Änderungssteuerung (Review-Pflicht => aktuell Major-Finding),
   A.5.23 Cloud, A.5.29/5.30 BCM/ICT-Readiness (RTO-Drill => external_gate).
3. ISMS-Pflichtdokumente als Skeleton anlegen falls fehlend: Scope, Politik,
   Risikoregister (mit den Findings ARCH-F1..F9 als Startbestand), SoA,
   Lieferantenliste (Keycloak, Fiskaly, Paperless, DATEV, LLM-Provider!).
4. Report artifacts/audit/iso27001-readiness.{json,md}: Konformitätsgrad %,
   Major-/Minor-Liste, external_gates.
Akzeptanz: Matrix 93/93 befüllt; kein Control ohne Verdikt; LLM-/Agenten-Zugriffe
(MCP-Tools, LLM-Gateway) sind als eigenes Risiko mit Kontrollen erfasst.
```

### Prompt AUDIT-2 — SOC-2-Readiness-Agent (Trust Services Criteria)

```
Rolle: Simulierter SOC-2-Prüfer (Type-I-Readiness). Scope: Security (Pflicht) +
Availability + Confidentiality; Processing Integrity optional für Beleg-Pfade
(für ein ERP fachlich dringend empfohlen), Privacy über DSGVO-Modul abgedeckt.
Aufgaben:
1. Erzeuge config/audit/soc2-tsc-matrix.yaml über die Common Criteria CC1–CC9 +
   A-/C-/PI-Serien: je Kriterium control_activity, owner, frequenz, evidenzquelle
   (CI-Run, Log, Protokoll), automatisierbar (j/n), status.
2. Schwerpunkt-Mappings: CC6 logischer Zugriff (OIDC/JWKS, Tenant-Isolation-Gate,
   Offboarding-Prozess => fehlt vermutlich => Finding), CC7 Betrieb (Alerting,
   Incident-Runbook, Restore-Drill), CC8 Change Management (Branch-Protection,
   Reviewer, unveränderliche SHA-Images), CC9/Vendor (Subprozessoren inkl.
   LLM-Provider + AVVs), A1 Verfügbarkeit (RTO 15 min, Lasttest), C1
   Vertraulichkeit (PII-Vorfall Lead-Datei => Finding + Remediation-Verweis),
   PI1 Verarbeitungsintegrität (3-Wege-Match, GoBD-Nachweisraum, Storno-Konsistenz
   => Teststichproben über UAT-Skripte scripts/uat/*).
3. Erweitere scripts/simulate_external_assessors.py um Profil "soc2" mit
   demselben conditional/external_gate-Modell wie die bestehenden Profile.
4. Evidenz-Sammelplan für Type II: welche Artefakte müssen ab sofort monatlich
   automatisch in artifacts/audit/evidence/<jahr-monat>/ abgelegt werden
   (CI-Runs, Sweep-Reports, Restore-Protokolle, Access-Reviews).
Akzeptanz: soc2-Profil läuft in CI; Report artifacts/audit/soc2-readiness.md;
Beobachtungszeitraum-Uhr dokumentiert (Type II startet erst mit lückenloser Evidenz).
```

### Prompt AUDIT-3 — "TÜV-Style" technische Produktprüfung

```
Rolle: Simuliertes technisches Prüfhaus. Prüfling: VALEO NeuroERP 3.0 als
Gesamtsystem im docker-compose-/Helm-Stack.
Prüfblöcke (jeder Block: Prüfplan → Durchführung → Messwerte → Verdikt):
1. Penetrationstest-Light: ZAP-Baseline+Full-Scan gegen lokalen Stack (Profile
   in .zap/ nutzen/erweitern), Auth-Bypass-Versuche ohne Token/mit fremdem
   Tenant, IDOR-Stichproben über 20 kritische Routen, Rate-Limit-Verhalten.
2. Lastprüfung: k6 tests/load/harvest-peak.js lokal gegen Compose; Zielwerte
   definieren (p95-Latenz, Fehlerrate <0,1 %) und messen; Engpässe profilieren.
3. Wiederanlauf/Fail-Safe: Postgres-Kill unter Last => Verhalten (kein stiller
   Datenverlust, Outbox konsistent?); NATS-Ausfall => Dead-Letter/Retry-Nachweis;
   Backend-Pod-Kill => Helm-Selbstheilung + /readyz.
4. Fiskal-Trockenlauf: DSFinV-K-Export erzeugen und gegen Schema 2.4 validieren;
   TSE-Simulationspfad Ende-zu-Ende inkl. Tagesabschluss.
5. Migrations-Sicherheit: alembic upgrade head auf (a) leerer DB, (b) Kopie einer
   befüllten DB; downgrade-Verzicht dokumentiert => Kompensationspfad testen.
Output: artifacts/audit/technical-inspection-report.md mit Prüfblock-Verdikten
(bestanden/Auflagen/nicht bestanden) + Messdaten-Anhang.
Akzeptanz: Kein Block "nicht bestanden"; Auflagen als Issues mit Owner.
```

### Prompt AUDIT-4 — Datenschutz-/DSGVO-Tiefenprüfung

```
Rolle: Simulierter Datenschutz-Auditor (Vorbereitung DSB-Freigabe).
Aufgaben: Art.-30-Verzeichnis aus gdpr_art30_ropa live befüllen und auf
Vollständigkeit gegen tatsächliche Datenflüsse prüfen (inkl. LLM-Gateway,
WhatsApp-Kanal, Voice, TAPI-Auto-Capture — besonders heikel: Gesprächs-/
E-Mail-Capture!); Löschkonzept je domain_*-Schema (Retention-Matrix); Art.-33-
Prozess-Drill (Simulierter Breach => Meldung <72 h durchspielen, auch für den
Lead-Datei-Vorfall aus Prompt A2); DSFA-Entwurf für KIM/Auto-Capture und
KI-Funktionen; AVV-Liste aller Prozessoren.
Akzeptanz: artifacts/audit/dsgvo-audit.md; offene Punkte als external_gate
(DSB-Unterschrift) markiert, technische Lücken als Findings mit Fix-Prompt.
```

### Prompt AUDIT-5 — Audit-Orchestrator (nichts dem Zufall überlassen)

```
Rolle: Audit-Pipeline-Orchestrator.
Aufgabe: Workflow .github/workflows/audit-simulation.yml (nightly + release-
trigger): führt simulate_external_assessors.py (alle Profile inkl. neuem soc2),
api_runtime_sweep.py, release_evidence_report.py --fail-on-red und die
automatisierbaren Teile aus AUDIT-1..4 aus. Ergebnis-Aggregation in
artifacts/audit/audit-dashboard.json mit Ampel je Standard (GoBD, DSFinV-K,
ISO 27001, SOC 2, DSGVO, Technik) und Trend zur Vorwoche. Jede Verschlechterung
=> Workflow rot. External_gates werden gelistet, nie als "bestanden" gewertet.
Akzeptanz: Dashboard generiert; Release-Gate konsumiert es; Doku im Runbook
verlinkt.
```

---

## 8. Empfohlene Sequenz (30/60/90)

**Tage 0–30 (Stabilisieren & Absichern):** A0 Verifikation → A2 PII-Notfall (parallel, sofort) → A1 CI-Grün → SPEC-P0-06 Branch-Protection/CODEOWNERS → A3 Runtime-Sweep-Gate → A5 Modul-Aktivierungsmatrix. Parallel Ops: Staging-Domain/DNS/TLS, Cluster-Secrets, Keycloak-Prod-Realm beauftragen.

**Tage 30–60 (Härten & Auditieren):** A6 Coverage-Offensive → A7 AppSec-Review → AUDIT-1/2/4 Matrizen + Findings → AUDIT-3 technische Prüfung lokal → SPEC-P0-08 Restore-Drill-Vorbereitung → Ops führt ersten Backup-/Restore-Drill und Erntepeak-Lasttest auf Staging durch.

**Tage 60–90 (Go-Live-Fenster):** A4 UIX-Release-Gates → A8 commandEndpoints/Chargen → AUDIT-5 Dashboard dauerhaft → externe Abnahmen einsammeln (DATEV-Testimport, DMS-Liveprobe, TSE/DSFinV-K, UAT-Unterschriften, DSB) → Release nach kanonischem Pfad (quality-gate → security-scan → staging → manuelles Prod-Deployment mit Reviewer, SHA-gepinnt).

**Danach:** SOC-2-Type-II-Evidenzuhr läuft (min. 3 Monate lückenlos), ISO-27001-Stage-1 mit akkreditierter Stelle terminieren, A9 Struktur-Konsolidierung, P2/P3-Backlog.

---

## 9. Schlussbemerkung

Das Projekt hat eine für seine Entstehungsweise ungewöhnlich reife Governance-Substanz (fail-closed-Prinzip, Evidenz-Gates, simulierte Prüfer). Der Weg zu "production ready" ist deshalb kein Neubau, sondern ein **Beweis-Programm**: verifizieren statt behaupten, PII-Risiko sofort schließen, CI öffentlich grün, Fallbacks in Fehlerpfade verwandeln, Coverage nur noch aufwärts — und die externen Gates mit Ownern und Terminen versehen. Die Prompts in Kapitel 6 und 7 sind darauf ausgelegt, genau diese Beweiskette agentisch und wiederholbar zu erzeugen.
