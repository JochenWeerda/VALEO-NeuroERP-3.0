import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

function inDays(days: number): string {
  const date = new Date()
  date.setDate(date.getDate() + days)
  date.setHours(9, 0, 0, 0)
  return date.toISOString()
}

test('Planungskalender rendert Layer und navigiert aus Termin', async ({ page }) => {
  await page.route('**/api/v1/planung/kalender**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'e2e-frist',
          layer: 'fristen',
          item_type: 'frist',
          title: 'Ende Fruehbezugsrabatt',
          starts_at: inDays(2),
          all_day: true,
          status: 'projected',
          object_route: '/kontrakte/e2e-kontrakt',
          object_screen_id: 'agrar/kontrakte',
        },
        {
          id: 'e2e-personal',
          layer: 'personal',
          item_type: 'frist',
          title: 'Sachkunde laeuft ab',
          starts_at: inDays(3),
          all_day: true,
          status: 'projected',
          object_route: '/compliance/sachkunde/e2e',
          object_screen_id: 'compliance/sachkunde',
        },
      ]),
    })
  })

  await page.goto('/planung/kalender', { waitUntil: 'domcontentloaded' })
  await waitForDashboardShell(page)

  await expect(page.getByTestId('planung-kalender')).toBeVisible()
  await expect(page.getByTestId('calendar-renderer')).toBeVisible()
  await expect(page.getByTestId('calendar-deadline-e2e-frist')).toBeVisible()
  await expect(page.getByTestId('calendar-item-e2e-personal')).toHaveCount(0)

  await page.getByTestId('calendar-layer-personal').click()
  await expect(page.getByTestId('calendar-item-e2e-personal')).toBeVisible()

  await page.getByTestId('calendar-item-e2e-frist').click()
  await expect(page).toHaveURL(/\/kontrakte\/e2e-kontrakt/)
})
