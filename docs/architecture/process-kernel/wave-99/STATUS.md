# Wave 99 — Gap-Closure: Process Mining, Command Monitor, Policy Explainability, Agent UX, Design Tokens

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-22
**TypeScript:** 0 Fehler

## Gap 018 — Ereignisbasierte Prozessbeobachtung (Process Mining Drilldown)

### `lib/api/process-mining.ts` (NEU)
- `useProcessMiningTopProcesses(limit)` → `GET /api/v1/process-mining/finance/top-processes?limit=N`
- `useProcessMiningBottlenecks()` → `GET /api/v1/process-mining/finance/bottlenecks`
- `useProcessMiningDrilldown(key)` → `GET /api/v1/process-mining/finance/drilldown/{key}`
- `useIdempotencyOverview()` → `GET /api/v1/admin/idempotency-overview`
- Typen: `ProcessSummary`, `ProcessBottleneck`, `ProcessMiningDrilldown`, `ProcessMiningReport`

### `pages/workflow/process-mining-analytics.tsx` (NEU)
- Vollständige Process-Mining-Seite mit:
  - Stats-Cards: Prozesse, Ausführungen, Engpässe gesamt, Kritische Engpässe
  - Top-Prozesse-DataTable mit Klick → Drilldown-Panel
  - Drilldown: SLA-Ziel, SLA-Einhaltung %, Step-by-Step mit Bottleneck-Highlighting
  - Engpass-DataTable mit Schwere-Badge, Empfehlung, Typ-Badge
- `AgentProcessPanel domain="workflow"` nach Header
- Keyboard: Ctrl+F, F5 → refetch, `KeyboardShortcutBar`

### Nav + Route-Alias
- `core.tsx`: neuer Eintrag `process-mining-analytics` unter Workflow
- `route-aliases.json`: `workflow/process-mining-analytics`

---

## Gap 016 — Idempotente Business-Commands Monitoring

### `pages/admin/command-monitor.tsx` (NEU)
- Vollständiger Command Monitor mit `IdempotencyMonitoringPanel` (echte API-Daten)
- Loading/Error/Empty States für `useIdempotencyOverview()`
- Aggregate & Commands Detail-Panel (alle überwachten Typen)
- Keyboard: F5 → refetch, `KeyboardShortcutBar`

### Nav + Route-Alias
- `core.tsx`: neuer Eintrag `command-monitor` unter Administration
- `route-aliases.json`: `admin/command-monitor`

---

## Gap 019 — Policy Explainability im UI

### `pages/workflows/approval.tsx` (erweitert)
- `useQuery` für `GET /api/v1/policies/explain/workflow/{workflowId}`
- `PolicyExplanationBadge` mit `showDetails` in separatem "Policy-Kontext"-Card
- Zeigt: Entscheidung (Freigegeben/Abgelehnt/Warnung/Eskalation), Zusammenfassung, entscheidende Regeln, Regelanzahl
- Erscheint oberhalb des Freigabe-Formulars wenn Daten verfügbar
- Import: `PolicyExplanationData` Typ + `apiClient` für fetch

---

## Gap 029 — Agent UX Panel Integration

### `components/agent/index.ts` (erweitert)
- `AgentUxPanel` + `AgentUxPanelProps/AgentUxSource/AgentUxAction` jetzt re-exportiert
- `IdempotencyMonitoringPanel` + `IdempotencyOverview/IdempotencyMonitoringPanelProps` re-exportiert

### `pages/workflows/supervisor.tsx` (erweitert)
- `AgentUxPanel` eingefügt zwischen Freigabe-Sektion und "Alle Runs"-Tabelle
- Confidence = Erfolgsrate aller Runs (completed / total × 100)
- 3 Quellen: Capability-Registry, Workflow-Runs API, Idempotency-Store
- Aktion: → `/admin/command-monitor` öffnen

---

## Gap 021 — Einheitliches Designsystem

### `lib/design-tokens.ts` (NEU)
- `colors`: success/warning/error/info/neutral/agent je mit bg/border/text/badge
- `spacing`: xs→2xl + pageInset/cardInset
- `typography`: pageTitle/sectionTitle/cardTitle/metricValue/mono/label
- `breakpoints`: sm/md/lg/xl/2xl
- `touch`: minTarget (44x44dp), buttonLg, inputLg (Gap 024-Vorbereitung)
- `maskComponents`: Status-Matrix aller Mask-Builder-Komponenten
- `agentUx`: UI-Konventionen für assisted/productive/background

---

## Route-Aliases (alle neuen Seiten)

| Pfad | Modul |
|------|-------|
| `finance/skonto-optimizer` | `@/pages/finance/skonto-optimizer` |
| `workflows/supervisor` | `@/pages/workflows/supervisor` |
| `admin/data-quality` | `@/pages/admin/data-quality` |
| `qualitaet/ausnahmen` | `@/pages/qualitaet/ausnahmen` |
| `workflow/process-mining-analytics` | `@/pages/workflow/process-mining-analytics` |
| `admin/command-monitor` | `@/pages/admin/command-monitor` |

---

## Gap-Status nach Wave 99

| Gap | Titel | Status |
|-----|-------|--------|
| 016 | Idempotente Commands + Monitoring | ✅ CLOSED — Command Monitor live |
| 018 | Process Mining Drilldown | ✅ CLOSED — Analytics-Seite + Drilldown |
| 019 | Policy Explainability im UI | ✅ CLOSED — PolicyExplanationBadge in Approval-Flow |
| 021 | Einheitliches Designsystem | ✅ CLOSED — Design Tokens + Komponent-Matrix |
| 029 | Agent UX Panel (Confidence/Sources) | ✅ CLOSED — AgentUxPanel in Supervisor |
| 023 | Keyboard-first (≥90% Abdeckung) | ✅ CLOSED — Wave 95-98 lieferten alle Kern-Masken |
| 002 | Waage/Annahme-Masken vollständig | ✅ CLOSED — Wave cd6bb848 |
| 043 | EDI/API Hub | ✅ CLOSED — Wave 36 |
| 049 | Security Hardening | ✅ CLOSED — Wave 34 |

Offen (ausserhalb Frontend-Scope):
| Gap | Titel | Grund |
|-----|-------|-------|
| 024 | Touch-optimierte Feldworkflows | Benötigt echte Device-Tests + UX-Audit |
| 037 | Lasttests Erntepeak | Benötigt Lasttest-Infrastruktur (k6/Locust) |
