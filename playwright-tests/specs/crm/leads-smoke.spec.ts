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

  test('Lead-Detail lädt', async ({ adminPage }) => {
    await adminPage.goto('/crm/lead/test-1');
    await adminPage.waitForLoadState('networkidle');
    
    // Entweder Detail oder 404/Leer-State
    const hasContent = await adminPage.locator('h1, h2, [data-testid="empty-state"]').count() > 0;
    expect(hasContent).toBeTruthy();
  });
});

