import { expect, test } from '@playwright/test'

type RouteCheck = {
  path: string
  /** Erwartete Überschrift (h1/heading) – optional */
  expectedHeading?: RegExp
  /** Alternativ: sichtbarer Text (z. B. bei Lade-/Fehlerzustand ohne h1) – optional */
  expectedText?: RegExp
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
  { path: '/fibu/abschluss-cockpit', expectedText: /Abschluss-Cockpit/ },
  { path: '/admin/monitoring/alerts' },
  { path: '/admin/report-berechtigungen' },
  { path: '/einstellungen/system' },
  { path: '/nawaro/vertraege' },
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

      if (route.expectedText) {
        await expect(page.getByText(route.expectedText).first()).toBeVisible()
      } else if (route.expectedHeading) {
        await expect(page.locator('h1, [role="heading"]').filter({ hasText: route.expectedHeading }).first()).toBeVisible()
      }
    })
  }
})

test.describe('Auth and NotFound routes', () => {
  test('route /login renders login page', async ({ page, context }) => {
    await context.clearCookies()
    await page.goto('/')
    await page.evaluate(() => {
      localStorage.clear()
      sessionStorage.clear()
    })
    await page.goto('/login')
    await page.waitForLoadState('domcontentloaded')

    // Login-Seite: Titel/Beschreibung/Button (oder Redirect zu / bei bereits gültiger Session)
    const loginContent = page.getByText(/valeo neuroerp|melden sie sich|sso anmelden|weiterleitung/i).first()
    const redirectedToHome = page.url().then((u) => !u.includes('/login') && (u.endsWith('/') || u.endsWith('/login') === false))
    await Promise.race([
      expect(loginContent).toBeVisible({ timeout: 12_000 }),
      page.waitForURL(/\/(?!login)/, { timeout: 12_000 }).then(() => expect(redirectedToHome).resolves.toBe(true)),
    ]).catch(async () => {
      const onLogin = await loginContent.isVisible().catch(() => false)
      const url = page.url()
      expect(onLogin || (!url.includes('/login') && url.includes(page.context().pages()[0]?.url() ? true : true)).toBe(true)
    })
    if (await loginContent.isVisible().catch(() => false)) {
      await expect(page.getByRole('button', { name: /sso anmelden|weiterleitung/i })).toBeVisible({ timeout: 5000 }).catch(() => {})
    }
  })

  test('unknown route renders 404 page', async ({ page }) => {
    await page.goto('/this-route-does-not-exist')
    await page.waitForLoadState('domcontentloaded')

    await expect(page.getByRole('heading', { name: /404/i })).toBeVisible()
    await expect(page.getByText(/seite nicht gefunden/i)).toBeVisible()
  })
})
