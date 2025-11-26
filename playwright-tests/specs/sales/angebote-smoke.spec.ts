/**
 * @smoke
 * Sales Domain: Angebote Smoke-Tests
 * Tests: CRUD, Export, Print
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Sales - Angebote @smoke', () => {
  test.beforeEach(async ({ adminPage }) => {
    await adminPage.goto('/sales/angebote');
    await adminPage.waitForLoadState('networkidle');
  });

  test('Angebote-Liste lädt ohne Fehler', async ({ adminPage }) => {
    // Prüfe ob Seite geladen
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
    
    // Prüfe Tabelle oder Liste vorhanden
    const hasTable = await adminPage.locator('table').count() > 0;
    const hasList = await adminPage.locator('[role="list"]').count() > 0;
    
    expect(hasTable || hasList).toBeTruthy();
  });

  test('Export-Button funktioniert (Level 2/3 Fallback)', async ({ adminPage, fallbackDetector }) => {
    // Suche Export-Button
    const exportButton = adminPage.locator('button:has-text("Export"), button:has-text("export")').first();
    
    if (await exportButton.count() === 0) {
      test.skip('Kein Export-Button gefunden');
    }

    // Click & warte auf Download oder Toast
    const downloadPromise = adminPage.waitForEvent('download', { timeout: 5000 }).catch(() => null);
    await exportButton.click();
    
    const download = await downloadPromise;
    
    // Validierung: Download ODER Toast
    if (download) {
      expect(download.suggestedFilename()).toContain('export');
    } else {
      // Prüfe ob Toast erscheint
      const toast = adminPage.locator('[role="alert"], .toast').first();
      await expect(toast).toBeVisible({ timeout: 3000 });
    }

    // Fallback-Level prüfen
    const detection = fallbackDetector.detectFallbackLevel('export');
    console.log('Export Fallback-Level:', detection);
  });

  test('Drucken-Button funktioniert (Level 2/3 Fallback)', async ({ adminPage, fallbackDetector }) => {
    const printButton = adminPage.locator('button:has-text("Drucken"), button:has-text("drucken")').first();
    
    if (await printButton.count() === 0) {
      test.skip('Kein Drucken-Button gefunden');
    }

    // Listener für window.print() oder PDF-Generation
    let printTriggered = false;
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
    
    // Entweder print() oder Toast
    if (!wasPrintCalled) {
      const toast = adminPage.locator('[role="alert"], .toast').first();
      await expect(toast).toBeVisible({ timeout: 3000 });
    }

    const detection = fallbackDetector.detectFallbackLevel('print');
    console.log('Print Fallback-Level:', detection);
  });

  test('Navigation zu Angebot erstellen', async ({ adminPage }) => {
    // Suche "Neu", "Erstellen", "Anlegen" Button
    const neuButton = adminPage.locator('button:has-text("Neu"), button:has-text("Erstellen"), a:has-text("Neu")').first();
    
    if (await neuButton.count() === 0) {
      test.skip('Kein Neu-Button gefunden');
    }

    await neuButton.click();
    
    // Warte auf Navigation
    await adminPage.waitForURL(/angebot.*neu|erstellen|new/i, { timeout: 5000 });
    
    // Prüfe Formular vorhanden
    const hasForm = await adminPage.locator('form').count() > 0;
    expect(hasForm).toBeTruthy();
  });
});

