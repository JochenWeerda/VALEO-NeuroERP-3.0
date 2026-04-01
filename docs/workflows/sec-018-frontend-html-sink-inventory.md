# SEC-018 - Frontend-HTML-/Print-Pfade inventarisieren

## Ziel

Die verbleibenden browserbasierten HTML-Sinks im Frontend sollen sichtbar und dauerhaft gegen Regressionen abgesichert werden.

## Scope

- `packages/frontend-web/src/__tests__/security/print-html-sinks.test.ts`
- `.github/workflows/security-agent.yml`
- `scripts/security/README.md`

## Inventur

Die aktuelle Suche nach `document.write`, `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `dangerouslySetInnerHTML`, `eval` und `new Function` in `packages/frontend-web/src` ergibt nur drei bewusst verbleibende Printpfade:

- `lib/export-utils.ts`
- `lib/services/bon-druck.ts`
- `pages/einkauf/bestellungen-liste.tsx`

Diese drei Stellen sind bereits ueber `escapeHtml()` gehaertet.

## Umsetzung

- neuer Vitest-Guard scannt den Frontend-Quellbaum auf gefaehrliche HTML-Sinks
- `document.write` ist nur in den drei bekannten Printpfaden erlaubt
- neue Vorkommen von `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `dangerouslySetInnerHTML`, `eval` oder `new Function` schlagen den Test sofort fehl
- die bestehende Security-CI-Lane fuehrt den Guard mit aus

## Verifikation

- `pnpm --dir packages/frontend-web exec vitest run src/__tests__/lib/export-utils.test.ts src/__tests__/security/print-html-sinks.test.ts`
- `node scripts/docs-governance-check.cjs`

## Restrisiken

- der Guard bewertet statische Quelltexte, nicht Laufzeitmanipulationen aus Drittbibliotheken
- falls bewusst neue HTML-Sinks noetig werden, muessen sie zuerst gehaertet und dann explizit in die Inventur aufgenommen werden
