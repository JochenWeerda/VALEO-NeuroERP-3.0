import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

test.describe('Fuetterungsberatung - hybride Aufgabenarchitektur', () => {
  test('Portal startet nativ und laedt den Solver erst nach Aufgabenwahl', async ({ page }) => {
    await page.goto('/portal/rationsoptimierung', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByTestId('feed-advice-cockpit')).toBeVisible()
    await expect(page.getByTestId('tile-grid')).toBeVisible()
    await expect(page.getByTestId('tile-ration_planen')).toBeVisible()
    await expect(page.getByRole('button', { name: /Demo starten/i })).toHaveCount(0)

    await page.getByTestId('tile-ration_planen').click()

    await expect(page).toHaveURL(/\/portal\/rationsoptimierung\?mode=expert/)
    await expect(page.getByTestId('feed-advice-task-workspace')).toBeVisible()
    await expect(page.getByRole('link', { name: /zur fuetterungsuebersicht/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /Demo starten/i }).first()).toBeVisible()
  })
})

