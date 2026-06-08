/**
 * Browser-Verifikation der neuen Masken (KIM 360° + Wave 2/3 UX-Altschuld).
 * Läuft gegen den laufenden Dev-Server:
 *   PLAYWRIGHT_SKIP_WEBSERVER=1 FRONTEND_BASE_URL=http://localhost:3000 \
 *   E2E_AUTH_TOKEN=dev-token npx playwright test tests/e2e/kim-wave-verify.spec.ts --project=chromium
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

const MASKEN: Array<{ path: string; needle: RegExp }> = [
  { path: '/crm', needle: /Kunde im Mittelpunkt|KIM|Cockpit|Debitoren/i },
  { path: '/admin-suite/ki-anbieter', needle: /KI-Anbieter|NeuroAI|Anbieter/i },
  { path: '/kontrakte/mengenzeitraeume', needle: /Mengenzeiträume|Zu-\/Abschläge/i },
  { path: '/stammdaten/artikel-stoffstrom', needle: /Stoffstrom|THG/i },
  { path: '/fibu/op-skonto-auszifferung', needle: /Skonto-Auszifferung|Auszifferung/i },
  { path: '/lager/permanente-inventur', needle: /Permanente Inventur|PIV/i },
]

test.describe('Masken-Verifikation', () => {
  for (const { path, needle } of MASKEN) {
    test(`rendert ${path}`, async ({ page }) => {
      const consoleErrors: string[] = []
      page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()) })

      await prepareE2EAuth(page)
      await page.goto(path, { waitUntil: 'domcontentloaded' })
      await waitForDashboardShell(page)
      // Vite optimiert beim Erstaufruf Deps neu → ein Reload stabilisiert den Inhalt.
      await page.reload({ waitUntil: 'domcontentloaded' })
      await waitForDashboardShell(page)

      const body = await page.locator('body').innerText()
      // Kein React-Render-Crash (ErrorBoundary, DE + EN):
      expect(body, `ErrorBoundary auf ${path}`).not.toMatch(
        /Fehler beim Laden der Seite|konnte nicht gerendert werden|Something went wrong|Etwas ist schiefgelaufen|Unexpected Application Error/i,
      )
      expect(body, `Inhalt auf ${path}`).toMatch(needle)

      await page.screenshot({ path: `tests/e2e/__verify__/${path.replace(/\//g, '_') || 'root'}.png`, fullPage: true })
      const fatal = consoleErrors.filter((e) => !/favicon|manifest|404|Failed to load resource/i.test(e))
      // Konsolenfehler nur protokollieren (API-Leerzustände in DEV sind erwartbar).
      if (fatal.length) console.warn(`[${path}] console errors:`, fatal.slice(0, 5))
    })
  }
})
