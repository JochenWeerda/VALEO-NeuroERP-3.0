# Wave 93 — Agentic Workflow UI (systemweite Rollout)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-20
**Tests:** 66 grün (Frontend Vitest), 0 Fehler (3 pre-existing failures unverändert)
**TypeScript:** 0 Fehler

## Strategischer Kontext

Kernfluss-Seiten sind die strukturelle Grundlage für agentenbasierte ERP-Prozesse.
Erst wenn Prozesse als Wizard-Schritte sichtbar sind, können AI-Agenten sinnvoll:
- Entscheidungen vorschlagen (Artikel, Lagerort, Strategie)
- Schritte automatisch ausführen (Buchung, Allokation)
- Ausnahmen eskalieren und Freigaben anfordern

```
Masken-ERP → Prozess-ERP (Kernfluss) → Agentic ERP
UI         → Workflow               → Agent
```

## Neue Dateien

### `src/lib/agentCapabilities.ts`
Zentrale Capability-Registry: 8 Capabilities (productive/assisted/prototype)
- Domain-Mapping: einkauf, annahme, lager, finanzen, compliance, stammdaten, operations
- Exports: `getCapabilityByKey()`, `getCapabilitiesForDomain()`, `getProductiveCapabilities()`

### `src/hooks/useAgentSuggestion.ts`
Generischer Hook: Trigger → Poll → Accept/Dismiss
- POST `/api/v1/agents/neuroassist/runs` → run_id
- Polls `/api/v1/agents/neuroassist/runs/{run_id}` alle 2s bis completed/rejected
- Rückgabe: `{ suggestion, isLoading, status, trigger, accept, dismiss, reset }`
- Status-Typ: `'idle' | 'loading' | 'ready' | 'accepted' | 'dismissed' | 'error'`

### `src/components/agent/AgentSuggestionBadge.tsx`
Inline-Komponente für Wizard-Schritte:
- Violett-Card mit "Analysieren"-Button (on demand)
- Bei Ready: Vorschlag + "Übernehmen" / "X" Buttons
- Generic `<T>`: `renderSuggestion(T)`, `onAccept(T)` — typsicher für jeden Prozess
- autoTrigger-Option für automatische Aktivierung

### `src/components/agent/AgentProcessPanel.tsx`
SSE-basiertes Echtzeit-Panel:
- Abonniert `MCPEvent` mit `topic === 'agent'`
- Domain-Filter: agentId muss Domain-String enthalten
- Zeigt Feed: started/running (Sparkles, pulsierend), done (CheckCircle), error (AlertCircle)
- Rendert null wenn keine Aktivität (zero-impact für inaktive Agents)

### `src/components/agent/index.ts`
Barrel-Export: `AgentSuggestionBadge`, `AgentProcessPanel`

### `src/pages/workflows/supervisor.tsx`
Process Supervisor — neue Seite unter `/workflows/supervisor`:
- Statistik-Cards: Freigaben ausstehend / Aktive Runs / Abgeschlossen / Gesamt
- AgentProcessPanel für systemweite Echtzeit-Aktivität
- Tabelle aller Runs mit Status-Badges und Inline-Freigabe
- Pending-Approval-Karten: Direkte Approve/Reject ohne Seitenwechsel
- Keyboard: F5 = Refresh, Escape = Zurück

## Backend-Erweiterung

### `app/api/v1/endpoints/agents.py`
Neuer Endpoint: `GET /api/v1/agents/neuroassist/runs`
- Query-Parameter: `status` (optional Filter), `limit` (default 50)
- Graceful Fallback: AttributeError → leere Liste (ServiceImpl optional)
- Alle anderen Fehler → leere Liste mit Logging

### `src/lib/api/workflows.ts`
Neuer Hook: `useListRuns(statusFilter?: string)`
- Query-Key: `['workflows', 'list', status]`
- Refetch-Interval: 10s (Supervisor-Polling)
- Typ: `RunListItem[]`

## Kernfluss-Seiten mit Agent-Integration

| Seite | AgentProcessPanel | AgentSuggestionBadge | Felder |
|-------|-------------------|----------------------|--------|
| `annahme/rohware.tsx` | ✓ domain=annahme | ✓ rohware_annahme_assistant | artikel, lagerZiel |
| `lager/auslagerung.tsx` | ✓ domain=lager | ✓ auslagerung_assistant | strategie, chargenId |
| `lager/einlagerung.tsx` | ✓ domain=lager | ✓ einlagerung_assistant | lagerort, lagerplatz |
| `verladung/lkw-beladung.tsx` | ✓ domain=lager | — | — |

## Navigation

Neuer Eintrag in `domains/core.tsx` unter Workflows:
- `workflow-supervisor` → `/workflows/supervisor`
- Keywords: supervisor, agent, prozess, agentic, ki, oversight

## Reifegradmodell

```
Masken-ERP       → Stufe 1: Nutzer klickt Screens
Prozess-ERP      → Stufe 2 (Wave 91/92): Kernfluss-Seiten + Keyboard/Touch ✓
Agentic ERP      → Stufe 3 (Wave 93): Agent schlägt vor, Mensch supervisiert ✓
```

## Architekturentscheidungen

- **SSE-Integration**: `useSSE()` Hook auf `MCPEvent` (topic='agent') — keine eigene SSE-Verbindung
- **Domain-Filter**: `agentId.includes(domain)` — Convention: agentId muss Domain-Prefix tragen
- **Generic Types**: `AgentSuggestionBadge<T>` mit `renderSuggestion` + `onAccept` Callbacks — typsicher ohne Casting in Pages
- **Graceful-Zero-Impact**: `AgentProcessPanel` rendert null wenn keine Aktivität → kein leerer Raum auf nicht-aktiven Seiten
- **Accept/Dismiss Pattern**: Agent-Vorschlag füllt Felder, überschreibt nichts ohne explizite Nutzeraktion
