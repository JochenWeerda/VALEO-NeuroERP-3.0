import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * UIX-060 Omnibox-Smoke: oeffnen → tippen → "Verstanden als"-Vorschau → Enter → URL.
 * Deterministisch gegen den statischen Command-Katalog (kein Backend noetig):
 * "offene posten debitoren folkerts" trifft eindeutig die OP-Debitoren-Liste
 * und haengt den Freitext als q-Filter an (deckt die Kern-Intent-Fixture #4).
 */

const OMNIBOX_INPUT = /Aktion suchen/

async function openOmnibox(page: import('@playwright/test').Page): Promise<void> {
  await page.goto('/', { waitUntil: 'domcontentloaded' })
  await waitForDashboardShell(page)
  // Deterministisch ueber den TopBar-Such-Button (Ctrl+K haengt am Fokus).
  await page.getByRole('button', { name: /Suche/ }).click()
  await expect(page.getByPlaceholder(OMNIBOX_INPUT)).toBeVisible()
}

test.describe('UIX-060 Omnibox', () => {
  test('kompiliert Eingabe zu Navigations-Plan mit Filter und navigiert bei Enter', async ({ page }) => {
    await openOmnibox(page)

    await page.getByPlaceholder(OMNIBOX_INPUT).fill('offene posten debitoren folkerts')

    // "Verstanden als"-Vorschau erscheint mit mindestens einem Intent-Plan.
    const intentItem = page.locator('[data-mcp-action^="omnibox-intent:"]').first()
    await expect(intentItem).toBeVisible()
    await expect(intentItem).toHaveAttribute('data-omnibox-confidence', /0\.\d\d/)

    // Freitext-Filter-Chip sichtbar
    await expect(page.getByText('„folkerts"')).toBeVisible()

    await intentItem.click()

    await expect(page).toHaveURL(/\/finance\/op-debitoren\?.*q=folkerts/)
  })

  test('Overlay hat keine kritischen axe-Verstoesse', { tag: '@accessibility' }, async ({ page }) => {
    await openOmnibox(page)
    await page.getByPlaceholder(OMNIBOX_INPUT).fill('offene posten')

    const results = await new AxeBuilder({ page })
      .include('[cmdk-root]')
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze()

    const serious = results.violations.filter(
      (v) => v.impact === 'serious' || v.impact === 'critical',
    )
    expect(
      serious,
      serious.length > 0 ? JSON.stringify(serious.map((v) => ({ id: v.id, nodes: v.nodes.length })), null, 2) : undefined,
    ).toEqual([])
  })
})
