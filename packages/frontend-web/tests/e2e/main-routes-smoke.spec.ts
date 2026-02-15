import { expect, test } from '@playwright/test'

type RouteCheck = {
  path: string
  expectedHeading?: RegExp
}

const MAIN_ROUTES: RouteCheck[] = [
  { path: '/sales' },
  { path: '/sales/order' },
  { path: '/sales/delivery' },
  { path: '/sales/invoice' },
  { path: '/verkauf/kunden-liste' },
  { path: '/artikel/liste' },
  { path: '/einkauf/bestellungen' },
  { path: '/einkauf/lieferschein-frachtauftrag' },
  { path: '/fibu/offene-posten' },
  { path: '/fibu/abschluss-cockpit', expectedHeading: /abschluss-cockpit|abschluss/i },
  { path: '/admin/monitoring/alerts' },
  { path: '/admin/report-berechtigungen' },
]

test.describe('Main Routes Smoke (no dashboard fallback)', () => {
  for (const route of MAIN_ROUTES) {
    test(`route ${route.path} renders target page`, async ({ page }) => {
      await page.goto(route.path)
      await page.waitForLoadState('domcontentloaded')

      // Hard guard against known routing failure: page falls back to App Starter dashboard.
      await expect(page.getByRole('heading', { name: /app starter/i })).toHaveCount(0)

      // Guard against global page-load failure fallback.
      await expect(page.getByText(/fehler beim laden der seite/i)).toHaveCount(0)

      // Basic sanity: route keeps own path.
      await expect(page).toHaveURL(new RegExp(`${route.path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|\\?)`))

      // Page should render meaningful app content.
      await expect(page.locator('main, [data-page], [data-testid="page-root"]').first()).toBeVisible()

      if (route.expectedHeading) {
        await expect(page.locator('h1, [role="heading"]').filter({ hasText: route.expectedHeading }).first()).toBeVisible()
      }
    })
  }
})

test.describe('Auth and NotFound routes', () => {
  test('route /login renders login page', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('domcontentloaded')

    await expect(page.getByRole('heading', { name: /valeo neuroerp/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /sso anmelden/i })).toBeVisible()
  })

  test('unknown route renders 404 page', async ({ page }) => {
    await page.goto('/this-route-does-not-exist')
    await page.waitForLoadState('domcontentloaded')

    await expect(page.getByRole('heading', { name: /404/i })).toBeVisible()
    await expect(page.getByText(/seite nicht gefunden/i)).toBeVisible()
  })
})
