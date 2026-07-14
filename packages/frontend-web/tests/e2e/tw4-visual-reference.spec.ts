import fs from 'node:fs'
import path from 'node:path'

import { test } from '@playwright/test'

import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * TW4-Visual-Referenz: Screenshots der prüfkritischen Masken für die manuelle
 * Sichtprüfung der Tailwind-4-Migration (Plan-Abschnitt E). Kein Diff-Gate —
 * erzeugt Referenzbilder unter test-results/tw4-visual/.
 */
const MASKS: { name: string; route: string }[] = [
  { name: 'rationsoptimierung', route: '/futtermittel/rationsoptimierung' },
  { name: 'feldbuch', route: '/portal/feldbuch' },
  { name: 'feldbuch-auswertungen', route: '/portal/feldbuch-auswertungen' },
  { name: 'crm', route: '/crm' },
  { name: 'finance-chart-of-accounts', route: '/finance/chart-of-accounts' },
  { name: 'auftrag', route: '/verkauf/betriebs-auftraege' },
]

test.describe('TW4 Visual-Referenz', () => {
  test.describe.configure({ timeout: 180_000 })

  test('Referenz-Screenshots prüfkritischer Masken', async ({ page }) => {
    const outDir = path.join(process.cwd(), 'test-results', 'tw4-visual')
    fs.mkdirSync(outDir, { recursive: true })
    for (const m of MASKS) {
      try {
        await page.goto(m.route, { waitUntil: 'domcontentloaded' })
        await waitForDashboardShell(page)
        await page.waitForTimeout(1200)
        await page.screenshot({ path: path.join(outDir, `${m.name}.png`), fullPage: false })
        // eslint-disable-next-line no-console
        console.log(`[tw4-visual] ${m.name} -> ok`)
      } catch (e) {
        // eslint-disable-next-line no-console
        console.log(`[tw4-visual] ${m.name} -> FEHLER ${(e as Error).message}`)
      }
    }
  })
})
