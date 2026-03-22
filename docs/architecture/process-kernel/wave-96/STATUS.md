# Wave 96 — Keyboard-Rollout FrmCoverageMonitor + Skonto-Optimizer (neue KI-Seite)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-20
**Tests:** 69 grün, 0 Fehler
**TypeScript:** 0 Fehler

## Geänderte Dateien

### `pages/disposition/FrmCoverageMonitor.tsx`
- `buildCoreMaskShortcuts({ onRefresh, onCancel })` + `useKeyboardShortcuts`
- F5 → `refetch()`
- Escape → `navigate('/disposition')`
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>`

## Neue Dateien

### `pages/finance/skonto-optimizer.tsx` (NEU)
- Vollständige KI-gestützte Skonto-Optimierungsseite
- Lädt offene Kreditoren-Posten (`GET /api/v1/finance/open-items?typ=kreditoren`)
- Filtert Posten mit aktiver Skontofrist (≤ 14 Tage bis Fälligkeit)
- `AgentSuggestionBadge` mit `skonto_optimizer` Capability (productive readiness)
  - Agent-Parameter: `item_count`, `total_offen`, `heute_ablaufend`
  - Suggest-Fields: `zahlungsbetrag`, `valutatag`
  - `onAccept` → Empfehlung wird als Card dauerhaft angezeigt
- `AgentProcessPanel domain="finanzen"` — zeigt laufende Finance-Agent-Aktivität
- Stats-Cards: Skonto-Posten, Skonto-Potenzial (2%-Estimate), heute ablaufend
- DataTable mit Fälligkeits-Badge (rot ≤ 3d, gelb ≤ 7d) und Skonto-Betrag-Spalte
- Keyboard: Ctrl+F → Suche, F5 → refetch, Escape → navigate('/finance/op-kreditoren')
- `KeyboardShortcutBar` + Wrapper-Pattern

### Navigation: `app/navigation/domains/finance.tsx`
- `Zap` Icon importiert
- Neuer Nav-Eintrag `skonto-optimizer` nach `op-kreditoren-finance`:
  - Label: "Skonto-Optimierung (KI)"
  - Icon: Zap
  - Keywords: skonto, optimizer, ki, agent, zahlung, fälligkeit, liquidität
  - `preferredPath: 'finance/skonto-optimizer'`

## Agentic Workflow Rollout-Stand nach Wave 96

| Domäne | Seite | Agent-Panel | Agent-Suggestion | Keyboard |
|--------|-------|-------------|------------------|----------|
| Annahme | rohware.tsx | ✓ | ✓ rohware_annahme_assistant | ✓ |
| Lager | einlagerung.tsx | ✓ | ✓ einlagerung_assistant | ✓ |
| Lager | auslagerung.tsx | ✓ | ✓ auslagerung_assistant | ✓ |
| Verladung | lkw-beladung.tsx | ✓ | — | ✓ |
| Verladung | liste.tsx | ✓ | — | ✓ |
| Einkauf | bestellvorschlag-lager.tsx | ✓ | — | ✓ |
| Disposition | liste.tsx | ✓ | — | ✓ |
| Disposition | LstCommodityPositionMatrix.tsx | ✓ | — | ✓ |
| Disposition | FrmCoverageMonitor.tsx | — | — | ✓ |
| Finance | skonto-optimizer.tsx | ✓ | ✓ skonto_optimizer (productive) | ✓ |
| Kontrakte | FrmKontraktDetail.tsx | — | — | ✓ |
| Kontrakte | LstKontraktUebersicht.tsx | — | — | ✓ |
| Workflows | supervisor.tsx | ✓ | — | ✓ |
