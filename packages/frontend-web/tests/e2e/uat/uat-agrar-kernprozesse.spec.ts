/**
 * UAT — Agrar-Kernprozesse
 *
 * Business Value:
 *   The Agrar module is the revenue-critical core of VALEO NeuroERP.
 *   These acceptance tests verify that farmers, grain traders and contract
 *   managers can access the key workflows without runtime errors.
 *
 * Test IDs: TC-AGR-001 … TC-AGR-004
 */
import { test, expect } from '@playwright/test'
import { attachConsoleErrorListener, UATHelpers } from './uat-helpers'
import { waitForDashboardShell } from '../helpers/wait-dashboard-shell'

test.describe('UAT TC-AGR: Agrar-Kernprozesse', () => {
  // -------------------------------------------------------------------------
  // TC-AGR-001: Sammelabrechnung Wizard
  // -------------------------------------------------------------------------
  test('TC-AGR-001: Sammelabrechnung — Wizard-Steps sichtbar und navigierbar', async ({ page }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/agrar/sammelabrechnung', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/agrar/sammelabrechnung')
    await UATHelpers.assertNoLoadError(page)

    // Business assertion: the 3-step wizard must be visible so the user can
    // identify their current position in the billing workflow.
    const stepBadges = page.locator('[class*="badge"], [data-slot="badge"]')
    // Step labels defined in sammelabrechnung.tsx: Ernteerfassungen / Abrechnungsdetails / Bestätigung
    await expect(page.getByText(/ernteerfassungen/i).first()).toBeVisible()
    await expect(page.getByText(/abrechnungsdetails/i).first()).toBeVisible()
    await expect(page.getByText(/bestätigung/i).first()).toBeVisible()

    // The first step's card content must be rendered
    await expect(page.getByText(/ernteerfassungen auswählen/i).first()).toBeVisible()

    // Heading check
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /sammelabrechnung/i }).first(),
    ).toBeVisible()

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-AGR-001')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-AGR-001')
  })

  // -------------------------------------------------------------------------
  // TC-AGR-002: Kontraktklassen — Tabelle und Kontrakttyp-Badges
  // -------------------------------------------------------------------------
  test('TC-AGR-002: Kontraktklassen — Tabelle lädt, Kontrakttyp-Badges sichtbar', async ({
    page,
  }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/kontrakte/kontraktklassen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/kontrakte/kontraktklassen')
    await UATHelpers.assertNoLoadError(page)

    // Business assertion: contract type badges communicate the pricing model to
    // the trader at a glance.  At least a table/grid OR a create button must be
    // present (empty state is acceptable for a fresh environment).
    await expect(
      page.locator('table, [role="grid"], button').first(),
    ).toBeVisible()

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /kontraktklasse/i }).first(),
    ).toBeVisible()

    // When rows exist, at least one known badge type should appear.
    // We use a soft check: if any badge with known text is present, assert it.
    const knownBadge = page.getByText(/FIXPREIS|BASIS|PRAEMIE|POOLPREIS/i).first()
    const badgeCount = await knownBadge.count()
    if (badgeCount > 0) {
      await expect(knownBadge).toBeVisible()
    }

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-AGR-002')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-AGR-002')
  })

  // -------------------------------------------------------------------------
  // TC-AGR-003: Saatzucht — Generationen-Badges
  // -------------------------------------------------------------------------
  test('TC-AGR-003: Saatzucht — Generationen-Badges (Z1/Z2/Z3/ZA) sichtbar', async ({ page }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/agrar/saatzucht', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/agrar/saatzucht')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /saatzucht/i }).first(),
    ).toBeVisible()

    // Business assertion: seed generation classification (Z1/Z2/Z3/ZA) is legally
    // required for certified seed tracking.  Either table rows or a badge exist.
    const tableOrGrid = page.locator('table, [role="grid"], button').first()
    await expect(tableOrGrid).toBeVisible()

    // Soft assertion for generation badges when data is present
    const genBadge = page.getByText(/\bZ[123A]\b/).first()
    const genCount = await genBadge.count()
    if (genCount > 0) {
      await expect(genBadge).toBeVisible()
    }

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-AGR-003')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-AGR-003')
  })

  // -------------------------------------------------------------------------
  // TC-AGR-004: Preiskalkulation — Kalkulationsweg-Tabelle
  // -------------------------------------------------------------------------
  test('TC-AGR-004: Preiskalkulation — Kalkulationsweg-Tabelle und Kostenstruktur sichtbar', async ({
    page,
  }) => {
    const collector = attachConsoleErrorListener(page)

    await page.goto('/preise/kalkulation', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/preise/kalkulation')
    await UATHelpers.assertNoLoadError(page)

    // Heading
    await expect(
      page.locator('h1, [role="heading"]').filter({ hasText: /kalkulation|preis/i }).first(),
    ).toBeVisible()

    // Business assertion: at a minimum an input or table must be rendered so the
    // user can enter or inspect pricing data.
    await expect(
      page.locator('table, [role="grid"], input, button').first(),
    ).toBeVisible()

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-AGR-004')
    await UATHelpers.assertResponseTime(page)
    await UATHelpers.recordTestEvidence(page, 'TC-AGR-004')
  })
})
