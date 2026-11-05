/** Sequential browser render/contrast evidence; no live authentication, database, or external actions. */
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createServer } from 'vite'
import { chromium } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

const here = path.dirname(fileURLToPath(import.meta.url))
const frontend = path.resolve(here, '../..')
const repo = path.resolve(frontend, '../..')
const output = path.join(repo, 'docs/quality-assurance/evidence/psm-zulassungen-20261105')
const raw = execFileSync('python', ['-c',
  'import json; from app.core.screen_definitions import get_screen_definition; print(json.dumps(get_screen_definition("compliance/zulassungen-liste")))'],
{ cwd: repo, encoding: 'utf8' })
const schema = JSON.parse(raw)
assert.equal(schema.id, 'compliance/zulassungen-liste')
assert.equal(schema.adapter.type, 'native')
assert.equal(schema.layout.floorplan, 'worklist')
const schemaHash = createHash('sha256').update(JSON.stringify(schema)).digest('hex')
const embedded = JSON.stringify(schema).replaceAll('<', '\\u003c')
const pagePath = '/__psm_visual'
const server = await createServer({
  root: frontend,
  server: { host: '127.0.0.1', port: 0, open: false },
  plugins: [{ name: 'isolated-psm-visual', configureServer(vite) {
    vite.middlewares.use(async (request, response, next) => {
      if (request.url?.split('?')[0] !== pagePath) return next()
      try {
        const html = `<!doctype html><html lang="de" data-theme="meridian"><head><meta charset="utf-8"><title>PSM-Komponentenprüfung</title></head><body><div id="root"></div><script>document.documentElement.classList.toggle('dark',new URLSearchParams(location.search).get('theme')==='dark');window.__PSM_VISUAL_SCHEMA__=${embedded};</script><script type="module" src="/tests/visual/psm-runtime-harness.tsx"></script></body></html>`
        response.setHeader('Content-Type', 'text/html')
        response.end(await vite.transformIndexHtml(pagePath, html))
      } catch (error) { next(error) }
    })
  } }],
})
let browser
const report = { schemaId: schema.id, schemaHash, scope: 'synthetic native component; not authenticated end-to-end', cases: [] }
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
      const errors = []
      const external = []
      page.on('pageerror', error => errors.push(error.message))
      await page.route('**/*', route => {
        if (route.request().url().startsWith(origin + '/')) return route.continue()
        external.push(route.request().url())
        return route.abort()
      })
      try {
        await page.goto(`${origin}${pagePath}?theme=${theme}`, { waitUntil: 'domcontentloaded', timeout: 120000 })
        await page.getByRole('gridcell', { name: 'PSM-VIS-001', exact: true }).waitFor({ timeout: 120000 })
        await page.getByRole('gridcell', { name: 'PSM-VIS-002', exact: true }).waitFor({ timeout: 120000 })
        await page.getByRole('gridcell', { name: 'PSM-VIS-003', exact: true }).waitFor({ timeout: 120000 })
        assert.deepEqual(errors, [], 'Browser runtime errors')
        assert.deepEqual(external, [], 'Unexpected external request')
        const sizes = await page.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth, dark: document.documentElement.classList.contains('dark') }))
        assert(sizes.scroll <= sizes.width + 1, 'Uncontained horizontal page overflow')
        assert.equal(sizes.dark, theme === 'dark')
        const audit = await new AxeBuilder({ page }).include('[data-testid="visual-psm"]').withRules(['color-contrast']).analyze()
        assert.deepEqual(audit.violations, [], 'Text contrast violations')
        assert.deepEqual(audit.incomplete, [], 'Text contrast could not be assessed')
        const name = `${viewport.width}x${viewport.height}-${theme}.png`
        await page.screenshot({ path: path.join(output, name), fullPage: false })
        report.cases.push({ viewport, theme, image: name, contrastViolations: audit.violations.length, contrastIncomplete: audit.incomplete.length, runtimeErrors: errors, externalRequests: external, sizes })
        console.log(`PASS ${name}`)
      } finally { await context.close() }
    }
  }
  await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n')
} finally {
  if (browser) await browser.close()
  await server.close()
}
