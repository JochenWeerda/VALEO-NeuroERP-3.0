/**
 * @smoke
 * DOM-CON-004: Kontrakt-Tiefe (Fixierung / Engagement / Settlement) — Smoke.
 *
 * Prüft, dass die drei Arbeitsräume des Kontrakt-Lebenszyklus laden und ihre
 * Kopfzeile rendern. Seit 08.11.2026 sind es Varianten der Studio-Familie
 * kontrakt-liste (Fixierung, Engagement je Artikel, Abrechnung). Die fachliche Kette wird im Live-UAT
 * (scripts/uat/con_contract_lifecycle_uat.py) end-to-end abgenommen.
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Agrar - Kontrakt-Lebenszyklus @smoke', () => {
  test('Fixierungs-Arbeitsraum lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/kontrakt-fixierung');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Fixierung', level: 1 })).toBeVisible({ timeout: 15000 });
  });

  test('Engagement-Sicht lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/kontrakt-engagement');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Engagement je Artikel', level: 1 })).toBeVisible({ timeout: 15000 });
  });

  test('Settlement-Arbeitsraum lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/kontrakt-settlement');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Abrechnung', level: 1 })).toBeVisible({ timeout: 15000 });
  });
});
