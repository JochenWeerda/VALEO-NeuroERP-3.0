import { expect, test } from '@playwright/test'

import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

const backendBase = process.env.E2E_BACKEND_URL ?? 'http://127.0.0.1:8000'
const token = process.env.E2E_API_DEV_TOKEN ?? 'dev-token'

test.describe('Fuetterungsberatung — nativer Rationslebenszyklus', () => {
  test.describe.configure({ timeout: 150_000 })

  test('Entwurf wird in Worklist geoeffnet, geprueft, freigegeben und aktiviert', async ({ page, request }) => {
    // Lifecycle tables intentionally reference the canonical tenant registry.
    const tenant = process.env.E2E_TENANT_ID ?? '00000000-0000-0000-0000-000000000001'
    const suffix = Date.now()
    const headers = {
      Authorization: `Bearer ${token}`,
      'X-Tenant-ID': tenant,
    }
    const health = await request.get(`${backendBase}/api/v1/agrar/rations-optimization/health`, { headers }).catch(() => null)
    test.skip(!health?.ok(), `Backend nicht erreichbar unter ${backendBase}.`)

    const groupResponse = await request.post(
      `${backendBase}/api/v1/agrar/rations-optimization/lifecycle/groups`,
      {
        headers,
        data: {
          name: `Frischmelker E2E ${suffix}`,
          animal_type: 'dairy_cow',
          animal_count: 48,
          body_mass_kg: 680,
          target_milk_kg: 38,
          feeding_system: 'TMR',
        },
      },
    )
    expect(groupResponse.ok()).toBeTruthy()
    const group = await groupResponse.json() as { id: string }

    const rationResponse = await request.post(
      `${backendBase}/api/v1/agrar/rations-optimization/lifecycle/rations`,
      {
        headers,
        data: {
          group_id: group.id,
          name: `Frischmelker Sommer E2E ${suffix}`,
          source: 'solver',
          comment: 'Browser-Abnahme',
          snapshot: {
            components: [{ name: 'Grassilage', amount_fm_kg: 18.5 }],
            mobile: { groupName: `Frischmelker E2E ${suffix}`, targetAnimals: 48, components: [] },
          },
        },
      },
    )
    expect(rationResponse.ok()).toBeTruthy()
    const ration = await rationResponse.json() as { id: string }

    await page.addInitScript(({ authToken, tenantId }) => {
      localStorage.setItem('access_token', authToken)
      localStorage.setItem('tenant_id', tenantId)
    }, { authToken: token, tenantId: tenant })

    await page.goto('/portal/rationsoptimierung?view=rations', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
    await expect(page.getByText(`Frischmelker Sommer E2E ${suffix}`)).toBeVisible()
    await page.getByText(`Frischmelker Sommer E2E ${suffix}`).click()
    await expect(page).toHaveURL(new RegExp(`ration_id=${ration.id}`))
    await expect(page.getByTestId('ration-lifecycle-detail')).toBeVisible()

    await page.getByRole('button', { name: 'Zur Pruefung' }).click()
    await page.getByRole('button', { name: 'Status wechseln' }).click()
    await expect(page.getByRole('button', { name: 'Freigeben' })).toBeVisible()

    await page.getByRole('button', { name: 'Freigeben' }).click()
    await page.getByRole('button', { name: 'Status wechseln' }).click()
    await expect(page.getByRole('button', { name: 'Jetzt aktivieren' })).toBeVisible()

    await page.getByRole('button', { name: 'Jetzt aktivieren' }).click()
    await page.getByRole('button', { name: 'Status wechseln' }).click()
    await expect(page.getByText(/Status wurde auf.*active/)).toBeVisible()

    const active = await request.get(
      `${backendBase}/api/v1/agrar/rations-optimization/lifecycle/active-rations`,
      { headers },
    )
    expect(active.ok()).toBeTruthy()
    const activeRations = await active.json() as Array<{ ration_id: string }>
    expect(activeRations.some((item) => item.ration_id === ration.id)).toBeTruthy()
  })
})
