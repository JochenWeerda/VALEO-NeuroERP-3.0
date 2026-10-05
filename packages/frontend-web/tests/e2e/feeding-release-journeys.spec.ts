/**
 * FEED-REL-047: Release-Journeys der Fütterungsberatung (Lastenheft Phase 6).
 *
 * Journey A: Ration → Editor-Bewertung → Freigabe → Bericht
 * Journey B: Plan → mobile Ist-Dokumentation
 * Journey C: Beratungsfall → Beratungs-Maske
 *
 * Läuft gegen den Dev-Server (Vite-Proxy) + echtes Backend; API-Setup über den
 * Playwright-Request-Context mit Dev-Token. Die Pilotabnahme durch einen
 * fachkundigen Fütterungsberater bleibt ein Auftraggeber-Gate und ist hier
 * bewusst NICHT simuliert.
 */
import { test, expect, type APIRequestContext } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

const ROOT = '/api/v1/agrar/rations-optimization'
const TENANT = process.env.E2E_TENANT_ID ?? '00000000-0000-0000-0000-000000000001'
const API_HEADERS = {
  Authorization: `Bearer ${process.env.E2E_API_DEV_TOKEN ?? 'dev-token'}`,
  'X-Tenant-Id': TENANT,
}

function suffix(): string {
  return Math.random().toString(16).slice(2, 10)
}

async function apiPost(request: APIRequestContext, path: string, data: unknown,
                       okStatus = 201): Promise<Record<string, any>> {
  const response = await request.post(path, { headers: API_HEADERS, data })
  expect(response.status(), `${path}: ${await response.text()}`).toBe(okStatus)
  return response.json()
}

async function approvedRation(request: APIRequestContext, tag: string): Promise<{
  rationId: string; rationName: string; versionId: string; groupId: string
}> {
  const group = await apiPost(request, `${ROOT}/lifecycle/groups`, {
    name: `Release ${tag}`, animal_count: 24, feeding_system: 'TMR',
    profile_code: 'fresh_cow', pregnancy_status: 'unknown',
  })
  await apiPost(request, `${ROOT}/feeding/requirement-profiles`, {
    group_id: group.id, inputs: { milk_kg_day: 28 },
  })
  const ration = await apiPost(request, `${ROOT}/lifecycle/rations`, {
    group_id: group.id, name: `ReleaseRation ${tag}`,
    snapshot: { components: [
      { feed_id: `rel-gras-${tag}`, name: 'Grassilage', kg_fm: 24, mixing_sequence: 1 },
      { feed_id: `rel-mais-${tag}`, name: 'Maissilage', kg_fm: 14, mixing_sequence: 2 },
    ] },
  })
  const versionId = ration.latest_version_id as string
  for (const [target, expected] of [['in_review', 'draft'], ['approved', 'in_review']] as const) {
    const transition = await request.post(`${ROOT}/lifecycle/versions/${versionId}/transitions`, {
      headers: API_HEADERS,
      data: { target_status: target, expected_status: expected, reason: 'Release-Journey' },
    })
    expect(transition.status(), await transition.text()).toBe(200)
  }
  return { rationId: ration.id, rationName: `ReleaseRation ${tag}`, versionId, groupId: group.id }
}

test.describe('Fütterungsberatung Release-Journeys (FEED-REL-047)', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Journey A: Ration → Editor → Freigabe → Bericht', async ({ page, request }) => {
    const tag = suffix()
    const setup = await approvedRation(request, tag)

    // Editor-Einstieg: Worklist zeigt die Ration, Klick öffnet den Editor
    await page.goto('/futtermittel/rationseditor')
    const worklistLink = page.getByRole('link', { name: setup.rationName })
    await expect(worklistLink).toBeVisible()
    await worklistLink.click()
    await expect(page.getByRole('heading', { name: setup.rationName })).toBeVisible()
    await expect(page.getByLabel(/Menge Grassilage/)).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Bewertung' })).toBeVisible()

    // Plan publizieren + Bericht erzeugen (Berichtsvertrag aus 039)
    const plan = await apiPost(request, `${ROOT}/feeding/plans/publish`, {
      source_ration_version_id: setup.versionId, animal_count: 24,
      dosing_step_kg: '0.5', rounding_mode: 'nearest',
      valid_from: new Date().toISOString().slice(0, 10),
      reason: 'Release-Journey A', idempotency_key: `rel-a-${tag}`,
    })
    const report = await apiPost(request, `${ROOT}/feeding/reports`, {
      report_type: 'feeding_plan', profile: 'farmer', source_ref: plan.id,
    })
    expect(report.content.loads.length).toBeGreaterThan(0)
    const csv = await request.get(`${ROOT}/feeding/reports/${report.id}/csv`,
                                  { headers: API_HEADERS })
    expect(csv.status()).toBe(200)
    expect(await csv.text()).toContain('Grassilage')
  })

  test('Journey B: Plan → mobile Ist-Dokumentation', async ({ page, request }) => {
    const tag = suffix()
    const setup = await approvedRation(request, tag)
    await apiPost(request, `${ROOT}/feeding/plans/publish`, {
      source_ration_version_id: setup.versionId, animal_count: 24,
      dosing_step_kg: '0.5', rounding_mode: 'nearest',
      valid_from: new Date().toISOString().slice(0, 10),
      reason: 'Release-Journey B', idempotency_key: `rel-b-${tag}`,
    })

    await page.goto('/futtermittel/fuetterungsdokumentation-mobil')
    // aktueller Plan wird als Stallanweisung angeboten (Gruppe + Mischfolge)
    await expect(page.getByText(/Jetzt füttern/).first()).toBeVisible()
    await expect(page.getByText('Mischfolge und SOLL-Mengen')).toBeVisible()
    await expect(page.getByText('Grassilage')).toBeVisible()
  })

  test('Journey C: Beratungsfall → Beratungs-Maske', async ({ page, request }) => {
    const tag = suffix()
    const feedingCase = await apiPost(request, `${ROOT}/feeding/consulting-cases`, {
      title: `Release Fall ${tag}`, case_type: 'visit',
      initial_situation: 'Release-Journey C prueft die Beratungskette',
    })
    await apiPost(request, `${ROOT}/feeding/consulting-cases/${feedingCase.id}/observations`, {
      category: 'fuetterung', text: 'Journey-Beobachtung fuer den Releasetest',
      client_ref: `rel-c-${tag}`,
    })

    await page.goto('/futtermittel/beratung')
    await expect(page.getByText(`Release Fall ${tag}`)).toBeVisible()
    await page.getByText(`Release Fall ${tag}`).click()
    await expect(page.getByText('Journey-Beobachtung fuer den Releasetest')).toBeVisible()
  })
})
