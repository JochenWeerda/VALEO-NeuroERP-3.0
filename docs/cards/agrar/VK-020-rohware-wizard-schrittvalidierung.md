# VK-020 — Rohware-Wizard Schrittvalidierung

**Slice:** VK-020 | **Datum:** 2026-03-27
**Status:** abgeschlossen

## Zweck

Schrittvalidierung in der Rohware-Schnellerfassung, damit keine Annahme ohne Lieferant/Fahrzeug, ohne Ware/Lager oder mit Netto 0 ausgeloest wird (Umsetzung von **VK-012-P1**).

## Dateibesitz

- `packages/frontend-web/src/pages/annahme/rohware.tsx`
- `packages/frontend-web/src/__tests__/pages/annahme/rohware.test.tsx`
- `docs/workflows/vk-020-rohware-wizard-schrittvalidierung.md`

## Abnahmekriterien

- `getStepValidationError` / `onStepValidationError` am `Wizard` verdrahtet
- Schritte `lieferant-fahrzeug` und `ware-gewicht` mit klaren Pflichtregeln
- Vitest-Regression fuer blockiertes **Weiter**

## Naechster Schritt

- VK-012-P2 Supplier-CRM-Dropdown / VK-012-P3 Artikel aus API (eigene Slices)
