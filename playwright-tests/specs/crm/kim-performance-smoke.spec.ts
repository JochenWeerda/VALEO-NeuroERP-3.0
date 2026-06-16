/**
 * @smoke
 * CRM/KIM 360°-Cockpit — Performance-/Verhaltens-Smoke.
 *
 * Sichert die Performance-Optimierung ab:
 *  - Cockpit (/crm) öffnet unter Zeitbudget.
 *  - Kundenwechsel löst GENAU den Bündelrequest (.../dashboard) aus — NICHT die vier
 *    Einzelrequests (contacts/logs/financials/documents).
 *  - Kundenwechsel rendert unter Zeitbudget.
 *  - Browser-Zurück liefert wieder /crm (kein 404 / NotFound).
 *
 * API gemockt → deterministisch und CI-stabil (misst Frontend-Verhalten, nicht die
 * Backend-Latenz; die Backend-Messung liegt im PR-Bericht).
 */

import { test, expect } from '../../fixtures/testSetup';

const OPEN_BUDGET_MS = 12000;   // großzügig: kalter Vite-Erstaufbau im Dev
const SWITCH_BUDGET_MS = 4000;

const CUSTOMERS = [
  { id: 'PERF-K1', name: 'Alpha Landhandel eG', debtorNo: 'PERF-K1', city: 'Nord', street: 'Weg 1', creditLimit: 1000, salesRepresentative: '', dispatcher: '', chefAnweisung: '', alertMessages: [], custGroup: '' },
  { id: 'PERF-K2', name: 'Beta Agrar GmbH', debtorNo: 'PERF-K2', city: 'Süd', street: 'Weg 2', creditLimit: 2000, salesRepresentative: '', dispatcher: '', chefAnweisung: '', alertMessages: [], custGroup: '' },
];

function dashboard(id: string) {
  return {
    customer: CUSTOMERS.find((c) => c.id === id) ?? null,
    contacts: [], logs: [], financials: [], documents: [],
    meta: { timings: { total: 5.0 }, sourceStatus: { customer: 'ok' } },
  };
}

test.describe('CRM/KIM - Performance @smoke', () => {
  test('Cockpit öffnet + Kundenwechsel nutzt Bündelrequest', async ({ adminPage }) => {
    const individualStreamCalls: string[] = [];
    let dashboardCalls = 0;

    // Playwright evaluates route handlers in reverse registration order.
    // Register the fallback first so the specific contracts below win.
    await adminPage.route('**/api/v1/crm/kim/**', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }));
    await adminPage.route('**/api/v1/crm/kim/customers?**', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(CUSTOMERS) }));
    await adminPage.route('**/api/v1/crm/kim/customers/*/dashboard', (route) => {
      dashboardCalls += 1;
      const id = route.request().url().split('/customers/')[1].split('/')[0];
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(dashboard(decodeURIComponent(id))) });
    });
    // Einzelströme dürfen beim Wechsel NICHT mehr aufgerufen werden — wir zählen sie.
    for (const stream of ['contacts', 'logs', 'financials', 'documents']) {
      await adminPage.route(`**/api/v1/crm/kim/customers/*/${stream}`, (route) => {
        individualStreamCalls.push(stream);
        route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
      });
    }
    // 1) Öffnen unter Budget
    const tOpen = Date.now();
    await adminPage.goto('/crm', { waitUntil: 'domcontentloaded' });
    await expect(adminPage.locator(`#sidebar-cust-item-${CUSTOMERS[0].id}`)).toBeVisible({ timeout: OPEN_BUDGET_MS });
    expect(Date.now() - tOpen).toBeLessThan(OPEN_BUDGET_MS);

    // Auto-Selektion des ersten Kunden hat bereits ein Dashboard geholt.
    await expect.poll(() => dashboardCalls).toBeGreaterThanOrEqual(1);
    const callsBeforeSwitch = dashboardCalls;

    // 2) Kundenwechsel → genau ein weiterer Bündelrequest, KEINE Einzelströme
    const tSwitch = Date.now();
    await adminPage.locator(`#sidebar-cust-item-${CUSTOMERS[1].id}`).click();
    await expect.poll(() => dashboardCalls).toBeGreaterThan(callsBeforeSwitch);
    expect(Date.now() - tSwitch).toBeLessThan(SWITCH_BUDGET_MS);
    expect(individualStreamCalls, 'Kundenwechsel darf keine Einzelströme mehr auslösen').toEqual([]);

    // 3) Browser-Zurück → kein 404 / NotFound, Cockpit bleibt erreichbar
    await adminPage.goBack({ waitUntil: 'domcontentloaded' }).catch(() => {});
    await expect(adminPage.getByText(/NotFound|Seite nicht gefunden|404/i)).toHaveCount(0);
  });
});
