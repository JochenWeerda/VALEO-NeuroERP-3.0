/**
 * Capture README screenshots (dashboard, finance, agrar) with Playwright.
 *
 * Prerequisites: Frontend and backend running (e.g. pnpm dev + uvicorn, or staging).
 *
 * Usage:
 *   FRONTEND_BASE_URL=http://localhost:3001 pnpm screenshots:readme
 *   pnpm screenshots:readme   # uses http://localhost:3000
 *
 * Writes: docs/screenshots/dashboard.png, finance.png, agrar.png (from repo root).
 */

import path from 'node:path'
import fs from 'node:fs'
import { chromium } from 'playwright'

const BASE_URL = process.env.FRONTEND_BASE_URL ?? 'http://localhost:3000'
const HEADLESS = process.env.HEADLESS !== 'false'

// From repo root: docs/screenshots (when run from packages/frontend-web, cwd is frontend-web)
const OUTPUT_DIR = process.env.SCREENSHOTS_OUTPUT_DIR ?? path.resolve(process.cwd(), '../../docs/screenshots')

const CAPTURES: {
  path: string
  file: string
  /** Selector or text to wait for before screenshot (so we don't capture loading state) */
  waitFor?: string
  /** Extra ms after navigation before waiting for content */
  waitAfterNav?: number
  /** Capture full scrollable page (e.g. entire dashboard) */
  fullPage?: boolean
}[] = [
  { path: '/', file: 'dashboard.png', waitAfterNav: 2000, fullPage: true },
  {
    path: '/finance/op-kreditoren',
    file: 'finance.png',
    waitFor: 'text=Offene Posten',
    waitAfterNav: 3000,
  },
  {
    path: '/agrar/ernte-annahme-erfassung',
    file: 'agrar.png',
    waitFor: "h1:has-text('Ernte-Annahme-Erfassung')",
    waitAfterNav: 1000,
  },
]

async function main() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true })
  }

  const browser = await chromium.launch({ headless: HEADLESS })
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    ignoreHTTPSErrors: true,
  })

  // Dev auth: set token so app treats us as logged in (when OIDC not configured)
  const devToken = process.env.VITE_API_DEV_TOKEN ?? process.env.API_DEV_TOKEN ?? 'dev-token'
  await context.addInitScript((token: string) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('token', token)
    if (!localStorage.getItem('tenant_id')) {
      localStorage.setItem('tenant_id', 'default')
    }
  }, devToken)

  const page = await context.newPage()

  const contentTimeout = 25_000

  for (const { path: routePath, file, waitFor, waitAfterNav = 1500, fullPage = false } of CAPTURES) {
    const url = `${BASE_URL}${routePath}`
    console.log(`Opening ${url} -> ${file}`)
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: contentTimeout })
      await page.waitForTimeout(waitAfterNav)
      if (waitFor) {
        await page.locator(waitFor).first().waitFor({ state: 'visible', timeout: contentTimeout })
        await page.waitForTimeout(500)
      }
      const outPath = path.join(OUTPUT_DIR, file)
      await page.screenshot({ path: outPath, fullPage })
      console.log(`  -> ${outPath}`)
    } catch (e) {
      console.error(`  Failed: ${e}`)
    }
  }

  await browser.close()
  console.log('Done.')
}

main()
