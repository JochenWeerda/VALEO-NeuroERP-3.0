# Wave-25 Status

## Scope
Kontextsensitive Quick Actions pro Maske als expliziter Backend-/Frontend-Contract (Gap 025)

## Zielbild

Wave 25 zieht die bisher flache Action-Liste auf einen echten
Quick-Action-Contract nach. Statt nur globaler Action-Listen mit
minimalem Domain-/Mask-Filter liefert das Backend jetzt explizite
Kontextaufloesung mit Relevanzscore, Kontext-Scope und Surface-Hinweisen
fuer Toolbar, Overflow, Palette und Voice. Das Frontend konsumiert
diesen Contract zentral und baut daraus dieselben Quick Actions fuer
`OverviewPage`, `ObjectPage`, `ListReport` und `Wizard`, statt pro
Pattern neue lokale Button-Logik zu verdrahten.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/ki_action_registry.py` | Zentrale Action-Registry mit `ActionDefinition`, `ResolvedAction`, `context_scope`, `relevance_score` und Surface-Hinweisen | abgeschlossen |
| AP2 | `app/api/v1/endpoints/ki_usability.py` | `GET /actions`, `GET /actions/{id}` und `POST /voice/resolve` nutzen die neue Registry statt einer flachen Action-Liste | abgeschlossen |
| AP3 | `packages/frontend-web/src/features/ki-usability/api/actions.ts` | Frontend-Action-Typen tragen jetzt `surfaces`, `context_scope`, `relevance_score`, `priority` und `default_params` | abgeschlossen |
| AP4 | `packages/frontend-web/src/features/ki-usability/toolbar-actions.ts` | Gemeinsamer Mapper von Registry-Actions auf `PageToolbar`-Primary/Overflow mit deterministischer Sortierung | abgeschlossen |
| AP5 | `packages/frontend-web/src/components/patterns/OverviewPage.tsx` + `ObjectPage.tsx` + `ListReport.tsx` + `Wizard.tsx` | Pattern-Komponenten konsumieren den gemeinsamen Quick-Action-Mapper statt lokaler Mapping-Varianten | abgeschlossen |
| AP6 | `tests/test_process_kernel_wave25_quick_actions.py` + `packages/frontend-web/src/__tests__/features/ki-usability/toolbar-actions.test.ts` | Contract- und Frontend-Tests fuer Kontextaufloesung, Relevanzsortierung und Toolbar-Surfacing | abgeschlossen |

## Abnahmekriterien

- Maskenspezifische Actions schlagen Domain- und Global-Fallbacks deterministisch
- Das Backend liefert Relevanz, Scope und Surface-Hinweise im API-Contract aus
- Voice-Aufloesung bleibt an denselben Action-IDs verankert wie Toolbar und Palette
- Pattern-Komponenten erzeugen Quick Actions nur noch ueber den gemeinsamen Mapper
- Keine neuen lokalen Toolbar-Sonderpfade in `OverviewPage`, `ObjectPage`, `ListReport` oder `Wizard`
- Keine Schichtverletzungen; der Registry-Contract lebt in `app/core/` und wird additiv von API/UI konsumiert

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave25_quick_actions.py` | 4 | Registry-Aufloesung, API-Metadaten, Fallback-Action-Aufloesung und Voice-Intent-Matching |
| `packages/frontend-web/src/__tests__/features/ki-usability/toolbar-actions.test.ts` | 2 | Surface-basiertes Primary/Overflow-Surfacing und Fallback ohne Surface-Hinweise |
| `packages/frontend-web/src/__tests__/components/patterns/Wizard.test.tsx` | 4 | Pattern-Harness auf aktuellen React-Query-Contract gezogen; `Wizard` bleibt unter `useActionsForMask()` stabil |

**Gesamt Wave 25: 10 Tests gruen**

## Gap geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 025 | Kontextsensitive Quick Actions pro Maske | Kontextsensitive Action-Registry mit Score/Scope/Surface-Contract; gemeinsame Toolbar-Aufloesung fuer Pattern-Komponenten und KI-Usability-API |

## Status
`abgeschlossen` - 2026-03-15 - Backend-Contract, Frontend-Mapper, Pattern-Integration und Wave-25-Tests gruen
