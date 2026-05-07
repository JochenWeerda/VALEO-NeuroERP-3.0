import { expect, test } from '@playwright/test'

import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * Schneller UI-Smoke: Dashboard → Demo-Flow → Workbench (ohne Compound-PDF).
 * Benötigt erreichbares Backend für POST …/optimize/demo (wie Compound-E2E).
 */
test.describe('Rationsoptimierung — Smoke', () => {
  test.describe.configure({ timeout: 150_000 })

  test('Demo starten lädt LP-Ergebnis und zeigt Futtermittel-Tabelle', async ({
    page,
    request,
  }) => {
    const backendBase = process.env.E2E_BACKEND_URL ?? 'http://127.0.0.1:8000'
    const devBearer = process.env.E2E_API_DEV_TOKEN ?? 'dev-token'
    let backendOk = false
    try {
      const health = await request.get(`${backendBase}/api/v1/agrar/rations-optimization/health`, {
        headers: { Authorization: `Bearer ${devBearer}` },
      })
      backendOk = health.ok()
    } catch {
      backendOk = false
    }
    test.skip(
      !backendOk,
      `Backend nicht erreichbar unter ${backendBase} — uvicorn mit Rations-API starten.`,
    )

    await page.goto('/futtermittel/rationsoptimierung', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await Promise.all([
      page.waitForResponse(
        (r) =>
          r.url().includes('/rations-optimization/optimize/demo') &&
          r.request().method() === 'POST' &&
          r.ok(),
        { timeout: 120_000 },
      ),
      page.getByRole('button', { name: /Demo starten/i }).first().click(),
    ])

    await expect(page.locator('#feed-table')).toBeVisible({ timeout: 60_000 })
    const rows = page.locator('#feed-table table tbody tr')
    await expect(rows.first()).toBeVisible({ timeout: 30_000 })
    await expect(rows).not.toHaveCount(0)
  })
})
