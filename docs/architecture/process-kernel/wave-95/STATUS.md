# Wave 95 — Keyboard/Agent-Rollout P1/P2-Listen (Verladungen, LstKontraktUebersicht, CommodityPositionMatrix)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-20
**Tests:** 69 grün, 0 Fehler
**TypeScript:** 0 Fehler

## Geänderte Dateien

### `pages/verladung/liste.tsx`
- `useRef` + `searchInputRef` für Suchfeld
- `buildCoreMaskShortcuts({ onNew, onSearch, onRefresh })` + `useKeyboardShortcuts`
- Ctrl+N → `navigate('/verladung/lkw-beladung')`
- Ctrl+F → Focus auf Suchfeld
- F5 → `refetch()`
- `AgentProcessPanel domain="lager"` nach Header-Zeile
- `ref={searchInputRef}`, `aria-label`, `min-h-touch` auf Search-Input
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>`

### `pages/kontrakte/LstKontraktUebersicht.tsx`
- `useRef` + `matchcodeRef` für Matchcode-1-Feld
- `buildCoreMaskShortcuts({ onNew, onSearch, onRefresh })` + `useKeyboardShortcuts`
- Ctrl+N → `navigate('/kontrakte/neu')`
- Ctrl+F → Focus auf Matchcode-1-Feld (`matchcodeRef`)
- F5 → `query.refetch()`
- `ref={matchcodeRef}` auf Matchcode-1-Input
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>`

### `pages/disposition/LstCommodityPositionMatrix.tsx`
- `useRef` + `articleFilterRef` für Artikel-Filter-Input
- `buildCoreMaskShortcuts({ onRefresh, onSearch })` + `useKeyboardShortcuts`
- F5 → `handleRefresh()` (refreshSnapshot + matrixQuery/kpiQuery refetch)
- Ctrl+F → Focus auf Artikel-Filter-Feld
- `AgentProcessPanel domain="einkauf"` nach Header-Zeile (Disposition feeds Einkauf-Domäne)
- `ref={articleFilterRef}` auf Artikel-Input
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>`

## Agentic Workflow Rollout-Stand nach Wave 95

| Domäne | Seite | Agent-Panel | Agent-Suggestion | Keyboard |
|--------|-------|-------------|------------------|----------|
| Annahme | rohware.tsx | ✓ | ✓ rohware_annahme_assistant | ✓ |
| Annahme | lkw-registrierung.tsx | — | — | ✓ |
| Annahme | qualitaets-check.tsx | — | — | ✓ |
| Annahme | abrechnung.tsx | — | — | ✓ |
| Lager | einlagerung.tsx | ✓ | ✓ einlagerung_assistant | ✓ |
| Lager | auslagerung.tsx | ✓ | ✓ auslagerung_assistant | ✓ |
| Lager | inventur.tsx | — | — | ✓ |
| Waage | wiegungen.tsx | — | — | ✓ |
| Waage | wiegeschein-detail.tsx | — | — | ✓ |
| Verladung | lkw-beladung.tsx | ✓ | — | ✓ |
| Verladung | liste.tsx | ✓ | — | ✓ |
| Einkauf | bestellvorschlag-lager.tsx | ✓ | — | ✓ |
| Disposition | liste.tsx | ✓ | — | ✓ |
| Disposition | LstCommodityPositionMatrix.tsx | ✓ | — | ✓ |
| Kontrakte | FrmKontraktDetail.tsx | — | — | ✓ |
| Kontrakte | LstKontraktUebersicht.tsx | — | — | ✓ |
| Workflows | supervisor.tsx | ✓ | — | ✓ |
