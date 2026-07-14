import { expect, test } from '@playwright/test'

import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

test.describe('Kundenportal — API-Verträge', () => {
  test('Portal-Fachseiten verwenden ausschließlich den /api/v1-Prefix', async ({ page }) => {
    const portalRequests: string[] = []
    const pageErrors: string[] = []

    page.on('request', (request) => {
      const pathname = new URL(request.url()).pathname
      if (request.resourceType() !== 'document' && pathname.includes('/portal/')) {
        portalRequests.push(pathname)
      }
    })
    page.on('pageerror', (error) => pageErrors.push(error.message))

    for (const path of ['/portal/preisspiegel', '/portal/lohndienste', '/portal/empfehlungen']) {
      const previousRequestCount = portalRequests.length
      await page.goto(path, { waitUntil: 'domcontentloaded' })
      await waitForDashboardShell(page)
      await expect.poll(() => portalRequests.length).toBeGreaterThan(previousRequestCount)
      await expect(page.locator('main')).toBeVisible()
    }

    expect(portalRequests).not.toEqual([])
    expect(portalRequests.filter((pathname) => pathname.startsWith('/portal/'))).toEqual([])
    expect(pageErrors).toEqual([])
  })
})
