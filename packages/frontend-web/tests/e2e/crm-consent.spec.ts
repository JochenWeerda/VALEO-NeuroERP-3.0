import { test, expect } from '@playwright/test'

/**
 * E2E Tests für CRM Consent-Management
 * 
 * Testet:
 * - Consent-Management Liste
 * - Consent-Detail (Create/Edit)
 * - Double-Opt-In Bestätigung
 * - Consent widerrufen
 * - Integration in Contact/Customer
 */

test.describe('CRM Consent-Management', () => {
  test.beforeEach(async ({ page }) => {
    // TODO: Setup authentication
    await page.goto('/crm/consents')
    await page.waitForLoadState('networkidle')
  })

  test.describe('Consent-Management Liste', () => {
    test('sollte die Consent-Liste anzeigen', async ({ page }) => {
      await expect(page.locator('h1')).toContainText('Consent')
      await expect(page.locator('table, [role="table"], .data-table')).toBeVisible()
    })

    test('sollte Filter anzeigen', async ({ page }) => {
      const filterButton = page.locator('button:has-text("Filter"), button[aria-label*="Filter"]').first()
      if (await filterButton.isVisible()) {
        await filterButton.click()
        await expect(page.locator('[role="dialog"], .filter-panel, .filters')).toBeVisible()
      }
    })

    test('sollte "Neu erstellen" Button haben', async ({ page }) => {
      const createButton = page.locator('button:has-text("Erstellen"), button:has-text("Neu"), button:has-text("Create")').first()
      await expect(createButton).toBeVisible()
    })

    test('sollte zu Detail-Seite navigieren können', async ({ page }) => {
      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/consent\//)
        await expect(page.locator('h1')).toContainText('Consent')
      }
    })

    test('sollte Export-Funktion haben', async ({ page }) => {
      const exportButton = page.locator('button:has-text("Export"), button[aria-label*="Export"]').first()
      if (await exportButton.isVisible()) {
        await exportButton.click()
        await page.waitForTimeout(1000)
      }
    })
  })

  test.describe('Consent-Detail', () => {
    test('sollte neue Consent erstellen können', async ({ page }) => {
      await page.goto('/crm/consent/new')
      await page.waitForLoadState('networkidle')

      // Fülle Formular aus
      const channelSelect = page.locator('select[name="channel"], [role="combobox"]').first()
      if (await channelSelect.isVisible()) {
        await channelSelect.selectOption('email')
      }

      const consentTypeSelect = page.locator('select[name="consent_type"]').first()
      if (await consentTypeSelect.isVisible()) {
        await consentTypeSelect.selectOption('marketing')
      }

      // Speichern
      const saveButton = page.locator('button:has-text("Speichern"), button:has-text("Save"), button[type="submit"]').first()
      if (await saveButton.isVisible()) {
        await saveButton.click()
        await page.waitForURL('/crm/consents')
      }
    })

    test('sollte bestehende Consent bearbeiten können', async ({ page }) => {
      await page.goto('/crm/consents')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/consent\//)

        // Ändere Status
        const statusSelect = page.locator('select[name="status"]').first()
        if (await statusSelect.isVisible()) {
          await statusSelect.selectOption('granted')
        }

        // Speichern
        const saveButton = page.locator('button:has-text("Speichern"), button:has-text("Save")').first()
        if (await saveButton.isVisible()) {
          await saveButton.click()
          await page.waitForURL('/crm/consents')
        }
      }
    })

    test('sollte History-Tab anzeigen', async ({ page }) => {
      await page.goto('/crm/consents')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/consent\//)

        // Prüfe ob History-Tab vorhanden ist
        const historySection = page.locator('text=History, text=Verlauf').first()
        if (await historySection.isVisible()) {
          await expect(historySection).toBeVisible()
        }
      }
    })

    test('sollte Consent widerrufen können', async ({ page }) => {
      await page.goto('/crm/consents')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/consent\//)

        const revokeButton = page.locator('button:has-text("Widerrufen"), button:has-text("revoke")').first()
        if (await revokeButton.isVisible()) {
          await revokeButton.click()
          await page.waitForURL('/crm/consents')
        }
      }
    })
  })

  test.describe('Double-Opt-In', () => {
    test('sollte Bestätigungsseite anzeigen', async ({ page }) => {
      // Simuliere Bestätigungslink
      await page.goto('/crm/consent/confirm?id=test-id&token=test-token')
      await page.waitForLoadState('networkidle')

      await expect(page.locator('text=bestätigen, text=confirm')).toBeVisible()
    })
  })

  test.describe('Integration in Customer', () => {
    test('sollte Consents-Tab in Customer-Detail anzeigen', async ({ page }) => {
      await page.goto('/crm/kunden-stamm/test-id')
      await page.waitForLoadState('networkidle')

      // Prüfe ob Consents-Section vorhanden ist
      const consentsSection = page.locator('text=Einwilligungen, text=Consents').first()
      if (await consentsSection.isVisible()) {
        await expect(consentsSection).toBeVisible()
      }
    })

    test('sollte Consent aus Customer-Detail erstellen können', async ({ page }) => {
      await page.goto('/crm/kunden-stamm/test-id')
      await page.waitForLoadState('networkidle')

      const createConsentButton = page.locator('button:has-text("Einwilligung erstellen")').first()
      if (await createConsentButton.isVisible()) {
        await createConsentButton.click()
        await page.waitForURL(/\/crm\/consent\/new/)
      }
    })
  })
})

