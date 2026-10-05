/**
 * @smoke
 * CRM Domain: Leads Smoke-Tests
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('CRM - Leads @smoke', () => {
  test('Leads-Liste lädt', async ({ adminPage }) => {
    await adminPage.goto('/crm/leads');
    await waitForAppReady(adminPage);
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Lead-Neuanlage lädt', async ({ adminPage }) => {
    await adminPage.goto('/crm/leads/new');
    await waitForAppReady(adminPage);

    await expect(adminPage).toHaveURL(/\/crm\/lead\/(new|neu)$/);
    await expect(adminPage.locator('h1').first()).toContainText(/Lead/i, { timeout: 15000 });
    // Feldlabels der nativen Lead-Maske (ScreenDefinition crm/lead, UIX-Rollout):
    // "Firma" aus dem Alt-Formular heisst dort "Unternehmen".
    await expect(adminPage.getByLabel(/Unternehmen/i).first()).toBeVisible();
    await expect(adminPage.getByLabel(/Ansprechpartner/i).first()).toBeVisible();
    await expect(adminPage.getByLabel(/Quelle/i).first()).toBeVisible();
  });
});

