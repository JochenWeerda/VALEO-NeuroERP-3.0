/**
 * UIX-074: VoiceBar-Integration in der Omnibox.
 * Der STT-Provider ist ein Browser-Stub; Audio wird nicht verwendet.
 */
import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

test('VoiceBar uebernimmt editierbares Transkript erst bei Commit und navigiert read-only', async ({ page }) => {
  await page.addInitScript(() => {
    const provider = {
      id: 'webspeech',
      partial: undefined as undefined | ((text: string) => void),
      final: undefined as undefined | ((text: string, confidence?: number) => void),
      error: undefined as undefined | ((err: { code: string; message: string }) => void),
      isAvailable() { return true },
      start() {
        window.setTimeout(() => {
          this.partial?.('zeige offene posten')
          this.final?.('zeige offene posten debitoren folkerts', 0.96)
        }, 25)
      },
      stop() {},
      onPartial(cb: (text: string) => void) { this.partial = cb },
      onFinal(cb: (text: string, confidence?: number) => void) { this.final = cb },
      onError(cb: (err: { code: string; message: string }) => void) { this.error = cb },
    }
    window.__VALEO_STT_PROVIDER__ = provider
  })

  await page.goto('/', { waitUntil: 'domcontentloaded' })
  await waitForDashboardShell(page)
  await page.getByRole('button', { name: /Suche/ }).click()

  await page.getByTestId('voice-ptt').click()
  const transcript = page.getByTestId('voice-transcript')
  await expect(transcript).toHaveValue('zeige offene posten debitoren folkerts')

  await transcript.fill('zeige offene posten debitoren folkerts')
  await page.getByTestId('voice-commit').click()

  await expect(page).toHaveURL(/\/finance\/op-debitoren\?.*q=folkerts/)
})
