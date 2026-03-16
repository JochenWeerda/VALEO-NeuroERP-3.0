# Wave-22 Status

## Scope
Command Palette fuer Power User: zentraler Action-Dispatch + Mask-Registry-Surfacing (Gap 022)

## Zielbild

Wave 22 schliesst Gap 022 aus dem Landhandel-Backlog:
`Ctrl/Cmd+K` wird von einer reinen Navigationshilfe zu einer zentralen
Power-User-Oberflaeche ausgebaut. Die Produktiv-Palette konsumiert
denselben Action-Dispatch-Contract wie Toolbar, Shortcut und Voice und
zieht Prozessmasken aus der bestehenden Mask Registry nach, statt
Routen und Events lokal zu duplizieren.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `packages/frontend-web/src/features/ki-usability/context/ActionDispatchContext.tsx` | Dispatcher faellt fuer unbekannte Action-IDs auf dynamische `path`-Navigation und `eventName`-Browser-Events zurueck | abgeschlossen |
| AP2 | `packages/frontend-web/src/components/navigation/command-palette-model.ts` | Zentrales, testbares Command-Model fuer Basisbefehle, Navigation, Action-/AI-Shortcuts und Mask-Registry-Eintraege | abgeschlossen |
| AP3 | `packages/frontend-web/src/lib/api/mask-registry.ts` | Typisierte Frontend-API fuer `/api/v1/ui/mask-registry` | abgeschlossen |
| AP4 | `packages/frontend-web/src/components/navigation/CommandPalette.tsx` | Produktive Palette nutzt jetzt TanStack Query + Mask Registry und dispatcht nur noch ueber zentrale Action-Contracts | abgeschlossen |
| AP5 | `packages/frontend-web/src/components/navigation/AppShell.tsx` | Tastatur-Action-Shortcuts laufen ebenfalls ueber denselben Dispatcher statt ueber direkte `navigate(...)`-Aufrufe | abgeschlossen |
| AP6 | `packages/frontend-web/src/__tests__/components/navigation/CommandPalette.test.tsx` + `packages/frontend-web/src/__tests__/components/navigation/command-palette-model.test.ts` + `packages/frontend-web/src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx` | Contract- und UI-Tests fuer Model, Dispatcher-Fallbacks und Palette-Auswahl | abgeschlossen |

## Abnahmekriterien

- `Ctrl/Cmd+K` nutzt denselben Dispatch-Einstiegspunkt wie Toolbar, Voice und globale Shortcut-Ausloeser
- Die Palette kann bestehende Prozessmasken aus `/api/v1/ui/mask-registry` als Kommandos surfacen
- Klasse-A- und Klasse-B-Masken sind suchbar; Klasse-C-Masken werden nicht als operative Kommandos gezogen
- Agrar-Eintraege werden bei deaktiviertem Feature konsistent gefiltert
- Es entstehen keine neuen direkten Event-/Routing-Sonderpfade in der Palette
- Keine Schichtverletzungen: Frontend-UI konsumiert API-/Context-Bausteine, dupliziert aber keine Dispatch-Logik

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `packages/frontend-web/src/__tests__/components/navigation/command-palette-model.test.ts` | 2 | Mask-Registry-Anhaengung und Agrar-Filterung |
| `packages/frontend-web/src/__tests__/components/navigation/CommandPalette.test.tsx` | 1 | Palette laedt Registry und dispatcht ueber zentrale Action-Contracts |
| `packages/frontend-web/src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx` | 2 | Dispatcher-Fallback fuer dynamische Navigation und Browser-Events |
| `packages/frontend-web/src/__tests__/navigation-wiring.test.ts` | 3 | Nav-Wiring erkennt jetzt auch Verzeichnis-Module mit `index.tsx` wie `@/pages/portal` korrekt |

**Gesamt Wave 22: 8 Tests gruen**

## Gap geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 022 | Command Palette (Ctrl/Cmd+K) fuer Power User | Palette auf zentralen Dispatcher gehoben und mit Mask-Registry-Prozesskommandos angereichert |

## Status
`abgeschlossen` - 2026-03-14 - Frontend-Typecheck gruen, 8 Wave-22-Tests gruen
