/**
 * @smoke
 * DOM-SALES-004: O2C-Tiefe (Match / Kreditlimit / Storno) — Smoke.
 *
 * Prüft, dass die O2C-Arbeitsräume laden und ihre Kopfzeile rendern. Die fachliche
 * Kette wird im Live-UAT (scripts/uat/sales_o2c_lifecycle_uat.py) end-to-end geprüft.
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Sales - O2C-Lebenszyklus @smoke', () => {
  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): sales/auftrag-lieferschein-abgleich ist eine batch15-Platzhaltermaske; fixme bis zum Studio-Umbau.
  test.fixme('Auftrag-Lieferschein-Abgleich lädt', async ({ adminPage }) => {
    await adminPage.goto('/sales/auftrag-lieferschein-abgleich');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Auftrag-Lieferschein-Abgleich' })).toBeVisible({ timeout: 15000 });
  });

  test('Kreditlimit-Prüfung lädt', async ({ adminPage }) => {
    await adminPage.goto('/sales/kreditlimit-pruefung');
    await waitForAppReady(adminPage);
    // Studio-Maske sales/kreditlimit-pruefung, Titel "Kreditlimit-Pruefung".
    await expect(adminPage.getByRole('heading', { name: /Kreditlimit-Pr(ü|ue)fung/ })).toBeVisible({ timeout: 15000 });
  });

  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): sales/lieferung-storno ist eine batch15-Platzhaltermaske; fixme bis zum Studio-Umbau.
  test.fixme('Lieferung-Storno lädt', async ({ adminPage }) => {
    await adminPage.goto('/sales/lieferung-storno');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Lieferung-Storno / Gutschrift' })).toBeVisible({ timeout: 15000 });
  });
});
