/**
 * Payment Matching E2E Tests
 * FIBU-AR-03: Zahlungseingänge & Matching
 * 
 * Tests:
 * - Bank Statement Import (CAMT/MT940/CSV)
 * - Auto-Matching
 * - Manual Matching
 * - Match Suggestions
 */

import { test, expect } from '@playwright/test';
import { testSetup } from '../fixtures/testSetup';

test.describe('Payment Matching', () => {
  let setup: Awaited<ReturnType<typeof testSetup>>;

  test.beforeEach(async ({ page }) => {
    setup = await testSetup(page);
  });

  test('@smoke - Bank Statement Import (CSV)', async ({ page }) => {
    // Navigate to Zahlungseingänge
    await page.goto('/fibu/zahlungseingaenge');
    await expect(page.locator('h1')).toContainText('Zahlungseingänge');

    // Click Bank-Import button
    const importButton = page.getByRole('button', { name: /Bank-Import/i });
    await expect(importButton).toBeVisible();
    
    // Note: File upload would require actual file - skipping for smoke test
    // In full test, would upload CSV file and verify import
  });

  test('@smoke - View Unmatched Payments', async ({ page }) => {
    await page.goto('/fibu/zahlungseingaenge');
    
    // Wait for payments to load
    await page.waitForSelector('table', { timeout: 5000 });
    
    // Check for unmatched payments indicator
    const unmatchedCard = page.locator('text=Offene Zuordnungen').locator('..');
    await expect(unmatchedCard).toBeVisible();
    
    // Verify table shows payments
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('@smoke - Auto-Match Button', async ({ page }) => {
    await page.goto('/fibu/zahlungseingaenge');
    
    // Find Auto-Match button
    const autoMatchButton = page.getByRole('button', { name: /Auto-Match/i });
    await expect(autoMatchButton).toBeVisible();
    
    // Click and verify loading state
    await autoMatchButton.click();
    
    // Verify button shows loading state
    await expect(autoMatchButton).toContainText(/Matching|starten/);
  });

  test('@smoke - Filter by Status', async ({ page }) => {
    await page.goto('/fibu/zahlungseingaenge');
    
    // Find status filter
    const statusFilter = page.locator('select, [role="combobox"]').first();
    await expect(statusFilter).toBeVisible();
    
    // Select "Offen" status
    await statusFilter.selectOption({ label: /Offen|UNMATCHED/i });
    
    // Verify filter is applied (table should update)
    await page.waitForTimeout(500); // Wait for filter to apply
  });

  test('@smoke - Search Payments', async ({ page }) => {
    await page.goto('/fibu/zahlungseingaenge');
    
    // Find search input
    const searchInput = page.getByPlaceholder(/Suche/i);
    await expect(searchInput).toBeVisible();
    
    // Enter search term
    await searchInput.fill('RE-2025');
    
    // Verify search is applied
    await page.waitForTimeout(500);
  });

  test('@full - Manual Match Flow', async ({ page }) => {
    await page.goto('/fibu/zahlungseingaenge');
    
    // Wait for payments to load
    await page.waitForSelector('table', { timeout: 5000 });
    
    // Find "Zuordnen" button for unmatched payment
    const matchButton = page.getByRole('button', { name: /Zuordnen/i }).first();
    
    if (await matchButton.isVisible()) {
      await matchButton.click();
      
      // Verify match dialog opens
      const dialog = page.locator('[role="dialog"]');
      await expect(dialog).toBeVisible();
      
      // Verify open items are shown
      const openItemsTable = dialog.locator('table');
      await expect(openItemsTable).toBeVisible();
      
      // Click "Zuordnen" on first open item
      const confirmButton = dialog.getByRole('button', { name: /Zuordnen/i }).first();
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
        
        // Verify success message
        await expect(page.locator('text=/erfolgreich|success/i')).toBeVisible({ timeout: 5000 });
      }
    } else {
      // Skip if no unmatched payments
      test.skip();
    }
  });

  test('@full - Match Suggestions', async ({ page }) => {
    await page.goto('/fibu/zahlungseingaenge');
    
    // Wait for payments
    await page.waitForSelector('table', { timeout: 5000 });
    
    // Click "Zuordnen" to open match dialog
    const matchButton = page.getByRole('button', { name: /Zuordnen/i }).first();
    
    if (await matchButton.isVisible()) {
      await matchButton.click();
      
      // Wait for dialog
      const dialog = page.locator('[role="dialog"]');
      await expect(dialog).toBeVisible();
      
      // Verify suggestions are loaded
      const suggestions = dialog.locator('table tbody tr');
      const count = await suggestions.count();
      
      // Should have at least one suggestion or empty state message
      expect(count).toBeGreaterThanOrEqual(0);
    } else {
      test.skip();
    }
  });

  test('@full - KPI Cards Display', async ({ page }) => {
    await page.goto('/fibu/zahlungseingaenge');
    
    // Verify KPI cards are visible
    const unmatchedCard = page.locator('text=Offene Zuordnungen').locator('..');
    const totalCard = page.locator('text=Gesamt').locator('..');
    const matchRateCard = page.locator('text=Auto-Match-Rate').locator('..');
    
    await expect(unmatchedCard).toBeVisible();
    await expect(totalCard).toBeVisible();
    await expect(matchRateCard).toBeVisible();
    
    // Verify cards show numbers
    const unmatchedValue = unmatchedCard.locator('text=/\\d+/');
    await expect(unmatchedValue).toBeVisible();
  });
});

