# SEC-013 - Print XSS Hardening

- Status: abgeschlossen
- Scope: `packages/frontend-web/src/lib/export-utils.ts`, `packages/frontend-web/src/lib/services/bon-druck.ts`, `packages/frontend-web/src/pages/einkauf/bestellungen-liste.tsx`
- Lieferung: HTML-Escaping fuer `document.write`-basierte Printpfade
- Nachweis: `packages/frontend-web/src/__tests__/lib/export-utils.test.ts`
