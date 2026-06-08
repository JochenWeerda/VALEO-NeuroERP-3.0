import { expect, test } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

const APP_ROUTES = [
  { path: '/crm', breadcrumb: /Crm/i },
  { path: '/crm/lead/router-smoke', breadcrumb: /Detail/i },
  { path: '/einkauf/rechnung-abgleich/router-smoke', breadcrumb: /Detail/i },
] as const

test.describe('TanStack router infrastructure', () => {
  for (const route of APP_ROUTES) {
    test(`renders ${route.path} without a router context failure`, async ({ page }) => {
      const errors: string[] = []
      page.on('pageerror', (error) => errors.push(error.message))
      page.on('console', (message) => {
        if (message.type() === 'error') errors.push(message.text())
      })

      await prepareE2EAuth(page)
      await page.goto(route.path, { waitUntil: 'domcontentloaded' })

      await expect(page.getByTestId('page-root')).toBeVisible()
      await expect(page.getByRole('navigation', { name: 'Breadcrumb' })).toContainText(route.breadcrumb)
      await expect(page.locator('body')).not.toContainText(
        /useNavigate\(\) may be used only|useLocation\(\) may be used only|Unexpected Application Error/i,
      )

      expect(errors.filter((message) => /router context|Unexpected Application Error/i.test(message))).toEqual([])
    })
  }

  test('renders public login outside the dashboard shell', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'domcontentloaded' })
    await expect(page.getByTestId('page-root')).toHaveCount(0)
    await expect(page.locator('body')).not.toContainText(/Unexpected Application Error/i)
  })

  test('renders public verification outside the dashboard shell', async ({ page }) => {
    await page.goto('/verify/invoice/R-42/router-smoke', { waitUntil: 'domcontentloaded' })
    await expect(page.getByTestId('page-root')).toHaveCount(0)
    await expect(page.locator('body')).not.toContainText(/Unexpected Application Error/i)
  })

  test('renders the portal layout independently', async ({ page }) => {
    await page.goto('/portal', { waitUntil: 'domcontentloaded' })
    await expect(page.locator('body')).not.toContainText(
      /useNavigate\(\) may be used only|Unexpected Application Error/i,
    )
  })

  test('redirects a known legacy alias to its canonical URL', async ({ page }) => {
    await prepareE2EAuth(page)
    await page.goto('/crm/kim', { waitUntil: 'domcontentloaded' })
    await expect(page).toHaveURL(/\/crm$/)

    await page.goto('/vertrag/router-smoke', { waitUntil: 'domcontentloaded' })
    await expect(page).toHaveURL(/\/kontrakte\/router-smoke$/)
  })

  test('renders the not-found page for an unknown URL', async ({ page }) => {
    await prepareE2EAuth(page)
    await page.goto('/router-smoke/unknown-url', { waitUntil: 'domcontentloaded' })
    await expect(page.locator('body')).toContainText(/nicht gefunden|not found/i)
  })
})
