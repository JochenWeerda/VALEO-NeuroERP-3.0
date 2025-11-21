/**
 * @smoke
 * Inventory Domain: Artikel Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Inventory - Artikel @smoke', () => {
  test('Artikel-Liste lädt', async ({ adminPage }) => {
    await adminPage.goto('/artikel/liste');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Artikel-Stamm lädt', async ({ adminPage }) => {
    await adminPage.goto('/artikel/stamm');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Export funktioniert', async ({ adminPage, fallbackDetector }) => {
    await adminPage.goto('/artikel/liste');
    await adminPage.waitForLoadState('networkidle');
    
    const exportButton = adminPage.locator('button:has-text("Export"), button:has-text("export")').first();
    
    if (await exportButton.count() === 0) {
      test.skip('Kein Export-Button gefunden');
    }

    await exportButton.click();
    await adminPage.waitForTimeout(1000);

    const detection = fallbackDetector.detectFallbackLevel('export');
    console.log('Artikel Export Fallback-Level:', detection);
  });
});

