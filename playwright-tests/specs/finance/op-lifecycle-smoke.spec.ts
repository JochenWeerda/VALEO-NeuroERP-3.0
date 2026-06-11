/**
 * @smoke
 * DOM-FIN-004: FIBU-Tiefe (Mahnlauf / Zahlungseingang / Periodenabschluss / DATEV) — Smoke.
 *
 * Prüft, dass die FIBU-Arbeitsräume laden. Die fachliche Kette wird im Live-UAT
 * (scripts/uat/fin_op_lifecycle_uat.py) end-to-end geprüft.
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Finance - OP-Lebenszyklus @smoke', () => {
  test('Mahnlauf lädt', async ({ adminPage }) => {
    await adminPage.goto('/finance/mahnlauf');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'Mahnlauf' })).toBeVisible({ timeout: 15000 });
  });

  test('Zahlungseingang lädt', async ({ adminPage }) => {
    await adminPage.goto('/finance/zahlungseingang');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'Zahlungseingang / Auszifferung' })).toBeVisible({ timeout: 15000 });
  });

  test('Periodenabschluss lädt', async ({ adminPage }) => {
    await adminPage.goto('/finance/periodenabschluss');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'Periodenabschluss' })).toBeVisible({ timeout: 15000 });
  });

  test('DATEV-Export lädt', async ({ adminPage }) => {
    await adminPage.goto('/finance/datev-export');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'DATEV-Export' })).toBeVisible({ timeout: 15000 });
  });
});
