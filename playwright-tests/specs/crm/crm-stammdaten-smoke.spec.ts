/**
 * @smoke
 * DOM-CRM-004: Kundenstamm-Tiefe (Dubletten / Zuordnung / Wiedervorlagen) — E2E.
 *
 * Prüft, dass die drei neuen CRM-Pflege-Seiten laden und ihren Kerninhalt zeigen.
 * Read-only-Smoke (keine Mutationen), gegen echte Seed-Daten.
 */

import { test, expect } from '../../fixtures/testSetup';
import type { Page } from '@playwright/test';

// Robust öffnen: Vite kompiliert die Route beim Erstaufruf (Spinner) → Reload-Retry.
async function open(page: Page, route: string, heading: string): Promise<void> {
  for (let attempt = 0; attempt < 3; attempt++) {
    await page.goto(route, { waitUntil: 'commit' });
    try {
      await expect(page.getByRole('heading', { name: heading })).toBeVisible({ timeout: 25000 });
      return;
    } catch {
      await page.reload({ waitUntil: 'commit' });
    }
  }
  await expect(page.getByRole('heading', { name: heading })).toBeVisible({ timeout: 30000 });
}

test.describe('CRM - Kundenstamm-Tiefe @smoke', () => {
  test.slow();

  test('Kunden-Dubletten lädt', async ({ adminPage }) => {
    await open(adminPage, '/crm/dubletten', 'Kunden-Dubletten');
    await expect(adminPage.getByText('Aktualisieren').first()).toBeVisible({ timeout: 30000 });
  });

  test('Kunden-Zuordnung lädt', async ({ adminPage }) => {
    await open(adminPage, '/crm/kunden-zuordnung', 'Kunden-Zuordnung');
    await expect(adminPage.getByText('Aktualisieren').first()).toBeVisible({ timeout: 30000 });
  });

  test('Wiedervorlagen lädt', async ({ adminPage }) => {
    await open(adminPage, '/crm/wiedervorlagen', 'Wiedervorlagen');
    await expect(adminPage.getByText('Aktualisieren').first()).toBeVisible({ timeout: 30000 });
  });
});
