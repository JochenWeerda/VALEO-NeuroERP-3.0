import fs from 'node:fs'
import path from 'node:path'

import { expect, test } from '@playwright/test'

import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * Verifiziert nach der Token-Konsolidierung (primitives/semantic/themes), dass die
 * Theme-Kaskade deterministisch greift: setzt data-theme='terra' am <html> und prüft,
 * dass das semantische --background (var(--color-gray-50)) auf die TERRA-Palette
 * umschaltet (Warm-Grau 40 15% 96%) statt Meridian (210 20% 98%).
 */
test.describe('TW4 Terra-Theme (Token-Split)', () => {
  test('data-theme=terra schaltet semantische Tokens auf Terra-Palette', async ({ page }) => {
    await page.goto('/crm', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    const read = () =>
      page.evaluate(() => {
        const cs = getComputedStyle(document.documentElement)
        return {
          theme: document.documentElement.dataset.theme || '(none)',
          background: cs.getPropertyValue('--background').trim(),
          muted: cs.getPropertyValue('--muted').trim(),
          primary: cs.getPropertyValue('--primary').trim(),
        }
      })

    const def = await read()
    // eslint-disable-next-line no-console
    console.log(`[terra] default=${JSON.stringify(def)}`)
    // Default (Meridian): Off-White 210 20% 98%, Ozeanblau 215 85% 42%.
    expect(def.background.replace(/\s+/g, ' ')).toContain('210 20% 98%')
    expect(def.primary.replace(/\s+/g, ' ')).toContain('215 85% 42%')

    await page.evaluate(() => {
      document.documentElement.dataset.theme = 'terra'
    })
    await page.waitForTimeout(300)
    const terra = await read()
    // eslint-disable-next-line no-console
    console.log(`[terra] terra=${JSON.stringify(terra)}`)
    // Terra aktiv: die Theme-Kaskade (:root[data-theme="terra"], 0,2,0) greift vollstaendig.
    // Nach Behebung der --color-gray-*/Tailwind-Kollision (Palette -> --palette-gray-*)
    // schaltet auch --background auf die Terra-Palette (Warm-Grau 40 15% 96%) statt auf
    // Tailwinds oklch; --primary = Waldgruen 158 64% 28%.
    expect(terra.background.replace(/\s+/g, ' ')).toContain('40 15% 96%')
    expect(terra.primary.replace(/\s+/g, ' ')).toContain('158 64% 28%')

    const outDir = path.join(process.cwd(), 'test-results', 'tw4-visual')
    fs.mkdirSync(outDir, { recursive: true })
    await page.screenshot({ path: path.join(outDir, 'crm-terra.png'), fullPage: false })
  })
})
