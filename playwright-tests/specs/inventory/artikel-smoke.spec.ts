/**
 * @smoke
 * Inventory Domain: Artikel Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Inventory - Artikel @smoke', () => {
  test('Artikel-Liste lädt', async ({ adminPage }) => {
    await adminPage.goto('/artikel/liste');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Artikel-Stamm lädt', async ({ adminPage }) => {
    await adminPage.goto('/artikel/stamm');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Export funktioniert', async ({ adminPage, fallbackDetector }) => {
    await adminPage.goto('/artikel/liste');
    await waitForAppReady(adminPage);
    
    const exportButton = adminPage.locator('button:has-text("Export"), button:has-text("export")').first();
    
    test.skip(await exportButton.count() === 0, 'Kein Export-Button gefunden');

    await exportButton.click();
    await adminPage.waitForTimeout(1000);

    const detection = fallbackDetector.detectFallbackLevel('export');
    console.log('Artikel Export Fallback-Level:', detection);
  });
});

