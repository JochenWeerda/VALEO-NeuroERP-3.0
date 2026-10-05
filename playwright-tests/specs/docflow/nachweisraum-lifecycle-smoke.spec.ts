/**
 * @smoke
 * DOM-DOC-004: Nachweisraum-Tiefe (Artefakt / Wiedervorlage / GoBD) — Smoke.
 *
 * Prüft, dass die GoBD-Nachweisraum-Arbeitsräume laden. Die fachliche Kette wird im
 * Live-UAT (scripts/uat/doc_nachweisraum_lifecycle_uat.py) end-to-end geprüft.
 */

import { test, expect } from '../../fixtures/testSetup';
import { waitForAppReady } from '../../helpers/ui';

test.describe('Docflow - Nachweisraum-Lebenszyklus @smoke', () => {
  test('Artefakt-Upload & Freigabe lädt', async ({ adminPage }) => {
    await adminPage.goto('/docflow/artefakt-freigabe');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Artefakt-Upload & Freigabe' })).toBeVisible({ timeout: 15000 });
  });

  test('Wiedervorlagen & Bescheide lädt', async ({ adminPage }) => {
    await adminPage.goto('/docflow/wiedervorlagen');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'Wiedervorlagen & Bescheide' })).toBeVisible({ timeout: 15000 });
  });

  test('GoBD-Export lädt', async ({ adminPage }) => {
    await adminPage.goto('/docflow/gobd-export');
    await waitForAppReady(adminPage);
    await expect(adminPage.getByRole('heading', { name: 'GoBD-Export' })).toBeVisible({ timeout: 15000 });
  });
});
