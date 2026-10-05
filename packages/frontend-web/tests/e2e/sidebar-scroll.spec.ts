import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

test('desktop sidebar scrolls to the final entry with expanded groups', async ({ page }) => {
  await page.setViewportSize({ width: 1366, height: 768 })
  await page.goto('/', { waitUntil: 'domcontentloaded' })
  await waitForDashboardShell(page)

  const sidebar = page.locator('[data-mcp-component="sidebar"]')
  const nav = sidebar.locator('nav').first()

  await expect(sidebar).toBeVisible()
  await expect(nav).toBeVisible()
  await expect(sidebar.getByRole('link', { name: /Dashboard/i })).toBeVisible()

  await sidebar.locator('nav button').evaluateAll((buttons) => {
    buttons.forEach((button) => button.click())
  })

  await nav.evaluate((element) => {
    element.scrollTop = element.scrollHeight
  })

  const canScroll = await nav.evaluate((element) => element.scrollHeight > element.clientHeight)
  const reachedBottom = await nav.evaluate((element) => element.scrollTop + element.clientHeight >= element.scrollHeight - 2)
  const lastNavItemVisible = await nav.locator('[data-mcp-nav-item]').last().isVisible()

  expect(canScroll).toBe(true)
  expect(reachedBottom).toBe(true)
  expect(lastNavItemVisible).toBe(true)
  await expect(sidebar.getByRole('link', { name: 'Einstellungen' })).toBeVisible()
})
