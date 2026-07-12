import { expect, test } from '@playwright/test'

const activeRation = {
  version: 1,
  updatedAt: '2026-07-12T08:00:00.000Z',
  group: { id: 'g1', name: 'Hochleistung Nordstall', count: 58 },
  milkYield: 38,
  milkPriceEur: 0.44,
  totalCostEurDay: 6.2,
  pendfSollGKgdm: 180,
  ndfProxyGKgdm: 360,
  components: [
    { feed_id: 'mais', name: 'Maissilage', soll_kg: 620 },
    { feed_id: 'gras', name: 'Grassilage', soll_kg: 410 },
  ],
}

const controlResult = {
  tm_verzehr_kg_kuh: 7.8, vorgelegt_kg: 1030, restfutter_kg: 0, aufgenommen_fm_kg: 1030,
  tierzahl: 58, tm_pct: 40, mischgenauigkeit_pct: 0, mischgenauigkeit_ok: true,
  komponenten: [], iofc_eur_kuh: 10.52, futterkosten_eur_kuh: 6.2,
  futtertisch_temp_c: 20, umgebung_temp_c: 18, warnungen: [], anpassungsvorschlaege: [],
  schuettelbox: { struktur_gt_8mm_pct: 50, pendf_soll_g_kgdm: 180, pendf_ist_g_kgdm: 180, pendf_delta_g_kgdm: 0, status: 'gruen', selektionsrisiko: false },
}

test.describe('Mobile Fütterungsdokumentation F6', () => {
  test('SOLL → IST → Kontrolle speichert ohne horizontalen Body-Scroll', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.addInitScript((snapshot) => localStorage.setItem('valeo.rations.active-mobile.v1', JSON.stringify(snapshot)), activeRation)
    await page.route('**/feeding-control/logs?**', async (route) => route.fulfill({ json: [] }))
    await page.route('**/feeding-control/logs', async (route) => {
      if (route.request().method() !== 'POST') return route.continue()
      const payload = route.request().postDataJSON()
      expect(payload.group_id).toBe('g1')
      expect(payload.komponenten).toHaveLength(2)
      await route.fulfill({ json: { id: 'log-1', group_id: 'g1', feeding_date: '2026-07-12', ration_ref: payload.ration_ref, control_result: controlResult, created_at: '2026-07-12T08:10:00Z' } })
    })

    await page.goto('/futtermittel/fuetterungsdokumentation-mobil')
    await expect(page.getByRole('heading', { name: 'Hochleistung Nordstall' })).toBeVisible()
    await expect(page.getByText('Maissilage')).toBeVisible()
    await page.getByRole('button', { name: 'Jetzt füttern' }).click()
    await expect(page.getByText('Ist-Mengen dokumentieren')).toBeVisible()
    await page.getByRole('button', { name: /Protokoll speichern/ }).click()
    await expect(page.getByRole('heading', { name: 'Kontrolle gespeichert' })).toBeVisible()
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
    expect(overflow).toBeLessThanOrEqual(0)
  })
})