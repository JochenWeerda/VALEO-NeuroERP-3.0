/**
 * @smoke
 * Agrar Domain: Dünger Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Agrar - Dünger @smoke', () => {
  test('Dünger-Liste lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/duenger-liste');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Dünger-Stamm lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/duenger-stamm');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Bedarfsrechner lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/duenger/bedarfsrechner');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

