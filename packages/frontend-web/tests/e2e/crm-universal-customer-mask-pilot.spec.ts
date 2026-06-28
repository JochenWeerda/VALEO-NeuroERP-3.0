import { expect, test } from '@playwright/test'

const PILOT_ENABLED = process.env.VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER === 'true'

test.describe('CRM Universal Customer Mask Pilot', () => {
  test.skip(!PILOT_ENABLED, 'Set VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER=true to run the pilot smoke.')

  test.beforeEach(async ({ page }) => {
    await page.route(/\/api\/v1\/crm\/customers\/e2e-customer\/screen-summary$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          schema_version: 1,
          screen_id: 'crm/customer-360',
          customer_id: 'e2e-customer',
          tenant_id: 'tenant-1',
          title: 'E2E Universal Kunde',
          subtitle: 'E2E-100',
          summary: {
            sales_ytd: 42000,
            open_items_total: 0,
            recent_activity_count: 5,
            credit_status: 'ok',
          },
          badges: [],
          available_tabs: ['stammdaten', 'kontakte', 'auftraege'],
          tab_endpoints: {
            contacts: '/api/v1/crm/customers/e2e-customer/tabs/contacts',
            auftraege: '/api/v1/crm/customers/e2e-customer/tabs/auftraege',
          },
          actions: [{ key: 'edit', label: 'Bearbeiten', permission: 'crm.customer.update' }],
          performance: {
            initial_payload_budget_kb: 48,
            tabs_lazy: true,
            lookup_min_chars: 2,
            default_table_limit: 25,
          },
        }),
      })
    })

    await page.route(/\/api\/v1\/crm\/customers\/e2e-customer\/tabs\/contacts$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tab_key: 'contacts',
          table_key: 'contacts_list',
          items: [
            {
              id: 'c-1',
              name: 'Schmidt',
              firstName: 'Anna',
              position: 'Einkauf',
              email: 'anna@example.test',
              phone1: '+49 111',
            },
          ],
        }),
      })
    })

    await page.route(/\/api\/v1\/masks\/crm%2Fcustomer-360\/screen-definition$/, async (route) => {
      await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'mock fallback' }) })
    })

    await page.route(/\/api\/v1\/crm\/customers\/e2e-customer$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'e2e-customer',
          customer_number: 'E2E-100',
          name: 'E2E Universal Kunde',
          email: 'kunde@example.test',
          phone: '+49 123 456',
          payment_terms: 14,
          is_active: true,
          tenant_id: 'tenant-1',
          created_at: '2026-06-28T00:00:00Z',
          updated_at: '2026-06-28T00:00:00Z',
        }),
      })
    })
  })

  test('renders summary-first generator shell on desktop', async ({ page }) => {
    const summaryResponse = page.waitForResponse(/\/api\/v1\/crm\/customers\/e2e-customer\/screen-summary$/)
    await page.goto('/crm/kunden-stamm-modern?id=e2e-customer', { waitUntil: 'domcontentloaded' })

    await expect(page.getByTestId('universal-customer-mask-pilot')).toBeVisible()
    await expect(page.getByTestId('screen-crm/customer-360')).toHaveAttribute('data-layout-mode', 'desktopDense')
    await summaryResponse
    await expect(page.getByRole('heading', { name: 'E2E Universal Kunde' })).toBeVisible()
    await expect(page.getByText('Umsatz 12M')).toBeVisible()
    await expect(page.getByRole('tab', { name: /adresse & kommunikation/i })).toBeVisible()
    await expect(page.getByRole('tab', { name: /ansprechpartner/i })).toBeVisible()
  })

  test('loads lazy tab data after switching tabs', async ({ page }) => {
    const tabResponse = page.waitForResponse(/\/api\/v1\/crm\/customers\/e2e-customer\/tabs\/contacts$/)
    await page.goto('/crm/kunden-stamm-modern?id=e2e-customer', { waitUntil: 'domcontentloaded' })

    await page.getByRole('tab', { name: /ansprechpartner/i }).click()
    await tabResponse
    await expect(page.getByRole('heading', { name: 'Ansprechpartner' })).toBeVisible()
    await expect(page.getByRole('button', { name: /Schmidt.*Anna.*Einkauf/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /anna@example\.test/i })).toBeVisible()
  })

  test('keeps the pilot usable on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto('/crm/kunden-stamm-modern?id=e2e-customer', { waitUntil: 'domcontentloaded' })

    await expect(page.getByTestId('universal-customer-mask-pilot')).toBeVisible()
    await expect(page.getByTestId('screen-crm/customer-360')).toHaveAttribute('data-mobile-layout', 'mobileStack')
    await expect(page.getByRole('heading', { name: 'E2E Universal Kunde' })).toBeVisible()
  })
})
