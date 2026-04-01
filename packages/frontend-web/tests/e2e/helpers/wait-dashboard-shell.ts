import type { Page } from '@playwright/test'

/**
 * Wartet auf das gerenderte Dashboard (AppShell) nach Vite-Lazy-Load.
 * Ohne diese Wartezeit schlagen Smokes fehl, weil zunächst nur der PageLoader (ohne main) sichtbar ist.
 */
export async function waitForDashboardShell(page: Page, timeout = 60_000): Promise<void> {
  await page.locator('main[role="main"]').first().waitFor({ state: 'visible', timeout })
}
