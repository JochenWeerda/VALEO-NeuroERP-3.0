import { expect, test } from '@playwright/test'

test.describe('Finance Reports Dashboard', () => {
  test('route /finance/reports renders core UI', async ({ page }) => {
    await page.goto('/finance/reports')
    await page.waitForLoadState('domcontentloaded')

    await expect(page.getByRole('heading', { name: /app starter/i })).toHaveCount(0)
    await expect(page.getByText(/fehler beim laden der seite/i)).toHaveCount(0)
    await expect(page).toHaveURL(/\/finance\/reports($|\?)/)

    await expect(page.getByText(/NeuroERP 3.0 · FIBU Suite/i)).toBeVisible()
    await expect(page.getByPlaceholder(/Konto suchen/i)).toBeVisible()
    await expect(page.getByRole('button', { name: 'Export öffnen' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Journal öffnen' })).toBeVisible()
  })
})
