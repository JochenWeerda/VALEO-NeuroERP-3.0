# SEC-013 - Print XSS Hardening

## Ziel

XSS in browserbasierten Print-/Exportpfaden mit `document.write` verhindern.

## Umsetzung

- zentrales `escapeHtml()` in `export-utils.ts`
- Verdrahtung in `printTable()`, Bestellungs-Bulk-Print und Bon-Druck-Fallback

## Tests

- `packages/frontend-web/src/__tests__/lib/export-utils.test.ts`

