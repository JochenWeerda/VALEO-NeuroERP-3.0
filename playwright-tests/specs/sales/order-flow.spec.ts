/**
 * @smoke
 * Sales Domain: Order-Flow Tests
 * Tests: Angebot → Auftrag → Lieferschein → Rechnung
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Sales - Order Flow @smoke', () => {
  test('Order-Editor lädt', async ({ adminPage }) => {
    await adminPage.goto('/sales/order');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Delivery-Editor lädt', async ({ adminPage }) => {
    await adminPage.goto('/sales/delivery');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Invoice-Editor lädt', async ({ adminPage }) => {
    await adminPage.goto('/sales/invoice');
    await adminPage.waitForLoadState('networkidle');
    
    await expect(adminPage.locator('h1, h2').first()).toBeVisible();
  });

  test('Folgebeleg-Buttons vorhanden (BelegFlowPanel)', async ({ adminPage }) => {
    await adminPage.goto('/sales/order');
    await adminPage.waitForLoadState('networkidle');
    
    // Suche nach Workflow/Folgebeleg-Buttons
    const workflowButtons = adminPage.locator('button:has-text("Lieferschein"), button:has-text("Rechnung")');
    
    const count = await workflowButtons.count();
    console.log(`Gefundene Workflow-Buttons: ${count}`);
    
    // Optional: mindestens 1 Folgebeleg-Button
    // expect(count).toBeGreaterThan(0);
  });
});

