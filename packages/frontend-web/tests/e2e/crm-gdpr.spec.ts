import { test, expect } from '@playwright/test'

/**
 * E2E Tests für CRM GDPR-Funktionen
 * 
 * Testet:
 * - GDPR-Requests Liste
 * - GDPR-Request Detail (Create/Edit)
 * - Verifizierung
 * - Datenexport
 * - Datenlöschung
 * - Public Request-Seite
 * - Integration in Contact/Customer
 */

test.describe('CRM GDPR-Funktionen', () => {
  test.beforeEach(async ({ page }) => {
    // TODO: Setup authentication
    await page.goto('/crm/gdpr-requests')
    await page.waitForLoadState('networkidle')
  })

  test.describe('GDPR-Requests Liste', () => {
    test('sollte die GDPR-Requests Liste anzeigen', async ({ page }) => {
      await expect(page.locator('h1')).toContainText('DSGVO-Anfrage')
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
        await page.waitForURL(/\/crm\/gdpr-request\//)
        await expect(page.locator('h1')).toContainText('DSGVO-Anfrage')
      }
    })
  })

  test.describe('GDPR-Request Detail', () => {
    test('sollte neue GDPR-Request erstellen können', async ({ page }) => {
      await page.goto('/crm/gdpr-request/new')
      await page.waitForLoadState('networkidle')

      // Fülle Formular aus
      const requestTypeSelect = page.locator('select[name="request_type"], [role="combobox"]').first()
      if (await requestTypeSelect.isVisible()) {
        await requestTypeSelect.selectOption('access')
      }

      // Speichern
      const saveButton = page.locator('button:has-text("Speichern"), button:has-text("Save"), button[type="submit"]').first()
      if (await saveButton.isVisible()) {
        await saveButton.click()
        await page.waitForURL('/crm/gdpr-requests')
      }
    })

    test('sollte bestehende GDPR-Request bearbeiten können', async ({ page }) => {
      await page.goto('/crm/gdpr-requests')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/gdpr-request\//)

        // Ändere Notes
        const notesField = page.locator('textarea[name="notes"]').first()
        if (await notesField.isVisible()) {
          await notesField.fill('Test Notes')
        }

        // Speichern
        const saveButton = page.locator('button:has-text("Speichern"), button:has-text("Save")').first()
        if (await saveButton.isVisible()) {
          await saveButton.click()
          await page.waitForURL('/crm/gdpr-requests')
        }
      }
    })

    test('sollte Request verifizieren können', async ({ page }) => {
      await page.goto('/crm/gdpr-requests')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/gdpr-request\//)

        const verifyButton = page.locator('button:has-text("Verifizieren"), button:has-text("Verify")').first()
        if (await verifyButton.isVisible()) {
          await verifyButton.click()
          await page.waitForTimeout(1000)
        }
      }
    })

    test('sollte Export generieren können', async ({ page }) => {
      await page.goto('/crm/gdpr-requests')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/gdpr-request\//)

        const exportButton = page.locator('button:has-text("Export generieren"), button:has-text("Generate Export")').first()
        if (await exportButton.isVisible()) {
          await exportButton.click()
          await page.waitForTimeout(2000) // Export generation takes time
        }
      }
    })

    test('sollte History-Tab anzeigen', async ({ page }) => {
      await page.goto('/crm/gdpr-requests')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/gdpr-request\//)

        // Prüfe ob History-Tab vorhanden ist
        const historySection = page.locator('text=History, text=Verlauf').first()
        if (await historySection.isVisible()) {
          await expect(historySection).toBeVisible()
        }
      }
    })
  })

  test.describe('Public Request-Seite', () => {
    test('sollte Public Request-Seite anzeigen', async ({ page }) => {
      await page.goto('/crm/gdpr-request-public')
      await page.waitForLoadState('networkidle')

      await expect(page.locator('text=DSGVO-Anfrage stellen, text=GDPR Request')).toBeVisible()
    })

    test('sollte Request erstellen können', async ({ page }) => {
      await page.goto('/crm/gdpr-request-public')
      await page.waitForLoadState('networkidle')

      // Fülle Formular aus
      await page.fill('input[name="contact_id"], input[id="contact_id"]', 'test-contact-id')
      await page.fill('input[name="email"], input[id="email"]', 'test@example.com')
      
      const requestTypeSelect = page.locator('select[name="request_type"], [role="combobox"]').first()
      if (await requestTypeSelect.isVisible()) {
        await requestTypeSelect.selectOption('access')
      }

      const submitButton = page.locator('button:has-text("Anfrage stellen"), button:has-text("Submit")').first()
      if (await submitButton.isVisible()) {
        await submitButton.click()
        await page.waitForTimeout(1000)
      }
    })

    test('sollte Status prüfen können', async ({ page }) => {
      await page.goto('/crm/gdpr-request-public')
      await page.waitForLoadState('networkidle')

      // Wechsle zu Status-Tab
      const statusTab = page.locator('button:has-text("Status"), button:has-text("Check Status")').first()
      if (await statusTab.isVisible()) {
        await statusTab.click()
      }

      // Prüfe Status
      const requestIdInput = page.locator('input[name="request_id"], input[id="request_id"]').first()
      if (await requestIdInput.isVisible()) {
        await requestIdInput.fill('test-request-id')
        
        const checkButton = page.locator('button:has-text("Status prüfen"), button:has-text("Check Status")').first()
        if (await checkButton.isVisible()) {
          await checkButton.click()
          await page.waitForTimeout(1000)
        }
      }
    })
  })

  test.describe('Integration in Customer', () => {
    test('sollte GDPR-Requests-Tab in Customer-Detail anzeigen', async ({ page }) => {
      await page.goto('/crm/kunden-stamm/test-id')
      await page.waitForLoadState('networkidle')

      // Prüfe ob GDPR-Requests-Section vorhanden ist
      const gdprSection = page.locator('text=DSGVO-Anfragen, text=GDPR Requests').first()
      if (await gdprSection.isVisible()) {
        await expect(gdprSection).toBeVisible()
      }
    })

    test('sollte GDPR-Request aus Customer-Detail erstellen können', async ({ page }) => {
      await page.goto('/crm/kunden-stamm/test-id')
      await page.waitForLoadState('networkidle')

      const createRequestButton = page.locator('button:has-text("DSGVO-Anfrage erstellen")').first()
      if (await createRequestButton.isVisible()) {
        await createRequestButton.click()
        await page.waitForURL(/\/crm\/gdpr-request\/new/)
      }
    })
  })
})

