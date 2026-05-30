/**
 * E2E Smoke für Slice-015: WhisperBar Summary (gemockt, kein Mikrofon).
 */
import { test, expect } from '@playwright/test'

const MOCK_SUMMARY = 'Kurze Zusammenfassung des Clipboard-Texts.'
const MOCK_CLIPBOARD = 'Langer Beispieltext aus der Zwischenablage fuer den Summary-Modus.'

test.beforeEach(async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write'])
  await page.addInitScript((clipboardText: string) => {
    window.localStorage.setItem('dev_bypass_auth', 'true')
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        readText: async () => clipboardText,
        writeText: async () => undefined,
      },
    })
  }, MOCK_CLIPBOARD)

  await page.route('**/api/ki-usability/api/v1/voice/pipeline', async (route) => {
    if (route.request().method() !== 'POST') {
      await route.continue()
      return
    }
    const body = route.request().postDataJSON() as { mode?: string }
    if (body?.mode === 'summary') {
      await route.fulfill({
        json: {
          mode: 'summary',
          source_text: MOCK_CLIPBOARD,
          summary_text: MOCK_SUMMARY,
          provider: 'ollama:mistral',
          summary_applied: true,
          estimated_seconds: 3,
        },
      })
      return
    }
    await route.continue()
  })
})

test.describe('WhisperBar Voice Summary (Slice-015)', () => {
  test('Summary-Shortcut zeigt Feedback und Copilot-Banner', async ({ page }) => {
    await page.goto('/')

    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('whisperbar-summary-clipboard'))
    })

    await expect(page.getByTestId('voice-feedback-summary')).toBeVisible({ timeout: 10_000 })
    await expect(page.getByTestId('voice-feedback-summary')).toContainText(MOCK_SUMMARY)

    await page.getByRole('button', { name: 'Copilot Chat oeffnen' }).click()
    await expect(page.getByTestId('copilot-voice-summary')).toBeVisible()
    await expect(page.getByTestId('copilot-voice-summary')).toContainText(MOCK_SUMMARY)
  })

  test('GET /voice/status liefert Readiness (gemockt)', async ({ page }) => {
    await page.route('**/api/ki-usability/api/v1/voice/status', async (route) => {
      await route.fulfill({
        json: {
          stt_provider: 'faster-whisper',
          stt_ready: true,
          tts_provider: 'piper',
          tts_ready: false,
          ollama_base_url: 'http://localhost:11434',
          ollama_reachable: true,
          voice_polish_enabled: true,
          voice_summary_enabled: true,
          kokoro_configured: false,
          piper_configured: false,
          faster_whisper_model: 'small',
        },
      })
    })

    const status = await page.evaluate(async () => {
      const res = await fetch('/api/ki-usability/api/v1/voice/status')
      return res.json() as Promise<Record<string, unknown>>
    })

    expect(status.stt_ready).toBe(true)
    expect(status.ollama_reachable).toBe(true)
  })
})
