/**
 * ALL-ROUTES SMOKE TEST
 *
 * Testet alle aus route-aliases + generierten Route-Gruppen geharvesteten Routen (typisch ~560).
 * Generiert einen JSON-Report unter tests/e2e/smoke-results.json
 *
 * Ausführung:
 *   npx playwright test tests/e2e/all-routes-smoke.spec.ts
 *   npm run test:e2e:smoke-all
 */
import { test, expect, type Page, type ConsoleMessage } from '@playwright/test'
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

// ── Typen ──────────────────────────────────────────────────────────────

type ErrorCategory =
  | 'OK'
  | 'ROUTE_MISSING'
  | 'RENDER_ERROR'
  | 'CONSOLE_ERROR'
  | 'EMPTY_PAGE'
  | 'TIMEOUT'
  | 'UNKNOWN'

interface RouteResult {
  path: string
  source: string
  original?: string
  category: ErrorCategory
  details: string
  consoleErrors: string[]
  durationMs: number
}

interface SmokeReport {
  generatedAt: string
  totalTested: number
  passed: number
  failed: number
  byCategory: Record<ErrorCategory, number>
  failures: RouteResult[]
  all: RouteResult[]
}

// ── Routen laden ───────────────────────────────────────────────────────

const ROUTES_FILE = resolve(process.cwd(), 'tests/e2e/.generated-routes.json')
if (!existsSync(ROUTES_FILE)) {
  throw new Error(
    'Route manifest nicht gefunden. Bitte zuerst ausführen:\n  node scripts/harvest-routes.mjs',
  )
}
const manifest = JSON.parse(readFileSync(ROUTES_FILE, 'utf-8'))
const routes: Array<{ path: string; source: string; original?: string }> = manifest.routes

// ── Report-Sammler ─────────────────────────────────────────────────────

const results: RouteResult[] = []

// ── Konfiguration ──────────────────────────────────────────────────────

const PAGE_TIMEOUT = 45_000
const BATCH_SIZE = 20

// ── Hilfsfunktionen ────────────────────────────────────────────────────

async function testRoute(
  page: Page,
  route: { path: string; source: string; original?: string },
): Promise<RouteResult> {
  const start = Date.now()
  const consoleErrors: string[] = []

  const onConsole = (msg: ConsoleMessage) => {
    if (msg.type() === 'error') {
      const text = msg.text()
      if (
        !text.includes('favicon.ico') &&
        !text.includes('net::ERR_') &&
        !text.includes('Failed to load resource')
      ) {
        consoleErrors.push(text.substring(0, 300))
      }
    }
  }
  page.on('console', onConsole)

  try {
    await page.goto(route.path, {
      waitUntil: 'domcontentloaded',
      timeout: PAGE_TIMEOUT,
    })

    try {
      await waitForDashboardShell(page, 30_000)
    } catch {
      await page.waitForTimeout(800)
    }

    const url = page.url()
    const pathname = new URL(url).pathname

    // ROUTE_MISSING: Seite fällt auf Dashboard oder 404 zurück
    const dashboardHeading = await page.getByRole('heading', { name: /app starter/i }).count()
    if (dashboardHeading > 0 && !DASHBOARD_ROUTES.has(route.path)) {
      return result(route, 'ROUTE_MISSING', 'Fällt auf App Starter Dashboard zurück', consoleErrors, start)
    }

    const notFoundHeading = await page.getByRole('heading', { name: /404/i }).count()
    if (notFoundHeading > 0) {
      return result(route, 'ROUTE_MISSING', '404 Seite angezeigt', consoleErrors, start)
    }

    // RENDER_ERROR: ErrorBoundary hat gegriffen
    const errorBoundary = await page.getByText(/fehler beim laden der seite/i).count()
    if (errorBoundary > 0) {
      return result(route, 'RENDER_ERROR', 'ErrorBoundary ausgelöst', consoleErrors, start)
    }

    // EMPTY_PAGE: Kein sichtbarer Inhalt
    const hasContent = await page
      .locator('main, [data-page], [data-testid="page-root"], .page-content, h1, h2, table, form')
      .first()
      .isVisible()
      .catch(() => false)

    if (!hasContent) {
      return result(route, 'EMPTY_PAGE', 'Keine sichtbaren Inhalte gefunden', consoleErrors, start)
    }

    // CONSOLE_ERROR: JS-Fehler (ReferenceError, TypeError etc.)
    const criticalErrors = consoleErrors.filter(
      (e) =>
        e.includes('ReferenceError') ||
        e.includes('TypeError') ||
        e.includes('SyntaxError') ||
        e.includes('is not defined') ||
        e.includes('Cannot read properties'),
    )
    if (criticalErrors.length > 0) {
      return result(route, 'CONSOLE_ERROR', criticalErrors[0], consoleErrors, start)
    }

    return result(route, 'OK', '', consoleErrors, start)
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err)
    if (msg.includes('Timeout') || msg.includes('timeout')) {
      return result(route, 'TIMEOUT', msg.substring(0, 200), consoleErrors, start)
    }
    return result(route, 'UNKNOWN', msg.substring(0, 200), consoleErrors, start)
  } finally {
    page.off('console', onConsole)
  }
}

function result(
  route: { path: string; source: string; original?: string },
  category: ErrorCategory,
  details: string,
  consoleErrors: string[],
  start: number,
): RouteResult {
  return {
    path: route.path,
    source: route.source,
    original: route.original,
    category,
    details,
    consoleErrors,
    durationMs: Date.now() - start,
  }
}

// ── Tests in Batches ───────────────────────────────────────────────────

const batches: Array<Array<{ path: string; source: string; original?: string }>> = []
for (let i = 0; i < routes.length; i += BATCH_SIZE) {
  batches.push(routes.slice(i, i + BATCH_SIZE))
}

const DASHBOARD_ROUTES = new Set(['/', '/start-dashboard'])

test.describe('ALL Routes Smoke Test', () => {
  test.describe.configure({ mode: 'serial', timeout: 600_000 })

  for (let batchIdx = 0; batchIdx < batches.length; batchIdx++) {
    const batch = batches[batchIdx]

    test(`Batch ${batchIdx + 1}/${batches.length} (${batch.length} Routen)`, async ({ page }) => {
      for (const route of batch) {
        const r = await testRoute(page, route)
        results.push(r)

        if (r.category !== 'OK') {
          console.log(`  FAIL [${r.category}] ${r.path} → ${r.details}`)
        }
      }
    })
  }

  test.afterAll(() => {
    const passed = results.filter((r) => r.category === 'OK').length
    const failed = results.filter((r) => r.category !== 'OK').length

    const byCategory: Record<string, number> = {}
    for (const r of results) {
      byCategory[r.category] = (byCategory[r.category] || 0) + 1
    }

    const report: SmokeReport = {
      generatedAt: new Date().toISOString(),
      totalTested: results.length,
      passed,
      failed,
      byCategory: byCategory as Record<ErrorCategory, number>,
      failures: results.filter((r) => r.category !== 'OK'),
      all: results,
    }

    const reportPath = resolve(process.cwd(), 'tests/e2e/smoke-results.json')
    writeFileSync(reportPath, JSON.stringify(report, null, 2), 'utf-8')

    console.log('\n' + '='.repeat(70))
    console.log('SMOKE TEST REPORT')
    console.log('='.repeat(70))
    console.log(`Getestet:       ${report.totalTested}`)
    console.log(`Bestanden:      ${passed}  (${((passed / report.totalTested) * 100).toFixed(1)}%)`)
    console.log(`Fehlgeschlagen: ${failed}`)
    console.log('')
    console.log('Nach Kategorie:')
    for (const [cat, count] of Object.entries(byCategory).sort((a, b) => b[1] - a[1])) {
      console.log(`  ${cat.padEnd(16)} ${count}`)
    }

    if (failed > 0) {
      console.log('')
      console.log('Top-Fehler:')
      const failures = report.failures.slice(0, 30)
      for (const f of failures) {
        console.log(`  [${f.category}] ${f.path}`)
        if (f.details) console.log(`    → ${f.details.substring(0, 120)}`)
      }
      if (report.failures.length > 30) {
        console.log(`  ... und ${report.failures.length - 30} weitere (siehe smoke-results.json)`)
      }
    }

    console.log('='.repeat(70))
    console.log(`Report: ${reportPath}`)
  })
})
