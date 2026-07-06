/**
 * @smoke
 * Finance Domain: Debitoren/OP Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Finance - Debitoren @smoke', () => {
  test('Debitoren-Liste lädt', async ({ adminPage }) => {
    await adminPage.goto('/fibu/debitoren');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Offene Posten lädt', async ({ adminPage }) => {
    await adminPage.goto('/fibu/offene-posten');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('OP-Verwaltung lädt', async ({ adminPage }) => {
    await adminPage.goto('/fibu/op-verwaltung');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });
});

