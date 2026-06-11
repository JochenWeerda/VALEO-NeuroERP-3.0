/**
 * @smoke
 * DOM-CON-004: Kontrakt-Tiefe (Fixierung / Engagement / Settlement) — Smoke.
 *
 * Prüft, dass die drei Arbeitsräume des Kontrakt-Lebenszyklus laden und ihre
 * Kopfzeile rendern. Die fachliche Kette wird im Live-UAT
 * (scripts/uat/con_contract_lifecycle_uat.py) end-to-end abgenommen.
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Agrar - Kontrakt-Lebenszyklus @smoke', () => {
  test('Fixierungs-Arbeitsraum lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/kontrakt-fixierung');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'Kontrakt-Fixierung' })).toBeVisible({ timeout: 15000 });
  });

  test('Engagement-Sicht lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/kontrakt-engagement');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'Kontrakt-Engagement' })).toBeVisible({ timeout: 15000 });
  });

  test('Settlement-Arbeitsraum lädt', async ({ adminPage }) => {
    await adminPage.goto('/agrar/kontrakt-settlement');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'Kontrakt-Settlement' })).toBeVisible({ timeout: 15000 });
  });
});
