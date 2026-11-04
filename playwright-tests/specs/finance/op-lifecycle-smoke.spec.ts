/**
 * @smoke
 * DOM-FIN-004: FIBU-Tiefe (Mahnlauf / Zahlungseingang / Periodenabschluss / DATEV) — Smoke.
 *
 * Prüft, dass die FIBU-Arbeitsräume laden. Die fachliche Kette wird im Live-UAT
 * (scripts/uat/fin_op_lifecycle_uat.py) end-to-end geprüft.
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Finance - OP-Lebenszyklus @smoke', () => {
  test('Mahnlauf lädt', async ({ adminPage }) => {
    await adminPage.goto('/finance/mahnlauf');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Mahnlauf' })).toBeVisible({ timeout: 15000 });
  });

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): finance/zahlungseingang ist eine batch15-Platzhaltermaske; fixme bis zum Studio-Umbau.
  test.fixme('Zahlungseingang lädt', async ({ adminPage }) => {
    await adminPage.goto('/finance/zahlungseingang');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Zahlungseingang / Auszifferung' })).toBeVisible({ timeout: 15000 });
  });

  test('Periodenabschluss lädt', async ({ adminPage }) => {
    await adminPage.goto('/finance/periodenabschluss');
    await waitForAppReady(adminPage);
    // Seit Batch 1 (02.11.2026) zeigt /finance/periodenabschluss das Abschluss-Cockpit (fibu/abschluss-cockpit).
    await expect(adminPage.getByRole('heading', { name: 'Abschluss-Cockpit' })).toBeVisible({ timeout: 15000 });
  });

  test('DATEV-Export lädt', async ({ adminPage }) => {
    await adminPage.goto('/finance/datev-export');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'DATEV-Export' })).toBeVisible({ timeout: 15000 });
  });
});
