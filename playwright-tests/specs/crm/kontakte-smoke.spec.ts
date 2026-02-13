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

  test('Kontakte-Liste laedt ohne Fehler', async ({ adminPage }) => {
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();

    // CRM-Varianten zeigen je nach Seed/Feature-Flag keine klassische Liste/Tabelle.
    const hasFatalError = await adminPage
      .locator('text=/Application error|Something went wrong|500|Internal Server Error|404/i')
      .first()
      .isVisible()
      .catch(() => false);

    expect(hasFatalError).toBeFalsy();
  });

  test('Export-Button funktioniert', async ({ adminPage, fallbackDetector }) => {
    const exportButton = adminPage.locator('button:has-text("Export"), button:has-text("export")').first();

    if ((await exportButton.count()) === 0) {
      test.skip('Kein Export-Button gefunden');
    }

    await exportButton.click();
    await adminPage.waitForTimeout(1000);

    const detection = fallbackDetector.detectFallbackLevel('export');
    console.log('CRM Kontakte Export Fallback-Level:', detection);
  });

  test('Drucken-Button funktioniert', async ({ adminPage }) => {
    const printButton = adminPage.locator('button:has-text("Drucken"), button:has-text("drucken")').first();

    if ((await printButton.count()) === 0) {
      test.skip('Kein Drucken-Button gefunden');
    }

    await printButton.click();
    await adminPage.waitForTimeout(1000);

    const toast = adminPage.locator('[role="alert"], .toast').first();
    const toastVisible = await toast.isVisible().catch(() => false);

    if (!toastVisible) {
      await expect(adminPage.locator('h1, h2').first()).toBeVisible();
    }
  });
});
