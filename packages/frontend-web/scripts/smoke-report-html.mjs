#!/usr/bin/env node
/**
 * Generiert einen HTML-Report aus smoke-results.json
 * Usage: node scripts/smoke-report-html.mjs
 * Output: tests/e2e/smoke-report.html
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const ROOT = join(__dirname, '..')
const INPUT = join(ROOT, 'tests', 'e2e', 'smoke-results.json')
const OUTPUT = join(ROOT, 'tests', 'e2e', 'smoke-report.html')

const data = JSON.parse(readFileSync(INPUT, 'utf-8'))

const COLORS = {
  OK: '#22c55e',
  ROUTE_MISSING: '#ef4444',
  RENDER_ERROR: '#f97316',
  CONSOLE_ERROR: '#eab308',
  EMPTY_PAGE: '#a855f7',
  TIMEOUT: '#6b7280',
  UNKNOWN: '#64748b',
}

const LABELS = {
  OK: 'Bestanden',
  ROUTE_MISSING: 'Route fehlt / 404 / Dashboard-Fallback',
  RENDER_ERROR: 'Render-Fehler (ErrorBoundary)',
  CONSOLE_ERROR: 'Konsolen-Fehler (JS)',
  EMPTY_PAGE: 'Leere Seite',
  TIMEOUT: 'Timeout',
  UNKNOWN: 'Unbekannt',
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

const failureRows = data.failures
  .map(
    (f) => `
  <tr>
    <td><span class="badge" style="background:${COLORS[f.category]}">${f.category}</span></td>
    <td><code>${esc(f.path)}</code></td>
    <td>${esc(f.details)}</td>
    <td class="small">${f.consoleErrors.length > 0 ? esc(f.consoleErrors[0].substring(0, 120)) : ''}</td>
    <td class="num">${f.durationMs}ms</td>
  </tr>`,
  )
  .join('\n')

const categoryRows = Object.entries(data.byCategory)
  .sort((a, b) => b[1] - a[1])
  .map(
    ([cat, count]) => `
  <tr>
    <td><span class="badge" style="background:${COLORS[cat] || '#666'}">${cat}</span></td>
    <td>${LABELS[cat] || cat}</td>
    <td class="num">${count}</td>
    <td class="num">${((count / data.totalTested) * 100).toFixed(1)}%</td>
  </tr>`,
  )
  .join('\n')

const html = `<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>VALEO NeuroERP – Smoke Test Report</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }
    h1 { font-size: 1.8rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.3rem; margin: 2rem 0 1rem; color: #94a3b8; }
    .summary { display: flex; gap: 2rem; margin: 1.5rem 0; }
    .card { background: #1e293b; border-radius: 12px; padding: 1.5rem 2rem; min-width: 160px; }
    .card .num { font-size: 2.5rem; font-weight: 700; }
    .card .label { font-size: 0.85rem; color: #94a3b8; margin-top: 0.3rem; }
    .green { color: #22c55e; }
    .red { color: #ef4444; }
    .blue { color: #3b82f6; }
    table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    th, td { padding: 0.6rem 1rem; text-align: left; border-bottom: 1px solid #334155; }
    th { background: #1e293b; color: #94a3b8; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }
    td { font-size: 0.9rem; }
    td.num { text-align: right; font-variant-numeric: tabular-nums; }
    td.small { font-size: 0.75rem; color: #94a3b8; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    code { background: #334155; padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; color: #fff; }
    .meta { color: #64748b; font-size: 0.8rem; margin-top: 2rem; }
    .filter-bar { margin: 1rem 0; display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .filter-btn { background: #334155; border: none; color: #e2e8f0; padding: 6px 14px; border-radius: 20px; cursor: pointer; font-size: 0.8rem; }
    .filter-btn:hover, .filter-btn.active { background: #3b82f6; }
  </style>
</head>
<body>
  <h1>VALEO NeuroERP – Smoke Test Report</h1>
  <p style="color:#64748b">Erstellt: ${data.generatedAt}</p>

  <div class="summary">
    <div class="card"><div class="num blue">${data.totalTested}</div><div class="label">Routen getestet</div></div>
    <div class="card"><div class="num green">${data.passed}</div><div class="label">Bestanden</div></div>
    <div class="card"><div class="num red">${data.failed}</div><div class="label">Fehlgeschlagen</div></div>
    <div class="card"><div class="num" style="color:#eab308">${((data.passed / data.totalTested) * 100).toFixed(1)}%</div><div class="label">Erfolgsrate</div></div>
  </div>

  <h2>Fehler nach Kategorie</h2>
  <table>
    <thead><tr><th>Kategorie</th><th>Beschreibung</th><th style="text-align:right">Anzahl</th><th style="text-align:right">Anteil</th></tr></thead>
    <tbody>${categoryRows}</tbody>
  </table>

  <h2>Alle Fehler (${data.failed})</h2>
  <div class="filter-bar">
    <button class="filter-btn active" onclick="filterTable('ALL')">Alle</button>
    ${Object.keys(COLORS)
      .filter((c) => c !== 'OK')
      .map((c) => `<button class="filter-btn" onclick="filterTable('${c}')">${c} (${data.byCategory[c] || 0})</button>`)
      .join('\n    ')}
  </div>
  <table id="failures">
    <thead><tr><th>Kategorie</th><th>Route</th><th>Details</th><th>Konsole</th><th style="text-align:right">Dauer</th></tr></thead>
    <tbody>${failureRows}</tbody>
  </table>

  <p class="meta">Report basiert auf ${data.totalTested} automatisch getesteten Routen. JSON-Daten: smoke-results.json</p>

  <script>
    function filterTable(cat) {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');
      document.querySelectorAll('#failures tbody tr').forEach(row => {
        const badge = row.querySelector('.badge')?.textContent;
        row.style.display = (cat === 'ALL' || badge === cat) ? '' : 'none';
      });
    }
  </script>
</body>
</html>`

writeFileSync(OUTPUT, html, 'utf-8')
console.log(`HTML-Report → ${OUTPUT}`)
