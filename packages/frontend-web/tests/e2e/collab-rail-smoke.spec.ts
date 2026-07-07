import { expect, test, type Page } from '@playwright/test'

const screenId = 'crm/customer-360'
const entityId = 'collab-customer'
const encodedScreenId = screenId.replace(/\//g, '__')

function screenDefinition() {
  return {
    schemaVersion: 1,
    id: screenId,
    domain: 'crm',
    mode: 'detail',
    title: 'Collab Smoke Kunde',
    adapter: { type: 'native', sourceId: screenId, temporary: false },
    fields: [
      { key: 'name', label: 'Name', type: 'text' },
      { key: 'status', label: 'Status', type: 'text', readOnly: true },
    ],
    dataSources: [
      { key: 'entity', endpoint: `/api/v1/masks/${encodedScreenId}/entity/{entity_id}` },
    ],
    tabs: [
      {
        key: 'kopf',
        label: 'Kopf',
        lazy: false,
        keepAlive: true,
        dataSourceKey: 'entity',
        fields: [
          { key: 'name', label: 'Name', type: 'text' },
          { key: 'status', label: 'Status', type: 'text', readOnly: true },
        ],
      },
    ],
    permissions: ['*'],
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      touchTargetPx: 44,
      floorplan: 'objectPage',
      density: 'compact',
      contextRail: 'combined',
      contextRailSections: ['workflow', 'audit', 'copilot', 'collab'],
      tableProfile: 'standard',
    },
    performance: {
      initialPayloadBudgetKb: 48,
      requiresLazyTabs: false,
      requiresVirtualTables: false,
      lookupMinChars: 2,
    },
  }
}

async function installMocks(page: Page): Promise<{ posted: unknown[] }> {
  const posted: unknown[] = []
  const notes = [
    {
      id: 'note-existing',
      tenant_id: 'tenant-e2e',
      entity_type: screenId,
      entity_id: entityId,
      body: 'Bestehende Notiz',
      mentions: [],
      created_by: 'other-user',
      created_at: '2026-07-07T08:00:00Z',
      updated_at: '2026-07-07T08:00:00Z',
      deleted_at: null,
    },
  ]

  await page.route(new RegExp(`/api/v1/masks/${encodedScreenId}/screen-definition$`), async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(screenDefinition()) })
  })

  await page.route(new RegExp(`/api/v1/masks/${encodedScreenId}/entity/${entityId}$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: entityId, name: 'Collab Smoke Kunde', status: 'open' }),
    })
  })

  await page.route('**/api/v1/collab/notes**', async (route) => {
    if (route.request().method() === 'POST') {
      const payload = route.request().postDataJSON()
      posted.push(payload)
      const created = {
        id: 'note-created',
        tenant_id: 'tenant-e2e',
        entity_type: payload.entity_type,
        entity_id: payload.entity_id,
        body: payload.body,
        mentions: payload.mentions,
        created_by: 'dev-user',
        created_at: '2026-07-07T08:01:00Z',
        updated_at: '2026-07-07T08:01:00Z',
        deleted_at: null,
      }
      notes.push(created)
      await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify(created) })
      return
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(notes) })
  })

  return { posted }
}

test.describe('UIX-062 Collab Rail', () => {
  test('Notiz mit Mention erzeugt Rail-Badge und API-Payload', async ({ page }) => {
    const { posted } = await installMocks(page)

    await page.goto(`/crm/kunden/${entityId}`, { waitUntil: 'domcontentloaded' })

    await expect(page.getByTestId('crm-customer-360')).toBeVisible()
    await expect(page.getByTestId('collab-rail')).toBeVisible()
    await expect(page.getByText('Bestehende Notiz')).toBeVisible()

    await page.getByTestId('collab-note-body').fill('Bitte rueckmelden @dev-user')
    await page.getByTestId('collab-mention-input').fill('u-mentioned')
    await page.getByTestId('collab-note-submit').click()

    await expect(page.getByText('Bitte rueckmelden @dev-user')).toBeVisible()
    await expect(page.getByTestId('collab-mention-badge')).toHaveText('1')
    expect(posted).toHaveLength(1)
    expect(posted[0]).toMatchObject({
      entity_type: screenId,
      entity_id: entityId,
      body: 'Bitte rueckmelden @dev-user',
      mentions: [{ user_id: 'dev-user' }, { user_id: 'u-mentioned' }],
    })
  })
})
