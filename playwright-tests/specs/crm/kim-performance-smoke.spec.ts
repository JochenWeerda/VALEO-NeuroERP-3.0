/** Native navigation replaces the retired KIM cockpit; keep the opening budget. */
import { test, expect } from '../../fixtures/testSetup';

const OPEN_BUDGET_MS = 12000;

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
    await adminPage.goto('/crm/kim?id=PERF-K1&tab=chef', { waitUntil: 'domcontentloaded' });
    await expect(adminPage).toHaveURL(/\/crm\/kunden\/PERF-K1\?tab=chef$/);
    await expect(adminPage.getByRole('heading', { name: 'Kundenakte', exact: true })).toBeVisible();
    await expect(adminPage.getByText(/NotFound|Seite nicht gefunden/i)).toHaveCount(0);
  });
});
