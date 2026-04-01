import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * Smoke: Service-to-Customer Kernpfad (Liste, Field-Service inkl. Neu, Flow-Spine).
 * Voraussetzung: Frontend dev server (z. B. Port 3000), wie bei anderen E2E-Smokes.
 * Dateiendung `.e2e.ts` — Root-ESLint ignoriert `*.spec.ts`.
 */
const SERVICE_ROUTES: { path: string }[] = [
  { path: '/service/anfragen' },
  { path: '/agribusiness/field-service-tasks' },
  { path: '/agribusiness/field-service-tasks/neu' },
  { path: '/workflow/flow-spine-service-to-customer' },
]

test.describe('Service-to-Customer Smoke', () => {
  for (const route of SERVICE_ROUTES) {
    test(`route ${route.path} lädt ohne Dashboard-Fallback`, async ({ page }) => {
      await page.goto(route.path, { waitUntil: 'domcontentloaded' })
      await waitForDashboardShell(page)

      await expect(page.getByRole('heading', { name: /app starter/i })).toHaveCount(0)
      await expect(page.getByText(/fehler beim laden der seite/i)).toHaveCount(0)

      await expect(page).toHaveURL(
        new RegExp(`${route.path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|\\?)`),
      )

      await expect(page.locator('main, [data-page], [data-testid="page-root"]').first()).toBeVisible()
    })
  }

  test('Field-Service Bearbeiten-Route (Demo-ID) — Shell ohne Dashboard-Fallback', async ({ page }) => {
    await page.goto('/agribusiness/field-service-tasks/fst-seed-001/bearbeiten', {
      waitUntil: 'domcontentloaded',
    })
    await waitForDashboardShell(page)

    await expect(page.getByRole('heading', { name: /app starter/i })).toHaveCount(0)
    await expect(page.getByText(/fehler beim laden der seite/i)).toHaveCount(0)
    await expect(page).toHaveURL(/fst-seed-001\/bearbeiten/)
    await expect(page.locator('main, [data-page], [data-testid="page-root"]').first()).toBeVisible()
  })
})
