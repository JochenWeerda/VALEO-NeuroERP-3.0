/**
 * UAT: Unterbrochene Annahmen — Qualitäts-Nachtrag (Laborbuch)
 *
 * Simuliert den typischen Nachtrag-Prozess: Getreideannahmen laufen ohne
 * Laborwerte an; die Qualitätsmessungen (hl-Gewicht, Feuchte, Besatz) werden
 * später seitenweise aus dem Laborbuch in die Annahmescheine nachgetragen.
 *
 * Human-Simulation: Werte in Zeilen-Inputs tippen, Batch speichern klicken.
 * Agent-Vergleich: dieselbe Kette via POST /quality-batch (Szenario im
 * Python-/API-Testlauf, siehe docs Performance-Report).
 */
import { test, expect } from '@playwright/test'
import { attachConsoleErrorListener, UATHelpers } from './uat-helpers'
import { waitForDashboardShell } from '../helpers/wait-dashboard-shell'

const API = process.env.API_URL ?? 'http://127.0.0.1:8000'
const TOKEN = process.env.API_DEV_TOKEN ?? 'dev-token'
const TENANT = process.env.TENANT_ID ?? '00000000-0000-0000-0000-000000000001'
const HEADERS = {
  Authorization: `Bearer ${TOKEN}`,
  'X-Tenant-Id': TENANT,
  'Content-Type': 'application/json',
}

test.describe('UAT TC-QNT: Qualitäts-Nachtrag für unterbrochene Annahmen', () => {
  const createdNumbers: string[] = []

  test.beforeAll(async ({ request }) => {
    // Zwei unterbrochene Annahmen anlegen (ohne Qualitätsprotokoll)
    for (const plate of ['TST-QN 001', 'TST-QN 002']) {
      const resp = await request.post(`${API}/api/v1/agrar/harvest-acceptance/`, {
        headers: HEADERS,
        data: {
          delivery_date: new Date().toISOString().slice(0, 10),
          customer_id: '019c0008-0000-7000-8000-000000000001',
          vehicle_plate: plate,
          origin_postal_code: '26789',
          origin_city: 'Leer',
        },
      })
      expect(resp.status(), 'Annahme-Anlage muss 201 liefern').toBe(201)
      const body = (await resp.json()) as { acceptance_number: string }
      createdNumbers.push(body.acceptance_number)
    }
  })

  test('TC-QNT-001: Worklist zeigt unterbrochene Annahmen, Batch-Nachtrag räumt sie ab', async ({
    page,
  }) => {
    const collector = attachConsoleErrorListener(page)
    const t0 = Date.now()

    await page.goto('/agrar/annahmen-qualitaet-nachtrag', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await UATHelpers.assertUrlRetained(page, '/agrar/annahmen-qualitaet-nachtrag')
    await UATHelpers.assertNoLoadError(page)

    await expect(
      page.locator('h1').filter({ hasText: /Qualitäts-Nachtrag/i }).first(),
    ).toBeVisible()

    // Beide angelegten Annahmen erscheinen in der Worklist
    for (const nr of createdNumbers) {
      await expect(page.getByText(nr).first()).toBeVisible()
    }

    // Menschliche Eingabe: Laborwerte in beide Zeilen tippen
    for (const nr of createdNumbers) {
      const row = page.locator('tr').filter({ hasText: nr })
      const inputs = row.locator('input')
      await inputs.nth(0).fill('14,5') // Feuchte (deutsches Dezimalkomma)
      await inputs.nth(1).fill('76.0') // hl-Gewicht
      await inputs.nth(2).fill('1.5') // Besatz
    }

    await page.getByLabel(/Labor \/ Gerät/i).fill('Laborbuch Seite 47')

    const saveButton = page.getByRole('button', { name: /Batch speichern \(2 Zeilen\)/ })
    await expect(saveButton).toBeEnabled()
    await saveButton.click()

    // Erfolg: Toast + Zeilen verschwinden aus der Worklist (Query-Invalidate)
    await expect(page.getByText(/2 von 2 Annahme\(n\) nachgetragen/).first()).toBeVisible({
      timeout: 10_000,
    })
    for (const nr of createdNumbers) {
      await expect(page.getByText(nr)).toHaveCount(0, { timeout: 10_000 })
    }

    test.info().annotations.push({
      type: 'Ladezeit',
      description: `Human-Flow Qualitäts-Nachtrag (2 Zeilen): ${Date.now() - t0} ms`,
    })

    await UATHelpers.assertNoConsoleErrors(collector, 'TC-QNT-001')
    await UATHelpers.recordTestEvidence(page, 'TC-QNT-001')
  })
})
