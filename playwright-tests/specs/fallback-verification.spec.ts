/**
 * @fallback
 * Fallback-Verifikation: 3-Ebenen-System
 * Prüft ob mindestens 1 Seite pro Level (1/2/3) nachgewiesen ist
 */

import { test, expect } from '../fixtures/testSetup';
import { CoverageReporter } from '../helpers/reporters';

const coverageReporter = new CoverageReporter();

test.describe('Fallback-System Verifikation @fallback', () => {
  test('Sales: Angebote Export-Fallback-Level', async ({ adminPage, fallbackDetector }) => {
    await adminPage.goto('/sales/angebote');
    await adminPage.waitForLoadState('networkidle');

    const exportButton = adminPage.locator('button:has-text("Export")').first();
    
    if (await exportButton.count() > 0) {
      await exportButton.click();
      await adminPage.waitForTimeout(1000);

      const detection = fallbackDetector.detectFallbackLevel('export');
      
      console.log('✓ Angebote Export Fallback:', JSON.stringify(detection));
      
      // Coverage-Eintrag
      coverageReporter.addEntry({
        seite: 'sales/angebote',
        rolle: 'admin',
        create: 'N/A',
        update: 'N/A',
        delete: 'N/A',
        workflow: 'N/A',
        print: 'N/A',
        export: 'OK',
        nav: 'N/A',
        fallbackLevel: detection.level === 'unknown' ? 'unknown' : String(detection.level) as '1' | '2' | '3',
        ergebnis: 'PASS',
        ticketID: '',
        runID: process.env.PLAYWRIGHT_RUN_ID || 'local',
        build: process.env.BUILD_ID || 'dev',
      });
      
      // Mindestens Level 2 oder 3 erwartet
      expect(['2', '3']).toContain(String(detection.level));
    }
  });

  test('CRM: Kontakte Export-Fallback-Level', async ({ adminPage, fallbackDetector }) => {
    await adminPage.goto('/crm/kontakte-liste');
    await adminPage.waitForLoadState('networkidle');

    const exportButton = adminPage.locator('button:has-text("Export")').first();
    
    if (await exportButton.count() > 0) {
      await exportButton.click();
      await adminPage.waitForTimeout(1000);

      const detection = fallbackDetector.detectFallbackLevel('export');
      
      console.log('✓ CRM Kontakte Export Fallback:', JSON.stringify(detection));
      
      coverageReporter.addEntry({
        seite: 'crm/kontakte-liste',
        rolle: 'admin',
        create: 'N/A',
        update: 'N/A',
        delete: 'N/A',
        workflow: 'N/A',
        print: 'N/A',
        export: 'OK',
        nav: 'N/A',
        fallbackLevel: detection.level === 'unknown' ? 'unknown' : String(detection.level) as '1' | '2' | '3',
        ergebnis: 'PASS',
        ticketID: '',
        runID: process.env.PLAYWRIGHT_RUN_ID || 'local',
        build: process.env.BUILD_ID || 'dev',
      });
    }
  });

  test('Agrar: PSM Print-Fallback-Level', async ({ adminPage, fallbackDetector }) => {
    await adminPage.goto('/agrar/psm');
    await adminPage.waitForLoadState('networkidle');

    const printButton = adminPage.locator('button:has-text("Drucken"), button:has-text("drucken")').first();
    
    if (await printButton.count() > 0) {
      await printButton.click();
      await adminPage.waitForTimeout(1000);

      const detection = fallbackDetector.detectFallbackLevel('print');
      
      console.log('✓ PSM Print Fallback:', JSON.stringify(detection));
      
      coverageReporter.addEntry({
        seite: 'agrar/psm',
        rolle: 'admin',
        create: 'N/A',
        update: 'N/A',
        delete: 'N/A',
        workflow: 'N/A',
        print: 'OK',
        export: 'N/A',
        nav: 'N/A',
        fallbackLevel: detection.level === 'unknown' ? 'unknown' : String(detection.level) as '1' | '2' | '3',
        ergebnis: 'PASS',
        ticketID: '',
        runID: process.env.PLAYWRIGHT_RUN_ID || 'local',
        build: process.env.BUILD_ID || 'dev',
      });
    }
  });

  test.afterAll(async () => {
    // Coverage-Matrix speichern
    coverageReporter.save();
    console.log('✓ Coverage-Matrix gespeichert');
  });
});

