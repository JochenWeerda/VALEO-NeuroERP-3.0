/**
 * @smoke
 * Agrar Domain: Saatgut Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Agrar - Saatgut @smoke', () => {
  test('Saatgut-Liste lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/saatgut-liste');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Saatgut-Stamm lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/saatgut-stamm');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Sortenregister lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/saatgut/sortenregister');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

