/**
 * @smoke
 * Inventory Domain: Lager Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Inventory - Lager @smoke', () => {
  test('Lagerbewegungen lädt', async ({ adminPage }) => {
    // /lager/bewegungen gab es nie; die Seite heisst /lager/lagerbewegungen (Maske lager/umlagerung).
    await adminPage.goto('/lager/lagerbewegungen');
    await waitForAppReady(adminPage);

    await expect(adminPage.getByRole('heading', { name: 'Lagerbewegungen' })).toBeVisible({ timeout: 15000 });
  });

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): lager/bestandsuebersicht hat keine Maske; fixme bis zum Studio-Umbau.
  test.fixme('Lagerbestand lädt', async ({ adminPage }) => {
    await adminPage.goto('/lager/bestand');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): Seite rendert inventory/adjust, die Maske fehlt; fixme bis zum Studio-Umbau.
  test.fixme('Inventory Route lädt', async ({ adminPage }) => {
    await adminPage.goto('/inventory');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

