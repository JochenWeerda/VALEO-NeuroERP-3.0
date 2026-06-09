import { expect, test, type Page, type Route } from '@playwright/test'

const APP_URL = process.env.VALEO_BASE_URL ?? process.env.FRONTEND_URL ?? 'http://127.0.0.1:4173'

async function json(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

async function installApi(page: Page): Promise<{ saved: Array<Record<string, unknown>> }> {
  const state = { saved: [] as Array<Record<string, unknown>> }
  await page.route('**/api/auth/**', (route) => json(route, { id: 'pos-admin', username: 'pos-admin', roles: ['admin'] }))
  await page.route('**/api/v1/auth/**', (route) => json(route, { id: 'pos-admin', username: 'pos-admin', roles: ['admin'] }))
  await page.route('**/api/events?**', (route) => route.fulfill({
    status: 200,
    contentType: 'text/event-stream',
    body: 'event: connected\ndata: {"status":"connected"}\n\n',
  }))
  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    if (path === '/api/v1/pos/fiscalization/config' && request.method() === 'GET') {
      return json(route, {
        configured: true,
        provider: 'fiskaly',
        dsfinvk_provider: 'fiskaly',
        cash_register_id: 'TSS-1',
        client_id: 'CLIENT-1',
        simulation_allowed: false,
        settings: { terminal_id: 'POS-1' },
      })
    }
    if (path === '/api/v1/pos/fiscalization/config' && request.method() === 'PUT') {
      const payload = request.postDataJSON() as Record<string, unknown>
      state.saved.push(payload)
      return json(route, { configured: true, ...payload })
    }
    if (path === '/api/v1/pos/fiscalization/readiness') {
      return json(route, {
        configured: true,
        ready: false,
        config_blockers: [],
        sign: {
          provider: 'fiskaly',
          ready: true,
          live: true,
          blockers: [],
          capabilities: ['sign', 'tse_export'],
          details: {},
        },
        dsfinvk: {
          provider: 'fiskaly',
          ready: true,
          live: true,
          blockers: [],
          capabilities: ['dsfinvk_closing', 'dsfinvk_export'],
          details: {},
        },
        products: [
          {
            product: 'submit_de',
            label: 'SUBMIT DE',
            ready: false,
            blockers: ['FISKALY_SUBMIT_DE_CONTRACT_VERSION fehlt; Produktvertrag/Lizenz nicht freigegeben'],
            details: { execution_enabled: false, execution_note: 'Live-Ausfuehrung ist getrennt gegatet.' },
          },
          {
            product: 'receipt',
            label: 'RECEIPT',
            ready: false,
            blockers: ['FISKALY_RECEIPT_CONTRACT_VERSION fehlt; Produktvertrag/Lizenz nicht freigegeben'],
            details: { execution_enabled: false, execution_note: 'Live-Ausfuehrung ist getrennt gegatet.' },
          },
          {
            product: 'safe',
            label: 'SAFE',
            ready: false,
            blockers: ['FISKALY_SAFE_CONTRACT_VERSION fehlt; Produktvertrag/Lizenz nicht freigegeben'],
            details: { execution_enabled: false, execution_note: 'Live-Ausfuehrung ist getrennt gegatet.' },
          },
        ],
      })
    }
    if (path === '/api/v1/pos/fiscalization/daily-summary') {
      return json(route, { transaction_count: 2, gross_total: 23.8, cash_total: 23.8, card_total: 0, incomplete_count: 1 })
    }
    if (path === '/api/v1/pos/dsfinvk/status') {
      return json(route, { status: 'bereit', taxonomie_version: '2.3', letzter_export: null, letzter_export_dateiname: null, kasse_id: 'TSS-1', hinweis: '' })
    }
    return json(route, {})
  })
  return state
}

test.describe('POS fiscalization operations @full', () => {
  test('admin selects Swissbit while DSFinV-K and optional products stay explicit', async ({ page }) => {
    const state = await installApi(page)
    await page.goto(`${APP_URL}/admin-suite/pos-fiscalization`)

    await expect(page.getByRole('heading', { name: 'POS-Fiskalisierung' })).toBeVisible()
    await page.locator('#fiscal-provider').selectOption('swissbit_cloud')
    await page.getByTestId('save-fiscal-config').click()

    await expect.poll(() => state.saved.length).toBe(1)
    expect(state.saved[0]).toMatchObject({
      provider: 'swissbit_cloud',
      dsfinvk_provider: 'fiskaly',
      cash_register_id: 'TSS-1',
      client_id: 'CLIENT-1',
      settings: { terminal_id: 'POS-1' },
    })
    expect(JSON.stringify(state.saved[0])).not.toMatch(/secret|token|password/i)
    await expect(page.getByTestId('product-submit_de')).toContainText('Nicht freigegeben')
    await expect(page.getByTestId('product-receipt')).toContainText('Nicht freigegeben')
    await expect(page.getByTestId('product-safe')).toContainText('Nicht freigegeben')
  })

  test('daily closing is visibly blocked by incomplete fiscal transactions', async ({ page }) => {
    await installApi(page)
    await page.goto(`${APP_URL}/pos/tagesabschluss-enhanced`)

    await expect(page.getByText(/Abschluss blockiert: 1 unvollst/)).toBeVisible()
    await page.getByRole('button', { name: /Fibu-Buchung/ }).click()
    await expect(page.getByRole('button', { name: /In Fibu buchen/ })).toBeDisabled()
  })
})
