import path from 'node:path'

import { expect, test } from '@playwright/test'

import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/** PDF mit Textlayer (scripts/generate_rations_e2e_compound_pdf.py). */
const COMPOUND_FIXTURE_PDF = path.join(
  process.cwd(),
  'tests',
  'fixtures',
  'rations',
  'e2e-compound-label.pdf',
)

const PRODUCT_SNIPPET = /Milchleistungsfutter Test E2E/

/** Deutsche Zahlen wie „12,3“ oder „–“. */
function parseDeDecimal(cell: string): number | null {
  const t = cell.trim()
  if (!t || t === '–' || t === '-') return null
  const normalized = t.replace(/\./g, '').replace(',', '.')
  const n = Number(normalized)
  return Number.isFinite(n) ? n : null
}

test.describe('Rationsoptimierung — Compound-PDF Upload', () => {
  test.describe.configure({ timeout: 150_000 })

  test('Wizard: Upload + ME/sidP > 0; Workbench: gleiche Zeile ME > 0', async ({
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
      `Backend nicht erreichbar unter ${backendBase} — bitte uvicorn starten (Rations-API).`,
    )

    await page.goto('/futtermittel/rationsoptimierung', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await page.getByRole('button', { name: /Neue Ration erstellen/i }).first().click()
    await expect(page.getByRole('heading', { name: /Schritt 1 von 3/i })).toBeVisible()

    await page.getByRole('button', { name: 'Weiter' }).click()
    await expect(page.getByText(/Schritt 2 von 3/i)).toBeVisible()

    const upload = page.getByTestId('rations-compound-upload-input')
    await expect(upload).toBeAttached()

    const [res] = await Promise.all([
      page.waitForResponse(
        (r) =>
          r.url().includes('/compound-feed/upload') &&
          r.request().method() === 'POST' &&
          r.ok(),
        { timeout: 60_000 },
      ),
      upload.setInputFiles(COMPOUND_FIXTURE_PDF),
    ])
    expect(res.status()).toBe(200)

    await expect(page.getByText(PRODUCT_SNIPPET).first()).toBeVisible({ timeout: 15_000 })

    // Futtermittel-Tabelle (Schritt 2): Spalten … TM %, ME, sidP, …
    const wizardRow = page
      .locator('main table tbody tr')
      .filter({ hasText: PRODUCT_SNIPPET })
      .first()
    await expect(wizardRow).toBeVisible()
    const wCells = wizardRow.locator('td')
    const wizardMe = parseDeDecimal(await wCells.nth(4).innerText())
    const wizardSidp = parseDeDecimal(await wCells.nth(5).innerText())
    expect(wizardMe).not.toBeNull()
    expect(wizardMe!).toBeGreaterThan(1)
    expect(wizardSidp).not.toBeNull()
    expect(wizardSidp!).toBeGreaterThan(10)

    await page.getByRole('button', { name: 'Weiter' }).click()
    await expect(page.getByText(/Schritt 3 von 3/i)).toBeVisible()

    await Promise.all([
      page.waitForResponse(
        (r) =>
          r.url().includes('/optimize/from-profile') &&
          r.request().method() === 'POST' &&
          r.ok(),
        { timeout: 120_000 },
      ),
      page.getByRole('button', { name: 'Optimierung starten' }).click(),
    ])

    await expect(page.getByRole('button', { name: /^Optimieren$/ })).toBeVisible({
      timeout: 30_000,
    })

    const wbRow = page.locator('#feed-table table tbody tr').filter({ hasText: PRODUCT_SNIPPET }).first()
    await expect(wbRow).toBeVisible({ timeout: 15_000 })
    const wbCells = wbRow.locator('td')
    const wbMe = parseDeDecimal(await wbCells.nth(4).innerText())
    expect(wbMe).not.toBeNull()
    expect(wbMe!).toBeGreaterThan(0.05)
  })
})
