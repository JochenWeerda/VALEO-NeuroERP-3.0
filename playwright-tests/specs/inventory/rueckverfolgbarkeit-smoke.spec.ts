/**
 * @smoke
 * DOM-SUPPLY-004: Rückverfolgbarkeit (durchgängige Lieferkette) — E2E-Abnahme.
 *
 * Prüft die durchgängige Kette Wiegung→Annahme→Lager→Abrechnung an den
 * Seed-Daten (Wiegeschein WG-2026-00001): Picker, Genealogie-Timeline,
 * kanonischer Status und Ereignis-Log werden gerendert.
 */

import { test, expect } from '../../fixtures/testSetup';
import type { Page } from '@playwright/test';

const ROUTE = '/lager/rueckverfolgbarkeit';

// Öffnet die Route robust: beim Erstaufruf optimiert Vite die Lazy-Chunk (Spinner),
// was länger dauern kann → Reload-Retry, bis der Picker sichtbar ist.
async function openTrace(page: Page): Promise<void> {
  for (let attempt = 0; attempt < 3; attempt++) {
    await page.goto(ROUTE, { waitUntil: 'commit' });
    try {
      await expect(page.getByPlaceholder('Nr. suchen…')).toBeVisible({ timeout: 25000 });
      return;
    } catch {
      await page.reload({ waitUntil: 'commit' });
    }
  }
  await expect(page.getByPlaceholder('Nr. suchen…')).toBeVisible({ timeout: 30000 });
}

test.describe('Inventory - Rückverfolgbarkeit @smoke', () => {
  test.slow(); // Vite-Erstkompilierung der Route kann den Default-Timeout sprengen.

  test('Seite lädt mit Picker', async ({ adminPage }) => {
    await openTrace(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Rückverfolgbarkeit' })).toBeVisible();
  });

  test('Kette eines Seed-Wiegescheins wird angezeigt', async ({ adminPage }) => {
    await adminPage.route('**/api/v1/supply-chain/traceability/tickets**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [{
            ticket_id: 'ticket-1',
            ticket_nr: 'WG-2026-00001',
            datum: '2026-06-10T08:00:00Z',
            menge_kg: 25000,
            status: 'abgerechnet',
            allokation: 'LOT-1',
            hat_annahme: true,
            hat_lager: true,
            hat_abrechnung: true,
            vollstaendig: true,
          }],
        }),
      });
    });
    await adminPage.route('**/api/v1/supply-chain/traceability/sync**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{"synced":4,"total":4}' });
    });
    await adminPage.route('**/api/v1/supply-chain/traceability?**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          found: true,
          ticket_id: 'ticket-1',
          ticket_nr: 'WG-2026-00001',
          kette: [
            { stage: 'wiegung', label: 'Wiegung', ref: 'WG-2026-00001', ref_id: 'ticket-1', status: 'erfasst', menge_kg: 25000, zeitpunkt: '2026-06-10T08:00:00Z', facts: {} },
            { stage: 'annahme', label: 'Annahme', ref: 'AN-1', ref_id: 'inbound-1', status: 'freigegeben', menge_kg: 25000, zeitpunkt: '2026-06-10T08:10:00Z', facts: {} },
            { stage: 'lager', label: 'Lager', ref: 'LOT-1', ref_id: 'lot-1', status: 'eingelagert', menge_kg: 25000, zeitpunkt: '2026-06-10T08:20:00Z', facts: {} },
            { stage: 'abrechnung', label: 'Abrechnung', ref: 'INV-1', ref_id: 'invoice-1', status: 'abgerechnet', menge_kg: 25000, zeitpunkt: '2026-06-10T09:00:00Z', facts: {} },
          ],
          mengen_konsistenz: [],
          luecken: [],
          ereignisse: [{
            id: 'event-1', ticket_id: 'ticket-1', stage: 'wiegung', ref_type: 'ticket',
            ref_id: 'ticket-1', ref_label: 'WG-2026-00001', event_type: 'erfasst',
            status_from: null, status_to: 'erfasst', menge_kg: 25000,
            abweichung_grund: null, bediener: 'CI', source: 'backfill',
            occurred_at: '2026-06-10T08:00:00Z', created_at: '2026-06-10T08:00:00Z',
          }],
          kanon_status: { status: 'abgerechnet', rang: 4 },
          summary: {
            stufen: 4,
            vollstaendig: true,
            hat_mengen_abweichung: false,
            offene_luecken: 0,
            status: 'abgerechnet',
          },
        }),
      });
    });
    await openTrace(adminPage);

    // Auf die geladene Liste warten (kalter Erstaufruf kann dauern), dann filtern.
    await expect(adminPage.getByText('Lädt …')).toBeHidden({ timeout: 45000 });
    await adminPage.getByPlaceholder('Nr. suchen…').fill('WG-2026-00001');
    const ticketButton = adminPage.getByRole('button', { name: /WG-2026-00001/ });
    await expect(ticketButton.first()).toBeVisible({ timeout: 20000 });
    await ticketButton.first().click();

    await expect(adminPage.getByText('Wiegung', { exact: false }).first()).toBeVisible({ timeout: 15000 });
    await expect(adminPage.getByText(/Status:/).first()).toBeVisible({ timeout: 15000 });
    await expect(adminPage.getByText('Ereignis-Log')).toBeVisible({ timeout: 15000 });
  });
});
