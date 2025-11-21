/**
 * @smoke
 * Agrar Domain: Dünger Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Agrar - Dünger @smoke', () => {
  test('Dünger-Liste lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/duenger-liste');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Dünger-Stamm lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/duenger-stamm');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Bedarfsrechner lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/duenger/bedarfsrechner');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

