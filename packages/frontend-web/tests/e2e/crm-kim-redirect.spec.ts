/**
 * KIM-Deep-Link landet in der nativen Kundenakte, inklusive ?tab=.
 */
import { expect, test } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test('KIM with customer and tab redirects to the native Akte', async ({ page }) => {
  await prepareE2EAuth(page)
  await page.goto('/crm/kim?id=GAP00216&tab=chef', { waitUntil: 'domcontentloaded' })
  await expect(page).toHaveURL(/\/crm\/kunden\/GAP00216\?tab=chef/)
})

test('Verkaufs-Stamm with id opens the native Akte', async ({ page }) => {
  await prepareE2EAuth(page)
  await page.goto('/verkauf/kunden-stamm/GAP00216', { waitUntil: 'domcontentloaded' })
  await expect(page).toHaveURL(/\/crm\/kunden\/GAP00216/)
})

test('Kunden-Cockpit with id opens the native Akte', async ({ page }) => {
  await prepareE2EAuth(page)
  await page.goto('/crm/kunden-cockpit?id=GAP00216&tab=geo', { waitUntil: 'domcontentloaded' })
  await expect(page).toHaveURL(/\/crm\/kunden\/GAP00216\?tab=geo/)
})
