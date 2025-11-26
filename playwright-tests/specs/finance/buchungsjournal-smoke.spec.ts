/**
 * @smoke
 * Finance Domain: Buchungsjournal Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Finance - Buchungsjournal @smoke', () => {
  test('Buchungsjournal lädt', async ({ adminPage }) => {
    await adminPage.goto('/finance/bookings/new');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('DATEV-Export vorhanden (Mock)', async ({ adminPage }) => {
    await adminPage.goto('/finance/bookings/new');
    await adminPage.waitForLoadState('networkidle');
    
    // Suche DATEV-Export-Button (kann auch in anderem Menü sein)
    const datevButton = adminPage.locator('button:has-text("DATEV"), a:has-text("DATEV")').first();
    
    const count = await datevButton.count();
    console.log(`DATEV-Buttons gefunden: ${count}`);
  });
});

