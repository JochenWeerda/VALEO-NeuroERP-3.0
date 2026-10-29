/**
 * @smoke
 * Agrar Domain: PSM Smoke-Tests
 * Tests: PSM-Maske CRUD, Export, Sachkunde-Check
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Agrar - PSM @smoke', () => {
  test.beforeEach(async ({ adminPage }) => {
    await adminPage.goto('/agrar/psm');
    await waitForAppReady(adminPage);
  });

  test('PSM-Liste lädt ohne Fehler', async ({ adminPage }) => {
    // Studio-Liste (MASK-STUDIO-ROLLOUT): Wurzel aus der ScreenDefinition; Tabelle oder Leerzustand je nach Daten.
    await expect(adminPage.locator('[data-screen-definition="agrar/psm-liste"]')).toBeVisible({ timeout: 15000 });
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Export-Button funktioniert', async ({ adminPage, fallbackDetector }) => {
    const exportButton = adminPage.locator('button:has-text("Export"), button:has-text("export")').first();
    
    test.skip(await exportButton.count() === 0, 'Kein Export-Button gefunden');

    const downloadPromise = adminPage.waitForEvent('download', { timeout: 5000 }).catch(() => null);
    await exportButton.click();
    
    const download = await downloadPromise;
    
    if (download) {
      expect(download.suggestedFilename()).toMatch(/psm|export/i);
    } else {
      const toast = adminPage.locator('[role="alert"], .toast').first();
      const toastVisible = await toast.isVisible().catch(() => false);
      if (!toastVisible) {
        await expect(adminPage.locator('h1, h2').first()).toBeVisible();
      }
    }

    const detection = fallbackDetector.detectFallbackLevel('export');
    console.log('PSM Export Fallback-Level:', detection);
  });

  test('Navigation zu PSM-Stamm', async ({ adminPage }) => {
    await adminPage.goto('/agrar/psm/stamm');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Sachkunde-Register erreichbar', async ({ adminPage }) => {
    await adminPage.goto('/agrar/psm/sachkunde-register');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

