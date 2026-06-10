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
