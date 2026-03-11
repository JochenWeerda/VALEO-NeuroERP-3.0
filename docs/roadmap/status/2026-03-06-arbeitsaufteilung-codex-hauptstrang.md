# VALEO Spitzenposition – Arbeitsaufteilung Codex vs. Hauptstrang

**Stand:** 2026-03-08  
**Zweck:** Gegenseitige Kontrolle, Vermeidung von Doppelarbeit, klare Verantwortlichkeiten

---

## Übersicht

| Strang | Anteil | Aufgaben | Verantwortlich |
|--------|--------|----------|----------------|
| **Codex (Parallel Chat)** | 30 % | 15 von 50 (IDs siehe unten) | GPT-5.3 Codex |
| **Hauptstrang** | 70 % | 35 von 50 | Aktueller Chat/Team |

**Einheitliches Steuerungsdokument:** Dieses Dokument. Beide Stränge aktualisieren hier den Status.

**Strategische Leitplanke:** [target-state-landhandel-erp.md](../../architecture/target-state-landhandel-erp.md) – Zielbild für Domänenmodell, Action-Layer und Workflow-/Policy-Kern.

---

## Codex-Strang (30 % – 15 Aufgaben)

Tasks mit geringerer Abhängigkeit vom Kern-Architektur-Pfad, überwiegend Frontend, API-Client, Validierung, i18n, Dokumentation.

| ID | Gap | Aufwand | KPI-Ziel | Hinweis für Codex |
|----|-----|---------|----------|-------------------|
| **005** | Saisonale Kampagnenprozesse (Erntefenster) als Vorlagen | S | Setup-Zeit <30 min | Workflow-Templates, Konfig-UI |
| **019** | Policy Explainability im UI (Warum freigegeben/blockiert) | S | -50 % Support-Rückfragen | Frontend-Komponente für Policy-Begründung |
| **022** | Command Palette (Ctrl/Cmd+K) für Power User | S | +30 % schneller | Bestehende Palette erweitern, Shortcuts vervollständigen |
| **025** | Kontextsensitive Quick Actions pro Maske | S | -25 % Klicks | Action-Registry, PageToolbar-Integration |
| **026** | Inline-Validierung mit domain-spezifischen Erklärungen | S | -35 % Eingabefehler | Validation Layer, Fehlermeldungen |
| **028** | Leitsystem für Ausnahmefälle (Error UX) | S | -50 % Abbruchquote | Error Boundaries, Retry/Recovery-UI |
| **029** | Agent UX Panel (Confidence, Quellen, Aktion) | M | AI-Adoption ≥60 % | Copilot UI, Erklärbarkeit |
| **030** | Multilingual + Fachsprache Landhandel konsistent | M | 0 Begriffsinkonsistenzen | i18n-Katalog, Terminologie |
| **031** | Query-Verträge härten (nie undefined für Query Data) | S | 0 React Query undefined | API Client, Schemas, Fallbacks |
| **034** | API-Bulk-Operationen für Massenvorgänge | M | 3× Throughput | Batch-Endpoints, Chunking |
| **040** | Datenqualitätsregeln (Dublette, Pflichtfeld, Referenz) | M | -50 % Stammdatenfehler | MDM-Regeln, Validierungs-Service |
| **046** | Nachhaltigkeit/CO2 Reporting für Agrarkonzerne | M | ESG-Berichte <1 Tag | Sustainability-Bericht, Export |
| **047** | Branchenbenchmarking Cockpit je Genossenschaft | M | Monatlicher Benchmark automatisch | Analytics Mart, Dashboard |
| **048** | Offene Integrationsfähigkeit für Agenten (Perplexity etc.) | M | 10 Agent-Use-Cases live | MCP-Tools, OpenAPI, Security |
| **012** | Simulation/Sandbox für neue Workflows | M | -80 % Fehler nach Go-Live | Testdaten, Sandbox-Mode |

### Codex-Status (wöchentlich aktualisieren)

| ID | Status | Letzte Aktualisierung |
|----|--------|----------------------|
| 005 | erledigt (Erntefenster-Vorlagen in `process_config`; API `/admin/erntefenster-templates`; Konfig-UI `agrar/erntefenster-konfig`) | 2026-03-07 |
| 012 | erledigt (Sandbox-Preview fuer Prozessvarianten + saisonale Kampagnen via `/admin/workflow-sandbox/preview`; UI `workflow/workflow-sandbox`; Deep-Link aus `agrar/erntefenster-konfig`; JSON-Export fuer Review/Audit) | 2026-03-07 |
| 019 | erledigt (Policy-Explainability in `PolicyBadge`: Status + Begründung + Regel/Freigabe-Details via `buildDecisionView`) | 2026-03-07 |
| 022 | erledigt (Manifest-Shortcuts + Action-Hotkeys `Ctrl+Alt+N/R/B/E` + Anzeige in Palette) | 2026-03-07 |
| 025 | erledigt (Quick-Action-Integration in `ListReport`/`ObjectPage`/`OverviewPage`/`Wizard`; `PageToolbar` + `ActionDispatchContext` fuer Voice/Palette/Agent) | 2026-03-07 |
| 026 | erledigt (`FormBuilder`/`validator`: Pflichtfeldpruefung + fachliche Validierungshinweise) | 2026-03-07 |
| 028 | erledigt (zentrale Recovery-UI in `ErrorState` + `ErrorBoundary` + Router-Fallbacks mit Retry/Reload/Home) | 2026-03-07 |
| 029 | erledigt (`AskValeo`: Konfidenz, Quellen, Folgeaktion via `ActionDispatchContext`) | 2026-03-07 |
| 030 | erledigt (Terminologie in Shared-UX: `ErrorState`, `FormBuilder`, `policy/decision-view`) | 2026-03-07 |
| 031 | erledigt (Query-Hooks mit `initialData`; `useActionsForMask` fallback; Page-Queries gehaertet inkl. Inventory/Start/Finance/FiBu/Admin/CRM-Listen) | 2026-03-07 |
| 034 | erledigt (Bulk-Delete `agrar/feldbuch/massnahmen` via `/api/v1/agrar/feldbuch/massnahmen/bulk-delete`; Frontend `agrar/feldbuch/massnahmen` mit Auswahl + Chunking; zusaetzlich echte Bulk-Delete-Endpoints fuer `futter/einzelfuttermittel` und `futter/mischfuttermittel`) | 2026-03-07 |
| 040 | erledigt (MDM-Regeln in `data_quality_rules.py`; API `/admin/data-quality/rules`, `/validate`; UI `admin/data-quality` unter Administration) | 2026-03-07 |
| 046 | erledigt (ESG-Report: Backend `sustainability.py` mit N/P2O5/CO2e-Aggregation; Frontend `esg-report.tsx` + API-Hooks; CSV/PDF-Export; Nav unter Compliance) | 2026-03-07 |
| 047 | erledigt (Benchmark-Cockpit: API `/analytics/benchmark` mit eigenen KPIs + Branchenreferenz; UI `controlling/benchmark-cockpit` unter Controlling) | 2026-03-07 |
| 048 | teilweise (Admin-Seite `admin/agenten-integration`, docs/AGENT-INTEGRATION.md, Agent-Manifest `/api/v1/admin/agent-manifest`; MCP-Server/Security Hauptstrang) | 2026-03-08 |

---

## Hauptstrang (70 % – 35 Aufgaben)

Kernprozesse, Workflow-Engine, Backend-Architektur, Compliance, Performance-Kern.

| IDs | Bereich |
|-----|---------|
| **001–004, 006–011, 013–018, 020** | Prozessabdeckung, Workflow, Policy, Agent-Backend |
| **021, 023–024, 027** | Designsystem-Kern, Keyboard, Touch |
| **032–033, 035–039** | 500er-Fixes, Read-Models, Locking, Jobs, Lasttests, Tracing |
| **041–045, 049–050** | GoBD, Intrastat, EDI, DMS, Security, SLO/Runbooks |

### Hauptstrang-Status (wöchentlich aktualisieren)

| Wave | Hauptstrang-IDs (Implementierung) | Codex-IDs (Parallel) | Status |
|------|----------------------------------|----------------------|--------|
| A | 001, 002, 003, 009, 010, 011, 013, 014, 032 | 031 | 001 E2E Qualitäts-Check→Abrechnung erledigt (2026-03-07), 032 erledigt (2026-03-06), 002 LKW-DB erledigt (2026-03-06), 003 Drying-Integration erledigt (2026-03-07), 009 Prozessvarianten-API erledigt (2026-03-07), 010 Audit-Hash-Kette erledigt (2026-03-07), 013 SLA/Timeout/Eskalation in process_config erledigt (2026-03-07), 014 Policy-Overrides (Tenant) erledigt (2026-03-07) |
| B | 004, 015, 021, 024, 033, 035, 039 | 019, 022, 025 | offen |
| C | 036, 041, 042, 049, 050 + Vorbereitung 016, 037, 043 | – | offen |

---

## Schnittstellen und Abhängigkeiten

| Codex-Task | Hauptstrang-Abhängigkeit |
|------------|---------------------------|
| 019 Policy Explainability | Policy-API und Audit-Format müssen vom Hauptstrang bereitstehen |
| 025 Quick Actions | Action-Registry-Schema vom Hauptstrang |
| 029 Agent UX Panel | Agent-Layer/Bestellvorschlag vom Hauptstrang |
| 031 Query-Verträge | API-Contract-Änderungen abstimmen |
| 034 API-Bulk | Bulk-Endpoint-Spezifikation vom Hauptstrang |
| 048 Agenten-Integration | MCP-Server, Security vom Hauptstrang |

**Abstimmregel:** Bei Schnittstellen-Änderungen zuerst in diesem Dokument vermerken, dann im jeweiligen Strang umsetzen.

---

## Wöchentliches Sync (Freitag)

1. **Codex** trägt Erledigtes in „Codex-Status“ ein (ID, Status, Commit/Link).
2. **Hauptstrang** trägt Wave-Fortschritt in „Hauptstrang-Status“ ein.
3. **Konflikte/Blockaden** in Abschnitt „Offene Punkte“ eintragen.

### Offene Punkte

| Datum | Thema | Strang | Status |
|-------|--------|--------|--------|
| – | – | – | – |

---

## Nächste Schritte (Codex)

**Priorität für nächste offene Aufgabe:** Keine – alle Codex-Tasks erledigt bzw. 048 vorbereitet.

- **048** (Agenten-Integration): Codex-Teil erledigt (Admin-Seite, Dokumentation). MCP-Server und Security bleiben beim Hauptstrang.

### Wave B – Codex-Unterstützung (2026-03-08)

| ID | Beitrag | Details |
|----|---------|---------|
| 021 | Designsystem | docs/DESIGNSYSTEM.md: Pattern-Katalog, Komponenten-Regeln |
| 024 | Touch-Optimierung | CSS `--touch-target: 44px`, Tailwind `min-h-touch`/`min-w-touch` |
| 015 | AI-Freigaben | Admin-Seite `admin/ai-approvals` (Frontend-Stub; API-Integration Hauptstrang) |

### Zusätzlich erledigt (Infrastruktur)

| Datum | Thema | Details |
|-------|--------|---------|
| 2026-03-08 | Build-Fix (Windows) | pnpm-Override `rollup → @rollup/wasm-node` in Root-`package.json` (Workaround für fehlendes `@rollup/rollup-win32-x64-msvc` unter Windows) |
| 2026-03-08 | lagerplaetze.tsx | JSX-Syntax: Fragment `<>...</>` um zwei Root-Elemente ergänzt; Template-Literale für `} / {`-Interpolationen (esbuild „Unterminated regex“ behoben) |
| 2026-03-10 | Frontend-Routing-Integritaet | Main- und Portal-Runtime auf gemeinsamen Alias-Matcher vereinheitlicht; `page-module-loader` um Portal-Gruppe erweitert; Vollcheck fuer Route-/Alias-/Page-Mapping ohne offene Treffer; Unknown-Module-Fehler im Frontend-Resolver behoben. |


---

## Referenzen

| Dokument | Pfad |
|----------|------|
| Top-50 Gap Backlog | [2026-03-06-top-50-gap-backlog-landhandel.md](2026-03-06-top-50-gap-backlog-landhandel.md) |
| Konsolidierte Strategie | [2026-03-06-valeo-spitzenposition-konsolidiert.md](2026-03-06-valeo-spitzenposition-konsolidiert.md) |
| Target State Landhandel ERP | [../../architecture/target-state-landhandel-erp.md](../../architecture/target-state-landhandel-erp.md) |
| ADR-003 Canonical Domain Model | [../../adr/adr-003-canonical-domain-model.md](../../adr/adr-003-canonical-domain-model.md) |
| ADR-004 Command-/Action-Layer | [../../adr/adr-004-command-action-layer.md](../../adr/adr-004-command-action-layer.md) |
| ADR-005 Workflow-/Policy-Kern | [../../adr/adr-005-workflow-policy-kern.md](../../adr/adr-005-workflow-policy-kern.md) |
