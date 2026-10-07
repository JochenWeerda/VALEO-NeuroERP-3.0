/** Native navigation replaces the retired KIM cockpit; keep the opening budget. */
import { test, expect } from '../../fixtures/testSetup';

const OPEN_BUDGET_MS = 12000;
const CUSTOMER_ID = '00000000-0000-4000-8000-000000000071';

test.describe('CRM/KIM - Native Weiterleitung @smoke', () => {
  test('Cockpit ohne Kundenkennung leitet unter Budget zur Kundenliste', async ({ adminPage }) => {
    const started = Date.now();
    await adminPage.goto('/crm', { waitUntil: 'domcontentloaded' });
    await expect(adminPage).toHaveURL(/\/verkauf\/kunden-liste$/, { timeout: OPEN_BUDGET_MS });
    await expect(adminPage.getByRole('heading', { name: /Kunden/i }).first()).toBeVisible();
    expect(Date.now() - started).toBeLessThan(OPEN_BUDGET_MS);
    await expect(adminPage.getByText(/NotFound|Seite nicht gefunden/i)).toHaveCount(0);
  });

  test('KIM-Deep-Link bewahrt Kundenkennung und Registerwahl', async ({ adminPage }) => {
    // Navigation smoke: a deterministic read fixture, not a persisted customer.
    // Keep the real ScreenDefinition and native renderer; only this entity is supplied.
    await adminPage.route(`**/api/v1/crm/customers/${CUSTOMER_ID}`, route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: CUSTOMER_ID, kunden_nr: 'SMOKE-K1', firma: 'KIM Smoke Kunde' }),
    }));
    await adminPage.goto(`/crm/kim?id=${CUSTOMER_ID}&tab=chef`, { waitUntil: 'domcontentloaded' });
    await expect(adminPage).toHaveURL(new RegExp(`/crm/kunden/${CUSTOMER_ID}\\?tab=chef$`));
    const nativeMask = adminPage.getByTestId('crm-customer-360');
    await expect(nativeMask).toBeVisible();
    await expect(nativeMask.getByLabel('Firma / Name', { exact: true })).toHaveValue('KIM Smoke Kunde');
    await expect(nativeMask.getByTestId('section-anchor-masterdata')).toHaveAttribute('aria-current', 'location');
    await expect(adminPage.getByText(/NotFound|Seite nicht gefunden/i)).toHaveCount(0);
    await expect(adminPage.getByText(/Datensatz nicht gefunden|Fehler beim Laden/i)).toHaveCount(0);
  });

  test('KIM-Deep-Link auf fehlenden Kunden zeigt den Fehlerzustand', async ({ adminPage }) => {
    await adminPage.route(`**/api/v1/crm/customers/${CUSTOMER_ID}`, route => route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Customer not found' }),
    }));
    await adminPage.goto(`/crm/kim?id=${CUSTOMER_ID}&tab=chef`, { waitUntil: 'domcontentloaded' });
    await expect(adminPage).toHaveURL(new RegExp(`/crm/kunden/${CUSTOMER_ID}\\?tab=chef$`));
    await expect(adminPage.getByText('Datensatz nicht gefunden', { exact: true })).toBeVisible();
    await expect(adminPage.getByTestId('crm-customer-360')).toHaveCount(0);
  });
});
