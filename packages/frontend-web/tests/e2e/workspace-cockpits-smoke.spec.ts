import { test, expect } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * UIX-061 Route-Smoke: die 5 Rollen-Workspaces rendern als cockpit-Startseiten
 * mit Kachel-Grid; eine Kachel navigiert in ihre Ziel-Maske.
 */
const WORKSPACES = ['einkauf', 'verkauf', 'lager', 'fibu', 'leitung'] as const

for (const ws of WORKSPACES) {
  test(`Workspace /${ws} rendert Cockpit mit Kacheln`, async ({ page }) => {
    await page.goto(`/workspace/${ws}`, { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByTestId(`workspace-${ws}`)).toBeVisible()
    await expect(page.getByTestId('tile-grid')).toBeVisible()
    // mindestens eine Kachel ist vorhanden
    await expect(page.locator('[data-testid^="tile-"]').first()).toBeVisible()
  })
}

test('Kachel im FIBU-Cockpit navigiert in die Ziel-Maske', async ({ page }) => {
  await page.goto('/workspace/fibu', { waitUntil: 'domcontentloaded' })
  await waitForDashboardShell(page)

  const zahlungslauf = page.getByTestId('tile-zahlungslauf')
  await expect(zahlungslauf).toBeVisible()
  await zahlungslauf.click()
  await expect(page).toHaveURL(/\/fibu\/zahlungslaeufe/)
})
