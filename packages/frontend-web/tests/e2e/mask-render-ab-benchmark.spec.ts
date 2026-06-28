import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { expect, test } from '@playwright/test'

import {
  BENCH_CONTRACT_ID,
  BENCH_ORDER_ID,
  setupKontraktBenchmarkMocks,
  setupSalesOrderBenchmarkMocks,
} from './helpers/mask-benchmark-fixtures'
import {
  aggregateMetricRuns,
  compareMaskMetrics,
  measureMaskRender,
  type MaskAbComparison,
  type MaskBenchmarkDomain,
  type MaskRenderMetrics,
} from './helpers/mask-render-metrics'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const RESULTS_DIR = path.join(__dirname, '.benchmark-results')
const EVIDENCE_DIR = path.join(__dirname, '../../../../evidence/perf')
const RUNS = Number(process.env.MASK_BENCHMARK_RUNS ?? 3)
const AB_BENCHMARK_ENABLED = process.env.MASK_AB_BENCHMARK === '1'

const scenarios: Array<{
  domain: MaskBenchmarkDomain
  entityId: string
  setupMocks: (page: import('@playwright/test').Page) => Promise<void>
  cases: Array<{
    variant: 'legacy' | 'pilot'
    path: string
    waitForShellReady: (page: import('@playwright/test').Page) => Promise<void>
    positionsRowSelector: string
    revealPositions: (page: import('@playwright/test').Page) => Promise<void>
  }>
}> = [
  {
    domain: 'sales-order',
    entityId: BENCH_ORDER_ID,
    setupMocks: setupSalesOrderBenchmarkMocks,
    cases: [
      {
        variant: 'legacy',
        path: `/dev/mask-benchmark/sales-order/legacy/${BENCH_ORDER_ID}`,
        waitForShellReady: async (page) => {
          await page.getByTestId('legacy-order-editor').waitFor({ state: 'visible', timeout: 45_000 })
          await page.waitForFunction(() => {
            const inputs = Array.from(document.querySelectorAll('[data-testid="legacy-order-editor"] input'))
            return inputs.some((input) => (input as HTMLInputElement).value === 'SO-BENCH-100')
          }, null, { timeout: 45_000 })
        },
        positionsRowSelector: 'table tbody tr:has-text("Benchmark Position 1")',
        revealPositions: async () => {
          /* Legacy rendert Positionen im Erstload — kein Tab-Klick noetig. */
        },
      },
      {
        variant: 'pilot',
        path: `/dev/mask-benchmark/sales-order/pilot/${BENCH_ORDER_ID}`,
        waitForShellReady: async (page) => {
          await page.getByTestId('universal-sales-order-pilot').waitFor({ state: 'visible', timeout: 45_000 })
          await page.getByText('Auftragssumme').waitFor({ state: 'visible', timeout: 45_000 })
        },
        positionsRowSelector: '[data-testid="virtual-data-table"] button[type="button"]',
        revealPositions: async (page) => {
          await page.getByRole('tab', { name: /positionen/i }).click()
        },
      },
    ],
  },
  {
    domain: 'kontrakt',
    entityId: BENCH_CONTRACT_ID,
    setupMocks: setupKontraktBenchmarkMocks,
    cases: [
      {
        variant: 'legacy',
        path: `/dev/mask-benchmark/kontrakt/legacy/${BENCH_CONTRACT_ID}`,
        waitForShellReady: async (page) => {
          await page.getByTestId('legacy-kontrakt-detail').waitFor({ state: 'visible', timeout: 45_000 })
          await page.waitForFunction(() => {
            const inputs = Array.from(document.querySelectorAll('[data-testid="legacy-kontrakt-detail"] input'))
            return inputs.some((input) => (input as HTMLInputElement).value === 'K-BENCH-100')
          }, null, { timeout: 45_000 })
        },
        positionsRowSelector: 'table tbody tr:has-text("Kontraktzeile 1")',
        revealPositions: async () => {
          /* Legacy rendert Positionen im Erstload — kein Tab-Klick noetig. */
        },
      },
      {
        variant: 'pilot',
        path: `/dev/mask-benchmark/kontrakt/pilot/${BENCH_CONTRACT_ID}`,
        waitForShellReady: async (page) => {
          await page.getByTestId('universal-kontrakt-pilot').waitFor({ state: 'visible', timeout: 45_000 })
          await page.getByText('Restmenge').waitFor({ state: 'visible', timeout: 45_000 })
        },
        positionsRowSelector: '[data-testid="virtual-data-table"] button[type="button"]',
        revealPositions: async (page) => {
          await page.getByRole('tab', { name: /positionen/i }).click()
        },
      },
    ],
  },
]

function writeJson(filePath: string, payload: unknown): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true })
  fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8')
}

/**
 * Geparkt bis Frontend-Baseline wieder stabil (428-Fehler-Fix).
 * Aktivierung: MASK_AB_BENCHMARK=1 pnpm benchmark:mask-render-ab
 */
test.describe('Mask render A/B benchmark (Legacy vs. Pilot)', () => {
  test.skip(!AB_BENCHMARK_ENABLED, 'Set MASK_AB_BENCHMARK=1 to run the A/B PoC benchmark.')
  test.describe.configure({ mode: 'serial' })

  const collected: MaskRenderMetrics[] = []

  for (const scenario of scenarios) {
    for (const benchmarkCase of scenario.cases) {
      test(`${scenario.domain} ${benchmarkCase.variant} benchmark (${RUNS} runs)`, async ({ page }) => {
        await scenario.setupMocks(page)

        const runs: MaskRenderMetrics[] = []
        for (let index = 0; index < RUNS; index += 1) {
          const metrics = await measureMaskRender(page, {
            domain: scenario.domain,
            variant: benchmarkCase.variant,
            entityId: scenario.entityId,
            path: benchmarkCase.path,
            waitForShellReady: benchmarkCase.waitForShellReady,
            positionsRowSelector: benchmarkCase.positionsRowSelector,
            revealPositions: benchmarkCase.revealPositions,
          })
          runs.push(metrics)
        }

        const aggregated = aggregateMetricRuns(runs)
        collected.push(aggregated)
        writeJson(path.join(RESULTS_DIR, `${scenario.domain}-${benchmarkCase.variant}.json`), {
          runs,
          aggregated,
        })
      })
    }
  }

  test('A/B PoC — pilot must beat or match legacy budgets', async () => {
    const comparisons: MaskAbComparison[] = []

    for (const scenario of scenarios) {
      const legacy = collected.find((item) => item.domain === scenario.domain && item.variant === 'legacy')
      const pilot = collected.find((item) => item.domain === scenario.domain && item.variant === 'pilot')
      expect(legacy, `legacy metrics missing for ${scenario.domain}`).toBeTruthy()
      expect(pilot, `pilot metrics missing for ${scenario.domain}`).toBeTruthy()
      if (!legacy || !pilot) continue

      const comparison = compareMaskMetrics(legacy, pilot)
      comparisons.push(comparison)
      expect(comparison.pocPassed, comparison.pocNotes.join(' | ')).toBe(true)
    }

    const report = {
      generatedAt: new Date().toISOString(),
      runsPerVariant: RUNS,
      comparisons,
    }

    writeJson(path.join(RESULTS_DIR, 'mask-render-ab-report.json'), report)
    writeJson(path.join(EVIDENCE_DIR, 'mask-render-ab.latest.json'), report)
  })
})
