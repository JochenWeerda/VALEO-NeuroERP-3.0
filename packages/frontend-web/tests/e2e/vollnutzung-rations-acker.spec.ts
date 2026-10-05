import fs from 'node:fs'
import path from 'node:path'

import { expect, test, type Page } from '@playwright/test'

import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

/**
 * Vollnutzungs-Simulation: ein User nutzt Rationsoptimierung UND Ackerschlagkartei
 * vollumfaenglich durch echtes Klicken. Protokolliert Seitenladezeiten und alle
 * Konsolen-/Netzwerk-/Page-Fehler in ein JSON-Protokoll.
 *
 * Voraussetzung: Backend erreichbar (Docker-Stack :8000 oder lokal). Frontend via
 * Playwright-webServer (Vite) oder extern (PLAYWRIGHT_SKIP_WEBSERVER=1 + FRONTEND_BASE_URL).
 */

type ConsoleErr = { type: string; text: string; url: string }
type NetErr = { status: number; method: string; url: string }
type PageTiming = { page: string; url: string; navMs: number; domContentLoadedMs: number; loadEventMs: number; ok: boolean; note?: string }

const PROTOCOL: {
  startedAt: string
  timings: PageTiming[]
  consoleErrors: ConsoleErr[]
  networkErrors: NetErr[]
  pageErrors: string[]
  steps: { step: string; ok: boolean; detail?: string }[]
} = {
  startedAt: new Date().toISOString(),
  timings: [],
  consoleErrors: [],
  networkErrors: [],
  pageErrors: [],
  steps: [],
}

function attachCollectors(page: Page) {
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      const text = msg.text()
      // Ignoriere Favicon/DevTools-Rauschen
      if (/favicon|Download the React DevTools/i.test(text)) return
      PROTOCOL.consoleErrors.push({ type: msg.type(), text, url: page.url() })
    }
  })
  page.on('pageerror', (err) => {
    PROTOCOL.pageErrors.push(`${err.name}: ${err.message}`)
  })
  page.on('response', (res) => {
    const status = res.status()
    const url = res.url()
    if (status >= 400 && url.includes('/api/')) {
      PROTOCOL.networkErrors.push({ status, method: res.request().method(), url })
    }
  })
}

async function measure(page: Page, label: string, route: string): Promise<PageTiming> {
  const t0 = Date.now()
  let ok = true
  let note: string | undefined
  try {
    await page.goto(route, { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)
  } catch (e) {
    ok = false
    note = (e as Error).message
  }
  const navMs = Date.now() - t0
  const timing = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined
    return {
      domContentLoadedMs: nav ? Math.round(nav.domContentLoadedEventEnd - nav.startTime) : -1,
      loadEventMs: nav ? Math.round(nav.loadEventEnd - nav.startTime) : -1,
    }
  })
  const rec: PageTiming = { page: label, url: route, navMs, ...timing, ok, note }
  PROTOCOL.timings.push(rec)
  return rec
}

function logStep(step: string, ok: boolean, detail?: string) {
  PROTOCOL.steps.push({ step, ok, detail })
}

test.describe('Vollnutzung Rationsoptimierung + Ackerschlagkartei', () => {
  test.describe.configure({ timeout: 300_000 })

  test.beforeAll(() => {
    const backendBase = process.env.E2E_BACKEND_URL ?? 'http://127.0.0.1:8000'
    // eslint-disable-next-line no-console
    console.log(`[Simulation] Backend erwartet unter ${backendBase}`)
  })

  test('durchklicken beide Tools und protokolliere Ladezeiten/Fehler', async ({ page }) => {
    attachCollectors(page)

    // ── 1) Rationsoptimierung ────────────────────────────────────────────
    const rations = await measure(page, 'Rationsoptimierung (Landing)', '/futtermittel/rationsoptimierung')
    logStep('Rations Landing geladen', rations.ok, `${rations.navMs} ms`)

    // Demo starten (loest LP-Optimierung im Backend aus)
    try {
      const demoBtn = page.getByRole('button', { name: /Demo starten/i }).first()
      await demoBtn.waitFor({ state: 'visible', timeout: 30_000 })
      await Promise.all([
        page.waitForResponse(
          (r) => r.url().includes('/rations-optimization/optimize/demo') && r.request().method() === 'POST',
          { timeout: 120_000 },
        ),
        demoBtn.click(),
      ])
      await expect(page.locator('#feed-table')).toBeVisible({ timeout: 60_000 })
      logStep('Rations Demo-Optimierung + Futtermitteltabelle', true)
    } catch (e) {
      logStep('Rations Demo-Optimierung + Futtermitteltabelle', false, (e as Error).message)
    }

    // KPI-Leiste sichtbar
    try {
      await expect(page.locator('#kpi-bar')).toBeVisible({ timeout: 15_000 })
      logStep('Rations KPI-Leiste sichtbar', true)
    } catch (e) {
      logStep('Rations KPI-Leiste sichtbar', false, (e as Error).message)
    }

    // DLG-Panel (Ampel-Indikatoren)
    try {
      await expect(page.locator('#dlg-panel')).toBeVisible({ timeout: 15_000 })
      logStep('Rations DLG-Panel sichtbar', true)
    } catch (e) {
      logStep('Rations DLG-Panel sichtbar', false, (e as Error).message)
    }

    // AI-Copilot vorhanden (AI-Agent-Bedienbarkeit)
    try {
      const copilot = page.locator('#ai-copilot')
      await expect(copilot).toBeVisible({ timeout: 10_000 })
      logStep('Rations AI-Copilot sichtbar', true)
    } catch (e) {
      logStep('Rations AI-Copilot sichtbar', false, (e as Error).message)
    }

    // ── 2) Ackerschlagkartei Portal-Feldbuch ─────────────────────────────
    const feldbuch = await measure(page, 'Ackerschlagkartei Feldbuch', '/portal/feldbuch')
    logStep('Feldbuch geladen', feldbuch.ok, `${feldbuch.navMs} ms`)

    for (const tab of ['schlaege', 'massnahmen']) {
      try {
        const trigger = page.getByRole('tab').filter({ hasText: new RegExp(tab === 'schlaege' ? 'Schläge' : 'Maßnahmen', 'i') }).first()
        await trigger.click({ timeout: 10_000 })
        await page.waitForTimeout(400)
        logStep(`Feldbuch-Tab "${tab}"`, true)
      } catch (e) {
        logStep(`Feldbuch-Tab "${tab}"`, false, (e as Error).message)
      }
    }

    // ── 3) Ackerschlagkartei DueV-Auswertungen (AS-W10) ──────────────────
    const ausw = await measure(page, 'Feldbuch DueV-Auswertungen', '/portal/feldbuch-auswertungen')
    logStep('Auswertungen geladen', ausw.ok, `${ausw.navMs} ms`)

    const auswTabs: { label: RegExp; api: string }[] = [
      { label: /Düngebedarf/i, api: '/feldbuch/duengebedarf' },
      { label: /Düngebilanz/i, api: '/feldbuch/duengebilanz' },
      { label: /Stoffstrombilanz/i, api: '/feldbuch/stoffstrombilanz' },
      { label: /Pflanzenschutz/i, api: '/feldbuch/pflanzenschutz-uebersicht' },
      { label: /Ernte/i, api: '/feldbuch/ernte-auswertung' },
    ]
    for (const t of auswTabs) {
      try {
        const btn = page.getByRole('button', { name: t.label }).first()
        const [res] = await Promise.all([
          page.waitForResponse((r) => r.url().includes(t.api), { timeout: 20_000 }).catch(() => null),
          btn.click({ timeout: 10_000 }),
        ])
        await page.waitForTimeout(300)
        logStep(`Auswertungs-Tab ${t.label.source}`, true, res ? `API ${res.status()}` : 'kein API-Call erfasst')
      } catch (e) {
        logStep(`Auswertungs-Tab ${t.label.source}`, false, (e as Error).message)
      }
    }

    // ── Protokoll schreiben ──────────────────────────────────────────────
    const outDir = path.join(process.cwd(), 'test-results')
    fs.mkdirSync(outDir, { recursive: true })
    const outFile = path.join(outDir, 'vollnutzung-protokoll.json')
    fs.writeFileSync(outFile, JSON.stringify(PROTOCOL, null, 2), 'utf8')

    // Konsolen-Zusammenfassung
    // eslint-disable-next-line no-console
    console.log('\n===== VOLLNUTZUNG-PROTOKOLL =====')
    // eslint-disable-next-line no-console
    console.log('Ladezeiten:')
    for (const t of PROTOCOL.timings) {
      // eslint-disable-next-line no-console
      console.log(`  ${t.page}: nav=${t.navMs}ms domContentLoaded=${t.domContentLoadedMs}ms load=${t.loadEventMs}ms ok=${t.ok}${t.note ? ' note=' + t.note : ''}`)
    }
    // eslint-disable-next-line no-console
    console.log(`Schritte ok: ${PROTOCOL.steps.filter((s) => s.ok).length}/${PROTOCOL.steps.length}`)
    // eslint-disable-next-line no-console
    console.log(`Konsolenfehler: ${PROTOCOL.consoleErrors.length}, Netzwerkfehler(>=400): ${PROTOCOL.networkErrors.length}, PageErrors: ${PROTOCOL.pageErrors.length}`)
    for (const c of PROTOCOL.consoleErrors.slice(0, 20)) console.log(`  [console] ${c.text} @ ${c.url}`)
    for (const n of PROTOCOL.networkErrors.slice(0, 20)) console.log(`  [net ${n.status}] ${n.method} ${n.url}`)
    for (const p of PROTOCOL.pageErrors.slice(0, 20)) console.log(`  [pageerror] ${p}`)
    // eslint-disable-next-line no-console
    console.log(`Protokoll: ${outFile}`)

    // Der Test selbst schlaegt nur bei komplettem Ladeversagen fehl; Fehlerdetails
    // werden protokolliert und danach behoben (nicht hart geblockt).
    expect(PROTOCOL.timings.every((t) => t.ok)).toBeTruthy()
  })
})
