import { expect, test, type Page, type Route } from '@playwright/test'
import { InteractionGuard, expectCrm360RoundTrip } from '../../helpers/interactionGuard'
import { AUTOMATED_CRM360_ACTIONS, CRM360_ACTION_CONTRACTS } from './crm360-action-contracts'
import { CRM_REVENUE_MODEL } from './crm360-workflow-model'

const APP_URL = process.env.VALEO_BASE_URL ?? process.env.FRONTEND_URL ?? 'http://127.0.0.1:4173'

const customer = {
  id: 'customer-360-1',
  name: 'Musterhof Nord GmbH',
  debtorNo: 'KD-360-001',
  custGroup: 'A1',
  street: 'Hafenstrasse 7',
  zipCode: '26603',
  city: 'Aurich',
  phone1: '+49 4941 12345',
  email: 'einkauf@musterhof.example',
  salesRepresentative: 'JW',
  dispatcher: 'AB',
  creditLimit: 75000,
  revenueStatus: 'A',
  abcStatus: 'A',
  alertMessages: [],
  chefAnweisung: 'Angebote ab 50 t mit Vertrieb abstimmen.',
}

const contacts = [{
  id: 'contact-1',
  customerId: customer.id,
  salutation: 'Herr',
  name: 'Mustermann',
  firstName: 'Max',
  position: 'Einkauf',
  priority: 1,
  phone1: '+49 4941 111',
  phone2: '+49 4941 222',
  email: 'max.mustermann@musterhof.example',
  weeklySchedule: [true, false, false, false, false, false, false, false, false, false],
}]

const offerDocument = {
  id: 'offer-360-1',
  customerId: customer.id,
  type: 'OFFER',
  docNo: 'AN-360-1',
  date: '2026-06-08',
  operator: 'JW',
  representative: 'JW',
  netAmount: 1000,
  taxAmount: 190,
  grossAmount: 1190,
  completed: false,
}

let logs = [{
  id: 'log-1',
  customerId: customer.id,
  direction: 'OUTGOING',
  date: '2026-06-08',
  completed: false,
  artKurzinfo: 'Angebot nachfassen',
  operator: 'JW',
  reSubmissionDate: '2026-06-09',
  referenceType: 'OFFER',
  referenceNo: 'AN-360-1',
}]
let recordedRequests: Array<{ method: string; path: string; body: unknown }> = []
let failNextLogPost = false

async function json(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  })
}

async function installKimApi(page: Page): Promise<void> {
  logs = logs.map((entry) => ({ ...entry, completed: false }))
  recordedRequests = []
  failNextLogPost = false
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
  await page.route('**/api/v1/crm/tapi/dial', (route) => {
    recordedRequests.push({
      method: route.request().method(),
      path: new URL(route.request().url()).pathname,
      body: route.request().postDataJSON(),
    })
    return json(route, {
      id: 'dial-1', caller: 'KIM', called: contacts[0].phone2, kunden_nr: customer.debtorNo,
      kunde_name: customer.name, status: 'dial_req',
    })
  })
  await page.route('**/api/v1/crm/customers/*/sales-eligibility', (route) => json(route, {
    allowed_order: true,
    allowed_delivery: true,
    allowed_invoice: true,
    reasons: [],
  }))
  await page.route('**/api/v1/sales/offers/?**', (route) => json(route, {
    items: [],
    total: 0,
    page: 1,
    size: 100,
    pages: 0,
    has_next: false,
    has_prev: false,
  }))
  await page.route(`**/api/v1/sales/offers/${offerDocument.id}`, (route) => json(route, {
    id: offerDocument.id,
    tenant_id: 'tenant-1',
    offer_number: offerDocument.docNo,
    customer_id: customer.id,
    customer_name: customer.name,
    subject: 'Saatgutangebot',
    description: '',
    total_amount: 1000,
    currency: 'EUR',
    status: 'offen',
    contact_person: 'Max Mustermann',
    valid_until: '2026-06-30T00:00:00Z',
    is_pauschale: false,
    items: [{
      id: 'offer-item-1',
      line_number: 1,
      article_number: 'SAAT-1',
      description: 'Weizensaatgut',
      quantity: 40,
      unit: 't',
      unit_price: 25,
      discount_percent: 0,
      line_total: 1000,
    }],
    created_at: '2026-06-08T00:00:00Z',
    version: 1,
  }))
  await page.route('**/api/v1/crm/kim/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const path = url.pathname
    if (request.method() !== 'GET') {
      recordedRequests.push({
        method: request.method(),
        path,
        body: request.postData() ? request.postDataJSON() : null,
      })
    }

    if (path.endsWith('/customers') && request.method() === 'GET') return json(route, [customer])
    if (path.endsWith(`/customers/${customer.id}`) && request.method() === 'PUT') return json(route, { status: 'success' })
    if (path.endsWith(`/customers/${customer.id}/contacts`) && request.method() === 'GET') return json(route, contacts)
    if (path.endsWith(`/customers/${customer.id}/contacts`) && request.method() === 'POST') return json(route, { status: 'success' })
    if (path.endsWith(`/customers/${customer.id}/logs`) && request.method() === 'GET') return json(route, logs)
    if (path.endsWith(`/customers/${customer.id}/logs`) && request.method() === 'POST') {
      if (failNextLogPost) {
        failNextLogPost = false
        return json(route, { detail: 'Testfehler beim Speichern' }, 500)
      }
      logs = [...logs, { ...request.postDataJSON(), id: 'log-created', customerId: customer.id, date: '2026-06-08' }]
      return json(route, { status: 'success' })
    }
    if (path.endsWith('/contact-logs/log-1/completed') && request.method() === 'PUT') {
      logs = logs.map((entry) => entry.id === 'log-1' ? { ...entry, completed: true } : entry)
      return json(route, { status: 'success' })
    }
    if (path.endsWith(`/customers/${customer.id}/financials`)) return json(route, [])
    if (path.endsWith(`/customers/${customer.id}/documents`)) return json(route, [offerDocument])
    if (path.endsWith('/neuro-summary')) {
      return json(route, {
        healthScore: 88,
        statusLabel: 'Stabil',
        summary: 'Kundenbeziehung ist stabil.',
        opportunities: ['Saatgutangebot vorbereiten'],
        risks: ['Kreditlimit beobachten'],
      })
    }
    if (path.endsWith('/draft-email')) {
      return json(route, { subject: 'Angebot', body: 'Guten Tag, anbei unser Angebot.', engine: 'test' })
    }
    return json(route, { detail: `Unmocked KIM route: ${request.method()} ${path}` }, 501)
  })
}

async function openCrm360(page: Page): Promise<void> {
  await installKimApi(page)
  await page.goto(`${APP_URL}/crm`, { waitUntil: 'domcontentloaded' })
  await expect(page.locator('#crm-main-viewport')).toBeVisible()
  await expect(page.locator(`#sidebar-cust-item-${customer.id}`)).toBeVisible()
}

test.describe('CRM 360 semantic action contracts', () => {
  test('@full action matrix has unique IDs and complete workflow metadata', async () => {
    const ids = CRM360_ACTION_CONTRACTS.map((action) => action.id)
    expect(new Set(ids).size).toBe(ids.length)
    expect(AUTOMATED_CRM360_ACTIONS.length).toBeGreaterThanOrEqual(15)
    for (const action of CRM360_ACTION_CONTRACTS) {
      expect(action.selector).not.toBe('')
      expect(action.expectedTarget).not.toBe('')
      expect(action.backTarget).toBe('/crm')
      expect(action.workflow).not.toBe('')
    }
  })

  test('@full all primary header actions are represented in the action matrix', async ({ page }) => {
    await openCrm360(page)
    const rendered = await page.locator('#customer-action-bar [data-action-id]').evaluateAll((nodes) =>
      nodes.map((node) => node.getAttribute('data-action-id')).filter(Boolean),
    )
    const contracted = new Set(CRM360_ACTION_CONTRACTS.map((action) => action.id))
    // 11 Toolbar-Aktionen seit QUICK-001 (Neukunde + Drucken ersetzen das alte „Neu"=Aktivität).
    expect(rendered.length).toBe(11)
    expect(rendered.filter((id) => !contracted.has(id!))).toEqual([])
  })

  test('@full modal and local actions open the expected CRM context', async ({ page }) => {
    await openCrm360(page)
    const guard = new InteractionGuard(page)
    const checkpoint = guard.checkpoint()

    // „Information" ist seit S2 ein Dropdown; „Kundeninformation" öffnet den Dialog.
    await page.locator('[data-action-id="crm360.customer.info"]').click()
    await page.locator('[data-action-id="crm360.info.dialog"]').click()
    await expect(page.getByRole('dialog', { name: 'Kundeninformation' })).toContainText(customer.debtorNo)
    await page.locator('[data-action-id="crm360.customer.info.close"]').click()

    await page.locator('[data-action-id="crm360.presents.open"]').click()
    await expect(page.getByText(/Präsente & Geschenke-PR Protokoll/i)).toBeVisible()
    await page.getByRole('button', { name: /Protokoll schließen/i }).click()

    // „Neu"=Aktivität wandert in die Kontakt-Historie (QUICK-001: Toolbar-„Neu" ist nun Neukunde).
    await page.locator('#btn-trigger-history-form').click()
    await expect(page.locator('#add-history-vorgang-form')).toBeVisible()

    await page.locator('[data-action-id="crm360.filters.reset"]').click()
    // Aktiver Tab nutzt seit dem DS-Umbau (KIM-DS-001) das theme-faehige Token
    // `bg-background` statt des hartkodierten `bg-white` (Dark-Mode-Konformitaet).
    await expect(page.locator('#sub-workspace-tab-allgemein')).toHaveClass(/bg-background/)
    await guard.expectNoNewErrors(checkpoint)
  })

  test('@full information dropdown opens every module in customer context without errors', async ({ page }) => {
    await openCrm360(page)
    const guard = new InteractionGuard(page)
    const checkpoint = guard.checkpoint()
    const sections = [
      'selektion',
      'profil',
      'mitbewerber',
      'kreditsicherheit',
      'kunden-artikel',
      'lieferanten-artikel',
      'preisvereinbarung',
      'konzern',
      'zusatzfelder',
    ]

    for (const section of sections) {
      await page.locator('[data-action-id="crm360.customer.info"]').click()
      await page.locator(`[data-action-id="crm360.info:${section}"]`).click()
      await expect(page.locator(`[data-info-section="${section}"]`)).toBeVisible()
      await expect(page).toHaveURL(/\/crm(?:\?|$)/)
    }

    await page.locator('[data-action-id="crm360.customer.info"]').click()
    await page.locator('[data-action-id="crm360.info:fibu-op"]').click()
    await expect(page.locator('#sub-workspace-tab-finanzen')).toHaveClass(/bg-background/)

    await page.locator('[data-action-id="crm360.customer.info"]').click()
    await page.locator('[data-action-id="crm360.info:kontrakt-uebersicht"]').click()
    await expect(page.locator('#sub-workspace-tab-kontrakte')).toHaveClass(/bg-background/)
    await guard.expectNoNewErrors(checkpoint)
  })

  test('@full document dropdown matches the L3 categories and overview clears prior filtering', async ({ page }) => {
    await openCrm360(page)
    const guard = new InteractionGuard(page)
    const checkpoint = guard.checkpoint()
    const categories = ['OFFER', 'ORDER', 'DELIVERY_NOTE', 'INQUIRY', 'PURCHASE_ORDER', 'ALL']

    for (const category of categories) {
      await page.locator('[data-action-id="crm360.offer.create"]').click()
      await page.locator(`[data-action-id="crm360.doc:${category}"]`).click()
      await expect(page.locator('#sub-workspace-tab-belege')).toHaveClass(/bg-background/)
      await expect(page.locator(`#tab-doc-sel-${category}`)).toHaveClass(/border-primary/)
      await expect(page).toHaveURL(/\/crm(?:\?|$)/)
    }

    await page.locator('#tab-doc-sel-ORDER').click()
    await page.locator('[data-action-id="crm360.offer.create"]').click()
    await page.locator('[data-action-id="crm360.doc:OFFER"]').click()
    await expect(page.locator('#tab-doc-sel-OFFER')).toHaveClass(/border-primary/)

    await page.locator('[data-action-id="crm360.offer.create"]').click()
    await page.locator('[data-action-id="crm360.doc:ALL"]').click()
    await expect(page.locator('#tab-doc-sel-ALL')).toHaveClass(/border-primary/)
    await expect(page.locator('[id^="doc-row-entry-"]')).toHaveCount(1)
    await expect(page.locator('[data-action-id="crm360.document.create"]')).toBeDisabled()
    await guard.expectNoNewErrors(checkpoint)
  })

  test('@full customer master update sends the correct entity context', async ({ page }) => {
    await openCrm360(page)

    await page.locator('[data-action-id="crm360.master.open"]').click()
    await expect(page.getByRole('dialog', { name: /Stammdaten/ })).toBeVisible()
    await page.getByLabel('PLZ & Ort').fill('Aurich-Test')
    await page.getByRole('button', { name: 'Sichern' }).click()

    await expect(page.getByRole('dialog', { name: /Stammdaten/ })).toBeHidden()
    expect(recordedRequests).toContainEqual(expect.objectContaining({
      method: 'PUT',
      path: `/api/v1/crm/kim/customers/${customer.id}`,
      body: expect.objectContaining({ city: 'Aurich-Test' }),
    }))
  })

  test('@full new customer route and browser back stay inside the typed CRM workflow', async ({ page }) => {
    await openCrm360(page)

    await page.locator('[data-action-id="crm360.customer.create"]').click()
    await expect(page).toHaveURL(/\/verkauf\/kunde\/neu$/)
    await expect(page.getByRole('heading', { name: 'Neuer Kunde' })).toBeVisible()
    await expectCrm360RoundTrip(page)
  })

  test('@full activity form persists all S1 fields and retains input after a failed save', async ({ page }) => {
    await openCrm360(page)
    await page.locator('#btn-trigger-history-form').click()
    const form = page.locator('#add-history-vorgang-form')

    await form.getByLabel(/Betreff/).fill('Erntegespraech')
    await form.getByLabel('Kommentar').fill('Lieferfenster und Menge abgestimmt.')
    await form.getByLabel(/CC/).fill('AO')
    await form.getByLabel('Art').selectOption('persoenlich')
    failNextLogPost = true
    await form.locator('#btn-save-activity-vorgang').click()

    await expect(form.getByRole('alert')).toContainText(/Testfehler|gespeichert/i)
    await expect(form.getByLabel(/Betreff/)).toHaveValue('Erntegespraech')
    await expect(form.getByLabel('Kommentar')).toHaveValue('Lieferfenster und Menge abgestimmt.')

    await form.locator('#btn-save-activity-vorgang').click()
    await expect(form).toBeHidden()
    expect(recordedRequests).toContainEqual(expect.objectContaining({
      method: 'POST',
      path: `/api/v1/crm/kim/customers/${customer.id}/logs`,
      body: expect.objectContaining({
        art: 'persoenlich',
        betreff: 'Erntegespraech',
        kommentar: 'Lieferfenster und Menge abgestimmt.',
        ccIntern: 'AO',
      }),
    }))
  })

  test('@full selected contact call uses number choice, TAPI and contact-aware logging', async ({ page }) => {
    await openCrm360(page)
    await page.locator(`#cp-row-${contacts[0].id}`).click()
    await page.locator('[data-action-id="crm360.contact.open"]').click()
    await expect(page.getByTestId('crm360-contact-details-dialog')).toContainText(contacts[0].email)
    await page.getByTestId('crm360-contact-details-dialog').getByRole('button', { name: 'Close' }).click()
    await page.locator('[data-action-id="crm360.contact.presents"]').click()
    await expect(page.getByRole('dialog')).toContainText('Max Mustermann')
    await page.getByRole('button', { name: /Protokoll schlie/ }).click()
    await page.locator('[data-action-id="crm360.contact.call"]').click()

    const phoneDialog = page.getByRole('dialog', { name: /Auswahl der Telefonnummer/ })
    await expect(phoneDialog).toBeVisible()
    await phoneDialog.getByLabel(/Telefon 2/).check()
    await phoneDialog.getByRole('button', { name: 'OK' }).click()
    await page.locator('#crm360-quick-call-description').fill('Saatgutmenge mit Ansprechpartner abgestimmt')
    await page.getByRole('button', { name: 'Loggen' }).click()

    expect(recordedRequests).toContainEqual(expect.objectContaining({
      method: 'POST',
      path: '/api/v1/crm/tapi/dial',
      body: { called: contacts[0].phone2, kunden_nr: customer.debtorNo },
    }))
    expect(recordedRequests).toContainEqual(expect.objectContaining({
      method: 'POST',
      path: `/api/v1/crm/kim/customers/${customer.id}/logs`,
      body: expect.objectContaining({
        art: 'telefon',
        betreff: 'Telefonat mit Max Mustermann',
        kommentar: 'Saatgutmenge mit Ansprechpartner abgestimmt',
      }),
    }))
  })

  test('@full print action exposes a complete print-only customer view', async ({ page }) => {
    await openCrm360(page)
    await page.evaluate(() => {
      window.print = () => {
        document.body.dataset.crm360PrintCalled = 'true'
      }
    })

    await page.locator('[data-action-id="crm360.customer.print"]').click()
    await expect.poll(() => page.locator('body').getAttribute('data-crm360-print-called')).toBe('true')
    await page.emulateMedia({ media: 'print' })
    await expect(page.getByTestId('crm360-print-view')).toBeVisible()
    await expect(page.getByTestId('crm360-print-view')).toContainText(customer.debtorNo)
    await expect(page.getByTestId('crm360-print-view')).toContainText(contacts[0].email)
    await expect(page.getByTestId('crm360-print-view')).toContainText(offerDocument.docNo)
  })

  test('@full call logging persists through the KIM log endpoint', async ({ page }) => {
    await openCrm360(page)

    await page.locator('[data-action-id="crm360.call.create"]').click()
    await page.getByLabel('Gesprächs-Kurzbericht').fill('40 t Saatgut angefragt')
    await page.getByRole('button', { name: 'Loggen' }).click()

    await expect(page.getByText(/Telefonat: 40 t Saatgut angefragt/)).toBeVisible()
    expect(recordedRequests).toContainEqual(expect.objectContaining({
      method: 'POST',
      path: `/api/v1/crm/kim/customers/${customer.id}/logs`,
      body: expect.objectContaining({
        direction: 'OUTGOING',
        artKurzinfo: 'Telefonat: 40 t Saatgut angefragt',
        completed: true,
      }),
    }))
  })

  test('@full AI action receives the selected customer and renders expected content', async ({ page }) => {
    await openCrm360(page)
    const requestPromise = page.waitForRequest((request) => request.url().endsWith('/api/v1/crm/kim/neuro-summary'))
    await page.locator('[data-action-id="crm360.ai.summary"]').click()
    const request = await requestPromise
    expect(request.postDataJSON()).toEqual({ customerId: customer.id })
    await expect(page.locator('#slide-ai-markdown')).toContainText('Kundenbeziehung ist stabil')
  })

  test('@full offer navigation transfers customer context and browser back returns to CRM 360', async ({ page }) => {
    await openCrm360(page)
    // „Ang./Auf." ist seit S2 ein Dropdown; „Neues Angebot / Auftrag" navigiert.
    await page.locator('[data-action-id="crm360.offer.create"]').click()
    await page.locator('[data-action-id="crm360.offer.new"]').click()
    await expect(page).toHaveURL(/\/sales\/angebot-erstellen\?/)
    const target = new URL(page.url())
    expect(target.searchParams.get('kunde')).toBe(customer.debtorNo)
    expect(target.searchParams.get('kundeName')).toBe(customer.name)
    expect(target.searchParams.get('entryMode')).toBe('crm360')
    await expect(page.getByPlaceholder(/Kein Kunde/)).toHaveValue(customer.name)
    await expectCrm360RoundTrip(page)
  })

  test('@full opening an existing offer loads the selected entity and browser back returns to CRM 360', async ({ page }) => {
    await openCrm360(page)
    await page.locator('#sub-workspace-tab-belege').click()
    await page.locator('#tab-doc-sel-OFFER').click()
    await page.locator(`#doc-row-entry-${offerDocument.id}`).click()
    await page.locator('[data-action-id="crm360.document.open"]').click()

    await expect(page).toHaveURL(new RegExp(`/sales/angebot/${offerDocument.id}`))
    await expect(page.locator(`[data-offer-id="${offerDocument.id}"]`)).toBeVisible()
    await expect(page.getByText('Angebot-Nr.:').locator('..').locator('input')).toHaveValue(offerDocument.docNo)
    await expect(page.getByPlaceholder(/Kein Kunde/)).toHaveValue(customer.name)
    await expect(page.getByText('Weizensaatgut')).toBeVisible()
    await expectCrm360RoundTrip(page)
  })

  test('@full receivables navigation transfers debtor context and browser back returns to CRM 360', async ({ page }) => {
    await openCrm360(page)
    await page.locator('[data-action-id="crm360.receivables.open"]').click()
    await expect(page).toHaveURL(/\/finance\/op-debitoren\?/)
    expect(new URL(page.url()).searchParams.get('kunden_nr')).toBe(customer.debtorNo)
    await expectCrm360RoundTrip(page)
  })

  test('@full delegated document and receivables creates disclose their specialist process', async ({ page }) => {
    await openCrm360(page)

    // QUICK-001: routbare Belege (Angebot/Auftrag/Lieferschein) navigieren in die
    // Fachmaske; nicht kanonisch routbare Kategorien (Kaufangebote) legen ehrlich
    // im Fachprozess an statt einen Scheinerfolg zu behaupten.
    await page.locator('#sub-workspace-tab-belege').click()
    await page.locator('#tab-doc-sel-PURCHASE_OFFER').click()
    await page.locator('[data-action-id="crm360.document.create"]').click()
    await expect(page.getByText(/Belege im Fachprozess anlegen/i).first()).toBeVisible()

    await page.locator('#sub-workspace-tab-finanzen').click()
    await page.locator('#financial-ledger-table-block button').first().click()
    const opForm = page.locator('#inline-op-insert-form')
    await opForm.locator('#crm360-open-item-number').fill('RE-TEST-1')
    await opForm.locator('#crm360-open-item-net').fill('2500')
    await opForm.locator('#crm360-open-item-description').fill('Testlieferung')
    await opForm.getByRole('button', { name: /OP verbuchen/i }).click()
    await expect(page.getByText(/Offene Posten im Fachprozess anlegen/i).first()).toBeVisible()
  })
})

test.describe('CRM-to-Revenue model', () => {
  test('@full model contains the complete customer-to-receivables path', async () => {
    expect(CRM_REVENUE_MODEL.map((transition) => transition.from)).toEqual([
      'customer',
      'offer',
      'order',
      'delivery',
      'invoice',
    ])
    expect(CRM_REVENUE_MODEL[CRM_REVENUE_MODEL.length - 1]?.to).toBe('receivables')
    for (const transition of CRM_REVENUE_MODEL) {
      expect(transition.route.startsWith('/')).toBeTruthy()
      expect(transition.requiredContext.length).toBeGreaterThan(0)
    }
  })
})
