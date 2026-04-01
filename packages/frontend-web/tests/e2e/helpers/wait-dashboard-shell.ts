import type { Page } from '@playwright/test'

/**
 * Wartet auf das erste sichtbare `<main>` (Dashboard-AppShell oder Kundenportal).
 * Vite/React lazy: zuerst PageLoader ohne `main` — daher zwingend vor Content-Assertions.
 */
export async function waitForDashboardShell(page: Page, timeout = 60_000): Promise<void> {
  await page.locator('main').first().waitFor({ state: 'visible', timeout })
}
