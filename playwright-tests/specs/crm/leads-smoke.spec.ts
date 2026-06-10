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
    await adminPage.goto('/crm/lead/new');
    await adminPage.waitForLoadState('networkidle');

    await expect(adminPage.getByText(/Neuen Lead anlegen|Lead bearbeiten/).first()).toBeVisible();
  });
});

