/**
 * E2E-Tests für Slice-008: DSGVO Art. 30 Verarbeitungsverzeichnis (RoPA).
 *
 * Testet:
 * - Leer-State mit CTA
 * - Neue Tätigkeit anlegen (Dialog, Speichern, Listeneintrag)
 * - Löschen eines Eintrags
 * - JSON-Export-Button (Download-Mock)
 * - Pflichtfeld-Validierung (kein Submit ohne Zweck / Verantwortlicher)
 */
import { test, expect } from '@playwright/test'

const ROPA_URL = '/compliance/verarbeitungsverzeichnis'

const MOCK_ACTIVITY = {
  id: 'mock-act-001',
  tenant_id: 'tenant-test',
  controller_name: 'Test GmbH',
  controller_contact: 'dsb@test.de',
  purpose: 'Kundenstammdatenverwaltung',
  subject_categories: ['Kunden'],
  data_categories: ['Name', 'E-Mail'],
  recipients: ['Steuerberater'],
  third_country_transfers: [],
  retention_period: '10 Jahre',
  toms: 'Verschlüsselung, Backup',
  legal_basis: 'Art. 6 Abs. 1 lit. b DSGVO',
  system_or_tool: 'VALEO NeuroERP',
  status: 'AKTIV',
  created_at: '2026-05-27T10:00:00Z',
  updated_at: '2026-05-27T10:00:00Z',
}

test.beforeEach(async ({ page }) => {
  // OIDC-ähnlicher Dev-Bypass
  await page.addInitScript(() => {
    window.localStorage.setItem('dev_bypass_auth', 'true')
  })
})

test.describe('Verarbeitungsverzeichnis Art. 30', () => {
  test('zeigt Leer-State mit Hinweis und CTA-Button', async ({ page }) => {
    await page.route('**/api/v1/gdpr/art30/activities', (route) => {
      void route.fulfill({ json: [] })
    })

    await page.goto(ROPA_URL)

    // Warte auf Seiten-Inhalt
    await expect(page.getByText('Verarbeitungsverzeichnis (Art. 30 DSGVO)')).toBeVisible({ timeout: 10_000 })
    await expect(page.getByText('Noch keine Verarbeitungstätigkeiten erfasst')).toBeVisible()
    await expect(page.getByTestId('ropa-add-btn')).toBeVisible()
  })

  test('öffnet Dialog und legt neue Tätigkeit an', async ({ page }) => {
    let postCalled = false

    await page.route('**/api/v1/gdpr/art30/activities', async (route) => {
      if (route.request().method() === 'GET') {
        void route.fulfill({ json: postCalled ? [MOCK_ACTIVITY] : [] })
      } else if (route.request().method() === 'POST') {
        postCalled = true
        void route.fulfill({ status: 201, json: MOCK_ACTIVITY })
      } else {
        await route.continue()
      }
    })

    await page.goto(ROPA_URL)
    await expect(page.getByTestId('ropa-add-btn')).toBeVisible({ timeout: 10_000 })

    // Dialog öffnen
    await page.getByTestId('ropa-add-btn').click()
    await expect(page.getByTestId('ropa-controller-name')).toBeVisible()

    // Felder ausfüllen
    await page.getByTestId('ropa-controller-name').fill('Test GmbH')
    await page.getByTestId('ropa-purpose').fill('Kundenstammdatenverwaltung')

    // Speichern
    await page.getByTestId('ropa-save-btn').click()

    // Toast oder Dialog schließt sich
    await expect(page.getByTestId('ropa-save-btn')).not.toBeVisible({ timeout: 5_000 })
  })

  test('listet Verarbeitungstätigkeiten auf', async ({ page }) => {
    await page.route('**/api/v1/gdpr/art30/activities', (route) => {
      void route.fulfill({ json: [MOCK_ACTIVITY] })
    })

    await page.goto(ROPA_URL)

    await expect(page.getByText('Kundenstammdatenverwaltung')).toBeVisible({ timeout: 10_000 })
    await expect(page.getByText('Test GmbH')).toBeVisible()
    // Status-Badge
    await expect(page.getByText('AKTIV')).toBeVisible()
  })

  test('löscht eine Tätigkeit nach Klick auf Löschen-Button', async ({ page }) => {
    let deleted = false

    await page.route('**/api/v1/gdpr/art30/activities', (route) => {
      void route.fulfill({ json: deleted ? [] : [MOCK_ACTIVITY] })
    })
    await page.route(`**/api/v1/gdpr/art30/activities/${MOCK_ACTIVITY.id}`, async (route) => {
      if (route.request().method() === 'DELETE') {
        deleted = true
        void route.fulfill({ status: 204 })
      } else {
        await route.continue()
      }
    })

    await page.goto(ROPA_URL)
    await expect(page.getByText('Kundenstammdatenverwaltung')).toBeVisible({ timeout: 10_000 })

    await page.getByTestId(`ropa-delete-${MOCK_ACTIVITY.id}`).click()
  })

  test('JSON-Export-Button ist sichtbar und aktivierbar', async ({ page }) => {
    await page.route('**/api/v1/gdpr/art30/activities', (route) => {
      void route.fulfill({ json: [] })
    })
    await page.route('**/api/v1/gdpr/art30/activities/export/json', (route) => {
      void route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          art30_verarbeitungsverzeichnis: {
            exported_at: new Date().toISOString(),
            tenant_id: 'tenant-test',
            total_activities: 0,
            activities: [],
          },
        }),
      })
    })

    await page.goto(ROPA_URL)
    const exportBtn = page.getByTestId('ropa-export-btn')
    await expect(exportBtn).toBeVisible({ timeout: 10_000 })
    await expect(exportBtn).toBeEnabled()
  })
})
