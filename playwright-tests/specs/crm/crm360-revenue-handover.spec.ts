import { expect, test, type Page, type Route } from '@playwright/test'
import { InteractionGuard } from '../../helpers/interactionGuard'

const APP_URL = process.env.VALEO_BASE_URL ?? process.env.FRONTEND_URL ?? 'http://127.0.0.1:4173'

const customer = {
  id: 'customer-360-1',
  customer_number: 'KD-360-001',
  company_name: 'Musterhof Nord GmbH',
  contact_person: 'JW',
  postal_code: '26603',
  city: 'Aurich',
  address: {
    street: 'Hafenstrasse 7',
    postalCode: '26603',
    city: 'Aurich',
  },
}

const order = {
  id: 'order-360-1',
  order_number: 'SO-360-1',
  customer_id: customer.id,
  subject: 'CRM360 Saatgutauftrag',
  description: 'Aus CRM360',
  status: 'open',
  created_at: '2026-06-08T10:00:00Z',
  delivery_date: '2026-06-12T00:00:00Z',
  items: [{
    id: 'order-item-1',
    article_number: 'ART-SAAT-1',
    description: 'Saatgut Test',
    quantity: 40,
    unit_price: 25,
    discount_percent: 0,
  }],
}

async function json(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  })
}

async function installOtcApi(page: Page): Promise<void> {
  await page.route('**/api/auth/**', (route) => json(route, {
    id: 'crm360-test-user',
    username: 'crm360-test',
    roles: ['admin'],
  }))
  await page.route('**/api/v1/auth/**', (route) => json(route, {
    id: 'crm360-test-user',
    username: 'crm360-test',
    roles: ['admin'],
  }))
  await page.route('**/api/events?**', (route) => route.fulfill({
    status: 200,
    contentType: 'text/event-stream',
    body: 'event: connected\ndata: {"status":"connected"}\n\n',
  }))
  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    const method = request.method()

    if (path === `/api/v1/sales/orders/${order.id}` && method === 'GET') return json(route, order)
    if (path === '/api/v1/sales/orders/' && method === 'GET') {
      return json(route, { items: [order], total: 1, page: 1, size: 100, pages: 1, has_next: false, has_prev: false })
    }
    // The specialist screen must retain the typed CRM handover context even
    // when the optional customer-detail lookup has no usable payload.
    if (path === `/api/v1/crm/customers/${customer.id}` && method === 'GET') return json(route, null)
    if (path.endsWith('/sales-eligibility') && method === 'GET') {
      return json(route, {
        allowed_order: true,
        allowed_delivery: true,
        allowed_invoice: true,
        reasons: [],
      })
    }
    if (path === '/api/v1/admin/branches' && method === 'GET') return json(route, [])
    if (path.includes('/schlaege') && method === 'GET') return json(route, [])
    if (path === '/api/v1/sales/delivery-notes' && method === 'POST') {
      return json(route, {
        id: 'delivery-360-1',
        delivery_note_number: 'LS-360-1',
        status: 'draft',
        invoice_number: null,
      })
    }
    if (path === '/api/v1/docflow/delivery-360-1/convert' && method === 'POST') {
      return json(route, {
        command: 'convert',
        target_doc_id: 'invoice-360-1',
        status: 'completed',
        payload: {
          target_doc_number: 'RE-360-1',
          target_doc_type: 'sales_invoice',
        },
      })
    }
    if (path === '/api/v1/docflow/invoice-360-1' && method === 'GET') {
      return json(route, {
        id: 'invoice-360-1',
        doc_number: 'RE-360-1',
        document_date: '2026-06-08',
        customer_id: customer.id,
        status: 'open',
        items: [{
          article_number: 'ART-SAAT-1',
          quantity: 40,
          unit_price: 25,
          tax_rate: 19,
        }],
        total_net: 1000,
        total_tax: 190,
        total_gross: 1190,
      })
    }
    return json(route, {})
  })
}

test('@full CRM360 revenue handover opens every expected specialist screen', async ({ page }) => {
  await installOtcApi(page)
  const guard = new InteractionGuard(page)

  await page.goto(
    `${APP_URL}/sales/order-editor/${order.id}?kunde=${customer.customer_number}`
    + `&kundeName=${encodeURIComponent(customer.company_name)}&entryMode=crm360&angebot=offer-360-1`,
    { waitUntil: 'domcontentloaded' },
  )
  await expect(page.getByText(customer.company_name).first()).toBeVisible()
  await expect(page.getByText('Saatgut Test').first()).toBeVisible()

  let checkpoint = guard.checkpoint()
  await page.locator('[data-action-id="sales.order.create-delivery"]').click()
  await expect(page).toHaveURL(/\/verkauf\/lieferschein-erfassung\?/)
  let target = new URL(page.url())
  expect(target.searchParams.get('auftrag')).toBe(order.id)
  expect(target.searchParams.get('angebot')).toBe('offer-360-1')
  expect(target.searchParams.get('kunde')).toBe(customer.customer_number)
  await expect(page.getByText('Saatgut Test').first()).toBeVisible()
  await guard.expectNoNewErrors(checkpoint)

  checkpoint = guard.checkpoint()
  await page.locator('[data-action-id="sales.delivery.create-invoice"]').click()
  await expect(page).toHaveURL(/\/sales\/invoice-editor\?/)
  target = new URL(page.url())
  expect(target.searchParams.get('auftrag')).toBe(order.id)
  expect(target.searchParams.get('lieferschein')).toBe('delivery-360-1')
  expect(target.searchParams.get('rechnungId')).toBe('invoice-360-1')
  expect(target.searchParams.get('rechnungsnr')).toBe('RE-360-1')
  expect(target.searchParams.get('kunde')).toBe(customer.customer_number)
  await expect(page.locator('input[value="RE-360-1"]')).toBeVisible()
  await guard.expectNoNewErrors(checkpoint)

  checkpoint = guard.checkpoint()
  await page.locator('[data-action-id="sales.invoice.open-receivables"]').click()
  await expect(page).toHaveURL(/\/finance\/op-debitoren\?/)
  target = new URL(page.url())
  expect(target.searchParams.get('rechnungsnr')).toBe('RE-360-1')
  expect(target.searchParams.get('rechnungId')).toBe('invoice-360-1')
  expect(target.searchParams.get('kunde')).toBe(customer.customer_number)
  await guard.expectNoNewErrors(checkpoint)
})
