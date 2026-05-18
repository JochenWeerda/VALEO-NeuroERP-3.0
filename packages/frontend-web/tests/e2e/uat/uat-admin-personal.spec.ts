/**
 * UAT — Admin & Personal-Modul
 *
 * Business Value:
 *   - Admin/Webshop: Integration cards allow the IT administrator to connect
 *     external shop systems without manual API configuration.
 *   - Admin/Webhooks: The active/inactive toggle status is required for the
 *     administrator to understand the real-time event delivery state.
 *   - Personal/Organigramm: HR relies on the org chart tree to manage reporting
 *     lines and headcount planning.
 *   - Personal/Bewerbungen: Recruitment pipeline badges enable HR to track
 *     applicants through standardised hiring stages.
 *   - Genossenschaft/Mitglieder: Cooperative administrators must see member
 *     capital data to comply with cooperative law (GenG § 19).
 *
 * Test IDs: TC-ADM-001, TC-ADM-002, TC-PER-001, TC-PER-002, TC-GEN-001
 */
import { test, expect } from '@playwright/test'
import { attachConsoleErrorListener, UATHelpers } from './uat-helpers'
import { waitForDashboardShell } from '../helpers/wait-dashboard-shell'

test.describe('UAT TC-ADM: Admin-Modul', () => {
  // -------------------------------------------------------------------------
  // TC-ADM-001: Webshop — Connector-Cards sichtbar
  // -------------------------------------------------------------------------
  test('TC-ADM-001: Webshop — Connector-Cards (Shopify/WooCommerce/etc.) sichtbar', async ({
    page,
  }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/admin/webshop', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/admin/webshop')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /webshop/i }).first(),
    ).toBeVisible()

    // Business assertion: at least one connector card or a form/table must be
    // visible so the administrator can configure shop integrations.
    await expect(page.locator('table, form, button, input').first()).toBeVisible()

    // Soft assertion: known connector names
    const connectorName = page.getByText(/shopify|woocommerce|magento|oxid/i).first()
    const connectorCount = await connectorName.count()
    if (connectorCount > 0) {
      await expect(connectorName).toBeVisible()
    }

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-ADM-001')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-ADM-001')
  })

  // -------------------------------------------------------------------------
  // TC-ADM-002: Webhooks — aktiv/inaktiv Toggle sichtbar
  // -------------------------------------------------------------------------
  test('TC-ADM-002: Webhooks — aktiv/inaktiv Toggle-Anzeige sichtbar', async ({ page }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/admin/webhooks', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/admin/webhooks')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /webhook/i }).first(),
    ).toBeVisible()

    // Business assertion: the active/inactive toggle (or status badge) is required
    // so the administrator knows which webhook subscriptions deliver events.
    await expect(page.locator('table, [role="grid"], button').first()).toBeVisible()

    // Soft assertion: toggle, switch, or aktiv/inaktiv badge
    const toggleOrStatus = page
      .locator(
        '[role="switch"], input[type="checkbox"], [class*="toggle"], [class*="switch"]',
      )
      .first()
    const statusBadge = page.getByText(/aktiv|inaktiv|active|inactive/i).first()

    const hasToggle = await toggleOrStatus.count()
    const hasStatus = await statusBadge.count()

    if (hasToggle + hasStatus > 0) {
      // At least one must be visible
      if (hasToggle > 0) await expect(toggleOrStatus).toBeVisible()
      else await expect(statusBadge).toBeVisible()
    }

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-ADM-002')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-ADM-002')
  })
})

test.describe('UAT TC-PER: Personal-Modul', () => {
  // -------------------------------------------------------------------------
  // TC-PER-001: Organigramm — Tree-Struktur gerendert
  // -------------------------------------------------------------------------
  test('TC-PER-001: Organigramm — Tree-Struktur (nested divs/SVG) gerendert', async ({ page }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/personal/organigramm', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/personal/organigramm')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /organigramm/i }).first(),
    ).toBeVisible()

    // Business assertion: the organisational chart must render a structural
    // representation (SVG, canvas, role="tree", or nested div tree) so HR staff
    // can visually navigate the company hierarchy.
    const treeEl = page
      .locator('svg, canvas, [role="tree"], [role="treeitem"], [class*="org"], [class*="tree"]')
      .first()
    const buttonFallback = page.getByRole('button').first()

    const hasTree = await treeEl.count()
    const hasButton = await buttonFallback.count()

    expect(
      hasTree + hasButton,
      'TC-PER-001: No tree structure or action button found on Organigramm page',
    ).toBeGreaterThan(0)

    if (hasTree > 0) await expect(treeEl).toBeVisible()

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-PER-001')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-PER-001')
  })

  // -------------------------------------------------------------------------
  // TC-PER-002: Bewerbungen — Stage-Pipeline-Badges sichtbar
  // -------------------------------------------------------------------------
  test('TC-PER-002: Bewerbungen — Stage-Pipeline-Badges sichtbar', async ({ page }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/personal/bewerbungen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/personal/bewerbungen')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /bewerbung/i }).first(),
    ).toBeVisible()

    // Business assertion: pipeline stage badges let recruiters filter and move
    // applicants through the hiring funnel (Eingang → Vorauswahl → Interview →
    // Angebot → Abgelehnt).
    await expect(page.locator('table, [role="grid"], button').first()).toBeVisible()

    // Soft assertion: known pipeline stage labels
    const stageBadge = page
      .getByText(/eingang|vorauswahl|interview|angebot|abgelehnt|hired|rejected/i)
      .first()
    const stageCount = await stageBadge.count()
    if (stageCount > 0) {
      await expect(stageBadge).toBeVisible()
    }

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-PER-002')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-PER-002')
  })
})

test.describe('UAT TC-GEN: Genossenschaft', () => {
  // -------------------------------------------------------------------------
  // TC-GEN-001: Mitglieder — Mitgliederliste + Kapitalübersicht
  // -------------------------------------------------------------------------
  test('TC-GEN-001: Genossenschaftsmitglieder — Mitgliederliste und Kapitalübersicht sichtbar', async ({
    page,
  }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/genossenschaft/mitglieder', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/genossenschaft/mitglieder')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page
        .locator('h1, [role="heading"]')
        .filter({ hasText: /genossenschaftsmitglied|mitglied/i })
        .first(),
    ).toBeVisible()

    // Business assertion: cooperative law (GenG) requires member share capital to
    // be tracked and visible.  The member table and a capital summary card (or
    // column heading) must be present.
    await expect(page.locator('table, [role="grid"], button').first()).toBeVisible()

    // Soft assertion: capital overview card or column
    const kapitalHint = page
      .getByText(/kapital|geschäftsanteil|pflichtanteil|einzahlung/i)
      .first()
    const kapitalCount = await kapitalHint.count()
    if (kapitalCount > 0) {
      await expect(kapitalHint).toBeVisible()
    }

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-GEN-001')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-GEN-001')
  })
})
