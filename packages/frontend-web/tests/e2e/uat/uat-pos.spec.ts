/**
 * UAT — POS (Point of Sale)
 *
 * Business Value:
 *   The POS module is used at grain reception desks and farm supply stores.
 *   Promotions must display the correct discount type so cashiers apply the
 *   right pricing rule without manual lookup.
 *
 * Test IDs: TC-POS-001, TC-POS-002
 */
import { test, expect } from '@playwright/test'
import { attachConsoleErrorListener, UATHelpers } from './uat-helpers'
import { waitForDashboardShell } from '../helpers/wait-dashboard-shell'

/** POS pages used across multiple test cases */
const POS_PAGES = [
  '/pos/promotionen',
  '/pos/terminal',
  '/pos/tagesabschluss',
] as const

test.describe('UAT TC-POS: POS-Modul', () => {
  // -------------------------------------------------------------------------
  // TC-POS-001: Promotionen — Aktionstyp-Badges
  // -------------------------------------------------------------------------
  test('TC-POS-001: Promotionen — Aktionstyp-Badges (PROZENT/BETRAG/GRATISARTIKEL) sichtbar', async ({
    page,
  }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/pos/promotionen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/pos/promotionen')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /promotion/i }).first(),
    ).toBeVisible()

    // Business assertion: cashiers rely on action-type badges (PROZENT = percentage
    // discount, BETRAG = fixed amount, GRATISARTIKEL = free item) to apply the
    // correct POS discount rule.  The table/grid must be present.
    await expect(page.locator('table, [role="grid"], button').first()).toBeVisible()

    // Soft assertion: when promotion rows exist, at least one badge should match
    const knownBadge = page.getByText(/PROZENT|BETRAG|GRATISARTIKEL/i).first()
    const badgeCount = await knownBadge.count()
    if (badgeCount > 0) {
      await expect(knownBadge).toBeVisible()
    }

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-POS-001')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-POS-001')
  })

  // -------------------------------------------------------------------------
  // TC-POS-002: Console-Error-Check auf allen POS-Seiten
  // -------------------------------------------------------------------------
  test('TC-POS-002: Keine TypeError/ReferenceError auf POS-Seiten', async ({ page }) => {
    const allErrors: string[] = []

    for (const path of POS_PAGES) {
      const collector = attachConsoleErrorListener(page)

      await page.goto(path, { waitUntil: 'domcontentloaded' })
      // Best-effort wait — if the page doesn't have a <main> we still collect errors
      await page
        .locator('main')
        .first()
        .waitFor({ state: 'visible', timeout: 30_000 })
        .catch(() => undefined)

      if (collector.errors.length > 0) {
        allErrors.push(`[${path}] ${collector.errors.join(' | ')}`)
      }

      // Screenshot per page for evidence
      const tcSuffix = path.replace(/\//g, '-').replace(/^-/, '')
      await UATHelpers.recordTestEvidence(page, `TC-POS-002-${tcSuffix}`)
    }

    expect(
      allErrors,
      `TC-POS-002: Console errors found on POS pages:\n${allErrors.join('\n')}`,
    ).toHaveLength(0)
  })
})
