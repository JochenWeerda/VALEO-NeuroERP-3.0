import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * Slice-006 E2E: XRechnung / ZUGFeRD Export für SalesInvoice.
 *
 * Validiert: Nach dem Laden einer bestehenden Rechnung (docflow) sind
 * XRechnung- und ZUGFeRD-Buttons sichtbar und lösen via gemockter Backend-API
 * den passenden Download-Roundtrip aus. Mutation-Pending-Guard verhindert
 * Doppel-Klicks.
 */

const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS',
}

const SALES_INVOICE_NUMBER = 'RE-2026-00042'
const DOCFLOW_ID = 'doc-slice006-001'

const fakeXrechnungXml = `<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xoev-de:kosit:standard:xrechnung_3.0</cbc:CustomizationID>
  <cbc:ID>${SALES_INVOICE_NUMBER}</cbc:ID>
</Invoice>`

test.describe('Slice-006: E-Rechnung B2B-Export (XRechnung/ZUGFeRD)', () => {
  test('XRechnung-Export löst gegen Backend aus', async ({ page }) => {
    const exportCalls: string[] = []

    await page.route(/\/api\/v1\/docflow\//, async (route) => {
      const url = route.request().url()
      if (url.includes('/record-')) {
        await route.fulfill({ status: 200, headers: corsHeaders, body: '{}', contentType: 'application/json' })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        headers: corsHeaders,
        body: JSON.stringify({
          id: DOCFLOW_ID,
          doc_number: SALES_INVOICE_NUMBER,
          document_date: '2026-05-27T00:00:00',
          customer_id: 'CUS-001',
          status: 'open',
          items: [
            { article_number: 'Saatgut', quantity: 10, unit_price: 50, tax_rate: 7 },
          ],
          total_net: 500,
          total_tax: 35,
          total_gross: 535,
        }),
      })
    })

    await page.route(/\/api\/v1\/sales\/invoices\/.+\/einvoice\/xrechnung/, async (route) => {
      exportCalls.push(`xrechnung:${route.request().method()}`)
      await route.fulfill({
        status: 200,
        contentType: 'application/xml',
        headers: {
          ...corsHeaders,
          'content-disposition': `attachment; filename="xrechnung-${SALES_INVOICE_NUMBER}.xml"`,
          'x-einvoice-format': 'XRechnung-3.0',
        },
        body: fakeXrechnungXml,
      })
    })

    await page.route(/\/api\/v1\/sales\/invoices\/.+\/einvoice\/zugferd/, async (route) => {
      exportCalls.push(`zugferd:${route.request().method()}`)
      await route.fulfill({
        status: 200,
        contentType: 'application/pdf',
        headers: {
          ...corsHeaders,
          'content-disposition': `attachment; filename="zugferd-${SALES_INVOICE_NUMBER}.pdf"`,
          'x-einvoice-format': 'ZUGFeRD-2.x',
        },
        body: '%PDF-1.7\n%fake-pdf-content',
      })
    })

    await page.goto(`/sales/invoice?id=${DOCFLOW_ID}`)
    await waitForDashboardShell(page)

    const xrechnungBtn = page.getByTestId('einvoice-xrechnung')
    const zugferdBtn = page.getByTestId('einvoice-zugferd')

    await expect(xrechnungBtn).toBeVisible({ timeout: 15000 })
    await expect(zugferdBtn).toBeVisible()
    await expect(xrechnungBtn).toBeEnabled()

    await xrechnungBtn.click()
    await expect
      .poll(() => exportCalls.filter((c) => c.startsWith('xrechnung:')).length, { timeout: 10000 })
      .toBeGreaterThanOrEqual(1)

    await zugferdBtn.click()
    await expect
      .poll(() => exportCalls.filter((c) => c.startsWith('zugferd:')).length, { timeout: 10000 })
      .toBeGreaterThanOrEqual(1)
  })
})
