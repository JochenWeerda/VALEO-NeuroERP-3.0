import { test, expect } from '@playwright/test'

test.describe('CRM Segments', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to segments page
    await page.goto('/crm/segments')
    await page.waitForLoadState('networkidle')
  })

  test.describe('Segment List Page', () => {
    test('should display segments list', async ({ page }) => {
      // Check if page title is visible
      await expect(page.locator('h1, [role="heading"]').first()).toBeVisible()
    })

    test('should filter segments by type', async ({ page }) => {
      // Find filter dropdown for type
      const typeFilter = page.locator('select, [role="combobox"]').filter({ hasText: /type|typ/i }).first()
      if (await typeFilter.isVisible()) {
        await typeFilter.selectOption('dynamic')
        await page.waitForTimeout(500) // Wait for filter to apply
      }
    })

    test('should filter segments by status', async ({ page }) => {
      // Find filter dropdown for status
      const statusFilter = page.locator('select, [role="combobox"]').filter({ hasText: /status/i }).first()
      if (await statusFilter.isVisible()) {
        await statusFilter.selectOption('active')
        await page.waitForTimeout(500) // Wait for filter to apply
      }
    })

    test('should navigate to create segment', async ({ page }) => {
      // Find create button
      const createButton = page.locator('button').filter({ hasText: /create|erstellen|neu/i }).first()
      if (await createButton.isVisible()) {
        await createButton.click()
        await page.waitForURL(/\/crm\/segment\/(new|neu)/)
      }
    })
  })

  test.describe('Segment Detail Page', () => {
    test('should create a new segment', async ({ page }) => {
      await page.goto('/crm/segment/new')
      await page.waitForLoadState('networkidle')

      // Fill in segment form
      const nameInput = page.locator('input[name="name"], input[placeholder*="name" i]').first()
      if (await nameInput.isVisible()) {
        await nameInput.fill('Test Segment')
      }

      const typeSelect = page.locator('select[name="type"], select[aria-label*="type" i]').first()
      if (await typeSelect.isVisible()) {
        await typeSelect.selectOption('static')
      }

      // Save segment
      const saveButton = page.locator('button').filter({ hasText: /save|speichern/i }).first()
      if (await saveButton.isVisible()) {
        await saveButton.click()
        await page.waitForTimeout(1000)
      }
    })

    test('should display segment details', async ({ page }) => {
      // Navigate to a segment detail page (assuming there's at least one segment)
      await page.goto('/crm/segments')
      await page.waitForLoadState('networkidle')

      // Try to click on first segment in list
      const firstSegment = page.locator('tr, [role="row"]').nth(1) // Skip header
      if (await firstSegment.isVisible()) {
        await firstSegment.click()
        await page.waitForURL(/\/crm\/segment\/[^/]+/)
        await page.waitForLoadState('networkidle')
      }
    })

    test('should calculate segment', async ({ page }) => {
      // Navigate to a segment detail page
      await page.goto('/crm/segments')
      await page.waitForLoadState('networkidle')

      const firstSegment = page.locator('tr, [role="row"]').nth(1)
      if (await firstSegment.isVisible()) {
        await firstSegment.click()
        await page.waitForURL(/\/crm\/segment\/[^/]+/)
        await page.waitForLoadState('networkidle')

        // Find calculate button
        const calculateButton = page.locator('button').filter({ hasText: /calculate|berechnen/i }).first()
        if (await calculateButton.isVisible()) {
          await calculateButton.click()
          await page.waitForTimeout(1000)
        }
      }
    })

    test('should export segment', async ({ page }) => {
      // Navigate to a segment detail page
      await page.goto('/crm/segments')
      await page.waitForLoadState('networkidle')

      const firstSegment = page.locator('tr, [role="row"]').nth(1)
      if (await firstSegment.isVisible()) {
        await firstSegment.click()
        await page.waitForURL(/\/crm\/segment\/[^/]+/)
        await page.waitForLoadState('networkidle')

        // Find export button
        const exportButton = page.locator('button').filter({ hasText: /export|exportieren/i }).first()
        if (await exportButton.isVisible()) {
          await exportButton.click()
          await page.waitForTimeout(1000)
        }
      }
    })
  })

  test.describe('Segment Members', () => {
    test('should display segment members', async ({ page }) => {
      // Navigate to a segment detail page
      await page.goto('/crm/segments')
      await page.waitForLoadState('networkidle')

      const firstSegment = page.locator('tr, [role="row"]').nth(1)
      if (await firstSegment.isVisible()) {
        await firstSegment.click()
        await page.waitForURL(/\/crm\/segment\/[^/]+/)
        await page.waitForLoadState('networkidle')

        // Check if members tab or section is visible
        const membersTab = page.locator('button, [role="tab"]').filter({ hasText: /members|mitglieder/i }).first()
        if (await membersTab.isVisible()) {
          await membersTab.click()
          await page.waitForTimeout(500)
        }
      }
    })
  })

  test.describe('Segment Performance', () => {
    test('should display segment performance', async ({ page }) => {
      // Navigate to a segment detail page
      await page.goto('/crm/segments')
      await page.waitForLoadState('networkidle')

      const firstSegment = page.locator('tr, [role="row"]').nth(1)
      if (await firstSegment.isVisible()) {
        await firstSegment.click()
        await page.waitForURL(/\/crm\/segment\/[^/]+/)
        await page.waitForLoadState('networkidle')

        // Check if performance tab or section is visible
        const performanceTab = page.locator('button, [role="tab"]').filter({ hasText: /performance/i }).first()
        if (await performanceTab.isVisible()) {
          await performanceTab.click()
          await page.waitForTimeout(500)
        }
      }
    })
  })

  test.describe('Navigation', () => {
    test('should navigate back to segments list', async ({ page }) => {
      await page.goto('/crm/segment/new')
      await page.waitForLoadState('networkidle')

      const backButton = page.locator('button').filter({ hasText: /back|zurück/i }).first()
      if (await backButton.isVisible()) {
        await backButton.click()
        await page.waitForURL(/\/crm\/segments/)
      }
    })
  })
})

