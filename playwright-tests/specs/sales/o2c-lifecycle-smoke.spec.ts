/**
 * @smoke
 * DOM-SALES-004: O2C-Tiefe (Match / Kreditlimit / Storno) — Smoke.
 *
 * Prüft, dass die O2C-Arbeitsräume laden und ihre Kopfzeile rendern. Die fachliche
 * Kette wird im Live-UAT (scripts/uat/sales_o2c_lifecycle_uat.py) end-to-end geprüft.
 */

import { test, expect } from '../../fixtures/testSetup';

test.describe('Sales - O2C-Lebenszyklus @smoke', () => {
  test('Auftrag-Lieferschein-Abgleich lädt', async ({ adminPage }) => {
    await adminPage.goto('/sales/auftrag-lieferschein-abgleich');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'Auftrag-Lieferschein-Abgleich' })).toBeVisible({ timeout: 15000 });
  });

  test('Kreditlimit-Prüfung lädt', async ({ adminPage }) => {
    await adminPage.goto('/sales/kreditlimit-pruefung');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'Kreditlimit-Prüfung' })).toBeVisible({ timeout: 15000 });
  });

  test('Lieferung-Storno lädt', async ({ adminPage }) => {
    await adminPage.goto('/sales/lieferung-storno');
    await adminPage.waitForLoadState('networkidle');
    await expect(adminPage.getByRole('heading', { name: 'Lieferung-Storno / Gutschrift' })).toBeVisible({ timeout: 15000 });
  });
});
