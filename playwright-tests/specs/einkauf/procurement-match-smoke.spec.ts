/**
 * @smoke
 * DOM-PROC-004: Beschaffungs-Match (Wareneingangs-Abgleich) — Smoke.
 *
 * Prüft, dass der 3-Wege-Match-Arbeitsraum lädt. Die fachliche Kette wird im
 * Live-UAT (scripts/uat/proc_match_lifecycle_uat.py) end-to-end abgenommen.
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Einkauf - Beschaffungs-Match @smoke', () => {
  test('Wareneingangs-Abgleich lädt', async ({ adminPage }) => {
    await adminPage.goto('/einkauf/wareneingangsabgleich');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Wareneingangs-Abgleich' })).toBeVisible({ timeout: 15000 });
  });
});
