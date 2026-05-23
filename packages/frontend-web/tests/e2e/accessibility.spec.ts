import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/** MERIDIAN/TERRA Kernrouten — Slice DESIGN-MERIDIAN-AXE-CI-001 */
const CORE_ROUTES = [
  '/',
  '/agrar',
  '/einkauf/bestellungen',
  '/finance',
  '/lager',
  '/portal/feldbuch',
  '/portal/naehrstoffbilanzen',
  '/portal/rationsoptimierung',
] as const

function formatViolations(violations: Awaited<ReturnType<AxeBuilder['analyze']>>['violations']): string {
  return violations
    .map((v) => {
      const nodes = v.nodes
        .slice(0, 3)
        .map((n) => `  - ${n.target.join(' ')}: ${n.failureSummary ?? n.html}`)
        .join('\n')
      return `[${v.impact}] ${v.id}: ${v.description}\n${nodes}`
    })
    .join('\n\n')
}

test.describe('WCAG 2.2 AA Audit @accessibility', () => {
  for (const route of CORE_ROUTES) {
    test(`Keine axe-Fehler auf ${route}`, { tag: '@accessibility' }, async ({ page }) => {
      await page.goto(route, { waitUntil: 'domcontentloaded' })
      await waitForDashboardShell(page)

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze()

      expect(
        results.violations,
        results.violations.length > 0
          ? `axe violations on ${route}:\n\n${formatViolations(results.violations)}`
          : undefined,
      ).toEqual([])
    })
  }
})
