import { expect, test } from '@playwright/test'

const currentPlan = {
  id: 'plan-version-2', plan_id: 'plan-1', group_id: 'g1', group_name: 'Hochleistung Nordstall',
  name: 'Stallplan', version_no: 2, source_ration_version_id: 'ration-v4', animal_count: 58,
  dosing_step_kg: 0.5, rounding_mode: 'nearest', valid_from: '2026-07-16', valid_until: '2026-07-31',
  reason: 'Freigabe fuer Stallarbeit', published_by: 'advisor', published_at: '2026-07-16T08:00:00Z',
  plan_status: 'current', is_stale: false,
  instructions: [
    { id: 'i1', sequence: 1, feed_id: 'mais', feed_name: 'Maissilage', kg_fm_per_animal: 10.69, raw_batch_kg: 620, target_batch_kg: 620, rounding_delta_kg: 0 },
    { id: 'i2', sequence: 2, feed_id: 'gras', feed_name: 'Grassilage', kg_fm_per_animal: 7.07, raw_batch_kg: 410, target_batch_kg: 410, rounding_delta_kg: 0 },
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
    await page.route('**/feeding/plans/current', async (route) => route.fulfill({ json: [currentPlan] }))
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
