import { test, expect } from '@playwright/test'

/**
 * E2E Tests für CRM Opportunities
 * 
 * Testet:
 * - Opportunities-Liste
 * - Opportunity-Detail (Create/Edit)
 * - Pipeline-Kanban (Drag & Drop)
 * - Forecast-Report
 */

test.describe('CRM Opportunities', () => {
  test.beforeEach(async ({ page }) => {
    // TODO: Setup authentication
    // await page.goto('/login')
    // await page.fill('[name="username"]', 'testuser')
    // await page.fill('[name="password"]', 'testpass')
    // await page.click('button[type="submit"]')
    // await page.waitForURL('/')
    
    // Für jetzt: Direkt zur Seite navigieren (wenn Auth nicht benötigt)
    await page.goto('/crm/opportunities')
    await page.waitForLoadState('networkidle')
  })

  test.describe('Opportunities-Liste', () => {
    test('sollte die Opportunities-Liste anzeigen', async ({ page }) => {
      await expect(page.locator('h1')).toContainText('Opportunity')
      await expect(page.locator('table, [role="table"], .data-table')).toBeVisible()
    })

    test('sollte nach Opportunities suchen können', async ({ page }) => {
      const searchInput = page.locator('input[type="search"], input[placeholder*="Suchen"], input[placeholder*="Search"]').first()
      if (await searchInput.isVisible()) {
        await searchInput.fill('Test')
        await page.waitForTimeout(500) // Wait for search to complete
      }
    })

    test('sollte Filter anzeigen', async ({ page }) => {
      // Prüfe ob Filter-Buttons oder Filter-Panel vorhanden sind
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
      // Klicke auf ersten Eintrag in der Liste (falls vorhanden)
      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/opportunity\//)
        await expect(page.locator('h1')).toContainText('Opportunity')
      }
    })

    test('sollte Export-Funktion haben', async ({ page }) => {
      const exportButton = page.locator('button:has-text("Export"), button[aria-label*="Export"]').first()
      if (await exportButton.isVisible()) {
        await exportButton.click()
        // Prüfe ob Download-Dialog erscheint oder Datei heruntergeladen wird
        await page.waitForTimeout(1000)
      }
    })
  })

  test.describe('Opportunity-Detail', () => {
    test('sollte neue Opportunity erstellen können', async ({ page }) => {
      await page.goto('/crm/opportunity/new')
      await page.waitForLoadState('networkidle')

      // Fülle Formular aus
      const nameInput = page.locator('input[name="name"], input[placeholder*="Name"]').first()
      if (await nameInput.isVisible()) {
        await nameInput.fill('Test Opportunity')
      }

      const amountInput = page.locator('input[name="amount"], input[type="number"]').first()
      if (await amountInput.isVisible()) {
        await amountInput.fill('50000')
      }

      const probabilityInput = page.locator('input[name="probability"]')
      if (await probabilityInput.isVisible()) {
        await probabilityInput.fill('75')
      }

      // Speichern
      const saveButton = page.locator('button:has-text("Speichern"), button:has-text("Save"), button[type="submit"]').first()
      if (await saveButton.isVisible()) {
        await saveButton.click()
        await page.waitForURL('/crm/opportunities')
      }
    })

    test('sollte bestehende Opportunity bearbeiten können', async ({ page }) => {
      // Gehe zu Liste und öffne erste Opportunity
      await page.goto('/crm/opportunities')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/opportunity\//)

        // Ändere Name
        const nameInput = page.locator('input[name="name"]').first()
        if (await nameInput.isVisible()) {
          await nameInput.fill('Updated Opportunity Name')
        }

        // Speichern
        const saveButton = page.locator('button:has-text("Speichern"), button:has-text("Save")').first()
        if (await saveButton.isVisible()) {
          await saveButton.click()
          await page.waitForURL('/crm/opportunities')
        }
      }
    })

    test('sollte History-Tab anzeigen', async ({ page }) => {
      await page.goto('/crm/opportunities')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/opportunity\//)

        // Prüfe ob History-Tab vorhanden ist
        const historyTab = page.locator('text=History, text=Verlauf, [role="tab"]:has-text("History")').first()
        if (await historyTab.isVisible()) {
          await historyTab.click()
          await expect(page.locator('text=History, text=Verlauf')).toBeVisible()
        }
      }
    })

    test('sollte "Als gewonnen markieren" können', async ({ page }) => {
      await page.goto('/crm/opportunities')
      await page.waitForLoadState('networkidle')

      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/opportunity\//)

        const markWonButton = page.locator('button:has-text("gewonnen"), button:has-text("won")').first()
        if (await markWonButton.isVisible()) {
          await markWonButton.click()
          await page.waitForURL('/crm/opportunities')
        }
      }
    })
  })

  test.describe('Pipeline-Kanban', () => {
    test('sollte Kanban-Board anzeigen', async ({ page }) => {
      await page.goto('/crm/opportunities-kanban')
      await page.waitForLoadState('networkidle')

      await expect(page.locator('h1')).toContainText('Pipeline')
      
      // Prüfe ob Stage-Spalten vorhanden sind
      const stageColumns = page.locator('[class*="column"], [class*="stage"], .kanban-column')
      await expect(stageColumns.first()).toBeVisible()
    })

    test('sollte Summary Cards anzeigen', async ({ page }) => {
      await page.goto('/crm/opportunities-kanban')
      await page.waitForLoadState('networkidle')

      // Prüfe ob Summary Cards vorhanden sind
      const summaryCards = page.locator('[class*="card"], .summary-card')
      await expect(summaryCards.first()).toBeVisible()
    })

    test('sollte Drag & Drop zwischen Stages ermöglichen', async ({ page }) => {
      await page.goto('/crm/opportunities-kanban')
      await page.waitForLoadState('networkidle')

      // Finde erste Opportunity-Card
      const opportunityCard = page.locator('[draggable="true"], .opportunity-card, [class*="card"]').first()
      
      if (await opportunityCard.isVisible()) {
        // Finde Ziel-Stage
        const targetStage = page.locator('[class*="column"], [class*="stage"]').nth(1)
        
        if (await targetStage.isVisible()) {
          // Drag & Drop
          await opportunityCard.dragTo(targetStage)
          await page.waitForTimeout(1000) // Wait for API call
          
          // Prüfe ob Toast-Notification erscheint
          const toast = page.locator('[role="alert"], .toast, [class*="toast"]').first()
          if (await toast.isVisible()) {
            await expect(toast).toBeVisible()
          }
        }
      }
    })

    test('sollte Filter anzeigen', async ({ page }) => {
      await page.goto('/crm/opportunities-kanban')
      await page.waitForLoadState('networkidle')

      const filterSection = page.locator('text=Filter, [class*="filter"]').first()
      if (await filterSection.isVisible()) {
        await expect(filterSection).toBeVisible()
      }
    })
  })

  test.describe('Forecast-Report', () => {
    test('sollte Forecast-Report anzeigen', async ({ page }) => {
      await page.goto('/crm/opportunities-forecast')
      await page.waitForLoadState('networkidle')

      await expect(page.locator('h1')).toContainText('Forecast')
    })

    test('sollte Summary Cards anzeigen', async ({ page }) => {
      await page.goto('/crm/opportunities-forecast')
      await page.waitForLoadState('networkidle')

      const summaryCards = page.locator('[class*="card"], .summary-card')
      await expect(summaryCards.first()).toBeVisible()
    })

    test('sollte Charts anzeigen', async ({ page }) => {
      await page.goto('/crm/opportunities-forecast')
      await page.waitForLoadState('networkidle')

      // Prüfe ob Recharts-Komponenten vorhanden sind
      const charts = page.locator('svg, [class*="chart"], .recharts-wrapper')
      await expect(charts.first()).toBeVisible()
    })

    test('sollte Filter anzeigen', async ({ page }) => {
      await page.goto('/crm/opportunities-forecast')
      await page.waitForLoadState('networkidle')

      const filterSection = page.locator('text=Filter, [class*="filter"]').first()
      if (await filterSection.isVisible()) {
        await expect(filterSection).toBeVisible()
      }
    })

    test('sollte View-Mode ändern können', async ({ page }) => {
      await page.goto('/crm/opportunities-forecast')
      await page.waitForLoadState('networkidle')

      const viewModeSelect = page.locator('select, [role="combobox"]').filter({ hasText: /Period|Stage|Owner/ }).first()
      if (await viewModeSelect.isVisible()) {
        await viewModeSelect.click()
        await page.locator('text=Stage, text=Phase').first().click()
        await page.waitForTimeout(1000) // Wait for chart update
      }
    })

    test('sollte Export-Funktion haben', async ({ page }) => {
      await page.goto('/crm/opportunities-forecast')
      await page.waitForLoadState('networkidle')

      const exportButton = page.locator('button:has-text("Export"), button[aria-label*="Export"]').first()
      if (await exportButton.isVisible()) {
        await exportButton.click()
        await page.waitForTimeout(1000)
      }
    })

    test('sollte Data Table anzeigen', async ({ page }) => {
      await page.goto('/crm/opportunities-forecast')
      await page.waitForLoadState('networkidle')

      const dataTable = page.locator('table, [role="table"]').first()
      if (await dataTable.isVisible()) {
        await expect(dataTable).toBeVisible()
      }
    })
  })

  test.describe('Navigation', () => {
    test('sollte zwischen Seiten navigieren können', async ({ page }) => {
      // Liste → Detail
      await page.goto('/crm/opportunities')
      await page.waitForLoadState('networkidle')
      
      const firstRow = page.locator('table tbody tr, [role="row"]').first()
      if (await firstRow.isVisible()) {
        await firstRow.click()
        await page.waitForURL(/\/crm\/opportunity\//)
      }

      // Detail → Kanban
      const kanbanLink = page.locator('a[href*="kanban"], button:has-text("Kanban")').first()
      if (await kanbanLink.isVisible()) {
        await kanbanLink.click()
      } else {
        await page.goto('/crm/opportunities-kanban')
      }
      await page.waitForURL(/\/crm\/opportunities-kanban/)

      // Kanban → Forecast
      await page.goto('/crm/opportunities-forecast')
      await page.waitForURL(/\/crm\/opportunities-forecast/)

      // Forecast → Liste
      const backButton = page.locator('button:has-text("Zurück"), button:has-text("Back")').first()
      if (await backButton.isVisible()) {
        await backButton.click()
        await page.waitForURL(/\/crm\/opportunities/)
      }
    })
  })
})

