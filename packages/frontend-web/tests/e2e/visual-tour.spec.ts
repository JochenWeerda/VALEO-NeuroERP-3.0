/**
 * Visual Tour — läuft headed, nimmt Screenshots auf allen Hauptseiten
 * Protokolliert: Textüberlauf, 404, Konsolfehler, Layout-Probleme
 * Getestete Viewport-Größen: Desktop 1440×900, Tablet 1024×768, Mobile 390×844
 */
import { test, expect } from '@playwright/test'
import type { Page } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const BASE_URL = 'http://localhost:3001'
const SCREENSHOT_DIR = path.join(__dirname, '../../visual-tour-results')

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet',  width: 1024, height: 768 },
  { name: 'mobile',  width: 390,  height: 844 },
]

const ROUTES = [
  { path: '/',                          label: 'Dashboard' },
  { path: '/agrar',                     label: 'Agrar Übersicht' },
  { path: '/agrar/annahme',             label: 'Ernte-Annahme' },
  { path: '/agrar/kontrakte',           label: 'Agrar Kontrakte' },
  { path: '/einkauf/bestellungen',      label: 'Einkauf Bestellungen' },
  { path: '/verkauf/auftraege',         label: 'Verkauf Aufträge' },
  { path: '/lager',                     label: 'Lager' },
  { path: '/finance',                   label: 'Finance Übersicht' },
  { path: '/fibu/bilanz',               label: 'FIBU Bilanz' },
  { path: '/crm/kunden',                label: 'CRM Kunden' },
  { path: '/workflow/flow-spine-studio',label: 'Flow Spine Studio' },
  { path: '/einstellungen/system',      label: 'Einstellungen' },
]

const issues: Array<{ route: string; viewport: string; type: string; detail: string }> = []

function ensureDir(dir: string): void {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
}

async function checkForIssues(page: Page, route: string, viewportName: string): Promise<void> {
  // 1. Konsolfehler
  const consoleErrors: string[] = []
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text())
  })

  // 2. Overflow — Elemente die über den Viewport hinausgehen
  const overflowElements = await page.evaluate(() => {
    const vw = window.innerWidth
    const overflowing: string[] = []
    document.querySelectorAll('*').forEach((el) => {
      const style = window.getComputedStyle(el)
      // Skip fixed/absolute/sticky positioned elements — their getBoundingClientRect()
      // reflects viewport-relative position, not document overflow
      if (['fixed', 'absolute', 'sticky'].includes(style.position)) return
      // Skip elements that are overflow:hidden parents
      if (style.overflow === 'hidden' || style.overflowX === 'hidden') return
      const rect = el.getBoundingClientRect()
      if (rect.right > vw + 5 || rect.left < -5) {
        const tag = el.tagName.toLowerCase()
        const id = el.id ? `#${el.id}` : ''
        const cls = Array.from(el.classList).slice(0, 2).join('.')
        overflowing.push(`${tag}${id}.${cls} (right:${Math.round(rect.right)}, vw:${vw})`)
      }
    })
    return overflowing.slice(0, 5)
  })

  // 3. 404 — only flag actual 404/error pages (heading-level text, not data that contains "404")
  const is404 = await page.evaluate(() => {
    const headings = Array.from(document.querySelectorAll('h1, h2, [role="heading"]'))
    return headings.some((h) => {
      const t = (h as HTMLElement).innerText ?? ''
      return /^\s*(404|Seite nicht gefunden|Not Found|Page Not Found)\s*$/.test(t)
    })
  })

  // 4. Unlesbare Texte (sehr kleiner Font < 10px)
  const tinyText = await page.evaluate(() => {
    const tiny: string[] = []
    document.querySelectorAll('p, span, td, th, label, button, a').forEach((el) => {
      const style = window.getComputedStyle(el)
      const size = parseFloat(style.fontSize)
      if (size > 0 && size < 10 && (el as HTMLElement).innerText?.trim().length > 0) {
        tiny.push(`${el.tagName.toLowerCase()}: "${(el as HTMLElement).innerText.substring(0, 30)}" (${size}px)`)
      }
    })
    return tiny.slice(0, 3)
  })

  if (is404) issues.push({ route, viewport: viewportName, type: '404', detail: 'Seite leer oder 404' })
  overflowElements.forEach((el) => issues.push({ route, viewport: viewportName, type: 'overflow', detail: el }))
  tinyText.forEach((t) => issues.push({ route, viewport: viewportName, type: 'tiny-text', detail: t }))
  consoleErrors.forEach((e) => {
    if (!e.includes('Warning') && !e.includes('axe')) {
      issues.push({ route, viewport: viewportName, type: 'console-error', detail: e.substring(0, 120) })
    }
  })
}

for (const vp of VIEWPORTS) {
  test.describe(`Viewport: ${vp.name} (${vp.width}×${vp.height})`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height } })

    for (const route of ROUTES) {
      test(`${route.label} [${vp.name}]`, async ({ page }) => {
        ensureDir(path.join(SCREENSHOT_DIR, vp.name))

        // Navigate with dev token
        await page.setExtraHTTPHeaders({ 'Authorization': 'Bearer dev-token' })
        await page.goto(BASE_URL + route.path, { waitUntil: 'networkidle', timeout: 15000 })
        await page.waitForTimeout(800) // wait for animations

        // Screenshot
        const screenshotName = `${route.label.replace(/[^a-zA-Z0-9äöüÄÖÜß]/g, '-')}.png`
        const screenshotPath = path.join(SCREENSHOT_DIR, vp.name, screenshotName)
        await page.screenshot({ path: screenshotPath, fullPage: false })

        // Check for visual issues
        await checkForIssues(page, route.path, vp.name)

        // Basic: page should not be completely empty
        const mainContent = page.locator('main, [role="main"], #root > *')
        await expect(mainContent.first()).toBeVisible({ timeout: 5000 })
      })
    }
  })
}

// Write issue report after all tests
test.afterAll(async () => {
  ensureDir(SCREENSHOT_DIR)
  const report = {
    timestamp: new Date().toISOString(),
    total_issues: issues.length,
    by_type: issues.reduce<Record<string, number>>((acc, i) => {
      acc[i.type] = (acc[i.type] ?? 0) + 1
      return acc
    }, {}),
    issues,
  }
  fs.writeFileSync(path.join(SCREENSHOT_DIR, 'issues.json'), JSON.stringify(report, null, 2))
  console.log(`\n📋 Visual Tour abgeschlossen: ${issues.length} Probleme gefunden`)
  console.log(`   Gespeichert in: ${SCREENSHOT_DIR}`)
  if (issues.length > 0) {
    console.log('\n🔴 Gefundene Probleme:')
    issues.forEach((i) => console.log(`  [${i.type}] ${i.viewport} / ${i.route}: ${i.detail}`))
  }
})
