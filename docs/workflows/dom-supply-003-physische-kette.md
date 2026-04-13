# DOM-SUPPLY-003 - Physische Kette

## Ziel

Die physische Kette `Partie -> Annahme -> Wiegung -> Charge -> Fracht -> Abrechnung` fachlich und statusseitig durchgaengig harmonisieren.

## Scope

- Annahme- und Warteschlangenpfade
- Wiegung und Wiegescheindetail
- Charge-/Rueckverfolgung
- Fracht-/Lieferobjekte
- Settlement-/Abrechnungskontext

## Dateibesitz

- `packages/frontend-web/src/pages/annahme/*`
- `packages/frontend-web/src/pages/waage/*`
- `packages/frontend-web/src/pages/charge/*`
- `packages/frontend-web/src/pages/logistik/*`
- zugehoerige Supply-/Inventory-Read-Models

## Abnahmekriterien

- Jeder Uebergabepunkt zeigt Objektbezug, Abweichung, Folgeobjekt und naechste Aktion konsistent.
- Die physische Kette kann vom Anwender ohne Medienbruch nachvollzogen werden.
- Ausnahmegruende und Blocker sind an den Uebergabepunkten sichtbar.

## Risiken

- historisch verteilte Objektmodelle zwischen Inventory, Ops und Finance
- zu starke UI-Verdichtung auf Listenraeumen
- uneinheitliche Statusquellen entlang der Kette
