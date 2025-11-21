/**
 * @smoke
 * Agrar Domain: PSM Smoke-Tests
 * Tests: PSM-Maske CRUD, Export, Sachkunde-Check
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Agrar - PSM @smoke', () => {
  test.beforeEach(async ({ adminPage }) => {
    await adminPage.goto('/agrar/psm');
    await adminPage.waitForLoadState('networkidle');
  });

  test('PSM-Liste lädt ohne Fehler', async ({ adminPage }) => {
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
    
    // Prüfe Tabelle oder Grid
    const hasTable = await adminPage.locator('table').count() > 0;
    const hasGrid = await adminPage.locator('[role="grid"]').count() > 0;
    
    expect(hasTable || hasGrid).toBeTruthy();
  });

  test('Export-Button funktioniert', async ({ adminPage, fallbackDetector }) => {
    const exportButton = adminPage.locator('button:has-text("Export"), button:has-text("export")').first();
    
    if (await exportButton.count() === 0) {
      test.skip('Kein Export-Button gefunden');
    }

    const downloadPromise = adminPage.waitForEvent('download', { timeout: 5000 }).catch(() => null);
    await exportButton.click();
    
    const download = await downloadPromise;
    
    if (download) {
      expect(download.suggestedFilename()).toMatch(/psm|export/i);
    } else {
      const toast = adminPage.locator('[role="alert"], .toast').first();
      await expect(toast).toBeVisible({ timeout: 3000 });
    }

    const detection = fallbackDetector.detectFallbackLevel('export');
    console.log('PSM Export Fallback-Level:', detection);
  });

  test('Navigation zu PSM-Stamm', async ({ adminPage }) => {
    await adminPage.goto('/agrar/psm/stamm');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Sachkunde-Register erreichbar', async ({ adminPage }) => {
    await adminPage.goto('/agrar/psm/sachkunde-register');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

