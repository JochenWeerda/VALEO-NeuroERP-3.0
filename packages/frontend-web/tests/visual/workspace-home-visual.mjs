/** Six fresh Chrome contexts; synthetic data only. Full axe findings are retained. */
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createServer } from 'vite'
import { chromium } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

const frontend = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const repo = path.resolve(frontend, '../..')
const output = path.join(repo, 'artifacts/app-launcher-visual-20261116')
const pagePath = '/__workspace_home_visual'
const server = await createServer({ root: frontend, server: { host: '127.0.0.1', port: 0, open: false }, plugins: [{
  name: 'isolated-workspace-home', configureServer(vite) {
    vite.middlewares.use(async (request, response, next) => {
      if (request.url?.split('?')[0] !== pagePath) return next()
      try {
        const html = `<!doctype html><html lang="de" data-theme="meridian"><head><meta charset="utf-8"><title>Arbeitsplatzprüfung</title></head><body><div id="root"></div><script>document.documentElement.classList.toggle('dark',new URLSearchParams(location.search).get('theme')==='dark')</script><script type="module" src="/tests/visual/workspace-home-harness.tsx"></script></body></html>`
        response.setHeader('Content-Type', 'text/html')
        response.end(await vite.transformIndexHtml(pagePath, html))
      } catch (error) { next(error) }
    })
  },
}] })
let browser
const report = { scope: 'Synthetic start page; no live authentication or business API', cases: [] }
try {
  await fs.mkdir(output, { recursive: true })
  await server.listen()
  const address = server.httpServer.address()
  assert(address && typeof address !== 'string')
  const origin = `http://127.0.0.1:${address.port}`
  browser = await chromium.launch({ channel: 'chrome', headless: true })
  for (const viewport of [{ width: 1366, height: 768 }, { width: 1440, height: 900 }, { width: 1920, height: 1080 }]) {
    for (const theme of ['light', 'dark']) {
      const context = await browser.newContext({ viewport, locale: 'de-DE', timezoneId: 'Europe/Berlin', deviceScaleFactor: 1 })
      const page = await context.newPage()
      const errors = [], blockedRequests = [], failures = []
      page.on('pageerror', error => errors.push(error.message))
      await page.route('**/*', route => {
        const url = route.request().url()
        if (url.startsWith(origin + '/') && !new URL(url).pathname.startsWith('/api/')) return route.continue()
        blockedRequests.push(url)
        return route.abort()
      })
      const name = `${viewport.width}x${viewport.height}-${theme}`
      try {
        await page.goto(`${origin}${pagePath}?theme=${theme}`, { waitUntil: 'domcontentloaded', timeout: 120000 })
        await page.getByRole('heading', { name: 'Anwendungen', exact: true }).waitFor({ timeout: 120000 })
        await page.getByTestId('launchpad-overview').waitFor()
        if (await page.getByTestId('workspace-composition-host').count()) failures.push('Operational dashboard mounted on launcher start')
        if (!(await page.getByTestId('launchpad-overview').getByRole('link').count())) failures.push('No app launchers available')
        const text = await page.locator('body').innerText()
        if (/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/i.test(text)) failures.push('Raw UUID in visible text')
        if (/\b(?:reason[_ -]?code|create_from_inbox_bucht_nicht|[a-z]+(?:_[a-z]+){2,})\b/i.test(text)) failures.push('Reason code or technical identifier in visible text')
        const sizes = await page.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth, dark: document.documentElement.classList.contains('dark'), headingFont: getComputedStyle(document.querySelector('h1')).fontSize, textToken: getComputedStyle(document.documentElement).getPropertyValue('--text-2xl'), radiusToken: getComputedStyle(document.documentElement).getPropertyValue('--radius') }))
        if (sizes.scroll > sizes.width + 1) failures.push('Horizontal page overflow')
        if (parseFloat(sizes.headingFont) < 24 || !sizes.textToken.trim() || !sizes.radiusToken.trim()) failures.push('Central typography or radius tokens are invalid');
        if (sizes.dark !== (theme === 'dark')) failures.push('Theme mismatch')
        const audit = await new AxeBuilder({ page }).include('main').withRules(['color-contrast']).analyze()
        await fs.writeFile(path.join(output, `${name}-axe.json`), JSON.stringify(audit, null, 2) + '\n')
        if (audit.violations.length) failures.push(`${audit.violations.length} color contrast violations`)
        if (audit.incomplete.length) failures.push(`${audit.incomplete.length} color contrast findings require review`)
        await page.screenshot({ path: path.join(output, `${name}.png`), fullPage: false })
        report.cases.push({ viewport, theme, image: `${name}.png`, axe: `${name}-axe.json`, sizes, failures, errors, blockedRequests })
      } catch (error) {
        failures.push(String(error))
        report.cases.push({ viewport, theme, failures, errors, blockedRequests })
      } finally { await context.close() }
    }
  }
} finally {
  await fs.mkdir(output, { recursive: true })
  await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n')
  if (browser) await browser.close()
  await server.close()
}
assert.equal(report.cases.length, 6, 'All six visual cases must complete')
assert.deepEqual(report.cases.filter(c => c.failures.length || c.errors.length || c.blockedRequests.length), [], 'Visual checks failed; inspect report and axe findings')
