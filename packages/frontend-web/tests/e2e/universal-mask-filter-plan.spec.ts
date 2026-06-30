import { expect, test } from '@playwright/test'

test.describe('Universal Mask FilterPlan contract', () => {
  test('filter control creates chip and sends canonical filter_plan to tab backend', async ({ page }) => {
    const tabRequests: string[] = []

    await page.route('**/api/v1/masks/**/screen-definition', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          schemaVersion: 1,
          id: 'crm/lead',
          domain: 'crm',
          mode: 'detail',
          title: 'Lead',
          adapter: { type: 'native', sourceId: 'crm/lead', temporary: false },
          dataSources: [
            { key: 'entity', endpoint: '/api/v1/crm/leads/{entity_id}' },
            { key: 'activities', endpoint: '/api/v1/crm/leads/{entity_id}/tabs/activities', pageSize: 25 },
          ],
          tabs: [
            {
              key: 'activities',
              label: 'Aktivitaeten',
              lazy: true,
              keepAlive: true,
              tables: [
                {
                  key: 'lead_activities',
                  label: 'Aktivitaeten',
                  dataSourceKey: 'activities',
                  serverPagination: true,
                  virtualized: true,
                  pageSize: 25,
                  rowHeight: 52,
                  columns: [
                    { key: 'subject', label: 'Betreff', sortable: true, filterable: true },
                    { key: 'status', label: 'Status', sortable: true, filterable: true },
                    { key: 'owner', label: 'Zustaendig' },
                  ],
                },
              ],
            },
          ],
          layout: { preferredMode: 'desktopDense', mobileMode: 'mobileStack', touchTargetPx: 44 },
          performance: { initialPayloadBudgetKb: 48, requiresLazyTabs: true, requiresVirtualTables: true, lookupMinChars: 2 },
        }),
      })
    })

    await page.route('**/api/v1/crm/leads/filter-lead', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'filter-lead', company_name: 'Filter Lead', status: 'qualified' }),
      })
    })

    await page.route('**/api/v1/crm/leads/filter-lead/tabs/activities*', async (route) => {
      const url = new URL(route.request().url())
      tabRequests.push(url.toString())
      const rawFilterPlan = url.searchParams.get('filter_plan')
      const rows = rawFilterPlan
        ? [{ id: 'a-1', subject: 'Angebot vorbereiten', status: 'offen', owner: 'Anna' }]
        : [
            { id: 'a-1', subject: 'Angebot vorbereiten', status: 'offen', owner: 'Anna' },
            { id: 'a-2', subject: 'Rueckfrage klaeren', status: 'wartet', owner: 'Bernd' },
          ]
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tab_key: 'activities',
          table_key: 'lead_activities',
          items: rows,
          page: 1,
          limit: 25,
          total: rows.length,
        }),
      })
    })

    await page.goto('/crm/lead/filter-lead', { waitUntil: 'domcontentloaded' })
    await expect(page.getByTestId('crm-lead')).toHaveAttribute('data-runtime', 'native')
    await page.getByRole('tab', { name: /aktivitaeten/i }).click()
    await expect(page.getByRole('button', { name: /Rueckfrage klaeren.*wartet/i })).toBeVisible()

    await page.getByTestId('filter-column-lead_activities').selectOption('status')
    await page.getByTestId('filter-value-lead_activities').fill('offen')
    await page.getByTestId('apply-filter-lead_activities').click()

    await expect(page.getByTestId('filter-chips')).toContainText('Status:')
    await expect(page.getByTestId('filter-chips')).toContainText('offen')
    await expect(page.getByRole('button', { name: /Angebot vorbereiten.*offen/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /Rueckfrage klaeren.*wartet/i })).toHaveCount(0)

    const filteredRequest = tabRequests.find((url) => new URL(url).searchParams.has('filter_plan'))
    expect(filteredRequest).toBeTruthy()
    expect(filteredRequest).not.toContain('filterPlan=')

    const filterPlan = JSON.parse(new URL(filteredRequest as string).searchParams.get('filter_plan') ?? '{}')
    expect(filterPlan).toEqual({ status: { op: 'contains', value: 'offen', label: 'offen' } })
  })
})
