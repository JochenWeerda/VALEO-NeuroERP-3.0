/**
 * @smoke
 * Inventory Domain: Lager Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Inventory - Lager @smoke', () => {
  test('Lagerbewegungen lädt', async ({ adminPage }) => {
    // /lager/bewegungen gab es nie; die Seite heisst /lager/lagerbewegungen (Studio-Liste lager/lagerbewegungen-liste).
    await adminPage.goto('/lager/lagerbewegungen');
    await waitForAppReady(adminPage);

    await expect(adminPage.getByRole('heading', { name: 'Lagerbewegungen' })).toBeVisible({ timeout: 15000 });
  });

  test('Lagerbestand lädt', async ({ adminPage }) => {
    // /lager/bestand gab es nie; die Bestandsuebersicht ist seit Batch 2 (03.11.2026) eine Studio-Liste.
    await adminPage.goto('/lager/bestandsuebersicht');
    await waitForAppReady(adminPage);

    await expect(adminPage.getByRole('heading', { name: 'Bestandsübersicht' })).toBeVisible({ timeout: 15000 });
  });

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): Seite rendert inventory/adjust, die Maske fehlt; fixme bis zum Studio-Umbau.
  test.fixme('Inventory Route lädt', async ({ adminPage }) => {
    await adminPage.goto('/inventory');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

