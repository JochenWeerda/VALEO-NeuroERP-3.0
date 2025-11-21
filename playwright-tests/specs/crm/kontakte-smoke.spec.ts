/**
 * @smoke
 * CRM Domain: Kontakte Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('CRM - Kontakte @smoke', () => {
  test.beforeEach(async ({ adminPage }) => {
    await adminPage.goto('/crm/kontakte-liste');
    await adminPage.waitForLoadState('networkidle');
  });

  test('Kontakte-Liste lädt ohne Fehler', async ({ adminPage }) => {
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
    
    const hasTable = await adminPage.locator('table').count() > 0;
    const hasList = await adminPage.locator('[role="list"]').count() > 0;
    
    expect(hasTable || hasList).toBeTruthy();
  });

  test('Export-Button funktioniert', async ({ adminPage, fallbackDetector }) => {
    const exportButton = adminPage.locator('button:has-text("Export"), button:has-text("export")').first();
    
    if (await exportButton.count() === 0) {
      test.skip('Kein Export-Button gefunden');
    }

    await exportButton.click();
    await adminPage.waitForTimeout(1000);

    const detection = fallbackDetector.detectFallbackLevel('export');
    console.log('CRM Kontakte Export Fallback-Level:', detection);
  });

  test('Drucken-Button funktioniert', async ({ adminPage }) => {
    const printButton = adminPage.locator('button:has-text("Drucken"), button:has-text("drucken")').first();
    
    if (await printButton.count() === 0) {
      test.skip('Kein Drucken-Button gefunden');
    }

    await printButton.click();
    await adminPage.waitForTimeout(1000);
    
    // Toast oder Print-Dialog
    const toast = adminPage.locator('[role="alert"], .toast').first();
    const toastVisible = await toast.isVisible().catch(() => false);
    
    expect(toastVisible).toBeTruthy();
  });
});

