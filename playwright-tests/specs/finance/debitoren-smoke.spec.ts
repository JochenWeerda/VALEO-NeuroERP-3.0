/**
 * @smoke
 * Finance Domain: Debitoren/OP Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Finance - Debitoren @smoke', () => {
  test('Debitoren-Liste lädt', async ({ adminPage }) => {
    await adminPage.goto('/fibu/debitoren');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Offene Posten lädt', async ({ adminPage }) => {
    await adminPage.goto('/fibu/offene-posten');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('OP-Verwaltung lädt', async ({ adminPage }) => {
    await adminPage.goto('/fibu/op-verwaltung');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

