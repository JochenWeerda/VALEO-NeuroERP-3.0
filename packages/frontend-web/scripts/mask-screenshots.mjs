/**
 * Screenshot-Auswertung der neuen Masken über mehrere Viewports.
 * Frontend :3000 + Backend :8000 müssen laufen.   node scripts/mask-screenshots.mjs
 */
import { chromium } from '@playwright/test'
import { mkdirSync } from 'node:fs'

const BASE = process.env.BASE_URL || 'http://localhost:3000'
const OUT = '.mask-shots'
mkdirSync(OUT, { recursive: true })

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'notebook', width: 1280, height: 800 },
  { name: 'tablet', width: 834, height: 1112 },
  { name: 'mobile', width: 390, height: 844 },
]

async function ready(page, slug) {
  if (slug === 'milchvieh-crosssell') {
    await page.waitForFunction(() => /Kunden \([1-9]/.test(document.body.textContent || '') && /Mio €/.test(document.body.textContent || ''), { timeout: 40000 }).catch(() => {})
    await page.waitForTimeout(600)
  } else if (slug === 'milchvieh-karte') {
    await page.waitForSelector('canvas', { timeout: 30000 }).catch(() => {})
    await page.waitForTimeout(5000) // Tiles + POIs
  } else if (slug === 'kunden-schnellauswahl') {
    const input = page.locator('input[aria-label="Kunden suchen"]')
    await input.fill('hof').catch(() => {})
    await page.waitForTimeout(1500)
  }
}

const ROUTES = [
  { slug: 'kunden-schnellauswahl', path: '/crm/kunden-schnellauswahl' },
  { slug: 'milchvieh-crosssell', path: '/agrar/milchvieh-crosssell' },
  { slug: 'milchvieh-karte', path: '/agrar/milchvieh-karte' },
]

const run = async () => {
  const browser = await chromium.launch()
  const results = []
  for (const vp of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } })
    await ctx.addInitScript(() => {
      localStorage.setItem('access_token', 'dev-token')
      localStorage.setItem('tenant_id', '00000000-0000-0000-0000-000000000001')
    })
    const page = await ctx.newPage()
    await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 120000 })
    await page.waitForFunction(() => !document.querySelector('.animate-spin') && (document.body.textContent || '').length > 200, { timeout: 120000 }).catch(() => {})
    for (const r of ROUTES) {
      await page.goto(BASE + r.path, { waitUntil: 'domcontentloaded', timeout: 60000 })
      await page.waitForSelector('h1', { timeout: 40000 }).catch(() => {})
      await ready(page, r.slug)
      try { await page.screenshot({ path: `${OUT}/${r.slug}__${vp.name}.png`, fullPage: false, timeout: 30000, animations: 'disabled' }) } catch {}
      results.push(`${r.slug}/${vp.name}`)
    }
    await ctx.close()
  }
  await browser.close()
  console.log('done: ' + results.length + ' shots')
}
run().catch((e) => { console.error(e); process.exit(1) })
