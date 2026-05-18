/**
 * UAT Shared Helpers — VALEO NeuroERP 3.0
 *
 * Provides reusable assertion utilities following the AI-Test-Oracle principle:
 * every helper encapsulates a business-observable quality contract, not just a
 * technical DOM assertion.
 */
import { type Page, type Response, expect } from '@playwright/test'

/** Maximum acceptable page load time in milliseconds (business SLA). */
export const PAGE_LOAD_BUDGET_MS = 3_000

/** Screenshot output directory (relative to project root when using Playwright). */
export const UAT_SCREENSHOT_DIR = 'test-results/uat'

// ---------------------------------------------------------------------------
// Collected console error state per test
// ---------------------------------------------------------------------------

export type ConsoleErrorCollector = { errors: string[] }

/**
 * Attaches a console listener to `page` and returns the collector object.
 * Must be called before navigation.  Any TypeError or ReferenceError found in
 * the browser console is appended to `collector.errors`.
 */
export function attachConsoleErrorListener(page: Page): ConsoleErrorCollector {
  const collector: ConsoleErrorCollector = { errors: [] }
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      const text = msg.text()
      if (/TypeError|ReferenceError/.test(text)) {
        collector.errors.push(text)
      }
    }
  })
  return collector
}

// ---------------------------------------------------------------------------
// UATHelpers namespace
// ---------------------------------------------------------------------------

export const UATHelpers = {
  /**
   * Waits until the AppShell `<main>` is visible AND network is idle.
   * Vite lazy-loads chunks; domcontentloaded fires too early.
   */
  async waitForPageLoad(page: Page, timeout = 60_000): Promise<void> {
    await page.locator('main').first().waitFor({ state: 'visible', timeout })
    // Best-effort network idle — ignore timeout (backend may be absent in unit runs)
    await page.waitForLoadState('networkidle', { timeout: 10_000 }).catch(() => undefined)
  },

  /**
   * Asserts that no TypeError or ReferenceError was collected.
   * Pass the collector returned by `attachConsoleErrorListener`.
   */
  assertNoConsoleErrors(collector: ConsoleErrorCollector, context: string): void {
    expect(
      collector.errors,
      `[${context}] Unexpected console errors: ${collector.errors.join(' | ')}`,
    ).toHaveLength(0)
  },

  /**
   * Asserts that the Navigation Timing API reports a total page load within
   * PAGE_LOAD_BUDGET_MS.  Skips silently when the API is unavailable (SSR/JSDOM).
   */
  async assertResponseTime(page: Page, budgetMs = PAGE_LOAD_BUDGET_MS): Promise<void> {
    const duration = await page.evaluate((): number | null => {
      const [nav] = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[]
      return nav ? nav.loadEventEnd - nav.startTime : null
    })
    if (duration !== null && duration > 0) {
      expect(
        duration,
        `Page load took ${duration.toFixed(0)} ms — exceeds budget of ${budgetMs} ms`,
      ).toBeLessThanOrEqual(budgetMs)
    }
  },

  /**
   * Saves a PNG screenshot as UAT evidence.
   * Path: `test-results/uat/<tcId>.png`
   */
  async recordTestEvidence(page: Page, tcId: string): Promise<void> {
    await page.screenshot({ path: `${UAT_SCREENSHOT_DIR}/${tcId}.png`, fullPage: false })
  },

  /**
   * Asserts that the current URL is still at the expected path (no silent redirect
   * to dashboard or error page).
   */
  async assertUrlRetained(page: Page, expectedPath: string): Promise<void> {
    await expect(page).toHaveURL(
      new RegExp(`${expectedPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|\\?)`),
    )
  },

  /**
   * Asserts that the generic "Fehler beim Laden" fallback is NOT shown.
   */
  async assertNoLoadError(page: Page): Promise<void> {
    await expect(page.getByText(/fehler beim laden der seite/i)).toHaveCount(0)
  },

  /**
   * Checks that outgoing requests include the X-Tenant-ID header.
   * Registers a request listener; returns an unsubscribe function.
   *
   * Note: the header is injected by the axios interceptor, so it appears on
   * API calls, not on the initial page navigation.
   */
  assertTenantIsolation(page: Page): { stop: () => void; violations: string[] } {
    const violations: string[] = []
    const handler = (req: { url: () => string; headers: () => Record<string, string> }) => {
      const url = req.url()
      if (url.includes('/api/v1/')) {
        const headers = req.headers()
        if (!headers['x-tenant-id']) {
          violations.push(url)
        }
      }
    }
    page.on('request', handler)
    return {
      violations,
      stop: () => page.off('request', handler),
    }
  },
}
