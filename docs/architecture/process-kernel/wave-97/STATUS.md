# Wave 97 — Compliance-Domain Keyboard/Agent-Rollout (QS-Checkliste, Cross-Compliance, Meldewesen-Konsole)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-20
**Tests:** 69 grün, 0 Fehler
**TypeScript:** 0 Fehler

## Geänderte Dateien

### `pages/compliance/qs-checkliste.tsx`
- `buildCoreMaskShortcuts({ onRefresh })` + `useKeyboardShortcuts`
- F5 → `refetch()`
- `AgentProcessPanel domain="compliance"` nach Header
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>`

### `pages/compliance/cross-compliance.tsx`
- `refetch` aus `useCrossCompliance()` destrukturiert
- `buildCoreMaskShortcuts({ onRefresh })` + `useKeyboardShortcuts`
- F5 → `refetch()`
- `AgentProcessPanel domain="compliance"` nach Header
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>`

### `pages/compliance/meldewesen-konsole.tsx`
- `buildCoreMaskShortcuts({ onRefresh })` + `useKeyboardShortcuts`
- F5 → alle 4 refetch() (connectors, reportingUnits, schedules, jobs)
- `AgentProcessPanel domain="compliance"` nach Export/Import-Header-Zeile
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>`

## Agentic Workflow Rollout-Stand nach Wave 97

| Domäne | Seite | Agent-Panel | Keyboard |
|--------|-------|-------------|----------|
| Compliance | qs-checkliste.tsx | ✓ compliance_copilot domain | ✓ |
| Compliance | cross-compliance.tsx | ✓ compliance_copilot domain | ✓ |
| Compliance | meldewesen-konsole.tsx | ✓ compliance_copilot domain | ✓ |
| Finance | skonto-optimizer.tsx | ✓ skonto_optimizer | ✓ |
| Disposition | LstCommodityPositionMatrix.tsx | ✓ einkauf domain | ✓ |
| Disposition | FrmCoverageMonitor.tsx | — | ✓ |
| Lager | einlagerung.tsx | ✓ einlagerung_assistant | ✓ |
| Lager | auslagerung.tsx | ✓ auslagerung_assistant | ✓ |
| Annahme | rohware.tsx | ✓ rohware_annahme_assistant | ✓ |
| Verladung | lkw-beladung.tsx | ✓ lager domain | ✓ |
| Workflows | supervisor.tsx | ✓ all domains | ✓ |
