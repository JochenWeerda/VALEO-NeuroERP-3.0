#!/usr/bin/env npx ts-node
/**
 * A/B Proof-of-Concept: Legacy vs. RenderPlan Pilot (Sales + Kontrakt).
 *
 * Status: geparkt — nur mit explizitem Opt-in starten:
 *   MASK_AB_BENCHMARK=1 pnpm benchmark:mask-render-ab
 */

import { execSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(__dirname, '..')
const FRONTEND = path.join(ROOT, 'packages', 'frontend-web')
const REPORT = path.join(FRONTEND, 'tests', 'e2e', '.benchmark-results', 'mask-render-ab-report.json')
const BASELINE_DOC = path.join(ROOT, 'docs', 'architecture', 'uix', 'render-performance-baseline.md')

function runPlaywright(): void {
  execSync(
    'npx playwright test tests/e2e/mask-render-ab-benchmark.spec.ts --workers=1',
    {
      cwd: FRONTEND,
      stdio: 'inherit',
      env: {
        ...process.env,
        MASK_AB_BENCHMARK: '1',
        MASK_BENCHMARK_RUNS: process.env.MASK_BENCHMARK_RUNS ?? '3',
      },
    },
  )
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  return `${(bytes / 1024).toFixed(1)} KB`
}

function appendBaselineSection(report: {
  generatedAt: string
  runsPerVariant: number
  comparisons: Array<{
    domain: string
    pocPassed: boolean
    legacy: { shellReadyMs: number; initialApiRequests: number; initialTransferBytes: number; domTableNodes: number }
    pilot: { shellReadyMs: number; initialApiRequests: number; initialTransferBytes: number; domTableNodes: number }
    deltas: { shellReadyPct: number; initialTransferPct: number; domTableNodes: number }
    pocNotes: string[]
  }>
}): void {
  const lines: string[] = [
    '',
    '## A/B PoC — Legacy vs. RenderPlan (gemessen)',
    '',
    `Letzte Messung: ${report.generatedAt} (${report.runsPerVariant} Median-Laeufe pro Variante, Playwright mocked APIs).`,
    '',
    '| Domäne | Metrik | Legacy | Pilot | Δ | PoC |',
    '|--------|--------|--------|-------|---|-----|',
  ]

  for (const item of report.comparisons) {
    lines.push(
      `| ${item.domain} | Shell ready (ms) | ${Math.round(item.legacy.shellReadyMs)} | ${Math.round(item.pilot.shellReadyMs)} | ${item.deltas.shellReadyPct.toFixed(1)}% | ${item.pocPassed ? 'PASS' : 'FAIL'} |`,
      `| ${item.domain} | Initiale API-Calls | ${Math.round(item.legacy.initialApiRequests)} | ${Math.round(item.pilot.initialApiRequests)} | ${Math.round(item.legacy.initialApiRequests - item.pilot.initialApiRequests)} | |`,
      `| ${item.domain} | Initiale Bytes | ${formatBytes(item.legacy.initialTransferBytes)} | ${formatBytes(item.pilot.initialTransferBytes)} | ${item.deltas.initialTransferPct.toFixed(1)}% | |`,
      `| ${item.domain} | DOM Tabellenzeilen | ${Math.round(item.legacy.domTableNodes)} | ${Math.round(item.pilot.domTableNodes)} | ${Math.round(item.deltas.domTableNodes)} | |`,
    )
  }

  lines.push('', '### Interpretation', '')
  for (const item of report.comparisons) {
    lines.push(`- **${item.domain}:** ${item.pocNotes.join(' ')}`)
  }
  lines.push('')

  const marker = '## A/B PoC — Legacy vs. RenderPlan (gemessen)'
  const current = fs.readFileSync(BASELINE_DOC, 'utf8')
  const withoutOld = current.includes(marker)
    ? current.slice(0, current.indexOf(marker)).trimEnd()
    : current.trimEnd()
  fs.writeFileSync(BASELINE_DOC, `${withoutOld}\n${lines.join('\n')}\n`, 'utf8')
}

function main(): void {
  if (process.env.MASK_AB_BENCHMARK !== '1') {
    console.log('A/B Benchmark ist geparkt. Start mit: MASK_AB_BENCHMARK=1 pnpm benchmark:mask-render-ab')
    process.exit(0)
  }

  console.log('=== Mask Render A/B Benchmark (Legacy vs. Pilot) ===\n')
  runPlaywright()

  if (!fs.existsSync(REPORT)) {
    console.error(`Report missing: ${REPORT}`)
    process.exit(1)
  }

  const report = JSON.parse(fs.readFileSync(REPORT, 'utf8')) as Parameters<typeof appendBaselineSection>[0]
  appendBaselineSection(report)
  console.log(`\nReport: ${REPORT}`)
  console.log(`Baseline updated: ${BASELINE_DOC}`)
}

main()
