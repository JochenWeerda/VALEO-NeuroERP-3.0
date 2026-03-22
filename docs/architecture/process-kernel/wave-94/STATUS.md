# Wave 94 — Keyboard/Agent-Rollout P1-Seiten (Kontrakte, Disposition, Bestellvorschlag)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-20
**Tests:** 66 grün, 0 Fehler (3 pre-existing failures unverändert)
**TypeScript:** 0 Fehler

## Geänderte Dateien

### `pages/kontrakte/FrmKontraktDetail.tsx`
- `buildCoreMaskShortcuts({ onSave, onRefresh, isSaveDisabled })` + `useKeyboardShortcuts`
- Ctrl+S → `saveMutation.mutate()` (nur wenn `isDraftEditable`)
- F5 → `detailQuery.refetch()`
- `KeyboardShortcutBar` am Seitenende
- Wrapper-Pattern: `<div className="flex flex-col">` + `<KeyboardShortcutBar>`

### `pages/disposition/liste.tsx`
- `buildCoreMaskShortcuts({ onNew, onRefresh })` + `useKeyboardShortcuts`
- Ctrl+N → `navigate('/einkauf/bestellvorschlaege')` (nächster Schritt im Prozess)
- F5 → `refetch()` (war vorher nicht verfügbar)
- `AgentProcessPanel domain="einkauf"` — zeigt Agent-Aktivität wenn Bestellvorschlag-Agent läuft
- `KeyboardShortcutBar` am Seitenende

### `pages/einkauf/bestellvorschlag-lager.tsx`
- `buildCoreMaskShortcuts({ onRefresh, onSearch, onCancel })` + `useKeyboardShortcuts`
- F5 → `loadData()` (Aufbereiten-Funktion)
- Ctrl+F → Focus auf Artikel-Nr.-Filter (`useRef` + `ref={filterRef}`)
- Escape → `navigate('/einkauf')`
- `AgentProcessPanel domain="einkauf"` — oben im Content-Bereich, rendert null wenn inaktiv
- Kein KeyboardShortcutBar (Seite hat eigene Bottom-Toolbar)

## Agentic Workflow Rollout-Stand nach Wave 94

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
| Einkauf | bestellvorschlag-lager.tsx | ✓ | — | ✓ |
| Disposition | liste.tsx | ✓ | — | ✓ |
| Kontrakte | FrmKontraktDetail.tsx | — | — | ✓ |
| Workflows | supervisor.tsx | ✓ | — | ✓ |
