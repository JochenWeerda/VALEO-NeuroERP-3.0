import { Page } from '@playwright/test';

/**
 * Deterministische Alternative zu `waitForLoadState('networkidle')`
 * (E2E-SMOKE-REPAIR-001).
 *
 * Die Universal-Mask-Seiten halten dauerhaft Netzwerkverbindungen offen
 * (SSE-Reconnects, Polling) — `networkidle` tritt dort nie ein und laeuft
 * in CI immer in den 15s-Timeout. Stattdessen warten wir auf das DOM plus
 * ein sichtbares App-Shell-Signal (Ueberschrift oder Hauptbereich); die
 * Specs pruefen ihre Zielelemente danach ohnehin mit auto-waitenden Asserts.
 */
export async function waitForAppReady(page: Page, timeoutMs = 15000): Promise<void> {
  await page.waitForLoadState('domcontentloaded');
  await page
    .locator('h1, h2, main, [role="main"]')
    .first()
    .waitFor({ state: 'visible', timeout: timeoutMs });
}
