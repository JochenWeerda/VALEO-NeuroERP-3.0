/**
 * E2E: Process Kernel — Flow Spines, Approvals, Command Monitor
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Process Kernel', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Flow Spine Studio lädt', async ({ page }) => {
    await page.goto('/admin/flow-spine-studio')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('AI Approvals lädt', async ({ page }) => {
    await page.goto('/admin/ai-approvals')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: Flow Spine Catalog', async ({ request }) => {
    const resp = await request.get('/api/v1/flow-spines/catalog')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('API: Process Approval Density', async ({ request }) => {
    const resp = await request.get('/api/v1/process/approval-density/overview')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('API: Low Stock Agent Status', async ({ request }) => {
    const resp = await request.get('/api/v1/agents/low-stock/status')
    expect([200, 401, 404]).toContain(resp.status())
  })
})
