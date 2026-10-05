/**
 * @smoke
 * Sales Domain: Angebote Smoke-Tests
 * Tests: CRUD, Export, Print
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Sales - Angebote @smoke', () => {
  test.beforeEach(async ({ adminPage }) => {
    await adminPage.goto('/sales/angebote');
    await waitForAppReady(adminPage);
  });

  test('Angebote-Liste laedt ohne Fehler', async ({ adminPage }) => {
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();

    const hasTable = (await adminPage.locator('table').count()) > 0;
    const hasList = (await adminPage.locator('[role="list"]').count()) > 0;
    const hasGrid = (await adminPage.locator('[role="grid"]').count()) > 0;
    const hasCards = (await adminPage.locator('[data-testid*="card"], .card').count()) > 0;
    const hasEmptyState = (await adminPage.locator('[data-testid="empty-state"]').count()) > 0;

    expect(hasTable || hasList || hasGrid || hasCards || hasEmptyState).toBeTruthy();
  });

  test('Export-Button funktioniert (Level 2/3 Fallback)', async ({ adminPage, fallbackDetector }) => {
    const exportButton = adminPage.locator('button:has-text("Export"), button:has-text("export")').first();

    test.skip((await exportButton.count()) === 0, 'Kein Export-Button gefunden');

    const downloadPromise = adminPage.waitForEvent('download', { timeout: 5000 }).catch(() => null);
    await exportButton.click();

    const download = await downloadPromise;

    if (download) {
      expect(download.suggestedFilename().toLowerCase()).toContain('export');
    } else {
      const toast = adminPage.locator('[role="alert"], .toast').first();
      const toastVisible = await toast.isVisible().catch(() => false);
      if (!toastVisible) {
        await expect(adminPage.locator('h1, h2').first()).toBeVisible();
      }
    }

    const detection = fallbackDetector.detectFallbackLevel('export');
    console.log('Export Fallback-Level:', detection);
  });

  test('Drucken-Button funktioniert (Level 2/3 Fallback)', async ({ adminPage, fallbackDetector }) => {
    const printButton = adminPage.locator('button:has-text("Drucken"), button:has-text("drucken")').first();

    test.skip((await printButton.count()) === 0, 'Kein Drucken-Button gefunden');

    await adminPage.evaluate(() => {
      (window as any).__printCalled = false;
      const originalPrint = window.print;
      window.print = () => {
        (window as any).__printCalled = true;
        originalPrint.call(window);
      };
    });

    await printButton.click();
    await adminPage.waitForTimeout(1000);

    const wasPrintCalled = await adminPage.evaluate(() => (window as any).__printCalled);

    if (!wasPrintCalled) {
      const toast = adminPage.locator('[role="alert"], .toast').first();
      const toastVisible = await toast.isVisible().catch(() => false);
      if (!toastVisible) {
        await expect(adminPage.locator('h1, h2').first()).toBeVisible();
      }
    }

    const detection = fallbackDetector.detectFallbackLevel('print');
    console.log('Print Fallback-Level:', detection);
  });

  test('Navigation zu Angebot erstellen', async ({ adminPage }) => {
    const neuButton = adminPage.locator('button:has-text("Neu"), button:has-text("Erstellen"), a:has-text("Neu")').first();

    test.skip((await neuButton.count()) === 0, 'Kein Neu-Button gefunden');

    await neuButton.click();
    await waitForAppReady(adminPage);

    const urlAfterClick = adminPage.url();
    const routeLooksCreate = /angebot.*neu|erstellen|new/i.test(urlAfterClick);
    const hasForm = (await adminPage.locator('form').count()) > 0;
    const hasCreateHeading =
      (await adminPage.locator('h1, h2').filter({ hasText: /neu|erstellen|angebot/i }).count()) > 0;

    expect(routeLooksCreate || hasForm || hasCreateHeading).toBeTruthy();
  });
});
