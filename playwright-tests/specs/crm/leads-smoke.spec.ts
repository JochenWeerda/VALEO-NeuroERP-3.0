/**
 * @smoke
 * CRM Domain: Leads Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('CRM - Leads @smoke', () => {
  test('Leads-Liste lädt', async ({ adminPage }) => {
    await adminPage.goto('/crm/leads');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Lead-Neuanlage lädt', async ({ adminPage }) => {
    await adminPage.goto('/crm/leads/new');
    await adminPage.waitForLoadState('networkidle');

    await expect(adminPage).toHaveURL(/\/crm\/lead\/(new|neu)$/);
    await expect(adminPage.locator('h1').first()).toContainText(/Lead/i, { timeout: 15000 });
    await expect(adminPage.getByLabel(/Firma/i)).toBeVisible();
    await expect(adminPage.getByLabel(/Ansprechpartner/i)).toBeVisible();
    await expect(adminPage.getByLabel(/Quelle/i)).toBeVisible();
  });
});

