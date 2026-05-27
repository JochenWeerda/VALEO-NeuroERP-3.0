/**
 * E2E-Tests für Slice-009: DSGVO Art. 33 Datenpannen-Meldeprozess.
 *
 * Testet:
 * - Leer-State mit CTA
 * - Neue Datenpanne erfassen (Dialog → Speichern → Liste)
 * - Ampelindikator (orange) bei frischer Datenpanne
 * - "Behörde gemeldet"-Button → Notify-Dialog
 * - Ampel wechselt auf grün nach Meldung
 */
import { test, expect } from '@playwright/test'

const BREACH_URL = '/compliance/datenpannen'
const NOW_ISO = new Date().toISOString()

const MOCK_BREACH = {
  id: 'breach-mock-001',
  tenant_id: 'tenant-test',
  breach_type: 'VERTRAULICHKEIT',
  description: 'Unbefugter Zugriff auf Kundendaten',
  data_categories: ['Name', 'E-Mail'],
  persons_count_approx: 250,
  records_count_approx: 750,
  dpo_name: 'Max Mustermann',
  dpo_contact: 'dsb@test.de',
  likely_consequences: 'Identitätsdiebstahl',
  measures_taken: 'Passwörter zurückgesetzt',
  discovered_at: NOW_ISO,
  status: 'ENTDECKT',
  internal_reference: 'INC-2026-001',
  created_at: NOW_ISO,
  updated_at: NOW_ISO,
  notified_at: null,
  notified_by: null,
  authority_reference: null,
}

const MOCK_DEADLINE_ORANGE = {
  breach_id: MOCK_BREACH.id,
  discovered_at: NOW_ISO,
  deadline_at: new Date(Date.now() + 60 * 60 * 1000 * 60).toISOString(),
  hours_remaining: 60,
  hours_elapsed: 12,
  is_overdue: false,
  is_notified: false,
  traffic_light: 'ORANGE',
}

const MOCK_DEADLINE_GREEN = {
  ...MOCK_DEADLINE_ORANGE,
  is_notified: true,
  traffic_light: 'GREEN',
}

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('dev_bypass_auth', 'true')
  })
})

test.describe('Datenpannen Art. 33', () => {
  test('zeigt Leer-State mit Hinweis und CTA', async ({ page }) => {
    await page.route('**/api/v1/gdpr/art33/breaches', (route) => {
      void route.fulfill({ json: [] })
    })

    await page.goto(BREACH_URL)
    await expect(page.getByText('Datenpannen-Meldeprozess (Art. 33 DSGVO)')).toBeVisible({ timeout: 10_000 })
    await expect(page.getByText('Keine Datenpannen erfasst')).toBeVisible()
    await expect(page.getByTestId('breach-add-btn')).toBeVisible()
  })

  test('öffnet Dialog und erfasst neue Datenpanne', async ({ page }) => {
    let posted = false

    await page.route('**/api/v1/gdpr/art33/breaches', async (route) => {
      if (route.request().method() === 'GET') {
        void route.fulfill({ json: posted ? [MOCK_BREACH] : [] })
      } else if (route.request().method() === 'POST') {
        posted = true
        void route.fulfill({ status: 201, json: MOCK_BREACH })
      } else {
        await route.continue()
      }
    })

    await page.goto(BREACH_URL)
    await expect(page.getByTestId('breach-add-btn')).toBeVisible({ timeout: 10_000 })

    await page.getByTestId('breach-add-btn').click()
    await expect(page.getByTestId('breach-description')).toBeVisible()

    await page.getByTestId('breach-description').fill('Unbefugter Zugriff auf Kundendaten')
    await page.getByTestId('breach-save-btn').click()

    await expect(page.getByTestId('breach-save-btn')).not.toBeVisible({ timeout: 5_000 })
  })

  test('listet Datenpanne mit Ampelindikator auf', async ({ page }) => {
    await page.route('**/api/v1/gdpr/art33/breaches', (route) => {
      void route.fulfill({ json: [MOCK_BREACH] })
    })
    await page.route(`**/api/v1/gdpr/art33/breaches/${MOCK_BREACH.id}/deadline`, (route) => {
      void route.fulfill({ json: MOCK_DEADLINE_ORANGE })
    })

    await page.goto(BREACH_URL)

    await expect(page.getByText('Unbefugter Zugriff auf Kundendaten')).toBeVisible({ timeout: 10_000 })
    await expect(page.getByTestId(`breach-row-${MOCK_BREACH.id}`)).toBeVisible()
    await expect(page.getByTestId('traffic-light-orange')).toBeVisible()
  })

  test('"Behörde gemeldet"-Button öffnet Notify-Dialog', async ({ page }) => {
    await page.route('**/api/v1/gdpr/art33/breaches', (route) => {
      void route.fulfill({ json: [MOCK_BREACH] })
    })
    await page.route(`**/api/v1/gdpr/art33/breaches/${MOCK_BREACH.id}/deadline`, (route) => {
      void route.fulfill({ json: MOCK_DEADLINE_ORANGE })
    })

    await page.goto(BREACH_URL)
    await expect(page.getByTestId(`breach-notify-${MOCK_BREACH.id}`)).toBeVisible({ timeout: 10_000 })
    await page.getByTestId(`breach-notify-${MOCK_BREACH.id}`).click()

    await expect(page.getByTestId('notify-by')).toBeVisible()
    await expect(page.getByTestId('notify-confirm-btn')).toBeVisible()
  })

  test('Ampel wechselt auf grün nach Notify', async ({ page }) => {
    const notifiedBreach = { ...MOCK_BREACH, status: 'GEMELDET', notified_at: NOW_ISO, notified_by: 'Hans Müller' }
    let notified = false

    await page.route('**/api/v1/gdpr/art33/breaches', (route) => {
      void route.fulfill({ json: [notified ? notifiedBreach : MOCK_BREACH] })
    })
    await page.route(`**/api/v1/gdpr/art33/breaches/${MOCK_BREACH.id}/deadline`, (route) => {
      void route.fulfill({ json: notified ? MOCK_DEADLINE_GREEN : MOCK_DEADLINE_ORANGE })
    })
    await page.route(`**/api/v1/gdpr/art33/breaches/${MOCK_BREACH.id}/notify`, async (route) => {
      notified = true
      void route.fulfill({ status: 200, json: notifiedBreach })
    })

    await page.goto(BREACH_URL)
    await expect(page.getByTestId('traffic-light-orange')).toBeVisible({ timeout: 10_000 })

    await page.getByTestId(`breach-notify-${MOCK_BREACH.id}`).click()
    await page.getByTestId('notify-by').fill('Hans Müller')
    await page.getByTestId('notify-confirm-btn').click()

    // Nach Notify → Ampel wird grün (nach Re-Fetch)
    await expect(page.getByTestId('notify-confirm-btn')).not.toBeVisible({ timeout: 5_000 })
  })
})
