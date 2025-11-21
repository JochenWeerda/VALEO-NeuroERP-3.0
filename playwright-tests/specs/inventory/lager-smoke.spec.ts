/**
 * @smoke
 * Inventory Domain: Lager Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Inventory - Lager @smoke', () => {
  test('Lagerbewegungen lädt', async ({ adminPage }) => {
    await adminPage.goto('/lager/bewegungen');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Lagerbestand lädt', async ({ adminPage }) => {
    await adminPage.goto('/lager/bestand');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Inventory Route lädt', async ({ adminPage }) => {
    await adminPage.goto('/inventory');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

