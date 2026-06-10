/**
 * @smoke
 * Agrar Domain: Saatgut Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Agrar - Saatgut @smoke', () => {
  test('Saatgut-Liste lädt', async ({ adminPage }) => {
    await adminPage.route('**/api/v1/agrar/saatgut?**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ items: [] }) });
    });
    await adminPage.goto('/agrar/saatgut-liste');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.getByText('Saatgut-Verwaltung', { exact: true })).toBeVisible({ timeout: 15000 });
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

